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
carried through unchanged.  The reasoning behind the translation strategy is
recorded in ``modernization/docs/decision-log.md``; this module states only
what it does.  Harness topology is Figure 5 "Validation Harness Control Flow"
in ``modernization/docs/architecture.md``.
"""

import argparse
import hashlib
import json
import re
import shutil
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

# --------------------------------------------------------------------------
# Write-path guard
# --------------------------------------------------------------------------
# Every write goes through BuildTree, whose root must resolve to a path whose
# final three components are exactly these.  modernization/.gitignore ignores
# /harness/build/; the guard confines every write to that directory.
BUILD_DIR_TAIL = ("modernization", "harness", "build")
BUILD_SUBDIRS = ("src", "bin", "samples", "logs", "run")

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
    "lgapol01.cbl": {"lines": 169, "exec_cics": 9, "exec_sql": 0},
    "lgapdb01.cbl": {"lines": 595, "exec_cics": 20, "exec_sql": 11},
    "lgapvs01.cbl": {"lines": 188, "exec_cics": 7, "exec_sql": 0},
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
    """One applied rewrite site, as recorded in the JSON report."""

    rule_id: str
    source_lines: str
    source_text: str
    generated_text: str
    notes: str

    def as_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "source_lines": self.source_lines,
            "source_text": self.source_text,
            "generated_text": self.generated_text,
            "notes": self.notes,
        }


@dataclass
class ProgramResult:
    """Generation outcome for one translated program."""

    source_name: str
    source_line_count: int
    generated_lines: list
    applications: list = field(default_factory=list)
    consumed_line_numbers: set = field(default_factory=set)
    rule_comment_lines: set = field(default_factory=set)
    exec_cics_sites: int = 0
    exec_sql_blocks: int = 0
    generated_rule_lines: int = 0
    abend_return_adjacencies: int = 0

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


def read_authorized_source(source_dir: Path, name: str) -> bytes:
    """Read one allow-listed source file in binary mode.

    Refuses any name outside SOURCE_ALLOW_LIST, any name carrying a path
    separator, and any path that resolves outside ``source_dir``.
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
        return handle.read()


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

    Construction fails unless the resolved root's final three path components
    are ``modernization/harness/build``, and every write is checked to land
    inside that root.
    """

    def __init__(self, root: Path) -> None:
        resolved = root.expanduser().resolve()
        if tuple(part.lower() for part in resolved.parts[-3:]) != BUILD_DIR_TAIL:
            raise TranslationError(
                f"refusing to write to {resolved}: the build directory must end "
                f"with {'/'.join(BUILD_DIR_TAIL)}"
            )
        self.root = resolved

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

    def prepare(self) -> None:
        """Create the build subdirectories and reset the generated source dir.

        ``src`` is removed and recreated; afterwards it holds only files
        written by the current run.
        """
        self.root.mkdir(parents=True, exist_ok=True)
        src_dir = self.path_for("src")
        if src_dir.exists():
            if not src_dir.is_dir():
                raise TranslationError(f"{src_dir} exists and is not a directory")
            shutil.rmtree(src_dir)
        for name in BUILD_SUBDIRS:
            self.path_for(name).mkdir(parents=True, exist_ok=True)

    def write_text(self, relative: str, text: str) -> Path:
        """Write ASCII text with LF endings; non-ASCII content is reported."""
        target = self.path_for(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            encoded = text.encode("ascii")
        except UnicodeEncodeError as error:
            raise TranslationError(
                f"refusing to write non-ASCII content to {target}: {error}"
            ) from error
        with target.open("wb") as handle:
            handle.write(encoded)
        return target

    def write_bytes(self, relative: str, data: bytes) -> Path:
        target = self.path_for(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as handle:
            handle.write(data)
        return target

    def copy_verbatim(self, relative: str, data: bytes, expected_digest: str) -> Path:
        """Write ``data`` and assert the written copy's digest is unchanged."""
        target = self.write_bytes(relative, data)
        with target.open("rb") as handle:
            written = sha256_of_bytes(handle.read())
        if written != expected_digest:
            raise TranslationError(
                f"verbatim copy {target} digest {written} does not match source "
                f"digest {expected_digest}"
            )
        return target



# --------------------------------------------------------------------------
# statement_map.yml
# --------------------------------------------------------------------------
def using_counts_key(call_program: str) -> str:
    """Map a stub program name onto its ``checks.using_counts`` key.

    ``SQL-INSERT-ENDOWMENT`` yields ``insert_endowment``, which is why the two
    endowment branches share a single key while remaining two dml entries.
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


def load_statement_map(path: Path) -> dict:
    """Load and validate ``statement_map.yml`` before any generation happens.

    Checks the ``checks`` block against the expected census (3 includes, 8 dml
    entries, 11 blocks in total, one ``using_counts`` entry per stub and seven
    ``call_programs``) and the internal consistency of every entry.
    """
    if not path.is_file():
        raise TranslationError(f"statement map not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    data = _require_mapping(data, f"{path}")

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
        using = _require_sequence(entry["using"], f"dml[{entry['id']}].using")
        for position, raw_host in enumerate(using):
            host = _require_mapping(
                raw_host, f"dml[{entry['id']}].using[{position}]"
            )
            if "host" not in host:
                raise TranslationError(
                    f"dml[{entry['id']}].using[{position}] has no 'host' key"
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
    return {
        "path": path,
        "source_program": source_program,
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

    # -- entry point -------------------------------------------------------
    def translate(self) -> ProgramResult:
        lines = split_source_lines(self.text)
        self.result = ProgramResult(
            source_name=self.name,
            source_line_count=len(lines),
            generated_lines=[],
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
    ) -> None:
        """Append the generated lines and record the site in the report.

        ``consumed_lines`` is the number of source lines the replacement
        stands in for; the corresponding line numbers are derived from
        ``locator`` and must not have been claimed by another rule.
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

        The length literal and the program operand are both taken from the
        parsed block; neither is fixed in this module.
        """
        commarea = require_operand(block, operands, "COMMAREA")
        length = require_operand(block, operands, "LENGTH")
        if not INTEGER_LITERAL_RE.match(length):
            raise TranslationError(
                f"{self.name}:{block.locator}: chain LINK LENGTH({length}) is not "
                f"an integer literal"
            )
        generated = emit_statement(block.indent, ["MOVE", length, "TO", "EIBCALEN"])
        generated += emit_statement(
            block.indent,
            ["CALL", program_operand, "USING", commarea],
            block.terminating_period,
        )
        self._record(
            rule_id="R5",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=f"PROGRAM({program_operand}) names a data item and the "
            f"dynamic CALL passes that item; LENGTH({length}) is carried into "
            f"EIBCALEN and COMMAREA({commarea}) is passed by reference",
            consumed_lines=len(block.source_lines),
        )

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
            notes="control returns to the caller at this point; see "
            "modernization/docs/decision-log.md: no called RETURN stub",
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
        """Rewrite the KSDSPOLY write to the capture stub."""
        operands = parse_cics_operands(block)
        file_name = unquote_literal(
            block, require_operand(block, operands, "FILE"), "FILE"
        )
        from_area = require_operand(block, operands, "FROM")
        ridfld = require_operand(block, operands, "RIDFLD")
        resp = require_operand(block, operands, "RESP")
        length = require_operand(block, operands, "LENGTH")
        key_length = require_operand(block, operands, "KEYLENGTH")
        for label, value in (("LENGTH", length), ("KEYLENGTH", key_length)):
            if not INTEGER_LITERAL_RE.match(value):
                raise TranslationError(
                    f"{self.name}:{block.locator}: WRITE {label}({value}) is not an "
                    f"integer literal"
                )
        generated = emit_statement(
            block.indent,
            ["CALL", f"'{STUB_WRITE}'", "USING", from_area, ridfld, resp],
            block.terminating_period,
        )
        self._record(
            rule_id="R9",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=f"FROM({from_area}), RIDFLD({ridfld}) and RESP({resp}) are passed in "
            f"that order; FILE('{file_name}'), LENGTH({length}) and "
            f"KEYLENGTH({key_length}) are constants of the {STUB_WRITE} stub",
            consumed_lines=len(block.source_lines),
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
        replacement = str(entry["replacement"]).strip()
        words = replacement.removesuffix(".").split()
        generated = emit_statement(block.indent, words, block.terminating_period)
        self._record(
            rule_id="R2",
            locator=block.locator,
            source_text=block.source_text,
            generated=generated,
            notes=f"statement map entry {entry['id']!r}; the COPY resolves to "
            f"{entry.get('resolves_to', 'the generated build source directory')} "
            f"under -ffold-copy=LOWER -ext cpy",
            consumed_lines=len(block.source_lines),
        )

    def _apply_r13(self, block: ExecBlock, entry: dict) -> None:
        """Replace an EXEC SQL DML block with the mapped stub CALL.

        The host variables parsed from the source must be an exact prefix of the
        mapped ``using`` list; any mapped host beyond that prefix is emitted as
        a superset argument and recorded.
        """
        hosts = [str(item["host"]) for item in entry["using"]]
        source_hosts = HOST_VARIABLE_RE.findall(block.body)
        mapped_upper = [name.upper() for name in hosts]
        source_upper = [name.upper() for name in source_hosts]
        if source_upper == mapped_upper:
            superset = []
        elif source_upper == mapped_upper[: len(source_upper)]:
            superset = hosts[len(source_upper):]
        else:
            raise TranslationError(
                f"{self.name}:{block.locator}: host variables {source_hosts} do "
                f"not prefix-match the statement map USING list {hosts} of entry "
                f"{entry['id']!r}"
            )
        generated = emit_call_with_operand_lines(
            block.indent,
            str(entry["call_program"]),
            hosts,
            block.terminating_period,
        )
        notes = (
            f"statement map entry {entry['id']!r} -> {entry['call_program']}; "
            f"{len(hosts)} host variable(s) passed by reference in source order"
        )
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
) -> dict:
    """Assemble the translation report.

    The per-program application lists and the per-rule totals account for
    every rewritten construct and for every source line carried through
    unchanged, which is the coverage
    ``modernization/docs/traceability-matrix.md`` consumes.
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

    Ordering: validate the statement map, read and digest the authorized
    sources and the harness copybooks, prepare the build tree, write the
    baseline, place the verbatim copies, translate the three programs, verify
    the generated tree, re-verify the sources, then write the report.
    """
    if not source_dir.is_dir():
        raise TranslationError(f"source directory not found: {source_dir}")
    if not copybook_dir.is_dir():
        raise TranslationError(f"copybook directory not found: {copybook_dir}")

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
            "generated harness build tree; its path must end with "
            f"{'/'.join(BUILD_DIR_TAIL)} (default: {DEFAULT_BUILD_DIR})"
        ),
    )
    parser.add_argument(
        "--statement-map",
        default=DEFAULT_STATEMENT_MAP,
        metavar="FILE",
        help=(
            "EXEC SQL block map driving rules R2 and R13 "
            f"(default: {DEFAULT_STATEMENT_MAP})"
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
        print(f"translate.py: error: {error}", file=sys.stderr)
        return 1
    except yaml.YAMLError as error:
        print(f"translate.py: error: statement map is not valid YAML: {error}",
              file=sys.stderr)
        return 1
    except OSError as error:
        print(f"translate.py: error: {error}", file=sys.stderr)
        return 1
    print(summarise(outcome))
    return 0


if __name__ == "__main__":
    sys.exit(main())

