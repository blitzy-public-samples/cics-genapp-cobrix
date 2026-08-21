#!/usr/bin/env python3
"""Translate-on-copy generator for the GnuCOBOL validation harness.

Reads the three named CICS/Db2 programs and the two named copybooks under
``base/src`` strictly read-only and writes GnuCOBOL-compilable copies into
``<build-dir>/src``.  The five authorized sources are never opened for
writing; their SHA-256 digests are captured before generation and re-checked
after it.

Behaviour
---------
* Applies the rewrite rules R1-R14 of AAP section 0.4.4 to the generated
  copies only.  Every rule carries an expected site count and every count
  mismatch is a hard failure.
* Holds each rewritten construct to the contract its source declares: every
  ``EXEC SQL`` DML block is compared with ``statement_map.yml`` on verb, table,
  ordered column list, ordered host list with declared directions, the whole
  predicate region token for token against the declared predicate, and non-host
  column expressions; both chain LINK sites are held to their target program,
  ``DFHCOMMAREA`` and length 32500; the KSDSPOLY write is held to
  ``KSDSPOLY``, length 64 and key length 21, and all six of its operands reach
  the capture module.
* Reads only inside its own checkout: ``--source-dir``, ``--copybook-dir`` and
  ``--statement-map`` each have exactly one accepted location, and a value
  naming anything else, or a symbolic link standing at the statement map, is
  refused before the file is opened.
* Holds the census ``statement_map.yml`` declares for the program it describes
  to the file name, program id and expected block counts of that source, and
  then to the line total, EXEC CICS and EXEC SQL block counts and longest line
  measured while translating it.
* Writes only inside the build tree of its own checkout, through
  descriptor-relative operations that follow no symbolic link.  The report of
  an earlier run is invalidated before any generated source is touched: it is
  unlinked, or emptied in place when a log directory that denies writing
  refuses the unlink, so no run that fails afterwards leaves a report standing
  for a build it did not produce.  A report that can be neither unlinked nor
  emptied, including a directory, a link inside the tree and a file reachable
  through a second name, stops the run with the generated tree of the earlier
  run untouched.
* Copies ``lgcmarea.cpy`` and ``lgpolicy.cpy`` byte-for-byte, and the four
  harness copybooks named by ``--copybook-dir``, into the generated source
  directory; a single ``-I <build-dir>/src`` then resolves every ``COPY``.
* Verifies the generated text: columns 8-72 only, no tab, valid indicator
  column, a trailing newline, no surviving ``EXEC CICS`` / ``EXEC SQL`` /
  ``END-EXEC`` / ``DFHRESP(`` / ``PROCESS SQL`` token, and the expected
  structural counts.
* Writes ``<build-dir>/logs/source-baseline.sha256`` in ``sha256sum`` format
  and a JSON report recording every applied rule site.

The script is argv-driven and never prompts.  Exit status is 0 on success and
non-zero, with a precise message on standard error, on any failure.

Rule-to-construct coverage is carried by the JSON report and its per-rule
totals, which account for every rewritten construct and for every source line
carried through unchanged.  The reasoning behind the translation strategy
belongs to ``modernization/docs/decision-log.md`` (planned deliverable; not
present at this milestone); this module states only what it does.  Harness
topology is Figure 5 — Validation Harness Control Flow in
``modernization/docs/architecture.md``.
"""

import argparse
import errno
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# --------------------------------------------------------------------------
# Repository geometry and CLI defaults
# --------------------------------------------------------------------------
# This module lives at <repo-root>/modernization/harness/translate.py; the
# repository root is two directories above its own parent.  Relative CLI
# values are resolved against this root rather than the current working
# directory.
REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SOURCE_DIR = "base/src"
DEFAULT_BUILD_DIR = "modernization/harness/build"
DEFAULT_STATEMENT_MAP = "modernization/harness/statement_map.yml"
DEFAULT_COPYBOOK_DIR = "modernization/harness/copybooks"

BASELINE_RELATIVE = "logs/source-baseline.sha256"
REPORT_RELATIVE = "logs/translation-report.json"

# --------------------------------------------------------------------------
# Read allow-list
# --------------------------------------------------------------------------
# The only file names this translator may open under --source-dir.  Any other
# name, in particular base/src/lgstsq.cbl or anything under synthetic_class/,
# is refused before the path is touched.
PROGRAM_SOURCES = ("lgapol01.cbl", "lgapdb01.cbl", "lgapvs01.cbl")
VERBATIM_SOURCE_COPYBOOKS = ("lgcmarea.cpy", "lgpolicy.cpy")
SOURCE_ALLOW_LIST = frozenset(PROGRAM_SOURCES + VERBATIM_SOURCE_COPYBOOKS)

# Harness copybooks copied verbatim out of --copybook-dir into <build>/src.
HARNESS_COPYBOOKS = ("dfheiblk.cpy", "dfhresp.cpy", "hsqlca.cpy", "hcapture.cpy")

# The directories the five authorized sources and the four harness copybooks
# are read from, and the statement map that drives rules R2 and R13, all
# relative to the repository root this module belongs to.  A --source-dir,
# --copybook-dir or --statement-map naming anything else is refused before a
# file is opened, so the read surface cannot be moved to another tree.
EXPECTED_SOURCE_DIR = REPO_ROOT / "base" / "src"
EXPECTED_COPYBOOK_DIR = REPO_ROOT / "modernization" / "harness" / "copybooks"
EXPECTED_STATEMENT_MAP = (
    REPO_ROOT / "modernization" / "harness" / "statement_map.yml"
)

# SHA-256 of each authorized source as this translator was written against it.
# The bytes read are compared with these values before any generation, so the
# content cannot certify itself: a source that differs by a single byte is
# refused even when its line count and statement census still agree.  The four
# harness copybooks carry no pinned digest because they are authored files of
# this project and change with it.
AUTHORIZED_SOURCE_DIGESTS = {
    "lgapol01.cbl":
        "4dddd29539dd96aaec9f6885d3d62d19d40a1c6c888636623164bc5f5b232f6f",
    "lgapdb01.cbl":
        "3d21ad353a03c63d05defc511372e14477613fa4c51068a51a84d3c840c29815",
    "lgapvs01.cbl":
        "e0bca62eed2d6390852befdbaddd684833040c8be183d23f4fca368834709215",
    "lgcmarea.cpy":
        "4ecc9ed8dbf0936a8b0738cbb03a947e937206100b0e34f749fbb9e0b03f701d",
    "lgpolicy.cpy":
        "717c8f5c50738a2ef4d432e4b397e21bdc0423a9fc789246eb3360aa3f99eaa5",
}

# Largest statement map this translator reads, in bytes, and the deepest and
# widest document it accepts once composed.
MAX_STATEMENT_MAP_BYTES = 1_048_576
MAX_MAP_DEPTH = 32
MAX_MAP_NODES = 200_000

# --------------------------------------------------------------------------
# Write-path guard
# --------------------------------------------------------------------------
# Every write goes through BuildTree, whose root must resolve to exactly
# CANONICAL_BUILD_ROOT: the build tree of the checkout this module belongs to.
# modernization/.gitignore ignores /harness/build/; the guard confines every
# write to that one directory.
BUILD_DIR_TAIL = ("modernization", "harness", "build")
BUILD_SUBDIRS = ("src", "bin", "samples", "logs", "run")
CANONICAL_BUILD_ROOT = REPO_ROOT.joinpath(*BUILD_DIR_TAIL)

# Directory descriptors are opened read-only, must be directories, and must
# not be symbolic links; the descriptors are not inherited by the git
# subprocess this module runs.
NOFOLLOW_DIR_FLAGS = (
    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
)
# Regular files are created without O_TRUNC: the descriptor's file type and
# link count are examined, and only then is the file truncated and written.
# The descriptor is also readable, and a verbatim copy is read back through it.
NOFOLLOW_FILE_FLAGS = (
    os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
)
# An existing file is opened for emptying without O_CREAT, so the open reaches
# nothing the stat before it did not see, and without O_TRUNC, so the file type
# and link count are examined on the descriptor before anything is discarded.
# O_NONBLOCK makes the open of anything that is not a regular file fail rather
# than wait, and has no effect on a regular file.
NOFOLLOW_EXISTING_FILE_FLAGS = (
    os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0)
)
BUILD_DIR_MODE = 0o755
BUILD_FILE_MODE = 0o644

# The errno values a directory that denies writing raises for an unlink of an
# entry below it.  A removal refused with one of these is followed by emptying
# the file in place; any other errno is reported as it stands.
UNLINK_REFUSED_ERRNOS = frozenset({errno.EACCES, errno.EPERM})

# --------------------------------------------------------------------------
# Fixed-format geometry
# --------------------------------------------------------------------------
# Columns 1-6 are the sequence area, column 7 the indicator, columns 8-72 the
# code area.  Indices below are 0-based offsets into a line.
SEQUENCE_AREA_WIDTH = 6
INDICATOR_INDEX = 6
CODE_START = 7
AREA_A_INDENT = 7
AREA_B_INDENT = 11
CONTINUATION_STEP = 5
MAX_LINE_LENGTH = 72

COMMENT_INDICATORS = frozenset("*/")
VALID_INDICATORS = frozenset({" ", "*", "/", "-"})
SEQUENCE_AREA_CHARS = frozenset(
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    " */-."
)

# --------------------------------------------------------------------------
# Expected census (AAP 0.6.1) and per-rule site counts (AAP 0.4.4)
# --------------------------------------------------------------------------
EXPECTED_SOURCE_CENSUS = {
    "lgapol01.cbl": {
        "program_id": "LGAPOL01", "lines": 169, "exec_cics": 9, "exec_sql": 0,
    },
    "lgapdb01.cbl": {
        "program_id": "LGAPDB01", "lines": 595, "exec_cics": 20,
        "exec_sql": 11,
    },
    "lgapvs01.cbl": {
        "program_id": "LGAPVS01", "lines": 188, "exec_cics": 7, "exec_sql": 0,
    },
}
EXPECTED_TOTAL_CICS_SITES = 36
EXPECTED_TOTAL_SQL_BLOCKS = 11

EXPECTED_RULE_SITES = {
    "R1": 1,    # PROCESS SQL commented
    "R2": 3,    # EXEC SQL INCLUDE  -> COPY
    "R3": 3,    # PROCEDURE DIVISION USING DFHCOMMAREA
    "R4": 3,    # inserted harness declarations
    "R5": 2,    # chain LINK -> length + dynamic CALL
    "R6": 9,    # diagnostic LINK -> CICS-DIAG-LINK
    "R7": 12,   # EXEC CICS RETURN -> GOBACK
    "R8": 6,    # EXEC CICS ABEND  -> capture + GOBACK
    "R9": 1,    # WRITE KSDSPOLY   -> CICS-WRITE
    "R10": 3,   # ASKTIME          -> CICS-ASKTIME
    "R11": 3,   # FORMATTIME       -> CICS-FORMATTIME
    "R12": 1,   # DFHRESP(NORMAL)  -> named constant
    "R13": 8,   # SQL DML          -> stub CALLs
}
# R14 copies every remaining source line unchanged.  Its observed count is the
# per-program remainder and is asserted against the source line total instead
# of a fixed number.
RULE_R14 = "R14"

# --------------------------------------------------------------------------
# Post-generation expectations
# --------------------------------------------------------------------------
FORBIDDEN_GENERATED_PATTERNS = (
    ("EXEC CICS", re.compile(r"EXEC\s+CICS", re.IGNORECASE)),
    ("EXEC SQL", re.compile(r"EXEC\s+SQL", re.IGNORECASE)),
    ("END-EXEC", re.compile(r"END-EXEC", re.IGNORECASE)),
    ("DFHRESP(", re.compile(r"DFHRESP\s*\(", re.IGNORECASE)),
    ("PROCESS SQL", re.compile(r"PROCESS\s+SQL", re.IGNORECASE)),
)

EXPECTED_STRUCTURAL_COUNTS = {
    "PROCEDURE DIVISION USING DFHCOMMAREA.": 3,
    "COPY DFHEIBLK.": 3,
    "COPY DFHRESP.": 1,
    "COPY HSQLCA.": 1,
    "COPY LGPOLICY.": 1,
    "COPY LGCMAREA.": 3,
}
STRUCTURAL_PATTERNS = {
    "PROCEDURE DIVISION USING DFHCOMMAREA.": re.compile(
        r"^\s*PROCEDURE\s+DIVISION\s+USING\s+DFHCOMMAREA\s*\.\s*$", re.IGNORECASE
    ),
    "COPY DFHEIBLK.": re.compile(r"^\s*COPY\s+DFHEIBLK\s*\.\s*$", re.IGNORECASE),
    "COPY DFHRESP.": re.compile(r"^\s*COPY\s+DFHRESP\s*\.\s*$", re.IGNORECASE),
    "COPY HSQLCA.": re.compile(r"^\s*COPY\s+HSQLCA\s*\.\s*$", re.IGNORECASE),
    "COPY LGPOLICY.": re.compile(r"^\s*COPY\s+LGPOLICY\s*\.\s*$", re.IGNORECASE),
    "COPY LGCMAREA.": re.compile(r"^\s*COPY\s+LGCMAREA\s*\.\s*$", re.IGNORECASE),
}
ANY_COPY_PATTERN = re.compile(
    r"^\s*COPY\s+([A-Za-z0-9][A-Za-z0-9\-_]*)\s*\.\s*$", re.IGNORECASE
)

# --------------------------------------------------------------------------
# statement_map.yml expectations (validated before any work is done)
# --------------------------------------------------------------------------
EXPECTED_MAP_INCLUDE_COUNT = 3
EXPECTED_MAP_DML_COUNT = 8
EXPECTED_MAP_TOTAL_BLOCKS = 11
EXPECTED_MAP_CALL_PROGRAM_COUNT = 7

# The members of the map's source_program block.  Each one is compared with
# the authorized source the block names: the path with the pinned source
# directory and the allow-listed program names, the program id and the three
# block figures with EXPECTED_SOURCE_CENSUS, and the line width with
# MAX_LINE_LENGTH.  The three block figures and the line width are compared a
# second time with the values measured while translating that source.
DECLARED_SOURCE_PROGRAM_KEYS = (
    "path",
    "program_id",
    "total_lines",
    "exec_sql_blocks",
    "exec_cics_blocks",
    "max_line_length",
)

# --------------------------------------------------------------------------
# Generated harness declarations (R4) and stub program names
# --------------------------------------------------------------------------
HARNESS_ABEND_ITEM = "HARNESS-ABEND-CODE"
HARNESS_DIAG_LEN_ITEM = "HARNESS-DIAG-LEN"
R4_DECLARATIONS = (
    "COPY DFHEIBLK.",
    "01  HARNESS-ABEND-CODE           PIC X(4)  VALUE SPACES.",
    "01  HARNESS-DIAG-LEN             PIC S9(8) COMP VALUE +0.",
)
R4_DFHRESP_DECLARATION = "COPY DFHRESP."
R4_DFHRESP_PROGRAM = "lgapvs01.cbl"

STUB_DIAG_LINK = "CICS-DIAG-LINK"
STUB_ABEND = "CICS-ABEND"
STUB_WRITE = "CICS-WRITE"
STUB_ASKTIME = "CICS-ASKTIME"
STUB_FORMATTIME = "CICS-FORMATTIME"

# The chain-link operand of the diagnostic LINK sites; every other LINK in the
# three programs is a chain link handled by R5.
DIAGNOSTIC_LINK_PROGRAM = "LGSTSQ"

R1_NOTE = "(R1: commented for the harness build)"

# --------------------------------------------------------------------------
# Chain-link contract (R5) and file-write contract (R9)
# --------------------------------------------------------------------------
# One chain LINK per program, each with its own required target.  The PROGRAM
# operand of both sites is a data item, so the target is taken from the VALUE
# clause of that item's declaration in the program being translated.
CHAIN_LINK_TARGETS = {
    "lgapol01.cbl": "LGAPDB01",
    "lgapdb01.cbl": "LGAPVS01",
}
CHAIN_LINK_COMMAREA = "DFHCOMMAREA"
CHAIN_LINK_LENGTH = 32500

# The one KSDSPOLY write: file name, record length and key length are required
# to be exactly these, and all six operands reach the capture module.
WRITE_FILE_NAME = "KSDSPOLY"
WRITE_FILE_NAME_LENGTH = 8
WRITE_RECORD_LENGTH = 64
WRITE_KEY_LENGTH = 21
# The two lengths travel as zero-padded alphanumeric literals of this width,
# read by PIC 9(5) receivers in the capture module.  That choice belongs to
# modernization/docs/decision-log.md (planned deliverable; not present at this
# milestone), row: WRITE length operands as 5-digit literals.
WRITE_LENGTH_LITERAL_DIGITS = 5


class TranslationError(Exception):
    """A condition that stops generation with a precise, actionable message."""


# --------------------------------------------------------------------------
# Records carried into the JSON report
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ExecBlock:
    """One ``EXEC CICS``/``EXEC SQL`` ... ``END-EXEC`` block of a source file.

    ``indent`` is the 0-based column index of the ``EXEC`` keyword, ``body``
    the block flattened to a single spaced string, and ``terminating_period``
    whether the ``END-EXEC`` line carried a trailing period.
    """

    kind: str
    verb: str
    start_line: int
    end_line: int
    indent: int
    terminating_period: bool
    source_lines: tuple
    body: str

    @property
    def locator(self) -> str:
        if self.start_line == self.end_line:
            return str(self.start_line)
        return f"{self.start_line}-{self.end_line}"

    @property
    def source_text(self) -> str:
        return "\n".join(self.source_lines)


@dataclass
class RuleApplication:
    """One applied rewrite site, as recorded in the JSON report.

    ``details`` carries the machine-readable operand or contract values a rule
    enforced at the site; it is omitted from the report when a rule records
    nothing beyond its prose note.
    """

    rule_id: str
    source_lines: str
    source_text: str
    generated_text: str
    notes: str
    details: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        recorded = {
            "rule_id": self.rule_id,
            "source_lines": self.source_lines,
            "source_text": self.source_text,
            "generated_text": self.generated_text,
            "notes": self.notes,
        }
        if self.details:
            recorded["details"] = self.details
        return recorded


@dataclass
class ProgramResult:
    """Generation outcome for one translated program.

    ``chain_links`` holds one entry per chain LINK site the program carries,
    each recording the enforced program target, COMMAREA operand and length.
    ``source_max_line_length`` is the length of the longest line read for the
    program.
    """

    source_name: str
    source_line_count: int
    generated_lines: list
    source_max_line_length: int = 0
    applications: list = field(default_factory=list)
    consumed_line_numbers: set = field(default_factory=set)
    rule_comment_lines: set = field(default_factory=set)
    exec_cics_sites: int = 0
    exec_sql_blocks: int = 0
    generated_rule_lines: int = 0
    abend_return_adjacencies: int = 0
    chain_links: list = field(default_factory=list)

    @property
    def consumed_source_lines(self) -> int:
        return len(self.consumed_line_numbers)

    @property
    def unchanged_source_lines(self) -> int:
        return self.source_line_count - self.consumed_source_lines


# --------------------------------------------------------------------------
# Fixed-format emitter
# --------------------------------------------------------------------------
def emit_statement(indent: int, words, terminating_period: bool = False) -> list:
    """Lay one COBOL statement out in fixed format within columns 8-72.

    ``words`` are emitted in order and wrapped only at word boundaries, never
    splitting a word or a literal; continuation lines are indented further into
    Area B and carry no indicator-column hyphen.  When ``terminating_period``
    is true the period is attached to the last word and is included in the
    width measurement.  Raises TranslationError when a single word cannot fit
    the code area at the requested indentation.
    """
    if indent < AREA_A_INDENT:
        raise TranslationError(
            f"statement indent {indent} starts before column {AREA_A_INDENT + 1}"
        )
    parts = [str(word) for word in words if str(word) != ""]
    if not parts:
        raise TranslationError("refusing to emit an empty statement")
    if terminating_period:
        parts[-1] = parts[-1] + "."

    continuation_indent = max(indent + CONTINUATION_STEP, AREA_B_INDENT)
    lines = []
    current_indent = indent
    current: list = []
    for word in parts:
        candidate = current + [word]
        if len(" " * current_indent + " ".join(candidate)) <= MAX_LINE_LENGTH:
            current = candidate
            continue
        if not current:
            raise TranslationError(
                f"word {word!r} does not fit columns "
                f"{current_indent + 1}-{MAX_LINE_LENGTH}"
            )
        lines.append(" " * current_indent + " ".join(current))
        current_indent = continuation_indent
        current = [word]
    lines.append(" " * current_indent + " ".join(current))
    return lines


def emit_call_with_operand_lines(
    indent: int, call_program: str, operands, terminating_period: bool = False
) -> list:
    """Emit ``CALL '<program>' USING`` with one operand per continuation line.

    The operand lines and the closing ``END-CALL`` sit in Area B; the period,
    when required, is attached to ``END-CALL``.
    """
    if not operands:
        raise TranslationError(
            f"CALL {call_program!r} requires at least one operand"
        )
    head = emit_statement(indent, ["CALL", f"'{call_program}'", "USING"])
    operand_indent = max(indent + CONTINUATION_STEP, AREA_B_INDENT)
    lines = list(head)
    for operand in operands:
        lines.extend(emit_statement(operand_indent, [operand]))
    lines.extend(emit_statement(indent, ["END-CALL"], terminating_period))
    return lines


def emit_comment(text: str) -> str:
    """Emit one fixed-format comment line with ``*`` in the indicator column."""
    line = " " * SEQUENCE_AREA_WIDTH + "*" + text
    if len(line) > MAX_LINE_LENGTH:
        raise TranslationError(
            f"comment line would reach column {len(line)}: {line!r}"
        )
    return line


# --------------------------------------------------------------------------
# Line classification helpers
# --------------------------------------------------------------------------
def is_comment_line(line: str) -> bool:
    """True when the indicator column marks the line as a comment."""
    return len(line) > INDICATOR_INDEX and line[INDICATOR_INDEX] in COMMENT_INDICATORS


def code_of(line: str) -> str:
    """Return the code area (columns 8-72) of a line."""
    return line[CODE_START:] if len(line) > CODE_START else ""


def split_source_lines(text: str) -> list:
    """Split a source file into lines, requiring a single trailing newline.

    The five sources are LF-terminated with no trailing blank line; anything
    else is reported rather than silently normalised.
    """
    if "\r" in text:
        raise TranslationError("source contains a carriage return; expected LF only")
    if "\t" in text:
        raise TranslationError("source contains a tab character")
    if not text.endswith("\n"):
        raise TranslationError("source does not end with a newline")
    lines = text.split("\n")
    if lines[-1] != "":
        raise TranslationError("unexpected trailing content after the final newline")
    return lines[:-1]


# --------------------------------------------------------------------------
# Read-only source access
# --------------------------------------------------------------------------
def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_expected_read_directory(supplied: Path, expected: Path,
                                    option: str) -> None:
    """Require ``supplied`` to resolve to exactly ``expected``.

    ``option`` names the command-line option the value came from.  The
    comparison is made on the resolved paths, so a relative value, a value
    carrying ``..`` and a value reached through a symbolic link are all
    reduced to the directory they name before it is compared.
    """
    resolved = supplied.resolve()
    if resolved != expected.resolve():
        raise TranslationError(
            f"{option} names {resolved}; this translator reads only "
            f"{expected}, the directory of the checkout holding "
            f"{Path(__file__).resolve()}"
        )


def require_expected_read_file(supplied: Path, expected: Path,
                               option: str) -> None:
    """Require ``supplied`` to resolve to exactly ``expected``, and be no link.

    ``option`` names the command-line option the value came from.  The
    comparison is made on the resolved paths, so a relative value, a value
    carrying ``..`` and a value reached through a symbolic link are all
    reduced to the file they name before it is compared; a symbolic link
    standing at either path is then refused instead of being read through.
    """
    resolved = supplied.resolve()
    if resolved != expected.resolve():
        raise TranslationError(
            f"{option} names {resolved}; this translator reads only "
            f"{expected}, the file of the checkout holding "
            f"{Path(__file__).resolve()}"
        )
    for candidate in (supplied, expected):
        if candidate.is_symlink():
            raise TranslationError(
                f"{option} names {candidate}, a symbolic link reaching "
                f"{resolved}; this translator reads that path of its own "
                f"checkout only as a regular file"
            )


def require_authorized_source_digest(name: str, data: bytes) -> None:
    """Assert the bytes read for ``name`` carry the pinned SHA-256 digest."""
    expected = AUTHORIZED_SOURCE_DIGESTS.get(name)
    if expected is None:
        raise TranslationError(f"no pinned digest for authorized source {name!r}")
    actual = sha256_of_bytes(data)
    if actual != expected:
        raise TranslationError(
            f"{name} does not carry its pinned digest: expected {expected}, "
            f"read {actual}"
        )


def read_authorized_source(source_dir: Path, name: str) -> bytes:
    """Read one allow-listed source file in binary mode.

    Refuses any name outside SOURCE_ALLOW_LIST, any name carrying a path
    separator, and any path that resolves outside ``source_dir``.  The bytes
    read are compared with the pinned digest of that name before they are
    returned.
    """
    if name not in SOURCE_ALLOW_LIST:
        raise TranslationError(
            f"refusing to read {name!r}: only the five authorized source files "
            f"{sorted(SOURCE_ALLOW_LIST)} may be read"
        )
    if Path(name).name != name:
        raise TranslationError(
            f"refusing to read {name!r}: names must be bare file names"
        )
    path = source_dir / name
    if not path.is_file():
        raise TranslationError(f"authorized source not found: {path}")
    resolved = path.resolve()
    if resolved.parent != source_dir.resolve():
        raise TranslationError(
            f"refusing to read {path}: resolves outside the source directory "
            f"({resolved})"
        )
    with resolved.open("rb") as handle:
        data = handle.read()
    require_authorized_source_digest(name, data)
    return data


def read_harness_copybook(copybook_dir: Path, name: str) -> bytes:
    """Read one harness copybook from --copybook-dir in binary mode."""
    path = copybook_dir / name
    if not path.is_file():
        raise TranslationError(
            f"harness copybook not found: {path} "
            f"(expected all of {list(HARNESS_COPYBOOKS)})"
        )
    with path.open("rb") as handle:
        return handle.read()


# --------------------------------------------------------------------------
# Write-path guard
# --------------------------------------------------------------------------
class BuildTree:
    """The single write gate for the generated harness tree.

    Construction fails unless the resolved root is exactly
    ``CANONICAL_BUILD_ROOT``, the build tree of the checkout this module lives
    in, and unless every path component from the repository root down to that
    directory is a real directory rather than a symbolic link.  Every removal
    and every write is then performed through descriptor-relative, no-follow
    operations inside that root, and every target path is checked to land
    inside it.
    """

    def __init__(self, root: Path) -> None:
        resolved = root.expanduser().resolve()
        if resolved != CANONICAL_BUILD_ROOT:
            raise TranslationError(
                f"refusing to write to {resolved}: the build directory must be "
                f"{CANONICAL_BUILD_ROOT}, the {'/'.join(BUILD_DIR_TAIL)} tree of "
                f"the checkout holding {Path(__file__).resolve()}"
            )
        self._reject_symlink_components(resolved)
        self.root = resolved

    @staticmethod
    def _reject_symlink_components(resolved: Path) -> None:
        """Assert no component below the repository root is a symbolic link.

        ``REPO_ROOT`` is itself a fully resolved path, so its own components
        carry no link; the components below it are checked one at a time and
        each one that exists must be a directory.
        """
        walked = REPO_ROOT
        for part in resolved.relative_to(REPO_ROOT).parts:
            walked = walked / part
            if walked.is_symlink():
                raise TranslationError(
                    f"refusing to write to {resolved}: {walked} is a symbolic "
                    f"link, and the build tree is reached through real "
                    f"directories only"
                )
            if walked.exists() and not walked.is_dir():
                raise TranslationError(
                    f"refusing to write to {resolved}: {walked} exists and is "
                    f"not a directory"
                )

    def path_for(self, relative: str) -> Path:
        """Resolve a build-relative path and assert it stays inside the root."""
        if Path(relative).is_absolute():
            raise TranslationError(f"build paths must be relative, got {relative!r}")
        target = (self.root / relative).resolve()
        if target != self.root and self.root not in target.parents:
            raise TranslationError(
                f"refusing to write outside the build tree: {target} is not "
                f"inside {self.root}"
            )
        return target

    # -- descriptor-relative primitives -----------------------------------
    def _open_root_fd(self) -> int:
        """Open the build root itself as a no-follow directory descriptor."""
        try:
            return os.open(str(self.root), NOFOLLOW_DIR_FLAGS)
        except OSError as error:
            raise TranslationError(
                f"cannot open the build tree {self.root} as a directory: {error}"
            ) from error

    def _mkdir_if_absent(self, parent_fd: int, name: str, display: Path) -> bool:
        """Create the directory ``name`` below ``parent_fd``.

        Returns True when this call created it and False when it was already
        there; any other failure is reported.
        """
        try:
            os.mkdir(name, BUILD_DIR_MODE, dir_fd=parent_fd)
        except FileExistsError:
            return False
        except OSError as error:
            raise TranslationError(
                f"cannot create the build directory {display}: {error}"
            ) from error
        return True

    def _open_child_fd(
        self, parent_fd: int, name: str, display: Path, *, create: bool
    ) -> int:
        """Open ``name`` below ``parent_fd``, creating it when asked to.

        The open refuses to follow a symbolic link and refuses anything that is
        not a directory; ``create`` tolerates an existing directory and nothing
        else.  ``display`` is the full path the message names.
        """
        if create:
            self._mkdir_if_absent(parent_fd, name, display)
        try:
            return os.open(name, NOFOLLOW_DIR_FLAGS, dir_fd=parent_fd)
        except OSError as error:
            raise TranslationError(
                f"refusing to descend into {display}: it is not a directory this "
                f"run may open without following a link ({error})"
            ) from error

    def _open_directory_fd(self, parts, *, create: bool) -> int:
        """Open the directory named by ``parts`` relative to the build root."""
        current = self._open_root_fd()
        walked = self.root
        try:
            for part in parts:
                walked = walked / part
                child = self._open_child_fd(current, part, walked, create=create)
                os.close(current)
                current = child
        except BaseException:
            os.close(current)
            raise
        return current

    def _lexical_parts(self, relative: str) -> tuple:
        """Split a build-relative path into components without resolving it.

        ``.`` is dropped and ``..`` cancels the component before it, so the
        components handed to the descriptor walk are the ones the caller asked
        for; the no-follow open then refuses a symbolic link standing at any of
        them.
        """
        candidate = Path(relative)
        if candidate.is_absolute():
            raise TranslationError(f"build paths must be relative, got {relative!r}")
        parts = []
        for part in candidate.parts:
            if part == ".":
                continue
            if part == "..":
                if not parts:
                    raise TranslationError(
                        f"refusing to write outside the build tree: {relative!r} "
                        f"leaves {self.root}"
                    )
                parts.pop()
                continue
            parts.append(part)
        if not parts:
            raise TranslationError(
                f"refusing to write to the build root itself, requested as "
                f"{relative!r}"
            )
        return tuple(parts)

    def _write_through_descriptor(
        self, dir_fd: int, name: str, data: bytes, target: Path
    ) -> bytes:
        """Write ``data`` to ``name`` below ``dir_fd`` without following links.

        The open fails on a symbolic link and carries no O_TRUNC; the
        descriptor is then checked for being a regular file with a single hard
        link, and the file is truncated and written only after those checks
        hold.  Returns the bytes read back through the same descriptor.
        """
        try:
            handle = os.open(name, NOFOLLOW_FILE_FLAGS, BUILD_FILE_MODE, dir_fd=dir_fd)
        except OSError as error:
            raise TranslationError(
                f"refusing to write {target}: it cannot be opened without "
                f"following a link ({error})"
            ) from error
        try:
            info = os.fstat(handle)
            if not stat.S_ISREG(info.st_mode):
                raise TranslationError(
                    f"refusing to write {target}: it is not a regular file"
                )
            if info.st_nlink > 1:
                raise TranslationError(
                    f"refusing to write {target}: it carries {info.st_nlink} hard "
                    f"links, so a write would reach content outside the build tree"
                )
            os.ftruncate(handle, 0)
            written = 0
            while written < len(data):
                written += os.write(handle, data[written:])
            os.lseek(handle, 0, os.SEEK_SET)
            return self._read_all(handle)
        except OSError as error:
            raise TranslationError(f"cannot write {target}: {error}") from error
        finally:
            os.close(handle)

    @staticmethod
    def _read_all(handle: int) -> bytes:
        chunks = []
        while True:
            chunk = os.read(handle, 65536)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)

    # -- public write gate -------------------------------------------------
    def prepare(self) -> None:
        """Invalidate the earlier report, then reset the generated source dir.

        The report named by ``REPORT_RELATIVE`` is invalidated first, before
        anything under ``src`` is touched, so a failure of this reset - or of
        any later stage - cannot leave a report of the run that came before it
        alongside a generated tree that run did not produce.  A report that can
        be neither unlinked nor emptied stops this method before its first
        removal, leaving the generated tree exactly as the earlier run left it.

        ``src`` is then removed and recreated, and the remaining build
        subdirectories are created, through descriptor-relative operations, so
        afterwards ``src`` holds only files written by the current run.
        """
        self._ensure_root()
        self.invalidate_file(REPORT_RELATIVE)
        root_fd = self._open_root_fd()
        try:
            source_dir = self.root / "src"
            try:
                info = os.stat("src", dir_fd=root_fd, follow_symlinks=False)
            except FileNotFoundError:
                info = None
            if info is not None and not stat.S_ISDIR(info.st_mode):
                raise TranslationError(
                    f"{source_dir} exists and is not a directory"
                )
            self._remove_entry(root_fd, "src", source_dir)
            for name in BUILD_SUBDIRS:
                os.close(
                    self._open_child_fd(
                        root_fd, name, self.root / name, create=True
                    )
                )
        finally:
            os.close(root_fd)

    def _ensure_root(self) -> None:
        """Create the build root below its parent without following links."""
        parent = self.root.parent
        try:
            parent_fd = os.open(str(parent), NOFOLLOW_DIR_FLAGS)
        except OSError as error:
            raise TranslationError(
                f"cannot open {parent}, the parent of the build tree: {error}"
            ) from error
        try:
            self._mkdir_if_absent(parent_fd, self.root.name, self.root)
            info = os.stat(self.root.name, dir_fd=parent_fd, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise TranslationError(
                    f"refusing to write to {self.root}: it is a symbolic link"
                )
            if not stat.S_ISDIR(info.st_mode):
                raise TranslationError(
                    f"{self.root} exists and is not a directory"
                )
        finally:
            os.close(parent_fd)

    def _remove_entry(self, parent_fd: int, name: str, display: Path) -> int:
        """Remove ``name`` below ``parent_fd``, recursing into directories.

        Returns the number of entries removed; a name that does not exist
        removes nothing.  Symbolic links are unlinked, never followed, so a
        planted link cannot redirect the removal outside the build tree.
        """
        try:
            info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return 0
        except OSError as error:
            raise TranslationError(
                f"cannot inspect {display} before removing it: {error}"
            ) from error
        if not stat.S_ISDIR(info.st_mode):
            try:
                os.unlink(name, dir_fd=parent_fd)
            except OSError as error:
                raise TranslationError(
                    f"cannot remove {display}: {error}"
                ) from error
            return 1
        child_fd = self._open_child_fd(parent_fd, name, display, create=False)
        removed = 0
        try:
            for entry in os.listdir(child_fd):
                removed += self._remove_entry(child_fd, entry, display / entry)
        finally:
            os.close(child_fd)
        try:
            os.rmdir(name, dir_fd=parent_fd)
        except OSError as error:
            raise TranslationError(
                f"cannot remove the directory {display}: {error}"
            ) from error
        return removed + 1

    def invalidate_file(self, relative: str) -> None:
        """Leave nothing at ``relative`` that can be read as this run's output.

        The request must land inside the root, which a name reaching outside it
        through a link does not, and every directory above the entry is opened
        descriptor by descriptor without following a link.  A name standing for
        nothing is already invalid and is left alone.  A regular file reachable
        through this one name only is unlinked; when its directory denies
        writing and refuses the unlink, the file is emptied in place through a
        no-follow descriptor instead, which needs no permission on that
        directory.  Anything this gate may not remove or empty - a directory, a
        link inside the tree, an entry of another type, a file reachable
        through a second name, and a file whose removal and emptying are both
        refused - is left exactly as it stands and reported by raising
        ``TranslationError`` naming the path and the reason.
        """
        self.path_for(relative)
        parts = self._lexical_parts(relative)
        target = self.root.joinpath(*parts)
        dir_fd = self._open_directory_fd(parts[:-1], create=True)
        try:
            try:
                info = os.stat(parts[-1], dir_fd=dir_fd, follow_symlinks=False)
            except FileNotFoundError:
                return
            except OSError as error:
                raise TranslationError(
                    f"cannot inspect {target} before removing it: {error}"
                ) from error
            self._require_removable_or_emptiable(info, target)
            try:
                os.unlink(parts[-1], dir_fd=dir_fd)
                return
            except FileNotFoundError:
                return
            except OSError as error:
                if error.errno not in UNLINK_REFUSED_ERRNOS:
                    raise TranslationError(
                        f"cannot remove {target}: {error}"
                    ) from error
                refusal = error
            self._empty_through_descriptor(dir_fd, parts[-1], target, refusal)
        finally:
            os.close(dir_fd)

    @staticmethod
    def _require_removable_or_emptiable(info: os.stat_result, target: Path) -> None:
        """Assert ``info`` describes an entry this gate may unlink or empty.

        ``info`` is the result of a no-follow ``stat`` or of an ``fstat`` on a
        no-follow descriptor.  A directory, a symbolic link and any other
        non-regular entry are refused, and so is a regular file carrying more
        than one hard link, whose content is reachable through a name this gate
        does not own.
        """
        if stat.S_ISDIR(info.st_mode):
            raise TranslationError(
                f"refusing to invalidate {target}: it is a directory"
            )
        if stat.S_ISLNK(info.st_mode):
            raise TranslationError(
                f"refusing to invalidate {target}: it is a symbolic link"
            )
        if not stat.S_ISREG(info.st_mode):
            raise TranslationError(
                f"refusing to invalidate {target}: it is not a regular file"
            )
        if info.st_nlink > 1:
            raise TranslationError(
                f"refusing to invalidate {target}: it carries {info.st_nlink} "
                f"hard links, and neither removing nor emptying this name would "
                f"leave the content it shares unreadable"
            )

    def _empty_through_descriptor(
        self, dir_fd: int, name: str, target: Path, refusal: OSError
    ) -> None:
        """Truncate ``name`` below ``dir_fd`` to nothing, following no link.

        The open creates nothing, follows no symbolic link and truncates
        nothing; the descriptor is then checked for still standing for a
        regular file reachable through this one name, and only then is the file
        emptied.  A name that has since gone is already invalid.  ``refusal``
        is the error that stopped the unlink and is named alongside any failure
        here, so a report that survives both is reported with both reasons.
        """
        try:
            handle = os.open(name, NOFOLLOW_EXISTING_FILE_FLAGS, dir_fd=dir_fd)
        except FileNotFoundError:
            return
        except OSError as error:
            raise TranslationError(
                f"cannot remove {target} ({refusal}) and cannot open it to "
                f"empty it ({error}), so this run stops before it changes the "
                f"generated sources the report describes"
            ) from error
        try:
            self._require_removable_or_emptiable(os.fstat(handle), target)
            os.ftruncate(handle, 0)
        except OSError as error:
            raise TranslationError(
                f"cannot remove {target} ({refusal}) and cannot empty it "
                f"({error}), so this run stops before it changes the generated "
                f"sources the report describes"
            ) from error
        finally:
            os.close(handle)

    def write_text(self, relative: str, text: str) -> Path:
        """Write ASCII text with LF endings; non-ASCII content is reported."""
        try:
            encoded = text.encode("ascii")
        except UnicodeEncodeError as error:
            raise TranslationError(
                f"refusing to write non-ASCII content to "
                f"{self.path_for(relative)}: {error}"
            ) from error
        return self.write_bytes(relative, encoded)

    def write_bytes(self, relative: str, data: bytes) -> Path:
        """Write ``data`` inside the build tree through no-follow operations."""
        target, _ = self._write(relative, data)
        return target

    def _write(self, relative: str, data: bytes) -> tuple:
        """Write ``data`` and return the target path and the bytes read back.

        ``path_for`` checks that the request resolves inside the build tree and
        the descriptor walk then opens the requested components themselves, so
        the path written is the path asked for.
        """
        self.path_for(relative)
        parts = self._lexical_parts(relative)
        target = self.root.joinpath(*parts)
        dir_fd = self._open_directory_fd(parts[:-1], create=True)
        try:
            written = self._write_through_descriptor(
                dir_fd, parts[-1], data, target
            )
        finally:
            os.close(dir_fd)
        return target, written

    def copy_verbatim(self, relative: str, data: bytes, expected_digest: str) -> Path:
        """Write ``data`` and assert the written copy's digest is unchanged.

        The copy is read back through the same descriptor the write used, so
        the digest covers the bytes that reached the file this run opened.
        """
        target, written = self._write(relative, data)
        digest = sha256_of_bytes(written)
        if digest != expected_digest:
            raise TranslationError(
                f"verbatim copy {target} digest {digest} does not match source "
                f"digest {expected_digest}"
            )
        return target



# --------------------------------------------------------------------------
# SQL contract: normalisation, parsing and comparison against statement_map.yml
# --------------------------------------------------------------------------
# The verbs the eight mapped DML blocks use and the two host directions the map
# spells.  A map entry naming anything else is refused before generation.
SUPPORTED_SQL_VERBS = frozenset({"INSERT", "SET", "SELECT"})
HOST_DIRECTIONS = frozenset({"in", "out"})

# ``present_in_source_block`` lists the ``<start>-<end>`` source ranges a host
# is referenced by.  A host whose list omits the range of the entry carrying it
# is not referenced by that source block and reaches the stub as a superset
# argument.  That choice belongs to modernization/docs/decision-log.md
# (planned deliverable; not present at this milestone), row: single-superset
# SQL-INSERT-ENDOWMENT call.
SOURCE_BLOCK_RANGE_RE = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*$")

SQL_ENVELOPE_RE = re.compile(
    r"^EXEC\s+SQL\s+(?P<body>.*?)\s*END-EXEC\s*\.?\s*$", re.IGNORECASE | re.DOTALL
)
SQL_LEADING_VERB_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\b")
SQL_TABLE_PATTERN = r"[A-Za-z][A-Za-z0-9_$#@]*(?:\.[A-Za-z][A-Za-z0-9_$#@]*)?"
SQL_INSERT_HEAD_RE = re.compile(
    rf"^INSERT\s+INTO\s+(?P<table>{SQL_TABLE_PATTERN})\s*(?=\()", re.IGNORECASE
)
SQL_VALUES_HEAD_RE = re.compile(r"^VALUES\s*(?=\()", re.IGNORECASE)
SQL_SET_RE = re.compile(
    r"^SET\s+:(?P<host>[A-Za-z][A-Za-z0-9\-]*)\s*=\s*(?P<expression>.+)$",
    re.IGNORECASE,
)
SQL_SELECT_RE = re.compile(
    r"^SELECT\s+(?P<columns>.+?)\s+INTO\s+(?P<targets>.+?)\s+FROM\s+"
    rf"(?P<table>{SQL_TABLE_PATTERN})(?P<tail>\s.*)?$",
    re.IGNORECASE,
)
HOST_REFERENCE_RE = re.compile(r"^:([A-Za-z][A-Za-z0-9\-]*)$")

# A declared ``predicate`` fragment is one complete comparison less its host
# reference: a boolean connector, the column being compared and the comparison
# operator, as in ``WHERE POLICYNUMBER =``.  Nothing else is a fragment.
SQL_PREDICATE_FRAGMENT_RE = re.compile(
    r"^(?P<connector>WHERE|AND|OR)\s+"
    rf"(?P<column>{SQL_TABLE_PATTERN})\s*"
    r"(?P<operator><>|!=|<=|>=|=|<|>)$",
    re.IGNORECASE,
)
# The first condition of a predicate opens with WHERE; every later one opens
# with a boolean connector.
SQL_FIRST_PREDICATE_CONNECTOR = "WHERE"
SQL_LATER_PREDICATE_CONNECTORS = ("AND", "OR")

# The complete token vocabulary of a predicate region: a host reference, a
# quoted literal, a number, a possibly qualified identifier, a two-character
# comparison operator, and the single characters SQL predicates spell.  A
# character outside this vocabulary is reported rather than skipped, so no
# predicate text can pass unread.
SQL_PREDICATE_TOKEN_RE = re.compile(
    r":[A-Za-z][A-Za-z0-9\-]*"
    r"|'[^']*'"
    r"|\d+(?:\.\d+)?"
    r"|[A-Za-z][A-Za-z0-9_$#@]*(?:\.[A-Za-z][A-Za-z0-9_$#@]*)*"
    r"|<>|!=|<=|>="
    r"|[=<>(),+\-*/]"
)
# WHERE standing as a whole word, used to split a statement tail at the point
# its predicate region begins.
SQL_WHERE_KEYWORD_RE = re.compile(
    r"(?<![A-Za-z0-9_$#@\-])WHERE(?![A-Za-z0-9_$#@\-])", re.IGNORECASE
)
# The part of each statement form whose text the predicate contract accounts
# for.  Each value is the phrase a rejection message uses to name that text.
PREDICATE_REGION_LABELS = {
    "INSERT": "the text following the VALUES list",
    "SET": "the text following the assigned expression",
    "SELECT": "the text following the FROM clause",
}


def normalise_sql_expression(text: str) -> str:
    """Fold one SQL fragment to a comparable form.

    Runs of whitespace collapse to a single space, the space around
    parentheses is removed and the result is upper-cased, so
    ``IDENTITY_VAL_LOCAL ( )`` and ``identity_val_local()`` compare equal
    while ``CURRENT TIMESTAMP`` keeps its separating space.
    """
    collapsed = re.sub(r"\s+", " ", str(text)).strip()
    collapsed = re.sub(r"\s*\(\s*", "(", collapsed)
    collapsed = re.sub(r"\s*\)", ")", collapsed)
    return collapsed.upper()


def normalise_sql_body(program: str, block: ExecBlock) -> str:
    """Strip the ``EXEC SQL`` / ``END-EXEC`` envelope and collapse whitespace."""
    match = SQL_ENVELOPE_RE.match(block.body)
    if match is None:
        raise TranslationError(
            f"{program}:{block.locator}: the EXEC SQL block does not carry the "
            f"expected EXEC SQL ... END-EXEC envelope: {block.body[:80]!r}"
        )
    return re.sub(r"\s+", " ", match.group("body")).strip()


def read_balanced_group(text: str, start: int, program: str, locator: str) -> tuple:
    """Return the contents of the parenthesised group at ``start``.

    ``start`` indexes the opening parenthesis, possibly preceded by spaces.
    The returned tuple is the text between the balanced parentheses and the
    index just past the closing one.
    """
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor >= len(text) or text[cursor] != "(":
        raise TranslationError(
            f"{program}:{locator}: expected a parenthesised list at "
            f"{text[start:start + 40]!r}"
        )
    depth = 0
    for index in range(cursor, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return text[cursor + 1:index], index + 1
    raise TranslationError(
        f"{program}:{locator}: unbalanced parenthesis in {text[cursor:cursor + 40]!r}"
    )


def split_top_level_commas(text: str) -> list:
    """Split a list on the commas that sit outside every parenthesis."""
    items = []
    depth = 0
    current = []
    for character in text:
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        if character == "," and depth == 0:
            items.append("".join(current).strip())
            current = []
            continue
        current.append(character)
    items.append("".join(current).strip())
    return items


def split_predicate_region(text: str) -> tuple:
    """Split a statement tail at the first predicate-opening ``WHERE``.

    The keyword is recognised only where it stands as a whole word outside
    every parenthesis and outside every quoted literal.  Returns the text
    before that point and the predicate region from it onwards; a tail holding
    no such keyword yields the whole text and an empty region.
    """
    depth = 0
    index = 0
    while index < len(text):
        character = text[index]
        if character == "'":
            closing = text.find("'", index + 1)
            index = len(text) if closing < 0 else closing + 1
            continue
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        elif depth == 0 and SQL_WHERE_KEYWORD_RE.match(text, index) is not None:
            return text[:index].strip(), text[index:].strip()
        index += 1
    return text.strip(), ""


def parse_sql_insert(program: str, locator: str, body: str) -> dict:
    """Parse ``INSERT INTO <table> ( columns ) VALUES ( values )``.

    Any text standing after the VALUES list is returned as ``tail``, the
    block's predicate region, and is accounted for by the predicate contract.
    """
    head = SQL_INSERT_HEAD_RE.match(body)
    if head is None:
        raise TranslationError(
            f"{program}:{locator}: the source does not open with "
            f"INSERT INTO <table> ( ... ): {body[:80]!r}"
        )
    columns_text, cursor = read_balanced_group(body, head.end(), program, locator)
    remainder = body[cursor:].lstrip()
    values_head = SQL_VALUES_HEAD_RE.match(remainder)
    if values_head is None:
        raise TranslationError(
            f"{program}:{locator}: the column list is not followed by "
            f"VALUES ( ... ): {remainder[:80]!r}"
        )
    values_text, after = read_balanced_group(
        remainder, values_head.end(), program, locator
    )
    return {
        "table": head.group("table"),
        "columns": split_top_level_commas(columns_text),
        "values": split_top_level_commas(values_text),
        "tail": remainder[after:].strip(),
    }


def parse_sql_set(program: str, locator: str, body: str) -> dict:
    """Parse ``SET :<host> = <expression>``.

    The assigned expression ends where a predicate-opening ``WHERE`` stands;
    that keyword and everything after it are returned as ``tail``, the block's
    predicate region.
    """
    match = SQL_SET_RE.match(body)
    if match is None:
        raise TranslationError(
            f"{program}:{locator}: the source does not carry the "
            f"SET :<host> = <expression> form: {body[:80]!r}"
        )
    expression, tail = split_predicate_region(match.group("expression").strip())
    return {
        "target_host": match.group("host"),
        "expression": expression,
        "tail": tail,
    }


def parse_sql_select(program: str, locator: str, body: str) -> dict:
    """Parse ``SELECT <columns> INTO <targets> FROM <table> [tail]``.

    Everything standing after the table name is returned as ``tail``, the
    block's predicate region, whether or not it opens with ``WHERE``.
    """
    match = SQL_SELECT_RE.match(body)
    if match is None:
        raise TranslationError(
            f"{program}:{locator}: the source does not carry the "
            f"SELECT ... INTO ... FROM ... form: {body[:80]!r}"
        )
    tail = match.group("tail")
    return {
        "table": match.group("table"),
        "columns": split_top_level_commas(match.group("columns")),
        "targets": split_top_level_commas(match.group("targets")),
        "tail": tail.strip() if tail else "",
    }


def source_block_range(entry: dict) -> str:
    """Render an entry's source range in the ``<start>-<end>`` map spelling."""
    return f"{int(entry['start_line'])}-{int(entry['end_line'])}"


def normalise_source_block_range(value, label: str) -> str:
    match = SOURCE_BLOCK_RANGE_RE.match(str(value))
    if match is None:
        raise TranslationError(
            f"{label} holds {value!r}, which is not a <start>-<end> source range"
        )
    return f"{int(match.group(1))}-{int(match.group(2))}"


def host_is_referenced_by(entry: dict, host: dict) -> bool:
    """True when the host is referenced by this entry's own source block.

    A host with no ``present_in_source_block`` marker is referenced by every
    block that maps to it; a host carrying the marker is referenced only by the
    ranges the marker lists.
    """
    marker = host.get("present_in_source_block")
    if marker is None:
        return True
    own = source_block_range(entry)
    label = f"dml[{entry['id']}].using[{host['host']}].present_in_source_block"
    return any(
        normalise_source_block_range(value, label) == own for value in marker
    )


def expected_source_hosts(entry: dict) -> tuple:
    """Split an entry's mapped hosts into those its source block references.

    Returns the hosts the source block must reference, in map order, and the
    hosts the map marks as absent from that block, which reach the stub as
    superset arguments.
    """
    referenced = []
    omitted = []
    for host in entry["using"]:
        if host_is_referenced_by(entry, host):
            referenced.append(host)
        else:
            omitted.append(host)
    return referenced, omitted


def _validate_presence_metadata(entry: dict, host: dict, label: str) -> None:
    """Check one host's ``present_in_source_block`` marker is well formed."""
    marker = host.get("present_in_source_block")
    if marker is None:
        return
    ranges = _require_sequence(marker, f"{label}.present_in_source_block")
    if not ranges:
        raise TranslationError(
            f"{label}.present_in_source_block is empty; a host referenced by no "
            f"source block cannot be validated against one"
        )
    for value in ranges:
        normalise_source_block_range(value, f"{label}.present_in_source_block")


def _host_signature(entry: dict) -> tuple:
    """Render an entry's ``using`` list as a comparable signature."""
    signature = []
    for host in entry["using"]:
        marker = host.get("present_in_source_block")
        listed = (
            tuple(
                normalise_source_block_range(
                    value, f"dml[{entry['id']}].using.present_in_source_block"
                )
                for value in marker
            )
            if marker is not None
            else None
        )
        signature.append(
            (
                str(host["host"]).upper(),
                normalise_sql_expression(str(host["column"])),
                str(host["direction"]).strip().lower(),
                normalise_sql_expression(str(host["pic"])),
                listed,
            )
        )
    return tuple(signature)


def _validate_shared_call_signatures(dml: list) -> None:
    """Check the entries that share one stub declare one identical signature.

    Two DML entries may name the same ``call_program`` only when their
    ``using`` lists are identical host by host, which is what makes the shared
    list the superset both source branches are measured against.  Every host of
    that shared list must be referenced by at least one of those blocks, and a
    ``present_in_source_block`` marker may name only the ranges of the blocks
    that share the stub.
    """
    by_program = {}
    for entry in dml:
        by_program.setdefault(str(entry["call_program"]), []).append(entry)
    for call_program, entries in sorted(by_program.items()):
        ranges = {source_block_range(entry) for entry in entries}
        reference = entries[0]
        reference_signature = _host_signature(reference)
        for entry in entries[1:]:
            if _host_signature(entry) != reference_signature:
                raise TranslationError(
                    f"dml entries {reference['id']!r} and {entry['id']!r} both map "
                    f"to {call_program} but declare different USING lists; entries "
                    f"sharing one stub must declare one identical signature"
                )
        for position, host in enumerate(reference["using"]):
            marker = host.get("present_in_source_block")
            if marker is None:
                continue
            label = (
                f"dml[{reference['id']}].using[{position}]"
                f".present_in_source_block"
            )
            listed = {
                normalise_source_block_range(value, label) for value in marker
            }
            unknown = sorted(listed - ranges)
            if unknown:
                raise TranslationError(
                    f"{label} names source range(s) {unknown} that no dml entry "
                    f"mapping to {call_program} declares; the known ranges are "
                    f"{sorted(ranges)}"
                )
        for entry in entries:
            referenced, _omitted = expected_source_hosts(entry)
            if not referenced:
                raise TranslationError(
                    f"dml[{entry['id']}] marks every mapped host as absent from "
                    f"its own source block {source_block_range(entry)}"
                )
        for position, host in enumerate(reference["using"]):
            if not any(host_is_referenced_by(entry, host) for entry in entries):
                raise TranslationError(
                    f"dml[{reference['id']}].using[{position}] host "
                    f"{host['host']!r} is marked absent from every source block "
                    f"that maps to {call_program}"
                )


def _require_declared_table(
    program: str, block: ExecBlock, entry: dict, table: str
) -> str:
    """Assert the table the source addresses is the one the map declares."""
    declared = str(entry["table"]).strip()
    if table.upper() != declared.upper():
        raise TranslationError(
            f"{program}:{block.locator}: statement map entry {entry['id']!r} "
            f"declares table {declared!r} but the source block addresses "
            f"{table!r}"
        )
    return table


def _validate_insert_contract(
    program: str, block: ExecBlock, entry: dict, referenced: list, body: str
) -> dict:
    """Compare an INSERT block's columns, values and directions with the map."""
    parsed = parse_sql_insert(program, block.locator, body)
    _require_declared_table(program, block, entry, parsed["table"])
    columns = parsed["columns"]
    values = parsed["values"]
    if len(columns) != len(values):
        raise TranslationError(
            f"{program}:{block.locator}: the source names {len(columns)} column(s) "
            f"and supplies {len(values)} value(s)"
        )
    declared_non_host = {
        normalise_sql_expression(str(column)): (str(column), str(expression))
        for column, expression in (entry.get("non_host_values") or {}).items()
    }
    bindings = []
    cursor = 0
    for column, value in zip(columns, values):
        if not column:
            raise TranslationError(
                f"{program}:{block.locator}: the column list holds an empty entry"
            )
        host_reference = HOST_REFERENCE_RE.match(value)
        if host_reference is not None:
            if cursor >= len(referenced):
                raise TranslationError(
                    f"{program}:{block.locator}: column {column!r} takes host "
                    f"{value!r}, beyond the {len(referenced)} host(s) statement map "
                    f"entry {entry['id']!r} declares for this block"
                )
            item = referenced[cursor]
            if host_reference.group(1).upper() != str(item["host"]).upper():
                raise TranslationError(
                    f"{program}:{block.locator}: value position {cursor + 1} holds "
                    f"host {host_reference.group(1)!r}; statement map entry "
                    f"{entry['id']!r} declares {item['host']!r} there"
                )
            if normalise_sql_expression(column) != normalise_sql_expression(
                str(item["column"])
            ):
                raise TranslationError(
                    f"{program}:{block.locator}: the source pairs host "
                    f"{item['host']!r} with column {column!r}; statement map entry "
                    f"{entry['id']!r} pairs it with {item['column']!r}"
                )
            if str(item["direction"]).strip().lower() != "in":
                raise TranslationError(
                    f"{program}:{block.locator}: host {item['host']!r} stands in an "
                    f"INSERT VALUES position, which requires direction 'in'; "
                    f"statement map entry {entry['id']!r} declares "
                    f"{item['direction']!r}"
                )
            bindings.append(
                {
                    "column": column,
                    "value": value,
                    "host": str(item["host"]),
                    "direction": "in",
                }
            )
            cursor += 1
            continue
        key = normalise_sql_expression(column)
        declared = declared_non_host.pop(key, None)
        if declared is None:
            raise TranslationError(
                f"{program}:{block.locator}: column {column!r} is supplied by the "
                f"expression {value!r}, and statement map entry {entry['id']!r} "
                f"declares no non_host_values entry for it"
            )
        if normalise_sql_expression(value) != normalise_sql_expression(declared[1]):
            raise TranslationError(
                f"{program}:{block.locator}: statement map entry {entry['id']!r} "
                f"declares non_host_values[{declared[0]!r}]={declared[1]!r}; the "
                f"source supplies {value!r}"
            )
        bindings.append(
            {
                "column": column,
                "value": value,
                "host": None,
                "direction": "expression",
            }
        )
    if cursor != len(referenced):
        raise TranslationError(
            f"{program}:{block.locator}: statement map entry {entry['id']!r} "
            f"declares {len(referenced)} host(s) for this block but only {cursor} "
            f"stand in a VALUES position"
        )
    if declared_non_host:
        missing = sorted(column for column, _ in declared_non_host.values())
        raise TranslationError(
            f"{program}:{block.locator}: statement map entry {entry['id']!r} "
            f"declares non-host column(s) {missing} that the source column list "
            f"does not name"
        )
    return {
        "table": parsed["table"],
        "columns": columns,
        "column_bindings": bindings,
        "predicate": parsed["tail"] or None,
    }


def _validate_set_contract(
    program: str, block: ExecBlock, entry: dict, referenced: list, body: str
) -> dict:
    """Compare a SET block's target host and expression with the map."""
    parsed = parse_sql_set(program, block.locator, body)
    if len(referenced) != 1:
        raise TranslationError(
            f"{program}:{block.locator}: statement map entry {entry['id']!r} "
            f"declares {len(referenced)} host(s) for a SET statement, which "
            f"assigns exactly one"
        )
    item = referenced[0]
    if parsed["target_host"].upper() != str(item["host"]).upper():
        raise TranslationError(
            f"{program}:{block.locator}: the SET target is "
            f"{parsed['target_host']!r}; statement map entry {entry['id']!r} "
            f"declares {item['host']!r}"
        )
    if str(item["direction"]).strip().lower() != "out":
        raise TranslationError(
            f"{program}:{block.locator}: host {item['host']!r} stands in the SET "
            f"target position, which requires direction 'out'; statement map entry "
            f"{entry['id']!r} declares {item['direction']!r}"
        )
    if normalise_sql_expression(parsed["expression"]) != normalise_sql_expression(
        str(item["column"])
    ):
        raise TranslationError(
            f"{program}:{block.locator}: the SET expression is "
            f"{parsed['expression']!r}; statement map entry {entry['id']!r} pairs "
            f"host {item['host']!r} with {item['column']!r}"
        )
    return {
        "table": None,
        "columns": [str(item["column"])],
        "column_bindings": [
            {
                "column": str(item["column"]),
                "value": parsed["expression"],
                "host": str(item["host"]),
                "direction": "out",
            }
        ],
        "predicate": parsed["tail"] or None,
    }


def _validate_select_contract(
    program: str, block: ExecBlock, entry: dict, referenced: list, body: str
) -> dict:
    """Compare a SELECT block's INTO targets, table and predicate with the map."""
    parsed = parse_sql_select(program, block.locator, body)
    _require_declared_table(program, block, entry, parsed["table"])
    out_items = [
        item
        for item in referenced
        if str(item["direction"]).strip().lower() == "out"
    ]
    in_items = [
        item for item in referenced if str(item["direction"]).strip().lower() == "in"
    ]
    targets = []
    for target in parsed["targets"]:
        reference = HOST_REFERENCE_RE.match(target)
        if reference is None:
            raise TranslationError(
                f"{program}:{block.locator}: the INTO list holds {target!r}, which "
                f"is not a host variable reference"
            )
        targets.append(reference.group(1))
    if len(parsed["columns"]) != len(targets):
        raise TranslationError(
            f"{program}:{block.locator}: the source selects "
            f"{len(parsed['columns'])} column(s) into {len(targets)} target(s)"
        )
    if [name.upper() for name in targets] != [
        str(item["host"]).upper() for item in out_items
    ]:
        raise TranslationError(
            f"{program}:{block.locator}: the INTO target position holds {targets}; "
            f"statement map entry {entry['id']!r} declares the output host(s) "
            f"{[str(item['host']) for item in out_items]} in that order"
        )
    for column, item in zip(parsed["columns"], out_items):
        if normalise_sql_expression(column) != normalise_sql_expression(
            str(item["column"])
        ):
            raise TranslationError(
                f"{program}:{block.locator}: the source reads column {column!r} "
                f"into host {item['host']!r}; statement map entry {entry['id']!r} "
                f"pairs it with {item['column']!r}"
            )
    predicate_hosts = HOST_VARIABLE_RE.findall(parsed["tail"])
    if [name.upper() for name in predicate_hosts] != [
        str(item["host"]).upper() for item in in_items
    ]:
        raise TranslationError(
            f"{program}:{block.locator}: the predicate position holds "
            f"{predicate_hosts}; statement map entry {entry['id']!r} declares the "
            f"input host(s) {[str(item['host']) for item in in_items]} in that "
            f"order"
        )
    return {
        "table": parsed["table"],
        "columns": parsed["columns"],
        "column_bindings": [
            {
                "column": column,
                "value": f":{item['host']}",
                "host": str(item["host"]),
                "direction": "out",
            }
            for column, item in zip(parsed["columns"], out_items)
        ],
        "predicate": parsed["tail"] or None,
    }


def parse_sql_predicate_fragment(label: str, fragment: str) -> dict:
    """Parse one declared ``predicate`` fragment into its three parts.

    A fragment is exactly ``<connector> <column> <operator>``: the boolean
    connector opening the condition, the column being compared and the
    comparison operator.  Anything else - a second condition, a literal, a
    function call, a parenthesis, a missing operator - is refused here, so a
    fragment can never declare more than one comparison.
    """
    match = SQL_PREDICATE_FRAGMENT_RE.match(str(fragment).strip())
    if match is None:
        raise TranslationError(
            f"{label} holds {fragment!r}, which is not one predicate condition "
            f"of the form <WHERE|AND|OR> <column> <comparison operator>"
        )
    return {
        "connector": match.group("connector").upper(),
        "column": normalise_sql_expression(match.group("column")),
        "operator": match.group("operator"),
    }


def tokenise_sql_predicate(program: str, locator: str, text: str) -> list:
    """Split a predicate region into its comparable tokens, reading all of it.

    Identifiers, host references and operators are upper-cased; a quoted
    literal keeps its own case.  Every non-blank character must belong to a
    token: text the vocabulary cannot read is reported, so a predicate region
    is never partly examined.
    """
    tokens = []
    cursor = 0
    for match in SQL_PREDICATE_TOKEN_RE.finditer(text):
        skipped = text[cursor:match.start()].strip()
        if skipped:
            raise TranslationError(
                f"{program}:{locator}: the predicate text {skipped[:40]!r} is "
                f"not readable as SQL predicate tokens"
            )
        token = match.group(0)
        tokens.append(token if token.startswith("'") else token.upper())
        cursor = match.end()
    remainder = text[cursor:].strip()
    if remainder:
        raise TranslationError(
            f"{program}:{locator}: the predicate text {remainder[:40]!r} is not "
            f"readable as SQL predicate tokens"
        )
    return tokens


def expected_predicate_conditions(entry: dict, referenced: list) -> list:
    """Build the predicate the statement map declares for one block.

    Walks the entry's hosts in map order, parses each declared ``predicate``
    fragment and renders the condition it stands for as the token sequence
    ``<connector> <column> <operator> :<host>``.  The first condition must open
    with WHERE and every later one with a boolean connector, and each
    condition must compare the column its own host declares.  Nothing in the
    source block contributes to the result.
    """
    conditions = []
    for item in referenced:
        fragment = item.get("predicate")
        if fragment is None:
            continue
        label = f"dml[{entry['id']}].using[{item['host']}].predicate"
        parsed = parse_sql_predicate_fragment(label, fragment)
        declared_column = normalise_sql_expression(str(item["column"]))
        if parsed["column"] != declared_column:
            raise TranslationError(
                f"{label} compares column {parsed['column']!r}; the host it "
                f"belongs to declares column {item['column']!r}"
            )
        if conditions:
            if parsed["connector"] not in SQL_LATER_PREDICATE_CONNECTORS:
                raise TranslationError(
                    f"{label} opens condition {len(conditions) + 1} with "
                    f"{parsed['connector']!r}; conditions after the first open "
                    f"with one of {list(SQL_LATER_PREDICATE_CONNECTORS)}"
                )
        elif parsed["connector"] != SQL_FIRST_PREDICATE_CONNECTOR:
            raise TranslationError(
                f"{label} opens the first condition with "
                f"{parsed['connector']!r}; a predicate opens with "
                f"{SQL_FIRST_PREDICATE_CONNECTOR}"
            )
        host = str(item["host"])
        conditions.append(
            {
                "host": host,
                "predicate": str(fragment),
                "connector": parsed["connector"],
                "column": parsed["column"],
                "operator": parsed["operator"],
                "tokens": [
                    parsed["connector"],
                    parsed["column"],
                    parsed["operator"],
                    f":{host.upper()}",
                ],
            }
        )
    return conditions


def _validate_predicate_contract(
    program: str,
    block: ExecBlock,
    entry: dict,
    referenced: list,
    region,
    region_label: str,
) -> list:
    """Compare a block's whole predicate region with the declared predicate.

    The expected token sequence is built from the statement map alone by
    ``expected_predicate_conditions``; the actual sequence is every token of
    the block's complete predicate region.  The two must be equal token for
    token and hold the same number of tokens, so an added condition, a changed
    connector, column, operator or host, a negation, a parenthesised subclause
    and any trailing clause are each rejected, and a declared condition the
    source no longer carries is rejected as well.  Returns the conditions that
    were enforced.
    """
    conditions = expected_predicate_conditions(entry, referenced)
    expected = [token for condition in conditions for token in condition["tokens"]]
    actual = tokenise_sql_predicate(program, block.locator, str(region or ""))
    expected_text = " ".join(expected)
    actual_text = " ".join(actual)
    if not expected and actual:
        raise TranslationError(
            f"{program}:{block.locator}: statement map entry {entry['id']!r} "
            f"declares no predicate for this block; {region_label} holds "
            f"{actual_text!r}"
        )
    for position, token in enumerate(expected):
        if position >= len(actual):
            raise TranslationError(
                f"{program}:{block.locator}: statement map entry "
                f"{entry['id']!r} declares {token!r} as predicate token "
                f"{position + 1}; {region_label} ends after {len(actual)} "
                f"token(s). Declared predicate {expected_text!r}; source "
                f"predicate {actual_text!r}"
            )
        if actual[position] != token:
            raise TranslationError(
                f"{program}:{block.locator}: statement map entry "
                f"{entry['id']!r} declares {token!r} as predicate token "
                f"{position + 1}; the source holds {actual[position]!r}. "
                f"Declared predicate {expected_text!r}; source predicate "
                f"{actual_text!r}"
            )
    if len(actual) > len(expected):
        residual = " ".join(actual[len(expected):])
        raise TranslationError(
            f"{program}:{block.locator}: statement map entry {entry['id']!r} "
            f"declares the predicate {expected_text!r}, and {region_label} "
            f"holds the undeclared trailing condition(s) {residual!r}. Source "
            f"predicate {actual_text!r}"
        )
    return conditions


def validate_sql_contract(program: str, block: ExecBlock, entry: dict) -> dict:
    """Compare one source EXEC SQL DML block with its statement map entry.

    Checks the SQL verb, the table, the ordered column list, the ordered host
    list with each host's declared direction and position, the block's complete
    predicate region against the predicate the map declares, and every non-host
    column expression.  Returns the contract that was enforced, for the report;
    any drift raises TranslationError naming the program, the locator, the
    expectation and what the source holds.
    """
    body = normalise_sql_body(program, block)
    declared_verb = str(entry["sql_verb"]).strip().upper()
    leading = SQL_LEADING_VERB_RE.match(body)
    if leading is None:
        raise TranslationError(
            f"{program}:{block.locator}: the EXEC SQL block opens with no SQL "
            f"verb: {body[:80]!r}"
        )
    body_verb = leading.group(1).upper()
    if body_verb != declared_verb:
        raise TranslationError(
            f"{program}:{block.locator}: statement map entry {entry['id']!r} "
            f"declares sql_verb {declared_verb!r} but the source block opens with "
            f"{body_verb!r}"
        )

    referenced, omitted = expected_source_hosts(entry)
    source_hosts = HOST_VARIABLE_RE.findall(body)
    if [name.upper() for name in source_hosts] != [
        str(item["host"]).upper() for item in referenced
    ]:
        message = (
            f"{program}:{block.locator}: statement map entry {entry['id']!r} "
            f"requires host variable(s) {[str(item['host']) for item in referenced]} "
            f"in that order; the source block references {source_hosts}"
        )
        if omitted:
            message += (
                f"; mapped host(s) "
                f"{[str(item['host']) for item in omitted]} are marked absent from "
                f"this block by present_in_source_block"
            )
        raise TranslationError(message)

    validators = {
        "INSERT": _validate_insert_contract,
        "SET": _validate_set_contract,
        "SELECT": _validate_select_contract,
    }
    contract = validators[declared_verb](program, block, entry, referenced, body)
    predicates = _validate_predicate_contract(
        program,
        block,
        entry,
        referenced,
        contract.get("predicate"),
        PREDICATE_REGION_LABELS[declared_verb],
    )
    return {
        "entry_id": str(entry["id"]),
        "sql_verb": declared_verb,
        "source_block": source_block_range(entry),
        "normalised_source": body,
        "hosts_referenced": [str(item["host"]) for item in referenced],
        "hosts_omitted": [str(item["host"]) for item in omitted],
        "non_host_values": {
            str(column): str(expression)
            for column, expression in (entry.get("non_host_values") or {}).items()
        },
        "predicates": predicates,
        **contract,
    }


# --------------------------------------------------------------------------
# statement_map.yml
# --------------------------------------------------------------------------
def using_counts_key(call_program: str) -> str:
    """Map a stub program name onto its ``checks.using_counts`` key.

    Strips surrounding whitespace, lower-cases the name, replaces every hyphen
    with an underscore and removes a leading ``sql_``.  ``SQL-INSERT-ENDOWMENT``
    returns ``insert_endowment``.
    """
    key = str(call_program).strip().lower().replace("-", "_")
    return key.removeprefix("sql_")


def _require_mapping(value, label: str) -> dict:
    if not isinstance(value, dict):
        raise TranslationError(f"{label} must be a mapping, got {type(value).__name__}")
    return value


def _require_sequence(value, label: str) -> list:
    if not isinstance(value, list):
        raise TranslationError(f"{label} must be a list, got {type(value).__name__}")
    return value


def _require_keys(entry: dict, keys, label: str) -> None:
    missing = [key for key in keys if key not in entry]
    if missing:
        raise TranslationError(f"{label} is missing required key(s): {missing}")


def _require_text(value, label: str) -> str:
    """Return ``value`` when it is a non-empty string, else raise."""
    if not isinstance(value, str):
        raise TranslationError(
            f"{label} holds {type(value).__name__} {value!r}; a string is required"
        )
    if not value.strip():
        raise TranslationError(f"{label} holds only blanks; a value is required")
    return value


def _require_integer(value, label: str) -> int:
    """Return ``value`` when it is an integer, else raise.

    ``bool`` and ``float`` are refused: ``True`` would compare equal to 1 and
    ``268.9`` would be accepted as a line number by a numeric comparison.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise TranslationError(
            f"{label} holds {type(value).__name__} {value!r}; an integer is required"
        )
    return value


def _require_boolean(value, label: str) -> bool:
    """Return ``value`` when it is a boolean, else raise."""
    if not isinstance(value, bool):
        raise TranslationError(
            f"{label} holds {type(value).__name__} {value!r}; true or false is "
            f"required"
        )
    return value


class _StrictMapLoader(yaml.SafeLoader):
    """A safe loader that refuses aliases, merge keys and duplicate keys.

    An anchor may be declared, but composing an alias of it is refused, so no
    node of the loaded document is shared with another and no part of it can be
    expanded more than once.  A ``<<`` merge key is refused for the same
    reason, and a mapping repeating a key is refused rather than silently
    keeping the last value.
    """

    def compose_node(self, parent, index):
        if self.check_event(yaml.events.AliasEvent):
            event = self.peek_event()
            raise TranslationError(
                f"statement map uses the YAML alias *{event.anchor} at "
                f"{event.start_mark.line + 1}: aliases are not accepted"
            )
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key == "<<":
                raise TranslationError(
                    f"statement map uses a YAML merge key at "
                    f"{key_node.start_mark.line + 1}: merge keys are not accepted"
                )
            if isinstance(key, (str, int, float, bool, type(None))):
                if key in seen:
                    raise TranslationError(
                        f"statement map repeats the key {key!r} at "
                        f"{key_node.start_mark.line + 1}"
                    )
                seen.add(key)
        return super().construct_mapping(node, deep=deep)


def _bound_loaded_document(value, label: str, depth: int = 0) -> int:
    """Return the node count of ``value``, refusing an over-deep or wide map."""
    if depth > MAX_MAP_DEPTH:
        raise TranslationError(
            f"{label} nests more than {MAX_MAP_DEPTH} containers"
        )
    count = 1
    if isinstance(value, dict):
        for key, item in value.items():
            count += 1 + _bound_loaded_document(item, label, depth + 1)
            if count > MAX_MAP_NODES:
                raise TranslationError(
                    f"{label} holds more than {MAX_MAP_NODES} values"
                )
    elif isinstance(value, (list, tuple)):
        for item in value:
            count += _bound_loaded_document(item, label, depth + 1)
            if count > MAX_MAP_NODES:
                raise TranslationError(
                    f"{label} holds more than {MAX_MAP_NODES} values"
                )
    return count


def _validate_map_scalar_types(data: dict, label: str) -> None:
    """Type-check every scalar this translator later reads from the map.

    Each value is checked before any hashing, comparison, upper-casing or
    numeric use, so a member of the wrong type is reported by name instead of
    escaping as a TypeError from the code that consumes it.
    """
    checks = data.get("checks")
    if isinstance(checks, dict):
        for key in ("include_count", "dml_count", "total_blocks"):
            if key in checks:
                _require_integer(checks[key], f"{label}: checks.{key}")
        programs = checks.get("call_programs")
        if isinstance(programs, list):
            for index, name in enumerate(programs):
                _require_text(name, f"{label}: checks.call_programs[{index}]")
        counts = checks.get("using_counts")
        if isinstance(counts, dict):
            for key, value in counts.items():
                _require_text(key, f"{label}: checks.using_counts key")
                _require_integer(value, f"{label}: checks.using_counts[{key}]")
    for group, text_keys, integer_keys, boolean_keys in (
        ("includes", ("id", "include_name", "replacement"),
         ("start_line", "end_line"), ("terminating_period",)),
        ("dml", ("id", "call_program"),
         ("start_line", "end_line"), ("terminating_period",)),
    ):
        entries = data.get(group)
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            where = f"{label}: {group}[{index}]"
            for key in text_keys:
                if key in entry:
                    _require_text(entry[key], f"{where}.{key}")
            for key in integer_keys:
                if key in entry:
                    _require_integer(entry[key], f"{where}.{key}")
            for key in boolean_keys:
                if key in entry:
                    _require_boolean(entry[key], f"{where}.{key}")
            for key in ("sql_verb",):
                if key in entry and entry[key] is not None:
                    _require_text(entry[key], f"{where}.{key}")
            hosts = entry.get("using")
            if isinstance(hosts, list):
                for position, host in enumerate(hosts):
                    if isinstance(host, dict):
                        for key in ("name", "direction"):
                            if key in host:
                                _require_text(
                                    host[key], f"{where}.using[{position}].{key}"
                                )
                    else:
                        _require_text(host, f"{where}.using[{position}]")


def _validate_declared_source_program(source_program: dict, label: str) -> str:
    """Compare the declared ``source_program`` block with the source it names.

    Returns the base name of the declared program.  The declared path must be
    one of the allow-listed program sources inside the pinned source
    directory, the declared program id must be the one that source carries,
    the declared line total and EXEC CICS/EXEC SQL block counts must equal the
    expected census of that source, and the declared line width must equal the
    code-area limit every line of the generated copy is held to.  Each
    mismatch names the member and both values.
    """
    _require_keys(source_program, DECLARED_SOURCE_PROGRAM_KEYS, label)
    declared_path = _require_text(source_program["path"], f"{label}.path").strip()
    name = Path(declared_path).name
    if name not in PROGRAM_SOURCES:
        raise TranslationError(
            f"{label}.path names {name!r}, expected one of the authorized "
            f"program sources {list(PROGRAM_SOURCES)}"
        )
    expected_path = (
        EXPECTED_SOURCE_DIR.relative_to(REPO_ROOT) / name
    ).as_posix()
    if Path(declared_path).as_posix() != expected_path:
        raise TranslationError(
            f"{label}.path is {declared_path!r}, expected {expected_path!r}"
        )
    census = EXPECTED_SOURCE_CENSUS[name]
    declared_id = _require_text(
        source_program["program_id"], f"{label}.program_id"
    ).strip().upper()
    if declared_id != census["program_id"]:
        raise TranslationError(
            f"{label}.program_id is {declared_id!r}, expected "
            f"{census['program_id']!r} for {name}"
        )
    for key, expected in (
        ("total_lines", census["lines"]),
        ("exec_cics_blocks", census["exec_cics"]),
        ("exec_sql_blocks", census["exec_sql"]),
        ("max_line_length", MAX_LINE_LENGTH),
    ):
        declared = _require_integer(source_program[key], f"{label}.{key}")
        if declared != expected:
            raise TranslationError(
                f"{label}.{key} is {declared}, expected {expected} for {name}"
            )
    return name


def load_statement_map(path: Path) -> dict:
    """Load and validate ``statement_map.yml`` before any generation happens.

    The document is read under a byte bound, composed with aliases, merge keys
    and duplicate keys refused, bounded again by nesting depth and value count,
    and then type-checked member by member.  The ``checks`` block is compared
    with the expected census (3 includes, 8 dml entries, 11 blocks in total,
    one ``using_counts`` entry per stub and seven ``call_programs``) and every
    entry is checked for internal consistency.  The ``source_program`` block is
    compared member by member with the authorized source it names.
    """
    if not path.is_file():
        raise TranslationError(f"statement map not found: {path}")
    size = path.stat().st_size
    if size > MAX_STATEMENT_MAP_BYTES:
        raise TranslationError(
            f"statement map {path} holds {size} bytes; at most "
            f"{MAX_STATEMENT_MAP_BYTES} are read"
        )
    with path.open("r", encoding="utf-8") as handle:
        text = handle.read(MAX_STATEMENT_MAP_BYTES + 1)
    if len(text.encode("utf-8")) > MAX_STATEMENT_MAP_BYTES:
        raise TranslationError(
            f"statement map {path} exceeds {MAX_STATEMENT_MAP_BYTES} bytes"
        )
    loader = _StrictMapLoader(text)
    try:
        data = loader.get_single_data()
    finally:
        loader.dispose()
    _bound_loaded_document(data, f"statement map {path}")
    data = _require_mapping(data, f"{path}")
    _validate_map_scalar_types(data, f"statement map {path}")

    _require_keys(data, ("includes", "dml", "checks", "source_program"), f"{path}")
    includes = _require_sequence(data["includes"], "includes")
    dml = _require_sequence(data["dml"], "dml")
    checks = _require_mapping(data["checks"], "checks")
    source_program = _require_mapping(data["source_program"], "source_program")

    _require_keys(
        checks,
        ("include_count", "dml_count", "total_blocks", "using_counts", "call_programs"),
        "checks",
    )
    if checks["include_count"] != EXPECTED_MAP_INCLUDE_COUNT:
        raise TranslationError(
            f"checks.include_count is {checks['include_count']}, "
            f"expected {EXPECTED_MAP_INCLUDE_COUNT}"
        )
    if checks["dml_count"] != EXPECTED_MAP_DML_COUNT:
        raise TranslationError(
            f"checks.dml_count is {checks['dml_count']}, "
            f"expected {EXPECTED_MAP_DML_COUNT}"
        )
    if checks["total_blocks"] != EXPECTED_MAP_TOTAL_BLOCKS:
        raise TranslationError(
            f"checks.total_blocks is {checks['total_blocks']}, "
            f"expected {EXPECTED_MAP_TOTAL_BLOCKS}"
        )
    if checks["include_count"] + checks["dml_count"] != checks["total_blocks"]:
        raise TranslationError(
            "checks.include_count + checks.dml_count does not equal "
            "checks.total_blocks"
        )
    if len(includes) != checks["include_count"]:
        raise TranslationError(
            f"includes holds {len(includes)} entries but checks.include_count "
            f"is {checks['include_count']}"
        )
    if len(dml) != checks["dml_count"]:
        raise TranslationError(
            f"dml holds {len(dml)} entries but checks.dml_count is "
            f"{checks['dml_count']}"
        )

    call_programs = _require_sequence(checks["call_programs"], "checks.call_programs")
    if len(call_programs) != EXPECTED_MAP_CALL_PROGRAM_COUNT:
        raise TranslationError(
            f"checks.call_programs holds {len(call_programs)} names, "
            f"expected {EXPECTED_MAP_CALL_PROGRAM_COUNT}"
        )
    if len(set(call_programs)) != len(call_programs):
        raise TranslationError("checks.call_programs contains a duplicate name")

    using_counts = _require_mapping(checks["using_counts"], "checks.using_counts")
    expected_using_keys = {using_counts_key(name) for name in call_programs}
    if set(using_counts) != expected_using_keys:
        raise TranslationError(
            "checks.using_counts keys "
            f"{sorted(using_counts)} do not match the keys derived from "
            f"checks.call_programs {sorted(expected_using_keys)}"
        )

    declared_program = _validate_declared_source_program(
        source_program, "source_program"
    )

    seen_include_ids = set()
    for index, raw_include in enumerate(includes):
        entry = _require_mapping(raw_include, f"includes[{index}]")
        _require_keys(
            entry,
            ("id", "include_name", "start_line", "end_line", "terminating_period",
             "replacement"),
            f"includes[{index}]",
        )
        if entry["id"] in seen_include_ids:
            raise TranslationError(f"duplicate includes id {entry['id']!r}")
        seen_include_ids.add(entry["id"])
        replacement = str(entry["replacement"]).strip()
        expected_replacement_body = f"COPY {str(entry['include_name']).upper()}"
        has_period = replacement.endswith(".")
        if has_period != bool(entry["terminating_period"]):
            raise TranslationError(
                f"includes[{entry['id']}] replacement {replacement!r} period does "
                f"not agree with terminating_period={entry['terminating_period']}"
            )
        body = replacement[:-1] if has_period else replacement
        if body.upper() != expected_replacement_body and str(
            entry["include_name"]
        ).upper() not in body.upper():
            raise TranslationError(
                f"includes[{entry['id']}] replacement {replacement!r} does not "
                f"name include {entry['include_name']!r}"
            )

    seen_dml_ids = set()
    for index, raw_dml in enumerate(dml):
        entry = _require_mapping(raw_dml, f"dml[{index}]")
        _require_keys(
            entry,
            ("id", "start_line", "end_line", "terminating_period", "call_program",
             "using"),
            f"dml[{index}]",
        )
        if entry["id"] in seen_dml_ids:
            raise TranslationError(f"duplicate dml id {entry['id']!r}")
        seen_dml_ids.add(entry["id"])
        if entry["call_program"] not in call_programs:
            raise TranslationError(
                f"dml[{entry['id']}] call_program {entry['call_program']!r} is not "
                f"listed in checks.call_programs"
            )
        _require_keys(entry, ("sql_verb", "table"), f"dml[{entry['id']}]")
        verb = str(entry["sql_verb"]).strip().upper()
        if verb not in SUPPORTED_SQL_VERBS:
            raise TranslationError(
                f"dml[{entry['id']}] declares sql_verb {entry['sql_verb']!r}; the "
                f"supported verbs are {sorted(SUPPORTED_SQL_VERBS)}"
            )
        if verb == "SET":
            if entry["table"] is not None:
                raise TranslationError(
                    f"dml[{entry['id']}] is a SET statement, which names no "
                    f"table, but declares table {entry['table']!r}"
                )
        elif not str(entry["table"] or "").strip():
            raise TranslationError(
                f"dml[{entry['id']}] declares sql_verb {verb} and must name the "
                f"table it addresses"
            )
        using = _require_sequence(entry["using"], f"dml[{entry['id']}].using")
        if not using:
            raise TranslationError(
                f"dml[{entry['id']}].using declares no host variable"
            )
        seen_columns = {}
        seen_hosts = set()
        for position, raw_host in enumerate(using):
            label = f"dml[{entry['id']}].using[{position}]"
            host = _require_mapping(raw_host, label)
            _require_keys(host, ("host", "column", "direction", "pic"), label)
            name = str(host["host"]).strip().upper()
            if not name:
                raise TranslationError(f"{label} declares an empty host name")
            if name in seen_hosts:
                raise TranslationError(
                    f"{label} repeats host {host['host']!r} inside one entry"
                )
            seen_hosts.add(name)
            direction = str(host["direction"]).strip().lower()
            if direction not in HOST_DIRECTIONS:
                raise TranslationError(
                    f"{label} declares direction {host['direction']!r}; the "
                    f"supported directions are {sorted(HOST_DIRECTIONS)}"
                )
            column = normalise_sql_expression(str(host["column"]))
            if not column:
                raise TranslationError(f"{label} declares an empty column")
            if column in seen_columns:
                raise TranslationError(
                    f"{label} pairs host {host['host']!r} with column "
                    f"{host['column']!r}, already paired with host "
                    f"{seen_columns[column]!r} by the same entry"
                )
            seen_columns[column] = host["host"]
            predicate = host.get("predicate")
            if verb == "SELECT" and direction == "in":
                if not predicate:
                    raise TranslationError(
                        f"{label} is an input host of a SELECT and must declare "
                        f"the predicate fragment it appears in"
                    )
            elif predicate is not None:
                raise TranslationError(
                    f"{label} declares predicate {predicate!r}; only an input "
                    f"host of a SELECT stands in a predicate, and this entry "
                    f"declares sql_verb {verb} with direction {direction!r}"
                )
            if predicate is not None:
                parsed_fragment = parse_sql_predicate_fragment(
                    f"{label}.predicate", predicate
                )
                if parsed_fragment["column"] != column:
                    raise TranslationError(
                        f"{label}.predicate compares column "
                        f"{parsed_fragment['column']!r}; the same host declares "
                        f"column {host['column']!r}"
                    )
            _validate_presence_metadata(entry, host, label)
        non_host = entry.get("non_host_values")
        if non_host is not None:
            non_host = _require_mapping(
                non_host, f"dml[{entry['id']}].non_host_values"
            )
            for column, expression in non_host.items():
                normalised = normalise_sql_expression(str(column))
                if normalised in seen_columns:
                    raise TranslationError(
                        f"dml[{entry['id']}].non_host_values names column "
                        f"{column!r}, which host {seen_columns[normalised]!r} "
                        f"already supplies"
                    )
                if not str(expression).strip():
                    raise TranslationError(
                        f"dml[{entry['id']}].non_host_values[{column!r}] declares "
                        f"no expression"
                    )
        key = using_counts_key(entry["call_program"])
        if using_counts[key] != len(using):
            raise TranslationError(
                f"dml[{entry['id']}] declares {len(using)} host variables but "
                f"checks.using_counts[{key!r}] is {using_counts[key]}"
            )

    mapped_call_programs = {entry["call_program"] for entry in dml}
    if mapped_call_programs != set(call_programs):
        raise TranslationError(
            "the call_program values used by dml "
            f"{sorted(mapped_call_programs)} do not match checks.call_programs "
            f"{sorted(call_programs)}"
        )
    _validate_shared_call_signatures(dml)
    return {
        "path": path,
        "source_program": source_program,
        "declared_program": declared_program,
        "includes": includes,
        "dml": dml,
        "checks": checks,
    }


def index_statement_map(statement_map: dict) -> dict:
    """Index the include and dml entries by their source start line."""
    index = {}
    for kind in ("includes", "dml"):
        for entry in statement_map[kind]:
            start = int(entry["start_line"])
            if start in index:
                raise TranslationError(
                    f"statement map has two entries starting at line {start}"
                )
            index[start] = (kind, entry)
    return index


# --------------------------------------------------------------------------
# EXEC block scanning and CICS operand parsing
# --------------------------------------------------------------------------
EXEC_START_RE = re.compile(r"^(\s*)EXEC\s+(CICS|SQL)\b", re.IGNORECASE)
END_EXEC_ANYWHERE_RE = re.compile(r"END-EXEC", re.IGNORECASE)
END_EXEC_TAIL_RE = re.compile(r"\bEND-EXEC\b\s*(\.?)\s*$", re.IGNORECASE)
CICS_VERB_RE = re.compile(r"^EXEC\s+CICS\s+([A-Za-z][A-Za-z0-9\-]*)", re.IGNORECASE)
SQL_VERB_RE = re.compile(r"^EXEC\s+SQL\s+([A-Za-z][A-Za-z0-9\-]*)", re.IGNORECASE)
OPERAND_HEAD_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9]*)\s*\(")
HOST_VARIABLE_RE = re.compile(r":([A-Za-z][A-Za-z0-9\-]*)")
LENGTH_OF_RE = re.compile(r"^LENGTH\s+OF\s+([A-Za-z0-9][A-Za-z0-9\-]*)$", re.IGNORECASE)
QUOTED_LITERAL_RE = re.compile(r"^'([^']*)'$")
DATA_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9\-]*$")


def read_exec_block(lines: list, start_index: int, program: str) -> ExecBlock:
    """Consume one whole ``EXEC ... END-EXEC`` block starting at ``start_index``.

    A block is consumed as a unit, which covers the multi-line ``EXEC SQL`` /
    ``INCLUDE <name>`` / ``END-EXEC.`` form whose include name sits on its own
    line.  Comment lines inside a block and a block that never terminates are
    both reported rather than guessed at.
    """
    head = lines[start_index]
    match = EXEC_START_RE.match(code_of(head))
    if match is None:
        raise TranslationError(
            f"{program}:{start_index + 1} is not the start of an EXEC block"
        )
    indent = CODE_START + len(match.group(1))
    kind = match.group(2).upper()

    end_index = None
    body_parts = []
    for offset in range(start_index, len(lines)):
        line = lines[offset]
        if is_comment_line(line):
            raise TranslationError(
                f"{program}:{offset + 1} is a comment line inside the EXEC block "
                f"opened at line {start_index + 1}"
            )
        body_parts.append(code_of(line).strip())
        if END_EXEC_ANYWHERE_RE.search(line):
            tail = END_EXEC_TAIL_RE.search(line)
            if tail is None:
                raise TranslationError(
                    f"{program}:{offset + 1} carries END-EXEC with unexpected "
                    f"trailing text: {line!r}"
                )
            end_index = offset
            terminating_period = tail.group(1) == "."
            break
    if end_index is None:
        raise TranslationError(
            f"{program}:{start_index + 1} opens an EXEC block that is never "
            f"terminated by END-EXEC"
        )

    body = " ".join(part for part in body_parts if part)
    verb_match = (CICS_VERB_RE if kind == "CICS" else SQL_VERB_RE).match(body)
    if verb_match is None:
        raise TranslationError(
            f"{program}:{start_index + 1} EXEC {kind} block has no recognisable "
            f"verb: {body[:60]!r}"
        )
    return ExecBlock(
        kind=kind,
        verb=verb_match.group(1).upper(),
        start_line=start_index + 1,
        end_line=end_index + 1,
        indent=indent,
        terminating_period=terminating_period,
        source_lines=tuple(lines[start_index:end_index + 1]),
        body=body,
    )


def parse_cics_operands(block: ExecBlock) -> dict:
    """Parse ``KEYWORD(value)`` operands out of a flattened CICS block body.

    Keys are upper-cased keyword names, values the text between the balanced
    parentheses with surrounding whitespace removed.  A keyword that appears
    twice, or an unbalanced parenthesis, is reported.
    """
    operands = {}
    body = block.body
    position = 0
    while True:
        match = OPERAND_HEAD_RE.search(body, position)
        if match is None:
            break
        name = match.group(1).upper()
        depth = 1
        cursor = match.end()
        while cursor < len(body) and depth:
            if body[cursor] == "(":
                depth += 1
            elif body[cursor] == ")":
                depth -= 1
            cursor += 1
        if depth:
            raise TranslationError(
                f"{block.locator}: unbalanced parenthesis in operand {name!r}"
            )
        if name in operands:
            raise TranslationError(
                f"{block.locator}: operand {name!r} appears more than once"
            )
        operands[name] = body[match.end():cursor - 1].strip()
        position = cursor
    return operands


def require_operand(block: ExecBlock, operands: dict, name: str) -> str:
    value = operands.get(name)
    if not value:
        raise TranslationError(
            f"{block.locator}: EXEC CICS {block.verb} has no {name}(...) operand "
            f"(found {sorted(operands)})"
        )
    return value


def unquote_literal(block: ExecBlock, value: str, operand: str) -> str:
    match = QUOTED_LITERAL_RE.match(value)
    if match is None:
        raise TranslationError(
            f"{block.locator}: {operand}({value}) is not a quoted literal"
        )
    return match.group(1)



# --------------------------------------------------------------------------
# Single-line constructs handled outside the EXEC scanner
# --------------------------------------------------------------------------
PROCESS_DIRECTIVE_RE = re.compile(r"^\s*PROCESS\b", re.IGNORECASE)
PROCEDURE_DIVISION_RE = re.compile(
    r"^(\s*)PROCEDURE\s+DIVISION\s*\.\s*$", re.IGNORECASE
)
WORKING_STORAGE_RE = re.compile(
    r"^(\s*)WORKING-STORAGE\s+SECTION\s*\.\s*$", re.IGNORECASE
)
DFHRESP_CALL_RE = re.compile(
    r"DFHRESP\s*\(\s*([A-Za-z][A-Za-z0-9]*)\s*\)", re.IGNORECASE
)
LEVEL_01_ITEM_RE = re.compile(r"^\s*01\s+([A-Za-z0-9][A-Za-z0-9\-]*)")
DATA_ITEM_DECLARATION_RE = re.compile(
    r"^\s*(?P<level>0?[1-9]|[1-4][0-9])\s+(?P<name>[A-Za-z][A-Za-z0-9\-]*)\b"
)
VALUE_LITERAL_RE = re.compile(r"\bVALUE\s+'([^']*)'", re.IGNORECASE)
INTEGER_LITERAL_RE = re.compile(r"^[+-]?\d+$")
SQL_INCLUDE_BODY_RE = re.compile(
    r"^EXEC\s+SQL\s+INCLUDE\s+([A-Za-z0-9][A-Za-z0-9\-_]*)\s+END-EXEC\s*\.?$",
    re.IGNORECASE,
)


def discover_level_01_item(name: str, data: bytes) -> str:
    """Return the single level-01 data name declared by a harness copybook.

    Harness copybooks are UTF-8; only their comment prose uses characters
    outside ASCII, and the scan reads code lines only.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise TranslationError(f"{name} is not valid UTF-8: {error}") from error
    names = []
    for line in text.split("\n"):
        if is_comment_line(line):
            continue
        match = LEVEL_01_ITEM_RE.match(code_of(line))
        if match is not None:
            names.append(match.group(1))
    if len(names) != 1:
        raise TranslationError(
            f"{name} must declare exactly one level-01 item, found {names}"
        )
    return names[0]


# --------------------------------------------------------------------------
# Program translator
# --------------------------------------------------------------------------
class ProgramTranslator:
    """Applies rules R1-R14 to one source program, producing a generated copy.

    The translator walks the source line by line.  Comment lines and any line
    no rule claims are copied byte-for-byte (R14).  A line that opens an
    ``EXEC`` block is handed to the scanner and the whole block is replaced.
    """

    def __init__(
        self,
        name: str,
        text: str,
        statement_map: dict,
        map_index: dict,
        dfhresp_item: str,
    ) -> None:
        self.name = name
        self.text = text
        self.statement_map = statement_map
        self.map_index = map_index
        self.dfhresp_item = dfhresp_item
        self.result = None
        self.source_lines = []

    # -- entry point -------------------------------------------------------
    def translate(self) -> ProgramResult:
        lines = split_source_lines(self.text)
        self.source_lines = lines
        self.result = ProgramResult(
            source_name=self.name,
            source_line_count=len(lines),
            generated_lines=[],
            source_max_line_length=max((len(line) for line in lines), default=0),
        )
        index = 0
        while index < len(lines):
            line = lines[index]
            if is_comment_line(line):
                self.result.generated_lines.append(line)
                index += 1
                continue
            code = code_of(line)
            if EXEC_START_RE.match(code):
                block = read_exec_block(lines, index, self.name)
                self._apply_block_rule(block, lines)
                index = block.end_line
                continue
            if PROCESS_DIRECTIVE_RE.match(code):
                self._apply_r1(line, index + 1)
                index += 1
                continue
            procedure = PROCEDURE_DIVISION_RE.match(code)
            if procedure is not None:
                self._apply_r3(line, index + 1, procedure)
                index += 1
                continue
            working_storage = WORKING_STORAGE_RE.match(code)
            if working_storage is not None:
                self._apply_r4(line, index + 1)
                index += 1
                continue
            if DFHRESP_CALL_RE.search(code):
                self._apply_r12(line, index + 1)
                index += 1
                continue
            self.result.generated_lines.append(line)
            index += 1
        self._verify_census()
        return self.result

    # -- bookkeeping -------------------------------------------------------
    def _record(
        self,
        *,
        rule_id: str,
        locator: str,
        source_text: str,
        generated: list,
        notes: str,
        consumed_lines: int,
        details: dict | None = None,
    ) -> None:
        """Append the generated lines and record the site in the report.

        ``consumed_lines`` is the number of source lines the replacement
        stands in for; the corresponding line numbers are derived from
        ``locator`` and must not have been claimed by another rule.
        ``details`` carries the operand or contract values the rule enforced.
        """
        if consumed_lines:
            claimed = self._locator_line_numbers(locator)
            if len(claimed) != consumed_lines:
                raise TranslationError(
                    f"{self.name}:{locator} claims {consumed_lines} source line(s) "
                    f"but the locator spans {len(claimed)}"
                )
            overlap = self.result.consumed_line_numbers & claimed
            if overlap:
                raise TranslationError(
                    f"{self.name}: source line(s) {sorted(overlap)} are claimed by "
                    f"more than one rule"
                )
            self.result.consumed_line_numbers |= claimed
        self.result.generated_lines.extend(generated)
        self.result.generated_rule_lines += len(generated)
        self.result.rule_comment_lines.update(
            line for line in generated if is_comment_line(line)
        )
        self.result.applications.append(
            RuleApplication(
                rule_id=rule_id,
                source_lines=f"{self.name}:{locator}",
                source_text=source_text,
                generated_text="\n".join(generated),
                notes=notes,
                details=dict(details) if details else {},
            )
        )

    @staticmethod
    def _locator_line_numbers(locator: str) -> set:
        if "-" in locator:
            first, last = locator.split("-", 1)
            return set(range(int(first), int(last) + 1))
        return {int(locator)}

    def _verify_census(self) -> None:
        expected = EXPECTED_SOURCE_CENSUS.get(self.name)
        if expected is None:
            raise TranslationError(f"no expected census for {self.name}")
        if self.result.source_line_count != expected["lines"]:
            raise TranslationError(
                f"{self.name} has {self.result.source_line_count} lines, "
                f"expected {expected['lines']}"
            )
        if self.result.exec_cics_sites != expected["exec_cics"]:
            raise TranslationError(
                f"{self.name} yielded {self.result.exec_cics_sites} EXEC CICS "
                f"sites, expected {expected['exec_cics']}"
            )
        if self.result.exec_sql_blocks != expected["exec_sql"]:
            raise TranslationError(
                f"{self.name} yielded {self.result.exec_sql_blocks} EXEC SQL "
                f"blocks, expected {expected['exec_sql']}"
            )

    # -- R1: PROCESS directive --------------------------------------------
    def _apply_r1(self, line: str, line_number: int) -> None:
        """Comment the ``PROCESS`` compiler directive in the generated copy."""
        original = code_of(line).rstrip()
        generated = [emit_comment(f"{original}  {R1_NOTE}")]
        self._record(
            rule_id="R1",
            locator=str(line_number),
            source_text=line,
            generated=generated,
            notes=f"compiler directive {original!r} commented; the indicator column "
            f"carries '*' and the line stays within column {MAX_LINE_LENGTH}",
            consumed_lines=1,
        )

    # -- R3: PROCEDURE DIVISION USING DFHCOMMAREA -------------------------
    def _apply_r3(self, line: str, line_number: int, match) -> None:
        """Bind the shared COMMAREA to the procedure division header."""
        indent = CODE_START + len(match.group(1))
        generated = emit_statement(
            indent, ["PROCEDURE", "DIVISION", "USING", "DFHCOMMAREA"], True
        )
        self._record(
            rule_id="R3",
            locator=str(line_number),
            source_text=line,
            generated=generated,
            notes="PROCEDURE DIVISION bound to DFHCOMMAREA for dynamic CALL "
            "by reference",
            consumed_lines=1,
        )

    # -- R4: inserted harness declarations --------------------------------
    def _apply_r4(self, line: str, line_number: int) -> None:
        """Insert the harness declarations after WORKING-STORAGE SECTION.

        The anchor line itself is copied unchanged and this rule consumes no
        source line.  ``COPY DFHRESP.`` is added only to the one program that
        tests a CICS response condition.
        """
        declarations = list(R4_DECLARATIONS)
        if self.name == R4_DFHRESP_PROGRAM:
            declarations.append(R4_DFHRESP_DECLARATION)
        generated = []
        for declaration in declarations:
            emitted = " " * AREA_A_INDENT + declaration
            if len(emitted) > MAX_LINE_LENGTH:
                raise TranslationError(
                    f"{self.name}:{line_number} inserted declaration would reach "
                    f"column {len(emitted)}: {emitted!r}"
                )
            generated.append(emitted)
        self.result.generated_lines.append(line)
        self._record(
            rule_id="R4",
            locator=str(line_number),
            source_text=line,
            generated=generated,
            notes="inserted after the anchor line, which is copied unchanged: "
            + ", ".join(item.split()[1].rstrip(".") for item in declarations),
            consumed_lines=0,
        )

    # -- R12: DFHRESP(NORMAL) named constant ------------------------------
    def _apply_r12(self, line: str, line_number: int) -> None:
        """Replace the response-condition macro with the copybook constant."""
        conditions = [
            match.group(1).upper() for match in DFHRESP_CALL_RE.finditer(line)
        ]
        unsupported = [name for name in conditions if name != "NORMAL"]
        if unsupported:
            raise TranslationError(
                f"{self.name}:{line_number} references unsupported response "
                f"condition(s) {unsupported}; only NORMAL has a harness constant"
            )
        generated_line = DFHRESP_CALL_RE.sub(self.dfhresp_item, line)
        if len(generated_line) > MAX_LINE_LENGTH:
            raise TranslationError(
                f"{self.name}:{line_number} rewritten line would reach column "
                f"{len(generated_line)}: {generated_line!r}"
            )
        self._record(
            rule_id="R12",
            locator=str(line_number),
            source_text=line,
            generated=[generated_line],
            notes=f"DFHRESP(NORMAL) replaced by {self.dfhresp_item}; the rest of the "
            f"condition is unchanged",
            consumed_lines=1,
        )

    # -- EXEC block dispatch ----------------------------------------------
    def _apply_block_rule(self, block: ExecBlock, lines: list) -> None:
        if block.kind == "SQL":
            self.result.exec_sql_blocks += 1
            self._apply_sql_rule(block)
            return
        self.result.exec_cics_sites += 1
        handlers = {
            "RETURN": self._apply_r7,
            "ABEND": self._apply_r8,
            "WRITE": self._apply_r9,
            "ASKTIME": self._apply_r10,
            "FORMATTIME": self._apply_r11,
        }
        if block.verb == "LINK":
            self._apply_link_rule(block)
            return
        handler = handlers.get(block.verb)
        if handler is None:
            raise TranslationError(
                f"{self.name}:{block.locator}: no rule covers EXEC CICS "
                f"{block.verb}"
            )
        if block.verb == "ABEND":
            handler(block, lines)
        else:
            handler(block)

    # -- R5 / R6: LINK ----------------------------------------------------
    def _apply_link_rule(self, block: ExecBlock) -> None:
        operands = parse_cics_operands(block)
        program_operand = require_operand(block, operands, "PROGRAM")
        if QUOTED_LITERAL_RE.match(program_operand):
            self._apply_r6(block, operands, program_operand)
        else:
            self._apply_r5(block, operands, program_operand)

    def _apply_r5(self, block: ExecBlock, operands: dict, program_operand: str) -> None:
        """Chain LINK: set the shared COMMAREA length, then call dynamically.

        The site is held to one exact tuple: the PROGRAM data item's VALUE must
        be the target this program links, the COMMAREA operand must be
        DFHCOMMAREA and the LENGTH must be the shared 32,500-byte length.  The
        enforced tuple is recorded on the result for the report's chain-link
        contract.
        """
        expected_target = CHAIN_LINK_TARGETS.get(self.name)
        if expected_target is None:
            known = sorted(
                f"{name} -> {target}"
                for name, target in CHAIN_LINK_TARGETS.items()
            )
            raise TranslationError(
                f"{self.name}:{block.locator}: this program carries no chain LINK "
                f"site; the chain links are {known}"
            )
        commarea = require_operand(block, operands, "COMMAREA")
        length = require_operand(block, operands, "LENGTH")
        if not INTEGER_LITERAL_RE.match(length):
            raise TranslationError(
                f"{self.name}:{block.locator}: chain LINK LENGTH({length}) is not "
                f"an integer literal"
            )
        if int(length) != CHAIN_LINK_LENGTH:
            raise TranslationError(
                f"{self.name}:{block.locator}: chain LINK LENGTH({length}) is not "
                f"the shared COMMAREA length {CHAIN_LINK_LENGTH}"
            )
        if commarea.upper() != CHAIN_LINK_COMMAREA:
            raise TranslationError(
                f"{self.name}:{block.locator}: chain LINK COMMAREA({commarea}) is "
                f"not {CHAIN_LINK_COMMAREA}"
            )
        declared = self._resolve_program_item_value(block, program_operand)
        if declared["value"].upper() != expected_target:
            raise TranslationError(
                f"{self.name}:{block.locator}: chain LINK PROGRAM"
                f"({program_operand}) resolves to {declared['value']!r} through the "
                f"declaration at {self.name}:{declared['line']}; this site must "
                f"link {expected_target}"
            )
        generated = emit_statement(block.indent, ["MOVE", length, "TO", "EIBCALEN"])
        generated += emit_statement(
            block.indent,
            ["CALL", program_operand, "USING", commarea],
            block.terminating_period,
        )
        site = {
            "program": self.name,
            "locator": block.locator,
            "program_operand": program_operand,
            "target_program": declared["value"].upper(),
            "target_declared_at": f"{self.name}:{declared['line']}",
            "target_declaration": declared["text"],
            "commarea_operand": commarea.upper(),
            "length": int(length),
        }
        self.result.chain_links.append(site)
        self._record(
            rule_id="R5",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=f"PROGRAM({program_operand}) names a data item whose VALUE is "
            f"{declared['value']!r} at {self.name}:{declared['line']} and the "
            f"dynamic CALL passes that item; LENGTH({length}) is carried into "
            f"EIBCALEN and COMMAREA({commarea}) is passed by reference",
            consumed_lines=len(block.source_lines),
            details={"chain_link": site},
        )

    def _resolve_program_item_value(self, block: ExecBlock, item: str) -> dict:
        """Return the VALUE literal of a data item declared by this program.

        The declaration is located by its level number and name on a code line;
        its text is read to the terminating period so a declaration continued
        over several lines resolves too.  An item that is not declared, that is
        declared more than once, or that is declared without exactly one
        alphanumeric VALUE literal, is reported.
        """
        lines = self.source_lines
        declarations = []
        for index, line in enumerate(lines):
            if is_comment_line(line):
                continue
            match = DATA_ITEM_DECLARATION_RE.match(code_of(line))
            if match is None or match.group("name").upper() != item.upper():
                continue
            collected = []
            for offset in range(index, len(lines)):
                if is_comment_line(lines[offset]):
                    continue
                collected.append(code_of(lines[offset]).strip())
                if "." in code_of(lines[offset]):
                    break
            declarations.append(
                (index + 1, re.sub(r"\s+", " ", " ".join(collected)).strip())
            )
        if not declarations:
            raise TranslationError(
                f"{self.name}:{block.locator}: {item!r} is used as a LINK PROGRAM "
                f"operand but this program declares no such data item"
            )
        if len(declarations) > 1:
            raise TranslationError(
                f"{self.name}:{block.locator}: {item!r} is declared at line(s) "
                f"{[line for line, _ in declarations]}; a single declaration is "
                f"required to resolve the link target"
            )
        line_number, text = declarations[0]
        values = VALUE_LITERAL_RE.findall(text)
        if len(values) != 1:
            raise TranslationError(
                f"{self.name}:{block.locator}: the declaration of {item!r} at "
                f"{self.name}:{line_number} carries {len(values)} alphanumeric "
                f"VALUE literal(s); exactly one is required to resolve the link "
                f"target: {text!r}"
            )
        return {"line": line_number, "text": text, "value": values[0]}

    def _apply_r6(self, block: ExecBlock, operands: dict, program_operand: str) -> None:
        """Diagnostic LINK: set the area length, then call the stub."""
        literal = unquote_literal(block, program_operand, "PROGRAM")
        if literal.upper() != DIAGNOSTIC_LINK_PROGRAM:
            raise TranslationError(
                f"{self.name}:{block.locator}: LINK PROGRAM('{literal}') is not "
                f"the diagnostic program '{DIAGNOSTIC_LINK_PROGRAM}'"
            )
        area = require_operand(block, operands, "COMMAREA")
        length = require_operand(block, operands, "LENGTH")
        length_of = LENGTH_OF_RE.match(length)
        if length_of is None:
            raise TranslationError(
                f"{self.name}:{block.locator}: diagnostic LINK LENGTH({length}) is "
                f"not of the form 'LENGTH OF <item>'"
            )
        if length_of.group(1).upper() != area.upper():
            raise TranslationError(
                f"{self.name}:{block.locator}: LENGTH OF {length_of.group(1)} does "
                f"not name the COMMAREA operand {area}"
            )
        generated = emit_statement(
            block.indent, ["MOVE", "LENGTH", "OF", area, "TO", HARNESS_DIAG_LEN_ITEM]
        )
        generated += emit_statement(
            block.indent,
            ["CALL", f"'{STUB_DIAG_LINK}'", "USING", area, HARNESS_DIAG_LEN_ITEM],
            block.terminating_period,
        )
        self._record(
            rule_id="R6",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=f"diagnostic area {area} and its length are passed to "
            f"{STUB_DIAG_LINK}; the source spelling of the length operand was "
            f"{length!r}",
            consumed_lines=len(block.source_lines),
        )

    # -- R7: RETURN -------------------------------------------------------
    def _apply_r7(self, block: ExecBlock) -> None:
        """Rewrite the CICS return to GOBACK, keeping the source's period."""
        operands = parse_cics_operands(block)
        if operands:
            raise TranslationError(
                f"{self.name}:{block.locator}: EXEC CICS RETURN carries operand(s) "
                f"{sorted(operands)}, which this rule does not cover"
            )
        generated = emit_statement(block.indent, ["GOBACK"], block.terminating_period)
        self._record(
            rule_id="R7",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes="control returns to the caller at this point; the choice "
            "belongs to modernization/docs/decision-log.md (planned "
            "deliverable; not present at this milestone), row: no called "
            "RETURN stub",
            consumed_lines=len(block.source_lines),
        )

    # -- R8: ABEND --------------------------------------------------------
    def _apply_r8(self, block: ExecBlock, lines: list) -> None:
        """Capture the abend code, call the stub, then return to the caller."""
        operands = parse_cics_operands(block)
        abend_code = unquote_literal(
            block, require_operand(block, operands, "ABCODE"), "ABCODE"
        )
        generated = emit_statement(
            block.indent, ["MOVE", f"'{abend_code}'", "TO", HARNESS_ABEND_ITEM]
        )
        generated += emit_statement(
            block.indent, ["CALL", f"'{STUB_ABEND}'", "USING", HARNESS_ABEND_ITEM]
        )
        generated += emit_statement(
            block.indent, ["GOBACK"], block.terminating_period
        )
        followed_by_return = self._next_block_is_return(lines, block.end_line)
        if followed_by_return:
            self.result.abend_return_adjacencies += 1
        notes = f"abend code {abend_code!r} captured before returning"
        if "NODUMP" in block.body.upper():
            notes += "; the NODUMP option has no harness counterpart"
        if followed_by_return:
            notes += (
                f"; source line {block.end_line + 1} is an EXEC CICS RETURN that "
                f"R7 emits as a second GOBACK, which is unreachable"
            )
        self._record(
            rule_id="R8",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=notes,
            consumed_lines=len(block.source_lines),
        )

    def _next_block_is_return(self, lines: list, end_line: int) -> bool:
        """True when the very next source line opens an EXEC CICS RETURN block."""
        index = end_line
        if index >= len(lines):
            return False
        candidate = lines[index]
        if is_comment_line(candidate):
            return False
        if EXEC_START_RE.match(code_of(candidate)) is None:
            return False
        verb = CICS_VERB_RE.match(code_of(candidate).strip())
        return verb is not None and verb.group(1).upper() == "RETURN"

    # -- R9: WRITE --------------------------------------------------------
    def _apply_r9(self, block: ExecBlock) -> None:
        """Rewrite the KSDSPOLY write to the capture module.

        The site is held to one exact tuple: FILE must be the 8-character
        literal ``KSDSPOLY``, LENGTH must be 64, KEYLENGTH must be 21, FROM and
        RIDFLD must name data items and RESP must name a data item.  All six
        operands reach the capture module in source-operand order, the two
        lengths as zero-padded 5-digit alphanumeric literals.
        """
        operands = parse_cics_operands(block)
        file_name = unquote_literal(
            block, require_operand(block, operands, "FILE"), "FILE"
        )
        from_area = require_operand(block, operands, "FROM")
        ridfld = require_operand(block, operands, "RIDFLD")
        resp = require_operand(block, operands, "RESP")
        length = require_operand(block, operands, "LENGTH")
        key_length = require_operand(block, operands, "KEYLENGTH")
        if file_name != WRITE_FILE_NAME:
            raise TranslationError(
                f"{self.name}:{block.locator}: WRITE FILE('{file_name}') is not the "
                f"projection file '{WRITE_FILE_NAME}'"
            )
        if len(file_name) != WRITE_FILE_NAME_LENGTH:
            raise TranslationError(
                f"{self.name}:{block.locator}: WRITE FILE('{file_name}') is "
                f"{len(file_name)} character(s) long; the file name operand is "
                f"exactly {WRITE_FILE_NAME_LENGTH} characters"
            )
        expected_lengths = {
            "LENGTH": (length, WRITE_RECORD_LENGTH),
            "KEYLENGTH": (key_length, WRITE_KEY_LENGTH),
        }
        for label, (value, expected) in expected_lengths.items():
            if not INTEGER_LITERAL_RE.match(value):
                raise TranslationError(
                    f"{self.name}:{block.locator}: WRITE {label}({value}) is not an "
                    f"integer literal"
                )
            if int(value) != expected:
                raise TranslationError(
                    f"{self.name}:{block.locator}: WRITE {label}({value}) is not "
                    f"{expected}"
                )
        for label, value in (
            ("FROM", from_area),
            ("RIDFLD", ridfld),
            ("RESP", resp),
        ):
            if QUOTED_LITERAL_RE.match(value) or INTEGER_LITERAL_RE.match(value):
                raise TranslationError(
                    f"{self.name}:{block.locator}: WRITE {label}({value}) is a "
                    f"literal; this operand must name a data item the capture "
                    f"module can read"
                )
            if DATA_NAME_RE.match(value) is None:
                raise TranslationError(
                    f"{self.name}:{block.locator}: WRITE {label}({value}) is not a "
                    f"single data name"
                )
        length_literal = str(WRITE_RECORD_LENGTH).zfill(WRITE_LENGTH_LITERAL_DIGITS)
        key_length_literal = str(WRITE_KEY_LENGTH).zfill(WRITE_LENGTH_LITERAL_DIGITS)
        generated = emit_call_with_operand_lines(
            block.indent,
            STUB_WRITE,
            [
                f"'{file_name}'",
                from_area,
                f"'{length_literal}'",
                ridfld,
                f"'{key_length_literal}'",
                resp,
            ],
            block.terminating_period,
        )
        self._record(
            rule_id="R9",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=f"FILE('{file_name}'), FROM({from_area}), LENGTH({length}), "
            f"RIDFLD({ridfld}), KEYLENGTH({key_length}) and RESP({resp}) are all "
            f"passed to {STUB_WRITE} in source-operand order; the two lengths "
            f"travel as the {WRITE_LENGTH_LITERAL_DIGITS}-digit literals "
            f"'{length_literal}' and '{key_length_literal}'",
            consumed_lines=len(block.source_lines),
            details={
                "file_write": {
                    "program": self.name,
                    "locator": block.locator,
                    "file": file_name,
                    "file_length": len(file_name),
                    "from_item": from_area,
                    "record_length": int(length),
                    "record_length_literal": length_literal,
                    "ridfld_item": ridfld,
                    "key_length": int(key_length),
                    "key_length_literal": key_length_literal,
                    "resp_item": resp,
                    "call_program": STUB_WRITE,
                }
            },
        )

    # -- R10: ASKTIME -----------------------------------------------------
    def _apply_r10(self, block: ExecBlock) -> None:
        """Rewrite ASKTIME to the deterministic harness stub."""
        operands = parse_cics_operands(block)
        abstime = require_operand(block, operands, "ABSTIME")
        generated = emit_statement(
            block.indent,
            ["CALL", f"'{STUB_ASKTIME}'", "USING", abstime],
            block.terminating_period,
        )
        self._record(
            rule_id="R10",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=f"ABSTIME({abstime}) receives the harness clock value",
            consumed_lines=len(block.source_lines),
        )

    # -- R11: FORMATTIME --------------------------------------------------
    def _apply_r11(self, block: ExecBlock) -> None:
        """Rewrite FORMATTIME to the deterministic harness stub."""
        operands = parse_cics_operands(block)
        abstime = require_operand(block, operands, "ABSTIME")
        mmddyyyy = require_operand(block, operands, "MMDDYYYY")
        formatted_time = require_operand(block, operands, "TIME")
        generated = emit_statement(
            block.indent,
            [
                "CALL",
                f"'{STUB_FORMATTIME}'",
                "USING",
                abstime,
                mmddyyyy,
                formatted_time,
            ],
            block.terminating_period,
        )
        self._record(
            rule_id="R11",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=f"ABSTIME({abstime}) is formatted into MMDDYYYY({mmddyyyy}) and "
            f"TIME({formatted_time})",
            consumed_lines=len(block.source_lines),
        )

    # -- R2 / R13: EXEC SQL -----------------------------------------------
    def _apply_sql_rule(self, block: ExecBlock) -> None:
        declared = str(self.statement_map["source_program"].get("path", ""))
        if Path(declared).name != self.name:
            raise TranslationError(
                f"{self.name}:{block.locator}: the statement map describes "
                f"{declared!r}, so it cannot map an EXEC SQL block of this program"
            )
        mapped = self.map_index.get(block.start_line)
        if mapped is None:
            raise TranslationError(
                f"{self.name}:{block.locator}: no statement map entry starts at "
                f"line {block.start_line}"
            )
        kind, entry = mapped
        if int(entry["end_line"]) != block.end_line:
            raise TranslationError(
                f"{self.name}:{block.locator}: statement map entry "
                f"{entry['id']!r} ends at line {entry['end_line']}, the source "
                f"block ends at line {block.end_line}"
            )
        if bool(entry["terminating_period"]) != block.terminating_period:
            raise TranslationError(
                f"{self.name}:{block.locator}: statement map entry "
                f"{entry['id']!r} declares terminating_period="
                f"{entry['terminating_period']}, the source END-EXEC "
                f"{'has' if block.terminating_period else 'has no'} period"
            )
        if kind == "includes":
            self._apply_r2(block, entry)
        else:
            self._apply_r13(block, entry)

    def _apply_r2(self, block: ExecBlock, entry: dict) -> None:
        """Replace an EXEC SQL INCLUDE with the mapped COPY statement."""
        if block.verb != "INCLUDE":
            raise TranslationError(
                f"{self.name}:{block.locator}: statement map entry "
                f"{entry['id']!r} is an include but the block verb is "
                f"{block.verb}"
            )
        body = SQL_INCLUDE_BODY_RE.match(block.body)
        if body is None:
            raise TranslationError(
                f"{self.name}:{block.locator}: unrecognised EXEC SQL INCLUDE "
                f"form: {block.body!r}"
            )
        include_name = body.group(1)
        if include_name.upper() != str(entry["include_name"]).upper():
            raise TranslationError(
                f"{self.name}:{block.locator}: source includes "
                f"{include_name!r} but the statement map entry "
                f"{entry['id']!r} names {entry['include_name']!r}"
            )
        enclosing = entry.get("enclosing_group")
        enclosing_locator = None
        if enclosing is not None:
            enclosing_locator = self._require_enclosing_group(
                block, entry, str(enclosing)
            )
        replacement = str(entry["replacement"]).strip()
        words = replacement.removesuffix(".").split()
        generated = emit_statement(block.indent, words, block.terminating_period)
        notes = (
            f"statement map entry {entry['id']!r}; the COPY resolves to "
            f"{entry.get('resolves_to', 'the generated build source directory')} "
            f"under -ffold-copy=LOWER -ext cpy"
        )
        if enclosing_locator is not None:
            notes += (
                f"; the copybook is included beneath {enclosing!r} at "
                f"{enclosing_locator}"
            )
        self._record(
            rule_id="R2",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=notes,
            consumed_lines=len(block.source_lines),
            details={
                "include_contract": {
                    "entry_id": str(entry["id"]),
                    "include_name": str(entry["include_name"]),
                    "replacement": replacement,
                    "resolves_to": entry.get("resolves_to"),
                    "enclosing_group": enclosing,
                    "enclosing_group_at": enclosing_locator,
                }
            },
        )

    def _require_enclosing_group(
        self, block: ExecBlock, entry: dict, declared: str
    ) -> str:
        """Assert the code line before the block is the declared group item.

        The nearest preceding line that is neither a comment nor blank must be
        the ``enclosing_group`` the map declares, compared with runs of
        whitespace collapsed and letter case folded.  Returns that line's
        locator.
        """
        expected = re.sub(r"\s+", " ", declared).strip()
        for index in range(block.start_line - 2, -1, -1):
            line = self.source_lines[index]
            if is_comment_line(line) or not code_of(line).strip():
                continue
            found = re.sub(r"\s+", " ", code_of(line)).strip()
            if found.upper() != expected.upper():
                raise TranslationError(
                    f"{self.name}:{block.locator}: statement map entry "
                    f"{entry['id']!r} declares enclosing_group {expected!r} but "
                    f"line {index + 1} of the source holds {found!r}"
                )
            return f"{self.name}:{index + 1}"
        raise TranslationError(
            f"{self.name}:{block.locator}: statement map entry {entry['id']!r} "
            f"declares enclosing_group {expected!r} but no code line precedes "
            f"the block"
        )

    def _apply_r13(self, block: ExecBlock, entry: dict) -> None:
        """Replace an EXEC SQL DML block with the mapped stub CALL.

        The block's SQL text is compared with the mapped contract first: verb,
        table, ordered column list, ordered host list with declared directions
        and positions, the complete predicate region against the declared
        predicate, and non-host column expressions.  The source must reference
        exactly the hosts the map marks as present in this block; a mapped host
        that ``present_in_source_block`` marks as absent from this block is
        still passed to the stub, as a superset argument.
        """
        contract = validate_sql_contract(self.name, block, entry)
        hosts = [str(item["host"]) for item in entry["using"]]
        superset = list(contract["hosts_omitted"])
        generated = emit_call_with_operand_lines(
            block.indent,
            str(entry["call_program"]),
            hosts,
            block.terminating_period,
        )
        notes = (
            f"statement map entry {entry['id']!r} -> {entry['call_program']}; "
            f"{len(hosts)} host variable(s) passed by reference in source order; "
            f"{contract['sql_verb']} contract verified against the source block"
        )
        if contract["predicates"]:
            enforced = " ".join(
                token
                for condition in contract["predicates"]
                for token in condition["tokens"]
            )
            notes += f"; predicate held to {enforced}"
        else:
            notes += "; no predicate declared and none found"
        if superset:
            notes += (
                f"; superset argument(s) {superset} appear in the mapped USING "
                f"list but not in this source branch"
            )
        non_host = entry.get("non_host_values")
        if non_host:
            rendered = ", ".join(
                f"{column}={value}" for column, value in non_host.items()
            )
            notes += f"; column(s) supplied by an SQL expression: {rendered}"
        self._record(
            rule_id="R13",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=notes,
            consumed_lines=len(block.source_lines),
            details={
                "call_program": str(entry["call_program"]),
                "using": hosts,
                "sql_contract": contract,
            },
        )



# --------------------------------------------------------------------------
# Post-generation verification
# --------------------------------------------------------------------------
def verify_generated_lines(name: str, lines: list) -> None:
    """Check every generated line against the fixed-format reference format."""
    for number, line in enumerate(lines, start=1):
        if "\t" in line:
            raise TranslationError(f"{name}:{number} contains a tab character")
        if len(line) > MAX_LINE_LENGTH:
            raise TranslationError(
                f"{name}:{number} reaches column {len(line)}, past column "
                f"{MAX_LINE_LENGTH}: {line!r}"
            )
        if not line:
            continue
        if len(line) < CODE_START:
            raise TranslationError(
                f"{name}:{number} is {len(line)} character(s) long; a non-empty "
                f"line must reach the indicator column at column "
                f"{INDICATOR_INDEX + 1}: {line!r}"
            )
        sequence_area = line[:SEQUENCE_AREA_WIDTH]
        invalid = [
            character
            for character in sequence_area
            if character not in SEQUENCE_AREA_CHARS
        ]
        if invalid:
            raise TranslationError(
                f"{name}:{number} sequence area holds invalid character(s) "
                f"{invalid}: {line!r}"
            )
        indicator = line[INDICATOR_INDEX]
        if indicator not in VALID_INDICATORS:
            raise TranslationError(
                f"{name}:{number} indicator column holds {indicator!r}; expected "
                f"one of {sorted(VALID_INDICATORS)}"
            )


def verify_no_forbidden_tokens(name: str, lines: list, allowed_comments: set) -> dict:
    """Assert no untranslated CICS, SQL or directive construct survives.

    A forbidden token on any code line is a hard failure.  A forbidden token
    inside a comment line is accepted only when that exact comment line was
    emitted by a recorded rule, which is how the commented ``PROCESS``
    directive of rule R1 is accounted for; every other comment occurrence is a
    failure.  Returns the accounted-for comment occurrences.
    """
    accounted = {}
    for number, line in enumerate(lines, start=1):
        for label, pattern in FORBIDDEN_GENERATED_PATTERNS:
            if not pattern.search(line):
                continue
            if not is_comment_line(line):
                raise TranslationError(
                    f"{name}:{number} still carries the active construct "
                    f"{label!r}: {line!r}"
                )
            if line not in allowed_comments:
                raise TranslationError(
                    f"{name}:{number} carries the token {label!r} in a comment "
                    f"that no rule emitted: {line!r}"
                )
            accounted.setdefault(label, []).append(number)
    return accounted


def verify_carry_through(result: ProgramResult, source_lines: list) -> None:
    """Assert every unclaimed source line reaches the copy byte-for-byte.

    The lines no rule claimed must appear, in order and unmodified, inside the
    generated output, and the generated output must hold exactly those lines
    plus the lines the rules emitted.
    """
    carry_through = [
        line
        for number, line in enumerate(source_lines, start=1)
        if number not in result.consumed_line_numbers
    ]
    expected_total = len(carry_through) + result.generated_rule_lines
    if len(result.generated_lines) != expected_total:
        raise TranslationError(
            f"{result.source_name}: generated {len(result.generated_lines)} lines "
            f"but {len(carry_through)} carried-through plus "
            f"{result.generated_rule_lines} rule-emitted lines is {expected_total}"
        )
    cursor = 0
    for line in result.generated_lines:
        if cursor < len(carry_through) and line == carry_through[cursor]:
            cursor += 1
    if cursor != len(carry_through):
        raise TranslationError(
            f"{result.source_name}: only {cursor} of {len(carry_through)} "
            f"unclaimed source lines were carried through unchanged; first "
            f"missing line is {carry_through[cursor]!r}"
        )


def verify_structural_counts(generated: dict) -> dict:
    """Count the mandated generated constructs across every generated program."""
    observed = dict.fromkeys(EXPECTED_STRUCTURAL_COUNTS, 0)
    for lines in generated.values():
        for line in lines:
            if is_comment_line(line):
                continue
            code = code_of(line)
            for label, pattern in STRUCTURAL_PATTERNS.items():
                if pattern.match(code):
                    observed[label] += 1
    for label, expected in EXPECTED_STRUCTURAL_COUNTS.items():
        if observed[label] != expected:
            raise TranslationError(
                f"generated tree holds {observed[label]} occurrence(s) of "
                f"{label!r}, expected {expected}"
            )
    return observed


def verify_copy_resolution(generated: dict, build_tree: BuildTree) -> list:
    """Assert every generated COPY name resolves inside the build source dir."""
    resolved = []
    for name, lines in generated.items():
        for number, line in enumerate(lines, start=1):
            if is_comment_line(line):
                continue
            match = ANY_COPY_PATTERN.match(code_of(line))
            if match is None:
                continue
            member = match.group(1)
            candidate = build_tree.path_for(f"src/{member.lower()}.cpy")
            if not candidate.is_file():
                raise TranslationError(
                    f"{name}:{number} copies {member!r} but {candidate} does not "
                    f"exist; a single -I on the build source directory would not "
                    f"resolve it"
                )
            resolved.append({"program": name, "line": number, "member": member})
    return resolved


def verify_rule_totals(results: list) -> dict:
    """Aggregate and check the per-rule site counts and the block totals."""
    observed = dict.fromkeys(EXPECTED_RULE_SITES, 0)
    for result in results:
        for application in result.applications:
            if application.rule_id not in observed:
                raise TranslationError(
                    f"unknown rule id {application.rule_id!r} in the report"
                )
            observed[application.rule_id] += 1
    for rule, expected in EXPECTED_RULE_SITES.items():
        if observed[rule] != expected:
            raise TranslationError(
                f"rule {rule} was applied {observed[rule]} time(s), expected "
                f"{expected}"
            )

    cics_sites = sum(result.exec_cics_sites for result in results)
    sql_blocks = sum(result.exec_sql_blocks for result in results)
    if cics_sites != EXPECTED_TOTAL_CICS_SITES:
        raise TranslationError(
            f"rewrote {cics_sites} EXEC CICS site(s), expected "
            f"{EXPECTED_TOTAL_CICS_SITES}"
        )
    if sql_blocks != EXPECTED_TOTAL_SQL_BLOCKS:
        raise TranslationError(
            f"rewrote {sql_blocks} EXEC SQL block(s), expected "
            f"{EXPECTED_TOTAL_SQL_BLOCKS}"
        )

    cics_rules = ("R5", "R6", "R7", "R8", "R9", "R10", "R11")
    cics_from_rules = sum(observed[rule] for rule in cics_rules)
    if cics_from_rules != cics_sites:
        raise TranslationError(
            f"CICS rules account for {cics_from_rules} site(s) but "
            f"{cics_sites} EXEC CICS block(s) were scanned"
        )
    sql_from_rules = observed["R2"] + observed["R13"]
    if sql_from_rules != sql_blocks:
        raise TranslationError(
            f"SQL rules account for {sql_from_rules} block(s) but "
            f"{sql_blocks} EXEC SQL block(s) were scanned"
        )
    return {
        "per_rule": observed,
        "exec_cics_sites": cics_sites,
        "exec_sql_blocks": sql_blocks,
    }


def verify_chain_link_contract(results: list) -> dict:
    """Aggregate the chain LINK sites and check the whole chain is present.

    Each program that carries a chain link must carry exactly one, to the
    target that program links, with the shared COMMAREA operand and the shared
    32,500-byte length.  The returned block is the machine-readable chain-link
    contract the report publishes for the runner to cross-check.
    """
    sites = []
    for result in results:
        for site in result.chain_links:
            sites.append(site)
    by_program = {}
    for site in sites:
        by_program.setdefault(site["program"], []).append(site)
    for program, target in sorted(CHAIN_LINK_TARGETS.items()):
        found = by_program.get(program, [])
        if len(found) != 1:
            raise TranslationError(
                f"{program} carries {len(found)} chain LINK site(s), expected "
                f"exactly one linking {target}"
            )
        site = found[0]
        if site["target_program"] != target:
            raise TranslationError(
                f"{program}:{site['locator']} links {site['target_program']}, "
                f"expected {target}"
            )
        if site["commarea_operand"] != CHAIN_LINK_COMMAREA:
            raise TranslationError(
                f"{program}:{site['locator']} passes COMMAREA"
                f"({site['commarea_operand']}), expected {CHAIN_LINK_COMMAREA}"
            )
        if site["length"] != CHAIN_LINK_LENGTH:
            raise TranslationError(
                f"{program}:{site['locator']} passes LENGTH({site['length']}), "
                f"expected {CHAIN_LINK_LENGTH}"
            )
    unexpected = sorted(set(by_program) - set(CHAIN_LINK_TARGETS))
    if unexpected:
        raise TranslationError(
            f"chain LINK site(s) found in {unexpected}, which the chain does not "
            f"link through"
        )
    return {
        "expected_sites": len(CHAIN_LINK_TARGETS),
        "observed_sites": len(sites),
        "commarea_operand": CHAIN_LINK_COMMAREA,
        "length": CHAIN_LINK_LENGTH,
        "expected_targets": {
            program: target for program, target in sorted(CHAIN_LINK_TARGETS.items())
        },
        "sites": sorted(sites, key=lambda site: (site["program"], site["locator"])),
    }


def verify_declared_source_census(statement_map: dict, results: list) -> None:
    """Compare the map's declared census with the figures measured this run.

    The program named by ``source_program.path`` must be one of the programs
    just translated, and its declared line total, EXEC CICS block count, EXEC
    SQL block count and longest line must equal the values measured from the
    bytes read for that program.  Each mismatch names the member, the declared
    value and the measured one.
    """
    declared = statement_map["source_program"]
    name = statement_map["declared_program"]
    measured = {result.source_name: result for result in results}
    result = measured.get(name)
    if result is None:
        raise TranslationError(
            f"source_program.path names {name!r}, which is not among the "
            f"translated programs {sorted(measured)}"
        )
    for key, measured_value in (
        ("total_lines", result.source_line_count),
        ("exec_cics_blocks", result.exec_cics_sites),
        ("exec_sql_blocks", result.exec_sql_blocks),
        ("max_line_length", result.source_max_line_length),
    ):
        declared_value = _require_integer(declared[key], f"source_program.{key}")
        if declared_value != measured_value:
            raise TranslationError(
                f"source_program.{key} is {declared_value}, measured "
                f"{measured_value} in {name}"
            )


def verify_sources_unchanged(source_dir: Path, baseline: dict) -> None:
    """Re-read every authorized source and assert its digest is unchanged."""
    for name, digest in baseline.items():
        current = sha256_of_bytes(read_authorized_source(source_dir, name))
        if current != digest:
            raise TranslationError(
                f"{source_dir / name} changed during the run: digest was "
                f"{digest}, is now {current}"
            )


def verify_no_tracked_source_modification(source_dir: Path) -> dict:
    """Assert git reports no working-tree change under the source directory.

    The check runs whenever the source directory lies inside the repository,
    which is the case for the default ``base/src``.  For a source directory
    outside the repository the result records ``checked`` false with the
    reason; the path-independent digest re-verification covers that case.
    """
    resolved = source_dir.resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT)
    except ValueError:
        return {
            "checked": False,
            "pathspec": resolved.as_posix(),
            "reason": (
                f"source directory is outside the repository at {REPO_ROOT}; "
                f"there is no tracked state to inspect"
            ),
        }
    pathspec = f"{relative.as_posix()}/"
    command = ["git", "status", "--porcelain", "--", pathspec]
    try:
        completed = subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise TranslationError(
            f"cannot verify the read-only guard: running {' '.join(command)} "
            f"failed ({error})"
        ) from error
    if completed.returncode != 0:
        raise TranslationError(
            f"cannot verify the read-only guard: {' '.join(command)} exited "
            f"{completed.returncode}: {completed.stderr.strip()}"
        )
    if completed.stdout.strip():
        raise TranslationError(
            f"git reports a working-tree change under {pathspec}:\n"
            f"{completed.stdout.rstrip()}"
        )
    return {"checked": True, "pathspec": pathspec, "reported_changes": 0}


# --------------------------------------------------------------------------
# Evidence files
# --------------------------------------------------------------------------
def render_baseline(source_dir: Path, baseline: dict) -> str:
    """Render the source digests in ``sha256sum -c`` format."""
    try:
        relative = source_dir.resolve().relative_to(REPO_ROOT)
    except ValueError:
        relative = source_dir.resolve()
    rows = []
    for name in sorted(baseline):
        rows.append(f"{baseline[name]}  {(relative / name).as_posix()}")
    return "\n".join(rows) + "\n"


def repo_relative(path: Path) -> str:
    """Render a path relative to the repository root when it lies inside it."""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def build_report(
    *,
    source_dir: Path,
    build_tree: BuildTree,
    statement_map_path: Path,
    copybook_dir: Path,
    baseline: dict,
    copybook_digests: dict,
    verbatim_copies: list,
    results: list,
    totals: dict,
    structural_counts: dict,
    resolved_copies: list,
    dfhresp_item: str,
    git_check: dict,
    commented_tokens: dict,
    chain_link_contract: dict,
) -> dict:
    """Assemble the translation report.

    The per-program application lists and the per-rule totals account for
    every rewritten construct and for every source line carried through
    unchanged, which is the coverage
    ``modernization/docs/traceability-matrix.md`` consumes.
    ``chain_link_contract`` publishes the nested link events - target program,
    COMMAREA operand and length per site - for the runner to cross-check.
    """
    programs = []
    for result in results:
        programs.append(
            {
                "source": repo_relative(source_dir / result.source_name),
                "generated": repo_relative(
                    build_tree.path_for(f"src/{result.source_name}")
                ),
                "source_lines": result.source_line_count,
                "generated_lines": len(result.generated_lines),
                "exec_cics_sites": result.exec_cics_sites,
                "exec_sql_blocks": result.exec_sql_blocks,
                "rewritten_source_lines": result.consumed_source_lines,
                "unchanged_source_lines": result.unchanged_source_lines,
                "rule_emitted_lines": result.generated_rule_lines,
                "abend_sites_followed_by_return": result.abend_return_adjacencies,
                "applications": [
                    application.as_dict() for application in result.applications
                ],
            }
        )
    per_rule = {
        rule: {"expected": expected, "observed": totals["per_rule"][rule]}
        for rule, expected in EXPECTED_RULE_SITES.items()
    }
    per_rule[RULE_R14] = {
        "expected": sum(result.unchanged_source_lines for result in results),
        "observed": sum(result.unchanged_source_lines for result in results),
        "unit": "source lines carried through byte-for-byte",
    }
    return {
        "schema_version": 1,
        "translator": repo_relative(Path(__file__)),
        "inputs": {
            "source_dir": repo_relative(source_dir),
            "build_dir": repo_relative(build_tree.root),
            "statement_map": repo_relative(statement_map_path),
            "copybook_dir": repo_relative(copybook_dir),
        },
        "source_baseline": {
            name: {
                "path": repo_relative(source_dir / name),
                "sha256": digest,
            }
            for name, digest in sorted(baseline.items())
        },
        "harness_copybooks": {
            name: {
                "path": repo_relative(copybook_dir / name),
                "sha256": digest,
            }
            for name, digest in sorted(copybook_digests.items())
        },
        "verbatim_copies": verbatim_copies,
        "programs": programs,
        "rule_totals": per_rule,
        "totals": {
            "exec_cics_sites": totals["exec_cics_sites"],
            "exec_sql_blocks": totals["exec_sql_blocks"],
            "expected_exec_cics_sites": EXPECTED_TOTAL_CICS_SITES,
            "expected_exec_sql_blocks": EXPECTED_TOTAL_SQL_BLOCKS,
            "abend_sites_followed_by_return": sum(
                result.abend_return_adjacencies for result in results
            ),
        },
        "structural_counts": {
            label: {"expected": EXPECTED_STRUCTURAL_COUNTS[label], "observed": count}
            for label, count in sorted(structural_counts.items())
        },
        "resolved_copies": resolved_copies,
        "chain_link_contract": chain_link_contract,
        "response_condition_item": dfhresp_item,
        "commented_source_tokens": {
            program: occurrences
            for program, occurrences in sorted(commented_tokens.items())
            if occurrences
        },
        "read_only_checks": {
            "source_digests_reverified": True,
            "git_working_tree": git_check,
        },
    }



# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
def resolve_input_path(value: str) -> Path:
    """Resolve a CLI path against the repository root, not the working dir."""
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate


def translate_all(
    source_dir: Path,
    build_dir: Path,
    statement_map_path: Path,
    copybook_dir: Path,
    report_path: Path | None,
) -> dict:
    """Run the whole generation and verification sequence.

    Ordering: contain the three read inputs, validate the statement map, read
    and digest the authorized sources and the harness copybooks, prepare the
    build tree - which invalidates any report of an earlier run before it
    resets the generated sources, and stops the run without touching them when
    that report cannot be invalidated - write the baseline, place the verbatim
    copies, translate the three programs, verify the generated tree against the
    rules and against the declared census, re-verify the sources, then write
    the report.
    """
    if not source_dir.is_dir():
        raise TranslationError(f"source directory not found: {source_dir}")
    if not copybook_dir.is_dir():
        raise TranslationError(f"copybook directory not found: {copybook_dir}")
    require_expected_read_directory(source_dir, EXPECTED_SOURCE_DIR, "--source-dir")
    require_expected_read_directory(
        copybook_dir, EXPECTED_COPYBOOK_DIR, "--copybook-dir"
    )
    require_expected_read_file(
        statement_map_path, EXPECTED_STATEMENT_MAP, "--statement-map"
    )
    if report_path is not None:
        expected_report = (CANONICAL_BUILD_ROOT / REPORT_RELATIVE).resolve()
        if report_path.resolve() != expected_report:
            raise TranslationError(
                f"--report names {report_path.resolve()}; the report of a run is "
                f"published only as {expected_report}"
            )

    build_tree = BuildTree(build_dir)
    statement_map = load_statement_map(statement_map_path)
    map_index = index_statement_map(statement_map)

    source_bytes = {
        name: read_authorized_source(source_dir, name)
        for name in sorted(SOURCE_ALLOW_LIST)
    }
    baseline = {
        name: sha256_of_bytes(data) for name, data in source_bytes.items()
    }
    copybook_bytes = {
        name: read_harness_copybook(copybook_dir, name) for name in HARNESS_COPYBOOKS
    }
    copybook_digests = {
        name: sha256_of_bytes(data) for name, data in copybook_bytes.items()
    }
    dfhresp_item = discover_level_01_item("dfhresp.cpy", copybook_bytes["dfhresp.cpy"])

    build_tree.prepare()
    baseline_path = build_tree.write_text(
        BASELINE_RELATIVE, render_baseline(source_dir, baseline)
    )

    verbatim_copies = []
    for name in VERBATIM_SOURCE_COPYBOOKS:
        target = build_tree.copy_verbatim(
            f"src/{name}", source_bytes[name], baseline[name]
        )
        verbatim_copies.append(
            {
                "origin": repo_relative(source_dir / name),
                "copy": repo_relative(target),
                "sha256": baseline[name],
                "kind": "authorized source copybook",
            }
        )
    for name in HARNESS_COPYBOOKS:
        target = build_tree.copy_verbatim(
            f"src/{name}", copybook_bytes[name], copybook_digests[name]
        )
        verbatim_copies.append(
            {
                "origin": repo_relative(copybook_dir / name),
                "copy": repo_relative(target),
                "sha256": copybook_digests[name],
                "kind": "harness copybook",
            }
        )

    results = []
    generated = {}
    commented_tokens = {}
    for name in PROGRAM_SOURCES:
        text = source_bytes[name].decode("ascii")
        source_lines = split_source_lines(text)
        translator = ProgramTranslator(
            name=name,
            text=text,
            statement_map=statement_map,
            map_index=map_index,
            dfhresp_item=dfhresp_item,
        )
        result = translator.translate()
        verify_generated_lines(name, result.generated_lines)
        commented_tokens[name] = verify_no_forbidden_tokens(
            name, result.generated_lines, result.rule_comment_lines
        )
        verify_carry_through(result, source_lines)
        build_tree.write_text(
            f"src/{name}", "\n".join(result.generated_lines) + "\n"
        )
        results.append(result)
        generated[name] = result.generated_lines

    structural_counts = verify_structural_counts(generated)
    resolved_copies = verify_copy_resolution(generated, build_tree)
    totals = verify_rule_totals(results)
    chain_link_contract = verify_chain_link_contract(results)
    verify_declared_source_census(statement_map, results)
    verify_sources_unchanged(source_dir, baseline)
    git_check = verify_no_tracked_source_modification(source_dir)

    report = build_report(
        source_dir=source_dir,
        build_tree=build_tree,
        statement_map_path=statement_map_path,
        copybook_dir=copybook_dir,
        baseline=baseline,
        copybook_digests=copybook_digests,
        verbatim_copies=verbatim_copies,
        results=results,
        totals=totals,
        structural_counts=structural_counts,
        resolved_copies=resolved_copies,
        dfhresp_item=dfhresp_item,
        git_check=git_check,
        commented_tokens=commented_tokens,
        chain_link_contract=chain_link_contract,
    )
    if report_path is None:
        report_relative = REPORT_RELATIVE
    else:
        resolved_report = Path(report_path).expanduser().resolve()
        try:
            report_relative = resolved_report.relative_to(build_tree.root).as_posix()
        except ValueError as error:
            raise TranslationError(
                f"refusing to write the report to {resolved_report}: it is not "
                f"inside {build_tree.root}"
            ) from error
    written_report = build_tree.write_text(
        report_relative, json.dumps(report, indent=2, sort_keys=False) + "\n"
    )

    return {
        "build_dir": build_tree.root,
        "baseline_path": baseline_path,
        "report_path": written_report,
        "results": results,
        "totals": totals,
        "verbatim_copies": verbatim_copies,
        "dfhresp_item": dfhresp_item,
        "chain_link_contract": chain_link_contract,
    }


def summarise(outcome: dict) -> str:
    """Render the one-block success summary written to standard output."""
    lines = [
        (
            f"translate.py: generated {len(outcome['results'])} program(s) into "
            f"{repo_relative(outcome['build_dir'])}/src"
        ),
    ]
    for result in outcome["results"]:
        lines.append(
            f"  {result.source_name}: {result.source_line_count} source line(s) -> "
            f"{len(result.generated_lines)} generated line(s); "
            f"{result.exec_cics_sites} EXEC CICS site(s), "
            f"{result.exec_sql_blocks} EXEC SQL block(s), "
            f"{result.unchanged_source_lines} line(s) copied unchanged"
        )
    per_rule = outcome["totals"]["per_rule"]
    lines.append(
        "  rules applied: "
        + ", ".join(f"{rule}={per_rule[rule]}" for rule in EXPECTED_RULE_SITES)
    )
    for site in outcome["chain_link_contract"]["sites"]:
        lines.append(
            f"  chain link {site['program']}:{site['locator']} -> "
            f"{site['target_program']} via {site['program_operand']} declared at "
            f"{site['target_declared_at']}; COMMAREA {site['commarea_operand']}, "
            f"LENGTH {site['length']}"
        )
    lines.append(
        f"  verbatim copies: {len(outcome['verbatim_copies'])}; "
        f"response-condition item: {outcome['dfhresp_item']}"
    )
    lines.append(f"  baseline: {repo_relative(outcome['baseline_path'])}")
    lines.append(f"  report:   {repo_relative(outcome['report_path'])}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="translate.py",
        description=(
            "Translate read-only copies of the named CICS/Db2 programs into "
            "GnuCOBOL-compilable form under the harness build tree. Relative "
            "paths resolve against the repository root."
        ),
        epilog=(
            "Writes the generated programs, the verbatim copybooks, the source "
            "SHA-256 baseline and the translation report; exits non-zero on any "
            "rule, count or guard failure."
        ),
    )
    parser.add_argument(
        "--source-dir",
        default=DEFAULT_SOURCE_DIR,
        metavar="DIR",
        help=(
            "directory holding the five authorized source files "
            f"(default: {DEFAULT_SOURCE_DIR})"
        ),
    )
    parser.add_argument(
        "--build-dir",
        default=DEFAULT_BUILD_DIR,
        metavar="DIR",
        help=(
            "generated harness build tree; it must resolve to "
            f"{DEFAULT_BUILD_DIR} of this checkout, reached through real "
            f"directories (default: {DEFAULT_BUILD_DIR})"
        ),
    )
    parser.add_argument(
        "--statement-map",
        default=DEFAULT_STATEMENT_MAP,
        metavar="FILE",
        help=(
            "EXEC SQL block map driving rules R2 and R13; it must resolve to "
            f"{DEFAULT_STATEMENT_MAP} of this checkout and be a regular file "
            f"rather than a symbolic link (default: {DEFAULT_STATEMENT_MAP})"
        ),
    )
    parser.add_argument(
        "--copybook-dir",
        default=DEFAULT_COPYBOOK_DIR,
        metavar="DIR",
        help=(
            "directory holding "
            + ", ".join(HARNESS_COPYBOOKS)
            + f" (default: {DEFAULT_COPYBOOK_DIR})"
        ),
    )
    parser.add_argument(
        "--report",
        default=None,
        metavar="FILE",
        help=(
            "translation report path, which must lie inside the build tree "
            f"(default: <build-dir>/{REPORT_RELATIVE})"
        ),
    )
    return parser


def one_line(text: str, limit: int = 400) -> str:
    """Render ``text`` as one bounded line of printable ASCII.

    Every byte outside printable ASCII, including the line separators a
    supplied value could carry, is rendered as ``\\xNN``, so a diagnostic that
    quotes a caller-supplied value cannot forge additional log lines.
    """
    rendered = []
    for character in str(text):
        if character == " " or ("!" <= character <= "~"):
            rendered.append(character)
        else:
            for byte in character.encode("utf-8", "surrogatepass"):
                rendered.append(f"\\x{byte:02x}")
    line = "".join(rendered)
    if len(line) > limit:
        line = line[: limit - 3] + "..."
    return line


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        outcome = translate_all(
            source_dir=resolve_input_path(args.source_dir),
            build_dir=resolve_input_path(args.build_dir),
            statement_map_path=resolve_input_path(args.statement_map),
            copybook_dir=resolve_input_path(args.copybook_dir),
            report_path=(
                resolve_input_path(args.report) if args.report is not None else None
            ),
        )
    except TranslationError as error:
        print(f"translate.py: error: {one_line(error)}", file=sys.stderr)
        return 1
    except yaml.YAMLError as error:
        print(
            "translate.py: error: statement map is not valid YAML: "
            f"{one_line(error)}",
            file=sys.stderr,
        )
        return 1
    except OSError as error:
        print(f"translate.py: error: {one_line(error)}", file=sys.stderr)
        return 1
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as error:
        print(
            "translate.py: error: the statement map or a source held a value this "
            f"translator cannot use: {one_line(f'{type(error).__name__}: {error}')}",
            file=sys.stderr,
        )
        return 1
    print(summarise(outcome))
    return 0


if __name__ == "__main__":
    sys.exit(main())
