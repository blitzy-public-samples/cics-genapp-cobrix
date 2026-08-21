#!/usr/bin/env python3
"""Load one landed GenApp Policy-Issue object into the local raw relation.

WHAT THIS TOOL DOES
    Downloads the single S3 object modernization/landing/land_to_s3.py wrote,
    confirms it still carries the landing contract, and writes it as one row of
    raw.genapp_policy_issue in a DuckDB database. The values written are the
    values the object carries: every one is bound as text or as SQL NULL exactly
    as landed, and no value is computed, scaled, rounded, padded, zero-filled,
    trimmed, defaulted or backfilled. The six amount values pass through
    untouched. Each of them reaches the landed object through one MOVE, at
    base/src/lgapdb01.cbl:265, 445, 489, 491, 493 and 495, and the three named
    programs carry no COMPUTE, MULTIPLY or DIVIDE statement and no COMP-3 item,
    so a loaded amount is the digit string the chain moved and nothing else.
    Typing is applied by the dbt models downstream, never here.

WHICH TARGET IT ADDRESSES
    The local branch of the bridge. On the real branch the same object and the
    same 17-column row shape reach the raw relation through
    modernization/landing/load_redshift.sql. This tool addresses a DuckDB
    database file and no warehouse service. Nothing it does depends on the local
    branch being in use:
    --endpoint-url, or the S3_ENDPOINT_URL environment variable, directs the
    download at a local S3-compatible endpoint, and with neither present the
    download addresses AWS S3. Access is established from resolved credentials
    and a resolved region; the presence of an environment variable whose name
    begins with AWS is never read as evidence of access, and no variable is
    matched on that prefix. Results this tool produces are local-substitute
    results and establish nothing about a real-target run.

WHICH INPUTS IT ACCEPTS
    --bucket        bucket holding the landed object, defaulting to the
                    S3_BUCKET environment variable. There is no built-in bucket
                    name.
    --key           exact object key, or the s3:// URI land_to_s3.py printed.
                    Omitted, the key is rebuilt from --source-system-key,
                    --entity and --extract-date.
    --source-system-key
                    source-system element of the landing prefix, defaulting to
                    the SOURCE_SYSTEM_KEY environment variable and then to
                    DEFAULT_SOURCE_SYSTEM_KEY. It must equal the object's own
                    source_system_key value.
    --entity        entity element of the landing prefix, defaulting to
                    DEFAULT_ENTITY.
    --extract-date  extract-date element of the landing prefix as YYYY-MM-DD,
                    defaulting to the current UTC date.
    --endpoint-url  S3 endpoint to address, defaulting to the S3_ENDPOINT_URL
                    environment variable. Absent on both, the download
                    addresses AWS S3.
    --region        region to address, defaulting to the AWS_REGION and then the
                    AWS_DEFAULT_REGION environment variable.
    --database      DuckDB database file, defaulting to the LOCAL_DUCKDB_PATH
                    and then the DUCKDB_DATABASE environment variable, and then
                    to modernization/validation/local.duckdb. A path inside this
                    tool's own directory is refused.
    --ddl           SQL scripts applied before the row is written, in the order
                    given, defaulting to every *.sql file in
                    modernization/warehouse/ddl sorted by name. --no-ddl applies
                    none.

WHERE IT WRITES
    One relation, raw.genapp_policy_issue, whose column names, column order and
    VARCHAR widths are defined by modernization/warehouse/ddl and whose 17
    column names and order this tool reads from
    modernization/landing/landing-schema.json. Within one transaction it removes
    any row already carrying the natural key (source_system_key, policy_number)
    of the object just downloaded and then writes that object as one row, so a
    repeated run leaves one row rather than two. No statement removes a row
    carrying any other natural key, so a row loaded from an earlier object
    survives every later run. On any failure the transaction is rolled back and
    the database is left as it was found.

    stdout carries exactly one line, naming the relation written, the natural
    key, and the rows removed and written. Every other message reaches stderr.
    No credential, token, session value or environment listing is ever printed,
    on any path.

HOW IT FAILS
    Every failure writes one control-free line to stderr and returns a non-zero
    status: 2 for a landed object that breaches the landing contract, 3 for a
    rejected command line or an unresolved setting, 4 for an S3 endpoint, bucket
    or object operation that did not succeed, 5 for a database or SQL operation
    that did not succeed. A missing setting is named in the diagnostic. A SQL
    statement that the database refused is reported as written, with its script
    and its position in that script. The tool never prompts and requires no TTY.

WHAT IT NEVER DOES
    It creates no bucket, cluster, workgroup, role, policy, network or key, and
    provisions nothing; a bucket that does not answer is reported, never
    created. It defines no relation of its own and restates no column type: the
    scripts named by --ddl are applied exactly as they are written and this tool
    adds no statement to them. It writes no relation but the one named above, no
    18th column, no load timestamp, no batch identifier and no audit column. It
    reads nothing under base/ and writes nothing under
    modernization/landing/.

WHERE THIS STEP SITS
    Figure 2 - AFTER (BUILT): Canonical Warehouse Bridge, and Figure 5 -
    Validation Harness Control Flow, both in
    modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple, NoReturn

import boto3.session
import duckdb
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    NoRegionError,
    PartialCredentialsError,
)

_PROGRAM = "load_local"

# Paths resolved from this script's own directory rather than from the working
# directory, so every working directory reads the same contract and reaches the
# same default database.
_THIS_DIR = Path(__file__).resolve().parent
_MODERNIZATION_DIR = _THIS_DIR.parent
DEFAULT_SCHEMA = _THIS_DIR / "landing-schema.json"
DEFAULT_DDL_DIRECTORY = _MODERNIZATION_DIR / "warehouse" / "ddl"
DEFAULT_DATABASE = _MODERNIZATION_DIR / "validation" / "local.duckdb"

# Pattern selecting the default DDL scripts, applied in sorted name order.
DDL_GLOB = "*.sql"

# Environment variables consulted when the matching option is omitted. No value
# read from any of them is ever printed.
BUCKET_VARIABLE = "S3_BUCKET"
ENDPOINT_URL_VARIABLE = "S3_ENDPOINT_URL"
SOURCE_SYSTEM_KEY_VARIABLE = "SOURCE_SYSTEM_KEY"
REGION_VARIABLES = ("AWS_REGION", "AWS_DEFAULT_REGION")
DATABASE_VARIABLES = ("LOCAL_DUCKDB_PATH", "DUCKDB_DATABASE")

# Environment variables naming the credentials a boto3 session resolves for
# itself. They are named in diagnostics and are never read by this module.
CREDENTIAL_VARIABLES = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")

# Landing prefix parts. The key is LANDING_KEY_ROOT, then one Hive-style segment
# per entry of PARTITION_FIELDS in this order, then OBJECT_NAME.
LANDING_KEY_ROOT = "landing"
PARTITION_FIELDS = ("source_system_key", "entity", "extract_date")
OBJECT_NAME = "part-0000.json"
KEY_SEPARATOR = "/"

# Values used when the matching option and environment variable are both absent.
DEFAULT_SOURCE_SYSTEM_KEY = "GENAPP_CLASS_EXEMPLAR"
DEFAULT_ENTITY = "policy_issue"

# Service addressed, and the URI form --key also accepts.
SERVICE_NAME = "s3"
URI_SCHEME_SEPARATOR = "://"

# Relation written, and the fields whose values identify one row of it. Both
# names are confirmed against _IDENTIFIER_SHAPE before they reach any statement.
RAW_SCHEMA_NAME = "raw"
RAW_TABLE_NAME = "genapp_policy_issue"
NATURAL_KEY_FIELDS = ("source_system_key", "policy_number")

# Keys the landed object carries. The names and their order are read from the
# properties block of the landing schema; this count is the invariant that
# reading is confirmed against.
EXPECTED_COLUMN_COUNT = 17

# Accepted shapes. A partition segment value becomes one path segment, so it
# carries no separator, no whitespace and no equals sign. A bucket name becomes
# the authority of a reported URI under the same restriction. An identifier
# becomes SQL text and so is confirmed rather than bound.
_SEGMENT_SHAPE = re.compile(r"\A[A-Za-z0-9_.\-]+\Z")
_BUCKET_SHAPE = re.compile(r"\A[A-Za-z0-9_.\-]+\Z")
_IDENTIFIER_SHAPE = re.compile(r"\A[a-z][a-z0-9_]*\Z")
MAX_SEGMENT_CHARACTERS = 64
MIN_BUCKET_CHARACTERS = 3
MAX_BUCKET_CHARACTERS = 63
MAX_IDENTIFIER_CHARACTERS = 63

# Extract date form accepted on the command line and emitted into the key.
EXTRACT_DATE_FORM = "YYYY-MM-DD"

# Bytes one read takes from the landed object and from the schema before
# anything parses them, and the bytes one read asks for at a time.
MAX_OBJECT_BYTES = 1024 * 1024
MAX_SCHEMA_BYTES = 4 * 1024 * 1024
MAX_DDL_BYTES = 1024 * 1024
READ_CHUNK_BYTES = 65536

# Rows one load removes and writes. A load carries one object, which carries one
# record.
EXPECTED_INSERTED_ROWS = 1

# Connection behaviour applied to every request, bounding the time a failing
# endpoint can hold up the caller.
CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 3
RETRY_MODE = "standard"

EXIT_OK = 0
EXIT_OBJECT_REJECTED = 2
EXIT_CONFIGURATION_REJECTED = 3
EXIT_S3_UNAVAILABLE = 4
EXIT_WAREHOUSE_UNAVAILABLE = 5
EXIT_INTERRUPTED = 130

# Characters of untrusted text one diagnostic fragment carries before
# truncation, and the keys one diagnostic names.
MAX_DIAGNOSTIC_CHARACTERS = 64
MAX_DIAGNOSTIC_PATH_CHARACTERS = 160
MAX_DIAGNOSTIC_MESSAGE_CHARACTERS = 200
MAX_DIAGNOSTIC_STATEMENT_CHARACTERS = 400
MAX_REPORTED_KEYS = 8

# Characters escaped out of a diagnostic.
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f-\x9f]")

# Client error codes reported with a specific diagnostic.
_CODES_BUCKET_ABSENT = frozenset({"404", "NoSuchBucket", "NotFound"})
_CODES_OBJECT_ABSENT = frozenset({"NoSuchKey"})
_CODES_ACCESS_DENIED = frozenset(
    {"403", "AccessDenied", "AllAccessDisabled", "Forbidden"}
)
_CODES_WRONG_REGION = frozenset(
    {"301", "PermanentRedirect", "IllegalLocationConstraint"}
)
_CODES_CREDENTIALS_REJECTED = frozenset(
    {"InvalidAccessKeyId", "SignatureDoesNotMatch", "InvalidClientTokenId"}
)


class LoadError(Exception):
    """Diagnostic raised by this module, carrying the process status to return."""

    exit_status = EXIT_OBJECT_REJECTED


class ObjectError(LoadError):
    """The landed object breaches the landing contract."""

    exit_status = EXIT_OBJECT_REJECTED


class ConfigurationError(LoadError):
    """A required setting is absent or carries a rejected value."""

    exit_status = EXIT_CONFIGURATION_REJECTED


class UsageError(ConfigurationError):
    """The command line omits a required argument or carries a rejected value."""

    exit_status = EXIT_CONFIGURATION_REJECTED


class SchemaError(ConfigurationError):
    """The landing schema cannot be read or does not name the landed columns."""

    exit_status = EXIT_CONFIGURATION_REJECTED


class AccessError(LoadError):
    """An S3 endpoint, bucket or object operation did not succeed."""

    exit_status = EXIT_S3_UNAVAILABLE


class WarehouseError(LoadError):
    """A database or SQL operation did not succeed."""

    exit_status = EXIT_WAREHOUSE_UNAVAILABLE


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def _type_name(value: Any) -> str:
    """Return the type name of ``value`` for use inside a diagnostic."""
    return type(value).__name__


def _escaped_character(character: str) -> str:
    """Return one printable 7-bit ASCII rendering of ``character``."""
    if " " <= character <= "~":
        return character
    codepoint = ord(character)
    if codepoint <= 0xFF:
        return f"\\x{codepoint:02x}"
    if codepoint <= 0xFFFF:
        return f"\\u{codepoint:04x}"
    return f"\\U{codepoint:08x}"


def _one_line(text: str) -> str:
    """Return ``text`` with every control character replaced by an escape."""
    return _CONTROL_CHARACTERS.sub(
        lambda match: _escaped_character(match.group()), text
    )


def _escaped(text: str, limit: int = MAX_DIAGNOSTIC_CHARACTERS) -> str:
    """Return ``text`` as one printable 7-bit ASCII fragment of at most ``limit``.

    Characters past ``limit`` are dropped and the fragment records how many were
    dropped. A fragment never spans more than one line.
    """
    kept = text[: max(limit, 1)]
    rendered = "".join(_escaped_character(character) for character in kept)
    dropped = len(text) - len(kept)
    if dropped:
        return f"{rendered}...(+{dropped} characters)"
    return rendered


def _shown(value: str, limit: int = MAX_DIAGNOSTIC_CHARACTERS) -> str:
    """Return ``value`` quoted and escaped for a diagnostic."""
    return f"'{_escaped(value, limit)}'"


def _path_shown(path: str | os.PathLike[str]) -> str:
    """Return ``path`` quoted and escaped for a diagnostic."""
    return _shown(os.fspath(path), MAX_DIAGNOSTIC_PATH_CHARACTERS)


def _display(value: Any) -> str:
    """Return any value rendered for a diagnostic, quoting text and naming a type."""
    if isinstance(value, str):
        return _shown(value)
    if value is None or isinstance(value, (bool, int, float)):
        return str(value)
    return f"a {_type_name(value)}"


def _reason(error: BaseException) -> str:
    """Return the reason text of ``error`` as one bounded diagnostic fragment."""
    text = str(error) or _type_name(error)
    return _escaped(text, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)


def _listed(names: Sequence[str]) -> str:
    """Return ``names`` as one comma-separated fragment of at most MAX_REPORTED_KEYS.

    Names past the limit are dropped and the fragment records how many were
    dropped, so a wildly wrong input cannot produce an unbounded diagnostic.
    """
    kept = [_shown(name) for name in names[:MAX_REPORTED_KEYS]]
    dropped = len(names) - len(kept)
    if dropped > 0:
        kept.append(f"and {dropped} more")
    return ", ".join(kept)


def _warn(message: str) -> None:
    """Write one control-free warning line to stderr."""
    print(f"{_PROGRAM}: warning: {_one_line(message)}", file=sys.stderr)


def _note(message: str) -> None:
    """Write one control-free progress line to stderr."""
    print(f"{_PROGRAM}: {_one_line(message)}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Landed column names
# ---------------------------------------------------------------------------


def _read_bounded_bytes(path: Path, limit: int, what: str) -> bytes:
    """Return the content of ``path``, refusing anything longer than ``limit`` bytes.

    One byte past ``limit`` is requested, so an oversized input is reported
    without being held in memory in full. ``what`` names the input in any
    diagnostic.

    Raises ``ConfigurationError`` when the file is empty, longer than ``limit``,
    or cannot be opened or read.
    """
    try:
        with Path(path).open("rb") as stream:
            chunks: list[bytes] = []
            remaining = limit + 1
            while remaining > 0:
                chunk = stream.read(min(READ_CHUNK_BYTES, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
    except OSError as error:
        raise ConfigurationError(
            f"the {what} cannot be read: {_path_shown(path)}: {_reason(error)}"
        ) from error
    content = b"".join(chunks)
    if not content:
        raise ConfigurationError(f"the {what} is empty: {_path_shown(path)}")
    if len(content) > limit:
        raise ConfigurationError(
            f"the {what} holds more than the accepted {limit} bytes: "
            f"{_path_shown(path)}"
        )
    return content


def load_schema(path: Path = DEFAULT_SCHEMA) -> Mapping[str, Any]:
    """Return the landing schema document read from ``path``.

    Raises ``SchemaError`` when the file is missing, empty, larger than
    ``MAX_SCHEMA_BYTES``, not valid UTF-8, not well-formed JSON, or not a JSON
    object.
    """
    try:
        raw = _read_bounded_bytes(path, MAX_SCHEMA_BYTES, "landing schema")
    except ConfigurationError as error:
        raise SchemaError(str(error)) from error
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SchemaError(
            f"the landing schema is not readable JSON: {_path_shown(path)}: "
            f"{_reason(error)}"
        ) from error
    if not isinstance(document, dict):
        raise SchemaError(
            f"the landing schema carries {_display(document)} at its top level: "
            f"{_path_shown(path)}; a JSON object is required"
        )
    return document


def _confirmed_identifier(name: str, what: str) -> str:
    """Return ``name`` confirmed usable as one unquoted SQL identifier.

    An identifier reaches a statement as SQL text rather than as a bound value,
    so it is confirmed to start with an ASCII lower-case letter and to carry
    only ASCII lower-case letters, digits and underscores, in at most
    ``MAX_IDENTIFIER_CHARACTERS`` characters.

    Raises ``SchemaError`` when ``name`` carries any other shape.
    """
    if not name:
        raise SchemaError(f"the {what} is empty")
    if len(name) > MAX_IDENTIFIER_CHARACTERS:
        raise SchemaError(
            f"the {what} holds {len(name)} characters: {_shown(name)}; at most "
            f"{MAX_IDENTIFIER_CHARACTERS} are accepted"
        )
    if not _IDENTIFIER_SHAPE.fullmatch(name):
        raise SchemaError(
            f"the {what} is not an unquoted SQL identifier: {_shown(name)}; an "
            "ASCII lower-case letter followed by ASCII lower-case letters, "
            "digits and underscores is accepted"
        )
    return name


def read_column_names(
    schema: Mapping[str, Any], path: Path = DEFAULT_SCHEMA
) -> tuple[str, ...]:
    """Return the landed column names, in the order the schema declares them.

    The order is the order of the schema's ``properties`` block, which is the
    order of the row written. When the schema also carries a ``required`` list,
    that list is confirmed to hold the same names as ``properties``, in the same
    order. The returned count is confirmed to be ``EXPECTED_COLUMN_COUNT`` and
    every name is confirmed usable as one unquoted SQL identifier.

    Raises ``SchemaError`` when the schema carries no usable ``properties``
    block, declares a name that is not an identifier, disagrees with its own
    ``required`` list, or declares a different number of columns.
    """
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise SchemaError(
            f"the landing schema carries no properties object: {_path_shown(path)}; "
            "the landed column names and their order are read from it"
        )
    names = tuple(
        _confirmed_identifier(str(name), "landed column name") for name in properties
    )
    if len(names) != EXPECTED_COLUMN_COUNT:
        raise SchemaError(
            f"the landing schema declares {len(names)} properties: "
            f"{_path_shown(path)}; {EXPECTED_COLUMN_COUNT} landed columns are "
            f"expected: {_listed(list(names))}"
        )
    if len(set(names)) != len(names):
        raise SchemaError(
            f"the landing schema declares a repeated property name: "
            f"{_path_shown(path)}: {_listed(list(names))}"
        )
    required = schema.get("required")
    if isinstance(required, list):
        declared = tuple(str(name) for name in required)
        if declared != names:
            raise SchemaError(
                f"the landing schema's required list and properties block do not "
                f"agree: {_path_shown(path)}; required carries "
                f"{_listed(list(declared))} and properties carries "
                f"{_listed(list(names))}"
            )
    for field in NATURAL_KEY_FIELDS:
        if field not in names:
            raise SchemaError(
                f"the landing schema declares no {_shown(field)} property: "
                f"{_path_shown(path)}; it is part of the natural key of the "
                "loaded row"
            )
    return names


def landed_column_names(path: Path = DEFAULT_SCHEMA) -> tuple[str, ...]:
    """Return the landed column names read from the landing schema at ``path``.

    Raises ``SchemaError`` when the schema cannot be read or does not declare
    the landed columns.
    """
    return read_column_names(load_schema(path), path)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


def _from_environment(names: Sequence[str]) -> tuple[str | None, str | None]:
    """Return the first non-empty value among ``names`` and the name that carried it.

    A variable that is set to the empty string is passed over. Returns
    ``(None, None)`` when no name carries a value. Only the name is ever quoted
    in a diagnostic.
    """
    for name in names:
        value = os.environ.get(name)
        if value:
            return value, name
    return None, None


def _resolved(
    supplied: str | None, option: str, variables: Sequence[str]
) -> tuple[str | None, str]:
    """Return the effective value for one setting and the origin it came from.

    ``supplied`` is the command-line value, which wins whenever it is present,
    and ``variables`` are consulted in order after it. The origin is the option
    name, the variable name, or ``'no setting'`` when neither carried a value.
    """
    if supplied is not None:
        return supplied, option
    value, name = _from_environment(variables)
    if value is not None and name is not None:
        return value, f"the {name} environment variable"
    return None, "no setting"


def _require_segment(value: str, what: str, origin: str) -> str:
    """Return ``value`` confirmed usable as one path segment of the landing key.

    A segment carries 1 to ``MAX_SEGMENT_CHARACTERS`` characters drawn from
    ASCII letters, digits, underscore, dot and hyphen, which admits no
    separator, no whitespace and no equals sign.

    Raises ``ConfigurationError`` when ``value`` is empty, too long, or carries
    any other character.
    """
    if not value:
        raise ConfigurationError(f"the {what} from {origin} is empty")
    if len(value) > MAX_SEGMENT_CHARACTERS:
        raise ConfigurationError(
            f"the {what} from {origin} holds {len(value)} characters: "
            f"{_shown(value)}; at most {MAX_SEGMENT_CHARACTERS} are accepted"
        )
    if not _SEGMENT_SHAPE.fullmatch(value):
        raise ConfigurationError(
            f"the {what} from {origin} carries a character outside ASCII letters, "
            f"digits, underscore, dot and hyphen: {_shown(value)}; it becomes one "
            "segment of the landing key"
        )
    return value


def _require_bucket(value: str, origin: str) -> str:
    """Return ``value`` confirmed usable as a bucket name and URI authority.

    Raises ``ConfigurationError`` when the value is shorter than
    ``MIN_BUCKET_CHARACTERS``, longer than ``MAX_BUCKET_CHARACTERS`` or carries a
    character that could not appear in a reported URI.
    """
    if not (MIN_BUCKET_CHARACTERS <= len(value) <= MAX_BUCKET_CHARACTERS):
        raise ConfigurationError(
            f"the bucket name from {origin} holds {len(value)} characters: "
            f"{_shown(value)}; between {MIN_BUCKET_CHARACTERS} and "
            f"{MAX_BUCKET_CHARACTERS} are accepted"
        )
    if not _BUCKET_SHAPE.fullmatch(value):
        raise ConfigurationError(
            f"the bucket name from {origin} carries a character outside ASCII "
            f"letters, digits, underscore, dot and hyphen: {_shown(value)}"
        )
    return value


def resolve_bucket(supplied: str | None) -> str:
    """Return the bucket holding the landed object, taking the first setting present.

    ``supplied`` is the ``--bucket`` value, and the ``S3_BUCKET`` environment
    variable is consulted when it is absent. There is no built-in bucket name.

    Raises ``ConfigurationError`` when neither carries a value, or when the
    value cannot be a bucket name.
    """
    value, origin = _resolved(supplied, "--bucket", (BUCKET_VARIABLE,))
    if value is None:
        raise ConfigurationError(
            "no bucket is set: supply --bucket or set the "
            f"{BUCKET_VARIABLE} environment variable to the bucket holding the "
            "landed object; this tool creates none"
        )
    return _require_bucket(value, origin)


def resolve_source_system_key(supplied: str | None) -> str:
    """Return the source-system key forming the prefix, and the object's own value.

    ``supplied`` is the ``--source-system-key`` value; the
    ``SOURCE_SYSTEM_KEY`` environment variable is consulted when it is absent,
    and ``DEFAULT_SOURCE_SYSTEM_KEY`` when neither carries a value.

    Raises ``ConfigurationError`` when the resolved value cannot form one path
    segment.
    """
    value, origin = _resolved(
        supplied, "--source-system-key", (SOURCE_SYSTEM_KEY_VARIABLE,)
    )
    if value is None:
        value, origin = DEFAULT_SOURCE_SYSTEM_KEY, "the built-in default"
    return _require_segment(value, "source-system key", origin)


def resolve_entity(supplied: str | None) -> str:
    """Return the entity element of the landing prefix.

    ``supplied`` is the ``--entity`` value and ``DEFAULT_ENTITY`` applies when
    it is absent.

    Raises ``ConfigurationError`` when the resolved value cannot form one path
    segment.
    """
    if supplied is None:
        return _require_segment(DEFAULT_ENTITY, "entity", "the built-in default")
    return _require_segment(supplied, "entity", "--entity")


def resolve_extract_date(supplied: str | None) -> datetime.date:
    """Return the extract date forming the prefix, as a date.

    ``supplied`` is the ``--extract-date`` value, which must be written exactly
    ``EXTRACT_DATE_FORM``; the current UTC date applies when it is absent. A
    value that parses as some other ISO 8601 form is refused, so the key segment
    and the date the caller wrote always agree character for character.

    Raises ``ConfigurationError`` when ``supplied`` is not a calendar date
    written in that form.
    """
    if supplied is None:
        return datetime.datetime.now(datetime.timezone.utc).date()
    try:
        parsed = datetime.date.fromisoformat(supplied)
    except ValueError as error:
        raise ConfigurationError(
            "the extract date from --extract-date is not a calendar date written "
            f"{EXTRACT_DATE_FORM}: {_shown(supplied)}: {_reason(error)}"
        ) from error
    if parsed.isoformat() != supplied:
        raise ConfigurationError(
            "the extract date from --extract-date is not written "
            f"{EXTRACT_DATE_FORM}: {_shown(supplied)}; "
            f"{_shown(parsed.isoformat())} is the accepted form of that date"
        )
    return parsed


def resolve_endpoint_url(supplied: str | None) -> str | None:
    """Return the S3 endpoint to address, or None to address AWS S3.

    ``supplied`` is the ``--endpoint-url`` value and the ``S3_ENDPOINT_URL``
    environment variable is consulted when it is absent. A returned value
    directs the client at that endpoint; None leaves the client addressing AWS
    S3.

    Raises ``ConfigurationError`` when the resolved value carries no scheme
    separator or carries whitespace.
    """
    value, origin = _resolved(supplied, "--endpoint-url", (ENDPOINT_URL_VARIABLE,))
    if value is None:
        return None
    scheme, separator, _ = value.partition(URI_SCHEME_SEPARATOR)
    if not separator or not scheme:
        raise ConfigurationError(
            f"the endpoint from {origin} is not an absolute URL: {_shown(value)}; a "
            "scheme such as http or https is required"
        )
    if any(character.isspace() for character in value):
        raise ConfigurationError(
            f"the endpoint from {origin} carries whitespace: {_shown(value)}"
        )
    return value


def resolve_region(supplied: str | None) -> str | None:
    """Return the region to address, or None to leave the session to resolve one.

    ``supplied`` is the ``--region`` value; ``AWS_REGION`` and then
    ``AWS_DEFAULT_REGION`` are consulted when it is absent. Returning None hands
    the resolution to the boto3 session, whose own answer is confirmed later.

    Raises ``ConfigurationError`` when the resolved value is empty or carries
    whitespace.
    """
    value, origin = _resolved(supplied, "--region", REGION_VARIABLES)
    if value is None:
        return None
    if not value or any(character.isspace() for character in value):
        raise ConfigurationError(
            f"the region from {origin} is empty or carries whitespace: {_shown(value)}"
        )
    return value


def resolve_database_path(supplied: str | None) -> Path:
    """Return the DuckDB database file to open.

    ``supplied`` is the ``--database`` value; ``LOCAL_DUCKDB_PATH`` and then
    ``DUCKDB_DATABASE`` are consulted when it is absent, and ``DEFAULT_DATABASE``
    when none carries a value. A path inside this tool's own directory is
    refused, and an in-memory database is refused, so a load always reaches a
    file a later step can read.

    Raises ``ConfigurationError`` when the resolved value is empty, names this
    tool's own directory, or names an in-memory database.
    """
    value, origin = _resolved(supplied, "--database", DATABASE_VARIABLES)
    if value is None:
        return DEFAULT_DATABASE
    if not value.strip():
        raise ConfigurationError(f"the database path from {origin} is empty")
    if value == ":memory:":
        raise ConfigurationError(
            f"the database path from {origin} names an in-memory database: "
            f"{_shown(value)}; a file the following step can read is required"
        )
    candidate = Path(value).expanduser()
    resolved = candidate if candidate.is_absolute() else Path.cwd() / candidate
    if _THIS_DIR == resolved.parent or _THIS_DIR in resolved.parents:
        raise ConfigurationError(
            f"the database path from {origin} is inside {_path_shown(_THIS_DIR)}: "
            f"{_path_shown(value)}; {_path_shown(DEFAULT_DATABASE)} is the path "
            "this bridge keeps its local database at"
        )
    return candidate


def resolve_ddl_paths(
    supplied: Sequence[str] | None, apply_ddl: bool
) -> tuple[Path, ...]:
    """Return the SQL scripts to apply before the row is written, in apply order.

    ``supplied`` names the scripts in the order given. With ``supplied`` empty or
    None, every ``DDL_GLOB`` match in ``DEFAULT_DDL_DIRECTORY`` is returned in
    sorted name order. With ``apply_ddl`` false, no script is returned and none
    is read.

    Raises ``ConfigurationError`` when a named script is absent or is not a
    file, or when the default directory holds no match.
    """
    if not apply_ddl:
        return ()
    if supplied:
        paths = tuple(Path(name).expanduser() for name in supplied)
        for path in paths:
            if not path.is_file():
                raise ConfigurationError(
                    f"the SQL script named by --ddl is not a readable file: "
                    f"{_path_shown(path)}"
                )
        return paths
    if not DEFAULT_DDL_DIRECTORY.is_dir():
        raise ConfigurationError(
            f"the default SQL script directory is absent: "
            f"{_path_shown(DEFAULT_DDL_DIRECTORY)}; supply --ddl with the scripts "
            "defining the raw relation, or --no-ddl to apply none"
        )
    found = tuple(sorted(DEFAULT_DDL_DIRECTORY.glob(DDL_GLOB)))
    if not found:
        raise ConfigurationError(
            f"the default SQL script directory holds no {DDL_GLOB} file: "
            f"{_path_shown(DEFAULT_DDL_DIRECTORY)}; supply --ddl with the scripts "
            "defining the raw relation, or --no-ddl to apply none"
        )
    return found


# ---------------------------------------------------------------------------
# Key construction
# ---------------------------------------------------------------------------


def build_landing_key(
    source_system_key: str, entity: str, extract_date: datetime.date
) -> str:
    """Return the landing object key for one extract.

    The key is ``LANDING_KEY_ROOT``, then one Hive-style ``field=value`` segment
    per entry of ``PARTITION_FIELDS`` in that order, then ``OBJECT_NAME``, with
    no leading separator, no empty segment and no percent-encoding of the equals
    sign. The date is written as ``EXTRACT_DATE_FORM``. This is the key
    land_to_s3.py writes for the same three values.

    Raises ``ConfigurationError`` when a supplied value cannot form one path
    segment.
    """
    values = {
        "source_system_key": _require_segment(
            source_system_key, "source-system key", "the caller"
        ),
        "entity": _require_segment(entity, "entity", "the caller"),
        "extract_date": extract_date.isoformat(),
    }
    segments = [LANDING_KEY_ROOT]
    segments.extend(f"{field}={values[field]}" for field in PARTITION_FIELDS)
    segments.append(OBJECT_NAME)
    return KEY_SEPARATOR.join(segments)


def build_object_uri(bucket: str, key: str) -> str:
    """Return the ``s3://`` URI naming the object ``key`` in ``bucket``."""
    return f"{SERVICE_NAME}{URI_SCHEME_SEPARATOR}{bucket}{KEY_SEPARATOR}{key}"


def parse_object_reference(supplied: str, bucket: str) -> str:
    """Return the object key ``supplied`` names, confirming any bucket it carries.

    ``supplied`` is either a bare object key or the ``s3://bucket/key`` URI
    land_to_s3.py prints, so the line that step wrote can be passed straight in.
    A URI's authority must equal ``bucket``. A leading separator is refused
    rather than trimmed, and so is a key carrying an empty segment, whitespace or
    a control character, so the key requested is the key the caller wrote.

    Raises ``ConfigurationError`` when ``supplied`` is empty, names another
    bucket, carries another URI scheme, or is not a usable object key.
    """
    text = supplied
    if URI_SCHEME_SEPARATOR in text:
        scheme, remainder = text.split(URI_SCHEME_SEPARATOR, 1)
        if scheme != SERVICE_NAME:
            raise ConfigurationError(
                f"the object from --key carries the URI scheme {_shown(scheme)}: "
                f"{_shown(text, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; a bare object key "
                f"or a {SERVICE_NAME}{URI_SCHEME_SEPARATOR} URI is accepted"
            )
        authority, separator, remainder = remainder.partition(KEY_SEPARATOR)
        if not separator or not remainder:
            raise ConfigurationError(
                "the object from --key names no key inside its bucket: "
                f"{_shown(text, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
            )
        if authority != bucket:
            raise ConfigurationError(
                f"the object from --key names bucket {_shown(authority)} while the "
                f"resolved bucket is {_shown(bucket)}; the two must agree"
            )
        text = remainder
    if not text:
        raise ConfigurationError("the object from --key is empty")
    if text.startswith(KEY_SEPARATOR):
        raise ConfigurationError(
            "the object from --key starts with a separator: "
            f"{_shown(text, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; a landing key carries "
            "no leading separator"
        )
    if any(character.isspace() for character in text):
        raise ConfigurationError(
            "the object from --key carries whitespace: "
            f"{_shown(text, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
        )
    if _CONTROL_CHARACTERS.search(text):
        raise ConfigurationError(
            "the object from --key carries a control character: "
            f"{_shown(text, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
        )
    if f"{KEY_SEPARATOR}{KEY_SEPARATOR}" in text:
        raise ConfigurationError(
            "the object from --key carries an empty segment: "
            f"{_shown(text, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
        )
    return text


def resolve_object_key(
    supplied: str | None,
    bucket: str,
    source_system_key: str,
    entity: str,
    extract_date: datetime.date,
) -> str:
    """Return the key of the object to download.

    ``supplied`` is the ``--key`` value, accepted as a bare key or as the
    ``s3://`` URI land_to_s3.py printed. With ``supplied`` absent the key is
    rebuilt from ``source_system_key``, ``entity`` and ``extract_date``, giving
    the same key that step wrote for those three values.

    Raises ``ConfigurationError`` when ``supplied`` is not a usable object
    reference or when a rebuilt segment is not usable.
    """
    if supplied is not None:
        return parse_object_reference(supplied, bucket)
    return build_landing_key(source_system_key, entity, extract_date)


# ---------------------------------------------------------------------------
# Client, credentials and access
# ---------------------------------------------------------------------------


def _client_config() -> Config:
    """Return the connection behaviour applied to every request.

    A failing endpoint is abandoned after ``CONNECT_TIMEOUT_SECONDS`` and a
    stalled response after ``READ_TIMEOUT_SECONDS``, with at most
    ``MAX_ATTEMPTS`` attempts, so an unreachable target cannot hold the caller
    open indefinitely.
    """
    return Config(
        connect_timeout=CONNECT_TIMEOUT_SECONDS,
        read_timeout=READ_TIMEOUT_SECONDS,
        retries={"max_attempts": MAX_ATTEMPTS, "mode": RETRY_MODE},
    )


def _client_error_code(error: ClientError) -> str:
    """Return the service error code ``error`` carries, or the empty string."""
    response = getattr(error, "response", None)
    if isinstance(response, Mapping):
        detail = response.get("Error")
        if isinstance(detail, Mapping):
            code = detail.get("Code")
            if isinstance(code, str):
                return code
    return ""


def _missing_credentials_message() -> str:
    """Return the diagnostic naming the credential settings that must be supplied."""
    return (
        "no credentials are resolved: set "
        f"{' and '.join(CREDENTIAL_VARIABLES)} in the environment, or configure a "
        "profile the session can read. An environment variable whose name merely "
        "begins with AWS is not a credential and is never read as one"
    )


def _missing_region_message() -> str:
    """Return the diagnostic naming the region settings that must be supplied."""
    return (
        "no region is resolved: supply --region or set "
        f"{' or '.join(REGION_VARIABLES)} in the environment"
    )


def _failure_for(error: BaseException, bucket: str, action: str) -> LoadError:
    """Return the diagnostic for an S3 ``action`` on ``bucket`` that did not succeed.

    A credential problem becomes a ``ConfigurationError`` naming the settings to
    supply; every other failure becomes an ``AccessError``. The returned
    diagnostic carries no credential, token or endpoint value.
    """
    if isinstance(error, NoCredentialsError):
        return ConfigurationError(f"cannot {action}: {_missing_credentials_message()}")
    if isinstance(error, PartialCredentialsError):
        return ConfigurationError(
            f"cannot {action}: the resolved credentials are incomplete: "
            f"{_reason(error)}; set {' and '.join(CREDENTIAL_VARIABLES)} together"
        )
    if isinstance(error, NoRegionError):
        return ConfigurationError(f"cannot {action}: {_missing_region_message()}")
    if isinstance(error, EndpointConnectionError):
        return AccessError(
            f"cannot {action}: the S3 endpoint refused the connection. A local "
            "endpoint must already be listening on the address "
            f"{ENDPOINT_URL_VARIABLE} or --endpoint-url names"
        )
    if isinstance(error, ClientError):
        code = _client_error_code(error)
        if code in _CODES_OBJECT_ABSENT:
            return AccessError(
                f"cannot {action}: no such object is in bucket {_shown(bucket)}; "
                "land the record first, or name the object land_to_s3.py wrote "
                "through --key"
            )
        if code in _CODES_BUCKET_ABSENT:
            return AccessError(
                f"cannot {action}: bucket {_shown(bucket)} or the object in it does "
                "not exist or is not visible to the resolved credentials; supply an "
                "existing bucket, which this tool never creates"
            )
        if code in _CODES_ACCESS_DENIED:
            return AccessError(
                f"cannot {action}: the resolved credentials are not permitted on "
                f"bucket {_shown(bucket)}"
            )
        if code in _CODES_WRONG_REGION:
            return AccessError(
                f"cannot {action}: bucket {_shown(bucket)} is not in the region being "
                "addressed; supply the bucket's own region through --region"
            )
        if code in _CODES_CREDENTIALS_REJECTED:
            return ConfigurationError(
                f"cannot {action}: the endpoint rejected the resolved credentials "
                f"with {_shown(code)}"
            )
        return AccessError(
            f"cannot {action} on bucket {_shown(bucket)}: the endpoint answered "
            f"{_shown(code) if code else 'an error'}: {_reason(error)}"
        )
    return AccessError(f"cannot {action} on bucket {_shown(bucket)}: {_reason(error)}")


def build_session(region: str | None = None) -> boto3.session.Session:
    """Return a boto3 session, pinned to ``region`` when one was resolved.

    Passing None leaves the session to resolve a region for itself, which
    ``resolve_session_region`` then confirms. No credential value is passed in:
    the session resolves credentials through its own providers.

    Raises ``ConfigurationError`` when the session cannot be constructed.
    """
    try:
        if region is None:
            return boto3.session.Session()
        return boto3.session.Session(region_name=region)
    except BotoCoreError as error:
        raise ConfigurationError(
            f"the S3 session cannot be created: {_reason(error)}"
        ) from error


def resolve_session_region(session: boto3.session.Session) -> str:
    """Return the region ``session`` resolves, refusing an unresolved one.

    Raises ``ConfigurationError`` naming the settings to supply when the session
    resolves no region.
    """
    region = session.region_name
    if not region:
        raise ConfigurationError(_missing_region_message())
    return region


def confirm_credentials(session: boto3.session.Session) -> None:
    """Confirm ``session`` resolves a usable set of credentials.

    The session's own providers do the resolving, so a variable whose name
    merely begins with AWS is never taken for a credential. An incomplete set
    surfaces as ``PartialCredentialsError`` from that resolution. Returns None
    once a credential set is resolved; no credential value is read beyond
    confirming one is present, and none is ever printed.

    Raises ``ConfigurationError`` naming the settings to supply when no complete
    set is resolved.
    """
    try:
        credentials = session.get_credentials()
    except PartialCredentialsError as error:
        raise ConfigurationError(
            f"the resolved credentials are incomplete: {_reason(error)}; set "
            f"{' and '.join(CREDENTIAL_VARIABLES)} together"
        ) from error
    except NoCredentialsError as error:
        raise ConfigurationError(_missing_credentials_message()) from error
    except BotoCoreError as error:
        raise ConfigurationError(
            f"credentials cannot be resolved: {_reason(error)}"
        ) from error
    if credentials is None or not credentials.access_key:
        raise ConfigurationError(_missing_credentials_message())


def build_s3_client(
    session: boto3.session.Session, endpoint_url: str | None = None
) -> Any:
    """Return an S3 client for ``session``, addressing ``endpoint_url`` when supplied.

    ``endpoint_url`` is passed to the client only when it is not None, so the
    same call shape serves a local endpoint and AWS S3.

    Raises ``ConfigurationError`` when the client cannot be constructed, which
    includes an endpoint the client library refuses.
    """
    arguments: dict[str, Any] = {"config": _client_config()}
    if endpoint_url is not None:
        arguments["endpoint_url"] = endpoint_url
    try:
        return session.client(SERVICE_NAME, **arguments)
    except NoRegionError as error:
        raise ConfigurationError(_missing_region_message()) from error
    except (BotoCoreError, ValueError) as error:
        raise ConfigurationError(
            f"the S3 client cannot be created: {_reason(error)}"
        ) from error


def resolve_s3_access(
    bucket: str,
    region: str | None = None,
    endpoint_url: str | None = None,
) -> Any:
    """Return an S3 client able to address ``bucket``, refusing to guess a setting.

    A session is created, its region is confirmed, its credentials are
    confirmed, and a client is built against ``endpoint_url`` when one was
    supplied. Nothing is requested from the service here and nothing is created.
    The resolved region is noted on stderr; neither the endpoint nor any
    credential value is printed.

    Raises ``ConfigurationError`` naming the setting to supply when the region,
    the credentials or the client cannot be resolved.
    """
    session = build_session(region)
    resolved_region = resolve_session_region(session)
    confirm_credentials(session)
    client = build_s3_client(session, endpoint_url)
    target = "a supplied endpoint" if endpoint_url is not None else "AWS S3"
    _note(
        f"reading bucket {_shown(bucket)} in region {_shown(resolved_region)} "
        f"through {target}"
    )
    return client


def fetch_object_bytes(client: Any, bucket: str, key: str) -> bytes:
    """Return the body of the object ``key`` in ``bucket``, as stored.

    One byte past ``MAX_OBJECT_BYTES`` is requested, so an oversized object is
    reported without being held in memory in full. The bytes are returned
    unchanged; nothing re-encodes or reformats them. Nothing is written to the
    bucket and nothing else in it is read.

    Raises ``AccessError`` when the object or the bucket did not answer,
    ``ConfigurationError`` when a credential or region setting is missing, and
    ``ObjectError`` when the object is empty or larger than
    ``MAX_OBJECT_BYTES``.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    try:
        response = client.get_object(Bucket=bucket, Key=key)
    except (ClientError, BotoCoreError) as error:
        raise _failure_for(
            error, bucket, f"read the landed object {shown_key}"
        ) from error
    body = response.get("Body")
    if body is None:
        raise AccessError(
            f"the endpoint returned no body for the landed object {shown_key} in "
            f"bucket {_shown(bucket)}"
        )
    try:
        content = body.read(MAX_OBJECT_BYTES + 1)
    except (ClientError, BotoCoreError, OSError) as error:
        raise _failure_for(
            error, bucket, f"read the body of the landed object {shown_key}"
        ) from error
    finally:
        closer = getattr(body, "close", None)
        if callable(closer):
            try:
                closer()
            except (ClientError, BotoCoreError, OSError) as error:
                _warn(
                    f"the body of the landed object {shown_key} could not be closed: "
                    f"{_reason(error)}"
                )
    if not isinstance(content, bytes):
        raise AccessError(
            f"the endpoint returned {_display(content)} as the body of the landed "
            f"object {shown_key}; bytes are required"
        )
    if not content:
        raise ObjectError(f"the landed object {shown_key} is empty")
    if len(content) > MAX_OBJECT_BYTES:
        raise ObjectError(
            f"the landed object {shown_key} holds more than the accepted "
            f"{MAX_OBJECT_BYTES} bytes"
        )
    return content


# ---------------------------------------------------------------------------
# Landed record
# ---------------------------------------------------------------------------


def parse_record(raw: bytes, key: str) -> Mapping[str, Any]:
    """Return the single JSON object ``raw`` carries, decoded as UTF-8.

    ``raw`` is the body of the landed object, one JSON object on a single line
    terminated by one line feed. ``key`` names the object in any diagnostic.

    Raises ``ObjectError`` when ``raw`` is not valid UTF-8, is not one
    well-formed JSON document, carries a second document, or carries a JSON
    value that is not an object.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ObjectError(
            f"the landed object {shown_key} is not valid UTF-8: {_reason(error)}"
        ) from error
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        if error.msg.startswith("Extra data"):
            raise ObjectError(
                f"the landed object {shown_key} carries more than one JSON document, "
                f"from line {error.lineno} column {error.colno}; one record is loaded "
                "per object"
            ) from error
        raise ObjectError(
            f"the landed object {shown_key} is not well-formed JSON at line "
            f"{error.lineno} column {error.colno}: "
            f"{_escaped(error.msg, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}"
        ) from error
    if not isinstance(document, dict):
        raise ObjectError(
            f"the landed object {shown_key} carries {_display(document)} at its top "
            "level; one JSON object is required"
        )
    return document


def confirm_record_contract(
    record: Mapping[str, Any], columns: Sequence[str], key: str
) -> None:
    """Confirm ``record`` carries exactly ``columns``, each as text or as null.

    The key set must equal ``columns`` exactly: a missing key and an extra key
    are both refused and named. Every value must be a JSON string or JSON null,
    which is what a number, a boolean, an object and an array are refused for.
    Returns None once the record matches.

    Raises ``ObjectError`` when a key is missing, a key is unexpected, or a value
    is neither text nor null.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    expected = set(columns)
    present = set(record)
    missing = [name for name in columns if name not in present]
    if missing:
        raise ObjectError(
            f"the landed object {shown_key} carries {len(present)} keys and omits "
            f"{len(missing)} the landing schema declares: {_listed(missing)}"
        )
    unexpected = sorted(name for name in present if name not in expected)
    if unexpected:
        raise ObjectError(
            f"the landed object {shown_key} carries {len(unexpected)} keys the "
            f"landing schema does not declare: {_listed(unexpected)}"
        )
    for name in columns:
        value = record[name]
        if value is not None and not isinstance(value, str):
            raise ObjectError(
                f"the landed object {shown_key} carries {_display(value)} as "
                f"{_shown(name)}; the landing contract carries every value as a JSON "
                "string or null, and typing is applied by the dbt models"
            )


def record_values(
    record: Mapping[str, Any], columns: Sequence[str]
) -> tuple[str | None, ...]:
    """Return the values of ``record`` in ``columns`` order, as text or None.

    Each value is returned exactly as the landed object carries it. No value is
    computed, scaled, rounded, padded, zero-filled, trimmed, defaulted or
    backfilled, and a JSON null becomes None, which binds as SQL NULL rather
    than as an empty string or a zero.
    """
    return tuple(record[name] for name in columns)


def natural_key_values(
    record: Mapping[str, Any], key: str
) -> tuple[str, ...]:
    """Return the natural-key values of ``record``, in ``NATURAL_KEY_FIELDS`` order.

    Every natural-key value must be present and non-empty, since the row removed
    before the write is selected by them.

    Raises ``ObjectError`` when a natural-key value is null or empty.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    values: list[str] = []
    for field in NATURAL_KEY_FIELDS:
        value = record.get(field)
        if not isinstance(value, str) or not value:
            raise ObjectError(
                f"the landed object {shown_key} carries {_display(value)} as "
                f"{_shown(field)}; it is part of the natural key "
                f"({', '.join(NATURAL_KEY_FIELDS)}) of the loaded row and must carry "
                "a value"
            )
        values.append(value)
    return tuple(values)


def confirm_source_system_key(
    record: Mapping[str, Any], expected: str, key: str
) -> None:
    """Confirm ``record`` carries ``expected`` as its source-system key.

    Returns None when the two agree.

    Raises ``ObjectError`` when the record carries another value, so a row is
    never loaded under a source-system key the run did not resolve.
    """
    field = NATURAL_KEY_FIELDS[0]
    carried = record.get(field)
    if carried != expected:
        raise ObjectError(
            f"the landed object {_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)} carries "
            f"{_display(carried)} as {_shown(field)} while the resolved source-system "
            f"key is {_shown(expected)}; the two must agree"
        )


# ---------------------------------------------------------------------------
# Shared SQL scripts
# ---------------------------------------------------------------------------


def split_sql_statements(text: str, path: Path) -> tuple[str, ...]:
    """Return the statements of one SQL script, in file order and as written.

    Statements are separated by semicolons outside quoted text and outside
    comments. A single-quoted literal, a double-quoted identifier, a
    dollar-quoted literal, a ``--`` line comment and a ``/* */`` block comment,
    including nested block comments, are all carried through without their
    contents being read as a separator. A statement is returned exactly as the
    script writes it, with surrounding whitespace removed, and a run of text
    holding only comments and whitespace is not returned as a statement.

    Raises ``ConfigurationError`` when the script leaves a quoted literal,
    quoted identifier, dollar-quoted literal or block comment unterminated,
    since the statement boundaries after that point cannot be established.
    """
    statements: list[str] = []
    verbatim: list[str] = []
    code: list[str] = []
    index = 0
    length = len(text)
    line = 1

    def _fail(what: str, opened_at: int) -> NoReturn:
        """Raise ``ConfigurationError`` for ``what`` left open from ``opened_at``."""
        raise ConfigurationError(
            f"the SQL script leaves {what} unterminated from line {opened_at}: "
            f"{_path_shown(path)}; its statement boundaries cannot be established"
        )

    while index < length:
        character = text[index]
        pair = text[index : index + 2]
        if character == "\n":
            line += 1
            verbatim.append(character)
            code.append(character)
            index += 1
            continue
        if pair == "--":
            end = text.find("\n", index)
            end = length if end < 0 else end
            verbatim.append(text[index:end])
            code.append(" ")
            index = end
            continue
        if pair == "/*":
            opened_at = line
            depth = 0
            start = index
            while index < length:
                inner = text[index : index + 2]
                if inner == "/*":
                    depth += 1
                    index += 2
                    continue
                if inner == "*/":
                    depth -= 1
                    index += 2
                    if depth == 0:
                        break
                    continue
                if text[index] == "\n":
                    line += 1
                index += 1
            else:
                _fail("a block comment", opened_at)
            if depth != 0:
                _fail("a block comment", opened_at)
            verbatim.append(text[start:index])
            code.append(" ")
            continue
        if character in {"'", '"'}:
            opened_at = line
            start = index
            index += 1
            while index < length:
                if text[index] == "\n":
                    line += 1
                if text[index] == character:
                    if text[index : index + 2] == character * 2:
                        index += 2
                        continue
                    index += 1
                    break
                index += 1
            else:
                _fail(
                    "a quoted literal" if character == "'" else "a quoted identifier",
                    opened_at,
                )
            fragment = text[start:index]
            if not fragment.endswith(character) or len(fragment) < 2:
                _fail(
                    "a quoted literal" if character == "'" else "a quoted identifier",
                    opened_at,
                )
            verbatim.append(fragment)
            code.append(fragment)
            continue
        if character == "$":
            tag = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$", text[index:])
            if tag is not None:
                opened_at = line
                marker = tag.group()
                closing = text.find(marker, index + len(marker))
                if closing < 0:
                    _fail("a dollar-quoted literal", opened_at)
                end = closing + len(marker)
                fragment = text[index:end]
                line += fragment.count("\n")
                verbatim.append(fragment)
                code.append(fragment)
                index = end
                continue
        if character == ";":
            if "".join(code).strip():
                statements.append("".join(verbatim).strip())
            verbatim = []
            code = []
            index += 1
            continue
        verbatim.append(character)
        code.append(character)
        index += 1

    if "".join(code).strip():
        statements.append("".join(verbatim).strip())
    return tuple(statements)


def read_sql_statements(path: Path) -> tuple[str, ...]:
    """Return the statements of the SQL script at ``path``, in file order.

    Raises ``ConfigurationError`` when the script is missing, empty, larger than
    ``MAX_DDL_BYTES``, not valid UTF-8, or leaves a quoted literal or comment
    unterminated.
    """
    raw = _read_bounded_bytes(path, MAX_DDL_BYTES, "SQL script")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ConfigurationError(
            f"the SQL script is not valid UTF-8: {_path_shown(path)}: "
            f"{_reason(error)}"
        ) from error
    statements = split_sql_statements(text, path)
    if not statements:
        raise ConfigurationError(
            f"the SQL script carries no statement: {_path_shown(path)}"
        )
    return statements


def apply_sql_script(
    connection: duckdb.DuckDBPyConnection, path: Path
) -> int:
    """Apply every statement of the script at ``path`` in order, and return the count.

    Each statement is executed exactly as the script writes it; none is
    rewritten, reordered, substituted or skipped. The scripts this tool is given
    are written to be re-runnable, so applying them to a database that already
    holds their objects changes nothing.

    Raises ``ConfigurationError`` when the script cannot be read or split, and
    ``WarehouseError`` naming the script, the statement's position in it and the
    statement as written when the database refuses a statement.
    """
    statements = read_sql_statements(path)
    for ordinal, statement in enumerate(statements, start=1):
        try:
            connection.execute(statement)
        except duckdb.Error as error:
            raise WarehouseError(
                f"the database refused statement {ordinal} of {len(statements)} in "
                f"{_path_shown(path)}: {_reason(error)}. The statement, as written: "
                f"{_shown(statement, MAX_DIAGNOSTIC_STATEMENT_CHARACTERS)}"
            ) from error
    _note(f"applied {len(statements)} statements from {_path_shown(path)}")
    return len(statements)


def apply_sql_scripts(
    connection: duckdb.DuckDBPyConnection, paths: Sequence[Path]
) -> int:
    """Apply every script in ``paths`` in order, and return the statement count.

    Raises ``ConfigurationError`` when a script cannot be read or split, and
    ``WarehouseError`` when the database refuses a statement.
    """
    return sum(apply_sql_script(connection, path) for path in paths)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------


def qualified_relation_name() -> str:
    """Return the schema-qualified name of the relation this tool writes.

    Both parts reach the statement as SQL text rather than as bound values, so
    both are confirmed usable as unquoted SQL identifiers first.

    Raises ``SchemaError`` when either part is not an unquoted SQL identifier.
    """
    schema = _confirmed_identifier(RAW_SCHEMA_NAME, "raw schema name")
    table = _confirmed_identifier(RAW_TABLE_NAME, "raw relation name")
    return f"{schema}.{table}"


def open_database(path: Path) -> duckdb.DuckDBPyConnection:
    """Return a read-write connection to the DuckDB database file at ``path``.

    A missing parent directory is created, so a first run reaches the database
    the bridge keeps at ``DEFAULT_DATABASE`` without a preparatory step. The
    file itself is created by the connection when it is absent.

    Raises ``WarehouseError`` when the parent directory cannot be created or the
    database cannot be opened.
    """
    parent = path.parent
    try:
        if str(parent):
            parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise WarehouseError(
            f"the database directory cannot be created: {_path_shown(parent)}: "
            f"{_reason(error)}"
        ) from error
    try:
        connection = duckdb.connect(str(path))
    except (duckdb.Error, OSError) as error:
        raise WarehouseError(
            f"the database cannot be opened: {_path_shown(path)}: {_reason(error)}"
        ) from error
    _note(f"opened database {_path_shown(path)}")
    return connection


def _affected_rows(result: Any, action: str) -> int:
    """Return the row count a data-changing statement reported.

    Raises ``WarehouseError`` when the database reported no usable count, so a
    silent zero is never reported as a successful write.
    """
    if not result:
        raise WarehouseError(f"the database reported no row count for the {action}")
    first = result[0]
    if not isinstance(first, (tuple, list)) or not first:
        raise WarehouseError(
            f"the database reported {_display(first)} as the row count for the "
            f"{action}"
        )
    count = first[0]
    if isinstance(count, bool) or not isinstance(count, int):
        raise WarehouseError(
            f"the database reported {_display(count)} as the row count for the "
            f"{action}; a whole number is required"
        )
    return count


def build_delete_statement(relation: str) -> str:
    """Return the statement removing the rows carrying one natural key.

    The predicate names every field of ``NATURAL_KEY_FIELDS`` and binds each
    value, so a row carrying any other natural key is out of its reach and no
    whole-relation form is ever issued.
    """
    predicate = " AND ".join(f"{field} = ?" for field in NATURAL_KEY_FIELDS)
    return f"DELETE FROM {relation} WHERE {predicate}"


def build_insert_statement(relation: str, columns: Sequence[str]) -> str:
    """Return the statement writing one row of ``columns`` into ``relation``.

    The column names come from the landing schema and are already confirmed
    usable as unquoted SQL identifiers. Every value is a placeholder, so no
    landed value is ever joined into statement text.
    """
    names = ", ".join(columns)
    placeholders = ", ".join("?" for _ in columns)
    return f"INSERT INTO {relation} ({names}) VALUES ({placeholders})"


def upsert_record(
    connection: duckdb.DuckDBPyConnection,
    columns: Sequence[str],
    values: Sequence[str | None],
    key_values: Sequence[str],
) -> tuple[int, int]:
    """Write one landed record as one row, and return the rows removed and written.

    Within one transaction the rows already carrying ``key_values`` as their
    natural key are removed and ``values`` is written as one row, so a repeated
    run leaves one row rather than two and a row carrying any other natural key
    is untouched. Every value is bound rather than joined into statement text,
    and a None binds as SQL NULL rather than as an empty string or a zero. The
    transaction is committed once both statements have succeeded; a failure in
    either rolls it back and leaves the database as it was found.

    Raises ``WarehouseError`` when either statement or the commit did not
    succeed, or when the write did not report exactly ``EXPECTED_INSERTED_ROWS``
    rows, and ``SchemaError`` when the relation name is not usable. Whatever the
    failure, the transaction is rolled back before the diagnostic leaves this
    function.
    """
    if len(values) != len(columns):
        raise WarehouseError(
            f"the landed record carries {len(values)} values for {len(columns)} "
            "columns; the two must agree"
        )
    relation = qualified_relation_name()
    delete_statement = build_delete_statement(relation)
    insert_statement = build_insert_statement(relation, columns)
    connection.execute("BEGIN TRANSACTION")
    try:
        removed = _affected_rows(
            connection.execute(delete_statement, list(key_values)).fetchall(),
            f"removal of any earlier row of {relation}",
        )
        written = _affected_rows(
            connection.execute(insert_statement, list(values)).fetchall(),
            f"write of one row of {relation}",
        )
        if written != EXPECTED_INSERTED_ROWS:
            raise WarehouseError(
                f"the write of one row of {relation} reported {written} rows; "
                f"{EXPECTED_INSERTED_ROWS} is required"
            )
        connection.execute("COMMIT")
    except BaseException as error:
        try:
            connection.execute("ROLLBACK")
        except duckdb.Error as rollback_error:
            _warn(
                "the transaction could not be rolled back after the load failed: "
                f"{_reason(rollback_error)}"
            )
        if isinstance(error, (LoadError, KeyboardInterrupt, SystemExit)):
            raise
        raise WarehouseError(
            f"the database refused the load of one row of {relation}: "
            f"{_reason(error)}"
        ) from error
    return removed, written


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


class LoadOutcome(NamedTuple):
    """What one load did: the object read, its natural key and the row counts.

    ``uri`` is the object downloaded, ``key_values`` are the values of
    ``NATURAL_KEY_FIELDS`` the object carried, in that order, ``removed`` is the
    rows carrying that natural key that the load removed, and ``written`` is the
    rows it wrote.
    """

    uri: str
    key_values: tuple[str, ...]
    removed: int
    written: int


def load_record(
    bucket: str,
    key: str,
    source_system_key: str,
    database_path: Path,
    ddl_paths: Sequence[Path],
    *,
    region: str | None = None,
    endpoint_url: str | None = None,
    schema_path: Path = DEFAULT_SCHEMA,
) -> LoadOutcome:
    """Load one landed object as one row, and return what the load did.

    The landed column names and their order are read from the landing schema at
    ``schema_path``, the object is downloaded and confirmed to carry exactly
    those keys as text or null, and the scripts in ``ddl_paths`` are applied
    before the row is written.

    Raises ``ObjectError`` when the landed object breaches the landing contract,
    ``SchemaError`` when the landing schema cannot be used,
    ``ConfigurationError`` when a setting or a script cannot be resolved,
    ``AccessError`` when the bucket or the object did not answer, and
    ``WarehouseError`` when the database or a statement did not succeed.
    """
    columns = landed_column_names(schema_path)
    uri = build_object_uri(bucket, key)
    client = resolve_s3_access(bucket, region, endpoint_url)
    body = fetch_object_bytes(client, bucket, key)
    record = parse_record(body, key)
    confirm_record_contract(record, columns, key)
    confirm_source_system_key(record, source_system_key, key)
    key_values = natural_key_values(record, key)
    values = record_values(record, columns)
    _note(
        f"read {len(body)} bytes carrying {len(columns)} landed columns from {uri}"
    )
    connection = open_database(database_path)
    try:
        apply_sql_scripts(connection, ddl_paths)
        removed, written = upsert_record(connection, columns, values, key_values)
    finally:
        try:
            connection.close()
        except duckdb.Error as error:
            _warn(f"the database connection could not be closed: {_reason(error)}")
    return LoadOutcome(uri, key_values, removed, written)


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


class _CommandLineParser(argparse.ArgumentParser):
    """Command line parser that raises ``UsageError`` for every failure but ``--help``.

    ``-h`` and ``--help`` keep printing the full help and exiting with status 0.
    Every other command line failure becomes one bounded, control-free
    diagnostic carried by ``UsageError``, which reaches stderr as one line.
    """

    def error(self, message: str) -> NoReturn:
        """Raise ``UsageError`` carrying ``message``, bounded and control-free."""
        raise UsageError(
            "command line rejected: "
            f"{_escaped(message, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}; run "
            f"'{_PROGRAM} --help' for the accepted arguments"
        )


def build_arg_parser() -> argparse.ArgumentParser:
    """Return the command line parser for this tool.

    Every option may also be supplied through the environment variable its help
    names, and the option wins whenever both carry a value. Abbreviated option
    names are not accepted.
    """
    key_template = KEY_SEPARATOR.join(
        (
            LANDING_KEY_ROOT,
            f"source_system_key=<{SOURCE_SYSTEM_KEY_VARIABLE}>",
            "entity=<ENTITY>",
            f"extract_date=<{EXTRACT_DATE_FORM}>",
            OBJECT_NAME,
        )
    )
    parser = _CommandLineParser(
        prog=_PROGRAM,
        allow_abbrev=False,
        description=(
            "Download one landed GenApp Policy-Issue object and write it as one "
            f"row of {RAW_SCHEMA_NAME}.{RAW_TABLE_NAME} in a DuckDB database.\n"
            "The values written are the values the object carries: each is bound "
            "as text or as SQL NULL exactly as landed, no amount is derived, and "
            "typing is applied by the dbt models downstream.\n"
            "Exit status: 0 success, 2 landed object rejected, 3 command line or "
            "setting rejected, 4 S3 endpoint, bucket or object operation "
            "unsuccessful, 5 database or SQL operation unsuccessful."
        ),
        epilog=(
            f"Object key: {key_template}\n"
            f"The landed column names and their order are read from "
            f"{DEFAULT_SCHEMA.name}, and the relation is defined by the scripts "
            "--ddl names; this tool defines none of its own.\n"
            f"Within one transaction the rows carrying the natural key "
            f"({', '.join(NATURAL_KEY_FIELDS)}) of the downloaded object are "
            "removed and that object is written as one row, so a repeated run "
            "leaves one row and a row loaded from an earlier object survives.\n"
            "stdout carries exactly one line, naming the relation written, the "
            "natural key and the rows removed and written. Every other message "
            "reaches stderr, and no credential, token or endpoint value is ever "
            "printed.\n"
            f"{ENDPOINT_URL_VARIABLE} or --endpoint-url directs the download at a "
            "local S3-compatible endpoint; with neither present it addresses AWS "
            "S3. An environment variable whose name merely begins with AWS is "
            "never read as a credential.\n"
            "This tool creates no bucket and provisions nothing. Results it "
            "produces are local-substitute results and establish nothing about a "
            "real-target run.\n"
            "Decision rationale: modernization/docs/decision-log.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--bucket",
        default=None,
        metavar="NAME",
        help=(
            "bucket holding the landed object, which must already exist; defaults "
            f"to the {BUCKET_VARIABLE} environment variable. There is no built-in "
            "bucket name"
        ),
    )
    parser.add_argument(
        "--key",
        default=None,
        metavar="KEY",
        help=(
            "object to download, given as a bare key or as the "
            f"{SERVICE_NAME}{URI_SCHEME_SEPARATOR} URI land_to_s3.py printed, whose "
            "bucket must match --bucket; omitted, the key is rebuilt from "
            "--source-system-key, --entity and --extract-date"
        ),
    )
    parser.add_argument(
        "--source-system-key",
        default=None,
        metavar="VALUE",
        help=(
            "source-system element of the landing prefix, which must equal the "
            f"object's own {NATURAL_KEY_FIELDS[0]} value; defaults to the "
            f"{SOURCE_SYSTEM_KEY_VARIABLE} environment variable, then to "
            f"{DEFAULT_SOURCE_SYSTEM_KEY}. At most {MAX_SEGMENT_CHARACTERS} "
            "characters drawn from ASCII letters, digits, underscore, dot and "
            "hyphen"
        ),
    )
    parser.add_argument(
        "--entity",
        default=None,
        metavar="VALUE",
        help=(
            f"entity element of the landing prefix (default: {DEFAULT_ENTITY}), "
            "under the same accepted characters as --source-system-key"
        ),
    )
    parser.add_argument(
        "--extract-date",
        default=None,
        metavar=EXTRACT_DATE_FORM,
        help=(
            "extract-date element of the landing prefix, written exactly "
            f"{EXTRACT_DATE_FORM}; defaults to the current UTC date"
        ),
    )
    parser.add_argument(
        "--endpoint-url",
        default=None,
        metavar="URL",
        help=(
            "S3 endpoint to address, selecting a local S3-compatible endpoint; "
            f"defaults to the {ENDPOINT_URL_VARIABLE} environment variable. With "
            "neither present the download addresses AWS S3"
        ),
    )
    parser.add_argument(
        "--region",
        default=None,
        metavar="NAME",
        help=(
            "region to address; defaults to the "
            f"{' environment variable, then the '.join(REGION_VARIABLES)} "
            "environment variable, and then to the region the session resolves for "
            "itself"
        ),
    )
    parser.add_argument(
        "--database",
        default=None,
        metavar="PATH",
        help=(
            "DuckDB database file to write; defaults to the "
            f"{' environment variable, then the '.join(DATABASE_VARIABLES)} "
            f"environment variable, and then to {DEFAULT_DATABASE}. A path inside "
            "this tool's own directory is refused"
        ),
    )
    parser.add_argument(
        "--ddl",
        action="append",
        default=None,
        metavar="PATH",
        help=(
            "SQL script applied before the row is written, repeatable and applied "
            f"in the order given; defaults to every {DDL_GLOB} file in "
            f"{DEFAULT_DDL_DIRECTORY} sorted by name. The scripts are applied "
            "exactly as written"
        ),
    )
    parser.add_argument(
        "--no-ddl",
        dest="apply_ddl",
        action="store_false",
        help=(
            "apply no SQL script before writing the row, for a database whose "
            "relation is already present"
        ),
    )
    parser.set_defaults(apply_ddl=True)
    return parser


def _report(
    relation: str, key_values: Sequence[str], removed: int, written: int
) -> str:
    """Return the single stdout line naming what one load wrote.

    The line names the relation, every natural-key field with the value it
    carried, and the rows removed and written, so a run can be audited from its
    own output.
    """
    identity = " ".join(
        f"{field}={value}" for field, value in zip(NATURAL_KEY_FIELDS, key_values)
    )
    return (
        f"loaded {relation} {identity} removed={removed} written={written}"
    )


def _run(args: argparse.Namespace) -> str:
    """Run one load and return the single line to write to stdout.

    Settings are resolved first, so a missing bucket, region, credential or
    script is reported before any object is downloaded and before the database
    is opened.
    """
    bucket = resolve_bucket(args.bucket)
    region = resolve_region(args.region)
    endpoint_url = resolve_endpoint_url(args.endpoint_url)
    source_system_key = resolve_source_system_key(args.source_system_key)
    entity = resolve_entity(args.entity)
    extract_date = resolve_extract_date(args.extract_date)
    database_path = resolve_database_path(args.database)
    ddl_paths = resolve_ddl_paths(args.ddl, args.apply_ddl)
    key = resolve_object_key(args.key, bucket, source_system_key, entity, extract_date)
    relation = qualified_relation_name()
    outcome = load_record(
        bucket,
        key,
        source_system_key,
        database_path,
        ddl_paths,
        region=region,
        endpoint_url=endpoint_url,
    )
    return _report(relation, outcome.key_values, outcome.removed, outcome.written)


def main(argv: list[str] | None = None) -> int:
    """Load one landed object into the local raw relation, returning the exit status.

    ``argv`` defaults to the process arguments. Exactly one line reaches stdout
    on success, naming the relation written, the natural key and the rows
    removed and written. Every diagnostic reaches stderr as one control-free
    line, names the setting to supply when one is missing, and carries no
    credential, token or endpoint value. A rejected command line is reported
    through that same single line, without a usage block, while ``--help``
    prints the full help and exits with status 0.
    """
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        result = _run(args)
    except LoadError as error:
        print(f"{_PROGRAM}: {_one_line(str(error))}", file=sys.stderr)
        return error.exit_status
    except KeyboardInterrupt:
        print(f"{_PROGRAM}: interrupted before completion", file=sys.stderr)
        return EXIT_INTERRUPTED

    print(result)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
