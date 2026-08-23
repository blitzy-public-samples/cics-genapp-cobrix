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
  ``--statement-map`` each have exactly one accepted location, compared
  lexically so a value reaching it through a link is not accepted as it.  Every
  read then walks from the repository root one component at a time with
  ``O_NOFOLLOW``, inspects the entry through the descriptor of its own
  directory and reads the descriptor it opened after confirming its device,
  inode, file type and size, so neither a link at a parent nor a replacement
  between the check and the read can move a read.  The capturing stubs the
  statement map names in its ordering metadata are read from
  ``modernization/harness/stubs/`` of the same checkout and from nowhere else.
* Validates the ordering metadata of ``statement_map.yml`` before generating
  anything: every ``execution_order`` entry is held to its two sides, its
  reason kind and host, the ordinal items ``hcapture.cpy`` declares, the
  assertions its shape requires and the capturing stub it names as its
  enforcer, and ``capture_ordinals`` is held to the declared dml ids and to
  ``checks.order_constraint_count``.  The validated contract is published in
  the JSON report.
* Reconciles the same ordering metadata with ``hcapture.cpy``, with the
  capture stubs its entries name and with ``driver.cbl``: every ordinal item is
  declared and accounted for, the prerequisite table of the copybook agrees
  with the entry covering each member, each member stamps the successor ordinal
  and guards on exactly the prerequisite ordinals its entry declares, and the
  order table the driver walks reads the same ordinal for every event and
  covers every ordinal the map resolves.  Any disagreement fails the run before
  generation.
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
* Writes ``<build-dir>/logs/source-baseline.sha256`` in ``sha256sum`` format,
  headed by a comment line carrying the run disposition, and a JSON report
  recording every applied rule site and carrying that disposition as a member.

The script is argv-driven and never prompts.  Exit status is 0 on success, 5
when a case of ``--self-test`` did not hold, and non-zero with a precise
message on standard error on any other failure.

WHAT --self-test CHECKS
    That every gate of this translator can fail, and on which input.  The
    matrix drives this module's own functions in this process, over synthetic
    fixed-format fragments and over copies of the shipped documents, and each
    case names both the fixture and what it observed.

    The rewrite rules R1-R14: the commented compiler directive, the mapped
    ``COPY`` replacements, the ``PROCEDURE DIVISION USING DFHCOMMAREA``
    binding, the inserted harness declarations, the chain ``LINK`` rewritten to
    ``EIBCALEN`` plus a dynamic ``CALL`` with length 32500, the diagnostic
    ``LINK``, ``GOBACK`` with and without the source's period, the captured
    abend, the six operands of the ``KSDSPOLY`` write, the two time stubs, the
    response-condition constant, the mapped DML ``CALL`` and the lines no rule
    claims, each with a contradicting fixture that must be refused: a link
    length of 32499, a foreign COMMAREA, a wrong link target, a chain link in a
    program that carries none, a diagnostic ``LINK`` to another program or with
    another length form, a ``RETURN`` carrying an operand, an ``ABEND`` without
    its code, another file, record length or key length on the write, a literal
    where the capture module needs an item, ``ASKTIME`` and ``FORMATTIME``
    missing an operand, an unsupported response condition, an include naming
    another copybook or standing outside its declared group, a DML block at an
    unmapped line, ending on another line, addressing another table, carrying
    another predicate or another host order, an uncovered CICS verb, an
    unterminated block, a comment inside a block, an altered carried-through
    line and a dropped rewrite site.

    The columns 8-72 layout rule: a generated line reaching past column 72,
    naming the line and the column it reaches, a tab, a line too short to reach
    the indicator column, an invalid indicator, an invalid sequence area, and
    the emitter refusing a word and a comment that would leave the code area.

    The statement-map contract: a dml or includes count that disagrees with
    ``checks``, a duplicated entry, a repeated dml id, two entries claiming one
    source line, a total-block count, a ``using_counts`` arity, an unlisted
    call program, a declared census that disagrees with the source, an order
    constraint count, an ordinal item the capture copybook does not declare, an
    enforcer that is not the capturing stub of its successor, a non-integer
    line number, a capture copybook missing a declared ordinal and a harness
    copybook absent from the directory read.

    The pinned digests and the read and write surfaces: a source whose bytes do
    not carry its pinned digest, a source whose digest changed against the
    baseline of the run, a name with no pinned digest, a name outside the
    five-file allow list, a traversal out of the source directory, a copybook
    outside the harness set, a source, copybook or statement-map location other
    than the pinned one, a read outside the checkout, a build directory that is
    not the build tree of this checkout, and a build path that leaves it or is
    absolute.

    The shipped inputs pass every one of those gates in the same run: the
    statement map validates, the five sources carry their pinned digests, the
    three programs translate and meet their census, every generated line holds
    the layout rule, no untranslated construct survives, every unclaimed line is
    carried through, the structural counts, per-rule totals, chain-link contract
    and declared census hold, the capture-order contract reconciles, and every
    input re-reads unchanged after the last case.

    The matrix builds every fixture in this process from strings, bytes and
    copies of the documents it read.  It creates no file, writes nothing inside
    or outside the build tree, starts no subprocess and reads nothing but the
    five authorized sources, the harness copybooks, the capture stubs, the
    driver and the statement map of this checkout.  Every case prints one line;
    a shipped input that cannot be read leaves status 1 before any case runs,
    and a case that does not hold leaves status 5.

Rule-to-construct coverage is carried by the JSON report and its per-rule
totals, which account for every rewritten construct and for every source line
carried through unchanged.  The reasoning behind the translation strategy
belongs to ``modernization/docs/decision-log.md``; this module states only what
it does.  Harness topology is Figure 5 — Validation Harness Control Flow in
``modernization/docs/architecture.md``.
"""

import argparse
import copy
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

# Disposition of the target this run was validated against.  Every artifact
# this module writes states it at its head, in that artifact's own syntax: the
# standard-output summary and the baseline take one line each, the JSON report
# takes a member, so no artifact of a run can be read without it.
STATUS_LABEL_TEXT = "validated against local substitute, not AWS"

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

# The capture stubs the map's execution_order entries name in enforced_by.
# Their order guards are read - never written - while the ordering metadata is
# reconciled, and a declared path outside this directory is refused.
EXPECTED_STUB_DIR = REPO_ROOT / "modernization" / "harness" / "stubs"

# The driver whose own order evaluation is reconciled with the map.  It walks
# the ordinals of the capture state and asserts they rise, which is the second
# reading of the order the stubs guard.
EXPECTED_DRIVER_SOURCE = (
    REPO_ROOT / "modernization" / "harness" / "driver.cbl"
)

# The copybook that declares the shared capture state, including every ordinal
# item the ordering metadata names, and the prerequisite table reconciled with
# that metadata.
CAPTURE_COPYBOOK = "hcapture.cpy"

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

# Largest authorized source, harness copybook or capture stub this translator
# reads through one descriptor, in bytes.  The bound is checked on the open
# descriptor before the read and again while reading it.
MAX_READ_FILE_BYTES = 1_048_576

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
# Every file this translator reads is opened read-only, creating nothing, with
# O_NOFOLLOW refusing a symbolic link at the name itself; O_NONBLOCK makes the
# open of a special file fail rather than wait, and has no effect on a regular
# file.  The bytes are then read from that descriptor.
NOFOLLOW_READ_FILE_FLAGS = (
    os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0)
)
# Modes carried by a directory and a file this translator creates inside the
# build tree.  Both are set on the created entry itself as well as requested at
# creation, and a write over an entry that already stands normalises its mode,
# so the ambient umask decides neither: the build tree is generated, is read
# and compiled by its owner alone, and stands beside the run outputs and
# samples that carry COMMAREA values.  Decision rationale:
# modernization/docs/decision-log.md, row D-127.
BUILD_DIR_MODE = 0o700
BUILD_FILE_MODE = 0o600

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

# The heading of the prerequisite table hcapture.cpy carries, the rows of which
# are reconciled with the execution_order entries.  A row names the capturing
# member, the ordinal item(s) it reads, and - where the entry declares no
# predecessor - the ordinal value the member requires instead.
CAPTURE_TABLE_HEADING = "The prerequisite each member reads:"
CAPTURE_TABLE_MEMBER_RE = re.compile(r"^([A-Za-z0-9_]+\.cbl)\b(.*)$")
CAPTURE_ORDINAL_ITEM_RE = re.compile(r"\bHC-[A-Z0-9]+(?:-[A-Z0-9]+)*-SEQ\b")
CAPTURE_TABLE_EQUAL_TO_RE = re.compile(r"\bequal to (\d+)\b")

# The declaration of an ordinal item inside hcapture.cpy: a level number, the
# item name and the PIC clause capture_ordinals declares for every ordinal.
CAPTURE_ORDINAL_DECLARATION_RE = re.compile(
    r"^\s*\d\d\s+(?P<name>HC-[A-Z0-9-]+-SEQ)\s+PIC\s+(?P<pic>\S+?)\s*\.\s*$",
    re.IGNORECASE,
)

# The two writes and the one read that make a capture stub the enforcing member
# of its entry: it stamps its own ordinal from the shared sequence item, names
# itself in HC-ORDER-LAST-STMT, and reports a violation under that same name.
STUB_ORDINAL_STAMP_RE = re.compile(
    r"\bMOVE\s+(?P<sequence>HC-[A-Z0-9-]+)\s+TO\s+(?P<ordinal>HC-[A-Z0-9-]+-SEQ)\b",
    re.IGNORECASE,
)
STUB_LAST_STMT_RE = re.compile(
    r"\bMOVE\s+(?P<operand>'[^']*'|[A-Z0-9-]+)\s+TO\s+HC-ORDER-LAST-STMT\b",
    re.IGNORECASE,
)
STUB_VIOLATION_STMT_RE = re.compile(
    r"\bMOVE\s+(?P<operand>'[^']*'|[A-Z0-9-]+)\s+TO\s+HC-ORDER-VIOLATION-STMT\b",
    re.IGNORECASE,
)
STUB_VIOLATION_FLAG_RE = re.compile(
    r"\bMOVE\s+'Y'\s+TO\s+HC-ORDER-VIOLATION(?!-)", re.IGNORECASE
)
STUB_GUARD_START_RE = re.compile(r"^IF\b", re.IGNORECASE)

# --------------------------------------------------------------------------
# Order metadata of statement_map.yml (execution_order and capture_ordinals)
# --------------------------------------------------------------------------
# One constraint per capture ordinal: the eight ordinal items of hcapture.cpy
# each stand as the successor of exactly one execution_order entry, and
# checks.order_constraint_count carries the same figure.
EXPECTED_MAP_ORDER_CONSTRAINT_COUNT = 8

# The capturing stubs named by the enforced_by member of an execution_order
# entry are read from this directory, the stubs directory of the checkout this
# module belongs to, and from nowhere else.  A declared path outside it, or a
# symbolic link standing at one, is refused before the file is opened.
EXPECTED_STUBS_DIR = REPO_ROOT / "modernization" / "harness" / "stubs"
MAX_STUB_BYTES = 262_144

# The copybook that declares the capture state, and therefore every ordinal
# item an execution_order witness may name.  Both order sections of the map
# declare this path and are held to it.
ORDER_WITNESS_COPYBOOK = "hcapture.cpy"

# Sentinel values of the order metadata.  `predecessor: 'none'` marks a
# constraint on the first captured event rather than on a pair, and
# `successor: 'cics_write'` names the recording stub of the KSDSPOLY write,
# which is not an EXEC SQL block of the map.
ORDER_NO_PREDECESSOR = "none"
ORDER_VSAM_SUCCESSOR = "cics_write"

# Closed vocabularies of the order metadata.
ORDER_REASON_KINDS = frozenset({"control_flow", "data_dependency"})
ORDER_ASSERTION_OPERATORS = frozenset({"greater_than", "less_than", "equal_to"})

# Required members of one execution_order entry, of its witness block and of
# the capture_ordinals block.
EXECUTION_ORDER_KEYS = (
    "id",
    "predecessor",
    "successor",
    "reason_kind",
    "enforced_by",
    "note",
    "witness",
)
ORDER_WITNESS_KEYS = (
    "copybook",
    "predecessor_ordinal_item",
    "successor_ordinal_item",
    "assertions",
)
CAPTURE_ORDINALS_KEYS = (
    "copybook",
    "sequence_item",
    "ordinal_pic",
    "unstamped_value",
    "by_dml_id",
    "vsam_write_ordinal_item",
    "distinct_ordinal_items",
)

# The value an ordinal item holds while the block it belongs to has not been
# captured, and the PICTURE every ordinal item and the shared sequence item
# are declared with.  The stub-side guard reads an ordinal still at this value
# as a prerequisite that has not run, and the driver reads it the same way.
EXPECTED_UNSTAMPED_ORDINAL = 0
ORDINAL_PIC_RE = re.compile(r"^9\((?P<digits>\d{1,4})\)$")

# The two items every capturing stub named by an enforced_by member moves its
# verdict into when a prerequisite ordinal is still unstamped.
ORDER_GUARD_ITEMS = ("HC-ORDER-VIOLATION", "HC-ORDER-VIOLATION-STMT")

# One data description entry of a harness copybook or stub, and the PICTURE
# clause inside it.  Entries are split on the periods that end them before
# either pattern is applied.
COPYBOOK_ENTRY_RE = re.compile(
    r"^(?P<level>\d{1,2})\s+(?P<name>[A-Za-z0-9][A-Za-z0-9\-]*)(?P<rest>\s.*|)$"
)
PICTURE_CLAUSE_RE = re.compile(
    r"\bPIC(?:TURE)?\s+(?:IS\s+)?(?P<picture>\S+)", re.IGNORECASE
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
# read by PIC 9(5) receivers in the capture module.  See
# modernization/docs/decision-log.md, row: WRITE length operands as 5-digit
# literals.
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


def lexical_repo_components(supplied: Path, option: str) -> tuple:
    """Return the components of ``supplied`` below the repository root.

    A relative value is made absolute against the repository root, ``.`` is
    dropped and ``..`` cancels the component before it, none of which asks the
    filesystem anything: resolving the value here would follow the very
    symbolic links the descriptor walk has to refuse, and would then compare a
    path this translator never opens.  A value that leaves the repository root,
    and a value naming the root itself, are refused.  ``option`` names the
    command-line option or map member the value came from.
    """
    candidate = Path(supplied).expanduser()
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    stack = []
    for part in candidate.parts:
        if part == ".":
            continue
        if part == "..":
            if len(stack) <= 1:
                raise TranslationError(
                    f"{option} names {supplied}, which climbs above the "
                    f"filesystem root"
                )
            stack.pop()
            continue
        stack.append(part)
    normalised = Path(*stack)
    try:
        relative = normalised.relative_to(REPO_ROOT)
    except ValueError as error:
        raise TranslationError(
            f"{option} names {normalised}; this translator reads only inside "
            f"{REPO_ROOT}, the checkout holding {Path(__file__).resolve()}"
        ) from error
    if not relative.parts:
        raise TranslationError(
            f"{option} names {REPO_ROOT}, the repository root itself; a "
            f"directory or file below it is required"
        )
    return relative.parts


def open_nofollow_directory(parent_fd: int, name: str, display: Path) -> int:
    """Open the directory ``name`` below ``parent_fd``, following no link.

    An absent directory is reported as absent; anything that exists and is not
    a directory this run may open without following a link - a symbolic link
    included - is reported with the reason the open gave.
    """
    try:
        return os.open(name, NOFOLLOW_DIR_FLAGS, dir_fd=parent_fd)
    except FileNotFoundError as error:
        raise TranslationError(
            f"cannot descend into {display}: it does not exist"
        ) from error
    except OSError as error:
        raise TranslationError(
            f"refusing to descend into {display}: it is not a directory this "
            f"run may open without following a link ({error})"
        ) from error


def open_repo_directory_fd(components) -> int:
    """Open a directory below the repository root, following no link.

    ``REPO_ROOT`` is a fully resolved path, so its own components carry no
    symbolic link, and it is the one path opened by name.  Every component
    below it is opened from the descriptor of its parent with ``O_NOFOLLOW``,
    so a link standing at any of them - a parent directory as much as the
    entry itself - is refused instead of traversed.  The caller closes the
    descriptor this returns.
    """
    try:
        current = os.open(str(REPO_ROOT), NOFOLLOW_DIR_FLAGS)
    except OSError as error:
        raise TranslationError(
            f"cannot open the repository root {REPO_ROOT} as a directory: "
            f"{error}"
        ) from error
    walked = REPO_ROOT
    try:
        for name in components:
            walked = walked / name
            child = open_nofollow_directory(current, name, walked)
            os.close(current)
            current = child
    except BaseException:
        os.close(current)
        raise
    return current


def _read_open_descriptor(handle: int, max_bytes: int, display: Path) -> bytes:
    """Read ``handle`` to end of file, refusing more than ``max_bytes``."""
    chunks = []
    total = 0
    while True:
        try:
            chunk = os.read(handle, 65536)
        except OSError as error:
            raise TranslationError(f"cannot read {display}: {error}") from error
        if not chunk:
            return b"".join(chunks)
        total += len(chunk)
        if total > max_bytes:
            raise TranslationError(
                f"{display} holds more than {max_bytes} bytes; a larger file "
                f"is not read"
            )
        chunks.append(chunk)


def read_repo_file(components, option: str, max_bytes: int) -> bytes:
    """Read one file below the repository root through a no-follow descriptor.

    The directories above the file are walked descriptor by descriptor, the
    entry is inspected with a no-follow ``stat`` through the descriptor of its
    own directory, and the file is then opened from that same descriptor with
    ``O_NOFOLLOW``.  The open descriptor must carry the device and inode the
    inspection reported, must be a regular file and must hold no more than
    ``max_bytes``, and the bytes are read from it: the entry inspected, the
    entry opened and the entry read are one file, whatever the name reaches
    afterwards.  ``option`` names the option or map member that asked for it.
    """
    display = REPO_ROOT.joinpath(*components)
    name = components[-1]
    dir_fd = open_repo_directory_fd(components[:-1])
    try:
        try:
            inspected = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        except FileNotFoundError as error:
            raise TranslationError(
                f"{option} names {display}, which does not exist"
            ) from error
        except OSError as error:
            raise TranslationError(
                f"cannot inspect {display} before reading it: {error}"
            ) from error
        if stat.S_ISLNK(inspected.st_mode):
            raise TranslationError(
                f"refusing to read {display}: it is a symbolic link, and this "
                f"translator reads the files of its own checkout only as "
                f"regular files"
            )
        try:
            handle = os.open(name, NOFOLLOW_READ_FILE_FLAGS, dir_fd=dir_fd)
        except OSError as error:
            raise TranslationError(
                f"refusing to read {display}: it cannot be opened without "
                f"following a link ({error})"
            ) from error
        try:
            opened = os.fstat(handle)
            if not stat.S_ISREG(opened.st_mode):
                raise TranslationError(
                    f"refusing to read {display}: it is not a regular file"
                )
            if (opened.st_dev, opened.st_ino) != (
                inspected.st_dev, inspected.st_ino
            ):
                raise TranslationError(
                    f"refusing to read {display}: the entry inspected as "
                    f"device {inspected.st_dev} inode {inspected.st_ino} "
                    f"opened as device {opened.st_dev} inode {opened.st_ino}, "
                    f"so the name was replaced between the two"
                )
            if opened.st_size > max_bytes:
                raise TranslationError(
                    f"{display} holds {opened.st_size} bytes; at most "
                    f"{max_bytes} are read"
                )
            return _read_open_descriptor(handle, max_bytes, display)
        finally:
            os.close(handle)
    finally:
        os.close(dir_fd)


def require_expected_read_directory(supplied: Path, expected: Path,
                                    option: str) -> tuple:
    """Require ``supplied`` to name exactly ``expected``, and open it.

    ``option`` names the command-line option the value came from.  The
    comparison is lexical, so a value that reaches the expected path through a
    symbolic link is not accepted as that path, and the directory is then
    opened component by component from the repository root with
    ``O_NOFOLLOW``, which refuses a link standing anywhere along it and
    anything that is not a directory.  Returns the components of the directory
    below the repository root.
    """
    components = lexical_repo_components(supplied, option)
    if components != lexical_repo_components(expected, option):
        raise TranslationError(
            f"{option} names {REPO_ROOT.joinpath(*components)}; this "
            f"translator reads only {expected}, the directory of the checkout "
            f"holding {Path(__file__).resolve()}"
        )
    os.close(open_repo_directory_fd(components))
    return components


def require_expected_read_file(supplied: Path, expected: Path,
                               option: str) -> tuple:
    """Require ``supplied`` to name exactly ``expected``.

    ``option`` names the command-line option the value came from.  The
    comparison is lexical for the reason ``lexical_repo_components`` states;
    the read itself then walks the directories above the file and opens it
    with ``O_NOFOLLOW``, so a link standing at the file or at any directory
    above it is refused rather than read through.  Returns the components of
    the file below the repository root.
    """
    components = lexical_repo_components(supplied, option)
    if components != lexical_repo_components(expected, option):
        raise TranslationError(
            f"{option} names {REPO_ROOT.joinpath(*components)}; this "
            f"translator reads only {expected}, the file of the checkout "
            f"holding {Path(__file__).resolve()}"
        )
    return components


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

    Refuses any name outside SOURCE_ALLOW_LIST and any name carrying a path
    separator, so the components read are exactly the pinned source directory
    plus that one name.  The file is read through a no-follow descriptor, and
    the bytes read are compared with the pinned digest of that name before
    they are returned.
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
    components = lexical_repo_components(source_dir, "--source-dir") + (name,)
    data = read_repo_file(
        components, f"the authorized source {name}", MAX_READ_FILE_BYTES
    )
    require_authorized_source_digest(name, data)
    return data


def read_harness_copybook(copybook_dir: Path, name: str) -> bytes:
    """Read one harness copybook from --copybook-dir in binary mode.

    The name must be one of the four harness copybooks and must carry no path
    separator; the file is read through a no-follow descriptor.
    """
    if name not in HARNESS_COPYBOOKS:
        raise TranslationError(
            f"refusing to read {name!r}: only the harness copybooks "
            f"{list(HARNESS_COPYBOOKS)} are read from --copybook-dir"
        )
    if Path(name).name != name:
        raise TranslationError(
            f"refusing to read {name!r}: names must be bare file names"
        )
    components = lexical_repo_components(copybook_dir, "--copybook-dir") + (name,)
    return read_repo_file(
        components, f"the harness copybook {name}", MAX_READ_FILE_BYTES
    )


def read_declared_capture_stub(declared_path: str, label: str) -> bytes:
    """Read the capture stub a statement-map entry names, in binary mode.

    ``declared_path`` is the repository-relative ``enforced_by`` value of an
    ``execution_order`` entry and ``label`` names that member.  The value must
    name a bare file below ``EXPECTED_STUB_DIR``, so an entry cannot move the
    read surface to another tree, and the file is read through a no-follow
    descriptor.
    """
    text = _require_text(declared_path, label).strip()
    components = lexical_repo_components(Path(text), label)
    expected = lexical_repo_components(EXPECTED_STUB_DIR, label)
    if components[:-1] != expected:
        raise TranslationError(
            f"{label} names {REPO_ROOT.joinpath(*components)}; every capture "
            f"stub of this map lives directly in {EXPECTED_STUB_DIR}"
        )
    return read_repo_file(components, label, MAX_READ_FILE_BYTES)


def read_driver_source() -> bytes:
    """Read the harness driver in binary mode, through a no-follow descriptor.

    The driver is read for one purpose: reconciling the order table it builds
    with the ordering metadata of the statement map.  The path is fixed at
    ``EXPECTED_DRIVER_SOURCE`` and comes from no map member, so no map entry can
    move this read.
    """
    components = lexical_repo_components(
        EXPECTED_DRIVER_SOURCE, "the harness driver"
    )
    return read_repo_file(components, "the harness driver", MAX_READ_FILE_BYTES)


def read_harness_stub(declared_path: str, label: str) -> bytes:
    """Read one capturing stub named by the statement map, in binary mode.

    ``declared_path`` is the repository-relative path an ``enforced_by`` member
    carries and ``label`` names that member.  The path must lie directly inside
    ``EXPECTED_STUBS_DIR``, carry no path component of its own beyond that
    directory, stand as a regular file rather than a symbolic link, and hold at
    most ``MAX_STUB_BYTES``; the bytes are read only after all four hold.
    """
    candidate = Path(declared_path.strip())
    if candidate.is_absolute():
        raise TranslationError(
            f"{label} names the absolute path {declared_path!r}; a path relative "
            f"to the repository root {REPO_ROOT} is required"
        )
    expected_parent = EXPECTED_STUBS_DIR.relative_to(REPO_ROOT).as_posix()
    if candidate.parent.as_posix() != expected_parent:
        raise TranslationError(
            f"{label} names {candidate.as_posix()!r}; a capturing stub is read "
            f"only from {expected_parent}/"
        )
    path = REPO_ROOT / candidate
    if path.is_symlink():
        raise TranslationError(
            f"{label} names {candidate.as_posix()}, a symbolic link; a capturing "
            f"stub is read only as a regular file"
        )
    if not path.is_file():
        raise TranslationError(
            f"{label} names {candidate.as_posix()}, which is not a regular file "
            f"of this checkout"
        )
    if path.resolve().parent != EXPECTED_STUBS_DIR.resolve():
        raise TranslationError(
            f"{label} names {candidate.as_posix()}, which resolves to "
            f"{path.resolve()}, outside {EXPECTED_STUBS_DIR}"
        )
    size = path.stat().st_size
    if size > MAX_STUB_BYTES:
        raise TranslationError(
            f"{label} names {candidate.as_posix()}, holding {size} bytes; at "
            f"most {MAX_STUB_BYTES} are read"
        )
    with path.open("rb") as handle:
        return handle.read(MAX_STUB_BYTES)


def split_data_entries(text: str) -> list:
    """Split one code-area stream into the entries its periods end.

    A period inside a quoted literal does not end an entry, so a ``VALUE``
    clause carrying a timestamp literal stays inside the entry that declares
    it.  Empty fragments are dropped.
    """
    entries = []
    current = []
    quote = ""
    for character in text:
        if quote:
            current.append(character)
            if character == quote:
                quote = ""
            continue
        if character in "'\"":
            quote = character
            current.append(character)
            continue
        if character == ".":
            fragment = "".join(current).strip()
            if fragment:
                entries.append(fragment)
            current = []
            continue
        current.append(character)
    fragment = "".join(current).strip()
    if fragment:
        entries.append(fragment)
    return entries


def code_area_text(name: str, data: bytes) -> str:
    """Return the code area (columns 8-72) of a COBOL file as one string.

    Comment lines are dropped and every remaining line contributes its code
    area only, so a name found in the returned text stands in executable or
    declarative code rather than in prose.  Harness copybooks and stubs are
    UTF-8; only their comment prose uses characters outside ASCII.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise TranslationError(f"{name} is not valid UTF-8: {error}") from error
    fragments = []
    for line in text.split("\n"):
        if is_comment_line(line):
            continue
        fragment = line[CODE_START:MAX_LINE_LENGTH].strip()
        if fragment:
            fragments.append(fragment)
    return " ".join(fragments)


def declared_copybook_items(name: str, data: bytes) -> dict:
    """Return the data items a harness copybook declares.

    Maps every declared name, upper-cased, onto the PICTURE character-string
    of its entry, or onto ``None`` for a group item, a condition name and any
    other entry that declares no PICTURE.
    """
    items = {}
    for entry in split_data_entries(code_area_text(name, data)):
        match = COPYBOOK_ENTRY_RE.match(entry)
        if match is None:
            continue
        picture = PICTURE_CLAUSE_RE.search(match.group("rest"))
        items[match.group("name").upper()] = (
            picture.group("picture").upper() if picture is not None else None
        )
    return items


def code_references_item(code: str, item: str) -> bool:
    """True when ``code`` names the COBOL data item ``item``.

    The name is matched whole: a hyphen, a letter or a digit standing beside it
    makes the occurrence a different name, so ``HC-ORDER-VIOLATION`` is not
    found inside ``HC-ORDER-VIOLATION-STMT``.
    """
    pattern = re.compile(
        rf"(?<![A-Za-z0-9\-]){re.escape(item)}(?![A-Za-z0-9\-])", re.IGNORECASE
    )
    return pattern.search(code) is not None


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
        """Open the build root as a no-follow directory descriptor.

        The walk starts at the repository root and opens one component at a
        time, so the descriptor stands for the build tree of this checkout
        even when a directory above it has been replaced by a link.
        """
        return open_repo_directory_fd(self.root.relative_to(REPO_ROOT).parts)

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
        return open_nofollow_directory(parent_fd, name, display)

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
            os.fchmod(handle, BUILD_FILE_MODE)
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
        """Create the build root below its parent without following links.

        The parent is reached by walking down from the repository root one
        component at a time, so no directory above the build tree can be
        substituted by a link between this run's checks and its writes.
        """
        parent = self.root.parent
        parent_fd = open_repo_directory_fd(parent.relative_to(REPO_ROOT).parts)
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

    def holds_regular_file(self, relative: str) -> bool:
        """True when ``relative`` stands for a regular file inside the tree.

        The directories above the entry are opened descriptor by descriptor
        without following a link and the entry itself is inspected with a
        no-follow stat, so a link planted inside the tree answers False rather
        than reporting whatever it points at.
        """
        self.path_for(relative)
        parts = self._lexical_parts(relative)
        dir_fd = self._open_directory_fd(parts[:-1], create=False)
        try:
            info = os.stat(parts[-1], dir_fd=dir_fd, follow_symlinks=False)
        except FileNotFoundError:
            return False
        except OSError as error:
            raise TranslationError(
                f"cannot inspect {self.root.joinpath(*parts)}: {error}"
            ) from error
        finally:
            os.close(dir_fd)
        return stat.S_ISREG(info.st_mode)



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
# argument.  That choice belongs to modernization/docs/decision-log.md, row:
# single-superset SQL-INSERT-ENDOWMENT call.
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
        for key in ("include_count", "dml_count", "total_blocks",
                    "order_constraint_count"):
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
    capture_ordinals = data.get("capture_ordinals")
    if isinstance(capture_ordinals, dict):
        for key in ("copybook", "sequence_item", "ordinal_pic",
                    "vsam_write_event_id", "vsam_write_ordinal_item"):
            if key in capture_ordinals:
                _require_text(
                    capture_ordinals[key], f"{label}: capture_ordinals.{key}"
                )
        for key in ("unstamped_value", "distinct_ordinal_items"):
            if key in capture_ordinals:
                _require_integer(
                    capture_ordinals[key], f"{label}: capture_ordinals.{key}"
                )
    entries = data.get("execution_order")
    if isinstance(entries, list):
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            where = f"{label}: execution_order[{index}]"
            for key in ("id", "predecessor", "successor", "reason_kind",
                        "enforced_by", "note", "host"):
                if key in entry:
                    _require_text(entry[key], f"{where}.{key}")
            witness = entry.get("witness")
            if isinstance(witness, dict):
                for key in ("copybook", "predecessor_ordinal_item",
                            "successor_ordinal_item"):
                    if key in witness:
                        _require_text(witness[key], f"{where}.witness.{key}")


def _validate_capture_ordinals(capture_ordinals: dict, dml_ids, label: str) -> dict:
    """Type- and shape-check ``capture_ordinals`` and resolve its event ids.

    Every member is required and typed: the copybook it names, the shared
    sequence item, the ordinal PIC, the unstamped value, one ordinal item per
    dml id, the VSAM write event id and its ordinal item, the count of distinct
    statement ordinals and the ordinal items that carry no statement of this
    map.  ``by_dml_id`` must name exactly the dml ids of the map, no ordinal
    item may be spelled twice across the roles it fills, and
    ``distinct_ordinal_items`` must equal the number of distinct statement
    ordinals the block resolves to.  Returns the event-id-to-ordinal-item
    resolution, which is the one such resolution this translator uses.
    """
    _require_keys(
        capture_ordinals,
        ("copybook", "sequence_item", "ordinal_pic", "unstamped_value",
         "by_dml_id", "vsam_write_event_id", "vsam_write_ordinal_item",
         "distinct_ordinal_items", "non_statement_ordinal_items"),
        label,
    )
    declared_copybook = _require_text(
        capture_ordinals["copybook"], f"{label}.copybook"
    ).strip()
    expected_copybook = (
        EXPECTED_COPYBOOK_DIR.relative_to(REPO_ROOT) / CAPTURE_COPYBOOK
    ).as_posix()
    if Path(declared_copybook).as_posix() != expected_copybook:
        raise TranslationError(
            f"{label}.copybook is {declared_copybook!r}, expected "
            f"{expected_copybook!r}"
        )
    _require_text(capture_ordinals["sequence_item"], f"{label}.sequence_item")
    _require_text(capture_ordinals["ordinal_pic"], f"{label}.ordinal_pic")
    unstamped = _require_integer(
        capture_ordinals["unstamped_value"], f"{label}.unstamped_value"
    )
    if unstamped != 0:
        raise TranslationError(
            f"{label}.unstamped_value is {unstamped}; an unstamped ordinal of "
            f"this copybook holds 0"
        )
    by_dml_id = _require_mapping(capture_ordinals["by_dml_id"], f"{label}.by_dml_id")
    resolution = {}
    for event_id, item in by_dml_id.items():
        _require_text(event_id, f"{label}.by_dml_id key")
        resolution[event_id] = _require_text(
            item, f"{label}.by_dml_id[{event_id}]"
        ).strip().upper()
    if set(by_dml_id) != set(dml_ids):
        raise TranslationError(
            f"{label}.by_dml_id names {sorted(by_dml_id)}; the dml entries of "
            f"this map are {sorted(dml_ids)}"
        )
    vsam_event = _require_text(
        capture_ordinals["vsam_write_event_id"], f"{label}.vsam_write_event_id"
    ).strip()
    if vsam_event in resolution:
        raise TranslationError(
            f"{label}.vsam_write_event_id is {vsam_event!r}, which is already a "
            f"dml id of this map"
        )
    vsam_item = _require_text(
        capture_ordinals["vsam_write_ordinal_item"],
        f"{label}.vsam_write_ordinal_item",
    ).strip().upper()
    if vsam_item in set(resolution.values()):
        raise TranslationError(
            f"{label}.vsam_write_ordinal_item is {vsam_item!r}, which a dml id "
            f"of this map already names"
        )
    resolution[vsam_event] = vsam_item
    distinct = _require_integer(
        capture_ordinals["distinct_ordinal_items"],
        f"{label}.distinct_ordinal_items",
    )
    if distinct != len(set(resolution.values())):
        raise TranslationError(
            f"{label}.distinct_ordinal_items is {distinct}; the block resolves "
            f"{len(set(resolution.values()))} distinct ordinal item(s)"
        )
    non_statement = _require_sequence(
        capture_ordinals["non_statement_ordinal_items"],
        f"{label}.non_statement_ordinal_items",
    )
    seen_non_statement = set()
    for index, item in enumerate(non_statement):
        name = _require_text(
            item, f"{label}.non_statement_ordinal_items[{index}]"
        ).strip().upper()
        if name in set(resolution.values()):
            raise TranslationError(
                f"{label}.non_statement_ordinal_items names {name!r}, which an "
                f"event id of this map already resolves to"
            )
        if name in seen_non_statement:
            raise TranslationError(
                f"{label}.non_statement_ordinal_items repeats {name!r}"
            )
        seen_non_statement.add(name)
    return resolution


def _assertion_pairs(entry: dict, label: str) -> tuple:
    """Return the ordinal items and comparisons the assertions of one entry make.

    Every assertion is typed and shape-checked: a plain assertion names a
    ``left_item`` and compares it with a ``right_item`` or a ``right_literal``
    under a supported ``operator``, and an ``any_of`` assertion holds a
    non-empty list of plain assertions.  Returns the set of ordinal items the
    assertions name, the list of ``(left, operator, right)`` comparisons made
    outside any ``any_of``, and the list of items each ``any_of`` group tests
    for having been captured.  ``label`` names the entry every message reports.
    """
    witness = _require_mapping(entry["witness"], f"{label}.witness")
    assertions = _require_sequence(
        witness["assertions"], f"{label}.witness.assertions"
    )
    if not assertions:
        raise TranslationError(
            f"{label}.witness.assertions declares no assertion"
        )
    named = set()
    comparisons = []
    any_groups = []

    def read_plain(raw, where: str) -> tuple:
        assertion = _require_mapping(raw, where)
        _require_keys(assertion, ("left_item", "operator"), where)
        left = _require_text(assertion["left_item"], f"{where}.left_item")
        left = left.strip().upper()
        operator = _require_text(assertion["operator"], f"{where}.operator").strip()
        if operator not in ORDER_ASSERTION_OPERATORS:
            raise TranslationError(
                f"{where}.operator is {operator!r}; the supported operators are "
                f"{sorted(ORDER_ASSERTION_OPERATORS)}"
            )
        has_item = "right_item" in assertion
        has_literal = "right_literal" in assertion
        if has_item == has_literal:
            raise TranslationError(
                f"{where} must compare left_item with exactly one of "
                f"right_item and right_literal"
            )
        named.add(left)
        if has_item:
            right = _require_text(
                assertion["right_item"], f"{where}.right_item"
            ).strip().upper()
            named.add(right)
            return left, operator, right
        literal = _require_integer(
            assertion["right_literal"], f"{where}.right_literal"
        )
        return left, operator, literal

    for position, raw in enumerate(assertions):
        where = f"{label}.witness.assertions[{position}]"
        if isinstance(raw, dict) and "any_of" in raw:
            if set(raw) != {"any_of"}:
                raise TranslationError(
                    f"{where} carries {sorted(raw)}; an any_of assertion holds "
                    f"that one member"
                )
            members = _require_sequence(raw["any_of"], f"{where}.any_of")
            if not members:
                raise TranslationError(f"{where}.any_of declares no assertion")
            group = []
            for member_index, member in enumerate(members):
                left, operator, right = read_plain(
                    member, f"{where}.any_of[{member_index}]"
                )
                if (operator, right) != ("greater_than", 0):
                    raise TranslationError(
                        f"{where}.any_of[{member_index}] compares {left} "
                        f"{operator} {right!r}; an alternative predecessor is "
                        f"tested for having been captured at all"
                    )
                group.append(left)
            any_groups.append(group)
            continue
        comparisons.append(read_plain(raw, where))
    return named, comparisons, any_groups


def _validate_execution_order(execution_order: list, resolution: dict,
                              first_ordinal: int, label: str) -> list:
    """Type- and shape-check ``execution_order`` and resolve each entry.

    Every entry is required to carry a unique id, a predecessor and successor
    that resolve through ``capture_ordinals``, the reason kind and the host it
    names where the reason is a data dependency, the capture stub that enforces
    it, a note and a witness whose ordinal items are the ones that resolution
    returns.  The assertions of an entry must compare exactly the pair it
    declares: a first-captured entry compares its own ordinal with
    ``first_ordinal``, the first value the shared sequence item issues, and
    every other entry states that both ordinals were stamped and that the
    predecessor was stamped first.  Returns one resolved record per entry.
    """
    resolved = []
    seen_ids = set()
    for index, raw_entry in enumerate(execution_order):
        where = f"{label}[{index}]"
        entry = _require_mapping(raw_entry, where)
        _require_keys(
            entry,
            ("id", "predecessor", "successor", "reason_kind", "enforced_by",
             "note", "witness"),
            where,
        )
        entry_id = _require_text(entry["id"], f"{where}.id").strip()
        if entry_id in seen_ids:
            raise TranslationError(f"duplicate execution_order id {entry_id!r}")
        seen_ids.add(entry_id)
        where = f"{label}[{entry_id}]"
        predecessor = _require_text(
            entry["predecessor"], f"{where}.predecessor"
        ).strip()
        successor = _require_text(entry["successor"], f"{where}.successor").strip()
        reason = _require_text(entry["reason_kind"], f"{where}.reason_kind").strip()
        if reason not in ORDER_REASON_KINDS:
            raise TranslationError(
                f"{where}.reason_kind is {reason!r}; the supported kinds are "
                f"{sorted(ORDER_REASON_KINDS)}"
            )
        if reason == "data_dependency":
            _require_keys(entry, ("host",), where)
            _require_text(entry["host"], f"{where}.host")
        elif "host" in entry:
            raise TranslationError(
                f"{where} declares host {entry['host']!r} with reason_kind "
                f"{reason!r}; only a data dependency names the host that "
                f"carries it"
            )
        _require_text(entry["note"], f"{where}.note")
        stub = _require_text(entry["enforced_by"], f"{where}.enforced_by").strip()
        if successor not in resolution:
            raise TranslationError(
                f"{where}.successor is {successor!r}, which is neither a dml id "
                f"nor the VSAM write event id of capture_ordinals "
                f"{sorted(resolution)}"
            )
        if predecessor != ORDER_NO_PREDECESSOR and predecessor not in resolution:
            raise TranslationError(
                f"{where}.predecessor is {predecessor!r}, which is neither "
                f"{ORDER_NO_PREDECESSOR!r} nor an event id of capture_ordinals "
                f"{sorted(resolution)}"
            )
        witness = _require_mapping(entry["witness"], f"{where}.witness")
        _require_keys(
            witness,
            ("copybook", "predecessor_ordinal_item", "successor_ordinal_item",
             "assertions"),
            f"{where}.witness",
        )
        declared_copybook = _require_text(
            witness["copybook"], f"{where}.witness.copybook"
        ).strip()
        expected_copybook = (
            EXPECTED_COPYBOOK_DIR.relative_to(REPO_ROOT) / CAPTURE_COPYBOOK
        ).as_posix()
        if Path(declared_copybook).as_posix() != expected_copybook:
            raise TranslationError(
                f"{where}.witness.copybook is {declared_copybook!r}, expected "
                f"{expected_copybook!r}"
            )
        successor_item = _require_text(
            witness["successor_ordinal_item"],
            f"{where}.witness.successor_ordinal_item",
        ).strip().upper()
        if successor_item != resolution[successor]:
            raise TranslationError(
                f"{where}.witness.successor_ordinal_item is "
                f"{successor_item!r}; capture_ordinals resolves the event "
                f"{successor!r} to {resolution[successor]!r}"
            )
        declared_predecessor_item = _require_text(
            witness["predecessor_ordinal_item"],
            f"{where}.witness.predecessor_ordinal_item",
        ).strip()
        if predecessor == ORDER_NO_PREDECESSOR:
            if declared_predecessor_item.lower() != ORDER_NO_PREDECESSOR:
                raise TranslationError(
                    f"{where} declares predecessor {ORDER_NO_PREDECESSOR!r} but "
                    f"names the predecessor ordinal item "
                    f"{declared_predecessor_item!r}"
                )
            predecessor_item = None
        else:
            predecessor_item = declared_predecessor_item.upper()
            if predecessor_item != resolution[predecessor]:
                raise TranslationError(
                    f"{where}.witness.predecessor_ordinal_item is "
                    f"{predecessor_item!r}; capture_ordinals resolves the event "
                    f"{predecessor!r} to {resolution[predecessor]!r}"
                )
        alternatives = []
        if "predecessor_ordinal_items_any" in witness:
            raw_alternatives = _require_sequence(
                witness["predecessor_ordinal_items_any"],
                f"{where}.witness.predecessor_ordinal_items_any",
            )
            if len(raw_alternatives) < 2:
                raise TranslationError(
                    f"{where}.witness.predecessor_ordinal_items_any holds "
                    f"{len(raw_alternatives)} item(s); a set of alternative "
                    f"predecessors holds at least two"
                )
            resolved_items = set(resolution.values())
            for position, item in enumerate(raw_alternatives):
                name = _require_text(
                    item,
                    f"{where}.witness.predecessor_ordinal_items_any[{position}]",
                ).strip().upper()
                if name not in resolved_items:
                    raise TranslationError(
                        f"{where}.witness.predecessor_ordinal_items_any names "
                        f"{name!r}, which no event id of capture_ordinals "
                        f"resolves to"
                    )
                if name in alternatives:
                    raise TranslationError(
                        f"{where}.witness.predecessor_ordinal_items_any repeats "
                        f"{name!r}"
                    )
                alternatives.append(name)
        named, comparisons, any_groups = _assertion_pairs(entry, where)
        declared_items = set(alternatives)
        declared_items.add(successor_item)
        if predecessor_item is not None:
            declared_items.add(predecessor_item)
        stray = sorted(named - declared_items)
        if stray:
            raise TranslationError(
                f"{where}.witness.assertions name ordinal item(s) {stray} that "
                f"the entry does not declare as predecessor, successor or "
                f"alternative predecessor"
            )
        if predecessor_item is None:
            expected_comparisons = [(successor_item, "equal_to", first_ordinal)]
        else:
            expected_comparisons = [
                (predecessor_item, "greater_than", 0),
                (successor_item, "greater_than", 0),
                (predecessor_item, "less_than", successor_item),
            ]
        if comparisons != expected_comparisons:
            raise TranslationError(
                f"{where}.witness.assertions compare {comparisons}; the pair "
                f"this entry declares requires exactly {expected_comparisons}"
            )
        if alternatives:
            if len(any_groups) != 1 or set(any_groups[0]) != set(alternatives):
                raise TranslationError(
                    f"{where}.witness.assertions test the alternative "
                    f"predecessors {any_groups}; the entry declares one group "
                    f"holding {sorted(alternatives)}"
                )
        elif any_groups:
            raise TranslationError(
                f"{where}.witness.assertions carry an any_of group but the "
                f"entry declares no alternative predecessor"
            )
        resolved.append(
            {
                "id": entry_id,
                "predecessor": predecessor,
                "successor": successor,
                "reason_kind": reason,
                "enforced_by": stub,
                "predecessor_ordinal_item": predecessor_item,
                "predecessor_ordinal_items_any": tuple(alternatives),
                "successor_ordinal_item": successor_item,
                "first_captured_ordinal": (
                    expected_comparisons[0][2] if predecessor_item is None else None
                ),
            }
        )
    covered = {record["successor_ordinal_item"] for record in resolved}
    missing = sorted(set(resolution.values()) - covered)
    if missing:
        raise TranslationError(
            f"{label} carries no entry whose successor stamps {missing}; every "
            f"ordinal item capture_ordinals resolves to is the successor of one "
            f"entry"
        )
    return resolved


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


def _pinned_witness_copybook() -> str:
    """Return the repository-relative path of the capture-state copybook."""
    return (
        EXPECTED_COPYBOOK_DIR.relative_to(REPO_ROOT) / ORDER_WITNESS_COPYBOOK
    ).as_posix()


def _require_witness_copybook(value, label: str) -> None:
    """Require a declared witness copybook to be the pinned capture copybook."""
    declared = _require_text(value, label).strip()
    expected = _pinned_witness_copybook()
    if Path(declared).as_posix() != expected:
        raise TranslationError(
            f"{label} names {declared!r}; every ordinal item of the order "
            f"metadata is declared by {expected}"
        )


def _require_declared_ordinal_item(
    value, label: str, declared_items: dict, ordinal_pic: str
) -> str:
    """Return the ordinal item ``value`` names, checked against the copybook.

    The name must be declared by the pinned capture copybook and must carry the
    PICTURE the order metadata declares for an ordinal, so an item that was
    renamed, removed or re-shaped in that copybook is reported here instead of
    reaching a generated program or a stub-side guard.
    """
    name = _require_text(value, label).strip().upper()
    if name not in declared_items:
        raise TranslationError(
            f"{label} names {name!r}, which {_pinned_witness_copybook()} does "
            f"not declare"
        )
    picture = declared_items[name]
    if picture != ordinal_pic:
        raise TranslationError(
            f"{label} names {name!r}, declared by {_pinned_witness_copybook()} "
            f"with PICTURE {picture!r}; the order metadata declares ordinal_pic "
            f"{ordinal_pic!r}"
        )
    return name


def _validate_ordinal_table(
    capture: dict, dml: list, declared_items: dict, label: str
) -> dict:
    """Check ``capture_ordinals`` against the dml entries and the copybook.

    Returns the resolved ordinal table: the item each dml id stamps, the item
    of the KSDSPOLY write, the shared sequence item, the value an unstamped
    ordinal holds and the highest value an ordinal can carry.  Every member is
    type-checked, every ordinal item is required to be declared by the pinned
    capture copybook with the declared ordinal PICTURE, the keys are required
    to be exactly the declared dml ids, two ids sharing one ordinal are
    required to share one stub, and ``distinct_ordinal_items`` is required to
    equal the number of distinct items the table names.
    """
    _require_keys(capture, CAPTURE_ORDINALS_KEYS, label)
    _require_witness_copybook(capture["copybook"], f"{label}.copybook")
    ordinal_pic = (
        _require_text(capture["ordinal_pic"], f"{label}.ordinal_pic").strip().upper()
    )
    pic_match = ORDINAL_PIC_RE.match(ordinal_pic)
    if pic_match is None:
        raise TranslationError(
            f"{label}.ordinal_pic is {ordinal_pic!r}; an unsigned display "
            f"picture of the form 9(n) is required"
        )
    max_ordinal = 10 ** int(pic_match.group("digits")) - 1
    unstamped = _require_integer(
        capture["unstamped_value"], f"{label}.unstamped_value"
    )
    if unstamped != EXPECTED_UNSTAMPED_ORDINAL:
        raise TranslationError(
            f"{label}.unstamped_value is {unstamped}; an ordinal that was never "
            f"stamped holds {EXPECTED_UNSTAMPED_ORDINAL}, the value the driver "
            f"clears the capture state to"
        )
    sequence_item = _require_declared_ordinal_item(
        capture["sequence_item"], f"{label}.sequence_item", declared_items,
        ordinal_pic,
    )

    call_program_by_id = {}
    for index, entry in enumerate(dml):
        call_program_by_id[str(entry["id"])] = str(entry["call_program"])
    by_dml_id = _require_mapping(capture["by_dml_id"], f"{label}.by_dml_id")
    if sorted(by_dml_id) != sorted(call_program_by_id):
        raise TranslationError(
            f"{label}.by_dml_id names {sorted(by_dml_id)}; the declared dml ids "
            f"are {sorted(call_program_by_id)}"
        )
    ordinal_by_id = {}
    first_id_of_item = {}
    for dml_id in sorted(call_program_by_id):
        item = _require_declared_ordinal_item(
            by_dml_id[dml_id], f"{label}.by_dml_id[{dml_id}]", declared_items,
            ordinal_pic,
        )
        if item == sequence_item:
            raise TranslationError(
                f"{label}.by_dml_id[{dml_id}] names the shared sequence item "
                f"{item!r}; an ordinal item is stamped from it and is not it"
            )
        ordinal_by_id[dml_id] = item
        owner = first_id_of_item.setdefault(item, dml_id)
        if call_program_by_id[owner] != call_program_by_id[dml_id]:
            raise TranslationError(
                f"{label}.by_dml_id gives dml ids {owner!r} and {dml_id!r} the "
                f"one ordinal item {item!r}, but they call "
                f"{call_program_by_id[owner]!r} and "
                f"{call_program_by_id[dml_id]!r}; ids sharing an ordinal share "
                f"the stub that stamps it"
            )
    vsam_item = _require_declared_ordinal_item(
        capture["vsam_write_ordinal_item"], f"{label}.vsam_write_ordinal_item",
        declared_items, ordinal_pic,
    )
    if vsam_item == sequence_item:
        raise TranslationError(
            f"{label}.vsam_write_ordinal_item names the shared sequence item "
            f"{vsam_item!r}; an ordinal item is stamped from it and is not it"
        )
    if vsam_item in set(ordinal_by_id.values()):
        raise TranslationError(
            f"{label}.vsam_write_ordinal_item names {vsam_item!r}, already "
            f"stamped by dml id {first_id_of_item[vsam_item]!r}; the KSDSPOLY "
            f"write is not an EXEC SQL block of this map"
        )
    distinct = set(ordinal_by_id.values()) | {vsam_item}
    declared_distinct = _require_integer(
        capture["distinct_ordinal_items"], f"{label}.distinct_ordinal_items"
    )
    if declared_distinct != len(distinct):
        raise TranslationError(
            f"{label}.distinct_ordinal_items is {declared_distinct}; the table "
            f"names {len(distinct)} distinct ordinal items "
            f"{sorted(distinct)}"
        )
    return {
        "ordinal_by_id": ordinal_by_id,
        "vsam_item": vsam_item,
        "sequence_item": sequence_item,
        "items": distinct,
        "unstamped": unstamped,
        "max_ordinal": max_ordinal,
        "ordinal_pic": ordinal_pic,
    }


def _describe_assertion(assertion: tuple) -> str:
    """Render one normalised assertion as the text a diagnostic reads.

    An item on the right prints as its name and a literal as its digits, so
    ``HC-POL-SEQ less_than HC-HOU-SEQ`` and ``HC-HOU-SEQ greater_than 0`` read
    the way the witness of the constraint spells them.
    """
    left, operator, (_kind, right) = assertion
    return f"{left} {operator} {right}"


def _normalise_order_assertion(
    raw, label: str, witness_items: set, ordinals: dict
) -> tuple:
    """Return one simple assertion as ``(left, operator, (kind, right))``.

    ``left_item`` and ``right_item`` must name an ordinal item this entry's
    witness carries, ``operator`` must be one of the closed set, and exactly
    one of ``right_item`` and ``right_literal`` must be present.  A literal must
    be an integer inside the range the declared ordinal PICTURE can hold.
    """
    assertion = _require_mapping(raw, label)
    unknown = sorted(
        set(assertion) - {"left_item", "operator", "right_item", "right_literal"}
    )
    if unknown:
        raise TranslationError(
            f"{label} carries the unknown member(s) {unknown}; an assertion "
            f"carries left_item, operator and one of right_item or right_literal"
        )
    _require_keys(assertion, ("left_item", "operator"), label)
    left = _require_text(assertion["left_item"], f"{label}.left_item").strip().upper()
    if left not in witness_items:
        raise TranslationError(
            f"{label}.left_item names {left!r}, which the witness of this entry "
            f"does not carry; the witness names {sorted(witness_items)}"
        )
    operator = _require_text(assertion["operator"], f"{label}.operator").strip()
    if operator not in ORDER_ASSERTION_OPERATORS:
        raise TranslationError(
            f"{label}.operator is {operator!r}; the accepted operators are "
            f"{sorted(ORDER_ASSERTION_OPERATORS)}"
        )
    has_item = "right_item" in assertion
    has_literal = "right_literal" in assertion
    if has_item == has_literal:
        declared = (
            "both right_item and right_literal"
            if has_item
            else "neither right_item nor right_literal"
        )
        raise TranslationError(
            f"{label} declares {declared}; exactly one of them stands on the "
            f"right of an assertion"
        )
    if has_item:
        right = _require_text(
            assertion["right_item"], f"{label}.right_item"
        ).strip().upper()
        if right not in witness_items:
            raise TranslationError(
                f"{label}.right_item names {right!r}, which the witness of this "
                f"entry does not carry; the witness names {sorted(witness_items)}"
            )
        if right == left:
            raise TranslationError(
                f"{label} compares {left!r} with itself"
            )
        return (left, operator, ("item", right))
    literal = _require_integer(
        assertion["right_literal"], f"{label}.right_literal"
    )
    if literal < 0 or literal > ordinals["max_ordinal"]:
        raise TranslationError(
            f"{label}.right_literal is {literal}; an ordinal declared "
            f"PIC {ordinals['ordinal_pic']} holds 0 through "
            f"{ordinals['max_ordinal']}"
        )
    return (left, operator, ("literal", literal))


def _validate_order_assertions(
    entry: dict, label: str, witness_items: set, required: set, required_any: set,
    ordinals: dict,
) -> int:
    """Check the assertions of one execution_order entry.

    Every assertion is normalised, so each one names ordinal items and an
    operator this translator can resolve, and the set the entry declares must
    contain the forms the constraint's own shape requires: the ordering pair and
    both stamped tests for a pair constraint, the first-ordinal equality for the
    constraint on the first captured event, and, where the witness names
    alternative predecessors, one ``any_of`` group holding exactly one stamped
    test per alternative.  Returns the number of assertions validated.
    """
    assertions = _require_sequence(entry["assertions"], f"{label}.assertions")
    if not assertions:
        raise TranslationError(f"{label}.assertions declares no assertion")
    simple = set()
    any_groups = []
    counted = 0
    for position, raw in enumerate(assertions):
        where = f"{label}.assertions[{position}]"
        assertion = _require_mapping(raw, where)
        if "any_of" in assertion:
            if len(assertion) != 1:
                raise TranslationError(
                    f"{where} carries any_of beside "
                    f"{sorted(set(assertion) - {'any_of'})}; an any_of group "
                    f"holds nothing else"
                )
            members = _require_sequence(assertion["any_of"], f"{where}.any_of")
            if len(members) < 2:
                raise TranslationError(
                    f"{where}.any_of holds {len(members)} member(s); a group of "
                    f"alternatives holds at least two"
                )
            group = set()
            for member_position, member in enumerate(members):
                group.add(
                    _normalise_order_assertion(
                        member, f"{where}.any_of[{member_position}]",
                        witness_items, ordinals,
                    )
                )
                counted += 1
            any_groups.append(group)
            continue
        simple.add(
            _normalise_order_assertion(raw, where, witness_items, ordinals)
        )
        counted += 1
    missing = sorted(
        _describe_assertion(assertion) for assertion in required - simple
    )
    if missing:
        raise TranslationError(
            f"{label}.assertions does not assert {missing}; the shape of this "
            f"constraint requires those assertion(s)"
        )
    if required_any and required_any not in any_groups:
        raise TranslationError(
            f"{label}.assertions carries no any_of group asserting "
            f"{sorted(_describe_assertion(item) for item in required_any)}, one "
            f"stamped test for each alternative predecessor the witness names"
        )
    if any_groups and not required_any:
        raise TranslationError(
            f"{label}.assertions carries an any_of group, but the witness of "
            f"this entry names no alternative predecessor"
        )
    return counted


def _validate_order_constraints(
    entries: list, dml: list, ordinals: dict, declared_items: dict, label: str,
) -> list:
    """Check ``execution_order`` against the dml entries, the ordinals and the
    capturing stubs, and return one summary record per constraint.

    Each entry is required to name a declared dml id, or the documented
    sentinel, on both sides; to carry a reason kind from the closed set, with
    the host of a data dependency declared by the successor block; to name the
    capturing stub that stands in for its successor as the file that enforces
    it, and that file must name the ordinal items of the constraint and both
    order-guard items in its code; and to carry a witness whose ordinal items
    are the ones ``capture_ordinals`` gives its two sides.  Every ordinal item
    of the capture state must stand as the successor of exactly one entry, so a
    captured statement without an ordering constraint, or a constraint on an
    ordinal that no longer exists, is reported here.
    """
    dml_by_id = {}
    for entry in dml:
        dml_by_id[str(entry["id"])] = entry
    stub_code = {}
    summaries = []
    seen_ids = set()
    successor_items = {}
    for index, raw_entry in enumerate(entries):
        where = f"{label}[{index}]"
        entry = _require_mapping(raw_entry, where)
        _require_keys(entry, EXECUTION_ORDER_KEYS, where)
        constraint_id = _require_text(entry["id"], f"{where}.id").strip()
        if constraint_id in seen_ids:
            raise TranslationError(
                f"{label} repeats the constraint id {constraint_id!r}"
            )
        seen_ids.add(constraint_id)
        where = f"{label}[{constraint_id}]"
        _require_text(entry["note"], f"{where}.note")

        reason_kind = _require_text(
            entry["reason_kind"], f"{where}.reason_kind"
        ).strip()
        if reason_kind not in ORDER_REASON_KINDS:
            raise TranslationError(
                f"{where}.reason_kind is {reason_kind!r}; the accepted kinds are "
                f"{sorted(ORDER_REASON_KINDS)}"
            )

        successor = _require_text(entry["successor"], f"{where}.successor").strip()
        if successor == ORDER_VSAM_SUCCESSOR:
            successor_item = ordinals["vsam_item"]
            successor_stub = f"{ORDER_VSAM_SUCCESSOR}.cbl"
        elif successor in dml_by_id:
            successor_item = ordinals["ordinal_by_id"][successor]
            successor_stub = (
                str(dml_by_id[successor]["call_program"]).strip().lower().replace(
                    "-", "_"
                )
                + ".cbl"
            )
        else:
            raise TranslationError(
                f"{where}.successor is {successor!r}; a successor names a "
                f"declared dml id {sorted(dml_by_id)} or the sentinel "
                f"{ORDER_VSAM_SUCCESSOR!r}"
            )

        predecessor = _require_text(
            entry["predecessor"], f"{where}.predecessor"
        ).strip()
        if predecessor == ORDER_NO_PREDECESSOR:
            predecessor_item = None
        elif predecessor in dml_by_id:
            predecessor_item = ordinals["ordinal_by_id"][predecessor]
        else:
            raise TranslationError(
                f"{where}.predecessor is {predecessor!r}; a predecessor names a "
                f"declared dml id {sorted(dml_by_id)} or the sentinel "
                f"{ORDER_NO_PREDECESSOR!r}"
            )
        if predecessor_item is not None and predecessor_item == successor_item:
            raise TranslationError(
                f"{where} orders {predecessor!r} against {successor!r}, which "
                f"both stamp the one ordinal item {successor_item!r}"
            )

        host = entry.get("host")
        if reason_kind == "data_dependency":
            if host is None:
                raise TranslationError(
                    f"{where} declares reason_kind {reason_kind!r} and must name "
                    f"the host the successor takes from the predecessor"
                )
            host_name = _require_text(host, f"{where}.host").strip().upper()
            if successor not in dml_by_id:
                raise TranslationError(
                    f"{where} declares reason_kind {reason_kind!r} with host "
                    f"{host_name!r}, but its successor {successor!r} declares no "
                    f"host list"
                )
            declared_hosts = {
                str(item["host"]).strip().upper()
                for item in dml_by_id[successor]["using"]
            }
            if host_name not in declared_hosts:
                raise TranslationError(
                    f"{where}.host is {host_name!r}, which dml[{successor}] does "
                    f"not declare; that entry declares {sorted(declared_hosts)}"
                )
        elif host is not None:
            raise TranslationError(
                f"{where} declares host {host!r} with reason_kind "
                f"{reason_kind!r}; only a data dependency names a host"
            )

        enforced_by = _require_text(
            entry["enforced_by"], f"{where}.enforced_by"
        ).strip()
        if Path(enforced_by).name != successor_stub:
            raise TranslationError(
                f"{where}.enforced_by names {enforced_by!r}; the successor "
                f"{successor!r} is captured by {successor_stub}, which is the "
                f"file that enforces this constraint"
            )
        if enforced_by not in stub_code:
            stub_code[enforced_by] = code_area_text(
                enforced_by,
                read_harness_stub(enforced_by, f"{where}.enforced_by"),
            )

        witness = _require_mapping(entry["witness"], f"{where}.witness")
        _require_keys(witness, ORDER_WITNESS_KEYS, f"{where}.witness")
        _require_witness_copybook(
            witness["copybook"], f"{where}.witness.copybook"
        )
        declared_successor_item = _require_declared_ordinal_item(
            witness["successor_ordinal_item"],
            f"{where}.witness.successor_ordinal_item", declared_items,
            ordinals["ordinal_pic"],
        )
        if declared_successor_item != successor_item:
            raise TranslationError(
                f"{where}.witness.successor_ordinal_item names "
                f"{declared_successor_item!r}; capture_ordinals gives successor "
                f"{successor!r} the ordinal item {successor_item!r}"
            )
        declared_predecessor = _require_text(
            witness["predecessor_ordinal_item"],
            f"{where}.witness.predecessor_ordinal_item",
        ).strip()
        if predecessor_item is None:
            if declared_predecessor != ORDER_NO_PREDECESSOR:
                raise TranslationError(
                    f"{where}.witness.predecessor_ordinal_item names "
                    f"{declared_predecessor!r}; this constraint declares "
                    f"predecessor {ORDER_NO_PREDECESSOR!r} and its witness "
                    f"carries the same sentinel"
                )
        else:
            declared_predecessor = _require_declared_ordinal_item(
                declared_predecessor,
                f"{where}.witness.predecessor_ordinal_item", declared_items,
                ordinals["ordinal_pic"],
            )
            if declared_predecessor != predecessor_item:
                raise TranslationError(
                    f"{where}.witness.predecessor_ordinal_item names "
                    f"{declared_predecessor!r}; capture_ordinals gives "
                    f"predecessor {predecessor!r} the ordinal item "
                    f"{predecessor_item!r}"
                )

        witness_items = {successor_item}
        if predecessor_item is not None:
            witness_items.add(predecessor_item)
        alternatives = []
        if "predecessor_ordinal_items_any" in witness:
            raw_alternatives = _require_sequence(
                witness["predecessor_ordinal_items_any"],
                f"{where}.witness.predecessor_ordinal_items_any",
            )
            if len(raw_alternatives) < 2:
                raise TranslationError(
                    f"{where}.witness.predecessor_ordinal_items_any holds "
                    f"{len(raw_alternatives)} item(s); a set of alternative "
                    f"predecessors holds at least two"
                )
            for position, value in enumerate(raw_alternatives):
                item = _require_declared_ordinal_item(
                    value,
                    f"{where}.witness.predecessor_ordinal_items_any[{position}]",
                    declared_items, ordinals["ordinal_pic"],
                )
                if item in alternatives:
                    raise TranslationError(
                        f"{where}.witness.predecessor_ordinal_items_any repeats "
                        f"{item!r}"
                    )
                if item in (successor_item, predecessor_item):
                    raise TranslationError(
                        f"{where}.witness.predecessor_ordinal_items_any names "
                        f"{item!r}, already named as the successor or the "
                        f"predecessor of this constraint"
                    )
                alternatives.append(item)
            witness_items.update(alternatives)

        if predecessor_item is None:
            required = {
                (
                    successor_item, "equal_to",
                    ("literal", ordinals["unstamped"] + 1),
                )
            }
        else:
            required = {
                (predecessor_item, "greater_than",
                 ("literal", ordinals["unstamped"])),
                (successor_item, "greater_than",
                 ("literal", ordinals["unstamped"])),
                (predecessor_item, "less_than", ("item", successor_item)),
            }
        required_any = {
            (item, "greater_than", ("literal", ordinals["unstamped"]))
            for item in alternatives
        }
        assertion_count = _validate_order_assertions(
            witness, f"{where}.witness", witness_items, required, required_any,
            ordinals,
        )

        for item in sorted(witness_items) + list(ORDER_GUARD_ITEMS):
            if not code_references_item(stub_code[enforced_by], item):
                raise TranslationError(
                    f"{where} is enforced by {enforced_by}, whose code does not "
                    f"name {item!r}; the enforcing stub stamps its own ordinal, "
                    f"reads the ordinal of every prerequisite and reports a "
                    f"violation in {list(ORDER_GUARD_ITEMS)}"
                )

        if successor_item in successor_items:
            raise TranslationError(
                f"{where} and {label}[{successor_items[successor_item]}] both "
                f"stand as the constraint on ordinal item {successor_item!r}; "
                f"each captured statement carries one"
            )
        successor_items[successor_item] = constraint_id
        summaries.append(
            {
                "id": constraint_id,
                "predecessor": predecessor,
                "successor": successor,
                "reason_kind": reason_kind,
                "predecessor_ordinal_item": predecessor_item or ORDER_NO_PREDECESSOR,
                "successor_ordinal_item": successor_item,
                "alternative_predecessor_ordinal_items": alternatives,
                "enforced_by": enforced_by,
                "assertions": assertion_count,
            }
        )

    uncovered = sorted(ordinals["items"] - set(successor_items))
    if uncovered:
        raise TranslationError(
            f"{label} declares no constraint on the ordinal item(s) "
            f"{uncovered}; every captured statement of capture_ordinals carries "
            f"one"
        )
    return summaries


def _validate_order_metadata(
    data: dict, dml: list, checks: dict, copybook_dir: Path, label: str
) -> dict:
    """Validate the order metadata of the map and return its report record.

    Reads the pinned capture copybook for the item names and pictures the
    metadata is held to, checks ``capture_ordinals`` against the dml entries,
    checks every ``execution_order`` entry against the ordinals it names, the
    host list of its successor and the capturing stub it names as its enforcer,
    and reconciles ``checks.order_constraint_count`` with the expected figure
    and with the number of entries.  ``distinct_ordinal_items`` is reconciled
    with the ordinal table itself, and the one-constraint-per-ordinal relation
    between the two sections is carried by the constraint validation: no two
    entries stand on one ordinal item and no ordinal item is left without an
    entry.
    """
    _require_keys(data, ("execution_order", "capture_ordinals"), label)
    entries = _require_sequence(data["execution_order"], f"{label}: execution_order")
    capture = _require_mapping(
        data["capture_ordinals"], f"{label}: capture_ordinals"
    )
    declared_items = declared_copybook_items(
        _pinned_witness_copybook(),
        read_harness_copybook(copybook_dir, ORDER_WITNESS_COPYBOOK),
    )
    for item in ORDER_GUARD_ITEMS:
        if item not in declared_items:
            raise TranslationError(
                f"{_pinned_witness_copybook()} does not declare the order-guard "
                f"item {item!r} the capturing stubs report a violation in"
            )
    ordinals = _validate_ordinal_table(
        capture, dml, declared_items, f"{label}: capture_ordinals"
    )
    declared_count = _require_integer(
        checks["order_constraint_count"], f"{label}: checks.order_constraint_count"
    )
    if declared_count != EXPECTED_MAP_ORDER_CONSTRAINT_COUNT:
        raise TranslationError(
            f"checks.order_constraint_count is {declared_count}, expected "
            f"{EXPECTED_MAP_ORDER_CONSTRAINT_COUNT}"
        )
    if len(entries) != declared_count:
        raise TranslationError(
            f"execution_order holds {len(entries)} entries but "
            f"checks.order_constraint_count is {declared_count}"
        )
    summaries = _validate_order_constraints(
        entries, dml, ordinals, declared_items, f"{label}: execution_order"
    )
    return {
        "declared_constraints": declared_count,
        "validated_constraints": len(summaries),
        "witness_copybook": _pinned_witness_copybook(),
        "sequence_item": ordinals["sequence_item"],
        "unstamped_value": ordinals["unstamped"],
        "ordinal_pic": ordinals["ordinal_pic"],
        "ordinal_by_dml_id": dict(sorted(ordinals["ordinal_by_id"].items())),
        "vsam_write_ordinal_item": ordinals["vsam_item"],
        "constraints": summaries,
    }


def read_statement_map_document(path: Path):
    """Read ``statement_map.yml`` and compose the document it carries.

    The bytes are read under ``MAX_STATEMENT_MAP_BYTES`` through the
    descriptor walk every read of this translator uses, decoded as UTF-8 and
    composed with aliases, merge keys and duplicate keys refused.  The document
    is returned exactly as composed; nothing of its content is checked here.
    """
    components = lexical_repo_components(path, "--statement-map")
    raw = read_repo_file(components, "--statement-map", MAX_STATEMENT_MAP_BYTES)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise TranslationError(
            f"statement map {path} is not valid UTF-8: {error}"
        ) from error
    loader = _StrictMapLoader(text)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()


def load_statement_map(path: Path, copybook_dir: Path) -> dict:
    """Load and validate ``statement_map.yml`` before any generation happens.

    The document is read under a byte bound, composed with aliases, merge keys
    and duplicate keys refused, bounded again by nesting depth and value count,
    and then type-checked member by member.  The ``checks`` block is compared
    with the expected census (3 includes, 8 dml entries, 11 blocks in total,
    one ``using_counts`` entry per stub, seven ``call_programs`` and 8 order
    constraints) and every entry is checked for internal consistency.  The
    ``source_program`` block is compared member by member with the authorized
    source it names.  The ``execution_order`` and ``capture_ordinals`` blocks
    are checked against the dml entries, against the ordinal items
    ``copybook_dir/hcapture.cpy`` declares and against the capturing stub each
    constraint names as its enforcer.
    """
    return validate_statement_map_document(
        read_statement_map_document(path), path, copybook_dir
    )


def validate_statement_map_document(data, path: Path, copybook_dir: Path) -> dict:
    """Validate one composed statement-map document and return its contract.

    ``data`` is the document ``read_statement_map_document`` composed for
    ``path``; every check the loaded map is held to is applied here, so the
    same document supplied from anywhere is held to the same contract.  Returns
    the validated blocks, the declared program name, the ordering metadata, the
    event-to-ordinal resolution and the order records the generation reads.
    """
    _bound_loaded_document(data, f"statement map {path}")
    data = _require_mapping(data, f"{path}")
    _validate_map_scalar_types(data, f"statement map {path}")

    _require_keys(
        data,
        ("includes", "dml", "checks", "source_program", "execution_order",
         "capture_ordinals"),
        f"{path}",
    )
    includes = _require_sequence(data["includes"], "includes")
    dml = _require_sequence(data["dml"], "dml")
    checks = _require_mapping(data["checks"], "checks")
    source_program = _require_mapping(data["source_program"], "source_program")
    execution_order = _require_sequence(data["execution_order"], "execution_order")
    capture_ordinals = _require_mapping(
        data["capture_ordinals"], "capture_ordinals"
    )

    _require_keys(
        checks,
        ("include_count", "dml_count", "total_blocks", "using_counts",
         "call_programs", "order_constraint_count"),
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
    order_metadata = _validate_order_metadata(
        data, dml, checks, copybook_dir, f"statement map {path}"
    )

    ordinal_resolution = _validate_capture_ordinals(
        capture_ordinals, seen_dml_ids, "capture_ordinals"
    )
    # The first ordinal any member can hold is one past the unstamped value
    # this map declares; a first-captured entry asserts exactly that value.
    first_ordinal = int(capture_ordinals["unstamped_value"]) + 1
    order_records = _validate_execution_order(
        execution_order, ordinal_resolution, first_ordinal, "execution_order"
    )
    return {
        "path": path,
        "source_program": source_program,
        "declared_program": declared_program,
        "includes": includes,
        "dml": dml,
        "checks": checks,
        "order_metadata": order_metadata,
        "execution_order": execution_order,
        "capture_ordinals": capture_ordinals,
        "ordinal_resolution": ordinal_resolution,
        "order_records": order_records,
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
        """Apply every rule to the source and hold the result to its census.

        The rules run first, then the measured line total and block counts are
        compared with the pinned census of the named source.
        """
        result = self.apply_rules()
        self._verify_census()
        return result

    def apply_rules(self) -> ProgramResult:
        """Apply rules R1-R14 to the source text and return the result.

        The census of the named source is not consulted here, so a fragment of
        fixed-format source shorter than a whole program is translated by the
        same rule table the three authorized programs go through.
        """
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
            notes="control returns to the caller at this point; see "
            "modernization/docs/decision-log.md, row: no called RETURN stub",
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
# Capture-order contract: statement map, capture copybook and capture stubs
# --------------------------------------------------------------------------
def _decode_harness_text(data: bytes, display: str) -> str:
    """Decode an authored harness artifact, reporting an undecodable byte."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise TranslationError(
            f"{display} is not valid UTF-8: {error}"
        ) from error


def _code_lines_of(text: str) -> list:
    """Return the (line number, code area) pair of every non-comment line."""
    pairs = []
    for number, line in enumerate(text.split("\n"), start=1):
        if not line.strip() or is_comment_line(line):
            continue
        code = code_of(line).rstrip()
        if code.strip():
            pairs.append((number, code.strip()))
    return pairs


def _comment_lines_of(text: str) -> list:
    """Return the (line number, comment text) pair of every comment line."""
    pairs = []
    for number, line in enumerate(text.split("\n"), start=1):
        if is_comment_line(line):
            pairs.append((number, code_of(line).rstrip()))
    return pairs


DRIVER_ORDER_PLACEMENT_RE = re.compile(
    r"MOVE\s+'(?P<event>[A-Za-z0-9_]+)'\s+TO\s+WS-ORDER-NAME\("
    r"WS-ORDER-COUNT\)\s+MOVE\s+(?P<ordinal>HC-[A-Z0-9-]+)\s+TO\s+"
    r"WS-ORDER-SEQ\(WS-ORDER-COUNT\)"
)
DRIVER_ORDER_VERDICT_RE = re.compile(r"IF\s+HC-ORDER-VIOLATION\b")


def verify_driver_order_agreement(text: str, display: str, resolution: dict) -> dict:
    """Reconcile the driver's own order evaluation with the map's metadata.

    The driver names each captured statement and reads its ordinal into the
    order table it walks, and it reads the guard verdict the capture stubs
    write.  Both readings must describe the same events as the map: a placement
    whose ordinal item differs from the one ``capture_ordinals`` resolves for
    that event, an event the map resolves no ordinal for, an ordinal item the
    map resolves that the driver never places, a placement repeated under one
    event name, and a driver that never reads the guard verdict are each a hard
    failure.  An event whose map ids carry a branch suffix, such as the two
    endowment insert branches sharing one ordinal, is matched on the ordinal the
    branches resolve to.  Returns the reconciliation for the report.
    """
    placements = {}
    for match in DRIVER_ORDER_PLACEMENT_RE.finditer(
        " ".join(code for _, code in _code_lines_of(text))
    ):
        event = match.group("event")
        ordinal = match.group("ordinal").upper()
        if event in placements:
            raise TranslationError(
                f"{display} places the event {event!r} in its order table more "
                f"than once, as {placements[event]!r} and {ordinal!r}"
            )
        placements[event] = ordinal
    if not placements:
        raise TranslationError(
            f"{display} builds no order table this translator can read: no "
            f"WS-ORDER-NAME and WS-ORDER-SEQ pair was found"
        )
    for event, ordinal in sorted(placements.items()):
        declared = resolution.get(event)
        if declared is None:
            branches = sorted(
                item
                for name, item in resolution.items()
                if name.startswith(f"{event}_")
            )
            if not branches:
                raise TranslationError(
                    f"{display} places the event {event!r}, which the "
                    f"capture_ordinals block of the statement map resolves no "
                    f"ordinal item for"
                )
            if set(branches) != {ordinal}:
                raise TranslationError(
                    f"{display} reads {ordinal!r} for the event {event!r}, "
                    f"while the statement map resolves its branches to "
                    f"{branches}"
                )
            continue
        if declared != ordinal:
            raise TranslationError(
                f"{display} reads {ordinal!r} for the event {event!r}, while "
                f"the capture_ordinals block of the statement map resolves that "
                f"event to {declared!r}"
            )
    unplaced = sorted(set(resolution.values()) - set(placements.values()))
    if unplaced:
        raise TranslationError(
            f"the statement map resolves the ordinal item(s) {unplaced}, which "
            f"{display} never places in its order table, so its evaluation of "
            f"the order does not cover them"
        )
    if not DRIVER_ORDER_VERDICT_RE.search(
        " ".join(code for _, code in _code_lines_of(text))
    ):
        raise TranslationError(
            f"{display} never reads HC-ORDER-VIOLATION, so the verdict the "
            f"capture stubs write is not evaluated by the driver"
        )
    return {
        "driver": display,
        "order_table_events": {
            event: ordinal for event, ordinal in sorted(placements.items())
        },
        "reads_order_violation": True,
    }


def _declared_ordinal_items(text: str, expected_pic: str, display: str) -> dict:
    """Return every ordinal item the capture copybook declares, with its line.

    An ordinal declared with a PIC other than the one ``capture_ordinals``
    declares is refused: the map's ``unstamped_value`` and the driver's
    comparisons read every ordinal at one width.
    """
    declared = {}
    for number, code in _code_lines_of(text):
        match = CAPTURE_ORDINAL_DECLARATION_RE.match(code)
        if match is None:
            continue
        name = match.group("name").upper()
        pic = match.group("pic")
        if name in declared:
            raise TranslationError(
                f"{display}:{number} declares the ordinal item {name} a second "
                f"time; it is already declared at line {declared[name]['line']}"
            )
        if pic.upper() != expected_pic.upper():
            raise TranslationError(
                f"{display}:{number} declares {name} as PIC {pic}; "
                f"capture_ordinals.ordinal_pic declares every ordinal item as "
                f"PIC {expected_pic}"
            )
        declared[name] = {"line": number, "pic": pic}
    return declared


def _declared_prerequisite_table(text: str, display: str) -> dict:
    """Return the prerequisite table the capture copybook carries.

    The table follows ``CAPTURE_TABLE_HEADING`` and ends at the first blank
    comment line after it.  A row names one capturing member and the ordinal
    item or items that member reads; a continuation line carries the rest of
    the row.  ``equal_to`` holds the ordinal value a row requires of a member
    that reads no predecessor.
    """
    lines = _comment_lines_of(text)
    heading = None
    for index, (number, comment) in enumerate(lines):
        if CAPTURE_TABLE_HEADING in comment:
            if heading is not None:
                raise TranslationError(
                    f"{display}:{number} repeats the prerequisite table heading "
                    f"{CAPTURE_TABLE_HEADING!r}, already at line "
                    f"{lines[heading][0]}"
                )
            heading = index
    if heading is None:
        raise TranslationError(
            f"{display} carries no prerequisite table: no comment line holds "
            f"{CAPTURE_TABLE_HEADING!r}"
        )
    table = {}
    current = None
    for number, comment in lines[heading + 1:]:
        body = comment.lstrip("*").strip()
        if not body:
            break
        match = CAPTURE_TABLE_MEMBER_RE.match(body)
        if match is not None:
            member = match.group(1)
            if member in table:
                raise TranslationError(
                    f"{display}:{number} names the member {member} a second "
                    f"time in the prerequisite table; it is already named at "
                    f"line {table[member]['line']}"
                )
            current = {"line": number, "items": [], "equal_to": None}
            table[member] = current
            body = match.group(2)
        if current is None:
            raise TranslationError(
                f"{display}:{number} stands in the prerequisite table before "
                f"any member is named"
            )
        for item in CAPTURE_ORDINAL_ITEM_RE.findall(body):
            if item not in current["items"]:
                current["items"].append(item)
        equal_to = CAPTURE_TABLE_EQUAL_TO_RE.search(body)
        if equal_to is not None:
            current["equal_to"] = int(equal_to.group(1))
    if not table:
        raise TranslationError(
            f"{display} carries a prerequisite table heading with no member row "
            f"below it"
        )
    return table


def _stub_order_guard(text: str, display: str) -> dict:
    """Return the order guard one capture stub carries.

    ``sequence_item`` and ``ordinal_item`` name the item the stub reads the
    shared sequence value from and the ordinal it stamps with it; ``condition``
    is the text of the guard that reports a violation, taken from its ``IF``
    through to the report itself; ``items`` are the ordinal items that
    condition names; ``read`` are the ordinal items the whole stub names;
    ``last_statement`` and ``violation_statement`` are the operands the stub
    moves into HC-ORDER-LAST-STMT and HC-ORDER-VIOLATION-STMT.  Code lines
    only are read, so a comment naming one of these items is not a write.  A
    stub carries exactly one stamp, one violation report, one move into
    HC-ORDER-LAST-STMT and one move into HC-ORDER-VIOLATION-STMT; any other
    count fails the run.
    """
    code = _code_lines_of(text)
    joined = "\n".join(line for _, line in code)
    stamps = STUB_ORDINAL_STAMP_RE.findall(joined)
    if len(stamps) != 1:
        raise TranslationError(
            f"{display} moves the shared sequence value into "
            f"{len(stamps)} ordinal item(s); a capture stub stamps exactly one"
        )
    sequence_item, ordinal_item = stamps[0]
    flag_positions = [
        index for index, (_, line) in enumerate(code)
        if STUB_VIOLATION_FLAG_RE.search(line)
    ]
    if len(flag_positions) != 1:
        raise TranslationError(
            f"{display} reports an order violation at {len(flag_positions)} "
            f"site(s); a capture stub carries exactly one order guard"
        )
    flag_index = flag_positions[0]
    start = None
    for index in range(flag_index - 1, -1, -1):
        if STUB_GUARD_START_RE.match(code[index][1]):
            start = index
            break
    if start is None:
        raise TranslationError(
            f"{display}:{code[flag_index][0]} reports an order violation "
            f"outside any IF; the guard tests its prerequisite ordinal before "
            f"it reports"
        )
    condition = " ".join(line for _, line in code[start:flag_index])
    last_statements = STUB_LAST_STMT_RE.findall(joined)
    if len(last_statements) != 1:
        raise TranslationError(
            f"{display} moves {len(last_statements)} operand(s) into "
            f"HC-ORDER-LAST-STMT; a capture stub names itself there exactly "
            f"once, as it records its event"
        )
    violation_statements = STUB_VIOLATION_STMT_RE.findall(joined)
    if len(violation_statements) != 1:
        raise TranslationError(
            f"{display} moves {len(violation_statements)} operand(s) into "
            f"HC-ORDER-VIOLATION-STMT; a capture stub names itself there "
            f"exactly once, when its prerequisite is missing"
        )
    return {
        "sequence_item": sequence_item.upper(),
        "ordinal_item": ordinal_item.upper(),
        "guard_line": code[start][0],
        "condition": condition,
        "items": sorted(set(CAPTURE_ORDINAL_ITEM_RE.findall(condition))),
        "read": sorted(set(CAPTURE_ORDINAL_ITEM_RE.findall(joined))),
        "last_statement": last_statements[0].upper(),
        "violation_statement": violation_statements[0].upper(),
    }


def _verify_stub_enforces(record: dict, guard: dict, expected_items: set,
                          sequence_item: str, display: str) -> None:
    """Assert one stub's guard enforces exactly the entry that names it."""
    if guard["ordinal_item"] != record["successor_ordinal_item"]:
        raise TranslationError(
            f"{display} stamps {guard['ordinal_item']}; execution_order entry "
            f"{record['id']} names it as the member that stamps "
            f"{record['successor_ordinal_item']}"
        )
    if guard["sequence_item"] != sequence_item.upper():
        raise TranslationError(
            f"{display} stamps its ordinal from {guard['sequence_item']}; "
            f"capture_ordinals.sequence_item is {sequence_item}"
        )
    if set(guard["items"]) != expected_items:
        raise TranslationError(
            f"{display}:{guard['guard_line']} guards on "
            f"{sorted(guard['items'])}; execution_order entry {record['id']} "
            f"declares the prerequisite ordinal(s) {sorted(expected_items)}"
        )
    literal = record["first_captured_ordinal"]
    for item in sorted(expected_items):
        if literal is None:
            pattern = re.compile(rf"\b{re.escape(item)}\s*=\s*ZERO\b", re.IGNORECASE)
            requirement = f"{item} = ZERO"
        else:
            pattern = re.compile(
                rf"\b{re.escape(item)}\s+NOT\s*=\s*{literal}\b", re.IGNORECASE
            )
            requirement = f"{item} NOT = {literal}"
        if pattern.search(guard["condition"]) is None:
            raise TranslationError(
                f"{display}:{guard['guard_line']} does not test {requirement}; "
                f"execution_order entry {record['id']} requires that test"
            )
    allowed = expected_items | {
        record["successor_ordinal_item"], sequence_item.upper()
    }
    stray = sorted(set(guard["read"]) - allowed)
    if stray:
        raise TranslationError(
            f"{display} names the ordinal item(s) {stray}; the entry "
            f"{record['id']} allows this member only {sorted(allowed)}"
        )
    if guard["violation_statement"] != guard["last_statement"]:
        raise TranslationError(
            f"{display} reports the violation under "
            f"{guard['violation_statement']} but records its event under "
            f"{guard['last_statement']}; a capture stub reports under the one "
            f"name it records"
        )


def verify_capture_order_contract(statement_map: dict, copybook_bytes: bytes,
                                  copybook_dir: Path) -> dict:
    """Reconcile the map's ordering metadata with the copybook, the stubs and
    the driver.

    Fails the run when an ordinal item the map names is not declared by
    ``hcapture.cpy`` or is declared there and accounted for nowhere in the map,
    when the prerequisite table of that copybook disagrees with the entry
    covering a member, when the ``enforced_by`` member of an entry does not
    stamp the successor ordinal from the shared sequence item, does not read
    exactly the prerequisite ordinals the entry declares, reads an ordinal the
    entry does not allow it, or reports a violation under a name other than the
    one it records its event under.  It then reconciles the order table
    modernization/harness/driver.cbl builds with the same metadata through
    ``verify_driver_order_agreement``, so the second, independent reading of the
    order is held to the map as well.  Returns the reconciliation for the
    report.
    """
    capture = statement_map["capture_ordinals"]
    resolution = statement_map["ordinal_resolution"]
    records = statement_map["order_records"]
    display = repo_relative(copybook_dir / CAPTURE_COPYBOOK)
    text = _decode_harness_text(copybook_bytes, display)

    sequence_item = str(capture["sequence_item"]).strip().upper()
    non_statement = tuple(
        str(item).strip().upper()
        for item in capture["non_statement_ordinal_items"]
    )
    declared = _declared_ordinal_items(
        text, str(capture["ordinal_pic"]).strip(), display
    )
    accounted = {sequence_item, *resolution.values(), *non_statement}
    undeclared = sorted(accounted - set(declared))
    if undeclared:
        raise TranslationError(
            f"the statement map names the ordinal item(s) {undeclared}, which "
            f"{display} does not declare"
        )
    unaccounted = sorted(set(declared) - accounted)
    if unaccounted:
        raise TranslationError(
            f"{display} declares the ordinal item(s) {unaccounted}, which the "
            f"statement map accounts for neither as a statement ordinal, the "
            f"shared sequence item nor a non-statement ordinal"
        )

    table = _declared_prerequisite_table(text, display)
    by_member = {}
    for record in records:
        member = Path(record["enforced_by"]).name
        if member in by_member:
            raise TranslationError(
                f"execution_order entries {by_member[member]['id']} and "
                f"{record['id']} both name {member} as the member that enforces "
                f"them; one member enforces one constraint"
            )
        by_member[member] = record
    missing_rows = sorted(set(by_member) - set(table))
    if missing_rows:
        raise TranslationError(
            f"the prerequisite table of {display} carries no row for "
            f"{missing_rows}, which the statement map names in enforced_by"
        )
    extra_rows = sorted(set(table) - set(by_member))
    if extra_rows:
        raise TranslationError(
            f"the prerequisite table of {display} carries a row for "
            f"{extra_rows}, which no execution_order entry names in enforced_by"
        )

    reconciled = []
    for member, record in sorted(by_member.items()):
        if record["predecessor_ordinal_item"] is None:
            expected_items = {record["successor_ordinal_item"]}
        else:
            expected_items = {
                record["predecessor_ordinal_item"],
                *record["predecessor_ordinal_items_any"],
            }
        row = table[member]
        if set(row["items"]) != expected_items:
            raise TranslationError(
                f"{display}:{row['line']} states that {member} reads "
                f"{sorted(row['items'])}; execution_order entry {record['id']} "
                f"declares the prerequisite ordinal(s) {sorted(expected_items)}"
            )
        if row["equal_to"] != record["first_captured_ordinal"]:
            raise TranslationError(
                f"{display}:{row['line']} states the ordinal value "
                f"{row['equal_to']!r} for {member}; execution_order entry "
                f"{record['id']} requires {record['first_captured_ordinal']!r}"
            )
        stub_display = repo_relative(EXPECTED_STUB_DIR / member)
        stub_text = _decode_harness_text(
            read_declared_capture_stub(
                record["enforced_by"],
                f"execution_order[{record['id']}].enforced_by",
            ),
            stub_display,
        )
        guard = _stub_order_guard(stub_text, stub_display)
        _verify_stub_enforces(
            record, guard, expected_items, sequence_item, stub_display
        )
        reconciled.append(
            {
                "entry": record["id"],
                "predecessor": record["predecessor"],
                "successor": record["successor"],
                "enforced_by": record["enforced_by"],
                "prerequisite_ordinal_items": sorted(expected_items),
                "successor_ordinal_item": record["successor_ordinal_item"],
                "first_captured_ordinal": record["first_captured_ordinal"],
                "guard_line": guard["guard_line"],
            }
        )
    driver_display = repo_relative(EXPECTED_DRIVER_SOURCE)
    driver_text = _decode_harness_text(read_driver_source(), driver_display)
    driver = verify_driver_order_agreement(
        driver_text, driver_display, resolution
    )
    return {
        "copybook": display,
        "sequence_item": sequence_item,
        "ordinal_items_declared": sorted(declared),
        "non_statement_ordinal_items": sorted(non_statement),
        "event_ordinals": {
            event: item for event, item in sorted(resolution.items())
        },
        "entries": reconciled,
        "driver_agreement": driver,
    }


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
            relative = f"src/{member.lower()}.cpy"
            candidate = build_tree.path_for(relative)
            if not build_tree.holds_regular_file(relative):
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
    """Render the source digests in ``sha256sum -c`` format.

    The first row is a ``#`` comment carrying the run disposition.
    ``sha256sum --check`` skips comment lines, so the rendered file still
    checks the five digest rows that follow it.
    """
    try:
        relative = source_dir.resolve().relative_to(REPO_ROOT)
    except ValueError:
        relative = source_dir.resolve()
    rows = [f"# status_label: {STATUS_LABEL_TEXT}"]
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
    order_metadata: dict,
    capture_order_contract: dict,
) -> dict:
    """Assemble the translation report.

    The per-program application lists and the per-rule totals account for
    every rewritten construct and for every source line carried through
    unchanged. That coverage is what
    ``modernization/docs/traceability-matrix.md``
    consumes.
    ``chain_link_contract`` publishes the nested link events - target program,
    COMMAREA operand and length per site - for the runner to cross-check.
    ``order_metadata`` publishes the validated ordering contract of the
    statement map: the ordinal item of every captured statement and, per
    constraint, its two sides, its enforcing stub and how many assertions it
    carries.  ``capture_order_contract`` publishes the same ordering metadata
    as reconciled with the capture copybook, the capture stubs and the driver:
    one record per execution_order entry, naming the member that enforces it,
    the prerequisite ordinals its guard reads and the line that guard stands
    on.
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
        "status_label": STATUS_LABEL_TEXT,
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
        "execution_order_contract": order_metadata,
        "capture_order_contract": capture_order_contract,
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
    statement_map = load_statement_map(statement_map_path, copybook_dir)
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
    capture_order_contract = verify_capture_order_contract(
        statement_map, copybook_bytes[CAPTURE_COPYBOOK], copybook_dir
    )

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
        order_metadata=statement_map["order_metadata"],
        capture_order_contract=capture_order_contract,
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
    """Render the one-block success summary written to standard output.

    The disposition of the run heads the block, so the log this output is
    retained in states it above its first generation record.
    """
    lines = [
        f"status_label: {STATUS_LABEL_TEXT}",
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
# Built-in case matrix
# --------------------------------------------------------------------------
# Status returned when a case of --self-test did not hold.  Every other status
# of this tool is unchanged: 0 on success and 1 on any generation failure.
EXIT_SELF_TEST_FAILED = 5


class _SelfTestFailure(Exception):
    """One case did not hold; the message states what the case observed."""


@dataclass(frozen=True)
class _CaseResult:
    """The outcome of one case, as its line and the summary report it."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class _SelfTestInputs:
    """The shipped inputs the matrix reads once and every case works from.

    ``document`` is the composed statement map before validation, ``contract``
    the validated one, ``results`` the translation of each authorized program
    and ``generated`` its generated lines.  Nothing here is written back.
    """

    document: dict
    contract: dict
    map_index: dict
    sources: dict
    baseline: dict
    copybooks: dict
    dfhresp_item: str
    results: dict
    generated: dict

    def dml_entry(self, entry_id: str) -> dict:
        """Return the validated dml entry carrying ``entry_id``."""
        for entry in self.contract["dml"]:
            if str(entry["id"]) == entry_id:
                return entry
        raise _SelfTestFailure(
            f"the statement map declares no dml entry {entry_id!r}; it declares "
            f"{[str(entry['id']) for entry in self.contract['dml']]}"
        )

    def include_entry(self, entry_id: str) -> dict:
        """Return the validated includes entry carrying ``entry_id``."""
        for entry in self.contract["includes"]:
            if str(entry["id"]) == entry_id:
                return entry
        raise _SelfTestFailure(
            f"the statement map declares no includes entry {entry_id!r}; it "
            f"declares "
            f"{[str(entry['id']) for entry in self.contract['includes']]}"
        )

    def source_lines(self, name: str) -> list:
        """Return the fixed-format lines of one authorized source."""
        return split_source_lines(self.sources[name].decode("ascii"))


def _self_test_inputs() -> _SelfTestInputs:
    """Read every shipped input the matrix works from, once.

    The five authorized sources, the four harness copybooks and the statement
    map are read through the guarded read path a generation run uses, and the
    three programs are translated in memory.  A failure here raises before any
    case runs, so no case is judged against inputs that did not load.
    """
    document = read_statement_map_document(EXPECTED_STATEMENT_MAP)
    contract = validate_statement_map_document(
        document, EXPECTED_STATEMENT_MAP, EXPECTED_COPYBOOK_DIR
    )
    map_index = index_statement_map(contract)
    sources = {
        name: read_authorized_source(EXPECTED_SOURCE_DIR, name)
        for name in sorted(SOURCE_ALLOW_LIST)
    }
    copybooks = {
        name: read_harness_copybook(EXPECTED_COPYBOOK_DIR, name)
        for name in HARNESS_COPYBOOKS
    }
    dfhresp_item = discover_level_01_item("dfhresp.cpy", copybooks["dfhresp.cpy"])
    results = {}
    for name in PROGRAM_SOURCES:
        results[name] = ProgramTranslator(
            name=name,
            text=sources[name].decode("ascii"),
            statement_map=contract,
            map_index=map_index,
            dfhresp_item=dfhresp_item,
        ).translate()
    return _SelfTestInputs(
        document=document,
        contract=contract,
        map_index=map_index,
        sources=sources,
        baseline={name: sha256_of_bytes(data) for name, data in sources.items()},
        copybooks=copybooks,
        dfhresp_item=dfhresp_item,
        results=results,
        generated={
            name: list(result.generated_lines)
            for name, result in results.items()
        },
    )


# --------------------------------------------------------------------------
# Case helpers
# --------------------------------------------------------------------------
def _observed(condition, message: str) -> None:
    """Raise ``_SelfTestFailure`` with ``message`` unless ``condition`` holds."""
    if not condition:
        raise _SelfTestFailure(message)


def _refused(what: str, body, *expected: str) -> str:
    """Run ``body``, requiring it to raise and to name every ``expected`` text.

    Returns the one-line diagnostic the refusal carried, which the case reports
    as what it observed.  A body that returns instead of raising fails the case,
    and so does a refusal whose message misses one of the expected texts: that
    means the guard fired for a reason other than the one the fixture
    contradicts.
    """
    try:
        body()
    except TranslationError as error:
        message = one_line(error, limit=600)
        for fragment in expected:
            if fragment not in message:
                raise _SelfTestFailure(
                    f"{what} was refused, but the diagnostic does not carry "
                    f"{fragment!r}: {message}"
                ) from None
        return message
    raise _SelfTestFailure(f"{what} was accepted; this fixture must be refused")


def _fixed_line(indent: int, text: str) -> str:
    """Return one fixed-format line holding ``text`` from column ``indent``+1."""
    line = " " * indent + text
    if len(line) > MAX_LINE_LENGTH:
        raise _SelfTestFailure(
            f"the fixture line {line!r} reaches column {len(line)}, past column "
            f"{MAX_LINE_LENGTH}"
        )
    return line


def _translated_fragment(inputs: _SelfTestInputs, name: str, lines: list):
    """Apply the rule table to one synthetic fragment attributed to ``name``.

    The fragment is a list of fixed-format lines and is translated by exactly
    the rules a whole program goes through; only the pinned census of ``name``
    is left out, so a fragment of any length can be held to one rule.
    """
    return ProgramTranslator(
        name=name,
        text="\n".join(lines) + "\n",
        statement_map=inputs.contract,
        map_index=inputs.map_index,
        dfhresp_item=inputs.dfhresp_item,
    ).apply_rules()


def _rules_of(result) -> list:
    """Return the rule ids the applications of ``result`` carry, in order."""
    return [application.rule_id for application in result.applications]


def _statements_of(result) -> list:
    """Return the code-area text of every generated non-comment line."""
    return [
        code_of(line).strip()
        for line in result.generated_lines
        if line.strip() and not is_comment_line(line)
    ]


def _mutated_document(inputs: _SelfTestInputs, mutate) -> dict:
    """Return a copy of the shipped map document with ``mutate`` applied to it.

    ``mutate`` receives the copy and changes one member of it; the document the
    matrix read is never handed to it.
    """
    candidate = copy.deepcopy(inputs.document)
    mutate(candidate)
    return candidate


def _validated(document: dict) -> dict:
    """Validate one statement-map document under the shipped map's identity."""
    return validate_statement_map_document(
        document, EXPECTED_STATEMENT_MAP, EXPECTED_COPYBOOK_DIR
    )


# --------------------------------------------------------------------------
# Synthetic fixed-format fixtures
# --------------------------------------------------------------------------
# Column the fixture statements start in, and the column their operand
# continuation lines start in.  Both sit inside the code area every generated
# line is held to.
_FIXTURE_INDENT = AREA_B_INDENT
_FIXTURE_OPERAND_INDENT = AREA_B_INDENT + 6

# The item names the fixtures use for the areas, keys and response fields the
# rewritten constructs name.  They stand for source items and are never read
# from a source.
_FIXTURE_LINK_ITEM = "WS-LINK-PROGRAM"
_FIXTURE_DIAG_AREA = "WS-ERROR-MESSAGE"
_FIXTURE_RECORD_ITEM = "WS-POLICY-RECORD"
_FIXTURE_KEY_ITEM = "WS-POLICY-KEY"
_FIXTURE_RESP_ITEM = "WS-WRITE-RESPONSE"
_FIXTURE_ABSTIME_ITEM = "WS-ABSTIME"
_FIXTURE_DATE_ITEM = "WS-DATE"
_FIXTURE_TIME_ITEM = "WS-TIME"


def _chain_link_fragment(
    target: str = "LGAPDB01",
    length: str = str(CHAIN_LINK_LENGTH),
    commarea: str = CHAIN_LINK_COMMAREA,
) -> list:
    """Return a fragment declaring a chain LINK and the item it names.

    The PROGRAM operand names a data item whose VALUE clause carries ``target``,
    which is the form both chain sites of the source use.
    """
    return [
        _fixed_line(
            AREA_A_INDENT,
            f"01  {_FIXTURE_LINK_ITEM}  PIC X(8) VALUE '{target}'.",
        ),
        _fixed_line(
            _FIXTURE_INDENT, f"EXEC CICS LINK PROGRAM({_FIXTURE_LINK_ITEM})"
        ),
        _fixed_line(_FIXTURE_OPERAND_INDENT, f"COMMAREA({commarea})"),
        _fixed_line(_FIXTURE_OPERAND_INDENT, f"LENGTH({length}) END-EXEC"),
    ]


def _diagnostic_link_fragment(
    program: str = DIAGNOSTIC_LINK_PROGRAM,
    length: str = f"LENGTH OF {_FIXTURE_DIAG_AREA}",
) -> list:
    """Return a fragment carrying one diagnostic LINK to a literal program."""
    return [
        _fixed_line(_FIXTURE_INDENT, f"EXEC CICS LINK PROGRAM('{program}')"),
        _fixed_line(
            _FIXTURE_OPERAND_INDENT, f"COMMAREA({_FIXTURE_DIAG_AREA})"
        ),
        _fixed_line(_FIXTURE_OPERAND_INDENT, f"LENGTH({length}) END-EXEC"),
    ]


def _write_fragment(
    file_name: str = WRITE_FILE_NAME,
    record_length: str = str(WRITE_RECORD_LENGTH).zfill(5),
    key_length: str = str(WRITE_KEY_LENGTH).zfill(5),
    from_item: str = _FIXTURE_RECORD_ITEM,
) -> list:
    """Return a fragment carrying one KSDSPOLY write with all six operands."""
    return [
        _fixed_line(_FIXTURE_INDENT, f"EXEC CICS WRITE FILE('{file_name}')"),
        _fixed_line(_FIXTURE_OPERAND_INDENT, f"FROM({from_item})"),
        _fixed_line(_FIXTURE_OPERAND_INDENT, f"LENGTH({record_length})"),
        _fixed_line(_FIXTURE_OPERAND_INDENT, f"RIDFLD({_FIXTURE_KEY_ITEM})"),
        _fixed_line(_FIXTURE_OPERAND_INDENT, f"KEYLENGTH({key_length})"),
        _fixed_line(
            _FIXTURE_OPERAND_INDENT, f"RESP({_FIXTURE_RESP_ITEM}) END-EXEC"
        ),
    ]


def _mapped_block_fragment(
    inputs: _SelfTestInputs,
    entry: dict,
    *,
    shift: int = 0,
    extra: str | None = None,
    replace: tuple | None = None,
) -> list:
    """Return a fragment holding one mapped source block at its mapped lines.

    The block's own source lines are taken from the authorized program the map
    describes and are preceded by as many blank lines as it takes for the block
    to open on the line the map declares for it.  ``shift`` moves the block that
    many lines further down, ``extra`` inserts one line ahead of its
    ``END-EXEC`` and ``replace`` rewrites one text of every line of it.
    """
    name = inputs.contract["declared_program"]
    lines = inputs.source_lines(name)
    start = int(entry["start_line"])
    end = int(entry["end_line"])
    block = list(lines[start - 1:end])
    if replace is not None:
        block = [line.replace(replace[0], replace[1]) for line in block]
    if extra is not None:
        block = block[:-1] + [extra] + block[-1:]
    return [""] * (start - 1 + shift) + block


# --------------------------------------------------------------------------
# Cases: the shipped inputs pass every guard
# --------------------------------------------------------------------------
def _case_statement_map_accepted(inputs: _SelfTestInputs) -> str:
    """The shipped statement map validates and indexes without a change."""
    contract = inputs.contract
    _observed(
        len(contract["includes"]) == EXPECTED_MAP_INCLUDE_COUNT
        and len(contract["dml"]) == EXPECTED_MAP_DML_COUNT,
        f"the shipped map holds {len(contract['includes'])} includes and "
        f"{len(contract['dml'])} dml entries; "
        f"{EXPECTED_MAP_INCLUDE_COUNT} and {EXPECTED_MAP_DML_COUNT} are "
        f"required",
    )
    checks = contract["checks"]
    _observed(
        checks["total_blocks"] == EXPECTED_MAP_TOTAL_BLOCKS,
        f"checks.total_blocks is {checks['total_blocks']}, expected "
        f"{EXPECTED_MAP_TOTAL_BLOCKS}",
    )
    _observed(
        len(inputs.map_index) == EXPECTED_MAP_TOTAL_BLOCKS,
        f"the index holds {len(inputs.map_index)} start line(s); "
        f"{EXPECTED_MAP_TOTAL_BLOCKS} blocks are declared",
    )
    return (
        f"{len(contract['includes'])} include(s), {len(contract['dml'])} dml "
        f"entry/entries, {len(inputs.map_index)} indexed start line(s), "
        f"declared program {contract['declared_program']}"
    )


def _case_order_metadata_accepted(inputs: _SelfTestInputs) -> str:
    """The shipped ordering metadata resolves every ordinal it declares."""
    metadata = inputs.contract["order_metadata"]
    _observed(
        metadata["declared_constraints"] == EXPECTED_MAP_ORDER_CONSTRAINT_COUNT
        and metadata["validated_constraints"]
        == EXPECTED_MAP_ORDER_CONSTRAINT_COUNT,
        f"the map declares {metadata['declared_constraints']} order "
        f"constraint(s) and validated "
        f"{metadata['validated_constraints']}; "
        f"{EXPECTED_MAP_ORDER_CONSTRAINT_COUNT} are required",
    )
    resolution = inputs.contract["ordinal_resolution"]
    _observed(
        len(resolution) == len(inputs.contract["dml"]) + 1,
        f"the ordinal resolution covers {len(resolution)} event(s); one per "
        f"dml entry plus the VSAM write is "
        f"{len(inputs.contract['dml']) + 1}",
    )
    return (
        f"{metadata['validated_constraints']} order constraint(s) validated, "
        f"{len(resolution)} event ordinal(s) resolved, sequence item "
        f"{metadata['sequence_item']}"
    )


def _case_pinned_digests_accepted(inputs: _SelfTestInputs) -> str:
    """Every authorized source read carries the digest pinned for its name."""
    for name, digest in sorted(inputs.baseline.items()):
        expected = AUTHORIZED_SOURCE_DIGESTS[name]
        _observed(
            digest == expected,
            f"{name} read as {digest}, pinned as {expected}",
        )
        require_authorized_source_digest(name, inputs.sources[name])
    _observed(
        len(inputs.baseline) == len(AUTHORIZED_SOURCE_DIGESTS),
        f"{len(inputs.baseline)} source(s) were read; "
        f"{len(AUTHORIZED_SOURCE_DIGESTS)} carry a pinned digest",
    )
    return (
        f"{len(inputs.baseline)} source(s) carry their pinned digest: "
        + ", ".join(sorted(inputs.baseline))
    )


def _case_harness_copybooks_accepted(inputs: _SelfTestInputs) -> str:
    """The four harness copybooks read, and dfhresp.cpy names one item."""
    sizes = {
        name: len(data) for name, data in sorted(inputs.copybooks.items())
    }
    _observed(
        set(sizes) == set(HARNESS_COPYBOOKS),
        f"the copybooks read are {sorted(sizes)}; "
        f"{sorted(HARNESS_COPYBOOKS)} are required",
    )
    _observed(
        all(size > 0 for size in sizes.values()),
        f"a harness copybook read as empty: {sizes}",
    )
    _observed(
        inputs.dfhresp_item == "DFHRESP-NORMAL",
        f"dfhresp.cpy declares {inputs.dfhresp_item!r}; the response-condition "
        f"item the rule substitutes is 'DFHRESP-NORMAL'",
    )
    return (
        f"{len(sizes)} copybook(s) read ("
        + ", ".join(f"{name}={size}B" for name, size in sizes.items())
        + f"); response-condition item {inputs.dfhresp_item}"
    )


def _case_shipped_programs_translate(inputs: _SelfTestInputs) -> str:
    """Each authorized program translates and meets its pinned census."""
    reported = []
    for name in PROGRAM_SOURCES:
        result = inputs.results[name]
        census = EXPECTED_SOURCE_CENSUS[name]
        _observed(
            result.source_line_count == census["lines"]
            and result.exec_cics_sites == census["exec_cics"]
            and result.exec_sql_blocks == census["exec_sql"],
            f"{name} measured {result.source_line_count} line(s), "
            f"{result.exec_cics_sites} EXEC CICS site(s) and "
            f"{result.exec_sql_blocks} EXEC SQL block(s) against the census "
            f"{census}",
        )
        reported.append(
            f"{name} {result.source_line_count}L/"
            f"{result.exec_cics_sites}C/{result.exec_sql_blocks}S"
        )
    return "; ".join(reported)


def _case_shipped_lines_within_columns(inputs: _SelfTestInputs) -> str:
    """Every generated line of every program holds the fixed-format rule."""
    widest = 0
    total = 0
    for name, lines in sorted(inputs.generated.items()):
        verify_generated_lines(name, lines)
        total += len(lines)
        widest = max(widest, max((len(line) for line in lines), default=0))
    _observed(
        widest <= MAX_LINE_LENGTH,
        f"a generated line reaches column {widest}, past column "
        f"{MAX_LINE_LENGTH}",
    )
    return (
        f"{total} generated line(s) across {len(inputs.generated)} program(s) "
        f"stay inside columns {CODE_START + 1}-{MAX_LINE_LENGTH}; widest is "
        f"column {widest}"
    )


def _case_shipped_tokens_accounted(inputs: _SelfTestInputs) -> str:
    """No untranslated construct survives, and the one comment is accounted."""
    accounted = {}
    for name in PROGRAM_SOURCES:
        result = inputs.results[name]
        for label, numbers in verify_no_forbidden_tokens(
            name, result.generated_lines, result.rule_comment_lines
        ).items():
            accounted.setdefault(label, []).extend(
                f"{name}:{number}" for number in numbers
            )
    _observed(
        sorted(accounted) == ["PROCESS SQL"],
        f"the accounted-for comment occurrences are {sorted(accounted)}; only "
        f"the commented PROCESS directive is expected",
    )
    return (
        "no active EXEC CICS, EXEC SQL, END-EXEC, DFHRESP( or PROCESS SQL "
        f"token survives; accounted comment(s): {accounted}"
    )


def _case_shipped_carry_through(inputs: _SelfTestInputs) -> str:
    """Every source line no rule claimed reaches the copy unchanged."""
    carried = []
    for name in PROGRAM_SOURCES:
        result = inputs.results[name]
        verify_carry_through(result, inputs.source_lines(name))
        carried.append(f"{name}={result.unchanged_source_lines}")
    return "line(s) copied unchanged: " + ", ".join(carried)


def _case_shipped_structural_counts(inputs: _SelfTestInputs) -> str:
    """The generated tree holds every mandated construct exactly as declared."""
    observed = verify_structural_counts(inputs.generated)
    _observed(
        observed == EXPECTED_STRUCTURAL_COUNTS,
        f"the generated tree holds {observed}; "
        f"{EXPECTED_STRUCTURAL_COUNTS} is required",
    )
    return ", ".join(
        f"{label}={count}" for label, count in sorted(observed.items())
    )


def _case_shipped_rule_totals(inputs: _SelfTestInputs) -> str:
    """Every rule was applied exactly as many times as it is expected to be."""
    totals = verify_rule_totals([inputs.results[name] for name in PROGRAM_SOURCES])
    _observed(
        totals["per_rule"] == EXPECTED_RULE_SITES,
        f"the per-rule totals are {totals['per_rule']}; "
        f"{EXPECTED_RULE_SITES} is required",
    )
    return (
        ", ".join(
            f"{rule}={totals['per_rule'][rule]}" for rule in EXPECTED_RULE_SITES
        )
        + f"; {totals['exec_cics_sites']} EXEC CICS site(s), "
        f"{totals['exec_sql_blocks']} EXEC SQL block(s)"
    )


def _case_shipped_chain_links(inputs: _SelfTestInputs) -> str:
    """Both chain LINK sites carry their target, COMMAREA and 32500 length."""
    contract = verify_chain_link_contract(
        [inputs.results[name] for name in PROGRAM_SOURCES]
    )
    _observed(
        len(contract["sites"]) == len(CHAIN_LINK_TARGETS),
        f"{len(contract['sites'])} chain link site(s) were recorded; "
        f"{len(CHAIN_LINK_TARGETS)} are required",
    )
    for site in contract["sites"]:
        _observed(
            site["length"] == CHAIN_LINK_LENGTH
            and site["commarea_operand"] == CHAIN_LINK_COMMAREA,
            f"{site['program']}:{site['locator']} links with LENGTH "
            f"{site['length']} and COMMAREA {site['commarea_operand']}",
        )
    return "; ".join(
        f"{site['program']}:{site['locator']} -> {site['target_program']} "
        f"LENGTH {site['length']}"
        for site in contract["sites"]
    )


def _case_shipped_declared_census(inputs: _SelfTestInputs) -> str:
    """The census the map declares equals the figures measured this run."""
    verify_declared_source_census(
        inputs.contract, [inputs.results[name] for name in PROGRAM_SOURCES]
    )
    declared = inputs.contract["source_program"]
    return (
        f"{inputs.contract['declared_program']}: "
        f"{declared['total_lines']} line(s), "
        f"{declared['exec_cics_blocks']} EXEC CICS block(s), "
        f"{declared['exec_sql_blocks']} EXEC SQL block(s), longest line "
        f"{declared['max_line_length']}"
    )


def _case_shipped_capture_order_contract(inputs: _SelfTestInputs) -> str:
    """The map, the capture copybook, the stubs and the driver state one order."""
    reconciled = verify_capture_order_contract(
        inputs.contract, inputs.copybooks[CAPTURE_COPYBOOK], EXPECTED_COPYBOOK_DIR
    )
    _observed(
        len(reconciled["entries"]) == EXPECTED_MAP_ORDER_CONSTRAINT_COUNT,
        f"{len(reconciled['entries'])} order constraint(s) were reconciled; "
        f"{EXPECTED_MAP_ORDER_CONSTRAINT_COUNT} are declared",
    )
    return (
        f"{len(reconciled['entries'])} constraint(s) reconciled across "
        f"{len(reconciled['ordinal_items_declared'])} declared ordinal item(s); "
        f"driver order events "
        f"{len(reconciled['driver_agreement']['order_table_events'])}"
    )


def _case_shipped_sources_unchanged(inputs: _SelfTestInputs) -> str:
    """Re-reading every authorized source yields the digest of the first read."""
    verify_sources_unchanged(EXPECTED_SOURCE_DIR, inputs.baseline)
    return (
        f"{len(inputs.baseline)} source(s) re-read at the same digest from "
        f"{repo_relative(EXPECTED_SOURCE_DIR)}"
    )


def _case_build_root_accepted() -> str:
    """The build tree of this checkout is accepted as the one write root."""
    tree = BuildTree(CANONICAL_BUILD_ROOT)
    _observed(
        tree.root == CANONICAL_BUILD_ROOT,
        f"the build tree resolved to {tree.root}, not {CANONICAL_BUILD_ROOT}",
    )
    report = tree.path_for(REPORT_RELATIVE)
    _observed(
        tree.root in report.parents,
        f"{report} does not stand inside {tree.root}",
    )
    return (
        f"build root {repo_relative(tree.root)} accepted; report path "
        f"{repo_relative(report)} stands inside it"
    )


# --------------------------------------------------------------------------
# Cases: the rewrite rules on synthetic fixed-format fragments
# --------------------------------------------------------------------------
def _case_r1_directive_commented(inputs: _SelfTestInputs) -> str:
    """R1 turns the compiler directive into a comment line of the copy."""
    source = _fixed_line(AREA_A_INDENT, "PROCESS SQL(DB2),APOST")
    result = _translated_fragment(inputs, "lgapdb01.cbl", [source])
    _observed(
        _rules_of(result) == ["R1"],
        f"the fragment applied {_rules_of(result)}; ['R1'] is expected",
    )
    generated = result.generated_lines
    _observed(
        len(generated) == 1 and is_comment_line(generated[0]),
        f"R1 emitted {generated!r}; one comment line is expected",
    )
    _observed(
        R1_NOTE in generated[0] and "PROCESS SQL(DB2),APOST" in generated[0],
        f"the commented directive is {generated[0]!r}; it must carry the "
        f"directive text and {R1_NOTE!r}",
    )
    accounted = verify_no_forbidden_tokens(
        "lgapdb01.cbl", generated, result.rule_comment_lines
    )
    _observed(
        accounted.get("PROCESS SQL") == [1],
        f"the comment accounting is {accounted}; the directive must be "
        f"accounted for at line 1",
    )
    return f"emitted {generated[0].strip()!r} and accounted for it as a comment"


def _case_r1_active_directive_refused(inputs: _SelfTestInputs) -> str:
    """An uncommented directive line is refused as a surviving construct."""
    source = _fixed_line(AREA_A_INDENT, "PROCESS SQL(DB2),APOST")
    message = _refused(
        "a generated line still carrying the PROCESS directive",
        lambda: verify_no_forbidden_tokens("lgapdb01.cbl", [source], set()),
        "lgapdb01.cbl:1 still carries the active construct 'PROCESS SQL'",
    )
    return message


def _case_r2_include_replaced(inputs: _SelfTestInputs) -> str:
    """R2 replaces the mapped EXEC SQL INCLUDE with the declared COPY."""
    entry = inputs.include_entry("include_lgcmarea")
    lines = inputs.source_lines(inputs.contract["declared_program"])
    start = int(entry["start_line"])
    fragment = [""] * (start - 2) + [lines[start - 2]] + list(
        lines[start - 1:int(entry["end_line"])]
    )
    result = _translated_fragment(inputs, "lgapdb01.cbl", fragment)
    statements = _statements_of(result)
    replacement = str(entry["replacement"]).strip()
    _observed(
        _rules_of(result) == ["R2"] and replacement in statements,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; one R2 site emitting {replacement!r} is expected",
    )
    return (
        f"entry {entry['id']} at lines {entry['start_line']}-"
        f"{entry['end_line']} generated {replacement!r} beneath "
        f"{str(entry['enclosing_group']).strip()!r}"
    )


def _case_r13_call_emitted(inputs: _SelfTestInputs) -> str:
    """R13 replaces the mapped DML block with the CALL its contract declares."""
    entry = inputs.dml_entry("select_lastchanged")
    result = _translated_fragment(
        inputs, "lgapdb01.cbl", _mapped_block_fragment(inputs, entry)
    )
    statements = _statements_of(result)
    hosts = [str(item["host"]) for item in entry["using"]]
    expected = [f"CALL '{entry['call_program']}' USING", *hosts, "END-CALL."]
    _observed(
        _rules_of(result) == ["R13"] and statements == expected,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; {expected} is expected",
    )
    contract = result.applications[0].details["sql_contract"]
    _observed(
        contract["sql_verb"] == str(entry["sql_verb"]).upper(),
        f"the enforced contract records verb {contract['sql_verb']!r}; the map "
        f"declares {entry['sql_verb']!r}",
    )
    return (
        f"entry {entry['id']} at lines {entry['start_line']}-"
        f"{entry['end_line']} generated a {len(hosts)}-host CALL to "
        f"{entry['call_program']}, {contract['sql_verb']} contract enforced"
    )


def _case_r14_lines_carried(inputs: _SelfTestInputs) -> str:
    """R14 copies a line no rule claims into the copy byte-for-byte."""
    fragment = [
        _fixed_line(AREA_A_INDENT, "MOVE '00' TO CA-RETURN-CODE."),
        "      *    a comment line of the source",
        "",
        _fixed_line(_FIXTURE_INDENT, "PERFORM WRITE-ERROR-MESSAGE"),
    ]
    result = _translated_fragment(inputs, "lgapol01.cbl", fragment)
    _observed(
        _rules_of(result) == [],
        f"the fragment applied {_rules_of(result)}; no rule site is expected",
    )
    _observed(
        result.generated_lines == fragment,
        f"the copy holds {result.generated_lines!r}; the source lines "
        f"{fragment!r} are expected byte-for-byte",
    )
    verify_carry_through(result, fragment)
    return (
        f"{len(fragment)} unclaimed line(s), including a comment and a blank "
        f"line, reached the copy unchanged"
    )


def _case_r3_binding_emitted(inputs: _SelfTestInputs) -> str:
    """R3 binds the shared COMMAREA to the procedure division header."""
    result = _translated_fragment(
        inputs,
        "lgapol01.cbl",
        [_fixed_line(AREA_A_INDENT, "PROCEDURE DIVISION.")],
    )
    statements = _statements_of(result)
    _observed(
        _rules_of(result) == ["R3"]
        and statements == ["PROCEDURE DIVISION USING DFHCOMMAREA."],
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; one R3 site binding DFHCOMMAREA is expected",
    )
    return f"generated {statements[0]!r}"


def _case_r3_missing_binding_refused(inputs: _SelfTestInputs) -> str:
    """A generated tree missing one procedure-division binding is refused."""
    mutated = {
        name: list(lines) for name, lines in inputs.generated.items()
    }
    program = "lgapol01.cbl"
    replaced = None
    for index, line in enumerate(mutated[program]):
        if STRUCTURAL_PATTERNS[_R3_STRUCTURAL_LABEL].match(code_of(line)):
            mutated[program][index] = _fixed_line(
                AREA_A_INDENT, "PROCEDURE DIVISION."
            )
            replaced = index + 1
            break
    _observed(
        replaced is not None,
        f"{program} carries no generated procedure-division binding to mutate",
    )
    message = _refused(
        f"a generated tree whose {program} binding was removed",
        lambda: verify_structural_counts(mutated),
        repr(_R3_STRUCTURAL_LABEL),
        f"expected "
        f"{EXPECTED_STRUCTURAL_COUNTS[_R3_STRUCTURAL_LABEL]}",
    )
    return f"{program}:{replaced} unbound -> {message}"


def _case_r4_declarations_inserted(inputs: _SelfTestInputs) -> str:
    """R4 inserts the harness declarations after the anchor it keeps."""
    anchor = _fixed_line(AREA_A_INDENT, "WORKING-STORAGE SECTION.")
    plain = _translated_fragment(inputs, "lgapol01.cbl", [anchor])
    witness = _translated_fragment(inputs, R4_DFHRESP_PROGRAM, [anchor])
    plain_statements = _statements_of(plain)
    witness_statements = _statements_of(witness)
    _observed(
        plain_statements
        == ["WORKING-STORAGE SECTION.", *R4_DECLARATIONS],
        f"the anchor of lgapol01.cbl generated {plain_statements}; the anchor "
        f"followed by {list(R4_DECLARATIONS)} is expected",
    )
    _observed(
        witness_statements
        == [
            "WORKING-STORAGE SECTION.",
            *R4_DECLARATIONS,
            R4_DFHRESP_DECLARATION,
        ],
        f"the anchor of {R4_DFHRESP_PROGRAM} generated {witness_statements}; "
        f"{R4_DFHRESP_DECLARATION!r} must follow the shared declarations",
    )
    _observed(
        plain.applications[0].source_text == anchor,
        f"the R4 site recorded {plain.applications[0].source_text!r} as its "
        f"source; the anchor line {anchor!r} is expected",
    )
    return (
        f"{len(R4_DECLARATIONS)} declaration(s) inserted after the anchor, "
        f"and {R4_DFHRESP_DECLARATION!r} only in {R4_DFHRESP_PROGRAM}"
    )


def _case_r5_chain_link_rewritten(inputs: _SelfTestInputs) -> str:
    """R5 carries the declared length into EIBCALEN and calls dynamically."""
    result = _translated_fragment(
        inputs, "lgapol01.cbl", _chain_link_fragment()
    )
    statements = _statements_of(result)
    expected = [
        f"01  {_FIXTURE_LINK_ITEM}  PIC X(8) VALUE 'LGAPDB01'.",
        f"MOVE {CHAIN_LINK_LENGTH} TO EIBCALEN",
        f"CALL {_FIXTURE_LINK_ITEM} USING {CHAIN_LINK_COMMAREA}",
    ]
    _observed(
        _rules_of(result) == ["R5"] and statements == expected,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; {expected} is expected",
    )
    site = result.chain_links[0]
    _observed(
        site["length"] == CHAIN_LINK_LENGTH
        and site["target_program"] == "LGAPDB01"
        and site["commarea_operand"] == CHAIN_LINK_COMMAREA,
        f"the recorded site is {site}",
    )
    return (
        f"LENGTH {site['length']} reached EIBCALEN and the dynamic CALL passes "
        f"{site['commarea_operand']} to {site['target_program']}"
    )


def _case_r6_diagnostic_link_rewritten(inputs: _SelfTestInputs) -> str:
    """R6 passes the diagnostic area and its length to the harness stub."""
    result = _translated_fragment(
        inputs, "lgapol01.cbl", _diagnostic_link_fragment()
    )
    statements = _statements_of(result)
    expected = [
        f"MOVE LENGTH OF {_FIXTURE_DIAG_AREA} TO {HARNESS_DIAG_LEN_ITEM}",
        f"CALL '{STUB_DIAG_LINK}' USING {_FIXTURE_DIAG_AREA} "
        f"{HARNESS_DIAG_LEN_ITEM}",
    ]
    _observed(
        _rules_of(result) == ["R6"] and statements == expected,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; {expected} is expected",
    )
    return f"generated a call to {STUB_DIAG_LINK} with the area and its length"


def _case_r7_return_becomes_goback(inputs: _SelfTestInputs) -> str:
    """R7 rewrites the CICS return to GOBACK, keeping the source's period."""
    with_period = _translated_fragment(
        inputs,
        "lgapol01.cbl",
        [_fixed_line(_FIXTURE_INDENT, "EXEC CICS RETURN END-EXEC.")],
    )
    without_period = _translated_fragment(
        inputs,
        "lgapol01.cbl",
        [_fixed_line(_FIXTURE_INDENT, "EXEC CICS RETURN END-EXEC")],
    )
    expected_period = ["GOBACK."]
    expected_plain = ["GOBACK"]
    _observed(
        _statements_of(with_period) == expected_period
        and _statements_of(without_period) == expected_plain,
        f"the two returns generated {_statements_of(with_period)} and "
        f"{_statements_of(without_period)}; {expected_period} and "
        f"{expected_plain} are expected",
    )
    _observed(
        _rules_of(with_period) == ["R7"] and with_period.exec_cics_sites == 1,
        f"the fragment applied {_rules_of(with_period)} over "
        f"{with_period.exec_cics_sites} EXEC CICS site(s)",
    )
    return "generated 'GOBACK.' and 'GOBACK' from the two source forms"


def _case_r8_abend_captured(inputs: _SelfTestInputs) -> str:
    """R8 captures the abend code, calls the stub and returns to the caller."""
    result = _translated_fragment(
        inputs,
        "lgapvs01.cbl",
        [
            _fixed_line(
                _FIXTURE_INDENT, "EXEC CICS ABEND ABCODE('LGCA') NODUMP END-EXEC"
            )
        ],
    )
    statements = _statements_of(result)
    expected = [
        f"MOVE 'LGCA' TO {HARNESS_ABEND_ITEM}",
        f"CALL '{STUB_ABEND}' USING {HARNESS_ABEND_ITEM}",
        "GOBACK",
    ]
    _observed(
        _rules_of(result) == ["R8"] and statements == expected,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; {expected} is expected",
    )
    return f"captured abend 'LGCA' through {STUB_ABEND}, then GOBACK"


def _case_r9_write_reaches_capture(inputs: _SelfTestInputs) -> str:
    """R9 passes all six write operands to the capture module in order."""
    result = _translated_fragment(inputs, "lgapvs01.cbl", _write_fragment())
    statements = _statements_of(result)
    expected = [
        f"CALL '{STUB_WRITE}' USING",
        f"'{WRITE_FILE_NAME}'",
        _FIXTURE_RECORD_ITEM,
        f"'{str(WRITE_RECORD_LENGTH).zfill(WRITE_LENGTH_LITERAL_DIGITS)}'",
        _FIXTURE_KEY_ITEM,
        f"'{str(WRITE_KEY_LENGTH).zfill(WRITE_LENGTH_LITERAL_DIGITS)}'",
        _FIXTURE_RESP_ITEM,
        "END-CALL",
    ]
    _observed(
        _rules_of(result) == ["R9"] and statements == expected,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; {expected} is expected",
    )
    recorded = result.applications[0].details["file_write"]
    _observed(
        recorded["record_length"] == WRITE_RECORD_LENGTH
        and recorded["key_length"] == WRITE_KEY_LENGTH,
        f"the recorded write contract is {recorded}",
    )
    return (
        f"six operand(s) reached {STUB_WRITE}: {WRITE_FILE_NAME}, record "
        f"length {recorded['record_length']}, key length "
        f"{recorded['key_length']}"
    )


def _case_r10_asktime_rewritten(inputs: _SelfTestInputs) -> str:
    """R10 rewrites the clock read to the deterministic harness stub."""
    result = _translated_fragment(
        inputs,
        "lgapol01.cbl",
        [
            _fixed_line(
                _FIXTURE_INDENT,
                f"EXEC CICS ASKTIME ABSTIME({_FIXTURE_ABSTIME_ITEM}) END-EXEC",
            )
        ],
    )
    statements = _statements_of(result)
    expected = [f"CALL '{STUB_ASKTIME}' USING {_FIXTURE_ABSTIME_ITEM}"]
    _observed(
        _rules_of(result) == ["R10"] and statements == expected,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; {expected} is expected",
    )
    return f"generated {statements[0]!r}"


def _case_r11_formattime_rewritten(inputs: _SelfTestInputs) -> str:
    """R11 passes all three time operands to the deterministic harness stub."""
    result = _translated_fragment(
        inputs,
        "lgapol01.cbl",
        [
            _fixed_line(
                _FIXTURE_INDENT,
                f"EXEC CICS FORMATTIME ABSTIME({_FIXTURE_ABSTIME_ITEM})",
            ),
            _fixed_line(
                _FIXTURE_OPERAND_INDENT, f"MMDDYYYY({_FIXTURE_DATE_ITEM})"
            ),
            _fixed_line(
                _FIXTURE_OPERAND_INDENT,
                f"TIME({_FIXTURE_TIME_ITEM}) END-EXEC",
            ),
        ],
    )
    statements = _statements_of(result)
    expected = [
        f"CALL '{STUB_FORMATTIME}' USING {_FIXTURE_ABSTIME_ITEM} "
        f"{_FIXTURE_DATE_ITEM} {_FIXTURE_TIME_ITEM}"
    ]
    _observed(
        _rules_of(result) == ["R11"] and statements == expected,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; {expected} is expected",
    )
    return f"generated {statements[0]!r}"


def _case_r12_condition_substituted(inputs: _SelfTestInputs) -> str:
    """R12 replaces the response macro with the copybook's named constant."""
    source = _fixed_line(
        _FIXTURE_INDENT, f"IF {_FIXTURE_RESP_ITEM} NOT = DFHRESP(NORMAL)"
    )
    result = _translated_fragment(inputs, "lgapvs01.cbl", [source])
    statements = _statements_of(result)
    expected = [f"IF {_FIXTURE_RESP_ITEM} NOT = {inputs.dfhresp_item}"]
    _observed(
        _rules_of(result) == ["R12"] and statements == expected,
        f"the fragment applied {_rules_of(result)} and generated "
        f"{statements}; {expected} is expected",
    )
    verify_no_forbidden_tokens(
        "lgapvs01.cbl", result.generated_lines, result.rule_comment_lines
    )
    return f"generated {statements[0]!r} with no DFHRESP( token surviving"


def _case_carry_through_mutation_refused(inputs: _SelfTestInputs) -> str:
    """A copy that alters one unclaimed source line is refused."""
    program = "lgapvs01.cbl"
    result = copy.deepcopy(inputs.results[program])
    lines = inputs.source_lines(program)
    mutated = None
    for index, line in enumerate(result.generated_lines):
        if line.strip() and not is_comment_line(line) and line in lines:
            result.generated_lines[index] = line.rstrip() + " X"
            mutated = index + 1
            break
    _observed(
        mutated is not None,
        f"{program} carries no unclaimed generated line to mutate",
    )
    message = _refused(
        f"a copy of {program} whose carried-through line {mutated} was altered",
        lambda: verify_carry_through(result, lines),
        "unclaimed source lines were carried through unchanged",
    )
    return f"{program}:{mutated} altered -> {message}"


def _case_rule_total_mutation_refused(inputs: _SelfTestInputs) -> str:
    """A run that drops one rewrite site of a rule is refused."""
    results = [copy.deepcopy(inputs.results[name]) for name in PROGRAM_SOURCES]
    dropped = None
    for result in results:
        for index, application in enumerate(result.applications):
            if application.rule_id == "R7":
                del result.applications[index]
                dropped = str(application.source_lines)
                break
        if dropped is not None:
            break
    _observed(dropped is not None, "no R7 site was found to drop")
    message = _refused(
        f"a run whose R7 site {dropped} was dropped",
        lambda: verify_rule_totals(results),
        f"rule R7 was applied {EXPECTED_RULE_SITES['R7'] - 1} time(s), expected "
        f"{EXPECTED_RULE_SITES['R7']}",
    )
    return f"dropped {dropped} -> {message}"


# --------------------------------------------------------------------------
# Cases: one contradicting fragment per rewritten construct
# --------------------------------------------------------------------------
# The structural label R3 is counted under, named once so the case that removes
# a binding and the diagnostic it expects cannot drift apart.
_R3_STRUCTURAL_LABEL = "PROCEDURE DIVISION USING DFHCOMMAREA."

# Each row is one fragment a rule must refuse: the case name, the program the
# fragment is attributed to, the fragment builder and the texts the refusal has
# to carry.  The builder receives the shipped inputs, so a row can place a real
# mapped block at a line the map does not declare for it.
_REFUSED_FRAGMENT_CASES = (
    (
        "r5_chain_link_length_mutation_refused",
        "lgapol01.cbl",
        lambda inputs: _chain_link_fragment(length="32499"),
        (
            "chain LINK LENGTH(32499) is not the shared COMMAREA length "
            f"{CHAIN_LINK_LENGTH}",
        ),
    ),
    (
        "r5_chain_link_commarea_mutation_refused",
        "lgapol01.cbl",
        lambda inputs: _chain_link_fragment(commarea="WS-OTHER-AREA"),
        (f"chain LINK COMMAREA(WS-OTHER-AREA) is not {CHAIN_LINK_COMMAREA}",),
    ),
    (
        "r5_chain_link_target_mutation_refused",
        "lgapol01.cbl",
        lambda inputs: _chain_link_fragment(target="LGAPVS01"),
        ("resolves to 'LGAPVS01'", "this site must link LGAPDB01"),
    ),
    (
        "r5_chain_link_in_unlinked_program_refused",
        "lgapvs01.cbl",
        lambda inputs: _chain_link_fragment(),
        ("this program carries no chain LINK site",),
    ),
    (
        "r6_diagnostic_program_mutation_refused",
        "lgapol01.cbl",
        lambda inputs: _diagnostic_link_fragment(program="LGZZZZ01"),
        (
            "LINK PROGRAM('LGZZZZ01') is not the diagnostic program "
            f"'{DIAGNOSTIC_LINK_PROGRAM}'",
        ),
    ),
    (
        "r6_diagnostic_length_form_refused",
        "lgapol01.cbl",
        lambda inputs: _diagnostic_link_fragment(length="90"),
        ("diagnostic LINK LENGTH(90) is not of the form 'LENGTH OF <item>'",),
    ),
    (
        "r7_return_with_operand_refused",
        "lgapol01.cbl",
        lambda inputs: [
            _fixed_line(
                _FIXTURE_INDENT, "EXEC CICS RETURN TRANSID('SSC1') END-EXEC"
            )
        ],
        ("EXEC CICS RETURN carries operand(s) ['TRANSID']",),
    ),
    (
        "r8_abend_without_code_refused",
        "lgapol01.cbl",
        lambda inputs: [
            _fixed_line(_FIXTURE_INDENT, "EXEC CICS ABEND NODUMP END-EXEC")
        ],
        ("EXEC CICS ABEND has no ABCODE(...) operand",),
    ),
    (
        "r9_write_file_mutation_refused",
        "lgapvs01.cbl",
        lambda inputs: _write_fragment(file_name="KSDSOTHR"),
        (
            "WRITE FILE('KSDSOTHR') is not the projection file "
            f"'{WRITE_FILE_NAME}'",
        ),
    ),
    (
        "r9_write_record_length_mutation_refused",
        "lgapvs01.cbl",
        lambda inputs: _write_fragment(record_length="00063"),
        (f"WRITE LENGTH(00063) is not {WRITE_RECORD_LENGTH}",),
    ),
    (
        "r9_write_key_length_mutation_refused",
        "lgapvs01.cbl",
        lambda inputs: _write_fragment(key_length="00020"),
        (f"WRITE KEYLENGTH(00020) is not {WRITE_KEY_LENGTH}",),
    ),
    (
        "r9_write_literal_area_refused",
        "lgapvs01.cbl",
        lambda inputs: _write_fragment(from_item="'A'"),
        ("WRITE FROM('A') is a literal",),
    ),
    (
        "r10_asktime_without_abstime_refused",
        "lgapol01.cbl",
        lambda inputs: [
            _fixed_line(_FIXTURE_INDENT, "EXEC CICS ASKTIME END-EXEC")
        ],
        ("EXEC CICS ASKTIME has no ABSTIME(...) operand",),
    ),
    (
        "r11_formattime_without_time_refused",
        "lgapol01.cbl",
        lambda inputs: [
            _fixed_line(
                _FIXTURE_INDENT,
                f"EXEC CICS FORMATTIME ABSTIME({_FIXTURE_ABSTIME_ITEM})",
            ),
            _fixed_line(
                _FIXTURE_OPERAND_INDENT,
                f"MMDDYYYY({_FIXTURE_DATE_ITEM}) END-EXEC",
            ),
        ],
        ("EXEC CICS FORMATTIME has no TIME(...) operand",),
    ),
    (
        "r12_unsupported_condition_refused",
        "lgapvs01.cbl",
        lambda inputs: [
            _fixed_line(
                _FIXTURE_INDENT,
                f"IF {_FIXTURE_RESP_ITEM} NOT = DFHRESP(NOTFND)",
            )
        ],
        (
            "references unsupported response condition(s) ['NOTFND']",
            "only NORMAL has a harness constant",
        ),
    ),
    (
        "r2_include_name_mutation_refused",
        "lgapdb01.cbl",
        lambda inputs: _mapped_block_fragment(
            inputs,
            inputs.include_entry("include_sqlca"),
            replace=("SQLCA", "LGPOLICY"),
        ),
        ("source includes 'LGPOLICY'", "names 'SQLCA'"),
    ),
    (
        "r2_enclosing_group_absent_refused",
        "lgapdb01.cbl",
        lambda inputs: _mapped_block_fragment(
            inputs, inputs.include_entry("include_lgcmarea")
        ),
        ("declares enclosing_group", "no code line precedes the block"),
    ),
    (
        "r13_unmapped_block_refused",
        "lgapdb01.cbl",
        lambda inputs: _mapped_block_fragment(
            inputs, inputs.dml_entry("set_identity"), shift=1
        ),
        ("no statement map entry starts at line",),
    ),
    (
        "r13_block_end_line_mismatch_refused",
        "lgapdb01.cbl",
        lambda inputs: _mapped_block_fragment(
            inputs,
            inputs.dml_entry("set_identity"),
            extra=_fixed_line(_FIXTURE_OPERAND_INDENT, "+ 0"),
        ),
        ("statement map entry 'set_identity' ends at line 310",),
    ),
    (
        "r13_table_mutation_refused",
        "lgapdb01.cbl",
        lambda inputs: _mapped_block_fragment(
            inputs,
            inputs.dml_entry("select_lastchanged"),
            replace=("FROM POLICY", "FROM POLICYX"),
        ),
        ("declares table 'POLICY'", "the source block addresses 'POLICYX'"),
    ),
    (
        "r13_predicate_mutation_refused",
        "lgapdb01.cbl",
        lambda inputs: _mapped_block_fragment(
            inputs,
            inputs.dml_entry("select_lastchanged"),
            replace=("WHERE POLICYNUMBER", "WHERE CUSTOMERNUMBER"),
        ),
        ("as predicate token 2", "the source holds 'CUSTOMERNUMBER'"),
    ),
    (
        "r13_host_mutation_refused",
        "lgapdb01.cbl",
        lambda inputs: _mapped_block_fragment(
            inputs,
            inputs.dml_entry("select_lastchanged"),
            replace=("INTO :CA-LASTCHANGED", "INTO :CA-POLICY-NUM"),
        ),
        ("requires host variable(s)", "in that order"),
    ),
    (
        "uncovered_cics_verb_refused",
        "lgapol01.cbl",
        lambda inputs: [
            _fixed_line(_FIXTURE_INDENT, "EXEC CICS SYNCPOINT END-EXEC")
        ],
        ("no rule covers EXEC CICS SYNCPOINT",),
    ),
    (
        "unterminated_exec_block_refused",
        "lgapol01.cbl",
        lambda inputs: [_fixed_line(_FIXTURE_INDENT, "EXEC CICS RETURN")],
        ("opens an EXEC block that is never terminated by END-EXEC",),
    ),
    (
        "comment_inside_exec_block_refused",
        "lgapol01.cbl",
        lambda inputs: [
            _fixed_line(
                _FIXTURE_INDENT,
                f"EXEC CICS ASKTIME ABSTIME({_FIXTURE_ABSTIME_ITEM})",
            ),
            "      *    a comment inside the block",
            _fixed_line(_FIXTURE_OPERAND_INDENT, "END-EXEC"),
        ],
        ("is a comment line inside the EXEC block opened at line 1",),
    ),
)


def _case_refused_fragment(
    inputs: _SelfTestInputs, program: str, build, expected: tuple
) -> str:
    """Translate one contradicting fragment and require the rule to refuse it."""
    lines = build(inputs)
    return _refused(
        f"a {program} fragment of {len(lines)} line(s)",
        lambda: _translated_fragment(inputs, program, lines),
        *expected,
    )


# --------------------------------------------------------------------------
# Cases: the fixed-format layout rule and the emitter width limit
# --------------------------------------------------------------------------
# The fixture the layout cases build: a line count and a width chosen so the
# diagnostic names both, in the form an over-wide generated line produces.
_LAYOUT_FIXTURE_LINES = 115
_LAYOUT_FIXTURE_WIDTH = 95


def _layout_fixture(last: str) -> list:
    """Return a fixture whose final line is ``last``, at the pinned count."""
    filler = _fixed_line(_FIXTURE_INDENT, "CONTINUE")
    return [filler] * (_LAYOUT_FIXTURE_LINES - 1) + [last]


# Each row is one line the layout rule must refuse: the case name, the line and
# the texts the refusal has to carry.  The line stands last in a fixture of
# _LAYOUT_FIXTURE_LINES lines, so every diagnostic names that line number.
_REFUSED_LAYOUT_CASES = (
    (
        "layout_line_past_column_72_refused",
        " " * AREA_B_INDENT + "X" * (_LAYOUT_FIXTURE_WIDTH - AREA_B_INDENT),
        (
            f"lgapvs01.cbl:{_LAYOUT_FIXTURE_LINES} reaches column "
            f"{_LAYOUT_FIXTURE_WIDTH}, past column {MAX_LINE_LENGTH}",
        ),
    ),
    (
        "layout_tab_refused",
        " " * AREA_B_INDENT + "MOVE\tX TO Y",
        (f"lgapvs01.cbl:{_LAYOUT_FIXTURE_LINES} contains a tab character",),
    ),
    (
        "layout_short_line_refused",
        "  X",
        (
            f"lgapvs01.cbl:{_LAYOUT_FIXTURE_LINES} is 3 character(s) long",
            f"must reach the indicator column at column {INDICATOR_INDEX + 1}",
        ),
    ),
    (
        "layout_indicator_column_refused",
        " " * INDICATOR_INDEX + "X" + "MOVE A TO B",
        (
            f"lgapvs01.cbl:{_LAYOUT_FIXTURE_LINES} indicator column holds 'X'",
        ),
    ),
    (
        "layout_sequence_area_refused",
        "00(1  " + " MOVE A TO B",
        (
            f"lgapvs01.cbl:{_LAYOUT_FIXTURE_LINES} sequence area holds invalid "
            f"character(s) ['(']",
        ),
    ),
)


def _case_refused_layout(line: str, expected: tuple) -> str:
    """Require the layout rule to refuse one generated line."""
    return _refused(
        f"a generated line of {len(line)} character(s)",
        lambda: verify_generated_lines(
            "lgapvs01.cbl", _layout_fixture(line)
        ),
        *expected,
    )


def _case_emitter_width_refusals() -> str:
    """The emitter refuses a word and a comment that leave the code area."""
    word = "X" * (MAX_LINE_LENGTH - AREA_A_INDENT + 1)
    statement = _refused(
        f"a statement word of {len(word)} character(s)",
        lambda: emit_statement(AREA_A_INDENT, [word]),
        f"does not fit columns {AREA_A_INDENT + 1}-{MAX_LINE_LENGTH}",
    )
    comment = _refused(
        "a comment line past the code area",
        lambda: emit_comment("Y" * MAX_LINE_LENGTH),
        "comment line would reach column",
    )
    _observed(
        len(emit_statement(AREA_A_INDENT, ["MOVE", "A", "TO", "B"], True)) == 1,
        "a statement that fits the code area was wrapped",
    )
    return f"{statement}; {comment}"


# --------------------------------------------------------------------------
# Cases: the statement-map contract
# --------------------------------------------------------------------------
# Each row is one mutation of the shipped statement-map document the contract
# must refuse: the case name, the mutation and the texts the refusal has to
# carry.  Every mutation is applied to a copy; the shipped document and the
# shipped file are never changed.
_REFUSED_MAP_CASES = (
    (
        "map_dml_count_mismatch_refused",
        lambda document: document["dml"].pop(),
        (
            f"dml holds {EXPECTED_MAP_DML_COUNT - 1} entries but "
            f"checks.dml_count is {EXPECTED_MAP_DML_COUNT}",
        ),
    ),
    (
        "map_duplicated_entry_refused",
        lambda document: document["dml"].append(
            copy.deepcopy(document["dml"][1])
        ),
        (
            f"dml holds {EXPECTED_MAP_DML_COUNT + 1} entries but "
            f"checks.dml_count is {EXPECTED_MAP_DML_COUNT}",
        ),
    ),
    (
        "map_duplicate_dml_id_refused",
        lambda document: document["dml"][2].update(
            {"id": document["dml"][1]["id"]}
        ),
        ("duplicate dml id 'set_identity'",),
    ),
    (
        "map_include_count_mismatch_refused",
        lambda document: document["includes"].pop(),
        (
            f"includes holds {EXPECTED_MAP_INCLUDE_COUNT - 1} entries but "
            f"checks.include_count is {EXPECTED_MAP_INCLUDE_COUNT}",
        ),
    ),
    (
        "map_total_blocks_mismatch_refused",
        lambda document: document["checks"].update(
            {"total_blocks": EXPECTED_MAP_TOTAL_BLOCKS + 1}
        ),
        (
            f"checks.total_blocks is {EXPECTED_MAP_TOTAL_BLOCKS + 1}, expected "
            f"{EXPECTED_MAP_TOTAL_BLOCKS}",
        ),
    ),
    (
        "map_using_count_mismatch_refused",
        lambda document: document["checks"]["using_counts"].update(
            {"set_identity": 2}
        ),
        (
            "dml[set_identity] declares 1 host variables but "
            "checks.using_counts['set_identity'] is 2",
        ),
    ),
    (
        "map_unlisted_call_program_refused",
        lambda document: document["dml"][1].update(
            {"call_program": "SQL-SET-IDENTITY-X"}
        ),
        ("is not listed in checks.call_programs",),
    ),
    (
        "map_declared_census_mutation_refused",
        lambda document: document["source_program"].update(
            {"exec_sql_blocks": EXPECTED_TOTAL_SQL_BLOCKS - 1}
        ),
        (
            f"source_program.exec_sql_blocks is "
            f"{EXPECTED_TOTAL_SQL_BLOCKS - 1}, expected "
            f"{EXPECTED_TOTAL_SQL_BLOCKS}",
        ),
    ),
    (
        "map_order_constraint_count_mismatch_refused",
        lambda document: document["checks"].update(
            {"order_constraint_count": EXPECTED_MAP_ORDER_CONSTRAINT_COUNT - 1}
        ),
        (
            f"checks.order_constraint_count is "
            f"{EXPECTED_MAP_ORDER_CONSTRAINT_COUNT - 1}, expected "
            f"{EXPECTED_MAP_ORDER_CONSTRAINT_COUNT}",
        ),
    ),
    (
        "map_capture_ordinal_mutation_refused",
        lambda document: document["capture_ordinals"]["by_dml_id"].update(
            {"set_identity": "HC-ABSENT-SEQ"}
        ),
        ("capture_ordinals",),
    ),
    (
        "map_enforcer_mutation_refused",
        lambda document: document["execution_order"][0].update(
            {"enforced_by": "modernization/harness/driver.cbl"}
        ),
        (
            "execution_order[policy_first_captured].enforced_by names "
            "'modernization/harness/driver.cbl'",
        ),
    ),
    (
        "map_non_integer_start_line_refused",
        lambda document: document["dml"][1].update({"start_line": "308"}),
        ("start_line holds str '308'; an integer is required",),
    ),
)


def _case_refused_map(inputs: _SelfTestInputs, mutate, expected: tuple) -> str:
    """Require the map contract to refuse one mutation of the shipped document."""
    document = _mutated_document(inputs, mutate)
    return _refused(
        "a mutated statement-map document",
        lambda: _validated(document),
        *expected,
    )


def _case_map_duplicate_start_line_refused(inputs: _SelfTestInputs) -> str:
    """Two map entries claiming one source block line are refused."""
    contract = copy.deepcopy(inputs.contract)
    first = int(contract["dml"][0]["start_line"])
    contract["dml"][1]["start_line"] = first
    message = _refused(
        f"a map whose second dml entry also starts at line {first}",
        lambda: index_statement_map(contract),
        f"statement map has two entries starting at line {first}",
    )
    return message


def _case_capture_copybook_mutation_refused(inputs: _SelfTestInputs) -> str:
    """A capture copybook missing one declared ordinal item is refused."""
    resolution = inputs.contract["ordinal_resolution"]
    item = resolution["set_identity"]
    text = inputs.copybooks[CAPTURE_COPYBOOK].decode("utf-8")
    kept = [
        line
        for line in text.split("\n")
        if item not in line or is_comment_line(line)
    ]
    _observed(
        len(kept) < len(text.split("\n")),
        f"{CAPTURE_COPYBOOK} declares no line naming {item} to remove",
    )
    message = _refused(
        f"a capture copybook whose declaration of {item} was removed",
        lambda: verify_capture_order_contract(
            inputs.contract,
            "\n".join(kept).encode("utf-8"),
            EXPECTED_COPYBOOK_DIR,
        ),
        f"names the ordinal item(s) ['{item}']",
        "does not declare",
    )
    return message


def _case_absent_harness_copybook_refused(inputs: _SelfTestInputs) -> str:
    """A harness copybook absent from the directory read is refused."""
    components = lexical_repo_components(
        EXPECTED_STUB_DIR, "--copybook-dir"
    ) + (CAPTURE_COPYBOOK,)
    message = _refused(
        f"a read of {CAPTURE_COPYBOOK} from a directory that does not hold it",
        lambda: read_repo_file(
            components,
            f"the harness copybook {CAPTURE_COPYBOOK}",
            MAX_READ_FILE_BYTES,
        ),
        f"the harness copybook {CAPTURE_COPYBOOK} names",
        "which does not exist",
    )
    return message


# --------------------------------------------------------------------------
# Cases: the pinned digests and the read and write surfaces
# --------------------------------------------------------------------------
def _case_source_digest_mutation_refused(inputs: _SelfTestInputs) -> str:
    """A source whose bytes differ from its pinned digest is refused."""
    name = "lgapvs01.cbl"
    mutated = inputs.sources[name].replace(b"KSDSPOLY", b"KSDSOTHR", 1)
    _observed(
        mutated != inputs.sources[name]
        and len(mutated) == len(inputs.sources[name]),
        f"the fixture did not change one construct of {name} at equal length",
    )
    message = _refused(
        f"{name} carrying a changed byte range at its original length",
        lambda: require_authorized_source_digest(name, mutated),
        f"{name} does not carry its pinned digest",
        AUTHORIZED_SOURCE_DIGESTS[name],
    )
    return message


def _case_sources_changed_during_run_refused(inputs: _SelfTestInputs) -> str:
    """A source whose digest differs from the baseline of the run is refused."""
    name = "lgapol01.cbl"
    baseline = dict(inputs.baseline)
    baseline[name] = "0" * 64
    message = _refused(
        f"a baseline recording another digest for {name}",
        lambda: verify_sources_unchanged(EXPECTED_SOURCE_DIR, baseline),
        f"{name} changed during the run",
        inputs.baseline[name],
    )
    return message


# Each row is one read or write surface the guards must refuse: the case name,
# the body and the texts the refusal has to carry.
_REFUSED_SURFACE_CASES = (
    (
        "source_digest_unknown_name_refused",
        lambda: require_authorized_source_digest("driver.cbl", b""),
        ("no pinned digest for authorized source 'driver.cbl'",),
    ),
    (
        "source_outside_allow_list_refused",
        lambda: read_authorized_source(EXPECTED_SOURCE_DIR, "lgstsq.cbl"),
        (
            "refusing to read 'lgstsq.cbl'",
            "only the five authorized source files",
        ),
    ),
    (
        "source_traversal_refused",
        lambda: read_authorized_source(
            EXPECTED_SOURCE_DIR, "../../modernization/harness/driver.cbl"
        ),
        ("refusing to read",),
    ),
    (
        "copybook_outside_harness_set_refused",
        lambda: read_harness_copybook(EXPECTED_COPYBOOK_DIR, "lgcmarea.cpy"),
        (
            "refusing to read 'lgcmarea.cpy'",
            "only the harness copybooks",
        ),
    ),
    (
        "source_directory_moved_refused",
        lambda: require_expected_read_directory(
            REPO_ROOT / "modernization" / "harness",
            EXPECTED_SOURCE_DIR,
            "--source-dir",
        ),
        ("--source-dir names", "this translator reads only"),
    ),
    (
        "copybook_directory_moved_refused",
        lambda: require_expected_read_directory(
            EXPECTED_STUB_DIR, EXPECTED_COPYBOOK_DIR, "--copybook-dir"
        ),
        ("--copybook-dir names", "this translator reads only"),
    ),
    (
        "statement_map_moved_refused",
        lambda: require_expected_read_file(
            EXPECTED_DRIVER_SOURCE, EXPECTED_STATEMENT_MAP, "--statement-map"
        ),
        ("--statement-map names", "this translator reads only"),
    ),
    (
        "read_outside_checkout_refused",
        lambda: lexical_repo_components(
            Path("/etc/passwd"), "--statement-map"
        ),
        ("this translator reads only inside",),
    ),
    (
        "build_directory_outside_checkout_refused",
        lambda: BuildTree(REPO_ROOT / "modernization" / "harness"),
        ("refusing to write to", "the build directory must be"),
    ),
    (
        "build_path_leaving_root_refused",
        lambda: BuildTree(CANONICAL_BUILD_ROOT).path_for("../src/escape.cbl"),
        ("refusing to write outside the build tree",),
    ),
    (
        "build_path_absolute_refused",
        lambda: BuildTree(CANONICAL_BUILD_ROOT).path_for("/etc/passwd"),
        ("build paths must be relative",),
    ),
)


def _case_refused_surface(body, expected: tuple) -> str:
    """Require one read or write surface guard to refuse its fixture."""
    return _refused("the surface under test", body, *expected)


# --------------------------------------------------------------------------
# Case runner
# --------------------------------------------------------------------------
def _case_inputs_unchanged_by_matrix(inputs: _SelfTestInputs) -> str:
    """Every shipped input still reads as it did before the cases ran."""
    for name, digest in sorted(inputs.baseline.items()):
        current = sha256_of_bytes(
            read_authorized_source(EXPECTED_SOURCE_DIR, name)
        )
        _observed(
            current == digest,
            f"{name} now reads as {current}; the matrix started from {digest}",
        )
    for name, data in sorted(inputs.copybooks.items()):
        current = read_harness_copybook(EXPECTED_COPYBOOK_DIR, name)
        _observed(
            current == data,
            f"the harness copybook {name} changed while the matrix ran",
        )
    document = read_statement_map_document(EXPECTED_STATEMENT_MAP)
    _observed(
        document == inputs.document,
        "the statement map changed while the matrix ran",
    )
    return (
        f"{len(inputs.baseline)} source(s), {len(inputs.copybooks)} harness "
        f"copybook(s) and the statement map re-read unchanged"
    )


def _run_case(results: list, stream, quiet: bool, name: str, body) -> None:
    """Run one case, record its outcome and print its line.

    A case that raises records a failure and the run continues with the next
    one, so one broken guard does not hide the state of the rest.
    ``_SelfTestFailure`` carries the observation the case made; a
    ``TranslationError`` a case did not expect, and any of the listed defect
    classes, are reported by type and message.
    """
    try:
        detail = body()
    except _SelfTestFailure as failure:
        result = _CaseResult(name=name, passed=False, detail=one_line(failure))
    except TranslationError as error:
        result = _CaseResult(
            name=name,
            passed=False,
            detail=f"unexpected refusal: {one_line(error)}",
        )
    except (
        ArithmeticError,
        AssertionError,
        AttributeError,
        LookupError,
        NameError,
        OSError,
        RuntimeError,
        StopIteration,
        TypeError,
        ValueError,
        yaml.YAMLError,
    ) as error:
        result = _CaseResult(
            name=name,
            passed=False,
            detail=f"unexpected {type(error).__name__}: {one_line(error)}",
        )
    else:
        result = _CaseResult(name=name, passed=True, detail=one_line(detail))
    results.append(result)
    if result.passed and quiet:
        return
    verdict = "PASS" if result.passed else "FAIL"
    print(f"self-test {verdict} {result.name} -- {result.detail}", file=stream)


def run_self_test(quiet: bool = False, stream=None) -> int:
    """Run every case and return 0, or ``EXIT_SELF_TEST_FAILED`` on a failure.

    The shipped statement map, the five authorized sources and the four harness
    copybooks are read first and the three programs are translated once, so an
    input that cannot be read raises its own ``TranslationError`` before any
    case runs.  Each case then prints one line to ``stream``, which defaults to
    standard output, followed by one summary line; ``quiet`` limits the case
    lines to the failing ones.  Every fixture is built in this process from
    strings, bytes and copies of the documents already read: the matrix creates
    no file, writes nothing inside or outside the build tree, starts no
    subprocess and leaves the shipped inputs exactly as it found them.
    """
    out = sys.stdout if stream is None else stream
    inputs = _self_test_inputs()
    results = []

    _run_case(results, out, quiet, "statement_map_accepted",
              lambda: _case_statement_map_accepted(inputs))
    _run_case(results, out, quiet, "order_metadata_accepted",
              lambda: _case_order_metadata_accepted(inputs))
    _run_case(results, out, quiet, "pinned_digests_accepted",
              lambda: _case_pinned_digests_accepted(inputs))
    _run_case(results, out, quiet, "harness_copybooks_accepted",
              lambda: _case_harness_copybooks_accepted(inputs))
    _run_case(results, out, quiet, "shipped_programs_translate",
              lambda: _case_shipped_programs_translate(inputs))
    _run_case(results, out, quiet, "shipped_lines_within_columns",
              lambda: _case_shipped_lines_within_columns(inputs))
    _run_case(results, out, quiet, "shipped_tokens_accounted",
              lambda: _case_shipped_tokens_accounted(inputs))
    _run_case(results, out, quiet, "shipped_carry_through",
              lambda: _case_shipped_carry_through(inputs))
    _run_case(results, out, quiet, "shipped_structural_counts",
              lambda: _case_shipped_structural_counts(inputs))
    _run_case(results, out, quiet, "shipped_rule_totals",
              lambda: _case_shipped_rule_totals(inputs))
    _run_case(results, out, quiet, "shipped_chain_links",
              lambda: _case_shipped_chain_links(inputs))
    _run_case(results, out, quiet, "shipped_declared_census",
              lambda: _case_shipped_declared_census(inputs))
    _run_case(results, out, quiet, "shipped_capture_order_contract",
              lambda: _case_shipped_capture_order_contract(inputs))
    _run_case(results, out, quiet, "shipped_sources_unchanged",
              lambda: _case_shipped_sources_unchanged(inputs))
    _run_case(results, out, quiet, "build_root_accepted",
              _case_build_root_accepted)

    _run_case(results, out, quiet, "r1_directive_commented",
              lambda: _case_r1_directive_commented(inputs))
    _run_case(results, out, quiet, "r1_active_directive_refused",
              lambda: _case_r1_active_directive_refused(inputs))
    _run_case(results, out, quiet, "r2_include_replaced",
              lambda: _case_r2_include_replaced(inputs))
    _run_case(results, out, quiet, "r3_binding_emitted",
              lambda: _case_r3_binding_emitted(inputs))
    _run_case(results, out, quiet, "r3_missing_binding_refused",
              lambda: _case_r3_missing_binding_refused(inputs))
    _run_case(results, out, quiet, "r4_declarations_inserted",
              lambda: _case_r4_declarations_inserted(inputs))
    _run_case(results, out, quiet, "r5_chain_link_rewritten",
              lambda: _case_r5_chain_link_rewritten(inputs))
    _run_case(results, out, quiet, "r6_diagnostic_link_rewritten",
              lambda: _case_r6_diagnostic_link_rewritten(inputs))
    _run_case(results, out, quiet, "r7_return_becomes_goback",
              lambda: _case_r7_return_becomes_goback(inputs))
    _run_case(results, out, quiet, "r8_abend_captured",
              lambda: _case_r8_abend_captured(inputs))
    _run_case(results, out, quiet, "r9_write_reaches_capture",
              lambda: _case_r9_write_reaches_capture(inputs))
    _run_case(results, out, quiet, "r10_asktime_rewritten",
              lambda: _case_r10_asktime_rewritten(inputs))
    _run_case(results, out, quiet, "r11_formattime_rewritten",
              lambda: _case_r11_formattime_rewritten(inputs))
    _run_case(results, out, quiet, "r12_condition_substituted",
              lambda: _case_r12_condition_substituted(inputs))
    _run_case(results, out, quiet, "r13_call_emitted",
              lambda: _case_r13_call_emitted(inputs))
    _run_case(results, out, quiet, "r14_lines_carried",
              lambda: _case_r14_lines_carried(inputs))
    _run_case(results, out, quiet, "r14_carry_through_mutation_refused",
              lambda: _case_carry_through_mutation_refused(inputs))
    _run_case(results, out, quiet, "rule_total_mutation_refused",
              lambda: _case_rule_total_mutation_refused(inputs))

    for name, program, build, expected in _REFUSED_FRAGMENT_CASES:
        _run_case(
            results, out, quiet, name,
            lambda program=program, build=build, expected=expected: (
                _case_refused_fragment(inputs, program, build, expected)
            ),
        )
    for name, line, expected in _REFUSED_LAYOUT_CASES:
        _run_case(
            results, out, quiet, name,
            lambda line=line, expected=expected: _case_refused_layout(
                line, expected
            ),
        )
    _run_case(results, out, quiet, "emitter_width_refusals",
              _case_emitter_width_refusals)
    for name, mutate, expected in _REFUSED_MAP_CASES:
        _run_case(
            results, out, quiet, name,
            lambda mutate=mutate, expected=expected: _case_refused_map(
                inputs, mutate, expected
            ),
        )
    _run_case(results, out, quiet, "map_duplicate_start_line_refused",
              lambda: _case_map_duplicate_start_line_refused(inputs))
    _run_case(results, out, quiet, "capture_copybook_mutation_refused",
              lambda: _case_capture_copybook_mutation_refused(inputs))
    _run_case(results, out, quiet, "absent_harness_copybook_refused",
              lambda: _case_absent_harness_copybook_refused(inputs))
    _run_case(results, out, quiet, "source_digest_mutation_refused",
              lambda: _case_source_digest_mutation_refused(inputs))
    _run_case(results, out, quiet, "sources_changed_during_run_refused",
              lambda: _case_sources_changed_during_run_refused(inputs))
    for name, body, expected in _REFUSED_SURFACE_CASES:
        _run_case(
            results, out, quiet, name,
            lambda body=body, expected=expected: _case_refused_surface(
                body, expected
            ),
        )

    _run_case(results, out, quiet, "shipped_inputs_unchanged_by_matrix",
              lambda: _case_inputs_unchanged_by_matrix(inputs))

    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    print(
        f"self-test summary cases={len(results)} passed={passed} "
        f"failed={failed}",
        file=out,
    )
    return 0 if failed == 0 else EXIT_SELF_TEST_FAILED


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
            "rule, count or guard failure. With --self-test it generates "
            "nothing and runs the built-in case matrix instead, leaving status "
            "0 when every case held and 5 when one did not. Decision "
            "rationale: modernization/docs/decision-log.md"
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
        "--self-test",
        action="store_true",
        help=(
            "run the built-in case matrix over the pinned sources, statement "
            "map and harness copybooks of this checkout and exit; it generates "
            "no build tree, writes no file and accepts no other path option"
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help=(
            "with --self-test, print only the failing case lines and the "
            "summary"
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
    if args.self_test:
        supplied = [
            option
            for option, value, default in (
                ("--source-dir", args.source_dir, DEFAULT_SOURCE_DIR),
                ("--build-dir", args.build_dir, DEFAULT_BUILD_DIR),
                ("--statement-map", args.statement_map, DEFAULT_STATEMENT_MAP),
                ("--copybook-dir", args.copybook_dir, DEFAULT_COPYBOOK_DIR),
                ("--report", args.report, None),
            )
            if value != default
        ]
        if supplied:
            parser.error(
                "--self-test reads the pinned locations of this checkout and "
                f"accepts no {', '.join(supplied)}"
            )
    if args.quiet and not args.self_test:
        parser.error("--quiet applies to --self-test only")
    try:
        if args.self_test:
            return run_self_test(quiet=args.quiet)
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
