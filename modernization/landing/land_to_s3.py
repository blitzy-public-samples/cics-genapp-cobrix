#!/usr/bin/env python3
"""Land one GenApp Policy-Issue record as a single S3 object.

WHAT THIS TOOL DOES
    Reads the landing JSON record written by
    modernization/extraction/extract_commarea.py, validates it against
    modernization/landing/landing-schema.json, and writes it to exactly one S3 object
    under the landing prefix this module builds. The bytes read from the record file
    are the bytes uploaded: no value is computed, scaled, rounded, padded, zero-filled
    or defaulted, no key is added, removed, renamed or reordered, and the parsed
    document is never re-serialised, so the object a loader reads is byte-identical to
    the record the harness produced. The six amount values pass through untouched.
    Each of them reaches the record through one MOVE, at base/src/lgapdb01.cbl:265,
    445, 489, 491, 493 and 495, and the three named programs carry no COMPUTE,
    MULTIPLY or DIVIDE statement and no COMP-3 item, so a landed amount is the digit
    string the chain moved and nothing else.

WHICH TARGET IT ADDRESSES
    One code path serves both targets. --endpoint-url, or the S3_ENDPOINT_URL
    environment variable, directs the client at a local S3-compatible endpoint; with
    neither present the client addresses AWS S3. Nothing else in this tool varies with
    the target. Access is established from resolved credentials, a resolved region and
    a bucket that answers a head request; the presence of an environment variable
    whose name begins with AWS is never read as evidence of access, and no variable is
    matched on that prefix.

WHICH INPUTS IT ACCEPTS
    --record        path to the landing JSON record, read as bytes and uploaded
                    unchanged, in a file of at most MAX_RECORD_BYTES bytes. Required
                    unless --probe is given, which reads no record.
    --bucket        destination bucket, defaulting to the S3_BUCKET environment
                    variable. There is no built-in bucket name.
    --source-system-key
                    source-system element of the landing prefix, defaulting to the
                    SOURCE_SYSTEM_KEY environment variable and then to
                    DEFAULT_SOURCE_SYSTEM_KEY. It must equal the record's own
                    source_system_key value.
    --extract-date  extract-date element of the landing prefix as YYYY-MM-DD,
                    defaulting to the current UTC date.
    --entity        entity element of the landing prefix, defaulting to
                    DEFAULT_ENTITY.
    --endpoint-url  S3 endpoint to address, defaulting to the S3_ENDPOINT_URL
                    environment variable. Absent on both, the client addresses AWS S3.
    --region        region to address, defaulting to the AWS_REGION and then the
                    AWS_DEFAULT_REGION environment variable, and then to whatever the
                    boto3 session resolves for itself.
    --probe         confirm access and exit, writing no landing object.

WHERE IT WRITES
    One object, under the key

        landing/source_system_key=<KEY>/entity=<ENTITY>/extract_date=<YYYY-MM-DD>/part-0000.json

    giving the URI s3://<bucket>/<key>. The segments are Hive-style key=value pairs in
    that order, the object name is literal, the key carries no leading slash, no empty
    segment and no percent-encoding, and the object is written with content type
    application/json. Partitioning applies to this key prefix alone: this tool states
    no distribution, sort or partition property for any warehouse relation.

    In landing mode stdout carries exactly one line, the s3:// URI of the object
    written. In probe mode stdout carries exactly one line, the probe verdict. Every
    other message reaches stderr. No credential, token, session value or environment
    listing is ever printed, on any path.

HOW IT FAILS
    Every failure writes one control-free line to stderr and returns a non-zero
    status: 2 for a record that breaches the landing contract, 3 for a rejected
    command line or an unresolved setting, 4 for an S3 endpoint, bucket or object
    operation that did not succeed. A missing setting is named in the diagnostic. The
    tool never prompts and requires no TTY.

WHAT IT NEVER DOES
    It creates no bucket, cluster, workgroup, role, policy, network or key, and sets
    no versioning, encryption, lifecycle or bucket policy; a bucket that does not
    answer a head request is reported, never created. It writes no canonical relation,
    no second object and no provenance object. It writes nothing to the local
    filesystem and reads nothing under base/. The probe object it writes in --probe
    mode is deleted before the tool returns.

WHERE THIS STEP SITS
    Figure 2 - AFTER (BUILT): Canonical Warehouse Bridge, and Figure 5 - Validation
    Harness Control Flow, both in modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import uuid
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, NoReturn

import boto3.session
import jsonschema.exceptions
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    NoRegionError,
    PartialCredentialsError,
)
from jsonschema.validators import Draft202012Validator

_PROGRAM = "land_to_s3"

# Landing schema used for validation, resolved from this script's own directory rather
# than from the working directory, so every working directory validates the same
# contract.
_THIS_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA = _THIS_DIR / "landing-schema.json"

# Environment variables consulted when the matching option is omitted. No value read
# from any of them is ever printed.
BUCKET_VARIABLE = "S3_BUCKET"
ENDPOINT_URL_VARIABLE = "S3_ENDPOINT_URL"
SOURCE_SYSTEM_KEY_VARIABLE = "SOURCE_SYSTEM_KEY"
REGION_VARIABLES = ("AWS_REGION", "AWS_DEFAULT_REGION")

# Environment variables naming the credentials a boto3 session resolves for itself.
# They are named in diagnostics and are never read by this module.
CREDENTIAL_VARIABLES = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")

# Landing prefix parts. The key is LANDING_KEY_ROOT, then one Hive-style segment per
# entry of PARTITION_FIELDS in this order, then OBJECT_NAME.
LANDING_KEY_ROOT = "landing"
PARTITION_FIELDS = ("source_system_key", "entity", "extract_date")
OBJECT_NAME = "part-0000.json"
KEY_SEPARATOR = "/"

# Values used when the matching option and environment variable are both absent.
DEFAULT_SOURCE_SYSTEM_KEY = "GENAPP_CLASS_EXEMPLAR"
DEFAULT_ENTITY = "policy_issue"

# Record key whose value must equal the resolved source-system key.
SOURCE_SYSTEM_KEY_FIELD = "source_system_key"

# Service addressed, and the content type the landed object carries.
SERVICE_NAME = "s3"
OBJECT_CONTENT_TYPE = "application/json"

# Accepted shapes. A partition segment value becomes one path segment, so it carries
# no separator, no whitespace and no equals sign. A bucket name becomes the authority
# of the reported URI under the same restriction.
_SEGMENT_SHAPE = re.compile(r"\A[A-Za-z0-9_.\-]+\Z")
_BUCKET_SHAPE = re.compile(r"\A[A-Za-z0-9_.\-]+\Z")
MAX_SEGMENT_CHARACTERS = 64
MIN_BUCKET_CHARACTERS = 3
MAX_BUCKET_CHARACTERS = 63

# Extract date form accepted on the command line and emitted into the key.
EXTRACT_DATE_FORM = "YYYY-MM-DD"

# Bytes one read takes from the record and from the schema before anything parses
# them, and the bytes one read asks for at a time.
MAX_RECORD_BYTES = 1024 * 1024
MAX_SCHEMA_BYTES = 4 * 1024 * 1024
READ_CHUNK_BYTES = 65536

# Prefix, object name shape and payload of the object written by --probe. The prefix
# is outside LANDING_KEY_ROOT, so a probe object can never be read as landed data.
PROBE_KEY_ROOT = "_genapp_rqi_access_probe"
PROBE_NAME_TEMPLATE = "probe-{token}.tmp"
PROBE_BODY = b"genapp-rqi-access-probe\n"
PROBE_CONTENT_TYPE = "text/plain"

# Leading text of the single stdout line --probe writes when every step succeeded.
PROBE_VERDICT = "s3-access-probe ok"

# Connection behaviour applied to every request, bounding the time a failing endpoint
# can hold up the caller.
CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 3
RETRY_MODE = "standard"

EXIT_OK = 0
EXIT_RECORD_REJECTED = 2
EXIT_CONFIGURATION_REJECTED = 3
EXIT_S3_UNAVAILABLE = 4
EXIT_INTERRUPTED = 130

# Characters of untrusted text one diagnostic fragment carries before truncation, and
# the number of schema violations one diagnostic reports.
MAX_DIAGNOSTIC_CHARACTERS = 64
MAX_DIAGNOSTIC_PATH_CHARACTERS = 160
MAX_DIAGNOSTIC_MESSAGE_CHARACTERS = 200
MAX_REPORTED_SCHEMA_ERRORS = 5

# Characters escaped out of a diagnostic.
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f-\x9f]")

# Client error codes reported with a specific diagnostic.
_CODES_BUCKET_ABSENT = frozenset({"404", "NoSuchBucket", "NotFound"})
_CODES_ACCESS_DENIED = frozenset(
    {"403", "AccessDenied", "AllAccessDisabled", "Forbidden"}
)
_CODES_WRONG_REGION = frozenset(
    {"301", "PermanentRedirect", "IllegalLocationConstraint"}
)
_CODES_CREDENTIALS_REJECTED = frozenset(
    {"InvalidAccessKeyId", "SignatureDoesNotMatch", "InvalidClientTokenId"}
)


class LandingError(Exception):
    """Diagnostic raised by this module, carrying the process status to return."""

    exit_status = EXIT_RECORD_REJECTED


class RecordError(LandingError):
    """The record file breaches the landing contract."""

    exit_status = EXIT_RECORD_REJECTED


class ConfigurationError(LandingError):
    """A required setting is absent or carries a rejected value."""

    exit_status = EXIT_CONFIGURATION_REJECTED


class UsageError(ConfigurationError):
    """The command line omits a required argument or carries a rejected value."""

    exit_status = EXIT_CONFIGURATION_REJECTED


class SchemaError(ConfigurationError):
    """The landing schema cannot be read or is not a usable schema document."""

    exit_status = EXIT_CONFIGURATION_REJECTED


class AccessError(LandingError):
    """An S3 endpoint, bucket or object operation did not succeed."""

    exit_status = EXIT_S3_UNAVAILABLE


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


def _warn(message: str) -> None:
    """Write one control-free warning line to stderr."""
    print(f"{_PROGRAM}: warning: {_one_line(message)}", file=sys.stderr)


def _note(message: str) -> None:
    """Write one control-free progress line to stderr."""
    print(f"{_PROGRAM}: {_one_line(message)}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Record and schema
# ---------------------------------------------------------------------------


def _read_bounded_bytes(path: Path, limit: int, what: str) -> bytes:
    """Return the content of ``path``, refusing anything longer than ``limit`` bytes.

    One byte past ``limit`` is requested, so an oversized input is reported without
    being held in memory in full. ``what`` names the input in any diagnostic.

    Raises ``RecordError`` when the file is empty, longer than ``limit``, or cannot be
    opened or read.
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
        raise RecordError(
            f"the {what} cannot be read: {_path_shown(path)}: {_reason(error)}"
        ) from error
    content = b"".join(chunks)
    if not content:
        raise RecordError(f"the {what} is empty: {_path_shown(path)}")
    if len(content) > limit:
        raise RecordError(
            f"the {what} holds more than the accepted {limit} bytes: "
            f"{_path_shown(path)}"
        )
    return content


def read_record_bytes(path: Path) -> bytes:
    """Return the exact bytes of the landing record at ``path``.

    These bytes are the object body: nothing downstream re-encodes, reformats or
    re-serialises them, so the landed object is byte-identical to this file.

    Raises ``RecordError`` when the file is empty, larger than ``MAX_RECORD_BYTES`` or
    unreadable.
    """
    return _read_bounded_bytes(path, MAX_RECORD_BYTES, "landing record")


def parse_record(raw: bytes, path: Path) -> Mapping[str, Any]:
    """Return the single JSON object ``raw`` carries, decoded as UTF-8.

    ``raw`` is inspected only; the caller keeps it for upload unchanged. ``path`` names
    the input in any diagnostic.

    Raises ``RecordError`` when ``raw`` is not valid UTF-8, is not one well-formed JSON
    document, carries a second document, or carries a JSON value that is not an object.
    """
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RecordError(
            f"the landing record is not valid UTF-8: {_path_shown(path)}: "
            f"{_reason(error)}"
        ) from error
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        if error.msg.startswith("Extra data"):
            raise RecordError(
                "the landing record carries more than one JSON document, from line "
                f"{error.lineno} column {error.colno}: {_path_shown(path)}; one record "
                "is landed per run"
            ) from error
        raise RecordError(
            f"the landing record is not well-formed JSON at line {error.lineno} "
            f"column {error.colno}: {_path_shown(path)}: "
            f"{_escaped(error.msg, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}"
        ) from error
    if not isinstance(document, dict):
        raise RecordError(
            f"the landing record carries {_display(document)} at its top level: "
            f"{_path_shown(path)}; one JSON object is required"
        )
    return document


def load_schema(path: Path = DEFAULT_SCHEMA) -> Mapping[str, Any]:
    """Return the landing schema document read from ``path``.

    The document is returned as parsed; no constraint of it is restated in this module.

    Raises ``SchemaError`` when the file is missing, empty, larger than
    ``MAX_SCHEMA_BYTES``, not valid UTF-8, not well-formed JSON, or not a JSON object.
    """
    try:
        raw = _read_bounded_bytes(path, MAX_SCHEMA_BYTES, "landing schema")
    except RecordError as error:
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


def build_validator(
    schema: Mapping[str, Any], path: Path = DEFAULT_SCHEMA
) -> Draft202012Validator:
    """Return a validator for ``schema``, confirming its declared dialect first.

    ``schema`` must declare the 2020-12 dialect in ``$schema``, which is the dialect
    the returned validator applies, and must itself satisfy that dialect's
    meta-schema. ``path`` names the schema in any diagnostic.

    Raises ``SchemaError`` when the declared dialect is absent or differs from the one
    applied, or when the document is not a valid schema.
    """
    applied = Draft202012Validator.META_SCHEMA["$id"]
    declared = schema.get("$schema")
    if declared is None:
        raise SchemaError(
            f"the landing schema declares no '$schema' dialect: {_path_shown(path)}; "
            f"{_shown(applied)} is required"
        )
    if declared != applied:
        raise SchemaError(
            f"the landing schema declares dialect {_display(declared)}: "
            f"{_path_shown(path)}; this tool applies {_shown(applied)}"
        )
    try:
        Draft202012Validator.check_schema(schema)
    except jsonschema.exceptions.SchemaError as error:
        raise SchemaError(
            f"the landing schema is not a valid 2020-12 schema: {_path_shown(path)}: "
            f"at {_json_pointer(error.absolute_schema_path)}: "
            f"{_escaped(error.message, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}"
        ) from error
    return Draft202012Validator(schema)


def _json_pointer(path: Iterable[Any]) -> str:
    """Return the RFC 6901 JSON Pointer for ``path``, rendering the root as ``/``.

    Each element is escaped as RFC 6901 requires, with ``~`` written ``~0`` and ``/``
    written ``~1``.
    """
    parts = [
        str(element).replace("~", "~0").replace(KEY_SEPARATOR, "~1")
        for element in path
    ]
    if not parts:
        return KEY_SEPARATOR
    return KEY_SEPARATOR + KEY_SEPARATOR.join(parts)


def _violation(error: jsonschema.exceptions.ValidationError) -> str:
    """Return one schema violation as a pointer and a bounded message."""
    return (
        f"at {_json_pointer(error.absolute_path)}: "
        f"{_escaped(error.message, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}"
    )


def validate_record(
    record: Mapping[str, Any],
    validator: Draft202012Validator,
    path: Path,
    limit: int = MAX_REPORTED_SCHEMA_ERRORS,
) -> None:
    """Confirm ``record`` satisfies the landing schema, reporting every violation.

    Violations are reported in JSON Pointer order, at most ``limit`` of them, with the
    number withheld recorded when there are more. ``path`` names the record in the
    diagnostic. Returns None when the record satisfies the schema.

    Raises ``RecordError`` carrying the violations when it does not.
    """
    errors = sorted(
        validator.iter_errors(record),
        key=lambda error: (_json_pointer(error.absolute_path), error.message),
    )
    if not errors:
        return
    reported = "; ".join(_violation(error) for error in errors[:limit])
    withheld = len(errors) - min(len(errors), limit)
    if withheld:
        reported = f"{reported}; (+{withheld} further violations)"
    raise RecordError(
        f"the landing record does not satisfy the landing schema: "
        f"{_path_shown(path)}: {reported}"
    )


def confirm_source_system_key(
    record: Mapping[str, Any], resolved: str, path: Path
) -> None:
    """Confirm the record's own source-system key equals the one forming the prefix.

    ``resolved`` is the value the landing key is built from. Returns None when the two
    agree, so the object cannot land under a prefix its payload contradicts.

    Raises ``RecordError`` when the record omits the field, carries a value that is not
    a string, or carries a value that differs from ``resolved``.
    """
    if SOURCE_SYSTEM_KEY_FIELD not in record:
        raise RecordError(
            f"the landing record omits {_shown(SOURCE_SYSTEM_KEY_FIELD)}: "
            f"{_path_shown(path)}"
        )
    carried = record[SOURCE_SYSTEM_KEY_FIELD]
    if not isinstance(carried, str):
        raise RecordError(
            f"the landing record carries {_display(carried)} for "
            f"{_shown(SOURCE_SYSTEM_KEY_FIELD)}: {_path_shown(path)}; a string is "
            "required"
        )
    if carried != resolved:
        raise RecordError(
            f"the landing record carries {_shown(carried)} for "
            f"{_shown(SOURCE_SYSTEM_KEY_FIELD)} while the landing prefix would carry "
            f"{_shown(resolved)}: {_path_shown(path)}; the two must agree"
        )



# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


def _from_environment(names: Sequence[str]) -> tuple[str | None, str | None]:
    """Return the first non-empty value among ``names`` and the name that carried it.

    A variable that is set to the empty string is passed over. Returns ``(None, None)``
    when no name carries a value. Only the name is ever quoted in a diagnostic.
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

    ``supplied`` is the command-line value, which wins whenever it is present, and
    ``variables`` are consulted in order after it. The origin is the option name, the
    variable name, or ``'no setting'`` when neither carried a value.
    """
    if supplied is not None:
        return supplied, option
    value, name = _from_environment(variables)
    if value is not None and name is not None:
        return value, f"the {name} environment variable"
    return None, "no setting"


def _require_segment(value: str, what: str, origin: str) -> str:
    """Return ``value`` confirmed usable as one path segment of the landing key.

    A segment carries 1 to ``MAX_SEGMENT_CHARACTERS`` characters drawn from ASCII
    letters, digits, underscore, dot and hyphen, which admits no separator, no
    whitespace and no equals sign.

    Raises ``ConfigurationError`` when ``value`` is empty, too long, or carries any
    other character.
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


def resolve_bucket(supplied: str | None) -> str:
    """Return the destination bucket name, taking the first setting that is present.

    ``supplied`` is the ``--bucket`` value, and the ``S3_BUCKET`` environment variable
    is consulted when it is absent. There is no built-in bucket name.

    Raises ``ConfigurationError`` when neither carries a value, or when the value is
    shorter than ``MIN_BUCKET_CHARACTERS``, longer than ``MAX_BUCKET_CHARACTERS`` or
    carries a character that could not appear in the reported URI.
    """
    value, origin = _resolved(supplied, "--bucket", (BUCKET_VARIABLE,))
    if value is None:
        raise ConfigurationError(
            "no destination bucket is set: supply --bucket or set the "
            f"{BUCKET_VARIABLE} environment variable to an existing bucket; this tool "
            "creates none"
        )
    if not (MIN_BUCKET_CHARACTERS <= len(value) <= MAX_BUCKET_CHARACTERS):
        raise ConfigurationError(
            f"the bucket name from {origin} holds {len(value)} characters: "
            f"{_shown(value)}; between {MIN_BUCKET_CHARACTERS} and "
            f"{MAX_BUCKET_CHARACTERS} are accepted"
        )
    if not _BUCKET_SHAPE.fullmatch(value):
        raise ConfigurationError(
            f"the bucket name from {origin} carries a character outside ASCII letters, "
            f"digits, underscore, dot and hyphen: {_shown(value)}"
        )
    return value


def resolve_source_system_key(supplied: str | None) -> str:
    """Return the source-system key forming the prefix, and the record's own value.

    ``supplied`` is the ``--source-system-key`` value; the ``SOURCE_SYSTEM_KEY``
    environment variable is consulted when it is absent, and
    ``DEFAULT_SOURCE_SYSTEM_KEY`` when neither carries a value.

    Raises ``ConfigurationError`` when the resolved value cannot form one path segment.
    """
    value, origin = _resolved(
        supplied, "--source-system-key", (SOURCE_SYSTEM_KEY_VARIABLE,)
    )
    if value is None:
        value, origin = DEFAULT_SOURCE_SYSTEM_KEY, "the built-in default"
    return _require_segment(value, "source-system key", origin)


def resolve_entity(supplied: str | None) -> str:
    """Return the entity element of the landing prefix.

    ``supplied`` is the ``--entity`` value and ``DEFAULT_ENTITY`` applies when it is
    absent.

    Raises ``ConfigurationError`` when the resolved value cannot form one path segment.
    """
    if supplied is None:
        return _require_segment(DEFAULT_ENTITY, "entity", "the built-in default")
    return _require_segment(supplied, "entity", "--entity")


def resolve_extract_date(supplied: str | None) -> datetime.date:
    """Return the extract date forming the prefix, as a date.

    ``supplied`` is the ``--extract-date`` value, which must be written exactly
    ``EXTRACT_DATE_FORM``; the current UTC date applies when it is absent. A value that
    parses as some other ISO 8601 form is refused, so the key segment and the date the
    caller wrote always agree character for character.

    Raises ``ConfigurationError`` when ``supplied`` is not a calendar date written in
    that form.
    """
    if supplied is None:
        return datetime.datetime.now(datetime.timezone.utc).date()
    try:
        parsed = datetime.date.fromisoformat(supplied)
    except ValueError as error:
        raise ConfigurationError(
            f"the extract date from --extract-date is not a calendar date written "
            f"{EXTRACT_DATE_FORM}: {_shown(supplied)}: {_reason(error)}"
        ) from error
    if parsed.isoformat() != supplied:
        raise ConfigurationError(
            f"the extract date from --extract-date is not written "
            f"{EXTRACT_DATE_FORM}: {_shown(supplied)}; "
            f"{_shown(parsed.isoformat())} is the accepted form of that date"
        )
    return parsed


def resolve_endpoint_url(supplied: str | None) -> str | None:
    """Return the S3 endpoint to address, or None to address AWS S3.

    ``supplied`` is the ``--endpoint-url`` value and the ``S3_ENDPOINT_URL``
    environment variable is consulted when it is absent. A returned value directs the
    client at that endpoint; None leaves the client addressing AWS S3.

    Raises ``ConfigurationError`` when the resolved value carries no scheme separator
    or carries whitespace.
    """
    value, origin = _resolved(supplied, "--endpoint-url", (ENDPOINT_URL_VARIABLE,))
    if value is None:
        return None
    if "://" not in value or value.split("://", 1)[0] == "":
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
    ``AWS_DEFAULT_REGION`` are consulted when it is absent. Returning None hands the
    resolution to the boto3 session, whose own answer is confirmed later.

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


# ---------------------------------------------------------------------------
# Key construction
# ---------------------------------------------------------------------------


def build_landing_key(
    source_system_key: str, entity: str, extract_date: datetime.date
) -> str:
    """Return the landing object key for one extract.

    The key is

        landing/source_system_key=<KEY>/entity=<ENTITY>/extract_date=<YYYY-MM-DD>/part-0000.json

    with the Hive-style segments in the order ``PARTITION_FIELDS`` records, the literal
    object name ``OBJECT_NAME``, no leading separator, no empty segment and no
    percent-encoding of the equals sign. The date is written as
    ``EXTRACT_DATE_FORM``.

    Raises ``ConfigurationError`` when a supplied value cannot form one path segment.
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
    return f"{SERVICE_NAME}://{bucket}{KEY_SEPARATOR}{key}"


def build_probe_key() -> str:
    """Return a fresh key for one access-probe object.

    The key sits under ``PROBE_KEY_ROOT``, outside the landing prefix, and carries a
    random token, so concurrent probes never address the same object and no probe
    object can be read as landed data.
    """
    name = PROBE_NAME_TEMPLATE.format(token=uuid.uuid4().hex)
    return KEY_SEPARATOR.join((PROBE_KEY_ROOT, name))



# ---------------------------------------------------------------------------
# Client, credentials and access
# ---------------------------------------------------------------------------


def _client_config() -> Config:
    """Return the connection behaviour applied to every request.

    A failing endpoint is abandoned after ``CONNECT_TIMEOUT_SECONDS`` and a stalled
    response after ``READ_TIMEOUT_SECONDS``, with at most ``MAX_ATTEMPTS`` attempts, so
    an unreachable target cannot hold the caller open indefinitely.
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


def _failure_for(error: BaseException, bucket: str, action: str) -> LandingError:
    """Return the diagnostic for an S3 ``action`` on ``bucket`` that did not succeed.

    A credential problem becomes a ``ConfigurationError`` naming the settings to
    supply; every other failure becomes an ``AccessError``. The returned diagnostic
    carries no credential, token or endpoint value.
    """
    if isinstance(error, NoCredentialsError):
        return ConfigurationError(
            f"cannot {action}: {_missing_credentials_message()}"
        )
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
        if code in _CODES_BUCKET_ABSENT:
            return AccessError(
                f"cannot {action}: bucket {_shown(bucket)} does not exist or is not "
                "visible to the resolved credentials; supply an existing bucket, which "
                "this tool never creates"
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
    return AccessError(
        f"cannot {action} on bucket {_shown(bucket)}: {_reason(error)}"
    )


def build_session(region: str | None = None) -> boto3.session.Session:
    """Return a boto3 session, pinned to ``region`` when one was resolved.

    Passing None leaves the session to resolve a region for itself, which
    ``resolve_session_region`` then confirms. No credential value is passed in: the
    session resolves credentials through its own providers.

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

    The session's own providers do the resolving, so a variable whose name merely
    begins with AWS is never taken for a credential. An incomplete set surfaces as
    ``PartialCredentialsError`` from that resolution. Returns None once a credential
    set is resolved; no credential value is read beyond confirming one is present, and
    none is ever printed.

    Raises ``ConfigurationError`` naming the settings to supply when no complete set is
    resolved.
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

    ``endpoint_url`` is passed to the client only when it is not None, so the same call
    shape serves a local endpoint and AWS S3.

    Raises ``ConfigurationError`` when the client cannot be constructed, which includes
    an endpoint the client library refuses.
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

    A session is created, its region is confirmed, its credentials are confirmed, and a
    client is built against ``endpoint_url`` when one was supplied. Nothing is
    requested from the service here and nothing is created. The resolved region is
    noted on stderr; neither the endpoint nor any credential value is printed.

    Raises ``ConfigurationError`` naming the setting to supply when the region, the
    credentials or the client cannot be resolved.
    """
    session = build_session(region)
    resolved_region = resolve_session_region(session)
    confirm_credentials(session)
    client = build_s3_client(session, endpoint_url)
    target = "a supplied endpoint" if endpoint_url is not None else "AWS S3"
    _note(
        f"addressing bucket {_shown(bucket)} in region {_shown(resolved_region)} "
        f"through {target}"
    )
    return client


def confirm_bucket_reachable(client: Any, bucket: str) -> None:
    """Confirm ``bucket`` answers a head request, creating nothing.

    Returns None when the bucket answers.

    Raises ``AccessError`` when the bucket is absent, is not permitted to the resolved
    credentials, is in another region or the endpoint did not answer, and
    ``ConfigurationError`` when the endpoint rejected the credentials.
    """
    try:
        client.head_bucket(Bucket=bucket)
    except (ClientError, BotoCoreError) as error:
        raise _failure_for(error, bucket, "reach the destination bucket") from error


def probe_bucket_access(
    client: Any, bucket: str, probe_key: str | None = None
) -> str:
    """Confirm ``bucket`` accepts one write and one delete, and return the key used.

    The bucket is head-requested, one object of ``PROBE_BODY`` is written under a key
    from ``build_probe_key`` unless ``probe_key`` names one, and that object is deleted
    in a finally block, so a failure part-way through leaves nothing behind. The probe
    key sits outside the landing prefix. Nothing is created beyond that one object and
    nothing is configured on the bucket.

    Raises ``AccessError`` when a step did not succeed or when the probe object could
    not be deleted after being written, and ``ConfigurationError`` when a credential or
    region setting is missing.
    """
    key = probe_key if probe_key is not None else build_probe_key()
    confirm_bucket_reachable(client, bucket)
    written_failure: BaseException | None = None
    try:
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=PROBE_BODY,
            ContentType=PROBE_CONTENT_TYPE,
        )
    except (ClientError, BotoCoreError) as error:
        written_failure = error
        raise _failure_for(error, bucket, "write the access probe object") from error
    finally:
        try:
            client.delete_object(Bucket=bucket, Key=key)
        except (ClientError, BotoCoreError) as cleanup_error:
            if written_failure is None:
                raise _failure_for(
                    cleanup_error, bucket, "delete the access probe object"
                ) from cleanup_error
            _warn(
                f"the access probe object {_shown(key)} could not be deleted after the "
                f"write failed: {_reason(cleanup_error)}"
            )
    return key


def put_record(client: Any, bucket: str, key: str, body: bytes) -> None:
    """Write ``body`` to ``key`` in ``bucket`` as one object, and return None.

    ``body`` is written exactly as given, with content type ``OBJECT_CONTENT_TYPE``, so
    the stored object is byte-identical to the record file the caller read. One object
    is written and nothing else on the bucket is read, written or configured.

    Raises ``AccessError`` when the write did not succeed, and ``ConfigurationError``
    when a credential setting is missing.
    """
    try:
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=OBJECT_CONTENT_TYPE,
        )
    except (ClientError, BotoCoreError) as error:
        raise _failure_for(
            error, bucket, f"write the landing object {_shown(key)}"
        ) from error



# ---------------------------------------------------------------------------
# Landing
# ---------------------------------------------------------------------------


def land_record(
    record_path: Path,
    bucket: str,
    source_system_key: str,
    entity: str,
    extract_date: datetime.date,
    *,
    region: str | None = None,
    endpoint_url: str | None = None,
    schema_path: Path = DEFAULT_SCHEMA,
) -> str:
    """Validate one landing record, write it as one object, and return its URI.

    The record is read as bytes, parsed, validated against the schema at
    ``schema_path`` and checked to carry ``source_system_key`` itself, and the landing
    key is built, all before any client exists. The bytes read are the bytes written,
    so the stored object is byte-identical to ``record_path``. Exactly one object is
    written and nothing is created on the bucket.

    Raises ``RecordError`` when the record breaches the landing contract,
    ``SchemaError`` when the schema cannot be used, ``ConfigurationError`` when a
    setting cannot be resolved, and ``AccessError`` when the bucket or the write did not
    answer.
    """
    body = read_record_bytes(record_path)
    record = parse_record(body, record_path)
    validator = build_validator(load_schema(schema_path), schema_path)
    validate_record(record, validator, record_path)
    confirm_source_system_key(record, source_system_key, record_path)
    key = build_landing_key(source_system_key, entity, extract_date)
    _note(
        f"validated {_path_shown(record_path)} carrying {len(body)} bytes for key "
        f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
    )
    client = resolve_s3_access(bucket, region, endpoint_url)
    confirm_bucket_reachable(client, bucket)
    put_record(client, bucket, key, body)
    return build_object_uri(bucket, key)


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


class _CommandLineParser(argparse.ArgumentParser):
    """Command line parser that raises ``UsageError`` for every failure but ``--help``.

    ``-h`` and ``--help`` keep printing the full help and exiting with status 0. Every
    other command line failure becomes one bounded, control-free diagnostic carried by
    ``UsageError``, which reaches stderr as one line.
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

    Every option may also be supplied through the environment variable its help names,
    and the option wins whenever both carry a value. Abbreviated option names are not
    accepted.
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
            "Validate one GenApp Policy-Issue landing record and write it as a single "
            "S3 object under the landing prefix.\n"
            "The bytes of the record file are the bytes uploaded: no amount is "
            "derived, no key is added, removed, renamed or reordered, and the JSON is "
            "never re-serialised.\n"
            "Exit status: 0 success, 2 record rejected, 3 command line or setting "
            "rejected, 4 S3 endpoint, bucket or object operation unsuccessful."
        ),
        epilog=(
            f"Object key: {key_template}\n"
            f"Object URI: {SERVICE_NAME}://<bucket>/<key>, written with content type "
            f"{OBJECT_CONTENT_TYPE}. Partitioning applies to this key prefix alone.\n"
            "In landing mode stdout carries exactly one line, the URI of the object "
            "written; in probe mode it carries exactly one line, the probe verdict. "
            "Every other message reaches stderr, and no credential, token or endpoint "
            "value is ever printed.\n"
            f"{ENDPOINT_URL_VARIABLE} or --endpoint-url directs the client at a local "
            "S3-compatible endpoint; with neither present the client addresses AWS S3. "
            "Access is established from resolved credentials, a resolved region and a "
            "bucket that answers a head request, and an environment variable whose "
            "name merely begins with AWS is never read as a credential.\n"
            "This tool creates no bucket and provisions nothing. It writes one object "
            "and nothing to the local filesystem.\n"
            "Decision rationale: modernization/docs/decision-log.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--record",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "landing JSON record written by extract_commarea.py, uploaded byte for "
            f"byte, of at most {MAX_RECORD_BYTES} bytes; required unless --probe is "
            "given, which reads no record"
        ),
    )
    parser.add_argument(
        "--bucket",
        default=None,
        metavar="NAME",
        help=(
            "destination bucket, which must already exist; defaults to the "
            f"{BUCKET_VARIABLE} environment variable. There is no built-in bucket name"
        ),
    )
    parser.add_argument(
        "--source-system-key",
        default=None,
        metavar="VALUE",
        help=(
            "source-system element of the landing prefix, which must equal the "
            f"record's own {SOURCE_SYSTEM_KEY_FIELD} value; defaults to the "
            f"{SOURCE_SYSTEM_KEY_VARIABLE} environment variable, then to "
            f"{DEFAULT_SOURCE_SYSTEM_KEY}. At most {MAX_SEGMENT_CHARACTERS} characters "
            "drawn from ASCII letters, digits, underscore, dot and hyphen"
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
        "--entity",
        default=None,
        metavar="VALUE",
        help=(
            "entity element of the landing prefix (default: "
            f"{DEFAULT_ENTITY}), under the same accepted characters as "
            "--source-system-key"
        ),
    )
    parser.add_argument(
        "--endpoint-url",
        default=None,
        metavar="URL",
        help=(
            "S3 endpoint to address, selecting a local S3-compatible endpoint; "
            f"defaults to the {ENDPOINT_URL_VARIABLE} environment variable. With "
            "neither present the client addresses AWS S3"
        ),
    )
    parser.add_argument(
        "--region",
        default=None,
        metavar="NAME",
        help=(
            "region to address; defaults to the "
            f"{' environment variable, then the '.join(REGION_VARIABLES)} environment "
            "variable, and then to the region the session resolves for itself"
        ),
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help=(
            "confirm credentials, region and bucket access by writing and deleting one "
            "probe object outside the landing prefix, then exit; no landing object is "
            "written and no record is read"
        ),
    )
    return parser


def _require_record_path(supplied: Path | None) -> Path:
    """Return the landing record path, refusing a landing run that names none.

    Raises ``UsageError`` when ``supplied`` is None.
    """
    if supplied is None:
        raise UsageError(
            "no landing record is named: supply --record with the path to the record "
            "extract_commarea.py wrote. It is required for every landing run, and only "
            "--probe, which reads no record, may omit it"
        )
    return supplied


def _run(args: argparse.Namespace) -> str:
    """Run one probe or one landing and return the single line to write to stdout.

    Settings are resolved first, so a missing bucket, region or credential is reported
    before any record is read. In probe mode no record is read and no landing object is
    written.
    """
    bucket = resolve_bucket(args.bucket)
    region = resolve_region(args.region)
    endpoint_url = resolve_endpoint_url(args.endpoint_url)
    if args.probe:
        client = resolve_s3_access(bucket, region, endpoint_url)
        key = probe_bucket_access(client, bucket)
        shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
        _note(f"the access probe wrote and deleted {shown_key}")
        return f"{PROBE_VERDICT} {SERVICE_NAME}://{bucket}"
    record_path = _require_record_path(args.record)
    return land_record(
        record_path,
        bucket,
        resolve_source_system_key(args.source_system_key),
        resolve_entity(args.entity),
        resolve_extract_date(args.extract_date),
        region=region,
        endpoint_url=endpoint_url,
    )


def main(argv: list[str] | None = None) -> int:
    """Land one record or run one access probe, returning the exit status.

    ``argv`` defaults to the process arguments. Exactly one line reaches stdout on
    success: the URI of the object written, or the probe verdict. Every diagnostic
    reaches stderr as one control-free line, names the setting to supply when one is
    missing, and carries no credential, token or endpoint value. A rejected command
    line is reported through that same single line, without a usage block, while
    ``--help`` prints the full help and exits with status 0.
    """
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        result = _run(args)
    except LandingError as error:
        print(f"{_PROGRAM}: {_one_line(str(error))}", file=sys.stderr)
        return error.exit_status
    except KeyboardInterrupt:
        print(f"{_PROGRAM}: interrupted before completion", file=sys.stderr)
        return EXIT_INTERRUPTED

    print(result)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

