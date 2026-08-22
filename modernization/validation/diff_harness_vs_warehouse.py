#!/usr/bin/env python3
"""Compare the GnuCOBOL harness captures with the two canonical warehouse rows.

WHAT THIS TOOL DOES
    For each executed case it reads what the harness already produced - the
    capture file, the returned 32,500-character COMMAREA and the generated
    sample record the driver was handed - and compares every canonical column
    of canonical.issued_policy and canonical.preissued_rating with the harness
    value for the same policy. It reads the harness output only: it starts no
    driver, invokes no compiler, writes no COMMAREA and executes no chain, so a
    comparison covers the run whose artifacts stand on disk.

    Both sides of the comparison are independent. The harness side carries the
    values the translated chain handed to the policy and product inserts, the
    values the returned COMMAREA carries after the chain completed and the
    values the driver was handed on standard input. The warehouse side carries
    the two rows the unchanged dbt models materialized from the landed record.

WHICH VALUES IT COMPARES
    Every column of both canonical relations, 20 canonical column instances per
    case: the 11 columns of canonical.issued_policy and the 9 columns of
    canonical.preissued_rating. No column is skipped and no column is inferred:
    a column whose harness input is absent is reported as MISSING and fails.
    Each comparison record names the relation, the column, the harness
    authority it read, the COBOL item and its path:line locator, both values,
    the delta for an amount, the normalisation applied and the verdict, so the
    report enumerates the whole comparison surface.

    Alongside the columns it asserts the VSAM write of the case - a 64-byte
    record under a 21-byte key equal to the type letter, the customer number
    X(10) and the policy number X(10) in that layout order - and the
    chain-completion state of the case: the driver status, the absence of an
    abend, the policy SQL capture, exactly one product capture and no endowment
    or house capture. The 43-byte VSAM payload is mapped to no canonical column.

    It also asserts the canonical inventory: schema canonical holds exactly
    issued_policy and preissued_rating, each with the declared column names in
    the declared ordinal order.

HOW AMOUNTS ARE COMPARED
    The six amount values are read as digit strings and carried as
    decimal.Decimal; no amount ever passes through a binary float. The delta is
    the absolute difference between the warehouse value and the harness value.
    A delta of zero passes. A non-zero delta within AMOUNT_TOLERANCE passes and
    is recorded in the unexpected_in_tolerance list, counted in the summary and
    printed in its own report section. A delta above AMOUNT_TOLERANCE fails.
    AMOUNT_TOLERANCE is a module constant and no command-line option changes it.
    The scale of each warehouse amount is recorded, and a scale other than 2 is
    reported as an unexpected observation of that comparison.

    A product premium the policy type does not populate must be NULL. A value
    of zero standing in such a column is reported as a zero standing in place of
    NULL and fails. A NULL standing where the policy type populates the column
    fails as well.

HOW EVERY OTHER VALUE IS COMPARED
    Exactly, after a named normalisation. Fixed-width alphanumeric items are
    compared with trailing spaces removed. Numeric identifiers are compared as
    integers, so leading zeros of the COMMAREA window do not enter the
    comparison. Dates are compared as ISO calendar dates. The 26-character Db2
    timestamp is normalised to microsecond precision and compared as a moment;
    the Db2 form YYYY-MM-DD-HH.MM.SS.ffffff and the ISO forms with a T or a
    space separator are all accepted. Each normalisation applied is named in the
    comparison record.

    Where two harness authorities carry one column - the returned COMMAREA and
    an SQL capture, or the driver input and the returned COMMAREA - both are
    read and both are compared. Two authorities that disagree fail the column,
    and the diagnostic names every value read.

    policy_number, policy_type and source_system_key are compared across the two
    relations as well as against the harness.

WHICH INPUTS IT ACCEPTS
    --case          case to compare, repeatable. Default: both supported cases.
    --cases         the same selection as one comma-separated value.
    --run-dir       directory holding one subdirectory per case. Default
                    modernization/harness/build/run.
    --captures      capture file of a single case, replacing the run-dir path.
    --commarea-post returned COMMAREA of a single case, replacing the run-dir
                    path.
    --sample-record record the driver was handed. Taken from the DD_SAMPLEFILE
                    environment variable when the option is absent, and from
                    <run-dir>/../samples/commarea_<fixture>.dat when neither is
                    given, where <fixture> is the FIXTURE capture of the case.
    --field-map     metadata spine. Default
                    modernization/extraction/copybook_field_map.yml.
    --target        warehouse to query, duckdb or redshift. Default from the
                    WAREHOUSE_TARGET environment variable, then duckdb.
    --database      DuckDB database file. Default from the LOCAL_DUCKDB_PATH and
                    then the DUCKDB_DATABASE environment variable, and then
                    modernization/validation/local.duckdb.
    --source-system-key
                    source-system discriminator to look up. Default from the
                    SOURCE_SYSTEM_KEY environment variable, then
                    GENAPP_CLASS_EXEMPLAR.
    --report        Markdown report path. Default
                    modernization/validation/artifacts/diff-report.md.
    --json          JSON report path. Default
                    modernization/validation/artifacts/diff-report.json.
    --expected-dir  directory of the per-case capture snapshots. Default
                    modernization/validation/expected.
    --quiet         print the verdict line alone.

    The Redshift target reads REDSHIFT_HOST, REDSHIFT_PORT, REDSHIFT_DATABASE,
    REDSHIFT_USER and REDSHIFT_PASSWORD, the variable contract of
    modernization/dbt/genapp_rqi/profiles.example.yml. An environment variable
    holding the empty string or whitespace alone counts as unset, so the
    documented default applies.

WHAT IT WRITES
    A Markdown report and a JSON report, each replaced in full on every run, and
    one capture snapshot per case at
    <expected-dir>/<case>/captures.normalized.json. A snapshot that is absent is
    written; a snapshot that is present is compared, and a difference is
    reported key by key and fails the run. Nothing else is written: no database
    is modified, no AWS resource is created and no path under base/ is opened
    for writing.

    No credential, password, token, IAM role, endpoint URL or environment
    listing reaches stdout, stderr, the Markdown report or the JSON report. A
    Redshift connection is recorded as its host and database alone. The reports
    do carry policy, customer and broker identifiers, which are the values under
    comparison.

    While the run addresses the local substitute, every claimed result in the
    Markdown report carries the phrase "validated against local substitute, not
    AWS" and the report states that these results leave the formal AWS diff
    requirement OPEN.

HOW IT FAILS
    0   every comparison passed. A non-zero delta inside the tolerance is
        reported in the unexpected_in_tolerance section and returns 0.
    1   a comparison failed.
    2   a harness input is missing or incomplete: an absent capture file or
        record, a COMMAREA of a length other than the one the field map
        declares, an unreadable capture line, a repeated capture key, an absent
        capture key a comparison needs, or a capture snapshot that differs from
        the one on disk.
    3   the warehouse answered but its content is refused: a canonical relation
        set or column set other than the declared one, or other than exactly one
        row for the natural key of a case.
    4   a connection, configuration or usage failure: an unknown option, a
        target that cannot be opened, an absent Redshift setting, an adapter
        that is not installed, or a field map that disagrees with the byte grid
        this tool carries. Nothing is written on this path.

WHERE THIS STEP SITS
    Figure 5 — Validation Harness Control Flow in
    modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import json
import os
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, NamedTuple

import yaml

_PROGRAM = "diff_harness_vs_warehouse"

# Repository root, two directories above this file's own parent. Every relative
# path a caller supplies, and every default below, resolves against it rather
# than against the current working directory.
REPO_ROOT = Path(__file__).resolve().parents[2]

# Absolute acceptance threshold for an amount comparison. It is a module
# constant and no command-line option, environment variable or field map value
# replaces it; the value the field map records is read only to confirm that it
# states the same threshold.
AMOUNT_TOLERANCE = Decimal("0.01")

# Scale every warehouse amount is expected to carry.
AMOUNT_SCALE = 2

# Disposition of the target a local-substitute run was validated against. The
# phrase is written exactly as it stands here.
STATUS_LABEL_TEXT = "validated against local substitute, not AWS"

# Statement the local-substitute report carries beside its verdict.
AWS_OPEN_TEXT = (
    "These results do not satisfy the formal AWS diff requirement, which "
    "remains OPEN: it closes only when the same dbt models run unmodified "
    "against real S3 and Amazon Redshift."
)

# Process statuses. Documented in the module docstring and in --help.
EXIT_OK = 0
EXIT_COMPARISON_FAILED = 1
EXIT_HARNESS_INPUT = 2
EXIT_WAREHOUSE_REFUSED = 3
EXIT_CONFIGURATION = 4

# Order the statuses are reported in when a run collects more than one.
_EXIT_PRECEDENCE = (
    EXIT_CONFIGURATION,
    EXIT_WAREHOUSE_REFUSED,
    EXIT_HARNESS_INPUT,
    EXIT_COMPARISON_FAILED,
    EXIT_OK,
)

# Targets this tool queries, and the adapter each one is opened through.
TARGET_DUCKDB = "duckdb"
TARGET_REDSHIFT = "redshift"
TARGETS = (TARGET_DUCKDB, TARGET_REDSHIFT)

# Parameter marker of each adapter's paramstyle. Every statement in this module
# is written with "?" markers and the marker is replaced before execution, so no
# value is ever concatenated into SQL text.
PARAMETER_MARKERS = {TARGET_DUCKDB: "?", TARGET_REDSHIFT: "%s"}

# Default paths, all relative to REPO_ROOT.
DEFAULT_RUN_DIR = "modernization/harness/build/run"
DEFAULT_FIELD_MAP = "modernization/extraction/copybook_field_map.yml"
DEFAULT_DUCKDB_PATH = "modernization/validation/local.duckdb"
DEFAULT_REPORT = "modernization/validation/artifacts/diff-report.md"
DEFAULT_JSON_REPORT = "modernization/validation/artifacts/diff-report.json"
DEFAULT_EXPECTED_DIR = "modernization/validation/expected"
ARTIFACTS_DIR = "modernization/validation/artifacts"

# Source-system discriminator applied when neither the option nor the
# environment names one.
DEFAULT_SOURCE_SYSTEM_KEY = "GENAPP_CLASS_EXEMPLAR"

# Names of the two files the harness writes per case inside <run-dir>/<case>,
# and the directory and name pattern of the record the driver was handed.
CAPTURES_NAME = "captures.txt"
COMMAREA_POST_NAME = "commarea_post.dat"
SAMPLES_DIR_NAME = "samples"
SAMPLE_NAME_TEMPLATE = "commarea_{fixture}.dat"
SAMPLE_PATH_VARIABLE = "DD_SAMPLEFILE"

# Name of the per-case capture snapshot inside <expected-dir>/<case>.
SNAPSHOT_NAME = "captures.normalized.json"

# Largest file this tool reads, applied to every input.
MAX_INPUT_BYTES = 1_048_576

# Trees no output path of this tool may resolve into.
PROTECTED_TREES = ("base", "synthetic_class")

# --------------------------------------------------------------------------
# Declared canonical surface
# --------------------------------------------------------------------------
# The schema and the two relations the canonical layer holds, with the column
# names in ordinal order. The field map is the naming authority and is read at
# run time; these tuples are the independently verified form the loaded map is
# held to, and they are the set the canonical inventory assertion applies.
CANONICAL_SCHEMA = "canonical"
ISSUED_POLICY_ALIAS = "issued_policy"
PREISSUED_RATING_ALIAS = "preissued_rating"

ISSUED_POLICY_COLUMNS = (
    "source_system_key",
    "policy_number",
    "policy_type",
    "customer_number",
    "request_id",
    "return_code",
    "issue_date",
    "expiry_date",
    "last_changed",
    "broker_id",
    "brokers_reference",
)

PREISSUED_RATING_COLUMNS = (
    "source_system_key",
    "policy_number",
    "policy_type",
    "payment_amount",
    "motor_premium_amount",
    "fire_premium_amount",
    "crime_premium_amount",
    "flood_premium_amount",
    "weather_premium_amount",
)

DECLARED_RELATIONS = {
    ISSUED_POLICY_ALIAS: ISSUED_POLICY_COLUMNS,
    PREISSUED_RATING_ALIAS: PREISSUED_RATING_COLUMNS,
}

# Relation keys of the field map's targets block, in report order.
RELATION_KEYS = (
    f"{CANONICAL_SCHEMA}.{ISSUED_POLICY_ALIAS}",
    f"{CANONICAL_SCHEMA}.{PREISSUED_RATING_ALIAS}",
)

# Column instances one case compares: the 11 columns of canonical.issued_policy
# and the 9 of canonical.preissued_rating.
CANONICAL_COLUMN_INSTANCES = len(ISSUED_POLICY_COLUMNS) + len(PREISSUED_RATING_COLUMNS)

# The three columns both relations carry, compared across the two rows as well
# as against the harness.
SHARED_COLUMNS = ("source_system_key", "policy_number", "policy_type")

# COMMAREA windows of base/src/lgcmarea.cpy this tool carries as (item, PIC,
# 1-based offset, length). The loaded field map must declare every one of them
# with the same PICTURE, offset and length; a disagreement ends the run with
# EXIT_CONFIGURATION rather than being reconciled.
VERIFIED_WINDOWS = (
    ("CA-REQUEST-ID", "X(6)", 1, 6),
    ("CA-RETURN-CODE", "9(2)", 7, 2),
    ("CA-CUSTOMER-NUM", "9(10)", 9, 10),
    ("CA-POLICY-NUM", "9(10)", 19, 10),
    ("CA-ISSUE-DATE", "X(10)", 29, 10),
    ("CA-EXPIRY-DATE", "X(10)", 39, 10),
    ("CA-LASTCHANGED", "X(26)", 49, 26),
    ("CA-BROKERID", "9(10)", 75, 10),
    ("CA-BROKERSREF", "X(10)", 85, 10),
    ("CA-PAYMENT", "9(6)", 95, 6),
    ("CA-M-PREMIUM", "9(6)", 166, 6),
    ("CA-B-FirePremium", "9(8)", 900, 8),
    ("CA-B-CrimePremium", "9(8)", 912, 8),
    ("CA-B-FloodPremium", "9(8)", 924, 8),
    ("CA-B-WeatherPremium", "9(8)", 936, 8),
)

# Length of the interface record, confirmed against the field map.
COMMAREA_RECORD_LENGTH = 32500

# Request routing of base/src/lgapdb01.cbl:184-207, confirmed against the field
# map, and the two request ids a sample definition describes.
VERIFIED_ROUTING = {"01AEND": "E", "01AHOU": "H", "01AMOT": "M", "01ACOM": "C"}
SUPPORTED_CASES = ("01AMOT", "01ACOM")

# Return codes the named chain sets, confirmed against the field map and carried
# into the report as the outcome vocabulary of the chain. The harness executes
# the success path alone, so a compared case carries 00.
VERIFIED_RETURN_CODES = ("00", "70", "80", "90", "98", "99")
SUCCESS_RETURN_CODE = "00"

# Capture key that carries the SQL value of one logical field entry. Each name
# is the key modernization/harness/driver.cbl writes into the capture file for
# the value the translated chain handed to that insert, or read back from it.
# An entry absent from this mapping has no SQL capture: request_id is compared
# against the driver input and the returned COMMAREA, and return_code against
# the returned COMMAREA and its own capture.
SQL_CAPTURE_KEYS = {
    "policy_number": "SQL_POLICY_ASSIGNED_NUMBER",
    "policy_type": "SQL_POLICY_POLICYTYPE",
    "customer_number": "SQL_POLICY_CUSTOMERNUM",
    "issue_date": "SQL_POLICY_ISSUEDATE",
    "expiry_date": "SQL_POLICY_EXPIRYDATE",
    "last_changed": "SQL_POLICY_ASSIGNED_LASTCHANGED",
    "broker_id": "SQL_POLICY_BROKERID",
    "brokers_reference": "SQL_POLICY_BROKERSREF",
    "payment": "SQL_POLICY_PAYMENT",
    "motor_premium": "SQL_MOTOR_PREMIUM",
    "fire_premium": "SQL_COMMERCIAL_FIREPREMIUM",
    "crime_premium": "SQL_COMMERCIAL_CRIMEPREMIUM",
    "flood_premium": "SQL_COMMERCIAL_FLOODPREMIUM",
    "weather_premium": "SQL_COMMERCIAL_WEATHERPREMIUM",
}

# Capture family each SQL capture key belongs to, named in the comparison record.
SQL_CAPTURE_FAMILIES = {
    "SQL_POLICY": "policy insert capture",
    "SQL_MOTOR": "motor insert capture",
    "SQL_COMMERCIAL": "commercial insert capture",
}

# Presence capture of each product insert, keyed by the policy type that
# populates it. A case asserts Y for its own product and N for every other.
PRODUCT_PRESENCE_KEYS = {
    "M": "SQL_MOTOR_PRESENT",
    "C": "SQL_COMMERCIAL_PRESENT",
    "E": "SQL_ENDOWMENT_PRESENT",
    "H": "SQL_HOUSE_PRESENT",
}

# Capture keys the chain-completion assertions read.
DRIVER_STATUS_KEY = "DRIVER_STATUS"
DRIVER_STATUS_PASS = "PASS"
DRIVER_EXIT_STATUS_KEY = "DRIVER_EXIT_STATUS"
DRIVER_EXIT_STATUS_OK = "00"
ABEND_PRESENT_KEY = "ABEND_PRESENT"
ABEND_CODE_KEY = "ABEND_CODE"
ABEND_COUNT_KEY = "ABEND_COUNT"
DIAG_LINK_COUNT_KEY = "DIAG_LINK_COUNT"
POLICY_PRESENT_KEY = "SQL_POLICY_PRESENT"
CASE_KEY = "CASE"
FIXTURE_KEY = "FIXTURE"
RETURN_CODE_CAPTURE_KEY = "CA_RETURN_CODE"

# Capture keys the VSAM corroboration reads, and the two lengths the write of
# base/src/lgapvs01.cbl:135-141 states.
VSAM_PRESENT_KEY = "VSAM_PRESENT"
VSAM_LENGTH_KEY = "VSAM_LENGTH"
VSAM_KEYLENGTH_KEY = "VSAM_KEYLENGTH"
VSAM_KEY_KEY = "VSAM_KEY"
VSAM_REQUEST_ID_KEY = "VSAM_REQUEST_ID"
VSAM_CUSTOMER_NUM_KEY = "VSAM_CUSTOMER_NUM"
VSAM_POLICY_NUM_KEY = "VSAM_POLICY_NUM"
VSAM_RECORD_LENGTH = 64
VSAM_KEY_LENGTH = 21

# Layout of WF-Policy-Key at base/src/lgapvs01.cbl:26-29 as (component, length),
# in layout order. The MOVE statements at base/src/lgapvs01.cbl:99-101 run in
# another order; the comparison follows the layout.
VSAM_KEY_LAYOUT = (
    ("WF-Request-ID", 1),
    ("WF-Customer-Num", 10),
    ("WF-Policy-Num", 10),
)

# Position of the type letter inside the request id, from
# "Move CA-Request-ID(4:1) To WF-Request-ID" at base/src/lgapvs01.cbl:99.
VSAM_TYPE_LETTER_POSITION = 4

# Length of the product payload the VSAM record carries after its key. It is
# corroboration of the write alone and is mapped to no canonical column.
VSAM_PAYLOAD_LENGTH = 43

# Comparison kinds. The kind of a column follows its declared canonical type,
# except that a column of the field map's amount list is always an amount.
KIND_TEXT = "exact string"
KIND_CHAR = "single char"
KIND_INTEGER = "integer"
KIND_DATE = "date"
KIND_TIMESTAMP = "timestamp"
KIND_AMOUNT = "amount"
KIND_NULL_EXPECTED = "null expectation"

# Statuses a comparison record carries. MISSING is a failure whose cause is an
# absent harness input; there is no status for a comparison that was not made.
STATUS_PASS = "PASS"
STATUS_PASS_IN_TOLERANCE = "PASS (unexpected in tolerance)"
STATUS_FAIL = "FAIL"
STATUS_MISSING = "MISSING"

# Timestamp forms accepted for CA-LASTCHANGED, in the order they are tried: the
# Db2 character form the chain reads back and the two ISO forms.
TIMESTAMP_INPUT_FORMATS = (
    "YYYY-MM-DD-HH.MM.SS.ffffff",
    "YYYY-MM-DDTHH:MM:SS.ffffff",
    "YYYY-MM-DD HH:MM:SS.ffffff",
)
_TIMESTAMP_SHAPES = (
    re.compile(
        r"\A([0-9]{4})-([0-9]{2})-([0-9]{2})-([0-9]{2})\.([0-9]{2})\.([0-9]{2})"
        r"(?:\.([0-9]{1,6}))?\Z"
    ),
    re.compile(
        r"\A([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})"
        r"(?:\.([0-9]{1,6}))?\Z"
    ),
    re.compile(
        r"\A([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})"
        r"(?:\.([0-9]{1,6}))?\Z"
    ),
)
TIMESTAMP_FRACTION_DIGITS = 6



# --------------------------------------------------------------------------
# Diagnostics
# --------------------------------------------------------------------------
class DiffError(Exception):
    """Diagnostic raised by this module, carrying the status to return."""

    exit_status = EXIT_CONFIGURATION


class ConfigurationError(DiffError):
    """A setting, an option, an adapter or the field map was refused."""

    exit_status = EXIT_CONFIGURATION


class HarnessInputError(DiffError):
    """A harness input is absent, incomplete or inconsistent."""

    exit_status = EXIT_HARNESS_INPUT


class WarehouseError(DiffError):
    """The warehouse answered and its content was refused."""

    exit_status = EXIT_WAREHOUSE_REFUSED


def _printable(text: str) -> str:
    """Return ``text`` with every character a terminal would act on replaced."""
    return "".join(character if character.isprintable() else "?" for character in text)


def _shown(value: str, limit: int = 120) -> str:
    """Return ``value`` printable, quoted and cut to ``limit`` characters."""
    rendered = _printable(value)
    if len(rendered) > limit:
        rendered = f"{rendered[:limit]}...({len(value)} characters)"
    return f"[{rendered}]"


def _path_shown(path: Path) -> str:
    """Return ``path`` relative to the repository root where it lies inside it."""
    try:
        return _printable(str(path.resolve().relative_to(REPO_ROOT)))
    except ValueError:
        return _printable(str(path))


def _quote_all(values: Iterable[str]) -> str:
    """Return ``values`` as a comma-separated list of quoted items."""
    return ", ".join(_shown(str(value)) for value in values)


def _worst_status(statuses: Iterable[int]) -> int:
    """Return the status of ``statuses`` that stands first in _EXIT_PRECEDENCE."""
    collected = set(statuses)
    for status in _EXIT_PRECEDENCE:
        if status in collected:
            return status
    return EXIT_OK


def _resolved(value: str | os.PathLike[str]) -> Path:
    """Return ``value`` as an absolute path, resolved against the repository root."""
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return Path(os.path.normpath(str(path)))


def _environment_value(name: str) -> str | None:
    """Return the environment value of ``name``, or None when it is unset or blank.

    A variable holding the empty string or whitespace alone counts as unset, which
    is the empty-value resolution every command-line tool of this bridge applies.
    """
    raw = os.environ.get(name)
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped or None


def _read_text(path: Path, what: str, status: type[DiffError]) -> str:
    """Return the text of ``path``, refusing an absent or undecodable file."""
    try:
        size = path.stat().st_size
    except FileNotFoundError as error:
        raise status(f"the {what} is not present at {_path_shown(path)}") from error
    except OSError as error:
        raise status(
            f"the {what} at {_path_shown(path)} cannot be examined: "
            f"{_printable(error.strerror or type(error).__name__)}"
        ) from error
    if size > MAX_INPUT_BYTES:
        raise status(
            f"the {what} at {_path_shown(path)} holds {size} bytes, beyond the "
            f"{MAX_INPUT_BYTES} bytes this tool reads"
        )
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise status(
            f"the {what} at {_path_shown(path)} is not UTF-8 text at byte "
            f"{error.start}"
        ) from error
    except OSError as error:
        raise status(
            f"the {what} at {_path_shown(path)} cannot be read: "
            f"{_printable(error.strerror or type(error).__name__)}"
        ) from error


def _first_line(error: BaseException) -> str:
    """Return the first line of ``error``, or its class name when it has none."""
    text = str(error).splitlines()
    return _printable(text[0]) if text and text[0] else type(error).__name__


def _without_one_trailing_line_ending(text: str) -> str:
    """Return ``text`` without one trailing line ending, and no more than one."""
    if text.endswith("\r\n"):
        return text[:-2]
    if text.endswith(("\n", "\r")):
        return text[:-1]
    return text


# --------------------------------------------------------------------------
# Field map
# --------------------------------------------------------------------------
class Window(NamedTuple):
    """One COMMAREA item as the field map's layout section declares it."""

    item: str
    pic: str
    offset: int
    length: int
    kind: str
    copybook: str
    line: int

    @property
    def locator(self) -> str:
        """Return the ``path:line`` locator of this declaration."""
        return f"{self.copybook}:{self.line}"

    @property
    def byte_range(self) -> str:
        """Return the 1-based inclusive byte range this item occupies."""
        return f"{self.offset}-{self.offset + self.length - 1}"


class TargetColumn(NamedTuple):
    """One canonical column a logical field entry supplies."""

    relation: str
    column: str
    type_text: str
    nullable: bool


class FieldEntry(NamedTuple):
    """One logical field entry of the field map, with its locators and targets."""

    logical_entry: str
    concept: str
    runtime_status: str
    populated_by: str | None
    applicable_policy_types: tuple[str, ...]
    commarea_item: str | None
    commarea_locator: str | None
    db2_item: str | None
    db2_locator: str | None
    evidence: tuple[str, ...]
    targets: tuple[TargetColumn, ...]

    @property
    def cobol_item(self) -> str:
        """Return the COBOL item names this entry is compared through."""
        names = [name for name in (self.commarea_item, self.db2_item) if name]
        return " / ".join(names) if names else "none (warehouse-assigned)"

    @property
    def locator(self) -> str:
        """Return the primary ``path:line`` locator of this entry."""
        for locator in (self.commarea_locator, self.db2_locator):
            if locator:
                return locator
        return "user requirement (no COBOL item supplies it)"


class RelationTarget(NamedTuple):
    """One canonical relation as the field map's targets section declares it."""

    key: str
    schema: str
    alias: str
    columns: tuple[str, ...]
    types: Mapping[str, str]
    nullable: Mapping[str, bool]
    sources: Mapping[str, str]
    unique_key: tuple[str, ...]


class FieldMap(NamedTuple):
    """The metadata spine this tool reads, checked against its own byte grid."""

    path: Path
    record_length: int
    windows: Mapping[str, Window]
    entries: Mapping[str, FieldEntry]
    source_system_entry: FieldEntry
    routing: Mapping[str, str]
    routing_locator: str
    supported_request_ids: tuple[str, ...]
    return_codes: Mapping[str, str]
    relations: Mapping[str, RelationTarget]
    amount_columns: tuple[str, ...]
    populated_amounts: Mapping[str, tuple[str, ...]]
    null_amounts: Mapping[str, tuple[str, ...]]
    declared_tolerance: str

    def window(self, item: str) -> Window:
        """Return the layout window of ``item``, refusing an item the map omits."""
        found = self.windows.get(item.upper())
        if found is None:
            raise ConfigurationError(
                f"the field map at {_path_shown(self.path)} declares no layout item "
                f"{_shown(item)}"
            )
        return found

    def entry(self, logical_entry: str) -> FieldEntry:
        """Return the logical field entry of ``logical_entry``."""
        if logical_entry == self.source_system_entry.logical_entry:
            return self.source_system_entry
        found = self.entries.get(logical_entry)
        if found is None:
            raise ConfigurationError(
                f"the field map at {_path_shown(self.path)} declares no logical field "
                f"entry {_shown(logical_entry)}"
            )
        return found


class _DuplicateRejectingLoader(yaml.SafeLoader):
    """``yaml.SafeLoader`` that refuses a mapping which repeats a key.

    Loading raises ``yaml.constructor.ConstructorError`` naming the repeated key and
    the position it reappears at, rather than resolving that key to its last value.
    A key the loader cannot compare against the keys already seen raises the same
    error class. Every mapping defect reaches the caller as a YAML error, which
    ``load_field_map`` reports with EXIT_CONFIGURATION.
    """

    def construct_mapping(
        self, node: yaml.MappingNode, deep: bool = False
    ) -> dict[Any, Any]:
        """Build one mapping, raising on a repeated key or a key it cannot compare."""
        seen: set[Any] = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in seen
                if not duplicate:
                    seen.add(key)
            except TypeError as error:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found unhashable key of type {type(key).__name__}",
                    key_node.start_mark,
                ) from error
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {_shown(str(key))}",
                    key_node.start_mark,
                )
        return super().construct_mapping(node, deep=deep)

# Shape of an ISO calendar date, applied to the two date windows.
_DATE_SHAPE = re.compile(r"\A([0-9]{4})-([0-9]{2})-([0-9]{2})\Z")

# Names of the normalisations a comparison record reports.
NORM_TRAILING_TRIM = "trailing-space trim"
NORM_INTEGER = "leading-zero-insensitive integer"
NORM_ISO_DATE = "ISO calendar date"
NORM_TIMESTAMP = "Db2 timestamp to microsecond precision"
NORM_DECIMAL = "DISPLAY digits to decimal"
NORM_NONE = "none"



def _mapping_member(container: Any, key: str, where: str) -> Mapping[str, Any]:
    """Return ``container[key]`` as a mapping, naming ``where`` when it is not one."""
    if not isinstance(container, Mapping) or key not in container:
        raise ConfigurationError(
            f"the field map declares no {_shown(f'{where}.{key}' if where else key)} "
            f"member"
        )
    value = container[key]
    if not isinstance(value, Mapping):
        raise ConfigurationError(
            f"the field map records {_shown(f'{where}.{key}' if where else key)} as "
            f"{type(value).__name__}; a mapping is required"
        )
    return value


def _sequence_member(container: Any, key: str, where: str) -> Sequence[Any]:
    """Return ``container[key]`` as a sequence, naming ``where`` when it is not one."""
    if not isinstance(container, Mapping) or key not in container:
        raise ConfigurationError(
            f"the field map declares no {_shown(f'{where}.{key}' if where else key)} "
            f"member"
        )
    value = container[key]
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ConfigurationError(
            f"the field map records {_shown(f'{where}.{key}' if where else key)} as "
            f"{type(value).__name__}; a sequence is required"
        )
    return value


def _text_member(container: Any, key: str, where: str) -> str:
    """Return ``container[key]`` as text, naming ``where`` when it is absent."""
    if not isinstance(container, Mapping) or key not in container:
        raise ConfigurationError(
            f"the field map declares no {_shown(f'{where}.{key}' if where else key)} "
            f"member"
        )
    value = container[key]
    if not isinstance(value, str):
        raise ConfigurationError(
            f"the field map records {_shown(f'{where}.{key}' if where else key)} as "
            f"{type(value).__name__}; text is required"
        )
    return value


def _optional_text(container: Mapping[str, Any], key: str) -> str | None:
    """Return ``container[key]`` as text, or None where it is absent or null."""
    value = container.get(key)
    return value if isinstance(value, str) else None


def _locator(container: Mapping[str, Any] | None) -> str | None:
    """Return the ``path:line`` locator a copybook or file block declares."""
    if not isinstance(container, Mapping):
        return None
    path = _optional_text(container, "copybook") or _optional_text(container, "file")
    line = container.get("line")
    if path is None or not isinstance(line, int):
        return None
    return f"{path}:{line}"


def _layout_windows(document: Mapping[str, Any]) -> dict[str, Window]:
    """Return every layout item of the field map, keyed by its upper-case item name."""
    layout = _mapping_member(document, "layout", "")
    windows: dict[str, Window] = {}
    for group_name in sorted(layout):
        group = _mapping_member(layout, group_name, "layout")
        copybook = _text_member(group, "copybook", f"layout.{group_name}")
        for position, raw in enumerate(
            _sequence_member(group, "items", f"layout.{group_name}")
        ):
            where = f"layout.{group_name}.items[{position}]"
            if not isinstance(raw, Mapping):
                raise ConfigurationError(
                    f"the field map records {_shown(where)} as {type(raw).__name__}; "
                    f"a mapping is required"
                )
            item = _text_member(raw, "item", where)
            offset = raw.get("offset")
            length = raw.get("length")
            line = raw.get("line")
            if not isinstance(offset, int) or not isinstance(length, int):
                raise ConfigurationError(
                    f"the field map records no whole-number offset and length for "
                    f"{_shown(item)} at {_shown(where)}"
                )
            if not isinstance(line, int):
                raise ConfigurationError(
                    f"the field map records no declaration line for {_shown(item)} at "
                    f"{_shown(where)}"
                )
            window = Window(
                item=item,
                pic=_text_member(raw, "pic", where),
                offset=offset,
                length=length,
                kind=_text_member(raw, "kind", where),
                copybook=copybook,
                line=line,
            )
            windows[item.upper()] = window
    return windows


def _field_entries(document: Mapping[str, Any]) -> dict[str, FieldEntry]:
    """Return every logical field entry of the field map, keyed by logical_entry."""
    entries: dict[str, FieldEntry] = {}
    for position, raw in enumerate(_sequence_member(document, "fields", "")):
        where = f"fields[{position}]"
        if not isinstance(raw, Mapping):
            raise ConfigurationError(
                f"the field map records {_shown(where)} as {type(raw).__name__}; a "
                f"mapping is required"
            )
        entry = _read_entry(raw, where)
        if entry.logical_entry in entries:
            raise ConfigurationError(
                f"the field map declares the logical field entry "
                f"{_shown(entry.logical_entry)} twice"
            )
        entries[entry.logical_entry] = entry
    return entries


def _read_entry(raw: Mapping[str, Any], where: str) -> FieldEntry:
    """Return one logical field entry read from the mapping at ``where``."""
    commarea = raw.get("commarea")
    db2 = raw.get("db2_declaration")
    targets: list[TargetColumn] = []
    for position, target in enumerate(raw.get("targets") or ()):
        target_where = f"{where}.targets[{position}]"
        if not isinstance(target, Mapping):
            raise ConfigurationError(
                f"the field map records {_shown(target_where)} as "
                f"{type(target).__name__}; a mapping is required"
            )
        nullable = target.get("nullable")
        if not isinstance(nullable, bool):
            raise ConfigurationError(
                f"the field map records no nullable flag at {_shown(target_where)}"
            )
        targets.append(
            TargetColumn(
                relation=_text_member(target, "relation", target_where),
                column=_text_member(target, "column", target_where),
                type_text=_text_member(target, "type", target_where),
                nullable=nullable,
            )
        )
    policy_types = tuple(
        str(value) for value in (raw.get("applicable_policy_types") or ())
    )
    evidence = tuple(str(value) for value in (raw.get("evidence") or ()))
    return FieldEntry(
        logical_entry=_text_member(raw, "logical_entry", where),
        concept=_optional_text(raw, "concept") or "",
        runtime_status=_text_member(raw, "runtime_status", where),
        populated_by=_optional_text(raw, "populated_by"),
        applicable_policy_types=policy_types,
        commarea_item=(
            _optional_text(commarea, "item") if isinstance(commarea, Mapping) else None
        ),
        commarea_locator=_locator(commarea if isinstance(commarea, Mapping) else None),
        db2_item=(_optional_text(db2, "item") if isinstance(db2, Mapping) else None),
        db2_locator=_locator(db2 if isinstance(db2, Mapping) else None),
        evidence=evidence,
        targets=tuple(targets),
    )


def _relation_targets(document: Mapping[str, Any]) -> dict[str, RelationTarget]:
    """Return the canonical relations the field map's targets section declares."""
    targets = _mapping_member(document, "targets", "")
    relations: dict[str, RelationTarget] = {}
    for key in RELATION_KEYS:
        block = _mapping_member(targets, key, "targets")
        columns: list[str] = []
        types: dict[str, str] = {}
        nullable: dict[str, bool] = {}
        sources: dict[str, str] = {}
        for position, raw in enumerate(
            _sequence_member(block, "columns", f"targets.{key}")
        ):
            where = f"targets.{key}.columns[{position}]"
            if not isinstance(raw, Mapping):
                raise ConfigurationError(
                    f"the field map records {_shown(where)} as {type(raw).__name__}; "
                    f"a mapping is required"
                )
            name = _text_member(raw, "name", where)
            flag = raw.get("nullable")
            if not isinstance(flag, bool):
                raise ConfigurationError(
                    f"the field map records no nullable flag at {_shown(where)}"
                )
            columns.append(name)
            types[name] = _text_member(raw, "type", where)
            nullable[name] = flag
            sources[name] = _text_member(raw, "source", where)
        relations[key] = RelationTarget(
            key=key,
            schema=_text_member(block, "schema", f"targets.{key}"),
            alias=_text_member(block, "alias", f"targets.{key}"),
            columns=tuple(columns),
            types=types,
            nullable=nullable,
            sources=sources,
            unique_key=tuple(
                str(value)
                for value in _sequence_member(block, "unique_key", f"targets.{key}")
            ),
        )
    return relations


def _premium_nullability(
    document: Mapping[str, Any],
) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    """Return the populated and null amount columns of each policy type."""
    section = _mapping_member(document, "product_premium_nullability", "")
    always = tuple(
        str(value)
        for value in _sequence_member(
            section, "always_populated", "product_premium_nullability"
        )
    )
    if section.get("zero_substitution_permitted") is not False:
        raise ConfigurationError(
            "the field map does not record "
            "product_premium_nullability.zero_substitution_permitted as false; this "
            "tool compares an inapplicable product premium against NULL alone"
        )
    by_policy_type = _mapping_member(
        section, "by_policy_type", "product_premium_nullability"
    )
    populated: dict[str, tuple[str, ...]] = {}
    empty: dict[str, tuple[str, ...]] = {}
    for policy_type in sorted(by_policy_type):
        where = f"product_premium_nullability.by_policy_type.{policy_type}"
        block = _mapping_member(by_policy_type, policy_type, where)
        populated[policy_type] = always + tuple(
            str(value) for value in (block.get("populated") or ())
        )
        empty[policy_type] = tuple(
            str(value) for value in (block.get("null_fields") or ())
        )
    return populated, empty



def load_field_map(path: Path) -> FieldMap:
    """Return the field map at ``path``, checked against the byte grid of this module.

    The document is parsed with a loader that refuses a repeated mapping key, then
    every section this tool reads is extracted: the record length, the layout
    windows, the seventeen logical field entries and the warehouse-assigned entry,
    the request routing, the return codes, the two canonical relations with their
    column order and types, the six amount columns, the product premium
    nullability and the declared comparison tolerance.

    The extracted map is then held to the independently verified facts this module
    carries: ``COMMAREA_RECORD_LENGTH``, every entry of ``VERIFIED_WINDOWS`` with
    its PICTURE, offset and length, ``VERIFIED_ROUTING``, ``VERIFIED_RETURN_CODES``,
    the declared column names and order of both relations and the value of
    ``AMOUNT_TOLERANCE``. A disagreement raises ``ConfigurationError``, naming the
    item and both values.
    """
    text = _read_text(path, "field map", ConfigurationError)
    try:
        document = yaml.load(text, Loader=_DuplicateRejectingLoader)
    except yaml.YAMLError as error:
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} is not a YAML document this tool "
            f"can read: {_printable(str(error).splitlines()[0] if str(error) else '')}"
        ) from error
    if not isinstance(document, Mapping):
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} does not hold a mapping at its root"
        )

    record = _mapping_member(document, "record", "")
    record_length = record.get("length")
    if record_length != COMMAREA_RECORD_LENGTH:
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} records record.length "
            f"{_shown(str(record_length))}; this tool reads a record of "
            f"{COMMAREA_RECORD_LENGTH} characters"
        )

    windows = _layout_windows(document)
    for item, pic, offset, length in VERIFIED_WINDOWS:
        declared = windows.get(item.upper())
        if declared is None:
            raise ConfigurationError(
                f"the field map at {_path_shown(path)} declares no layout item "
                f"{_shown(item)}, which this tool reads at bytes "
                f"{offset}-{offset + length - 1}"
            )
        if (declared.pic, declared.offset, declared.length) != (pic, offset, length):
            raise ConfigurationError(
                f"the field map at {_path_shown(path)} declares {_shown(item)} as PIC "
                f"{declared.pic} at bytes {declared.byte_range}; this tool reads it as "
                f"PIC {pic} at bytes {offset}-{offset + length - 1}"
            )

    entries = _field_entries(document)
    source_block = _mapping_member(document, "source_system_key", "")
    source_entry = _read_entry(source_block, "source_system_key")

    routing_block = _mapping_member(document, "request_routing", "")
    routing_map = _mapping_member(routing_block, "map", "request_routing")
    routing = {
        str(request_id): _text_member(
            _mapping_member(routing_map, str(request_id), "request_routing.map"),
            "policy_type",
            f"request_routing.map.{request_id}",
        )
        for request_id in sorted(routing_map)
    }
    if routing != VERIFIED_ROUTING:
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} records the request routing "
            f"{_shown(str(sorted(routing.items())))}; this tool reads the routing of "
            f"base/src/lgapdb01.cbl:184-207 as "
            f"{_shown(str(sorted(VERIFIED_ROUTING.items())))}"
        )
    routing_locator = (
        _optional_text(routing_block, "evaluate_range")
        or "base/src/lgapdb01.cbl:184-207"
    )

    supported = tuple(
        str(value)
        for value in _sequence_member(document, "supported_request_ids", "")
    )
    if tuple(sorted(supported)) != tuple(sorted(SUPPORTED_CASES)):
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} records the supported request ids "
            f"{_quote_all(supported)}; this tool compares {_quote_all(SUPPORTED_CASES)}"
        )

    codes_block = _mapping_member(document, "return_codes", "")
    return_codes = {
        str(code): _optional_text(
            _mapping_member(codes_block, str(code), "return_codes"), "meaning"
        )
        or ""
        for code in sorted(codes_block)
    }
    if tuple(sorted(return_codes)) != tuple(sorted(VERIFIED_RETURN_CODES)):
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} records the return codes "
            f"{_quote_all(sorted(return_codes))}; the named chain sets "
            f"{_quote_all(VERIFIED_RETURN_CODES)}"
        )

    relations = _relation_targets(document)
    for key, relation in relations.items():
        declared = DECLARED_RELATIONS.get(relation.alias)
        if relation.schema != CANONICAL_SCHEMA or declared is None:
            raise ConfigurationError(
                f"the field map at {_path_shown(path)} declares relation {_shown(key)} "
                f"as {_shown(f'{relation.schema}.{relation.alias}')}; this tool "
                f"compares {_quote_all(RELATION_KEYS)}"
            )
        if relation.columns != declared:
            raise ConfigurationError(
                f"the field map at {_path_shown(path)} declares the columns of "
                f"{_shown(key)} as {_quote_all(relation.columns)}; this tool compares "
                f"{_quote_all(declared)} in that order"
            )

    comparison = _mapping_member(document, "comparison", "")
    amount_columns = tuple(
        str(value)
        for value in _sequence_member(comparison, "amount_fields", "comparison")
    )
    rating = relations[RELATION_KEYS[1]]
    for column in amount_columns:
        if column not in rating.columns:
            raise ConfigurationError(
                f"the field map at {_path_shown(path)} names the amount column "
                f"{_shown(column)}, which {_shown(rating.key)} does not declare"
            )
    if comparison.get("skipped_fields_permitted") is not False:
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} does not record "
            f"comparison.skipped_fields_permitted as false; this tool compares every "
            f"canonical column of both relations"
        )
    # The declared threshold is compared as text; AMOUNT_TOLERANCE is the only value
    # any amount comparison applies.
    declared_tolerance = str(comparison.get("amount_tolerance_abs"))
    try:
        if Decimal(declared_tolerance) != AMOUNT_TOLERANCE:
            raise ConfigurationError(
                f"the field map at {_path_shown(path)} records the amount tolerance "
                f"{_shown(declared_tolerance)}; this tool applies "
                f"{_shown(str(AMOUNT_TOLERANCE))}"
            )
    except InvalidOperation as error:
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} records the amount tolerance "
            f"{_shown(declared_tolerance)}, which is not a decimal value"
        ) from error

    populated, empty = _premium_nullability(document)
    return FieldMap(
        path=path,
        record_length=COMMAREA_RECORD_LENGTH,
        windows=windows,
        entries=entries,
        source_system_entry=source_entry,
        routing=routing,
        routing_locator=routing_locator,
        supported_request_ids=supported,
        return_codes=return_codes,
        relations=relations,
        amount_columns=amount_columns,
        populated_amounts=populated,
        null_amounts=empty,
        declared_tolerance=declared_tolerance,
    )


# --------------------------------------------------------------------------
# Harness inputs
# --------------------------------------------------------------------------
class HarnessCase(NamedTuple):
    """The three harness inputs of one case, with the paths they were read from."""

    case: str
    fixture: str
    captures: Mapping[str, str]
    captures_path: Path
    commarea: str
    commarea_path: Path
    sample: str | None
    sample_path: Path | None
    sample_source: str


def parse_captures(path: Path) -> dict[str, str]:
    """Return the ``NAME=VALUE`` capture file at ``path`` as a mapping.

    Each line is read to the first ``=`` alone, so a value carrying that character
    stays intact. Trailing whitespace of a value, which a fixed-width COBOL DISPLAY
    leaves, is removed and the name is stripped. A blank line and a line whose first
    non-blank character is ``#`` are passed over. A line carrying no ``=``, a line
    carrying an empty name and a name that appears twice each raise
    ``HarnessInputError`` naming the line number.
    """
    text = _read_text(path, "capture file", HarnessInputError)
    captures: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in line:
            raise HarnessInputError(
                f"line {number} of the capture file at {_path_shown(path)} carries no "
                f"'=' and is not a NAME=VALUE record: {_shown(line)}"
            )
        name, _, value = line.partition("=")
        name = name.strip()
        if not name:
            raise HarnessInputError(
                f"line {number} of the capture file at {_path_shown(path)} carries an "
                f"empty capture name"
            )
        if name in captures:
            raise HarnessInputError(
                f"the capture file at {_path_shown(path)} carries the key "
                f"{_shown(name)} twice, at line {number} and earlier"
            )
        captures[name] = value.rstrip()
    if not captures:
        raise HarnessInputError(
            f"the capture file at {_path_shown(path)} carries no NAME=VALUE record"
        )
    return captures


def read_record(path: Path, what: str, record_length: int) -> str:
    """Return the fixed-width record at ``path``, refusing any other width.

    One trailing line ending is removed, and no more than one. The remaining text
    must hold exactly ``record_length`` characters; any other width raises
    ``HarnessInputError`` naming both widths.
    """
    text = _without_one_trailing_line_ending(
        _read_text(path, what, HarnessInputError)
    )
    if len(text) != record_length:
        raise HarnessInputError(
            f"the {what} at {_path_shown(path)} holds {len(text)} characters after one "
            f"trailing line ending is removed; {record_length} are required"
        )
    return text



def slice_window(record: str, window: Window, what: str) -> str:
    """Return the characters ``window`` declares out of ``record``.

    ``window.offset`` is 1-based, as the field map declares it. A window reaching
    beyond the record raises ``HarnessInputError`` naming the item and both widths.
    """
    start = window.offset - 1
    end = start + window.length
    if end > len(record):
        raise HarnessInputError(
            f"{window.item} occupies bytes {window.byte_range} of the {what}, which "
            f"holds {len(record)} characters"
        )
    return record[start:end]


def derive_policy_type(request_id: str, field_map: FieldMap) -> str:
    """Return the policy-type letter the request routing assigns to ``request_id``.

    The routing is the EVALUATE of base/src/lgapdb01.cbl:184-207 as the field map
    records it. A request id the routing does not carry raises ``HarnessInputError``
    naming the ids it does.
    """
    trimmed = request_id.strip()
    letter = field_map.routing.get(trimmed)
    if letter is None:
        raise HarnessInputError(
            f"the request id {_shown(trimmed)} matches no branch of the request "
            f"routing at {field_map.routing_locator}, which carries "
            f"{_quote_all(sorted(field_map.routing))}"
        )
    return letter


# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------
def _normalise_text(raw: str) -> str:
    """Return ``raw`` with trailing spaces of the fixed-width window removed."""
    return raw.rstrip()


def _normalise_char(raw: str) -> str:
    """Return ``raw`` with surrounding spaces removed."""
    return raw.strip()


def _normalise_integer(raw: str) -> int:
    """Return ``raw`` as an integer, reading a zero-padded DISPLAY window."""
    text = raw.strip()
    if not text or not text.isdigit():
        raise ValueError(f"{_shown(raw)} does not hold decimal digits alone")
    return int(text)


def _normalise_date(raw: str) -> datetime.date:
    """Return ``raw`` as a calendar date, accepting the ISO form YYYY-MM-DD alone."""
    text = raw.strip()
    matched = _DATE_SHAPE.fullmatch(text)
    if matched is None:
        raise ValueError(f"{_shown(raw)} is not an ISO date of the form YYYY-MM-DD")
    year, month, day = (int(part) for part in matched.groups())
    try:
        return datetime.date(year, month, day)
    except ValueError as error:
        raise ValueError(f"{_shown(raw)} is not a calendar date: {error}") from error


def _normalise_timestamp(raw: str) -> datetime.datetime:
    """Return ``raw`` as a moment at microsecond precision.

    The Db2 character form YYYY-MM-DD-HH.MM.SS.ffffff the chain reads back at
    base/src/lgapdb01.cbl:315-321 is accepted, as are the ISO forms with a ``T``
    and with a space separator. A fractional part of one to six digits, and no
    fractional part at all, are both accepted and neither is rounded.
    """
    text = raw.strip()
    for shape in _TIMESTAMP_SHAPES:
        matched = shape.fullmatch(text)
        if matched is None:
            continue
        year, month, day, hour, minute, second = (
            int(part) for part in matched.groups()[:6]
        )
        fraction = matched.group(7) or ""
        try:
            # The Db2 character timestamp carries no zone and is compared as the
            # naive moment it states.
            return datetime.datetime(  # noqa: DTZ001
                year,
                month,
                day,
                hour,
                minute,
                second,
                int(fraction.ljust(TIMESTAMP_FRACTION_DIGITS, "0") or "0"),
            )
        except ValueError as error:
            raise ValueError(
                f"{_shown(raw)} is not a calendar moment: {error}"
            ) from error
    raise ValueError(
        f"{_shown(raw)} matches none of the accepted timestamp forms "
        f"{_quote_all(TIMESTAMP_INPUT_FORMATS)}"
    )


def _normalise_amount(raw: str) -> Decimal:
    """Return ``raw`` as a decimal amount read from its DISPLAY digits.

    The window holds unsigned digits without an implied decimal, so ``000480``
    yields ``Decimal("480")``. No binary float is constructed on this path.
    """
    text = raw.strip()
    if not text or not text.isdigit():
        raise ValueError(f"{_shown(raw)} does not hold decimal digits alone")
    return Decimal(text)


_HARNESS_NORMALISERS = {
    KIND_TEXT: (_normalise_text, NORM_TRAILING_TRIM),
    KIND_CHAR: (_normalise_char, NORM_TRAILING_TRIM),
    KIND_INTEGER: (_normalise_integer, NORM_INTEGER),
    KIND_DATE: (_normalise_date, NORM_ISO_DATE),
    KIND_TIMESTAMP: (_normalise_timestamp, NORM_TIMESTAMP),
    KIND_AMOUNT: (_normalise_amount, NORM_DECIMAL),
}


def _warehouse_comparable(kind: str, value: Any) -> Any:
    """Return the warehouse ``value`` in the comparable form of ``kind``.

    Both adapters are accepted: a value already carried as ``int``, ``Decimal``,
    ``datetime.date`` or ``datetime.datetime`` is used as it stands, and a value
    carried as text is read through the same normalisation the harness side applies.
    """
    if kind == KIND_TEXT:
        return _normalise_text(str(value))
    if kind == KIND_CHAR:
        return _normalise_char(str(value))
    if kind == KIND_INTEGER:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, Decimal):
            if value != value.to_integral_value():
                raise ValueError(f"{_shown(str(value))} is not a whole number")
            return int(value)
        return _normalise_integer(str(value))
    if kind == KIND_DATE:
        if isinstance(value, datetime.datetime):
            if value.time() != datetime.time():
                raise ValueError(
                    f"{_shown(value.isoformat())} carries a time of day where a date "
                    f"is declared"
                )
            return value.date()
        if isinstance(value, datetime.date):
            return value
        return _normalise_date(str(value))
    if kind == KIND_TIMESTAMP:
        if isinstance(value, datetime.datetime):
            return value.replace(tzinfo=None) if value.tzinfo is None else value
        if isinstance(value, datetime.date):
            # A warehouse date read where a timestamp is declared is compared as the
            # naive midnight of that day.
            return datetime.datetime(value.year, value.month, value.day)  # noqa: DTZ001
        return _normalise_timestamp(str(value))
    if kind == KIND_AMOUNT:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            return Decimal(value)
        return Decimal(str(value).strip())
    raise ValueError(f"no comparable form is defined for kind {_shown(kind)}")


def _render(value: Any) -> str:
    """Return ``value`` as the text the reports carry."""
    if value is None:
        return "NULL"
    if isinstance(value, datetime.datetime):
        return value.isoformat(sep=" ", timespec="microseconds")
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def _amount_scale(value: Decimal) -> int | None:
    """Return the number of decimal places ``value`` carries, or None when it has no
    finite exponent."""
    exponent = value.as_tuple().exponent
    if not isinstance(exponent, int):
        return None
    return -exponent if exponent < 0 else 0



# --------------------------------------------------------------------------
# Comparison records
# --------------------------------------------------------------------------
class Witness(NamedTuple):
    """One harness authority for one column, and the value it carried.

    ``family`` names where the value came from: ``commarea`` for a window of the
    returned COMMAREA, ``capture`` for a capture-file key, ``driver-input`` for a
    window of the record the driver was handed, ``derived`` for the request-routing
    derivation and ``configured`` for the value the run was invoked with. ``raw``
    is None for an authority that was absent, and ``absent`` then names what was
    absent.
    """

    source: str
    raw: str | None
    absent: str | None = None
    family: str = "capture"
    key: str | None = None

    def as_document(self) -> dict[str, Any]:
        """Return this witness as the JSON report carries it."""
        return {
            "source": self.source,
            "family": self.family,
            "key": self.key,
            "value": self.raw,
            "absent": self.absent,
        }


@dataclass
class Comparison:
    """One canonical column compared, with both values and the verdict."""

    relation: str
    column: str
    kind: str
    cobol_item: str
    locator: str
    evidence: tuple[str, ...] = ()
    witnesses: tuple[Witness, ...] = ()
    harness_value: str | None = None
    warehouse_value: str | None = None
    delta: str | None = None
    normalisations: tuple[str, ...] = ()
    status: str = STATUS_PASS
    notes: tuple[str, ...] = ()
    in_tolerance_anomaly: bool = False
    scale_anomaly: bool = False

    @property
    def passed(self) -> bool:
        """Return True when this comparison did not fail."""
        return self.status in (STATUS_PASS, STATUS_PASS_IN_TOLERANCE)

    @property
    def missing(self) -> bool:
        """Return True when a harness input this column needs was absent."""
        return self.status == STATUS_MISSING

    @property
    def authority(self) -> str:
        """Return the harness authorities this column was compared against."""
        return "; ".join(witness.source for witness in self.witnesses) or "none"

    def fail(self, note: str) -> Comparison:
        """Record ``note`` and mark this comparison failed."""
        self.status = STATUS_FAIL
        self.notes = self.notes + (note,)
        return self

    def miss(self, note: str) -> Comparison:
        """Record ``note`` and mark the harness input of this comparison absent."""
        self.status = STATUS_MISSING
        self.notes = self.notes + (note,)
        return self

    def note(self, note: str) -> Comparison:
        """Record ``note`` without changing the verdict."""
        self.notes = self.notes + (note,)
        return self

    def as_document(self) -> dict[str, Any]:
        """Return this comparison as the JSON report carries it."""
        return {
            "relation": self.relation,
            "column": self.column,
            "kind": self.kind,
            "cobol_item": self.cobol_item,
            "locator": self.locator,
            "evidence": list(self.evidence),
            "harness_authority": self.authority,
            "witnesses": [witness.as_document() for witness in self.witnesses],
            "harness_value": self.harness_value,
            "warehouse_value": self.warehouse_value,
            "delta": self.delta,
            "normalisations": list(self.normalisations),
            "status": self.status,
            "notes": list(self.notes),
            "in_tolerance_anomaly": self.in_tolerance_anomaly,
            "scale_anomaly": self.scale_anomaly,
        }


@dataclass
class Assertion:
    """One assertion outside the canonical columns, with what it observed."""

    group: str
    name: str
    expected: str
    observed: str
    locator: str
    status: str = STATUS_PASS
    notes: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        """Return True when this assertion did not fail."""
        return self.status == STATUS_PASS

    @property
    def missing(self) -> bool:
        """Return True when the capture this assertion reads was absent."""
        return self.status == STATUS_MISSING

    def as_document(self) -> dict[str, Any]:
        """Return this assertion as the JSON report carries it."""
        return {
            "group": self.group,
            "name": self.name,
            "expected": self.expected,
            "observed": self.observed,
            "locator": self.locator,
            "status": self.status,
            "notes": list(self.notes),
        }


@dataclass
class CaseResult:
    """Everything one compared case contributes to the reports."""

    case: str
    fixture: str = ""
    policy_type: str = ""
    request_id: str = ""
    policy_number: int | None = None
    captures_path: str = ""
    commarea_path: str = ""
    sample_path: str = ""
    sample_source: str = ""
    comparisons: list[Comparison] = field(default_factory=list)
    assertions: list[Assertion] = field(default_factory=list)
    snapshot_path: str = ""
    snapshot_state: str = ""
    errors: list[str] = field(default_factory=list)
    statuses: list[int] = field(default_factory=list)

    @property
    def coverage(self) -> str:
        """Return the coverage line of this case."""
        return (
            f"coverage: {len(self.comparisons)}/{CANONICAL_COLUMN_INSTANCES} canonical "
            f"column instances compared"
        )

    @property
    def failed(self) -> list[Comparison]:
        """Return the comparisons of this case that did not pass."""
        return [record for record in self.comparisons if not record.passed]

    @property
    def in_tolerance(self) -> list[Comparison]:
        """Return the comparisons carrying a non-zero delta inside the tolerance."""
        return [record for record in self.comparisons if record.in_tolerance_anomaly]

    @property
    def scale_anomalies(self) -> list[Comparison]:
        """Return the comparisons whose warehouse amount carried another scale."""
        return [record for record in self.comparisons if record.scale_anomaly]

    @property
    def failed_assertions(self) -> list[Assertion]:
        """Return the assertions of this case that did not pass."""
        return [record for record in self.assertions if not record.passed]

    @property
    def exit_status(self) -> int:
        """Return the status this case contributes to the run."""
        collected = list(self.statuses)
        if any(record.missing for record in self.comparisons) or any(
            record.missing for record in self.assertions
        ):
            collected.append(EXIT_HARNESS_INPUT)
        if self.failed or self.failed_assertions:
            collected.append(EXIT_COMPARISON_FAILED)
        return _worst_status(collected or [EXIT_OK])

    @property
    def verdict(self) -> str:
        """Return PASS or FAIL for this case."""
        return "PASS" if self.exit_status == EXIT_OK else "FAIL"

    def as_document(self) -> dict[str, Any]:
        """Return this case as the JSON report carries it."""
        return {
            "case": self.case,
            "fixture": self.fixture,
            "policy_type": self.policy_type,
            "request_id": self.request_id,
            "policy_number": self.policy_number,
            "inputs": {
                "captures": self.captures_path,
                "commarea_post": self.commarea_path,
                "sample_record": self.sample_path,
                "sample_record_source": self.sample_source,
            },
            "snapshot": {"path": self.snapshot_path, "state": self.snapshot_state},
            "coverage": {
                "compared": len(self.comparisons),
                "expected": CANONICAL_COLUMN_INSTANCES,
                "line": self.coverage,
            },
            "comparisons": [record.as_document() for record in self.comparisons],
            "assertions": [record.as_document() for record in self.assertions],
            "errors": list(self.errors),
            "verdict": self.verdict,
            "exit_status": self.exit_status,
        }



# --------------------------------------------------------------------------
# Column comparison
# --------------------------------------------------------------------------
def comparison_kind(column: str, type_text: str, field_map: FieldMap) -> str:
    """Return the comparison kind of ``column`` from its declared canonical type."""
    if column in field_map.amount_columns:
        return KIND_AMOUNT
    declared = type_text.strip().upper()
    if declared.startswith("BIGINT"):
        return KIND_INTEGER
    if declared.startswith("TIMESTAMP"):
        return KIND_TIMESTAMP
    if declared.startswith("DATE"):
        return KIND_DATE
    if declared == "CHAR(1)":
        return KIND_CHAR
    return KIND_TEXT


def _capture_key_of(item: str) -> str:
    """Return the capture-file key the driver writes for COMMAREA item ``item``."""
    return item.upper().replace("-", "_")


def _capture_witness(
    captures: Mapping[str, str], key: str, description: str
) -> Witness:
    """Return the witness of capture key ``key``, absent when the file omits it."""
    if key not in captures:
        return Witness(
            source=f"{description} (capture key {key})",
            raw=None,
            absent=f"the capture file carries no key {key}",
            key=key,
        )
    return Witness(
        source=f"{description} (capture key {key})", raw=captures[key], key=key
    )


def _sql_capture_witness(
    entry: FieldEntry, captures: Mapping[str, str]
) -> Witness | None:
    """Return the SQL capture witness of ``entry``, or None when it has none."""
    key = SQL_CAPTURE_KEYS.get(entry.logical_entry)
    if key is None:
        return None
    family = "SQL capture"
    for prefix, description in SQL_CAPTURE_FAMILIES.items():
        if key.startswith(f"{prefix}_"):
            family = description
            break
    return _capture_witness(captures, key, family)


def _column_witnesses(
    entry: FieldEntry,
    harness: HarnessCase,
    field_map: FieldMap,
    source_system_key: str,
) -> tuple[Witness, ...]:
    """Return every harness authority that carries the column ``entry`` supplies.

    A COMMAREA item contributes the window of the returned record and the capture
    the driver echoed it into. An item the request supplies contributes the same
    window of the record the driver was handed. An entry with an SQL capture
    contributes that capture. policy_type contributes the request-routing
    derivation and the captured DB2-POLICYTYPE; source_system_key contributes the
    value the run was invoked with.
    """
    if entry.logical_entry == field_map.source_system_entry.logical_entry:
        return (
            Witness(
                source="configured run value (--source-system-key)",
                raw=source_system_key,
                family="configured",
            ),
        )
    witnesses: list[Witness] = []
    if entry.logical_entry == "policy_type":
        request_window = field_map.window("CA-REQUEST-ID")
        request_id = slice_window(
            harness.commarea, request_window, "returned COMMAREA"
        ).strip()
        witnesses.append(
            Witness(
                source=(
                    f"request routing derivation from CA-REQUEST-ID "
                    f"[{field_map.routing_locator}]"
                ),
                raw=derive_policy_type(request_id, field_map),
                family="derived",
            )
        )
    elif entry.commarea_item:
        window = field_map.window(entry.commarea_item)
        witnesses.append(
            Witness(
                source=(
                    f"returned COMMAREA bytes {window.byte_range} "
                    f"({window.item})"
                ),
                raw=slice_window(harness.commarea, window, "returned COMMAREA"),
                family="commarea",
                key=window.item,
            )
        )
        witnesses.append(
            _capture_witness(
                harness.captures,
                _capture_key_of(window.item),
                "returned COMMAREA capture",
            )
        )
        if entry.populated_by == "request":
            if harness.sample is None:
                witnesses.append(
                    Witness(
                        source=f"driver input bytes {window.byte_range}",
                        raw=None,
                        absent=(
                            f"the record the driver was handed was not read: "
                            f"{harness.sample_source}"
                        ),
                        family="driver-input",
                        key=window.item,
                    )
                )
            else:
                witnesses.append(
                    Witness(
                        source=f"driver input bytes {window.byte_range}",
                        raw=slice_window(harness.sample, window, "driver input"),
                        family="driver-input",
                        key=window.item,
                    )
                )
    sql_witness = _sql_capture_witness(entry, harness.captures)
    if sql_witness is not None:
        witnesses.append(sql_witness)
    return tuple(witnesses)


def _compare_null_expected(record: Comparison, warehouse_value: Any) -> Comparison:
    """Compare a column the policy type populates with no value against NULL."""
    record.harness_value = None
    record.warehouse_value = _render(warehouse_value)
    if warehouse_value is None:
        return record.note(
            "the policy type of this case populates no value for this column and the "
            "warehouse carries NULL"
        )
    try:
        numeric = _warehouse_comparable(KIND_AMOUNT, warehouse_value)
    except (ValueError, ArithmeticError):
        numeric = None
    if numeric is not None and numeric == 0:
        return record.fail(
            "zero instead of NULL: the policy type of this case populates no value "
            "for this column, and a zero stands in it"
        )
    return record.fail(
        "the policy type of this case populates no value for this column, and "
        f"{_shown(record.warehouse_value)} stands in it"
    )


def _compare_amount(
    record: Comparison, harness: Decimal, warehouse: Decimal
) -> Comparison:
    """Compare one amount, classifying the delta against AMOUNT_TOLERANCE."""
    delta = abs(warehouse - harness)
    record.delta = format(delta, "f")
    scale = _amount_scale(warehouse)
    record.note(f"warehouse scale {scale if scale is not None else 'not finite'}")
    if scale != AMOUNT_SCALE:
        record.scale_anomaly = True
        record.note(
            f"the warehouse amount carries scale "
            f"{scale if scale is not None else 'not finite'} where the canonical type "
            f"declares {AMOUNT_SCALE}"
        )
    if delta == 0:
        return record
    if delta <= AMOUNT_TOLERANCE:
        record.status = STATUS_PASS_IN_TOLERANCE
        record.in_tolerance_anomaly = True
        return record.note(
            f"the delta {record.delta} is not zero and is within the tolerance "
            f"{AMOUNT_TOLERANCE}"
        )
    return record.fail(
        f"the delta {record.delta} is above the tolerance {AMOUNT_TOLERANCE}"
    )


def _compare_column(
    record: Comparison, warehouse_value: Any, *, nullable: bool
) -> Comparison:
    """Compare every harness authority of ``record`` with the warehouse value.

    An absent authority marks the column MISSING. Authorities that disagree with
    one another fail the column and every value read is named. The remaining
    comparison is exact for every kind but an amount, which is classified against
    AMOUNT_TOLERANCE. A window that holds spaces alone in a nullable column is
    compared against NULL, and the value of every other authority is recorded.
    """
    if record.kind == KIND_NULL_EXPECTED:
        return _compare_null_expected(record, warehouse_value)

    absent = [witness for witness in record.witnesses if witness.raw is None]
    if absent or not record.witnesses:
        record.warehouse_value = _render(warehouse_value)
        if not record.witnesses:
            return record.miss("no harness authority carries this column")
        for witness in absent:
            record.miss(f"{witness.source} is absent: {witness.absent}")
        return record

    normaliser, normalisation = _HARNESS_NORMALISERS[record.kind]
    record.normalisations = record.normalisations + (normalisation,)

    blank = [
        witness
        for witness in record.witnesses
        if witness.family == "commarea" and (witness.raw or "").strip() == ""
    ]
    if blank and nullable:
        record.normalisations = record.normalisations + ("blank window lands null",)
        record.harness_value = None
        record.warehouse_value = _render(warehouse_value)
        for witness in record.witnesses:
            record.note(f"{witness.source} carried {_shown(witness.raw or '')}")
        if warehouse_value is None:
            return record.note(
                "the COMMAREA window holds spaces alone and the warehouse carries NULL"
            )
        return record.fail(
            "the COMMAREA window holds spaces alone and the warehouse carries "
            f"{_shown(record.warehouse_value)}"
        )

    comparable: dict[str, Any] = {}
    for witness in record.witnesses:
        try:
            comparable[witness.source] = normaliser(witness.raw or "")
        except ValueError as error:
            record.harness_value = _shown(witness.raw or "")
            record.warehouse_value = _render(warehouse_value)
            return record.fail(f"{witness.source} carried {error}")

    values = list(comparable.values())
    first = values[0]
    if any(value != first for value in values[1:]):
        record.harness_value = "; ".join(
            f"{source} {_render(value)}" for source, value in comparable.items()
        )
        record.warehouse_value = _render(warehouse_value)
        return record.fail(
            "the harness authorities disagree, so no single harness value stands for "
            "this column"
        )

    record.harness_value = _render(first)
    if warehouse_value is None:
        record.warehouse_value = "NULL"
        return record.fail(
            "the warehouse carries NULL where the harness carries "
            f"{_shown(record.harness_value)}"
        )
    try:
        warehouse = _warehouse_comparable(record.kind, warehouse_value)
    except (ValueError, ArithmeticError) as error:
        record.warehouse_value = _shown(str(warehouse_value))
        return record.fail(f"the warehouse value is not comparable: {error}")
    record.warehouse_value = _render(warehouse)

    if record.kind == KIND_AMOUNT:
        return _compare_amount(record, first, warehouse)
    if warehouse == first:
        return record
    return record.fail(
        f"the warehouse carries {_shown(record.warehouse_value)} where the harness "
        f"carries {_shown(record.harness_value)}"
    )



# --------------------------------------------------------------------------
# Warehouse access
# --------------------------------------------------------------------------
# Every statement below is written with "?" parameter markers and carries no value
# in its text. Warehouse.query replaces the marker with the one the open adapter
# uses, so one statement serves both adapters. The only identifiers composed into
# a statement are the schema, relation and column names of DECLARED_RELATIONS.
_INVENTORY_TABLES_SQL = (
    "select table_name from information_schema.tables where table_schema = ?"
)
_INVENTORY_COLUMNS_SQL = (
    "select table_name, column_name, ordinal_position "
    "from information_schema.columns where table_schema = ? "
    "order by table_name, ordinal_position"
)


class Warehouse:
    """One open warehouse connection, with the paramstyle of its adapter."""

    def __init__(
        self,
        target: str,
        connection: Any,
        adapter: str,
        adapter_version: str,
        identity: str,
    ) -> None:
        self.target = target
        self.adapter = adapter
        self.adapter_version = adapter_version
        self.identity = identity
        self._connection = connection
        self._marker = PARAMETER_MARKERS[target]

    @property
    def local_substitute(self) -> bool:
        """Return True when this connection addresses the local substitute."""
        return self.target == TARGET_DUCKDB

    def query(self, statement: str, parameters: Sequence[Any] = ()) -> list[tuple]:
        """Return every row of ``statement``, executed with ``parameters`` bound.

        The ``?`` markers of ``statement`` are replaced with the marker of the open
        adapter and every value is bound through the driver, so no value is composed
        into SQL text. A failure raises ``WarehouseError`` carrying the statement as
        it was written.
        """
        prepared = statement.replace("?", self._marker)
        try:
            cursor = self._connection.cursor()
        except Exception as error:  # the adapter's own failure
            raise WarehouseError(
                f"the {self.target} target refused a cursor: "
                f"{_printable(type(error).__name__)}"
            ) from error
        try:
            cursor.execute(prepared, tuple(parameters))
            rows = cursor.fetchall()
        except Exception as error:  # the adapter's own failure
            raise WarehouseError(
                f"the {self.target} target refused the statement "
                f"{_shown(statement, limit=200)}: {_first_line(error)}"
            ) from error
        finally:
            # A cursor the adapter closed already is passed over.
            with contextlib.suppress(Exception):
                cursor.close()
        return [tuple(row) for row in rows]

    def close(self) -> None:
        """Close the connection, passing over an adapter that closed it already."""
        with contextlib.suppress(Exception):
            self._connection.close()


def _open_duckdb(database: Path) -> Warehouse:
    """Return a read-only connection to the DuckDB database at ``database``."""
    try:
        import duckdb  # imported for this target alone
    except ImportError as error:
        raise ConfigurationError(
            "the duckdb distribution is not installed for this interpreter; "
            "modernization/requirements.txt pins duckdb==1.5.5"
        ) from error
    if not database.is_file():
        raise ConfigurationError(
            f"the DuckDB database is not present at {_path_shown(database)}; the local "
            f"branch writes it through modernization/landing/load_local.py"
        )
    try:
        connection = duckdb.connect(str(database), read_only=True)
    except Exception as error:  # the adapter's own failure
        raise ConfigurationError(
            f"the DuckDB database at {_path_shown(database)} could not be opened "
            f"read-only: {_first_line(error)}"
        ) from error
    return Warehouse(
        target=TARGET_DUCKDB,
        connection=connection,
        adapter="duckdb",
        adapter_version=str(getattr(duckdb, "__version__", "unknown")),
        identity=_path_shown(database),
    )


def _open_redshift() -> Warehouse:
    """Return a connection to the Redshift target named by the environment.

    REDSHIFT_HOST, REDSHIFT_DATABASE, REDSHIFT_USER and REDSHIFT_PASSWORD are
    required and REDSHIFT_PORT and REDSHIFT_CONNECT_TIMEOUT carry defaults, the
    variable contract of modernization/dbt/genapp_rqi/profiles.example.yml. A
    variable that is unset is named; no value of any variable is printed, and the
    connection is recorded as its host and database alone.
    """
    try:
        import redshift_connector  # imported for this target alone
    except ImportError as error:
        raise ConfigurationError(
            "the redshift-connector distribution is not installed for this "
            "interpreter; modernization/requirements.txt pins "
            "redshift-connector==2.1.16"
        ) from error
    required = (
        "REDSHIFT_HOST",
        "REDSHIFT_DATABASE",
        "REDSHIFT_USER",
        "REDSHIFT_PASSWORD",
    )
    settings = {name: _environment_value(name) for name in required}
    missing = [name for name in required if settings[name] is None]
    if missing:
        raise ConfigurationError(
            f"the redshift target requires {_quote_all(missing)}, which "
            f"{'is' if len(missing) == 1 else 'are'} unset or hold whitespace alone; "
            f"the variable contract stands in "
            f"modernization/dbt/genapp_rqi/profiles.example.yml"
        )
    port_text = _environment_value("REDSHIFT_PORT") or "5439"
    if not port_text.isdigit() or not 1 <= int(port_text) <= 65535:
        raise ConfigurationError(
            "REDSHIFT_PORT must be a decimal whole number between 1 and 65535"
        )
    timeout_text = _environment_value("REDSHIFT_CONNECT_TIMEOUT") or "30"
    if not timeout_text.isdigit() or int(timeout_text) < 1:
        raise ConfigurationError(
            "REDSHIFT_CONNECT_TIMEOUT must be a decimal whole number of seconds, one "
            "or above"
        )
    try:
        connection = redshift_connector.connect(
            host=settings["REDSHIFT_HOST"],
            database=settings["REDSHIFT_DATABASE"],
            user=settings["REDSHIFT_USER"],
            password=settings["REDSHIFT_PASSWORD"],
            port=int(port_text),
            ssl=True,
            sslmode="verify-full",
            timeout=int(timeout_text),
            application_name=_PROGRAM,
        )
    except Exception as error:  # the adapter's own failure
        raise ConfigurationError(
            f"the redshift target did not accept a connection: "
            f"{_printable(type(error).__name__)}"
        ) from error
    host = settings["REDSHIFT_HOST"] or ""
    database = settings["REDSHIFT_DATABASE"] or ""
    return Warehouse(
        target=TARGET_REDSHIFT,
        connection=connection,
        adapter="redshift-connector",
        adapter_version=str(getattr(redshift_connector, "__version__", "unknown")),
        identity=f"{host}/{database}",
    )


def open_warehouse(target: str, database: Path) -> Warehouse:
    """Return an open connection to ``target``, importing that adapter alone."""
    if target == TARGET_DUCKDB:
        return _open_duckdb(database)
    if target == TARGET_REDSHIFT:
        return _open_redshift()
    raise ConfigurationError(
        f"the target {_shown(target)} is not one of {_quote_all(TARGETS)}"
    )


def assert_canonical_inventory(warehouse: Warehouse) -> dict[str, Any]:
    """Assert that schema canonical holds the two declared relations and no other.

    The relation set of ``information_schema.tables`` must equal
    ``DECLARED_RELATIONS`` exactly, and the column names of
    ``information_schema.columns`` must equal the declared list of each relation in
    ordinal order. A third relation, an extra column, an absent column and a
    reordered column each raise ``WarehouseError``, whose message states that the
    run stops and reports.
    """
    tables = sorted(
        str(row[0])
        for row in warehouse.query(_INVENTORY_TABLES_SQL, (CANONICAL_SCHEMA,))
    )
    declared = sorted(DECLARED_RELATIONS)
    if tables != declared:
        extra = sorted(set(tables) - set(declared))
        absent = sorted(set(declared) - set(tables))
        detail = []
        if extra:
            detail.append(
                f"a third canonical relation stands there: {_quote_all(extra)}"
            )
        if absent:
            detail.append(f"a declared relation is absent: {_quote_all(absent)}")
        raise WarehouseError(
            f"schema {CANONICAL_SCHEMA} of the {warehouse.target} target holds "
            f"{_quote_all(tables)}; this work builds {_quote_all(declared)} and no "
            f"other relation. " + "; ".join(detail) + ". The run stops and reports "
            "rather than comparing a canonical layer other than the declared one"
        )
    observed: dict[str, list[str]] = {name: [] for name in declared}
    for row in warehouse.query(_INVENTORY_COLUMNS_SQL, (CANONICAL_SCHEMA,)):
        table_name = str(row[0])
        if table_name in observed:
            observed[table_name].append(str(row[1]))
    for alias, columns in DECLARED_RELATIONS.items():
        found = tuple(observed[alias])
        if found != columns:
            extra = sorted(set(found) - set(columns))
            absent = sorted(set(columns) - set(found))
            detail = []
            if extra:
                detail.append(
                    f"a non-required column stands there: {_quote_all(extra)}"
                )
            if absent:
                detail.append(f"a declared column is absent: {_quote_all(absent)}")
            if not detail:
                detail.append("the columns stand in another ordinal order")
            raise WarehouseError(
                f"{CANONICAL_SCHEMA}.{alias} of the {warehouse.target} target carries "
                f"{_quote_all(found)}; the declared contract is {_quote_all(columns)} "
                f"in that order. " + "; ".join(detail) + ". The run stops and reports "
                "rather than comparing a relation other than the declared one"
            )
    return {
        "schema": CANONICAL_SCHEMA,
        "relations": declared,
        "columns": {
            alias: list(columns) for alias, columns in DECLARED_RELATIONS.items()
        },
        "verdict": "PASS",
    }


def fetch_canonical_row(
    warehouse: Warehouse,
    relation: RelationTarget,
    source_system_key: str,
    policy_number: int,
) -> dict[str, Any]:
    """Return the single row of ``relation`` carrying the natural key supplied.

    The select list names the declared columns of the relation in contract order,
    so no column outside that contract is read: canonical.preissued_rating applies
    its return-code filter without projecting return_code, and no statement of this
    module names that column on that relation. Zero rows and more than one row each
    raise ``WarehouseError``.
    """
    columns = ", ".join(relation.columns)
    statement = (
        f"select {columns} from {relation.schema}.{relation.alias} "
        f"where source_system_key = ? and policy_number = ?"
    )
    rows = warehouse.query(statement, (source_system_key, policy_number))
    if not rows:
        raise WarehouseError(
            f"{relation.key} carries no row for source_system_key "
            f"{_shown(source_system_key)} and policy_number {policy_number}; exactly "
            f"one row is required"
        )
    if len(rows) > 1:
        raise WarehouseError(
            f"{relation.key} carries {len(rows)} rows for source_system_key "
            f"{_shown(source_system_key)} and policy_number {policy_number}; exactly "
            f"one row is required"
        )
    return dict(zip(relation.columns, rows[0]))



# --------------------------------------------------------------------------
# Assertions outside the canonical columns
# --------------------------------------------------------------------------
GROUP_CHAIN = "Chain completion"
GROUP_VSAM = "VSAM corroboration"
GROUP_IDENTITY = "Cross-relation identity"


def _capture_assertion(
    captures: Mapping[str, str],
    group: str,
    key: str,
    expected: str,
    locator: str,
    *,
    numeric: bool = False,
) -> Assertion:
    """Return the assertion of capture ``key`` against ``expected``.

    A key the capture file omits is reported MISSING. With ``numeric`` the observed
    and expected values are compared as integers, so a zero-padded count matches the
    count it carries; otherwise they are compared as text with trailing spaces
    removed.
    """
    if key not in captures:
        return Assertion(
            group=group,
            name=key,
            expected=expected,
            observed="absent",
            locator=locator,
            status=STATUS_MISSING,
            notes=(f"the capture file carries no key {key}",),
        )
    observed = captures[key].strip()
    if numeric:
        try:
            matched = int(observed or "x") == int(expected)
        except ValueError:
            matched = False
    else:
        matched = observed == expected
    return Assertion(
        group=group,
        name=key,
        expected=expected,
        observed=observed,
        locator=locator,
        status=STATUS_PASS if matched else STATUS_FAIL,
        notes=()
        if matched
        else (
            (
                f"the capture carries {_shown(observed)} where {_shown(expected)} "
                f"is required"
            ),
        ),
    )


def chain_completion_assertions(
    case: str, policy_type: str, captures: Mapping[str, str]
) -> list[Assertion]:
    """Return the chain-completion assertions of one case.

    The driver status, the absence of an abend and of a diagnostic link, the
    presence of the policy SQL capture, the presence of exactly the product capture
    the policy type selects, and the returned success code are each asserted from
    the capture file.
    """
    assertions = [
        _capture_assertion(
            captures, GROUP_CHAIN, CASE_KEY, case, "modernization/harness/driver.cbl"
        ),
        _capture_assertion(
            captures,
            GROUP_CHAIN,
            DRIVER_STATUS_KEY,
            DRIVER_STATUS_PASS,
            "modernization/harness/driver.cbl",
        ),
        _capture_assertion(
            captures,
            GROUP_CHAIN,
            DRIVER_EXIT_STATUS_KEY,
            DRIVER_EXIT_STATUS_OK,
            "modernization/harness/driver.cbl",
            numeric=True,
        ),
        _capture_assertion(
            captures,
            GROUP_CHAIN,
            RETURN_CODE_CAPTURE_KEY,
            SUCCESS_RETURN_CODE,
            "base/src/lgapdb01.cbl:293",
        ),
        _capture_assertion(
            captures, GROUP_CHAIN, ABEND_PRESENT_KEY, "N", "base/src/lgapdb01.cbl:393"
        ),
        _capture_assertion(
            captures, GROUP_CHAIN, ABEND_CODE_KEY, "", "base/src/lgapdb01.cbl:393"
        ),
        _capture_assertion(
            captures,
            GROUP_CHAIN,
            ABEND_COUNT_KEY,
            "0",
            "base/src/lgapdb01.cbl:393",
            numeric=True,
        ),
        _capture_assertion(
            captures,
            GROUP_CHAIN,
            DIAG_LINK_COUNT_KEY,
            "0",
            "base/src/lgapdb01.cbl:575-592",
            numeric=True,
        ),
        _capture_assertion(
            captures,
            GROUP_CHAIN,
            POLICY_PRESENT_KEY,
            "Y",
            "base/src/lgapdb01.cbl:268-287",
        ),
    ]
    for letter in sorted(PRODUCT_PRESENCE_KEYS):
        assertions.append(
            _capture_assertion(
                captures,
                GROUP_CHAIN,
                PRODUCT_PRESENCE_KEYS[letter],
                "Y" if letter == policy_type else "N",
                "base/src/lgapdb01.cbl:223-241",
            )
        )
    return assertions


def vsam_assertions(
    captures: Mapping[str, str], row: Mapping[str, Any]
) -> list[Assertion]:
    """Return the VSAM corroboration of one case against the canonical identifiers.

    The record length and the key length are asserted against the lengths the write
    of base/src/lgapvs01.cbl:135-141 states. The key is rebuilt from the canonical
    row in the layout order of WF-Policy-Key at base/src/lgapvs01.cbl:26-29 - the
    type letter taken from position 4 of the request id, the customer number as
    X(10) and the policy number as X(10) - and compared with the key the write
    carried, component by component. The 43-byte product payload is corroboration of
    the write alone and is compared with no canonical column.
    """
    assertions = [
        _capture_assertion(
            captures, GROUP_VSAM, VSAM_PRESENT_KEY, "Y", "base/src/lgapvs01.cbl:135-141"
        ),
        _capture_assertion(
            captures,
            GROUP_VSAM,
            VSAM_LENGTH_KEY,
            str(VSAM_RECORD_LENGTH),
            "base/src/lgapvs01.cbl:137",
            numeric=True,
        ),
        _capture_assertion(
            captures,
            GROUP_VSAM,
            VSAM_KEYLENGTH_KEY,
            str(VSAM_KEY_LENGTH),
            "base/src/lgapvs01.cbl:139",
            numeric=True,
        ),
    ]
    request_id = str(row.get("request_id", "")).strip()
    letter = (
        request_id[VSAM_TYPE_LETTER_POSITION - 1]
        if len(request_id) >= VSAM_TYPE_LETTER_POSITION
        else ""
    )
    components: list[tuple[str, str]] = []
    try:
        customer = f"{int(row['customer_number']):010d}"
        policy = f"{int(row['policy_number']):010d}"
    except (KeyError, TypeError, ValueError):
        customer = ""
        policy = ""
    components.append((VSAM_KEY_LAYOUT[0][0], letter))
    components.append((VSAM_KEY_LAYOUT[1][0], customer))
    components.append((VSAM_KEY_LAYOUT[2][0], policy))
    expected_key = "".join(value for _, value in components)
    assertions.append(
        _capture_assertion(
            captures,
            GROUP_VSAM,
            VSAM_KEY_KEY,
            expected_key,
            "base/src/lgapvs01.cbl:26-29",
        )
    )
    for (_, expected), key in zip(
        components,
        (VSAM_REQUEST_ID_KEY, VSAM_CUSTOMER_NUM_KEY, VSAM_POLICY_NUM_KEY),
    ):
        assertions.append(
            _capture_assertion(
                captures, GROUP_VSAM, key, expected, "base/src/lgapvs01.cbl:26-29"
            )
        )
    assertions.append(
        Assertion(
            group=GROUP_VSAM,
            name="product payload",
            expected=f"{VSAM_PAYLOAD_LENGTH} bytes, mapped to no canonical column",
            observed=f"{VSAM_PAYLOAD_LENGTH} bytes, not compared",
            locator="base/src/lgapvs01.cbl:30",
            notes=(
                "the payload corroborates the write and the composite key alone",
            ),
        )
    )
    return assertions


def identity_assertions(
    issued: Mapping[str, Any], rating: Mapping[str, Any]
) -> list[Assertion]:
    """Assert that the three shared columns carry one value across both relations."""
    assertions: list[Assertion] = []
    for column in SHARED_COLUMNS:
        left = _render(issued.get(column))
        right = _render(rating.get(column))
        matched = left == right
        assertions.append(
            Assertion(
                group=GROUP_IDENTITY,
                name=column,
                expected=f"{RELATION_KEYS[0]} carries {_shown(left)}",
                observed=f"{RELATION_KEYS[1]} carries {_shown(right)}",
                locator="modernization/extraction/copybook_field_map.yml: targets",
                status=STATUS_PASS if matched else STATUS_FAIL,
                notes=()
                if matched
                else (
                    f"the two relations carry different values for {column}",
                ),
            )
        )
    return assertions



# --------------------------------------------------------------------------
# Harness input resolution and the capture snapshot
# --------------------------------------------------------------------------
class CasePaths(NamedTuple):
    """The three input paths of one case and how the sample path was resolved."""

    captures: Path
    commarea: Path
    sample: Path | None
    sample_source: str


def resolve_case_paths(
    case: str,
    fixture: str,
    run_dir: Path,
    captures_override: Path | None,
    commarea_override: Path | None,
    sample_override: Path | None,
) -> CasePaths:
    """Return the input paths of ``case``.

    The capture file and the returned COMMAREA stand in ``<run-dir>/<case>`` under
    the names the harness writes, unless an override names another file. The record
    the driver was handed comes from the override, then from the DD_SAMPLEFILE
    environment variable, and then from ``<run-dir>/../samples/commarea_<fixture>.dat``,
    the generated record the harness runner hands the driver on standard input.
    """
    directory = run_dir / case.lower()
    captures = captures_override or directory / CAPTURES_NAME
    commarea = commarea_override or directory / COMMAREA_POST_NAME
    if sample_override is not None:
        return CasePaths(captures, commarea, sample_override, "--sample-record")
    from_environment = _environment_value(SAMPLE_PATH_VARIABLE)
    if from_environment:
        return CasePaths(
            captures,
            commarea,
            _resolved(from_environment),
            f"the {SAMPLE_PATH_VARIABLE} environment variable",
        )
    derived = (
        run_dir.parent / SAMPLES_DIR_NAME / SAMPLE_NAME_TEMPLATE.format(fixture=fixture)
    )
    return CasePaths(
        captures,
        commarea,
        derived,
        f"the generated record of fixture {fixture} under the harness build tree",
    )


def read_harness_case(
    case: str,
    run_dir: Path,
    field_map: FieldMap,
    captures_override: Path | None,
    commarea_override: Path | None,
    sample_override: Path | None,
) -> HarnessCase:
    """Return the harness inputs of ``case``.

    The capture file is parsed first, so the FIXTURE it carries resolves the record
    the driver was handed. The returned COMMAREA is required and must hold the
    record length the field map declares. The driver input is read when it stands at
    the resolved path; a path that carries nothing is recorded, and every column that
    reads the driver input then reports MISSING.
    """
    interim = resolve_case_paths(
        case,
        case.lower(),
        run_dir,
        captures_override,
        commarea_override,
        sample_override,
    )
    captures = parse_captures(interim.captures)
    declared_case = captures.get(CASE_KEY, "").strip()
    if declared_case and declared_case != case:
        raise HarnessInputError(
            f"the capture file at {_path_shown(interim.captures)} carries "
            f"{CASE_KEY}={_shown(declared_case)}; the case being compared is "
            f"{_shown(case)}"
        )
    fixture = captures.get(FIXTURE_KEY, "").strip() or case.lower()
    paths = resolve_case_paths(
        case, fixture, run_dir, captures_override, commarea_override, sample_override
    )
    commarea = read_record(paths.commarea, "returned COMMAREA", field_map.record_length)
    sample: str | None = None
    sample_source = paths.sample_source
    if paths.sample is not None:
        if paths.sample.is_file():
            sample = read_record(
                paths.sample, "record the driver was handed", field_map.record_length
            )
        else:
            sample_source = (
                f"no record stands at {_path_shown(paths.sample)}, resolved from "
                f"{paths.sample_source}"
            )
    return HarnessCase(
        case=case,
        fixture=fixture,
        captures=captures,
        captures_path=paths.captures,
        commarea=commarea,
        commarea_path=paths.commarea,
        sample=sample,
        sample_path=paths.sample,
        sample_source=sample_source,
    )


def build_snapshot(result: CaseResult, harness: HarnessCase) -> dict[str, Any]:
    """Return the normalised harness capture snapshot of one compared case.

    It carries every capture key this run read with the value it held, every
    COMMAREA and driver-input window this run sliced, and the case identity the
    comparison used. Keys and window names are sorted, so two runs of the same
    harness output write the same document.
    """
    captures: dict[str, str] = {}
    commarea_windows: dict[str, str] = {}
    driver_windows: dict[str, str] = {}
    for comparison in result.comparisons:
        for witness in comparison.witnesses:
            if witness.raw is None or witness.key is None:
                continue
            if witness.family == "capture":
                captures[witness.key] = witness.raw
            elif witness.family == "commarea":
                commarea_windows[witness.key] = witness.raw
            elif witness.family == "driver-input":
                driver_windows[witness.key] = witness.raw
    for assertion in result.assertions:
        if (
            assertion.group in (GROUP_CHAIN, GROUP_VSAM)
            and not assertion.missing
            and assertion.name in harness.captures
        ):
            captures[assertion.name] = harness.captures[assertion.name]
    return {
        "case": result.case,
        "fixture": result.fixture,
        "policy_type": result.policy_type,
        "request_id": result.request_id,
        "record_length": len(harness.commarea),
        "captures": dict(sorted(captures.items())),
        "commarea_windows": dict(sorted(commarea_windows.items())),
        "driver_input_windows": dict(sorted(driver_windows.items())),
    }


def _snapshot_differences(
    expected: Mapping[str, Any], observed: Mapping[str, Any], where: str = ""
) -> list[str]:
    """Return one line per difference between two snapshot documents."""
    differences: list[str] = []
    for key in sorted(set(expected) | set(observed)):
        path = f"{where}.{key}" if where else key
        if key not in expected:
            differences.append(
                f"{path}: absent from the snapshot, now "
                f"{_shown(str(observed[key]))}"
            )
            continue
        if key not in observed:
            differences.append(
                f"{path}: {_shown(str(expected[key]))} in the snapshot, now absent"
            )
            continue
        left, right = expected[key], observed[key]
        if isinstance(left, Mapping) and isinstance(right, Mapping):
            differences.extend(_snapshot_differences(left, right, path))
        elif left != right:
            differences.append(
                f"{path}: {_shown(str(left))} in the snapshot, now {_shown(str(right))}"
            )
    return differences


def apply_snapshot(path: Path, document: Mapping[str, Any]) -> str:
    """Write the snapshot at ``path``, or compare it with the one already there.

    A path that carries nothing is written and reported as written. A path that
    carries a snapshot is read and compared, and a difference raises
    ``HarnessInputError`` naming every key that differs with both values.
    """
    rendered = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if not path.exists():
        _write_output(path, rendered)
        return "written"
    text = _read_text(path, "capture snapshot", HarnessInputError)
    try:
        stored = json.loads(text)
    except json.JSONDecodeError as error:
        raise HarnessInputError(
            f"the capture snapshot at {_path_shown(path)} is not a JSON document: "
            f"{_printable(error.msg)} at line {error.lineno}"
        ) from error
    if not isinstance(stored, Mapping):
        raise HarnessInputError(
            f"the capture snapshot at {_path_shown(path)} does not hold an object at "
            f"its root"
        )
    differences = _snapshot_differences(stored, document)
    if differences:
        raise HarnessInputError(
            f"the harness output differs from the capture snapshot at "
            f"{_path_shown(path)} in {len(differences)} place"
            f"{'' if len(differences) == 1 else 's'}: " + "; ".join(differences[:20])
        )
    return "matched"



# --------------------------------------------------------------------------
# Output paths
# --------------------------------------------------------------------------
def _refuse_protected_path(path: Path) -> None:
    """Refuse an output path resolving inside a tree this tool never writes."""
    resolved = path.resolve() if path.exists() else _resolved(path)
    for tree in PROTECTED_TREES:
        root = (REPO_ROOT / tree).resolve()
        if resolved == root or root in resolved.parents:
            raise ConfigurationError(
                f"the output path {_path_shown(path)} resolves inside {tree}/, which "
                f"this tool never writes"
            )


def _write_output(path: Path, text: str) -> None:
    """Write ``text`` to ``path``, creating the directories above it."""
    _refuse_protected_path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as error:
        raise ConfigurationError(
            f"the file at {_path_shown(path)} could not be written: "
            f"{_printable(error.strerror or type(error).__name__)}"
        ) from error


# --------------------------------------------------------------------------
# One compared case
# --------------------------------------------------------------------------
def compare_case(
    case: str,
    harness: HarnessCase,
    warehouse: Warehouse,
    field_map: FieldMap,
    source_system_key: str,
    expected_dir: Path,
) -> CaseResult:
    """Compare one case against both canonical relations and return its result.

    The request id and the policy number come from the returned COMMAREA, the
    policy type from the request routing, and the two canonical rows from the
    natural key (source_system_key, policy_number). Every column of both relations
    is then compared, followed by the chain-completion assertions, the VSAM
    corroboration, the cross-relation identity of the three shared columns and the
    capture snapshot.
    """
    result = CaseResult(
        case=case,
        fixture=harness.fixture,
        captures_path=_path_shown(harness.captures_path),
        commarea_path=_path_shown(harness.commarea_path),
        sample_path=_path_shown(harness.sample_path) if harness.sample_path else "",
        sample_source=harness.sample_source,
    )
    request_window = field_map.window("CA-REQUEST-ID")
    result.request_id = slice_window(
        harness.commarea, request_window, "returned COMMAREA"
    ).strip()
    result.policy_type = derive_policy_type(result.request_id, field_map)
    policy_window = field_map.window("CA-POLICY-NUM")
    policy_text = slice_window(
        harness.commarea, policy_window, "returned COMMAREA"
    ).strip()
    try:
        result.policy_number = _normalise_integer(policy_text)
    except ValueError as error:
        raise HarnessInputError(
            f"{policy_window.item} at bytes {policy_window.byte_range} of the returned "
            f"COMMAREA carries {error}; the chain assigns it at "
            f"base/src/lgapdb01.cbl:308-311"
        ) from error

    rows: dict[str, Mapping[str, Any]] = {}
    for key in RELATION_KEYS:
        rows[key] = fetch_canonical_row(
            warehouse,
            field_map.relations[key],
            source_system_key,
            result.policy_number,
        )

    for key in RELATION_KEYS:
        relation = field_map.relations[key]
        row = rows[key]
        for column in relation.columns:
            entry = field_map.entry(relation.sources[column])
            kind = comparison_kind(column, relation.types[column], field_map)
            witnesses: tuple[Witness, ...] = ()
            notes: tuple[str, ...] = ()
            if kind == KIND_AMOUNT and column not in field_map.populated_amounts.get(
                result.policy_type, ()
            ):
                if column not in field_map.null_amounts.get(result.policy_type, ()):
                    raise ConfigurationError(
                        f"the field map records {_shown(column)} neither as populated "
                        f"nor as null for policy type {_shown(result.policy_type)} "
                        f"under product_premium_nullability.by_policy_type"
                    )
                kind = KIND_NULL_EXPECTED
                notes = (
                    (
                        f"product_premium_nullability records this column as null "
                        f"for policy type {result.policy_type}"
                    ),
                )
            else:
                witnesses = _column_witnesses(
                    entry, harness, field_map, source_system_key
                )
            record = Comparison(
                relation=key,
                column=column,
                kind=kind,
                cobol_item=entry.cobol_item,
                locator=entry.locator,
                evidence=entry.evidence,
                witnesses=witnesses,
                notes=notes,
            )
            result.comparisons.append(
                _compare_column(
                    record, row.get(column), nullable=relation.nullable[column]
                )
            )

    result.assertions.extend(
        chain_completion_assertions(case, result.policy_type, harness.captures)
    )
    result.assertions.extend(vsam_assertions(harness.captures, rows[RELATION_KEYS[0]]))
    result.assertions.extend(
        identity_assertions(rows[RELATION_KEYS[0]], rows[RELATION_KEYS[1]])
    )

    snapshot_path = expected_dir / case.lower() / SNAPSHOT_NAME
    result.snapshot_path = _path_shown(snapshot_path)
    result.snapshot_state = apply_snapshot(
        snapshot_path, build_snapshot(result, harness)
    )
    return result



# --------------------------------------------------------------------------
# Run report
# --------------------------------------------------------------------------
@dataclass
class RunReport:
    """Everything one run of this tool records, in both report formats."""

    generated_at: str
    target: str
    adapter: str
    adapter_version: str
    python_version: str
    connection: str
    source_system_key: str
    field_map: str
    run_dir: str
    expected_dir: str
    requested_cases: tuple[str, ...]
    local_substitute: bool
    inventory: dict[str, Any] = field(default_factory=dict)
    gate_artifact: dict[str, Any] = field(default_factory=dict)
    return_codes: Mapping[str, str] = field(default_factory=dict)
    cases: list[CaseResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    statuses: list[int] = field(default_factory=list)

    @property
    def status_label(self) -> str:
        """Return the disposition every claimed result of this run carries."""
        return (
            STATUS_LABEL_TEXT
            if self.local_substitute
            else f"validated against the {self.target} target"
        )

    @property
    def exit_status(self) -> int:
        """Return the status of the run, the first of its statuses in precedence."""
        collected = list(self.statuses)
        collected.extend(case.exit_status for case in self.cases)
        if not self.cases and not collected:
            collected.append(EXIT_HARNESS_INPUT)
        return _worst_status(collected or [EXIT_OK])

    @property
    def verdict(self) -> str:
        """Return PASS or FAIL for the run."""
        return "PASS" if self.exit_status == EXIT_OK else "FAIL"

    @property
    def in_tolerance(self) -> list[tuple[str, Comparison]]:
        """Return every non-zero in-tolerance amount delta of the run."""
        return [
            (case.case, record)
            for case in self.cases
            for record in case.in_tolerance
        ]

    @property
    def scale_anomalies(self) -> list[tuple[str, Comparison]]:
        """Return every warehouse amount of the run carrying another scale."""
        return [
            (case.case, record)
            for case in self.cases
            for record in case.scale_anomalies
        ]

    def as_document(self) -> dict[str, Any]:
        """Return the JSON report of the run."""
        return {
            "tool": _PROGRAM,
            "generated_at": self.generated_at,
            "status_label": self.status_label,
            "aws_diff_requirement": (
                "OPEN" if self.local_substitute else "addressed by this run"
            ),
            "aws_statement": AWS_OPEN_TEXT if self.local_substitute else "",
            "target": self.target,
            "adapter": {"name": self.adapter, "version": self.adapter_version},
            "python_version": self.python_version,
            "connection": self.connection,
            "source_system_key": self.source_system_key,
            "amount_tolerance": format(AMOUNT_TOLERANCE, "f"),
            "amount_scale": AMOUNT_SCALE,
            "field_map": self.field_map,
            "run_dir": self.run_dir,
            "expected_dir": self.expected_dir,
            "requested_cases": list(self.requested_cases),
            "canonical_inventory": self.inventory,
            "gate_artifact": self.gate_artifact,
            "return_code_vocabulary": dict(sorted(self.return_codes.items())),
            "figure_reference": (
                "Figure 5 — Validation Harness Control Flow in "
                "modernization/docs/architecture.md"
            ),
            "cases": [case.as_document() for case in self.cases],
            "summary": {
                "cases": len(self.cases),
                "comparisons": sum(len(case.comparisons) for case in self.cases),
                "expected_comparisons": len(self.cases) * CANONICAL_COLUMN_INSTANCES,
                "failed": sum(len(case.failed) for case in self.cases),
                "missing": sum(
                    1
                    for case in self.cases
                    for record in case.comparisons
                    if record.missing
                ),
                "assertions": sum(len(case.assertions) for case in self.cases),
                "failed_assertions": sum(
                    len(case.failed_assertions) for case in self.cases
                ),
                "unexpected_in_tolerance": [
                    {"case": case, "column": record.column, "delta": record.delta}
                    for case, record in self.in_tolerance
                ],
                "scale_anomalies": [
                    {"case": case, "column": record.column}
                    for case, record in self.scale_anomalies
                ],
            },
            "errors": list(self.errors),
            "verdict": self.verdict,
            "exit_status": self.exit_status,
        }


def _cell(value: Any) -> str:
    """Return ``value`` as one Markdown table cell.

    A value that is absent renders as an em dash and a value that is the empty
    string renders as ``(empty)``, so the two are told apart in the report. A
    vertical bar of a value is escaped and a line break is replaced by a space, so
    one value stays inside one cell.
    """
    if value is None:
        return "—"
    text = str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    return _printable(text) if text else "(empty)"


def _table(headings: Sequence[str], rows: Iterable[Sequence[Any]]) -> list[str]:
    """Return one Markdown table as a list of lines."""
    lines = [
        "| " + " | ".join(headings) + " |",
        "|" + "|".join("---" for _ in headings) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_cell(value) for value in row) + " |")
    return lines


def render_markdown(report: RunReport) -> str:
    """Return the Markdown report of one run.

    Every claimed result of a local-substitute run carries the disposition phrase,
    and the report states that such a run leaves the formal AWS diff requirement
    open. Each per-case table enumerates every compared column with its COBOL item
    and locator, so the enumeration can be cited column by column.
    """
    label = report.status_label
    lines: list[str] = [
        "# Comparison gate — harness captures against the two canonical relations",
        "",
        (
            f"**Disposition — {label}.** Every result in this report carries that "
            "disposition."
        ),
        "",
    ]
    if report.local_substitute:
        lines.extend([AWS_OPEN_TEXT, ""])
    lines.extend(
        [
            (
                "Flow context: Figure 5 — Validation Harness Control Flow in "
                "modernization/docs/architecture.md."
            ),
            "",
            "Decision rationale: see modernization/docs/decision-log.md.",
            "",
            "## Run metadata",
            "",
        ]
    )
    lines.extend(
        _table(
            ("Item", "Value"),
            (
                ("generated at (UTC)", report.generated_at),
                ("target", report.target),
                ("adapter", f"{report.adapter} {report.adapter_version}"),
                ("python", report.python_version),
                ("connection", report.connection),
                ("source-system key", report.source_system_key),
                ("amount tolerance", format(AMOUNT_TOLERANCE, "f")),
                ("expected amount scale", AMOUNT_SCALE),
                ("field map", report.field_map),
                ("harness run directory", report.run_dir),
                ("capture snapshots", report.expected_dir),
                ("cases requested", ", ".join(report.requested_cases)),
                (
                    "gate artifact",
                    report.gate_artifact.get("name")
                    or report.gate_artifact.get("note", "none read"),
                ),
                ("disposition", label),
            ),
        )
    )
    lines.extend(["", "## Verdict", ""])
    lines.extend(
        _table(
            (
                "Case",
                "Verdict",
                "Coverage",
                "Failed",
                "Missing",
                "Unexpected in tolerance",
                "Disposition",
            ),
            (
                (
                    case.case,
                    case.verdict,
                    f"{len(case.comparisons)}/{CANONICAL_COLUMN_INSTANCES}",
                    len(case.failed) + len(case.failed_assertions),
                    sum(1 for record in case.comparisons if record.missing),
                    len(case.in_tolerance),
                    label,
                )
                for case in report.cases
            ),
        )
    )
    lines.extend(
        [
            "",
            (
                f"**Overall verdict: {report.verdict}** (exit status "
                f"{report.exit_status}) — {label}."
            ),
            "",
        ]
    )
    if report.errors:
        lines.extend(["## Reported failures", ""])
        lines.extend(f"- {_printable(message)}" for message in report.errors)
        lines.append("")
    lines.extend(["## Canonical inventory", ""])
    if report.inventory:
        lines.extend(
            _table(
                ("Relation", "Columns in ordinal order", "Verdict"),
                (
                    (
                        f"{CANONICAL_SCHEMA}.{alias}",
                        ", ".join(columns),
                        report.inventory.get("verdict", ""),
                    )
                    for alias, columns in sorted(
                        report.inventory.get("columns", {}).items()
                    )
                ),
            )
        )
        lines.extend(
            [
                "",
                (
                    f"Schema {CANONICAL_SCHEMA} holds exactly "
                    f"{', '.join(sorted(DECLARED_RELATIONS))} — {label}."
                ),
                "",
            ]
        )
    else:
        lines.extend(
            [
                (
                    "The canonical inventory was not established on this run; the "
                    "reported failures above name what the warehouse answered."
                ),
                "",
            ]
        )
    for case in report.cases:
        lines.extend(_render_case(case, label))
    lines.extend(["## Amount deltas inside the tolerance", ""])
    if report.in_tolerance:
        lines.extend(
            _table(
                ("Case", "Relation", "Column", "Harness", "Warehouse", "Delta"),
                (
                    (
                        case,
                        record.relation,
                        record.column,
                        record.harness_value,
                        record.warehouse_value,
                        record.delta,
                    )
                    for case, record in report.in_tolerance
                ),
            )
        )
        lines.extend(
            [
                "",
                (
                    "Each delta above is non-zero and within the tolerance: the "
                    f"comparison passes and the delta is unexpected — {label}."
                ),
                "",
            ]
        )
    else:
        lines.extend([f"unexpected_in_tolerance: none — {label}.", ""])
    lines.extend(["## Warehouse amount scale", ""])
    if report.scale_anomalies:
        lines.extend(
            _table(
                ("Case", "Column", "Warehouse value", "Notes"),
                (
                    (
                        case,
                        record.column,
                        record.warehouse_value,
                        "; ".join(record.notes),
                    )
                    for case, record in report.scale_anomalies
                ),
            )
        )
        lines.append("")
    else:
        lines.extend(
            [
                (
                    f"Every compared warehouse amount carries scale {AMOUNT_SCALE} "
                    f"— {label}."
                ),
                "",
            ]
        )
    lines.extend(["## Return-code vocabulary of the named chain", ""])
    lines.extend(
        _table(
            ("Code", "Observed meaning"),
            sorted(report.return_codes.items()),
        )
    )
    lines.extend(
        [
            "",
            (
                f"The harness executes the success path and a compared case carries "
                f"{SUCCESS_RETURN_CODE}; the remaining codes stand in the vocabulary "
                f"of the chain and are unexercised by this run."
            ),
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_case(case: CaseResult, label: str) -> list[str]:
    """Return the Markdown section of one compared case."""
    lines = [
        f"## Case {case.case}",
        "",
    ]
    lines.extend(
        _table(
            ("Item", "Value"),
            (
                ("fixture", case.fixture),
                ("request id", case.request_id),
                ("policy type", case.policy_type),
                ("policy number", case.policy_number),
                ("capture file", case.captures_path),
                ("returned COMMAREA", case.commarea_path),
                ("driver input", case.sample_path or case.sample_source),
                ("capture snapshot", f"{case.snapshot_path} ({case.snapshot_state})"),
                ("verdict", f"{case.verdict} — {label}"),
            ),
        )
    )
    lines.extend(["", f"{case.coverage} — {label}.", ""])
    if case.errors:
        lines.extend(["### Reported failures of this case", ""])
        lines.extend(f"- {_printable(message)}" for message in case.errors)
        lines.append("")
    if case.comparisons:
        lines.extend(["### Canonical column comparison", ""])
        lines.extend(
            _table(
                (
                    "Relation",
                    "Column",
                    "Kind",
                    "Harness authority",
                    "COBOL item",
                    "Locator",
                    "Harness value",
                    "Warehouse value",
                    "Delta",
                    "Normalisation",
                    "Verdict",
                    "Notes",
                ),
                (
                    (
                        record.relation,
                        record.column,
                        record.kind,
                        record.authority,
                        record.cobol_item,
                        record.locator,
                        record.harness_value,
                        record.warehouse_value,
                        record.delta,
                        ", ".join(record.normalisations) or NORM_NONE,
                        record.status,
                        "; ".join(record.notes),
                    )
                    for record in case.comparisons
                ),
            )
        )
        lines.append("")
    for group in (GROUP_CHAIN, GROUP_VSAM, GROUP_IDENTITY):
        selected = [record for record in case.assertions if record.group == group]
        if not selected:
            continue
        lines.extend([f"### {group}", ""])
        lines.extend(
            _table(
                ("Assertion", "Expected", "Observed", "Locator", "Verdict", "Notes"),
                (
                    (
                        record.name,
                        record.expected,
                        record.observed,
                        record.locator,
                        record.status,
                        "; ".join(record.notes),
                    )
                    for record in selected
                ),
            )
        )
        passed = all(record.passed for record in selected)
        lines.extend(
            [
                "",
                f"{group}: {'PASS' if passed else 'FAIL'} — {label}.",
                "",
            ]
        )
    unexpected = case.in_tolerance
    lines.append(
        f"unexpected_in_tolerance for {case.case}: "
        + (
            ", ".join(record.column for record in unexpected)
            if unexpected
            else "none"
        )
        + f" — {label}."
    )
    lines.append("")
    return lines



# --------------------------------------------------------------------------
# Gate artifact
# --------------------------------------------------------------------------
def read_gate_artifact(artifacts_dir: Path) -> dict[str, Any]:
    """Return what a gate artifact in ``artifacts_dir`` names, where one stands there.

    No file name is fixed by contract, so every regular file whose name begins with
    "gate" is considered, in sorted order, and the first one is read. The target
    word it names is recorded beside the target this run actually used. An absent
    artifact is recorded as absent and fails nothing.
    """
    try:
        candidates = sorted(
            path
            for path in artifacts_dir.iterdir()
            if path.is_file() and path.name.lower().startswith("gate")
        )
    except OSError:
        candidates = []
    if not candidates:
        return {
            "name": None,
            "note": f"no gate artifact stands in {_path_shown(artifacts_dir)}",
        }
    chosen = candidates[0]
    try:
        text = chosen.read_text(encoding="utf-8", errors="replace")[:8192]
    except OSError as error:
        return {
            "name": _path_shown(chosen),
            "note": (
                f"the gate artifact could not be read: "
                f"{_printable(error.strerror or type(error).__name__)}"
            ),
        }
    found = re.search(
        r"(?i)\b(duckdb|redshift|local[_-]substitute|local_branch)\b", text
    )
    return {
        "name": _path_shown(chosen),
        "target_named": found.group(1).lower() if found else None,
        "note": "read opportunistically; the target recorded below is the one used",
    }


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------
class _ArgumentParser(argparse.ArgumentParser):
    """``argparse.ArgumentParser`` reporting a rejected command line as a setting."""

    def error(self, message: str) -> Any:
        raise ConfigurationError(f"the command line was refused: {_printable(message)}")


_EXIT_HELP = """
exit statuses:
  0  every comparison passed; a non-zero delta inside the tolerance is reported
     in the unexpected_in_tolerance section and still returns 0
  1  a comparison failed
  2  a harness input is missing or incomplete, including an absent capture key a
     comparison needs and a capture snapshot the harness output differs from
  3  the warehouse content was refused: a canonical relation or column set other
     than the declared one, or other than exactly one row for a natural key
  4  a connection, configuration or usage failure; nothing is written
"""


def build_parser() -> _ArgumentParser:
    """Return the command-line parser of this tool."""
    parser = _ArgumentParser(
        prog=_PROGRAM,
        description=(
            "Compare the GnuCOBOL harness captures of a case with the two canonical "
            "warehouse rows for the same policy, column by column. Reads the harness "
            "output alone: no driver is started, no program is compiled and no chain "
            "is executed. Flow context: Figure 5 — Validation Harness Control Flow "
            "in modernization/docs/architecture.md."
        ),
        epilog=_EXIT_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        metavar="CASE",
        help=(
            "case to compare, repeatable. Supported: "
            f"{', '.join(SUPPORTED_CASES)}. Default: every supported case."
        ),
    )
    parser.add_argument(
        "--cases",
        default=None,
        metavar="CASE,CASE",
        help="the same selection as one comma-separated value.",
    )
    parser.add_argument(
        "--run-dir",
        default=DEFAULT_RUN_DIR,
        metavar="PATH",
        help=(
            "directory holding one subdirectory per case, each carrying "
            f"{CAPTURES_NAME} and {COMMAREA_POST_NAME}. Default: {DEFAULT_RUN_DIR}."
        ),
    )
    parser.add_argument(
        "--captures",
        default=None,
        metavar="PATH",
        help="capture file of a single case, replacing the run-directory path.",
    )
    parser.add_argument(
        "--commarea-post",
        default=None,
        metavar="PATH",
        help="returned COMMAREA of a single case, replacing the run-directory path.",
    )
    parser.add_argument(
        "--sample-record",
        default=None,
        metavar="PATH",
        help=(
            "record the driver was handed. Taken from the "
            f"{SAMPLE_PATH_VARIABLE} environment variable when absent, and then from "
            "the generated record of the case under the harness build tree."
        ),
    )
    parser.add_argument(
        "--field-map",
        default=DEFAULT_FIELD_MAP,
        metavar="PATH",
        help=f"metadata spine to read. Default: {DEFAULT_FIELD_MAP}.",
    )
    parser.add_argument(
        "--target",
        choices=TARGETS,
        default=None,
        help=(
            "warehouse to query. Default: the WAREHOUSE_TARGET environment variable, "
            f"then {TARGET_DUCKDB}."
        ),
    )
    parser.add_argument(
        "--database",
        default=None,
        metavar="PATH",
        help=(
            "DuckDB database file. Default: the LOCAL_DUCKDB_PATH and then the "
            f"DUCKDB_DATABASE environment variable, then {DEFAULT_DUCKDB_PATH}."
        ),
    )
    parser.add_argument(
        "--source-system-key",
        default=None,
        metavar="KEY",
        help=(
            "source-system discriminator to look up. Default: the SOURCE_SYSTEM_KEY "
            f"environment variable, then {DEFAULT_SOURCE_SYSTEM_KEY}."
        ),
    )
    parser.add_argument(
        "--report",
        default=DEFAULT_REPORT,
        metavar="PATH",
        help=f"Markdown report to write. Default: {DEFAULT_REPORT}.",
    )
    parser.add_argument(
        "--json",
        dest="json_report",
        default=DEFAULT_JSON_REPORT,
        metavar="PATH",
        help=f"JSON report to write. Default: {DEFAULT_JSON_REPORT}.",
    )
    parser.add_argument(
        "--expected-dir",
        default=DEFAULT_EXPECTED_DIR,
        metavar="PATH",
        help=(
            "directory of the per-case capture snapshots, one "
            f"{SNAPSHOT_NAME} per case. Default: {DEFAULT_EXPECTED_DIR}."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print the verdict line alone.",
    )
    return parser


class Settings(NamedTuple):
    """Every setting one run was invoked with, resolved."""

    cases: tuple[str, ...]
    run_dir: Path
    captures: Path | None
    commarea: Path | None
    sample: Path | None
    field_map: Path
    target: str
    database: Path
    source_system_key: str
    report: Path
    json_report: Path
    expected_dir: Path
    quiet: bool


def resolve_settings(arguments: argparse.Namespace) -> Settings:
    """Return the settings of one run, refusing a value this tool does not accept."""
    selected: list[str] = []
    for value in list(arguments.case) + (
        arguments.cases.split(",") if arguments.cases else []
    ):
        name = value.strip().upper()
        if not name:
            continue
        if name not in SUPPORTED_CASES:
            raise ConfigurationError(
                f"the case {_shown(name)} is not one of {_quote_all(SUPPORTED_CASES)}"
            )
        if name not in selected:
            selected.append(name)
    cases = (
        tuple(name for name in SUPPORTED_CASES if name in selected) or SUPPORTED_CASES
    )

    overrides = {
        "--captures": arguments.captures,
        "--commarea-post": arguments.commarea_post,
    }
    named = [option for option, value in overrides.items() if value]
    if named and len(cases) != 1:
        raise ConfigurationError(
            f"{_quote_all(named)} name the files of a single case; select one case "
            f"with --case or --cases"
        )

    target = (
        arguments.target
        or _environment_value("WAREHOUSE_TARGET")
        or TARGET_DUCKDB
    )
    if target not in TARGETS:
        raise ConfigurationError(
            f"the target {_shown(target)} is not one of {_quote_all(TARGETS)}"
        )
    database = _resolved(
        arguments.database
        or _environment_value("LOCAL_DUCKDB_PATH")
        or _environment_value("DUCKDB_DATABASE")
        or DEFAULT_DUCKDB_PATH
    )
    source_system_key = (
        (arguments.source_system_key or "").strip()
        or _environment_value("SOURCE_SYSTEM_KEY")
        or DEFAULT_SOURCE_SYSTEM_KEY
    )
    return Settings(
        cases=cases,
        run_dir=_resolved(arguments.run_dir),
        captures=_resolved(arguments.captures) if arguments.captures else None,
        commarea=(
            _resolved(arguments.commarea_post) if arguments.commarea_post else None
        ),
        sample=_resolved(arguments.sample_record) if arguments.sample_record else None,
        field_map=_resolved(arguments.field_map),
        target=target,
        database=database,
        source_system_key=source_system_key,
        report=_resolved(arguments.report),
        json_report=_resolved(arguments.json_report),
        expected_dir=_resolved(arguments.expected_dir),
        quiet=bool(arguments.quiet),
    )



# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------
def run(settings: Settings) -> RunReport:
    """Compare every selected case and return the report of the run.

    The field map is read and checked, the warehouse is opened, the canonical
    inventory is asserted once, and each case is then read and compared. A failure
    of one case is recorded against that case and the remaining cases are still
    compared, so one run reports the whole selection.
    """
    field_map = load_field_map(settings.field_map)
    warehouse = open_warehouse(settings.target, settings.database)
    report = RunReport(
        generated_at=datetime.datetime.now(datetime.UTC).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        target=settings.target,
        adapter=warehouse.adapter,
        adapter_version=warehouse.adapter_version,
        python_version=".".join(str(number) for number in sys.version_info[:3]),
        connection=warehouse.identity,
        source_system_key=settings.source_system_key,
        field_map=_path_shown(settings.field_map),
        run_dir=_path_shown(settings.run_dir),
        expected_dir=_path_shown(settings.expected_dir),
        requested_cases=settings.cases,
        local_substitute=warehouse.local_substitute,
        gate_artifact=read_gate_artifact(_resolved(ARTIFACTS_DIR)),
        return_codes=dict(field_map.return_codes),
    )
    try:
        try:
            report.inventory = assert_canonical_inventory(warehouse)
        except WarehouseError as error:
            report.errors.append(str(error))
            report.statuses.append(error.exit_status)
            return report
        for case in settings.cases:
            try:
                harness = read_harness_case(
                    case,
                    settings.run_dir,
                    field_map,
                    settings.captures,
                    settings.commarea,
                    settings.sample,
                )
                report.cases.append(
                    compare_case(
                        case,
                        harness,
                        warehouse,
                        field_map,
                        settings.source_system_key,
                        settings.expected_dir,
                    )
                )
            except DiffError as error:
                failed = CaseResult(case=case)
                failed.errors.append(str(error))
                failed.statuses.append(error.exit_status)
                report.cases.append(failed)
                report.errors.append(f"{case}: {error}")
    finally:
        warehouse.close()
    return report


def write_reports(report: RunReport, settings: Settings) -> None:
    """Write the Markdown and JSON reports of one run, replacing both in full."""
    _write_output(settings.report, render_markdown(report))
    _write_output(
        settings.json_report,
        json.dumps(report.as_document(), indent=2, sort_keys=True, ensure_ascii=True)
        + "\n",
    )


def print_summary(report: RunReport, settings: Settings) -> None:
    """Print the outcome of one run: the verdict line alone under --quiet."""
    verdict = (
        f"{_PROGRAM}: {report.verdict} - {len(report.cases)} case"
        f"{'' if len(report.cases) == 1 else 's'}, "
        f"{sum(len(case.comparisons) for case in report.cases)} of "
        f"{len(report.cases) * CANONICAL_COLUMN_INSTANCES} canonical column instances "
        f"compared, {sum(len(case.failed) for case in report.cases)} failed, "
        f"{len(report.in_tolerance)} unexpected in tolerance - {report.status_label}"
    )
    if settings.quiet:
        print(verdict)
        return
    for case in report.cases:
        print(
            f"{_PROGRAM}: {case.case} {case.verdict} - {case.coverage}, "
            f"{len(case.failed)} column failure"
            f"{'' if len(case.failed) == 1 else 's'}, "
            f"{len(case.failed_assertions)} assertion failure"
            f"{'' if len(case.failed_assertions) == 1 else 's'}, "
            f"unexpected_in_tolerance: "
            + (
                ", ".join(record.column for record in case.in_tolerance)
                if case.in_tolerance
                else "none"
            )
        )
        for record in case.failed:
            print(
                f"{_PROGRAM}:   {record.status} {record.relation}.{record.column}: "
                f"{'; '.join(record.notes)}",
                file=sys.stderr,
            )
        for assertion in case.failed_assertions:
            print(
                f"{_PROGRAM}:   {assertion.status} {assertion.group} "
                f"{assertion.name}: {'; '.join(assertion.notes)}",
                file=sys.stderr,
            )
        for message in case.errors:
            print(f"{_PROGRAM}:   {_printable(message)}", file=sys.stderr)
    print(f"{_PROGRAM}: markdown report {_path_shown(settings.report)}")
    print(f"{_PROGRAM}: json report {_path_shown(settings.json_report)}")
    print(verdict)
    if report.local_substitute:
        print(f"{_PROGRAM}: {AWS_OPEN_TEXT}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the comparison gate and return the status of the run."""
    try:
        arguments = build_parser().parse_args(list(argv) if argv is not None else None)
        settings = resolve_settings(arguments)
    except ConfigurationError as error:
        print(f"{_PROGRAM}: {_printable(str(error))}", file=sys.stderr)
        return EXIT_CONFIGURATION
    try:
        report = run(settings)
    except ConfigurationError as error:
        print(f"{_PROGRAM}: {_printable(str(error))}", file=sys.stderr)
        return EXIT_CONFIGURATION
    except DiffError as error:
        print(f"{_PROGRAM}: {_printable(str(error))}", file=sys.stderr)
        return error.exit_status
    try:
        write_reports(report, settings)
    except ConfigurationError as error:
        print(f"{_PROGRAM}: {_printable(str(error))}", file=sys.stderr)
        return EXIT_CONFIGURATION
    for message in report.errors:
        print(f"{_PROGRAM}: {_printable(message)}", file=sys.stderr)
    print_summary(report, settings)
    return report.exit_status


if __name__ == "__main__":
    sys.exit(main())

