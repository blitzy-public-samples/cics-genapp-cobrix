#!/usr/bin/env python3
"""Decode the returned GenApp Policy-Issue COMMAREA into the landing JSON record.

WHAT THIS TOOL DOES
    Reads the post-chain COMMAREA capture the harness driver writes, decodes each
    landed value at the offset, length and kind ``copybook_field_map.yml`` records for
    it, derives ``policy_type`` from the request id through the map's
    ``request_routing`` table, normalises the returned ``CA-LASTCHANGED`` value to
    ISO-8601, and writes one landing JSON object carrying exactly the keys the map
    lists under ``landing.field_order``. No amount is derived: each premium and the
    payment are carried through as the digits the record holds, with leading zeros
    stripped, and a premium the derived policy type does not apply to is written as
    null. The four commercial peril codes are never read. A window the map records
    ``blank_window_lands_null`` for is written as null when it holds only spaces,
    whatever its kind; every other window whose content the map requires, an applicable
    amount and a value the chain assigns among them, is refused when it is blank.

WHICH RECORDS IT LANDS
    Successful extractions only. A returned ``CA-RETURN-CODE`` of
    ``RETURN_CODE_SUCCESS`` is landed. A record carrying any other code of the domain
    the field map records - ``70`` policy insert returned SQLCODE -530, ``80`` VSAM
    write response was not normal, ``90`` SQL failure, ``98`` COMMAREA shorter than
    the required length, ``99`` unsupported request id - is refused with a diagnostic
    naming the observed code, the meaning the map's ``return_codes`` section records
    for it and the stage ``RETURN_CODE_STAGES`` records it stopped at, and nothing is
    written; the codes and their meanings are set at base/src/lgapol01.cbl:108-126 and
    base/src/lgapdb01.cbl:184-213,290-305. A code outside that recorded domain is
    refused as a breached record contract, with its own status. The landing and raw
    contracts therefore carry no failure row: the evidence of a run that returned
    another code is the harness captures and driver logs the harness retains under
    modernization/validation/artifacts/.

WHICH INPUTS IT ACCEPTS
    --commarea   the post-chain COMMAREA capture: exactly
                 ``COMMAREA_RECORD_LENGTH`` characters, optionally followed by one
                 line ending, in a file of at most ``MAX_CAPTURE_BYTES`` bytes.
    --field-map  the field map supplying every offset, length, kind, routing entry,
                 nullability rule, return-code meaning and landing key, in a file of
                 at most ``MAX_FIELD_MAP_BYTES`` bytes (default:
                 ``copybook_field_map.yml`` beside this script; every working
                 directory resolves the same default).
    --output     destination path for the landing JSON record; missing parent
                 directories are created and an existing file is left in place unless
                 ``--overwrite`` is given.
    --overwrite  replace an existing regular file at the destination. Without it a
                 destination that already exists is refused by name and nothing is
                 written; with it the record replaces that file, which keeps the mode
                 it carries.
    --source-system-key
                 the source-system discriminator written to the record. Taken from
                 the ``SOURCE_SYSTEM_KEY`` environment variable when the option is
                 omitted and from ``DEFAULT_SOURCE_SYSTEM_KEY`` when neither is
                 present; a variable holding the empty string or whitespace alone
                 counts as unset, which is the resolution every command-line tool of
                 this bridge applies. It carries 1 to
                 ``MAX_SOURCE_SYSTEM_KEY_CHARACTERS`` characters drawn from ASCII
                 letters, digits, underscore, dot and hyphen. The same value forms
                 the ``source_system_key`` element of the landing prefix.
    --show-identifiers
                 carry record values in diagnostics and the request id, policy type,
                 policy number, customer number, broker id, broker's reference and
                 return code on the summary line. Withheld by default; the
                 ``GENAPP_SHOW_IDENTIFIERS`` environment variable carrying one of
                 ``SHOW_IDENTIFIERS_ENABLING``, in any case and ignoring surrounding
                 spaces, enables the same diagnostics and the same summary line as the
                 option. Every other value of that variable, an empty one and an absent
                 variable leave the values withheld, and the withheld summary line
                 carries the digest of the policy number rather than the number.
    --self-test  run the built-in case matrix instead of extracting a record. It
                 accepts ``--field-map`` and neither ``--commarea`` nor ``--output``.

WHICH DESTINATIONS IT ACCEPTS
    The destination is canonicalised - every component of its parent chain is
    resolved, so a symbolic-link chain and a ``/proc/self/cwd`` style alias reach the
    same check as the path they name. A canonical destination inside the repository
    directory holding this script must stand below one of the generated roots
    ``GENERATED_OUTPUT_ROOTS``; any other path inside that repository is refused by
    name, an authored file, the committed evidence under
    modernization/validation/artifacts/ and anything below ``READ_ONLY_SOURCE_ROOT``
    among them. A canonical destination outside that repository is accepted. A
    destination whose final component is a symbolic link, one that resolves onto an
    existing entry that is not a regular file, and one that resolves onto an existing
    regular file without ``--overwrite``, are refused before anything is created.

WHAT IT WRITES
    One JSON object serialised as a single line terminated by one line feed, holding
    the landing keys in the order the field map lists them. Every value is a JSON
    string or null; no number, boolean, array or nested object is emitted. The record
    is written through a temporary entry in the destination directory, created and
    moved through a descriptor held on that directory, so the parent the record lands
    in cannot be substituted between the checks and the write. Each directory this
    tool creates carries mode ``DIRECTORY_MODE`` and a record this tool creates carries
    mode ``FILE_MODE``, both set on the created entry itself so the ambient umask cannot
    widen them; a record written over an existing file under ``--overwrite`` keeps the
    mode that file carries. On success one summary line naming the destination, the
    resolved source-system key with where it came from, the derived policy type and the
    landed key counts reaches stdout, and nothing else does; the business identifiers
    reach stdout only under ``--show-identifiers`` or an enabling
    ``GENAPP_SHOW_IDENTIFIERS`` value, which select the same line.

HOW IT FAILS
    Every failure writes one diagnostic line to stderr and returns a non-zero status:
    2 for a capture that breaches the record contract, 3 for a runtime environment
    that is not the pinned one or a field map missing a member this tool reads or
    contradicting itself, 4 for an unreadable input, a
    refused output or a rejected command line, 5 for a failed self-test case, 6 for a
    capture whose returned ``CA-RETURN-CODE`` is a recorded code other than
    ``RETURN_CODE_SUCCESS``, 130 for an interrupt. Diagnostics carry untrusted text
    escaped to one printable 7-bit ASCII line. A record value never reaches a
    diagnostic or stdout unless ``--show-identifiers`` is given: without it a rejected
    window, timestamp or identifier is reported by field name, COBOL item, byte range,
    the constraint it breached and its character count alone. The tool never prompts
    and requires no TTY. It reads the capture and the field map without modifying
    either, and writes nothing outside the destination the command line names; an
    interrupt removes the temporary entry it was writing through, and under
    ``--self-test`` it writes only inside the private scratch directory the case matrix
    creates and removes.

WHAT --self-test CHECKS
    One case matrix, run in this process against the field map and records this module
    renders from the map's own windows: field-map validation and every way the map can
    contradict itself, capture reading at, below and above the record length, window
    decoding for every landing key including blank and all-zero windows, the window the
    map records ``blank_window_lands_null`` for against the blank windows that stay
    refused, a control character in every alphanumeric window, request-id
    routing for the four routed ids and an unrouted one, all six return codes and an
    out-of-domain code, timestamp normalisation and calendar validity for both dates
    and the returned timestamp, the product-specific NULL pattern for M, C, E and H,
    landing key order and JSON serialisation, summary redaction with and without
    ``--show-identifiers`` and under every ``GENAPP_SHOW_IDENTIFIERS`` value it
    resolves, the resolved source-system key and its origin on the summary line, the
    environment guard against the pinned runtime, destination confinement and refusal
    including the committed evidence directory, the refusal of an existing destination
    and its replacement under ``--overwrite``, the modes of the created directory and
    the landed record under a permissive umask and the mode an overwritten file keeps,
    and the output failure paths. Every case runs in one private scratch directory the
    matrix creates
    and removes, reads and writes nothing else, and depends on no network, no S3 and
    no clock.

WHICH CHARACTER SET IT READS
    The capture is decoded as ``CAPTURE_ENCODING``, the workstation character set the
    local harness writes; a z/OS extract carries the installation CCSID, documented as
    285 by default, and is not decoded by this tool. A decoded alphanumeric window
    carrying a control character - one of the C0 range, DEL or one of the C1 range - is
    refused with the record contract's own status and nothing is written, so no landed
    value carries one; a numeric window admits digits alone.

WHERE THIS STEP SITS
    Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge and
    Figure 5 — Validation Harness Control Flow, both in
    modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md, a planned deliverable not present at this milestone.
"""

from __future__ import annotations

import sys

_PROGRAM = "extract_commarea"

# Status a run returns when the interpreter running it, or a version installed for it,
# is not the one the project pins, and the status an interrupted run returns. Both are
# declared before every import but sys so the environment is confirmed, and an
# interrupt is reported, before an import of this module can fail on its own.
EXIT_ENVIRONMENT_REJECTED = 3
EXIT_INTERRUPTED = 130
INTERRUPTED_MESSAGE = f"{_PROGRAM}: interrupted before completion"

# Python release series and distribution versions this tool runs under: the series
# modernization/requirements.txt is installed against and the exact version it pins for
# every distribution this module imports. The interpreter carrying them is
# modernization/.venv/bin/python.
PINNED_PYTHON_SERIES = (3, 12)
PINNED_DISTRIBUTIONS = (("PyYAML", "6.0.3"),)
PINNED_INTERPRETER = "modernization/.venv/bin/python"
PINNED_REQUIREMENTS = "modernization/requirements.txt"


def _report_interrupt() -> None:
    """Write the one line an interrupted run reports to stderr, and return None."""
    print(INTERRUPTED_MESSAGE, file=sys.stderr)


def _printable(text: str) -> str:
    """Return ``text`` with every character a terminal would act on replaced."""
    return "".join(character if character.isprintable() else "?" for character in text)


def _refuse_environment(reason: str) -> None:
    """Write one line naming ``reason`` and end the run, returning None to no caller."""
    print(f"{_PROGRAM}: {_printable(reason)}", file=sys.stderr)
    raise SystemExit(EXIT_ENVIRONMENT_REJECTED)


def confirm_pinned_environment() -> None:
    """Confirm this run carries the pinned interpreter series and versions.

    The interpreter's release series is compared with ``PINNED_PYTHON_SERIES`` and the
    installed version of every distribution in ``PINNED_DISTRIBUTIONS`` with the version
    pinned there, before any distribution is imported: an interpreter of another series,
    a distribution that is absent and a distribution at another version each end the run
    with ``EXIT_ENVIRONMENT_REJECTED`` and one line naming what was found, what is
    required and the interpreter to run this tool through. A run whose environment
    matches returns None and nothing is written.
    """
    found = ".".join(str(number) for number in sys.version_info[:3])
    required = ".".join(str(number) for number in PINNED_PYTHON_SERIES)
    if sys.version_info[: len(PINNED_PYTHON_SERIES)] != PINNED_PYTHON_SERIES:
        _refuse_environment(
            f"this tool runs on the Python {required} series, and the interpreter "
            f"running it is Python {found} at {sys.executable}; run it through "
            f"{PINNED_INTERPRETER}"
        )
    from importlib import metadata

    for name, pinned in PINNED_DISTRIBUTIONS:
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            _refuse_environment(
                f"{name} is not installed for the interpreter at {sys.executable}, and "
                f"{PINNED_REQUIREMENTS} pins {name} {pinned}; run this tool through "
                f"{PINNED_INTERPRETER}"
            )
            return
        if installed != pinned:
            _refuse_environment(
                f"{name} {installed} is installed for the interpreter at "
                f"{sys.executable}, and {PINNED_REQUIREMENTS} pins {name} {pinned}; "
                f"run this tool through {PINNED_INTERPRETER}"
            )


try:
    confirm_pinned_environment()

    import argparse
    import contextlib
    import copy
    import datetime
    import hashlib
    import io
    import json
    import os
    import re
    import shutil
    import stat
    import tempfile
    from collections.abc import Callable, Iterable, Mapping, Sequence
    from pathlib import Path
    from typing import Any, NamedTuple, NoReturn

    import yaml
except KeyboardInterrupt:
    _report_interrupt()
    raise SystemExit(EXIT_INTERRUPTED) from None

# Field map used when --field-map is omitted, resolved from this script's own
# directory rather than from the working directory.
_THIS_DIR = Path(__file__).resolve().parent
DEFAULT_FIELD_MAP = _THIS_DIR / "copybook_field_map.yml"

# Repository directory holding this script (modernization/extraction/ -> repository
# root) and the read-only source directory no destination may resolve inside. A copy of
# this script placed fewer than two directories below the filesystem root takes its own
# directory as the root, which keeps importing this module free of any path assumption.
# The root is taken from this file's own location and never from the working directory.
_ANCESTORS = _THIS_DIR.parents
REPOSITORY_ROOT = _ANCESTORS[1] if len(_ANCESTORS) > 1 else _THIS_DIR
READ_ONLY_SOURCE_ROOT = REPOSITORY_ROOT / "base"

# The generated roots of the bridge, relative to REPOSITORY_ROOT. A destination that
# canonicalises inside the repository must stand below one of them; every other path
# inside the repository holds an authored artifact, committed evidence or read-only
# source and is refused. modernization/validation/artifacts is not among them: it holds
# the committed harness evidence its own evidence-manifest.sha256 hashes and
# modernization/validation/verify_readonly.sh exempts by name, and a destination
# resolving onto it is refused like any other path inside the repository.
GENERATED_OUTPUT_ROOTS = (
    Path("modernization/harness/build"),
    Path("modernization/validation/expected"),
    Path("modernization/dbt/genapp_rqi/target"),
    Path("modernization/dbt/genapp_rqi/logs"),
)

# Record width the capture must carry: the sum of the four level-03 items declared at
# base/src/lgcmarea.cpy:10-13, which are 6 + 2 + 10 + 32482 characters. The field map
# must declare this same width under record.length.
COMMAREA_RECORD_LENGTH = 32500

# Character set the capture is decoded with, and the line endings one trailing line
# ending may consist of.
CAPTURE_ENCODING = "ascii"
_TRAILING_LINE_ENDINGS = ("\r\n", "\n", "\r")

# Bytes one read takes from each input before anything parses it, and the bytes one
# read of an input asks for at a time.
MAX_CAPTURE_BYTES = 64 * 1024
MAX_FIELD_MAP_BYTES = 1024 * 1024
READ_CHUNK_BYTES = 65536

# Statuses this tool returns. EXIT_ENVIRONMENT_REJECTED and EXIT_INTERRUPTED are
# declared with the environment check above, before the imports they cover.
EXIT_OK = 0
EXIT_RECORD_REJECTED = 2
EXIT_FIELD_MAP_INVALID = EXIT_ENVIRONMENT_REJECTED
EXIT_IO_ERROR = 4
EXIT_SELF_TEST_FAILED = 5
EXIT_CHAIN_NOT_SUCCESSFUL = 6

# Characters of untrusted text one diagnostic fragment carries before truncation, and
# the window positions one diagnostic lists.
MAX_DIAGNOSTIC_CHARACTERS = 64
MAX_DIAGNOSTIC_PATH_CHARACTERS = 160
MAX_DIAGNOSTIC_MESSAGE_CHARACTERS = 200
MAX_REPORTED_POSITIONS = 8

# Opt-in carrying record values into diagnostics and the business identifiers onto the
# summary line, the environment variable consulted when the option is omitted, and the
# values that variable may carry to enable it. Without the opt-in a record value is
# reported by its character count and the policy number by its digest.
SHOW_IDENTIFIERS_OPTION = "--show-identifiers"
SHOW_IDENTIFIERS_VARIABLE = "GENAPP_SHOW_IDENTIFIERS"
SHOW_IDENTIFIERS_ENABLING = ("1", "true", "yes", "on")
IDENTIFIER_DIGEST_CHARACTERS = 12
IDENTIFIER_DIGEST_PREFIX = "sha256-"

# Candidate names tried when creating the temporary entry the record is written
# through, the modes carried by a directory this tool creates and by a record this tool
# creates, and the directories one containment check ascends before it reports the
# destination directory as unreachable from the filesystem root. Both modes are set on
# the created entry as well as requested at creation, so the ambient umask cannot widen
# either: the landed policy data is readable and writable by its owner alone. Neither
# mode is applied to an entry this tool did not create: a record written over an
# existing file under OVERWRITE_OPTION carries the mode that file already carries, and
# a directory that already exists keeps its own mode.
MAX_TEMPORARY_ATTEMPTS = 8
DIRECTORY_MODE = 0o700
FILE_MODE = 0o600
MAX_CONTAINMENT_ASCENT = 256

# Opt-in replacing an existing regular file at the destination. Without it a destination
# that resolves onto an existing file is refused by name and nothing is written.
OVERWRITE_OPTION = "--overwrite"

# Item kinds the field map declares under layout.<group>.items[].kind.
KIND_NUMERIC = "numeric_display"
KIND_ALPHANUMERIC = "alphanumeric"
KNOWN_KINDS = (KIND_NUMERIC, KIND_ALPHANUMERIC)

# Values the field map records under fields[].populated_by and fields[].runtime_status.
POPULATED_BY_CHAIN = "chain"
RUNTIME_STATUS_DERIVED = "derived"
RUNTIME_STATUS_WAREHOUSE_ASSIGNED = "warehouse_assigned"

# Group the field map records for the six amount entries.
GROUP_PREMIUM_PAYMENT = "premium_payment"

# The return code the chain writes on a completed policy issue.
RETURN_CODE_SUCCESS = "00"

# The return code LGAPVS01 writes when the VSAM write response was not normal, at
# base/src/lgapvs01.cbl:142-147.
RETURN_CODE_VSAM_WRITE_FAILED = "80"

# The return codes a record may be landed under, and the stage each remaining code of
# the recorded domain stops at. Only a completed policy issue is landed, so
# LANDABLE_RETURN_CODES holds RETURN_CODE_SUCCESS alone; every other code of the domain
# is rejected and named with the stage it stopped at and the base/src locators of that
# stage.
LANDABLE_RETURN_CODES = (RETURN_CODE_SUCCESS,)
RETURN_CODE_STAGES = {
    "70": (
        "the policy insert returned SQLCODE -530 and no policy row was written "
        "(base/src/lgapdb01.cbl:290-299)"
    ),
    RETURN_CODE_VSAM_WRITE_FAILED: (
        "the policy and product rows were written and the identity and timestamp were "
        "read back, and the VSAM write response was then not normal, so the chain did "
        "not complete the issue (base/src/lgapvs01.cbl:142-147, "
        "base/src/lgapdb01.cbl:307-321)"
    ),
    "90": (
        "a SQL operation failed before or during the inserts "
        "(base/src/lgapdb01.cbl:300-303, 389-395, 427-433, 473-479, 547-553)"
    ),
    "98": (
        "the COMMAREA was shorter than the length the request requires and the chain "
        "returned before any insert (base/src/lgapol01.cbl:108-116, "
        "base/src/lgapdb01.cbl:181-213)"
    ),
    "99": (
        "the request id is not one the chain routes and no product path ran "
        "(base/src/lgapdb01.cbl:184-207, 239)"
    ),
}

# Landing keys this tool treats individually. Each must appear in the field map's
# landing.field_order, and each name below is the map's own landing_field value.
LANDING_SOURCE_SYSTEM_KEY = "source_system_key"
LANDING_REQUEST_ID = "request_id"
LANDING_RETURN_CODE = "return_code"
LANDING_POLICY_TYPE = "policy_type"
LANDING_POLICY_NUMBER = "policy_number"
LANDING_CUSTOMER_NUMBER = "customer_number"
LANDING_ISSUE_DATE = "issue_date"
LANDING_EXPIRY_DATE = "expiry_date"
LANDING_LAST_CHANGED = "last_changed"
LANDING_BROKER_ID = "broker_id"
LANDING_BROKERS_REFERENCE = "brokers_reference"

# Landing keys validated as calendar dates, being the two X(10) date items declared at
# base/src/lgcmarea.cpy:38-39. Each is parsed as a real date before it is landed, so a
# value of the right shape that names no day, such as 2026-02-31, is rejected here
# rather than at the DATE cast of the downstream dbt models.
CALENDAR_DATE_FIELDS = (LANDING_ISSUE_DATE, LANDING_EXPIRY_DATE)

# Canonical column types the field map records under fields[].targets[].type. They
# name the landing keys whose value carries calendar and clock semantics, which this
# tool confirms before the value is written.
CANONICAL_TYPE_DATE = "DATE"
CANONICAL_TYPE_TIMESTAMP = "TIMESTAMP"

# Landing keys the summary line carries only once record values are shown, which
# --show-identifiers and an enabling SHOW_IDENTIFIERS_VARIABLE value both select.
IDENTIFIER_FIELDS = (
    LANDING_POLICY_NUMBER,
    LANDING_CUSTOMER_NUMBER,
    LANDING_BROKER_ID,
    LANDING_BROKERS_REFERENCE,
)

# Source-system key accepted values and where an omitted option looks for one.
DEFAULT_SOURCE_SYSTEM_KEY = "GENAPP_CLASS_EXEMPLAR"
SOURCE_SYSTEM_KEY_VARIABLE = "SOURCE_SYSTEM_KEY"
MAX_SOURCE_SYSTEM_KEY_CHARACTERS = 64
_SOURCE_SYSTEM_KEY_SHAPE = re.compile(r"\A[A-Za-z0-9_.\-]+\Z")

# Window content accepted for a numeric_display item, and the characters escaped out
# of a diagnostic.
_ASCII_DIGITS = re.compile(r"\A[0-9]+\Z")
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f-\x9f]")

# Shape of a landed calendar date, being the form the two X(10) date items carry.
CALENDAR_DATE_FORM = "YYYY-MM-DD"
_CALENDAR_DATE_SHAPE = re.compile(r"\A([0-9]{4})-([0-9]{2})-([0-9]{2})\Z")

# Timestamp forms accepted for CA-LASTCHANGED, tried in this order. The first is the
# Db2 character form the 26-character read-back at base/src/lgapdb01.cbl:315-321
# carries; the rest are ISO-8601 with a T or a space separator. Each accepts a
# fractional-second part of one to six digits and each accepts the form without one.
# Every form is a shape only: the calendar and clock components a matched form yields
# are validated afterwards.
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

# Digits the emitted fractional-second part carries, and the accepted ranges of the
# clock components a matched timestamp shape yields.
TIMESTAMP_FRACTION_DIGITS = 6
_HOUR_RANGE = (0, 23)
_MINUTE_RANGE = (0, 59)
_SECOND_RANGE = (0, 59)
_MONTH_RANGE = (1, 12)
_DAY_RANGE = (1, 31)

# Separator and precision the normalised timestamp is emitted with.
TIMESTAMP_OUTPUT_SEPARATOR = "T"
TIMESTAMP_OUTPUT_PRECISION = "microseconds"


class ExtractError(Exception):
    """Diagnostic raised by this module, carrying the process status to return."""

    exit_status = EXIT_RECORD_REJECTED


class RecordError(ExtractError):
    """The capture breaches the COMMAREA record contract."""

    exit_status = EXIT_RECORD_REJECTED


class ChainNotSuccessfulError(ExtractError):
    """The returned ``CA-RETURN-CODE`` is a recorded code other than ``00``.

    The capture is well formed and the chain ran; it did not complete the policy
    issue, so there is no successful extraction to land. This status is distinct from
    the one a breached record contract returns, which a code outside the recorded
    domain carries.
    """

    exit_status = EXIT_CHAIN_NOT_SUCCESSFUL


class FieldMapError(ExtractError):
    """The field map is missing a member this tool reads or contradicts itself."""

    exit_status = EXIT_FIELD_MAP_INVALID


class InputOutputError(ExtractError):
    """An input cannot be read or the destination cannot be written."""

    exit_status = EXIT_IO_ERROR


class UsageError(ExtractError):
    """The command line omits a required argument or carries a rejected value."""

    exit_status = EXIT_IO_ERROR


# Whether a diagnostic and the summary may carry record values. Set once from the
# command line and the environment before any decoding starts.
_show_identifiers = False


def set_show_identifiers(enabled: bool) -> None:
    """Record whether a diagnostic and the summary may carry record values."""
    global _show_identifiers
    _show_identifiers = bool(enabled)


def show_identifiers_enabled() -> bool:
    """Return True when a diagnostic and the summary may carry record values."""
    return _show_identifiers


def resolve_show_identifiers(supplied: bool) -> bool:
    """Return whether record values are shown, from the option then the environment.

    ``supplied`` is the ``--show-identifiers`` flag, which enables display on its own.
    With the flag absent the ``SHOW_IDENTIFIERS_VARIABLE`` environment variable enables
    display
    when it carries one of ``SHOW_IDENTIFIERS_ENABLING``, in any case and ignoring
    surrounding spaces; every other value, including an empty one and an absent
    variable, leaves record values withheld.
    """
    if supplied:
        return True
    carried = os.environ.get(SHOW_IDENTIFIERS_VARIABLE)
    if carried is None:
        return False
    return carried.strip().lower() in SHOW_IDENTIFIERS_ENABLING


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
    if limit < 1:
        limit = 1
    kept = text[:limit]
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


def _withheld(length: int) -> str:
    """Return the fragment standing for a withheld value of ``length`` characters."""
    return f"<redacted {length} chars>"


def _value(value: str, limit: int = MAX_DIAGNOSTIC_CHARACTERS) -> str:
    """Return one record value for a diagnostic, withheld unless display is enabled.

    With display enabled the value is quoted and escaped as any other fragment. With
    display withheld the fragment carries the character count alone, so a diagnostic
    still states how long the rejected value was without carrying the value itself.
    """
    if show_identifiers_enabled():
        return _shown(value, limit)
    return _withheld(len(value))


def _digest(value: str) -> str:
    """Return a stable short digest of ``value``, standing in for the value itself.

    The digest is the leading ``IDENTIFIER_DIGEST_CHARACTERS`` hexadecimal characters
    of the SHA-256 of the UTF-8 encoding of ``value``, so two runs carrying the same
    identifier report the same fragment.
    """
    encoded = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return IDENTIFIER_DIGEST_PREFIX + encoded[:IDENTIFIER_DIGEST_CHARACTERS]


def _quote_all(names: Iterable[str]) -> str:
    """Return ``names`` quoted, escaped and joined by a comma, in the order given."""
    return ", ".join(_shown(str(name)) for name in names)


def _window_range(offset: int, length: int) -> str:
    """Return the 1-based inclusive byte range a window covers, as ``first-last``."""
    return f"{offset}-{offset + length - 1}"


def _offending_characters(window: str) -> str:
    """Return the distinct non-digit characters of ``window``, in first-seen order."""
    seen: list[str] = []
    for character in window:
        if character not in "0123456789" and character not in seen:
            seen.append(character)
    return _quote_all(seen)


def _non_digit_report(window: str) -> str:
    """Return how many characters of ``window`` are outside 0-9 and where they sit.

    Positions are 1-based within the window and at most ``MAX_REPORTED_POSITIONS`` of
    them are listed, with the number withheld recorded. The distinct offending
    characters are named only when record values are shown.
    """
    positions = [
        index
        for index, character in enumerate(window, start=1)
        if character not in "0123456789"
    ]
    listed = ", ".join(str(position) for position in positions[:MAX_REPORTED_POSITIONS])
    withheld = len(positions) - min(len(positions), MAX_REPORTED_POSITIONS)
    if withheld:
        listed = f"{listed} (+{withheld} further)"
    report = (
        f"{len(positions)} characters lie outside 0-9, at window positions {listed}"
    )
    if show_identifiers_enabled():
        return f"{report}; they are {_offending_characters(window)}"
    return report


def _control_character_report(window: str) -> str:
    """Return how many characters of ``window`` are control characters and where.

    A control character is one of the C0 range, DEL or one of the C1 range, which is
    what ``_CONTROL_CHARACTERS`` matches. Positions are 1-based within the window and at
    most ``MAX_REPORTED_POSITIONS`` of them are listed, with the number withheld
    recorded. The offending characters are named, each escaped to printable 7-bit ASCII,
    only when record values are shown.
    """
    positions = [
        index
        for index, character in enumerate(window, start=1)
        if _CONTROL_CHARACTERS.search(character)
    ]
    listed = ", ".join(str(position) for position in positions[:MAX_REPORTED_POSITIONS])
    withheld = len(positions) - min(len(positions), MAX_REPORTED_POSITIONS)
    if withheld:
        listed = f"{listed} (+{withheld} further)"
    report = (
        f"{len(positions)} characters are control characters, at window positions "
        f"{listed}"
    )
    if show_identifiers_enabled():
        distinct = dict.fromkeys(
            character
            for character in window
            if _CONTROL_CHARACTERS.search(character)
        )
        return f"{report}; they are {_quote_all(distinct)}"
    return report


# ---------------------------------------------------------------------------
# Field map
# ---------------------------------------------------------------------------


class LandingField(NamedTuple):
    """One landing key and the COMMAREA window, where there is one, that supplies it.

    ``offset``, ``length`` and ``kind`` are None for a landing key the map records
    without a ``commarea`` block, which is a key this tool derives rather than reads.
    ``applicable_policy_types`` holds the policy-type letters the map records for the
    entry, ``evidence`` holds the locators it cites, ``domain`` holds the accepted
    values where the entry records them, and ``target_types`` holds the distinct
    canonical column types its ``targets`` block records, which is where the calendar
    and clock semantics of a value are declared. ``blank_window_lands_null`` is the
    map's ``blank_window_lands_null`` member: True for a window that lands null when it
    holds only spaces, whatever its kind, and False for every window whose content is
    required.
    """

    name: str
    logical_entry: str
    group: str
    runtime_status: str
    populated_by: str | None
    item: str | None
    copybook: str | None
    line: int | None
    pic: str | None
    offset: int | None
    length: int | None
    kind: str | None
    applicable_policy_types: tuple[str, ...]
    evidence: tuple[str, ...]
    domain: tuple[str, ...] = ()
    target_types: tuple[str, ...] = ()
    blank_window_lands_null: bool = False

    @property
    def is_read_from_record(self) -> bool:
        """Return True when this key is decoded from a COMMAREA window."""
        return self.offset is not None and self.length is not None

    @property
    def locator(self) -> str:
        """Return the copybook locator of the declaring item, as ``path:line``."""
        if self.copybook and self.line:
            return f"{self.copybook}:{self.line}"
        return self.copybook or "no copybook locator recorded"

    @property
    def described(self) -> str:
        """Return the item, its locator and its byte range for use in a diagnostic."""
        if not self.is_read_from_record:
            return f"landing key {_shown(self.name)}"
        assert self.offset is not None and self.length is not None
        return (
            f"{self.item} ({self.locator}) bytes "
            f"{_window_range(self.offset, self.length)}"
        )


class FieldMap(NamedTuple):
    """Every member of ``copybook_field_map.yml`` this tool reads, already validated.

    ``fields`` is keyed by landing key and excludes the warehouse-assigned key, which
    ``source_system_key_field`` names. ``nullability`` maps a policy-type letter to the
    amount keys populated for it and the amount keys left null for it, with the keys
    the map records as always populated held separately in ``always_populated``.
    ``date_fields`` and ``timestamp_fields`` hold the landing keys whose recorded
    canonical type is ``CANONICAL_TYPE_DATE`` and ``CANONICAL_TYPE_TIMESTAMP``, whose
    values are confirmed as calendar dates and timestamps before they are written.
    ``return_code_meanings`` maps every code of ``return_code_domain`` to the meaning
    the map's ``return_codes`` section records for it.
    """

    path: Path
    record_length: int
    field_order: tuple[str, ...]
    fields: Mapping[str, LandingField]
    routing: Mapping[str, str]
    amount_fields: tuple[str, ...]
    always_populated: frozenset[str]
    nullability: Mapping[str, tuple[frozenset[str], frozenset[str]]]
    return_code_domain: tuple[str, ...]
    return_code_meanings: Mapping[str, str]
    source_system_key_field: str
    source_system_key_run_value: str
    chain_populated: frozenset[str]
    unrecognised_request_return_code: str
    date_fields: frozenset[str]
    timestamp_fields: frozenset[str]


class _DuplicateRejectingLoader(yaml.SafeLoader):
    """``yaml.SafeLoader`` that refuses a mapping which repeats a key.

    Loading raises ``yaml.constructor.ConstructorError`` naming the repeated key and
    the position it reappears at, instead of resolving that key to its last value. A
    key this loader cannot compare against the keys already seen raises the same error
    class. Every mapping defect reaches the caller as a YAML error.
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
                    f"found unhashable key of type {_type_name(key)}",
                    key_node.start_mark,
                ) from error
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {_display(key)}",
                    key_node.start_mark,
                )
        return super().construct_mapping(node, deep=deep)


def _path_of(where: str, key: str) -> str:
    """Return the dotted field map path of ``key`` inside the container at ``where``."""
    return f"{where}.{key}" if where else key


def _member(container: Any, key: str, where: str) -> Any:
    """Return ``container[key]``, raising ``FieldMapError`` when it is absent.

    ``where`` is the dotted path of ``container`` inside the field map, empty for the
    document root, and every diagnostic names the dotted path of the member itself.
    """
    if not isinstance(container, Mapping):
        raise FieldMapError(
            f"the field map records {_shown(where) if where else 'its root'} as "
            f"{_display(container)}; a mapping is required"
        )
    if key not in container:
        raise FieldMapError(
            f"the field map is missing {_shown(_path_of(where, key))}"
        )
    return container[key]


def _member_mapping(container: Any, key: str, where: str) -> Mapping[str, Any]:
    """Return a required member that must be a mapping."""
    value = _member(container, key, where)
    if not isinstance(value, Mapping):
        raise FieldMapError(
            f"the field map records {_shown(_path_of(where, key))} as "
            f"{_display(value)}; a mapping is required"
        )
    return value


def _member_sequence(container: Any, key: str, where: str) -> Sequence[Any]:
    """Return a required member that must be a sequence and not text."""
    value = _member(container, key, where)
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise FieldMapError(
            f"the field map records {_shown(_path_of(where, key))} as "
            f"{_display(value)}; a sequence is required"
        )
    return value


def _member_text(container: Any, key: str, where: str) -> str:
    """Return a required member that must be a non-empty string."""
    value = _member(container, key, where)
    if not isinstance(value, str) or not value:
        raise FieldMapError(
            f"the field map records {_shown(_path_of(where, key))} as "
            f"{_display(value)}; a non-empty string is required"
        )
    return value


def _member_integer(container: Any, key: str, where: str, minimum: int = 1) -> int:
    """Return a required member that must be an integer of at least ``minimum``."""
    value = _member(container, key, where)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise FieldMapError(
            f"the field map records {_shown(_path_of(where, key))} as "
            f"{_display(value)}; an integer of at least {minimum} is required"
        )
    return value


def _text_sequence(container: Any, key: str, where: str) -> tuple[str, ...]:
    """Return a required member that must be a sequence of non-empty strings."""
    values = _member_sequence(container, key, where)
    for position, value in enumerate(values):
        if not isinstance(value, str) or not value:
            raise FieldMapError(
                f"the field map records element {position} of "
                f"{_shown(_path_of(where, key))} as {_display(value)}; a non-empty "
                "string is required"
            )
    return tuple(str(value) for value in values)


def _optional_text_sequence(
    container: Mapping[str, Any], key: str, where: str
) -> tuple[str, ...]:
    """Return a sequence of non-empty strings, or an empty tuple when it is absent."""
    if container.get(key) is None:
        return ()
    return _text_sequence(container, key, where)


def _target_types(entry: Mapping[str, Any], where: str) -> tuple[str, ...]:
    """Return the distinct canonical column types the entry's ``targets`` records.

    Each element of a ``targets`` block records the relation, column, type and
    nullability of one canonical column the landing key feeds. The recorded types are
    where a landed value's calendar and clock semantics are declared: a key targeting
    ``CANONICAL_TYPE_DATE`` carries a calendar date and a key targeting
    ``CANONICAL_TYPE_TIMESTAMP`` carries a timestamp. The types are returned in
    first-seen order, so a key feeding both canonical relations with the same type
    yields that type once. An entry recording no ``targets`` block contributes none.

    Raises ``FieldMapError`` when ``targets`` is not a sequence of mappings or an
    element records a ``type`` that is not a non-empty string.
    """
    if entry.get("targets") is None:
        return ()
    targets = _member_sequence(entry, "targets", where)
    types: list[str] = []
    for position, target in enumerate(targets):
        recorded = _member_text(target, "type", f"{where}.targets[{position}]")
        if recorded not in types:
            types.append(recorded)
    return tuple(types)


def _blank_window_lands_null(
    entry: Mapping[str, Any], where: str, has_window: bool, populated_by: str | None
) -> bool:
    """Return the entry's ``blank_window_lands_null`` rule, checked against the entry.

    An absent member is False, which is the treatment of every window whose content is
    required. A member recording True is accepted only on an entry the rule can hold
    for: it must carry a ``commarea`` block, since a derived key reads no window; it
    must record ``populated_by`` other than ``POPULATED_BY_CHAIN``, since a value the
    chain assigns on every successful execution is required rather than optional; and
    every element of its ``targets`` block must record ``nullable`` as true, since a
    window landing null must reach a column that accepts null.

    Raises ``FieldMapError`` when the member is neither absent nor a boolean, and when
    an entry recording True carries no window, is populated by the chain or records a
    target that is not nullable.
    """
    recorded = entry.get("blank_window_lands_null")
    if recorded is None:
        return False
    if not isinstance(recorded, bool):
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.blank_window_lands_null')} as "
            f"{_display(recorded)}; true, false or no member at all is required"
        )
    if not recorded:
        return False
    if not has_window:
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.blank_window_lands_null')} as "
            "true without a 'commarea' block, so there is no window to find blank"
        )
    if populated_by == POPULATED_BY_CHAIN:
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.blank_window_lands_null')} as "
            f"true and {_shown(f'{where}.populated_by')} as "
            f"{_shown(POPULATED_BY_CHAIN)}; the chain assigns that value on every "
            f"execution returning {_shown(RETURN_CODE_SUCCESS)}, so a blank window of "
            "it is refused rather than landed"
        )
    for position, target in enumerate(_member_sequence(entry, "targets", where)):
        target_where = f"{where}.targets[{position}]"
        if _member(target, "nullable", target_where) is not True:
            raise FieldMapError(
                f"the field map records {_shown(f'{where}.blank_window_lands_null')} "
                f"as true and {_shown(f'{target_where}.nullable')} as "
                f"{_display(target.get('nullable'))}; a window that lands null feeds a "
                "nullable column alone"
            )
    return True


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def _read_bounded_bytes(path: Path, limit: int, what: str) -> bytes:
    """Return the bytes of one regular file, refusing anything past ``limit``.

    ``what`` names the input inside every diagnostic. The file is opened read-only and
    is never written, truncated or removed. Raises ``InputOutputError`` when the path
    cannot be opened or read, when it is not a regular file, or when it carries more
    than ``limit`` bytes.
    """
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError as error:
        raise InputOutputError(
            f"{what} cannot be opened: {_path_shown(path)}: {_reason(error)}"
        ) from error
    try:
        try:
            status = os.fstat(descriptor)
        except OSError as error:
            raise InputOutputError(
                f"{what} cannot be examined: {_path_shown(path)}: {_reason(error)}"
            ) from error
        if not stat.S_ISREG(status.st_mode):
            raise InputOutputError(
                f"{what} is not a regular file: {_path_shown(path)}"
            )
        chunks: list[bytes] = []
        collected = 0
        try:
            while collected <= limit:
                chunk = os.read(descriptor, READ_CHUNK_BYTES)
                if not chunk:
                    break
                chunks.append(chunk)
                collected += len(chunk)
        except OSError as error:
            raise InputOutputError(
                f"{what} cannot be read: {_path_shown(path)}: {_reason(error)}"
            ) from error
    finally:
        os.close(descriptor)
    if collected > limit:
        raise InputOutputError(
            f"{what} holds more than {limit} bytes: {_path_shown(path)}"
        )
    return b"".join(chunks)


def _without_one_trailing_line_ending(text: str) -> str:
    """Return ``text`` with at most one trailing line ending removed.

    A carriage return and line feed pair counts as one ending. A second ending is
    left in place and reaches the length check as content.
    """
    for ending in _TRAILING_LINE_ENDINGS:
        if text.endswith(ending):
            return text[: -len(ending)]
    return text


def read_commarea(path: Path, record_length: int = COMMAREA_RECORD_LENGTH) -> str:
    """Return the fixed-width record held by the post-chain COMMAREA capture.

    ``path`` names the capture the harness driver writes. It is decoded as
    ``CAPTURE_ENCODING`` rather than by the platform default, at most one trailing
    line ending is removed, and the remainder must hold exactly ``record_length``
    characters, being the width the four level-03 items at
    base/src/lgcmarea.cpy:10-13 declare. The capture is read once and is not
    modified.

    Raises ``InputOutputError`` when the capture cannot be read and ``RecordError``
    when it is not ``CAPTURE_ENCODING`` text or does not carry exactly
    ``record_length`` characters, naming the observed length.
    """
    content = _read_bounded_bytes(path, MAX_CAPTURE_BYTES, "the COMMAREA capture")
    try:
        text = content.decode(CAPTURE_ENCODING)
    except UnicodeDecodeError as error:
        raise RecordError(
            f"the COMMAREA capture is not {CAPTURE_ENCODING} text: "
            f"{_path_shown(path)}: {_reason(error)}"
        ) from error
    record = _without_one_trailing_line_ending(text)
    if len(record) != record_length:
        raise RecordError(
            f"the COMMAREA capture holds {len(record)} characters once one optional "
            f"trailing line ending is removed: {_path_shown(path)}; exactly "
            f"{record_length} characters are required"
        )
    return record


def _layout_windows(
    document: Mapping[str, Any], record_length: int
) -> Mapping[str, tuple[int, int, str]]:
    """Return each layout item's offset, length and kind, keyed by item name.

    Every group under ``layout`` contributes its ``items``. An item repeated with a
    differing offset, length or kind, an unknown kind, or a window reaching past
    ``record_length`` raises ``FieldMapError``.
    """
    groups = _member_mapping(document, "layout", "")
    windows: dict[str, tuple[int, int, str]] = {}
    for group_name, group in groups.items():
        where = f"layout.{group_name}"
        items = _member_sequence(group, "items", where)
        for position, item in enumerate(items):
            item_where = f"{where}.items[{position}]"
            name = _member_text(item, "item", item_where)
            offset = _member_integer(item, "offset", item_where)
            length = _member_integer(item, "length", item_where)
            kind = _member_text(item, "kind", item_where)
            if kind not in KNOWN_KINDS:
                raise FieldMapError(
                    f"the field map records {_shown(f'{item_where}.kind')} as "
                    f"{_shown(kind)}; one of {_quote_all(KNOWN_KINDS)} is required"
                )
            if offset + length - 1 > record_length:
                raise FieldMapError(
                    f"the field map places {name} at bytes "
                    f"{_window_range(offset, length)}, past the {record_length}-"
                    f"character record: {item_where}"
                )
            existing = windows.get(name)
            if existing is not None and existing != (offset, length, kind):
                raise FieldMapError(
                    f"the field map declares {name} twice with differing placement: "
                    f"bytes {_window_range(existing[0], existing[1])} of kind "
                    f"{_shown(existing[2])} and bytes "
                    f"{_window_range(offset, length)} of kind {_shown(kind)}"
                )
            windows[name] = (offset, length, kind)
    if not windows:
        raise FieldMapError("the field map records no item under 'layout'")
    return windows


def _landing_field(
    entry: Mapping[str, Any],
    where: str,
    landing_name: str,
    windows: Mapping[str, tuple[int, int, str]],
) -> LandingField:
    """Return one landing field built from a ``fields`` entry and the layout windows.

    The entry's ``commarea`` block supplies the declaring item and its placement, and
    the item's ``kind`` is taken from the layout windows. A ``commarea`` block naming an
    item the layout does not declare, or recording an offset or length the layout
    contradicts, raises ``FieldMapError``. The entry's ``blank_window_lands_null``
    member is read through ``_blank_window_lands_null``, which checks it against the
    rest of the entry. A member this tool does not read is ignored.
    """
    logical_entry = _member_text(entry, "logical_entry", where)
    group = _member_text(entry, "group", where)
    runtime_status = _member_text(entry, "runtime_status", where)
    populated_by = entry.get("populated_by")
    if populated_by is not None and not isinstance(populated_by, str):
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.populated_by')} as "
            f"{_display(populated_by)}; a string or null is required"
        )
    applicable = _optional_text_sequence(entry, "applicable_policy_types", where)
    evidence = _optional_text_sequence(entry, "evidence", where)
    domain = _optional_text_sequence(entry, "domain", where)
    target_types = _target_types(entry, where)
    commarea = entry.get("commarea")
    lands_null_when_blank = _blank_window_lands_null(
        entry, where, commarea is not None, populated_by
    )
    if commarea is None:
        return LandingField(
            name=landing_name,
            logical_entry=logical_entry,
            group=group,
            runtime_status=runtime_status,
            populated_by=populated_by,
            item=None,
            copybook=None,
            line=None,
            pic=None,
            offset=None,
            length=None,
            kind=None,
            applicable_policy_types=applicable,
            evidence=evidence,
            domain=domain,
            target_types=target_types,
            blank_window_lands_null=lands_null_when_blank,
        )
    commarea_where = f"{where}.commarea"
    item = _member_text(commarea, "item", commarea_where)
    copybook = _member_text(commarea, "copybook", commarea_where)
    line = _member_integer(commarea, "line", commarea_where)
    pic = _member_text(commarea, "pic", commarea_where)
    offset = _member_integer(commarea, "offset", commarea_where)
    length = _member_integer(commarea, "length", commarea_where)
    window = windows.get(item)
    if window is None:
        raise FieldMapError(
            f"the field map records {_shown(f'{commarea_where}.item')} as "
            f"{_shown(item)}, which no 'layout' group declares"
        )
    if (offset, length) != (window[0], window[1]):
        raise FieldMapError(
            f"the field map places {item} at bytes {_window_range(offset, length)} "
            f"under {commarea_where} and at bytes "
            f"{_window_range(window[0], window[1])} under 'layout'"
        )
    return LandingField(
        name=landing_name,
        logical_entry=logical_entry,
        group=group,
        runtime_status=runtime_status,
        populated_by=populated_by,
        item=item,
        copybook=copybook,
        line=line,
        pic=pic,
        offset=offset,
        length=length,
        kind=window[2],
        applicable_policy_types=applicable,
        evidence=evidence,
        domain=domain,
        target_types=target_types,
        blank_window_lands_null=lands_null_when_blank,
    )


def _landing_fields(
    document: Mapping[str, Any], windows: Mapping[str, tuple[int, int, str]]
) -> Mapping[str, LandingField]:
    """Return every ``fields`` entry carrying a landing key, keyed by that key."""
    entries = _member_sequence(document, "fields", "")
    fields: dict[str, LandingField] = {}
    for position, entry in enumerate(entries):
        where = f"fields[{position}]"
        if not isinstance(entry, Mapping):
            raise FieldMapError(
                f"the field map records {_shown(where)} as {_display(entry)}; a "
                "mapping is required"
            )
        if "landing_field" not in entry:
            raise FieldMapError(
                f"the field map is missing {_shown(f'{where}.landing_field')}"
            )
        landing_name = entry["landing_field"]
        if landing_name is None:
            continue
        if not isinstance(landing_name, str) or not landing_name:
            raise FieldMapError(
                f"the field map records {_shown(f'{where}.landing_field')} as "
                f"{_display(landing_name)}; a non-empty string or null is required"
            )
        if landing_name in fields:
            raise FieldMapError(
                f"the field map records landing key {_shown(landing_name)} on two "
                f"entries, the second at {where}"
            )
        fields[landing_name] = _landing_field(entry, where, landing_name, windows)
    if not fields:
        raise FieldMapError("the field map records no landing key under 'fields'")
    return fields


def _reject_excluded_items(
    document: Mapping[str, Any], fields: Mapping[str, LandingField]
) -> None:
    """Raise ``FieldMapError`` when a landing key reads an item recorded as excluded.

    The ``excluded`` section names the in-scope declarations that carry no target
    column, the four commercial peril codes among them. No landing key may be sourced
    from one of those items.
    """
    entries = _member_sequence(document, "excluded", "")
    excluded: set[str] = set()
    for position, entry in enumerate(entries):
        excluded.add(_member_text(entry, "item", f"excluded[{position}]"))
    for name, field in fields.items():
        if field.item is not None and field.item in excluded:
            raise FieldMapError(
                f"the field map sources landing key {_shown(name)} from "
                f"{field.item}, which it also records under 'excluded' as carrying no "
                "target column"
            )


def _routing(document: Mapping[str, Any]) -> tuple[Mapping[str, str], str]:
    """Return the request-id to policy-type table and the unrecognised return code.

    The table is ``request_routing.map``, whose every entry records a single-character
    uppercase ``policy_type``. The second value is
    ``request_routing.unrecognised_request.return_code``.
    """
    routing_section = _member_mapping(document, "request_routing", "")
    entries = _member_mapping(routing_section, "map", "request_routing")
    table: dict[str, str] = {}
    for request_id, entry in entries.items():
        where = f"request_routing.map.{request_id}"
        if not isinstance(request_id, str) or not request_id:
            raise FieldMapError(
                f"the field map records {_display(request_id)} as a key of "
                "'request_routing.map'; a non-empty string is required"
            )
        policy_type = _member_text(entry, "policy_type", where)
        if len(policy_type) != 1 or not policy_type.isupper():
            raise FieldMapError(
                f"the field map records {_shown(f'{where}.policy_type')} as "
                f"{_shown(policy_type)}; one uppercase character is required"
            )
        table[request_id] = policy_type
    if not table:
        raise FieldMapError(
            "the field map records no entry under 'request_routing.map'"
        )
    unrecognised = _member_mapping(
        routing_section, "unrecognised_request", "request_routing"
    )
    return table, _member_text(
        unrecognised, "return_code", "request_routing.unrecognised_request"
    )


def _amount_fields(
    document: Mapping[str, Any], fields: Mapping[str, LandingField]
) -> tuple[str, ...]:
    """Return the amount landing keys, checked against the entries' recorded group.

    The keys are ``comparison.amount_fields``. Each must be a landing key of kind
    ``numeric_display`` recorded under group ``premium_payment``, and every landing key
    of that group must appear among them.
    """
    comparison = _member_mapping(document, "comparison", "")
    names = _text_sequence(comparison, "amount_fields", "comparison")
    for name in names:
        field = fields.get(name)
        if field is None:
            raise FieldMapError(
                f"the field map lists {_shown(name)} under "
                "'comparison.amount_fields' but records no landing key of that name"
            )
        if field.group != GROUP_PREMIUM_PAYMENT:
            raise FieldMapError(
                f"the field map records landing key {_shown(name)} under group "
                f"{_shown(field.group)} and lists it under "
                f"'comparison.amount_fields'; group {_shown(GROUP_PREMIUM_PAYMENT)} "
                "is required"
            )
        if field.kind != KIND_NUMERIC:
            raise FieldMapError(
                f"the field map records amount {_shown(name)} as kind "
                f"{_display(field.kind)}; kind {_shown(KIND_NUMERIC)} is required"
            )
    grouped = {
        name
        for name, field in fields.items()
        if field.group == GROUP_PREMIUM_PAYMENT
    }
    missing = sorted(grouped - set(names))
    if missing:
        raise FieldMapError(
            f"the field map records {_quote_all(missing)} under group "
            f"{_shown(GROUP_PREMIUM_PAYMENT)} without listing them under "
            "'comparison.amount_fields'"
        )
    return names


def _return_code_meanings(
    document: Mapping[str, Any], domain: Sequence[str]
) -> Mapping[str, str]:
    """Return the meaning the ``return_codes`` section records for each code.

    The section keys must be exactly the codes ``domain`` holds, which is the domain the
    ``return_code`` entry records, and each entry must carry a non-empty ``meaning``.
    Those meanings are the observed return convention of the chain: the codes are set at
    base/src/lgapol01.cbl:105,114 and base/src/lgapdb01.cbl:204,211,239,293,296,301 and
    base/src/lgapvs01.cbl:144.

    Raises ``FieldMapError`` when the section is absent, when its keys differ from
    ``domain``, or when an entry records no meaning.
    """
    section = _member_mapping(document, "return_codes", "")
    meanings: dict[str, str] = {}
    for code, entry in section.items():
        if not isinstance(code, str):
            raise FieldMapError(
                f"the field map records {_display(code)} as a key of 'return_codes'; a "
                "string is required"
            )
        meanings[code] = _member_text(entry, "meaning", f"return_codes.{code}")
    absent = sorted(set(domain) - set(meanings))
    extra = sorted(set(meanings) - set(domain))
    if absent or extra:
        raise FieldMapError(
            "the field map's 'return_codes' section does not cover the recorded domain "
            f"of {_shown(LANDING_RETURN_CODE)}: absent {_quote_all(absent) or 'none'}, "
            f"outside the domain {_quote_all(extra) or 'none'}"
        )
    return meanings


def _nullability(
    document: Mapping[str, Any],
    amount_fields: Sequence[str],
    policy_types: Iterable[str],
    fields: Mapping[str, LandingField],
) -> tuple[frozenset[str], Mapping[str, tuple[frozenset[str], frozenset[str]]]]:
    """Return the always-populated amount keys and the per-policy-type split.

    ``product_premium_nullability`` must record every policy type the routing table
    yields, must account for every amount key exactly once per policy type across
    ``always_populated``, ``populated`` and ``null_fields``, must record null as the
    inapplicable value and must refuse zero substitution. The split is checked against
    each amount entry's ``applicable_policy_types`` in both directions.
    """
    section = _member_mapping(document, "product_premium_nullability", "")
    where = "product_premium_nullability"
    if section.get("inapplicable_value") is not None:
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.inapplicable_value')} as "
            f"{_display(section.get('inapplicable_value'))}; null is required"
        )
    if section.get("zero_substitution_permitted") is not False:
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.zero_substitution_permitted')} "
            f"as {_display(section.get('zero_substitution_permitted'))}; false is "
            "required"
        )
    always = frozenset(_text_sequence(section, "always_populated", where))
    unknown = sorted(always - set(amount_fields))
    if unknown:
        raise FieldMapError(
            f"the field map lists {_quote_all(unknown)} under "
            f"{_shown(f'{where}.always_populated')} without listing them as amounts"
        )
    by_type = _member_mapping(section, "by_policy_type", where)
    split: dict[str, tuple[frozenset[str], frozenset[str]]] = {}
    for policy_type in policy_types:
        entry_where = f"{where}.by_policy_type.{policy_type}"
        if policy_type not in by_type:
            raise FieldMapError(f"the field map is missing {_shown(entry_where)}")
        entry = by_type[policy_type]
        populated = frozenset(_optional_text_sequence(entry, "populated", entry_where))
        nulled = frozenset(_optional_text_sequence(entry, "null_fields", entry_where))
        overlap = sorted(populated & nulled)
        if overlap:
            raise FieldMapError(
                f"the field map lists {_quote_all(overlap)} as both populated and null "
                f"under {_shown(entry_where)}"
            )
        accounted = always | populated | nulled
        if accounted != set(amount_fields):
            unaccounted = sorted(set(amount_fields) - accounted)
            foreign = sorted(accounted - set(amount_fields))
            raise FieldMapError(
                f"the field map accounts for {len(accounted)} of the "
                f"{len(amount_fields)} amounts under {_shown(entry_where)}: "
                f"unaccounted {_quote_all(unaccounted) or 'none'}, "
                f"not an amount {_quote_all(foreign) or 'none'}"
            )
        for name in amount_fields:
            applicable = policy_type in fields[name].applicable_policy_types
            populated_here = name in always or name in populated
            if applicable != populated_here:
                raise FieldMapError(
                    f"the field map records amount {_shown(name)} as "
                    f"{'applicable' if applicable else 'inapplicable'} to policy type "
                    f"{_shown(policy_type)} under 'fields' and as "
                    f"{'populated' if populated_here else 'null'} under "
                    f"{_shown(entry_where)}"
                )
        split[policy_type] = (always | populated, nulled)
    return always, split


def load_field_map(path: Path) -> FieldMap:
    """Return the validated field map members this tool reads.

    ``path`` names ``copybook_field_map.yml``. Every offset, length, kind, routing
    entry, landing key, amount key and nullability rule is taken from it; none is
    written into this tool. The document is parsed with a repeated mapping key rejected
    rather than resolved to its last value.

    Raises ``InputOutputError`` when the file cannot be read and ``FieldMapError``
    when it cannot be parsed, is missing a member this tool reads, or contradicts
    itself: a record length other than ``COMMAREA_RECORD_LENGTH``, a landing key
    without either a COMMAREA window or a derived runtime status, a landing order that
    disagrees with the recorded landing keys, a request-routing entry without a
    single-character policy type, an amount outside group ``premium_payment``, a
    nullability split that disagrees with the recorded applicable policy types, a
    landing key sourced from an item the map records under ``excluded``, a
    ``return_codes`` section that does not cover the recorded return-code domain, a
    source-system runtime status other than ``RUNTIME_STATUS_WAREHOUSE_ASSIGNED``, a
    recorded source-system run value other than ``DEFAULT_SOURCE_SYSTEM_KEY``, or a
    date or timestamp landing key whose ``targets`` block does not record the canonical
    type this tool confirms that key's value against.
    """
    content = _read_bounded_bytes(path, MAX_FIELD_MAP_BYTES, "the field map")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise InputOutputError(
            f"the field map is not UTF-8 text: {_path_shown(path)}: {_reason(error)}"
        ) from error
    try:
        document = yaml.load(text, Loader=_DuplicateRejectingLoader)
    except yaml.YAMLError as error:
        raise FieldMapError(
            f"the field map cannot be parsed: {_path_shown(path)}: {_reason(error)}"
        ) from error
    if not isinstance(document, Mapping):
        raise FieldMapError(
            f"the field map is {_display(document)}: {_path_shown(path)}; a mapping is "
            "required"
        )

    record_length = _member_integer(
        _member_mapping(document, "record", ""), "length", "record"
    )
    if record_length != COMMAREA_RECORD_LENGTH:
        raise FieldMapError(
            f"the field map records 'record.length' as {record_length}; "
            f"{COMMAREA_RECORD_LENGTH} is required"
        )

    landing = _member_mapping(document, "landing", "")
    field_order = _text_sequence(landing, "field_order", "landing")
    repeated = sorted({name for name in field_order if field_order.count(name) > 1})
    if repeated:
        raise FieldMapError(
            f"the field map repeats {_quote_all(repeated)} in 'landing.field_order'"
        )

    windows = _layout_windows(document, record_length)
    fields = _landing_fields(document, windows)
    _reject_excluded_items(document, fields)
    routing, unrecognised_return_code = _routing(document)
    amount_fields = _amount_fields(document, fields)
    for name in amount_fields:
        if fields[name].blank_window_lands_null:
            raise FieldMapError(
                f"the field map records landing key {_shown(name)} as an amount of "
                f"group {_shown(GROUP_PREMIUM_PAYMENT)} and records "
                "'blank_window_lands_null' as true for it; an amount the derived "
                "policy type applies to carries the digits the record holds, and its "
                "blank window is refused rather than landed"
            )
    always_populated, nullability = _nullability(
        document, amount_fields, sorted(set(routing.values())), fields
    )

    key_section = _member_mapping(document, LANDING_SOURCE_SYSTEM_KEY, "")
    source_system_key_field = _member_text(
        key_section, "landing_field", LANDING_SOURCE_SYSTEM_KEY
    )
    source_system_key_run_value = _member_text(
        key_section, "run_value", LANDING_SOURCE_SYSTEM_KEY
    )
    key_runtime_status = _member_text(
        key_section, "runtime_status", LANDING_SOURCE_SYSTEM_KEY
    )
    if key_runtime_status != RUNTIME_STATUS_WAREHOUSE_ASSIGNED:
        raise FieldMapError(
            f"the field map records "
            f"{_shown(f'{LANDING_SOURCE_SYSTEM_KEY}.runtime_status')} as "
            f"{_shown(key_runtime_status)}; "
            f"{_shown(RUNTIME_STATUS_WAREHOUSE_ASSIGNED)} is required"
        )
    if source_system_key_run_value != DEFAULT_SOURCE_SYSTEM_KEY:
        raise FieldMapError(
            f"the field map records "
            f"{_shown(f'{LANDING_SOURCE_SYSTEM_KEY}.run_value')} as "
            f"{_shown(source_system_key_run_value)}; "
            f"{_shown(DEFAULT_SOURCE_SYSTEM_KEY)} is required"
        )

    expected_order = {source_system_key_field, *fields}
    if set(field_order) != expected_order:
        absent = sorted(expected_order - set(field_order))
        extra = sorted(set(field_order) - expected_order)
        raise FieldMapError(
            "the field map's 'landing.field_order' does not match its recorded landing "
            f"keys: absent {_quote_all(absent) or 'none'}, unrecorded "
            f"{_quote_all(extra) or 'none'}"
        )

    for name in (
        LANDING_REQUEST_ID,
        LANDING_RETURN_CODE,
        LANDING_POLICY_TYPE,
        LANDING_POLICY_NUMBER,
        LANDING_LAST_CHANGED,
        *CALENDAR_DATE_FIELDS,
    ):
        if name not in fields:
            raise FieldMapError(
                f"the field map records no landing key {_shown(name)} under 'fields'"
            )
    for name, field in fields.items():
        if not field.is_read_from_record and field.runtime_status != (
            RUNTIME_STATUS_DERIVED
        ):
            raise FieldMapError(
                f"the field map records landing key {_shown(name)} without a "
                f"'commarea' block and with runtime status "
                f"{_shown(field.runtime_status)}; "
                f"{_shown(RUNTIME_STATUS_DERIVED)} is required to omit the block"
            )
    if fields[LANDING_POLICY_TYPE].is_read_from_record:
        raise FieldMapError(
            f"the field map places landing key {_shown(LANDING_POLICY_TYPE)} at bytes "
            f"{_window_range(*windows[str(fields[LANDING_POLICY_TYPE].item)][:2])}; it "
            "is derived from the request id and is not read from the record"
        )
    if fields[LANDING_REQUEST_ID].kind != KIND_ALPHANUMERIC:
        raise FieldMapError(
            f"the field map records landing key {_shown(LANDING_REQUEST_ID)} as kind "
            f"{_display(fields[LANDING_REQUEST_ID].kind)}; kind "
            f"{_shown(KIND_ALPHANUMERIC)} is required"
        )
    return_code_field = fields[LANDING_RETURN_CODE]
    if return_code_field.kind != KIND_NUMERIC:
        raise FieldMapError(
            f"the field map records landing key {_shown(LANDING_RETURN_CODE)} as kind "
            f"{_display(return_code_field.kind)}; kind {_shown(KIND_NUMERIC)} is "
            "required"
        )
    domain = return_code_field.domain
    if not domain:
        raise FieldMapError(
            f"the field map records no 'domain' for landing key "
            f"{_shown(LANDING_RETURN_CODE)}"
        )
    expected_width = return_code_field.length
    for code in domain:
        if len(code) != expected_width or not _ASCII_DIGITS.fullmatch(code):
            raise FieldMapError(
                f"the field map records {_shown(code)} in the domain of "
                f"{_shown(LANDING_RETURN_CODE)}; {expected_width} digits are required"
            )
    for code in LANDABLE_RETURN_CODES:
        if code not in domain:
            raise FieldMapError(
                f"the field map's domain for {_shown(LANDING_RETURN_CODE)} omits "
                f"{_shown(code)}, which is one of the codes a record is landed under "
                f"({_quote_all(LANDABLE_RETURN_CODES)})"
            )
    for code in domain:
        if code not in LANDABLE_RETURN_CODES and code not in RETURN_CODE_STAGES:
            raise FieldMapError(
                f"the field map records {_shown(code)} in the domain of "
                f"{_shown(LANDING_RETURN_CODE)}; this tool records neither a landing "
                f"stage for it nor the stage it stops at, and lands only "
                f"{_quote_all(LANDABLE_RETURN_CODES)}"
            )
    return_code_meanings = _return_code_meanings(document, domain)

    date_fields = frozenset(
        name
        for name, field in fields.items()
        if CANONICAL_TYPE_DATE in field.target_types
    )
    timestamp_fields = frozenset(
        name
        for name, field in fields.items()
        if CANONICAL_TYPE_TIMESTAMP in field.target_types
    )
    for name, recorded, required_type in (
        (LANDING_ISSUE_DATE, date_fields, CANONICAL_TYPE_DATE),
        (LANDING_EXPIRY_DATE, date_fields, CANONICAL_TYPE_DATE),
        (LANDING_LAST_CHANGED, timestamp_fields, CANONICAL_TYPE_TIMESTAMP),
    ):
        if name not in recorded:
            raise FieldMapError(
                f"the field map records landing key {_shown(name)} with the canonical "
                f"target types {_quote_all(fields[name].target_types) or 'none'}; a "
                f"target of type {_shown(required_type)} is required, because this "
                "tool confirms the calendar and clock values of that key before "
                "writing them"
            )

    return FieldMap(
        path=path,
        record_length=record_length,
        field_order=field_order,
        fields=fields,
        routing=routing,
        amount_fields=amount_fields,
        always_populated=always_populated,
        nullability=nullability,
        return_code_domain=domain,
        return_code_meanings=return_code_meanings,
        source_system_key_field=source_system_key_field,
        source_system_key_run_value=source_system_key_run_value,
        chain_populated=frozenset(
            name
            for name, field in fields.items()
            if field.populated_by == POPULATED_BY_CHAIN
        ),
        unrecognised_request_return_code=unrecognised_return_code,
        date_fields=date_fields,
        timestamp_fields=timestamp_fields,
    )


# ---------------------------------------------------------------------------
# Decoding
# ---------------------------------------------------------------------------


def slice_field(record: str, offset: int, length: int) -> str:
    """Return the window ``record`` holds at 1-based inclusive ``offset``.

    The window is ``record[offset - 1 : offset - 1 + length]``. Raises
    ``FieldMapError`` for an offset or length below one and ``RecordError`` when the
    window reaches past the end of ``record``.
    """
    if offset < 1 or length < 1:
        raise FieldMapError(
            f"a window at offset {offset} of length {length} is not addressable; both "
            "must be at least 1"
        )
    start = offset - 1
    end = start + length
    if end > len(record):
        raise RecordError(
            f"a window at bytes {_window_range(offset, length)} reaches past the "
            f"{len(record)}-character record"
        )
    return record[start:end]


def decode_alphanumeric(field: LandingField, window: str) -> str | None:
    """Return ``window`` without leading or trailing spaces, or None when it is blank.

    A window holding only spaces decodes to None, which lands as JSON null rather than
    as an empty string. A window carrying a control character - one of the C0 range, DEL
    or one of the C1 range - is refused, so no landed value carries a character the
    loaders reading the record cannot represent as text.

    Raises ``RecordError`` naming the landing key, the item, its byte range, how many
    control characters the window holds and where they sit; the window content itself is
    reported only when record values are shown.
    """
    if _CONTROL_CHARACTERS.search(window):
        raise RecordError(
            f"{field.described} holds {_value(window)}, which carries a control "
            f"character; landing key {_shown(field.name)} lands printable text alone; "
            f"{_control_character_report(window)}"
        )
    trimmed = window.strip(" ")
    return trimmed or None


def decode_numeric_display(field: LandingField, window: str) -> str:
    """Return the digits of ``window`` with leading zeros stripped.

    ``window`` must hold digits only; all zeros decode to ``'0'`` so at least one digit
    is always carried. Raises ``RecordError`` naming the item, its byte range, how many
    characters lie outside 0-9 and where they sit in the window when the window holds
    anything else; the window content itself is reported only when record values are
    shown. No arithmetic is applied: the returned text holds the digits the record
    carries.
    """
    if not _ASCII_DIGITS.fullmatch(window):
        raise RecordError(
            f"{field.described} holds {_value(window)}, which is not all digits; "
            f"{_non_digit_report(window)}"
        )
    return window.lstrip("0") or "0"


def decode_window(field: LandingField, record: str) -> str | None:
    """Return one landing value decoded from the record by the field's recorded kind.

    A field the map records ``blank_window_lands_null`` for returns None when its window
    holds only spaces, whatever its kind, so an optional value the request left blank
    lands as JSON null instead of reaching the check of its kind. Every other window is
    decoded by its kind, under which a blank numeric window is refused.

    Raises ``FieldMapError`` when the field carries no window or records a kind this
    tool does not decode, and ``RecordError`` when the window content breaches the
    kind.
    """
    if not field.is_read_from_record:
        raise FieldMapError(
            f"the field map records no 'commarea' block for landing key "
            f"{_shown(field.name)}, so it cannot be decoded from the record"
        )
    assert field.offset is not None and field.length is not None
    window = slice_field(record, field.offset, field.length)
    if field.blank_window_lands_null and not window.strip(" "):
        return None
    if field.kind == KIND_ALPHANUMERIC:
        return decode_alphanumeric(field, window)
    if field.kind == KIND_NUMERIC:
        return decode_numeric_display(field, window)
    raise FieldMapError(
        f"the field map records landing key {_shown(field.name)} as kind "
        f"{_display(field.kind)}; one of {_quote_all(KNOWN_KINDS)} is required"
    )


def decode_return_code(field: LandingField, record: str) -> str:
    """Return the returned ``CA-RETURN-CODE`` as a zero-padded string of its own width.

    The window is carried verbatim: a leading zero is never stripped and the value is
    never converted to an integer. Raises ``RecordError`` when the window is not all
    digits or holds a value outside the domain the field map records. A digit pair
    outside the domain is named, being the status the chain reported; a window that is
    not a digit pair is reported by its character count unless record values are shown.
    """
    assert field.offset is not None and field.length is not None
    window = slice_field(record, field.offset, field.length)
    if not _ASCII_DIGITS.fullmatch(window):
        raise RecordError(
            f"{field.described} holds {_value(window)}, which is not all digits; the "
            f"chain writes one of {_quote_all(field.domain)} there"
        )
    if window not in field.domain:
        raise RecordError(
            f"{field.described} holds {_shown(window)}, which is outside the recorded "
            f"domain {_quote_all(field.domain)}"
        )
    return window


# ---------------------------------------------------------------------------
# Derivation and normalisation
# ---------------------------------------------------------------------------


def derive_policy_type(request_id: str, field_map: FieldMap) -> str:
    """Return the one-character policy type the field map routes ``request_id`` to.

    The routing table is ``request_routing.map`` in the field map, which records the
    request-id to policy-type assignments of the EVALUATE at
    base/src/lgapdb01.cbl:184-207. ``request_id`` is the trimmed ``CA-REQUEST-ID``
    value.

    No default letter is substituted and no other source is consulted: an id the
    table holds no entry for is refused, since the chain sets return code
    ``unrecognised_request_return_code`` at base/src/lgapdb01.cbl:204 for one and only a
    successful execution is landed.

    Raises ``RecordError`` naming the accepted request ids when the table holds no entry
    for ``request_id``.
    """
    policy_type = field_map.routing.get(request_id)
    if policy_type is None:
        raise RecordError(
            f"the record carries request id {_shown(request_id)}, which the field "
            "map's request routing does not recognise; the routed request ids are "
            f"{_quote_all(sorted(field_map.routing))}, and the chain returns "
            f"{_shown(field_map.unrecognised_request_return_code)} for any other"
        )
    return policy_type


def _refuse_component(
    field: LandingField, raw: str, what: str, value: int, bounds: tuple[int, int]
) -> NoReturn:
    """Raise ``RecordError`` for a date or clock component outside its range."""
    low, high = bounds
    raise RecordError(
        f"{field.described} holds {_value(raw)}, whose {what} is {value:02d}; "
        f"{low:02d} to {high:02d} is the accepted range"
    )


def _checked_calendar_day(
    field: LandingField, raw: str, year: int, month: int, day: int
) -> datetime.date:
    """Return the calendar date ``year``, ``month`` and ``day`` name.

    The month and day are first checked against their own ranges, then the three
    components are built into a date, which refuses a day the month does not hold: the
    30th of February, and the 29th of a February outside a leap year.

    Raises ``RecordError`` naming the item, its byte range, the raw characters and the
    component at fault.
    """
    if not _MONTH_RANGE[0] <= month <= _MONTH_RANGE[1]:
        _refuse_component(field, raw, "month", month, _MONTH_RANGE)
    if not _DAY_RANGE[0] <= day <= _DAY_RANGE[1]:
        _refuse_component(field, raw, "day", day, _DAY_RANGE)
    try:
        return datetime.date(year, month, day)
    except ValueError as error:
        raise RecordError(
            f"{field.described} holds {_value(raw)}, which names day {day:02d} of "
            f"month {month:02d} in {year:04d}: {_reason(error)}"
        ) from error


def validate_calendar_date(value: str | None, field: LandingField) -> str | None:
    """Return ``value`` once it is confirmed to be a real calendar date, or None.

    ``value`` is the trimmed window of a landed date item, being ``CA-ISSUE-DATE`` or
    ``CA-EXPIRY-DATE`` at base/src/lgcmarea.cpy:38-39, or None when that window holds
    only spaces. A value must be written ``CALENDAR_DATE_FORM`` and must name a day the
    month holds in that year, so an impossible date reaches this refusal rather than the
    warehouse cast that would otherwise be the first check of it.

    Raises ``RecordError`` naming the item, its byte range and the raw characters when
    the value is not written in that form or is not a real date.
    """
    if value is None:
        return None
    matched = _CALENDAR_DATE_SHAPE.fullmatch(value)
    if matched is None:
        raise RecordError(
            f"{field.described} holds {_value(value)}, which is not written "
            f"{CALENDAR_DATE_FORM}"
        )
    year, month, day = (int(part) for part in matched.groups())
    _checked_calendar_day(field, value, year, month, day)
    return value


def normalise_timestamp(raw: str, field: LandingField) -> str:
    """Return ``raw`` as an ISO-8601 timestamp with microsecond precision.

    ``raw`` is the trimmed ``CA-LASTCHANGED`` value the chain read back from the POLICY
    row at base/src/lgapdb01.cbl:315-321. Every shape listed in
    ``TIMESTAMP_INPUT_FORMATS`` is accepted, in that order: the Db2 character form
    ``YYYY-MM-DD-HH.MM.SS.ffffff`` and the ISO forms using a ``T`` or a space separator
    with colons in the time part, each with a fractional-second part of one to six
    digits or without one. A matched shape is then validated as a real date and clock
    time, so an impossible month, day, hour, minute or second is refused here rather
    than at the warehouse cast. The result is emitted as
    ``YYYY-MM-DDTHH:MM:SS.ffffff``; a fractional part shorter than
    ``TIMESTAMP_FRACTION_DIGITS`` digits is carried at microsecond precision and no
    value is truncated or rounded.

    Raises ``RecordError`` naming the item, its byte range, the accepted forms and the
    character count of the rejected value when no accepted form matches, when a
    component is outside its range, when the day is not a day of that month, or when
    ``raw`` is empty; the rejected characters themselves are reported only when record
    values are shown. The current wall-clock time is never substituted.
    """
    if not raw:
        raise RecordError(
            f"{field.described} holds no timestamp; the chain reads one back into it "
            f"from the POLICY row "
            f"({_quote_all(field.evidence) or 'no locator recorded'})"
        )
    for shape in _TIMESTAMP_SHAPES:
        matched = shape.fullmatch(raw)
        if matched is None:
            continue
        year, month, day, hour, minute, second = (
            int(part) for part in matched.groups()[:6]
        )
        fraction = matched.group(7) or ""
        if not _HOUR_RANGE[0] <= hour <= _HOUR_RANGE[1]:
            _refuse_component(field, raw, "hour", hour, _HOUR_RANGE)
        if not _MINUTE_RANGE[0] <= minute <= _MINUTE_RANGE[1]:
            _refuse_component(field, raw, "minute", minute, _MINUTE_RANGE)
        if not _SECOND_RANGE[0] <= second <= _SECOND_RANGE[1]:
            _refuse_component(field, raw, "second", second, _SECOND_RANGE)
        date = _checked_calendar_day(field, raw, year, month, day)
        moment = datetime.datetime(
            date.year,
            date.month,
            date.day,
            hour,
            minute,
            second,
            int(fraction.ljust(TIMESTAMP_FRACTION_DIGITS, "0")),
        )
        return moment.isoformat(
            sep=TIMESTAMP_OUTPUT_SEPARATOR, timespec=TIMESTAMP_OUTPUT_PRECISION
        )
    raise RecordError(
        f"{field.described} holds {_value(raw)}, which matches none of the accepted "
        f"timestamp forms {_quote_all(TIMESTAMP_INPUT_FORMATS)}, each accepting a "
        f"fractional-second part of 1 to {TIMESTAMP_FRACTION_DIGITS} digits or none"
    )


def amount_applies(name: str, policy_type: str | None, field_map: FieldMap) -> bool:
    """Return True when the field map populates amount ``name`` for ``policy_type``.

    The answer is read from ``product_premium_nullability``: the amount keys the map
    records as always populated together with those it lists as populated for this
    policy type. ``load_field_map`` has already confirmed that this split agrees with
    each amount entry's ``applicable_policy_types`` in both directions. A None
    ``policy_type`` selects no product overlay, and only the map's always-populated
    amounts apply.

    A ``policy_type`` of None is the record the routing selected no product for, which
    is the path that sets return code 99. No product overlay is selected there, so only
    the amounts the map records as always populated apply; those sit in the fixed policy
    header rather than in an overlay. Every product premium returns False.

    Raises ``FieldMapError`` when the map records no split for a named ``policy_type``
    or when ``name`` is not one of its amount keys.
    """
    if name not in field_map.amount_fields:
        raise FieldMapError(
            f"landing key {_shown(name)} is not one of the field map's amounts "
            f"{_quote_all(field_map.amount_fields)}"
        )
    if policy_type is None:
        return name in field_map.always_populated
    split = field_map.nullability.get(policy_type)
    if split is None:
        raise FieldMapError(
            f"the field map records no product premium nullability for policy type "
            f"{_shown(policy_type)}; it records "
            f"{_quote_all(sorted(field_map.nullability))}"
        )
    return name in split[0]


def decode_amount(
    field: LandingField, record: str, policy_type: str | None, field_map: FieldMap
) -> str | None:
    """Return one amount as the digits the record carries, or None when inapplicable.

    An amount the field map does not populate for ``policy_type`` returns None, and its
    window is not read. The product overlays redefine the same bytes, and the window of
    an unselected overlay holds the selected overlay's content. An applicable window is
    validated as all digits and returned with leading zeros stripped. No arithmetic is
    applied: no scaling, rounding, defaulting or unit conversion touches the value.
    A ``policy_type`` of None selects no overlay, so every product premium returns None.

    Raises ``RecordError`` naming the item and its byte range when an applicable window
    is not all digits.
    """
    if not amount_applies(field.name, policy_type, field_map):
        return None
    assert field.offset is not None and field.length is not None
    return decode_numeric_display(
        field, slice_field(record, field.offset, field.length)
    )


# ---------------------------------------------------------------------------
# Landing record
# ---------------------------------------------------------------------------


def _decode_chain_populated(field: LandingField, record: str) -> str | None:
    """Return one chain-assigned value, or None when the chain never assigned it.

    A window holding only spaces returns None whatever the field's kind, so an
    unassigned value reaches ``_require_assigned`` as absent and is reported as the
    unassigned value it is rather than as a numeric decoding failure. A window holding
    content is decoded by the field's recorded kind, under which an alphanumeric window
    carrying a control character and a numeric window carrying a non-digit are refused.
    """
    assert field.offset is not None and field.length is not None
    window = slice_field(record, field.offset, field.length)
    if not window.strip(" "):
        return None
    if field.kind == KIND_ALPHANUMERIC:
        return decode_alphanumeric(field, window)
    return decode_numeric_display(field, window)


def _require_assigned(field: LandingField, value: str | None) -> str:
    """Return ``value``, raising ``RecordError`` when the chain left it unassigned.

    An absent value and a numeric value of only zeros both raise, and the diagnostic
    names the item, its byte range and every locator the field map cites for the field.
    Every landed record carries return code ``RETURN_CODE_SUCCESS``, so this applies to
    each of them.
    """
    locators = _quote_all(field.evidence) or "no locator recorded"
    if value is None:
        raise RecordError(
            f"{field.described} is blank; the chain assigns it on every execution "
            f"returning {_shown(RETURN_CODE_SUCCESS)}, per {locators}"
        )
    if field.kind == KIND_NUMERIC and value == "0":
        raise RecordError(
            f"{field.described} holds only zeros; the chain assigns a non-zero value "
            f"on every execution returning {_shown(RETURN_CODE_SUCCESS)}, per "
            f"{locators}"
        )
    return value


def refuse_unsuccessful_return_code(return_code: str, field_map: FieldMap) -> None:
    """Refuse a capture whose returned ``CA-RETURN-CODE`` is not ``00``.

    ``return_code`` is the code ``decode_return_code`` read, already confirmed to be one
    of the domain the field map records. The landing and raw contracts carry successful
    extractions only, so a record carrying any other recorded code has nothing to land:
    the diagnostic names the code, the meaning the map's ``return_codes`` section
    records for it and the code that is landed.

    Raises ``ChainNotSuccessfulError``, whose status is distinct from the one a breached
    record contract returns.
    """
    if return_code == RETURN_CODE_SUCCESS:
        return
    meaning = field_map.return_code_meanings.get(return_code, "no meaning recorded")
    raise ChainNotSuccessfulError(
        f"{field_map.fields[LANDING_RETURN_CODE].described} holds "
        f"{_shown(return_code)}, recorded as {_shown(meaning)}; the chain did not "
        f"complete the policy issue and only {_shown(RETURN_CODE_SUCCESS)} is landed"
    )


def build_landing_record(
    record: str,
    field_map: FieldMap,
    source_system_key: str,
) -> dict[str, str | None]:
    """Return the landing record decoded from one successful post-chain COMMAREA record.

    ``record`` is the fixed-width record ``read_commarea`` returned, ``field_map`` the
    validated map and ``source_system_key`` the discriminator to write. The returned
    mapping holds the field map's ``landing.field_order`` keys, in that order, and
    every value is a string or None. Only a record whose returned ``CA-RETURN-CODE`` is
    ``RETURN_CODE_SUCCESS`` yields a landing record; every value the chain assigns is
    then confirmed to be assigned, both dates are confirmed to be real calendar dates
    and the returned timestamp is normalised.

    Raises ``ChainNotSuccessfulError`` when the return code is a recorded code other
    than ``RETURN_CODE_SUCCESS``. Raises ``RecordError`` when the request id is not
    routed, when the return code is outside the recorded domain, when an applicable
    amount window is not all digits, when a landed date is not a real calendar date,
    when the returned timestamp cannot be normalised, or when a value the chain assigns
    is unassigned. Raises ``FieldMapError`` when the assembled keys do not match
    ``landing.field_order`` or a value is not a string or None.
    """
    request_id = decode_window(field_map.fields[LANDING_REQUEST_ID], record)
    if request_id is None:
        raise RecordError(
            f"{field_map.fields[LANDING_REQUEST_ID].described} is blank; the chain "
            "routes on it"
        )
    return_code = decode_return_code(field_map.fields[LANDING_RETURN_CODE], record)
    refuse_unsuccessful_return_code(return_code, field_map)
    policy_type = derive_policy_type(request_id, field_map)

    values: dict[str, str | None] = {}
    for name in field_map.field_order:
        if name == field_map.source_system_key_field:
            values[name] = source_system_key
            continue
        field = field_map.fields[name]
        if name == LANDING_REQUEST_ID:
            values[name] = request_id
        elif name == LANDING_RETURN_CODE:
            values[name] = return_code
        elif name == LANDING_POLICY_TYPE:
            values[name] = policy_type
        elif name in field_map.amount_fields:
            values[name] = decode_amount(field, record, policy_type, field_map)
        elif name in field_map.chain_populated:
            decoded = _decode_chain_populated(field, record)
            if name == LANDING_LAST_CHANGED and decoded is not None:
                decoded = normalise_timestamp(decoded, field)
            values[name] = decoded
        else:
            decoded = decode_window(field, record)
            if name in field_map.date_fields:
                decoded = validate_calendar_date(decoded, field)
            values[name] = decoded

    # Every record reaching this point carries RETURN_CODE_SUCCESS. Every value the
    # chain assigns is required on it.
    for name in field_map.field_order:
        if name == LANDING_RETURN_CODE or name not in field_map.chain_populated:
            continue
        _require_assigned(field_map.fields[name], values[name])

    if tuple(values) != field_map.field_order:
        absent = sorted(set(field_map.field_order) - set(values))
        extra = sorted(set(values) - set(field_map.field_order))
        raise FieldMapError(
            "the assembled landing record does not carry the field map's landing "
            f"keys in order: absent {_quote_all(absent) or 'none'}, unexpected "
            f"{_quote_all(extra) or 'none'}"
        )
    for name, value in values.items():
        if value is not None and not isinstance(value, str):
            raise FieldMapError(
                f"the assembled landing record carries a {_type_name(value)} for "
                f"{_shown(name)}; a string or null is required"
            )
    return values


def serialise_record(
    record: Mapping[str, str | None], field_order: Sequence[str]
) -> str:
    """Return the landing record as one JSON line terminated by one line feed.

    The keys are emitted in the order ``record`` carries them, which must be exactly
    ``field_order``. Text is escaped to ASCII and no key is re-sorted. The emitted order
    is the field map's landing order.

    Raises ``FieldMapError`` when the keys do not match ``field_order`` or a value is
    not a string or None.
    """
    if tuple(record) != tuple(field_order):
        raise FieldMapError(
            "the landing record does not carry the field map's landing keys in order: "
            f"expected {_quote_all(field_order)}, carried {_quote_all(record)}"
        )
    for name, value in record.items():
        if value is not None and not isinstance(value, str):
            raise FieldMapError(
                f"the landing record carries a {_type_name(value)} for "
                f"{_shown(name)}; a string or null is required"
            )
    return json.dumps(dict(record), ensure_ascii=True) + "\n"


def _stands_inside(path: Path, root: Path) -> bool:
    """Return True when ``path`` is ``root`` itself or stands below it."""
    return path == root or root in path.parents


def _canonical_generated_roots() -> tuple[Path, ...]:
    """Return the generated output roots as canonical paths under the repository.

    Each root is resolved so a symbolic-link component of the repository checkout is
    compared in the same form a canonicalised destination carries. A root that does not
    exist yet resolves to the pathname itself, which is the form a destination below it
    canonicalises to.
    """
    return tuple(
        Path(os.path.realpath(REPOSITORY_ROOT / relative))
        for relative in GENERATED_OUTPUT_ROOTS
    )


def confine_destination(destination: Path, *, overwrite: bool = False) -> Path:
    """Return the canonical path ``destination`` names, or refuse it.

    Every component of the destination's parent chain is resolved, so a symbolic-link
    chain, a ``..`` component and a ``/proc/self/cwd`` style alias all reach this check
    in the form of the path they actually name; the components that do not exist yet
    cannot be links and are carried as spelled. The repository directory is taken from
    this file's own location, never from the working directory.

    A canonical destination inside that repository is accepted only below one of
    ``GENERATED_OUTPUT_ROOTS``: every other path inside it holds an authored artifact or
    committed evidence, modernization/validation/artifacts among them, and anything
    below ``READ_ONLY_SOURCE_ROOT`` is refused by that name. A canonical destination
    outside the repository is accepted, which is the documented workflow of landing into
    a temporary directory. A destination whose final component is a symbolic link, and
    one that resolves onto an existing entry that is not a regular file, are refused.

    A destination that resolves onto an existing regular file is refused unless
    ``overwrite`` is true, wherever it stands: a run that names an occupied path
    replaces nothing until the command line asks for it through ``OVERWRITE_OPTION``.
    The containment checks above run first, so a path inside the repository is refused
    by name whether or not ``overwrite`` was given.

    Raises ``InputOutputError`` naming the destination, the canonical form it resolves
    to and the roots that are accepted.
    """
    absolute = Path(os.path.abspath(destination))
    if not absolute.name:
        raise InputOutputError(
            f"the destination names no file: {_path_shown(destination)}"
        )
    if os.path.islink(absolute):
        raise InputOutputError(
            f"the destination is a symbolic link: {_path_shown(destination)}"
        )
    canonical = Path(os.path.realpath(absolute.parent)) / absolute.name
    repository = Path(os.path.realpath(REPOSITORY_ROOT))
    read_only = Path(os.path.realpath(READ_ONLY_SOURCE_ROOT))
    if _stands_inside(canonical, read_only):
        raise InputOutputError(
            f"the destination resolves inside the read-only source directory "
            f"{_path_shown(read_only)}: {_path_shown(destination)} resolves to "
            f"{_path_shown(canonical)}"
        )
    if _stands_inside(canonical, repository):
        roots = _canonical_generated_roots()
        if not any(root in canonical.parents for root in roots):
            raise InputOutputError(
                f"the destination resolves inside the repository directory "
                f"{_path_shown(repository)} and outside every generated root "
                f"{_quote_all(str(root) for root in GENERATED_OUTPUT_ROOTS)}: "
                f"{_path_shown(destination)} resolves to {_path_shown(canonical)}"
            )
    try:
        status = os.lstat(canonical)
    except FileNotFoundError:
        return canonical
    except OSError as error:
        raise InputOutputError(
            f"the destination cannot be examined: {_path_shown(canonical)}: "
            f"{_reason(error)}"
        ) from error
    if not stat.S_ISREG(status.st_mode):
        raise InputOutputError(
            f"the destination exists and is not a regular file: "
            f"{_path_shown(canonical)}"
        )
    if not overwrite:
        raise InputOutputError(
            f"the destination exists and is left in place: {_path_shown(canonical)}; "
            f"{OVERWRITE_OPTION} replaces an existing regular file"
        )
    return canonical


def _create_destination_directory(directory: Path) -> None:
    """Create ``directory`` and every missing directory above it, mode DIRECTORY_MODE.

    ``directory`` is the canonical parent of an accepted destination, so no component
    that already exists is a symbolic link. Each missing component is created one at a
    time and its mode is then set on the created directory itself through a descriptor
    opened without following a link, which leaves the mode at ``DIRECTORY_MODE``
    whatever the ambient umask requested. A directory that already exists keeps the mode
    it carries. Once every component exists, the canonical form of ``directory`` is
    confirmed to be unchanged, so a component replaced while it was being created is
    refused instead of written through.

    Raises ``InputOutputError`` when a directory cannot be created, when its mode cannot
    be set, or when the canonical form changed.
    """
    missing: list[Path] = []
    probe = directory
    while not probe.exists():
        missing.append(probe)
        if probe.parent == probe:
            break
        probe = probe.parent
    for path in reversed(missing):
        try:
            os.mkdir(path, DIRECTORY_MODE)
        except FileExistsError:
            continue
        except OSError as error:
            raise InputOutputError(
                f"the destination directory cannot be created: {_path_shown(path)}: "
                f"{_reason(error)}"
            ) from error
        try:
            descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as error:
            raise InputOutputError(
                f"the created destination directory cannot be opened to set its mode: "
                f"{_path_shown(path)}: {_reason(error)}"
            ) from error
        try:
            os.fchmod(descriptor, DIRECTORY_MODE)
        except OSError as error:
            raise InputOutputError(
                f"the mode of the created destination directory cannot be set to "
                f"{DIRECTORY_MODE:04o}: {_path_shown(path)}: {_reason(error)}"
            ) from error
        finally:
            os.close(descriptor)
    if not directory.is_dir():
        raise InputOutputError(
            f"the destination directory is not a directory: {_path_shown(directory)}"
        )
    settled = Path(os.path.realpath(directory))
    if settled != directory:
        raise InputOutputError(
            f"the destination directory {_path_shown(directory)} now resolves to "
            f"{_path_shown(settled)}; it was replaced while it was being created"
        )


def _descriptor_path(descriptor: int) -> str | None:
    """Return the path the kernel reports for ``descriptor``, or None when unavailable.

    The path is read from /proc/self/fd, so it names the directory the descriptor
    holds without walking the destination path a second time. None is returned on a
    system that publishes no such entry.
    """
    try:
        return os.readlink(f"/proc/self/fd/{descriptor}")
    except OSError:
        return None


def _refuse_read_only_directory(descriptor: int, directory: Path) -> None:
    """Raise ``InputOutputError`` when the held directory is base/ or lies inside it.

    The directory is identified by ``descriptor`` alone: its device and inode numbers
    are compared with those of ``READ_ONLY_SOURCE_ROOT`` and the check then ascends
    through ``..`` descriptors, comparing every ancestor the same way, so a path
    component replaced after the destination was resolved cannot place the write inside
    the read-only source directory. The ascent stops at the filesystem root, where
    ``..`` is the directory itself, and after ``MAX_CONTAINMENT_ASCENT`` levels. A
    ``READ_ONLY_SOURCE_ROOT`` that cannot be examined holds no file to protect and
    passes.
    """
    try:
        protected = os.stat(READ_ONLY_SOURCE_ROOT)
    except OSError:
        return
    protected_identity = (protected.st_dev, protected.st_ino)
    reported = _descriptor_path(descriptor)
    shown = _path_shown(reported if reported is not None else directory)
    try:
        current = os.open(".", os.O_RDONLY | os.O_DIRECTORY, dir_fd=descriptor)
    except OSError as error:
        raise InputOutputError(
            f"the destination directory cannot be examined: {shown}: {_reason(error)}"
        ) from error
    try:
        for _ in range(MAX_CONTAINMENT_ASCENT):
            try:
                info = os.stat(current)
            except OSError as error:
                raise InputOutputError(
                    f"the destination directory cannot be confirmed to lie outside "
                    f"{_path_shown(READ_ONLY_SOURCE_ROOT)}: {shown}: {_reason(error)}"
                ) from error
            if (info.st_dev, info.st_ino) == protected_identity:
                raise InputOutputError(
                    f"the destination directory lies inside the read-only source "
                    f"directory {_path_shown(READ_ONLY_SOURCE_ROOT)}: {shown}"
                )
            try:
                parent = os.open("..", os.O_RDONLY | os.O_DIRECTORY, dir_fd=current)
            except OSError as error:
                raise InputOutputError(
                    f"the destination directory cannot be confirmed to lie outside "
                    f"{_path_shown(READ_ONLY_SOURCE_ROOT)}: {shown}: {_reason(error)}"
                ) from error
            try:
                parent_info = os.stat(parent)
            except OSError as error:
                os.close(parent)
                raise InputOutputError(
                    f"the destination directory cannot be confirmed to lie outside "
                    f"{_path_shown(READ_ONLY_SOURCE_ROOT)}: {shown}: {_reason(error)}"
                ) from error
            reached_root = (parent_info.st_dev, parent_info.st_ino) == (
                info.st_dev,
                info.st_ino,
            )
            os.close(current)
            current = parent
            if reached_root:
                return
        raise InputOutputError(
            f"the destination directory sits more than {MAX_CONTAINMENT_ASCENT} "
            f"directories below the filesystem root, so it cannot be confirmed to lie "
            f"outside {_path_shown(READ_ONLY_SOURCE_ROOT)}: {shown}"
        )
    finally:
        os.close(current)


def _confirm_replaceable(
    name: str, descriptor: int, destination: Path, *, overwrite: bool
) -> int | None:
    """Return the mode of the entry ``name`` names inside the held directory, or None.

    The entry is examined relative to ``descriptor`` and without following a symbolic
    link, so the entry examined is the entry inside the directory the caller holds. An
    absent name passes and returns None; a symbolic link and anything that is not a
    regular file are refused. An existing regular file is refused unless ``overwrite``
    is true, and under ``overwrite`` its permission bits are returned so the record
    that replaces it can carry the mode it already carries. ``destination`` names the
    entry in any diagnostic.
    """
    try:
        info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise InputOutputError(
            f"the destination cannot be examined: {_path_shown(destination)}: "
            f"{_reason(error)}"
        ) from error
    if stat.S_ISLNK(info.st_mode):
        raise InputOutputError(
            f"the destination is a symbolic link: {_path_shown(destination)}"
        )
    if not stat.S_ISREG(info.st_mode):
        raise InputOutputError(
            f"the destination exists and is not a regular file: "
            f"{_path_shown(destination)}"
        )
    if not overwrite:
        raise InputOutputError(
            f"the destination exists and is left in place: "
            f"{_path_shown(destination)}; {OVERWRITE_OPTION} replaces an existing "
            "regular file"
        )
    return stat.S_IMODE(info.st_mode)


def _write_through_temporary(
    encoded: bytes, name: str, descriptor: int, destination: Path, *, overwrite: bool
) -> None:
    """Write ``encoded`` to a temporary entry beside ``name`` and move it onto ``name``.

    Every step is taken relative to ``descriptor``: the temporary entry is created
    exclusively and without following a symbolic link, the content is written and
    flushed, the destination name is confirmed once more immediately before the move,
    and the move replaces the destination in one step, so no reader observes a partial
    record. The directory entry is flushed as well, and a filesystem that refuses to
    flush a directory leaves the record in place rather than failing the run. A
    temporary entry that survives a failure is removed relative to the same descriptor.

    The temporary entry is created with ``FILE_MODE`` and that mode is set on the open
    descriptor, so a record this tool creates carries it whatever the ambient umask
    requested, and it carries it across the move onto the destination name. The final
    confirmation reports the mode of an existing regular file the move replaces under
    ``overwrite``, and that mode is set on the same open descriptor before the move, so
    a file this tool did not create keeps the mode it carries. A destination name
    occupied since the earlier confirmation is refused here rather than replaced when
    ``overwrite`` is false.
    """
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    temporary: str | None = None
    file_descriptor = -1
    for attempt in range(MAX_TEMPORARY_ATTEMPTS):
        candidate = f".{name}.{os.getpid()}.{attempt}.tmp"
        try:
            file_descriptor = os.open(
                candidate, flags, FILE_MODE, dir_fd=descriptor
            )
        except FileExistsError:
            continue
        except OSError as error:
            raise InputOutputError(
                f"the destination cannot be written through a temporary entry: "
                f"{_path_shown(destination)}: {_reason(error)}"
            ) from error
        temporary = candidate
        break
    if temporary is None or file_descriptor < 0:
        raise InputOutputError(
            f"no temporary entry could be created beside the destination after "
            f"{MAX_TEMPORARY_ATTEMPTS} attempts: {_path_shown(destination)}"
        )
    try:
        try:
            os.fchmod(file_descriptor, FILE_MODE)
            written = 0
            while written < len(encoded):
                written += os.write(file_descriptor, encoded[written:])
            os.fsync(file_descriptor)
            replaced = _confirm_replaceable(
                name, descriptor, destination, overwrite=overwrite
            )
            if replaced is not None:
                os.fchmod(file_descriptor, replaced)
        finally:
            os.close(file_descriptor)
        os.replace(temporary, name, src_dir_fd=descriptor, dst_dir_fd=descriptor)
        temporary = None
        try:
            os.fsync(descriptor)
        except OSError:
            pass
    except OSError as error:
        raise InputOutputError(
            f"the landing record cannot be written: {_path_shown(destination)}: "
            f"{_reason(error)}"
        ) from error
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary, dir_fd=descriptor)
            except OSError:
                pass


def write_record(
    record: Mapping[str, str | None],
    destination: Path,
    field_order: Sequence[str],
    *,
    overwrite: bool = False,
) -> Path:
    """Write the landing record to ``destination`` and return the path written.

    The destination is confined by ``confine_destination`` before anything is created,
    and the canonical form it returns is the path written. Missing parent directories
    are then created one at a time, outermost first, so each of them carries
    ``DIRECTORY_MODE`` rather than only the innermost one. The destination directory is
    held open as one descriptor, opened without following a symbolic link, and every
    later step is taken relative to that descriptor: the containment check against the
    read-only source directory, the examination of the destination name, the creation of
    the temporary entry, the move onto the destination name and both flushes. The parent
    therefore cannot be substituted between the checks and the write. The temporary
    entry carries ``FILE_MODE`` and a destination name this call creates carries that
    same mode, so a reader never observes a partial record. A destination that already
    exists is refused unless ``overwrite`` is true, and is then replaced only when it is
    a regular file and is not a symbolic link, keeping the mode it carries; a
    destination directory that is itself a symbolic link is refused.

    Raises ``FieldMapError`` when the record does not match ``field_order`` and
    ``InputOutputError`` when the destination is refused, cannot be created or cannot
    be written.
    """
    encoded = serialise_record(record, field_order).encode(CAPTURE_ENCODING)
    target = confine_destination(destination, overwrite=overwrite)
    name = target.name
    directory = target.parent
    _create_destination_directory(directory)
    try:
        descriptor = os.open(
            directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        )
    except OSError as error:
        raise InputOutputError(
            f"the destination directory cannot be opened: {_path_shown(directory)}: "
            f"{_reason(error)}"
        ) from error
    try:
        _refuse_read_only_directory(descriptor, directory)
        _confirm_replaceable(name, descriptor, target, overwrite=overwrite)
        _write_through_temporary(
            encoded, name, descriptor, target, overwrite=overwrite
        )
    finally:
        os.close(descriptor)
    return target


def summarise(
    destination: Path,
    record: Mapping[str, str | None],
    *,
    source_system_key_origin: str,
    show_identifiers: bool = False,
) -> str:
    """Return the one-line stdout summary of a written landing record.

    ``destination`` is the canonical path the record was written to and
    ``source_system_key_origin`` is the origin ``resolve_source_system_key`` reported
    for the key the record carries. The default line names that path, the source-system
    key with that origin - a discriminator of source systems, not an identifier of any
    policy, customer or broker, so it is named in full - the derived policy type, a
    product class of four letters that identifies no policy, customer or broker, the
    return code, how many landing keys carry a value and how many are null, and the
    digest ``_digest`` returns for the policy number, so the same run stays recognisable
    without the identifier reaching stdout. It carries no policy number, customer
    number, broker id or broker's reference, so a captured run log holds no business
    identifier.

    ``show_identifiers`` restores the identifier line for a local run: the request id,
    the policy type, the policy number, the customer number, the broker id, the
    broker's reference and the return code, each named with its landing key, after the
    same source-system key and origin. It carries the resolution
    ``resolve_show_identifiers`` returned, so the option and the
    ``SHOW_IDENTIFIERS_VARIABLE`` environment variable select the same line. The
    redacted line carries the digest of the policy number whatever that resolution is,
    so a line stating that identifiers are redacted never carries one.
    """

    def shown(name: str) -> str:
        value = record.get(name)
        return "null" if value is None else value

    def digested(name: str) -> str:
        value = record.get(name)
        return "null" if value is None else _digest(value)

    source_system = (
        f"{LANDING_SOURCE_SYSTEM_KEY}={shown(LANDING_SOURCE_SYSTEM_KEY)} "
        f"from {source_system_key_origin}"
    )
    if show_identifiers:
        named = (
            LANDING_REQUEST_ID,
            LANDING_POLICY_TYPE,
            LANDING_POLICY_NUMBER,
            LANDING_CUSTOMER_NUMBER,
            LANDING_BROKER_ID,
            LANDING_BROKERS_REFERENCE,
            LANDING_RETURN_CODE,
        )
        values = " ".join(f"{name}={shown(name)}" for name in named)
        return f"landed {destination} {source_system} {values}"
    present = sum(1 for value in record.values() if value is not None)
    return (
        f"landed {destination} {source_system} "
        f"{LANDING_POLICY_TYPE}={shown(LANDING_POLICY_TYPE)} "
        f"{LANDING_RETURN_CODE}={shown(LANDING_RETURN_CODE)} "
        f"keys={len(record)} values={present} nulls={len(record) - present} "
        f"policy_digest={digested(LANDING_POLICY_NUMBER)} "
        "identifiers=redacted (--show-identifiers carries them)"
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

# Prefix of the private scratch directory one self-test run creates and removes, and the
# names the cases give the capture and the landing record inside it.
_SCRATCH_PREFIX = "extract-commarea-selftest-"
_SCRATCH_CAPTURE_NAME = "commarea_post.dat"
_SCRATCH_RECORD_NAME = "landing.json"

# Window content the matrix renders a record from, keyed by the field map's landing key.
# A value is padded to the declared window: left with zeros for a numeric_display item
# and right with spaces for an alphanumeric one. An empty value renders a blank window.
# Both sets carry the values the harness driver's post-chain captures hold for request
# ids 01AMOT and 01ACOM, so the two records share no identifier and no amount.
_MOTOR_WINDOWS: Mapping[str, str] = {
    LANDING_REQUEST_ID: "01AMOT",
    LANDING_RETURN_CODE: RETURN_CODE_SUCCESS,
    LANDING_CUSTOMER_NUMBER: "1001",
    LANDING_POLICY_NUMBER: "1000301",
    LANDING_ISSUE_DATE: "2026-08-19",
    LANDING_EXPIRY_DATE: "2027-08-18",
    LANDING_LAST_CHANGED: "2026-08-19-12.00.00.000000",
    LANDING_BROKER_ID: "42",
    LANDING_BROKERS_REFERENCE: "BRMOT001",
    "payment_amount": "500",
    "motor_premium_amount": "450",
}
_MOTOR_RECORD: Mapping[str, str | None] = {
    LANDING_SOURCE_SYSTEM_KEY: DEFAULT_SOURCE_SYSTEM_KEY,
    LANDING_POLICY_NUMBER: "1000301",
    LANDING_POLICY_TYPE: "M",
    LANDING_CUSTOMER_NUMBER: "1001",
    LANDING_REQUEST_ID: "01AMOT",
    LANDING_RETURN_CODE: "00",
    LANDING_ISSUE_DATE: "2026-08-19",
    LANDING_EXPIRY_DATE: "2027-08-18",
    LANDING_LAST_CHANGED: "2026-08-19T12:00:00.000000",
    LANDING_BROKER_ID: "42",
    LANDING_BROKERS_REFERENCE: "BRMOT001",
    "payment_amount": "500",
    "motor_premium_amount": "450",
    "fire_premium_amount": None,
    "crime_premium_amount": None,
    "flood_premium_amount": None,
    "weather_premium_amount": None,
}
_COMMERCIAL_WINDOWS: Mapping[str, str] = {
    LANDING_REQUEST_ID: "01ACOM",
    LANDING_RETURN_CODE: RETURN_CODE_SUCCESS,
    LANDING_CUSTOMER_NUMBER: "2002",
    LANDING_POLICY_NUMBER: "1000302",
    LANDING_ISSUE_DATE: "2026-08-19",
    LANDING_EXPIRY_DATE: "2027-08-18",
    LANDING_LAST_CHANGED: "2026-08-19-12.00.00.000000",
    LANDING_BROKER_ID: "84",
    LANDING_BROKERS_REFERENCE: "BRCOM001",
    "payment_amount": "1750",
    "fire_premium_amount": "13500",
    "crime_premium_amount": "3400",
    "flood_premium_amount": "7800",
    "weather_premium_amount": "2600",
}
_COMMERCIAL_RECORD: Mapping[str, str | None] = {
    LANDING_SOURCE_SYSTEM_KEY: DEFAULT_SOURCE_SYSTEM_KEY,
    LANDING_POLICY_NUMBER: "1000302",
    LANDING_POLICY_TYPE: "C",
    LANDING_CUSTOMER_NUMBER: "2002",
    LANDING_REQUEST_ID: "01ACOM",
    LANDING_RETURN_CODE: "00",
    LANDING_ISSUE_DATE: "2026-08-19",
    LANDING_EXPIRY_DATE: "2027-08-18",
    LANDING_LAST_CHANGED: "2026-08-19T12:00:00.000000",
    LANDING_BROKER_ID: "84",
    LANDING_BROKERS_REFERENCE: "BRCOM001",
    "payment_amount": "1750",
    "motor_premium_amount": None,
    "fire_premium_amount": "13500",
    "crime_premium_amount": "3400",
    "flood_premium_amount": "7800",
    "weather_premium_amount": "2600",
}

# The 17 landing keys in the order the field map lists them, which is the order every
# landed record and every JSON line carries.
_EXPECTED_FIELD_ORDER = tuple(_MOTOR_RECORD)

# Request ids and the policy types the routing table assigns them, and one id no branch
# of the EVALUATE at base/src/lgapdb01.cbl:184-207 recognises.
_ROUTED_REQUEST_IDS = {
    "01AEND": "E",
    "01AHOU": "H",
    "01AMOT": "M",
    "01ACOM": "C",
}
_UNROUTED_REQUEST_ID = "01AXXX"

# The landing keys the field map records 'blank_window_lands_null' for, whose window
# lands null when it holds only spaces. Every other window whose content the map
# requires is refused when it is blank.
_BLANK_WINDOW_LANDS_NULL = (LANDING_BROKER_ID,)

# Control characters a case places inside a decoded window: NUL, tab, line feed,
# carriage return and DEL, each of which a landed value never carries.
_CONTROL_CHARACTER_CASES = ("\x00", "\t", "\n", "\r", "\x7f")

# Content a case writes into a window of the product overlay its request does not
# select; the overlays redefine the same bytes from offset 101.
_INACTIVE_OVERLAY_TEXT = "ADDRESS1"


class _SelfTestFailure(Exception):
    """One self-test case did not hold; the message states what was observed."""


class _CaseResult(NamedTuple):
    """The outcome of one self-test case."""

    name: str
    passed: bool
    detail: str


class _CliResult(NamedTuple):
    """The status and captured streams of one command line run in this process."""

    status: int
    stdout: str
    stderr: str


def _run_cli(argv: list[str]) -> _CliResult:
    """Run one command line in this process and capture its status and streams."""
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            status = main(argv)
        except SystemExit as request:
            status = request.code if isinstance(request.code, int) else 1
    return _CliResult(status=status, stdout=out.getvalue(), stderr=err.getvalue())


def _expect(observed: Any, expected: Any, what: str) -> None:
    """Confirm ``observed`` equals ``expected``, naming ``what`` when it does not."""
    if observed != expected:
        raise _SelfTestFailure(
            f"{what} is {_display(observed)}, expected {_display(expected)}"
        )


def _expect_record(
    observed: Mapping[str, str | None],
    expected: Mapping[str, str | None],
    what: str,
) -> None:
    """Confirm one landing record carries the expected keys, in order, and values."""
    if tuple(observed) != tuple(expected):
        raise _SelfTestFailure(
            f"{what} carries keys {_quote_all(observed)}, expected "
            f"{_quote_all(expected)}"
        )
    differing = [name for name in expected if observed[name] != expected[name]]
    if differing:
        detail = "; ".join(
            f"{name} is {_display(observed[name])}, expected "
            f"{_display(expected[name])}"
            for name in differing
        )
        raise _SelfTestFailure(f"{what} differs: {detail}")


def _expect_holds(text: str, fragment: str, what: str) -> None:
    """Confirm ``text`` names ``fragment``."""
    if fragment not in text:
        raise _SelfTestFailure(
            f"{what} is {_shown(text, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}, which does "
            f"not name {_shown(fragment)}"
        )


def _expect_lacks(text: str, fragment: str, what: str) -> None:
    """Confirm ``text`` does not name ``fragment``."""
    if fragment in text:
        raise _SelfTestFailure(
            f"{what} is {_shown(text, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}, which names "
            f"{_shown(fragment)}"
        )


def _expect_raised(
    kind: type[ExtractError],
    status: int,
    fragments: Sequence[str],
    action: Callable[[], Any],
    what: str,
) -> str:
    """Run ``action``, confirm the diagnostic it raises, and return that diagnostic.

    The raised error must be an instance of ``kind``, must carry ``status`` as its exit
    status, and its message must name every fragment. An action that returns instead of
    raising fails the case.
    """
    try:
        outcome = action()
    except ExtractError as error:
        if not isinstance(error, kind):
            raise _SelfTestFailure(
                f"{what} raised {_type_name(error)} carrying "
                f"{_shown(str(error), MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}, expected "
                f"{kind.__name__}"
            ) from None
        if error.exit_status != status:
            raise _SelfTestFailure(
                f"{what} raised {kind.__name__} with status {error.exit_status}, "
                f"expected {status}"
            ) from None
        message = str(error)
        for fragment in fragments:
            _expect_holds(message, fragment, f"the diagnostic {what} raised")
        return _escaped(message, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)
    raise _SelfTestFailure(
        f"{what} returned {_display(outcome)}, expected {kind.__name__}"
    )


def _expect_cli_failure(
    result: _CliResult, status: int, fragments: Sequence[str], what: str
) -> str:
    """Confirm one command line failed with ``status`` and one named diagnostic line."""
    if result.status != status:
        raise _SelfTestFailure(
            f"{what} returned status {result.status} carrying "
            f"{_shown(result.stderr, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}, expected "
            f"{status}"
        )
    if result.stdout:
        raise _SelfTestFailure(
            f"{what} wrote {_shown(result.stdout, MAX_DIAGNOSTIC_CHARACTERS)} to "
            "stdout, expected nothing"
        )
    if not result.stderr.endswith("\n") or result.stderr.count("\n") != 1:
        raise _SelfTestFailure(
            f"{what} wrote {result.stderr.count(chr(10))} line ending(s) to stderr, "
            "expected 1"
        )
    line = result.stderr[:-1]
    if not line.startswith(f"{_PROGRAM}: "):
        raise _SelfTestFailure(
            f"{what} wrote a diagnostic that does not name this tool: "
            f"{_shown(line, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}"
        )
    for fragment in fragments:
        _expect_holds(line, fragment, f"the diagnostic {what} wrote")
    return _escaped(line, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)


def _expect_cli_success(result: _CliResult, what: str) -> str:
    """Confirm one command line succeeded and wrote one summary line to stdout."""
    if result.status != EXIT_OK:
        raise _SelfTestFailure(
            f"{what} returned status {result.status} carrying "
            f"{_shown(result.stderr, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}, expected "
            f"{EXIT_OK}"
        )
    if result.stderr:
        raise _SelfTestFailure(
            f"{what} wrote {_shown(result.stderr, MAX_DIAGNOSTIC_CHARACTERS)} to "
            "stderr, expected nothing"
        )
    if not result.stdout.endswith("\n") or result.stdout.count("\n") != 1:
        raise _SelfTestFailure(
            f"{what} wrote {result.stdout.count(chr(10))} line ending(s) to stdout, "
            "expected 1"
        )
    return result.stdout[:-1]


def _rendered_record(field_map: FieldMap, windows: Mapping[str, str]) -> str:
    """Return one COMMAREA record of the map's record length carrying ``windows``.

    Each key of ``windows`` is a landing key the field map places in the record. Its
    text is padded to the declared length, left with zeros for a ``KIND_NUMERIC`` item
    and right with spaces for a ``KIND_ALPHANUMERIC`` one; an empty value renders the
    window blank whatever its kind. A key whose window belongs to a product overlay the
    request does not select is written all the same, which is how a case fills the bytes
    of an inactive overlay. Every other byte of the record is a space.
    """
    characters = [" "] * field_map.record_length
    for name, value in windows.items():
        field = field_map.fields.get(name)
        if field is None or field.offset is None or field.length is None:
            raise _SelfTestFailure(
                f"the field map places no window for landing key {_shown(name)}"
            )
        if len(value) > field.length:
            raise _SelfTestFailure(
                f"the case gives landing key {_shown(name)} {len(value)} characters "
                f"for its {field.length}-character window"
            )
        if not value:
            padded = " " * field.length
        elif field.kind == KIND_NUMERIC:
            padded = value.rjust(field.length, "0")
        else:
            padded = value.ljust(field.length, " ")
        start = field.offset - 1
        characters[start : start + field.length] = list(padded)
    return "".join(characters)


def _written(directory: Path, name: str, payload: bytes) -> Path:
    """Write one scratch file below ``directory`` and return its path."""
    path = directory / name
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, FILE_MODE
    )
    try:
        written = 0
        while written < len(payload):
            written += os.write(descriptor, payload[written:])
    finally:
        os.close(descriptor)
    return path


def _case_directory(scratch: Path, name: str) -> Path:
    """Return one private directory for a case, created below the run's scratch root."""
    directory = scratch / name
    directory.mkdir(mode=DIRECTORY_MODE)
    return directory


def _extraction_argv(
    capture: Path, destination: Path, map_path: Path, *extra: str
) -> list[str]:
    """Return one extraction command line naming the capture, output and field map."""
    return [
        "--commarea",
        str(capture),
        "--output",
        str(destination),
        "--field-map",
        str(map_path),
        "--source-system-key",
        DEFAULT_SOURCE_SYSTEM_KEY,
        *extra,
    ]


def _mutated_map_text(text: str, mutate: Callable[[Any], None]) -> str:
    """Return the field map text with ``mutate`` applied to the parsed document.

    The document is parsed, handed to ``mutate`` as a deep copy of the real map's
    members, and serialised again, so a case describes the one contradiction it is
    exercising rather than restating the whole map.
    """
    document = copy.deepcopy(yaml.safe_load(text))
    mutate(document)
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def _field_entry(document: Any, landing_field: str) -> Any:
    """Return the ``fields`` entry of ``document`` carrying ``landing_field``."""
    for entry in document["fields"]:
        if entry.get("landing_field") == landing_field:
            return entry
    raise _SelfTestFailure(
        f"the field map records no entry for landing key {_shown(landing_field)}"
    )


def _fingerprint(path: Path) -> tuple[bytes, int]:
    """Return the content and modification time of one file, to compare it later."""
    return path.read_bytes(), os.stat(path).st_mtime_ns


def _expect_untouched(path: Path, before: tuple[bytes, int], what: str) -> None:
    """Confirm one file still holds the content and modification time it held."""
    after = _fingerprint(path)
    if after[0] != before[0]:
        raise _SelfTestFailure(
            f"{what} holds {len(after[0])} bytes, held {len(before[0])} bytes before "
            "the refused run"
        )
    if after[1] != before[1]:
        raise _SelfTestFailure(
            f"{what} carries modification time {after[1]}, carried {before[1]} before "
            "the refused run"
        )


def _decoded_line(path: Path) -> tuple[str, dict[str, Any]]:
    """Return the landed line and the object it parses to, rejecting a repeated key.

    The line must be one JSON object terminated by exactly one line feed, and a member
    the object repeats is refused rather than resolved to its last value.
    """

    def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        seen: dict[str, Any] = {}
        for key, value in pairs:
            if key in seen:
                raise _SelfTestFailure(
                    f"the landed record repeats the member {_shown(key)}"
                )
            seen[key] = value
        return seen

    text = path.read_bytes().decode(CAPTURE_ENCODING)
    if not text.endswith("\n") or text.count("\n") != 1:
        raise _SelfTestFailure(
            f"the landed record carries {text.count(chr(10))} line ending(s), "
            "expected 1"
        )
    return text, json.loads(text, object_pairs_hook=_no_duplicates)


# ---------------------------------------------------------------------------
# Self-test cases: field map
# ---------------------------------------------------------------------------


def _case_field_map_members(field_map: FieldMap) -> str:
    """Confirm the real field map supplies every member this tool reads."""
    _expect(field_map.record_length, COMMAREA_RECORD_LENGTH, "the record length")
    _expect(field_map.field_order, _EXPECTED_FIELD_ORDER, "the landing field order")
    _expect(len(field_map.field_order), 17, "the number of landing keys")
    _expect(
        {name: field_map.routing[name] for name in sorted(field_map.routing)},
        _ROUTED_REQUEST_IDS,
        "the request routing table",
    )
    _expect(len(field_map.amount_fields), 6, "the number of amount keys")
    _expect(
        tuple(sorted(field_map.return_code_domain)),
        ("00", "70", "80", "90", "98", "99"),
        "the return-code domain",
    )
    _expect(
        sorted(field_map.return_code_meanings),
        sorted(field_map.return_code_domain),
        "the codes the return_codes section records",
    )
    _expect(
        field_map.source_system_key_field,
        LANDING_SOURCE_SYSTEM_KEY,
        "the warehouse-assigned landing key",
    )
    _expect(
        sorted(field_map.nullability),
        sorted(set(_ROUTED_REQUEST_IDS.values())),
        "the policy types the nullability section records",
    )
    _expect(
        sorted(
            name
            for name, field in field_map.fields.items()
            if field.blank_window_lands_null
        ),
        sorted(_BLANK_WINDOW_LANDS_NULL),
        "the landing keys whose blank window lands null",
    )
    return (
        f"{len(field_map.field_order)} landing keys, "
        f"{len(field_map.routing)} routed request ids, "
        f"{len(field_map.amount_fields)} amounts, "
        f"{len(field_map.return_code_domain)} return codes, "
        f"{len(_BLANK_WINDOW_LANDS_NULL)} blank windows landing null"
    )


def _case_return_code_meanings(field_map: FieldMap) -> str:
    """Confirm every recorded return code carries the meaning the chain gives it."""
    expected = {
        "00": "success",
        "70": "policy insert returned SQLCODE -530",
        "80": "VSAM write response was not normal",
        "90": "SQL failure",
        "98": "COMMAREA shorter than the required length",
        "99": "unsupported request id",
    }
    for code, meaning in expected.items():
        _expect(
            field_map.return_code_meanings.get(code),
            meaning,
            f"the meaning recorded for return code {code}",
        )
    return f"{len(expected)} return-code meanings match the recorded convention"


def _case_map_refused(
    directory: Path,
    map_text: str,
    name: str,
    mutate: Callable[[Any], None],
    fragments: Sequence[str],
) -> str:
    """Confirm one contradiction inside the field map is refused with its own status."""
    path = _written(
        directory, f"{name}.yml", _mutated_map_text(map_text, mutate).encode("utf-8")
    )
    return _expect_raised(
        FieldMapError,
        EXIT_FIELD_MAP_INVALID,
        fragments,
        lambda: load_field_map(path),
        f"loading the field map mutated for {name}",
    )


def _case_map_bytes_refused(
    directory: Path,
    name: str,
    payload: bytes,
    kind: type[ExtractError],
    status: int,
    fragments: Sequence[str],
) -> str:
    """Confirm one field map document this tool cannot read is refused."""
    path = _written(directory, f"{name}.yml", payload)
    return _expect_raised(
        kind,
        status,
        fragments,
        lambda: load_field_map(path),
        f"loading the field map written for {name}",
    )


def _case_map_missing_refused(directory: Path) -> str:
    """Confirm a field map path that names no file is refused as an input failure."""
    path = directory / "absent.yml"
    return _expect_raised(
        InputOutputError,
        EXIT_IO_ERROR,
        ["the field map cannot be opened"],
        lambda: load_field_map(path),
        "loading a field map that does not exist",
    )


# ---------------------------------------------------------------------------
# Self-test cases: capture reading
# ---------------------------------------------------------------------------


def _case_capture_accepted(
    directory: Path, name: str, payload: bytes, field_map: FieldMap
) -> str:
    """Confirm one capture is read as exactly the record the field map declares."""
    path = _written(directory, name, payload)
    record = read_commarea(path, field_map.record_length)
    _expect(len(record), field_map.record_length, "the length of the record read")
    return f"{len(payload)} bytes read as a {len(record)}-character record"


def _case_capture_refused(
    directory: Path,
    name: str,
    payload: bytes,
    kind: type[ExtractError],
    status: int,
    fragments: Sequence[str],
    field_map: FieldMap,
) -> str:
    """Confirm one capture that breaches the record contract is refused."""
    path = _written(directory, name, payload)
    return _expect_raised(
        kind,
        status,
        fragments,
        lambda: read_commarea(path, field_map.record_length),
        f"reading the capture written for {name}",
    )


def _case_capture_directory_refused(directory: Path, field_map: FieldMap) -> str:
    """Confirm a capture path naming a directory is refused as an input failure."""
    path = directory / "capture-directory"
    path.mkdir(mode=DIRECTORY_MODE)
    return _expect_raised(
        InputOutputError,
        EXIT_IO_ERROR,
        ["the COMMAREA capture is not a regular file"],
        lambda: read_commarea(path, field_map.record_length),
        "reading a capture path that names a directory",
    )


def _case_capture_missing_refused(directory: Path, field_map: FieldMap) -> str:
    """Confirm a capture path that names no file is refused as an input failure."""
    path = directory / "absent.dat"
    return _expect_raised(
        InputOutputError,
        EXIT_IO_ERROR,
        ["the COMMAREA capture cannot be opened"],
        lambda: read_commarea(path, field_map.record_length),
        "reading a capture that does not exist",
    )


# ---------------------------------------------------------------------------
# Self-test cases: decoding, routing and the landing record
# ---------------------------------------------------------------------------


def _case_landing_record(
    field_map: FieldMap,
    windows: Mapping[str, str],
    expected: Mapping[str, str | None],
    what: str,
) -> str:
    """Confirm one rendered record decodes to the expected landing record."""
    record = build_landing_record(
        _rendered_record(field_map, windows), field_map, DEFAULT_SOURCE_SYSTEM_KEY
    )
    _expect_record(record, expected, f"the landing record of {what}")
    populated = sum(1 for value in record.values() if value is not None)
    return (
        f"{len(record)} keys in the map's order, {populated} populated, "
        f"{len(record) - populated} null"
    )


def _case_record_refused(
    field_map: FieldMap,
    windows: Mapping[str, str],
    kind: type[ExtractError],
    status: int,
    fragments: Sequence[str],
    what: str,
) -> str:
    """Confirm one rendered record is refused with the expected status."""
    record = _rendered_record(field_map, windows)
    return _expect_raised(
        kind,
        status,
        fragments,
        lambda: build_landing_record(record, field_map, DEFAULT_SOURCE_SYSTEM_KEY),
        f"decoding {what}",
    )


def _case_refusal_names_values_under_the_option(field_map: FieldMap) -> str:
    """Confirm a refused window names its own characters once display is enabled.

    The default contract withholds every record value from a diagnostic, so the same
    refusal is exercised twice: once withheld, where the diagnostic states the character
    count alone, and once with display enabled, where it names the offending character.
    The setting is restored before the case returns.
    """
    windows = {**_MOTOR_WINDOWS, "payment_amount": "50A"}
    record = _rendered_record(field_map, windows)
    previous = show_identifiers_enabled()
    try:
        set_show_identifiers(False)
        withheld = _expect_raised(
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-PAYMENT", "not all digits", _withheld(6)),
            lambda: build_landing_record(record, field_map, DEFAULT_SOURCE_SYSTEM_KEY),
            "decoding a non-numeric payment with values withheld",
        )
        _expect_lacks(withheld, "'00050A'", "the withheld diagnostic")
        set_show_identifiers(True)
        shown = _expect_raised(
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-PAYMENT", "not all digits", "'00050A'", "'A'"),
            lambda: build_landing_record(record, field_map, DEFAULT_SOURCE_SYSTEM_KEY),
            "decoding a non-numeric payment with values shown",
        )
    finally:
        set_show_identifiers(previous)
    return (
        f"withheld as {_shown(_withheld(6))}, named under "
        f"{SHOW_IDENTIFIERS_OPTION}: {_escaped(shown, 72)}"
    )


def _case_control_character_refused(
    field_map: FieldMap, name: str, character: str
) -> str:
    """Confirm one control character inside an alphanumeric window is refused.

    The window of landing key ``name`` carries ``character`` between two printable
    characters, and the whole record is decoded so the refusal is the one an extraction
    meets. The diagnostic must name the item, its byte range, the landing key and the
    breached constraint, and must carry the character escaped rather than raw.
    """
    field = field_map.fields[name]
    record = _rendered_record(field_map, {**_MOTOR_WINDOWS, name: f"A{character}B"})
    diagnostic = _expect_raised(
        RecordError,
        EXIT_RECORD_REJECTED,
        (
            field.described,
            "carries a control character",
            _shown(name),
            "1 characters are control characters, at window positions 2",
        ),
        lambda: build_landing_record(record, field_map, DEFAULT_SOURCE_SYSTEM_KEY),
        f"decoding {name} carrying {_shown(_escaped_character(character))}",
    )
    _expect_lacks(diagnostic, character, "the control-character diagnostic")
    return f"{name} refused: {_escaped(diagnostic, 96)}"


def _case_control_character_names_itself_under_the_option(
    field_map: FieldMap, character: str
) -> str:
    """Confirm a refused control character is named, escaped, once display is enabled.

    The default contract withholds the window from the diagnostic, which then states
    how many control characters it holds and where; with display enabled the diagnostic
    also names them, each escaped to printable 7-bit ASCII. The setting is restored
    before the case returns.
    """
    record = _rendered_record(
        field_map,
        {**_MOTOR_WINDOWS, LANDING_BROKERS_REFERENCE: f"AB{character}CD"},
    )
    escaped = _escaped_character(character)
    previous = show_identifiers_enabled()
    try:
        set_show_identifiers(False)
        withheld = _expect_raised(
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-BROKERSREF", "carries a control character", _withheld(10)),
            lambda: build_landing_record(record, field_map, DEFAULT_SOURCE_SYSTEM_KEY),
            "decoding a control character with values withheld",
        )
        _expect_lacks(withheld, escaped, "the withheld control-character diagnostic")
        set_show_identifiers(True)
        shown = _expect_raised(
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-BROKERSREF", "carries a control character", f"they are '{escaped}'"),
            lambda: build_landing_record(record, field_map, DEFAULT_SOURCE_SYSTEM_KEY),
            "decoding a control character with values shown",
        )
        _expect_lacks(shown, character, "the shown control-character diagnostic")
    finally:
        set_show_identifiers(previous)
    return (
        f"named as '{escaped}' under {SHOW_IDENTIFIERS_OPTION}: "
        f"{_escaped(shown, 72)}"
    )


def _case_window_decoding(
    field_map: FieldMap,
    windows: Mapping[str, str],
    expected: Mapping[str, str | None],
    what: str,
) -> str:
    """Confirm every landing key the map reads from the record decodes as expected."""
    record = _rendered_record(field_map, windows)
    policy_type = str(expected[LANDING_POLICY_TYPE])
    checked = 0
    for name in field_map.field_order:
        field = field_map.fields.get(name)
        if field is None or not field.is_read_from_record:
            continue
        if name == LANDING_RETURN_CODE:
            observed: str | None = decode_return_code(field, record)
        elif name in field_map.amount_fields:
            observed = decode_amount(field, record, policy_type, field_map)
        elif name == LANDING_LAST_CHANGED:
            decoded = _decode_chain_populated(field, record)
            observed = None if decoded is None else normalise_timestamp(decoded, field)
        elif name in CALENDAR_DATE_FIELDS:
            observed = validate_calendar_date(decode_window(field, record), field)
        else:
            observed = decode_window(field, record)
        _expect(observed, expected[name], f"the decoded window of {name} on {what}")
        checked += 1
    return f"{checked} windows of {what} decoded to their expected values"


def _case_request_routing(field_map: FieldMap, request_id: str, expected: str) -> str:
    """Confirm one routed request id yields the policy type the map records for it."""
    _expect(
        derive_policy_type(request_id, field_map),
        expected,
        f"the policy type derived for request id {request_id}",
    )
    return f"request id {request_id} routes to policy type {expected}"


def _case_return_code_refused(field_map: FieldMap, code: str) -> str:
    """Confirm one recorded unsuccessful return code is refused with its meaning."""
    meaning = field_map.return_code_meanings[code]
    return _case_record_refused(
        field_map,
        {**_MOTOR_WINDOWS, LANDING_RETURN_CODE: code},
        ChainNotSuccessfulError,
        EXIT_CHAIN_NOT_SUCCESSFUL,
        [f"'{code}'", meaning, "did not complete the policy issue"],
        f"a motor record whose return code is {code}",
    )


def _case_product_null_pattern(field_map: FieldMap) -> str:
    """Confirm the amount keys applicable to each policy type match the recorded split.

    Every policy type the routing table yields is checked against
    ``product_premium_nullability``: the payment is applicable to all four, the motor
    premium to M alone, the four commercial premiums to C alone, and E and H carry no
    product premium.
    """
    expected = {
        "M": {"payment_amount", "motor_premium_amount"},
        "C": {
            "payment_amount",
            "fire_premium_amount",
            "crime_premium_amount",
            "flood_premium_amount",
            "weather_premium_amount",
        },
        "E": {"payment_amount"},
        "H": {"payment_amount"},
    }
    for policy_type, applicable in expected.items():
        observed = {
            name
            for name in field_map.amount_fields
            if amount_applies(name, policy_type, field_map)
        }
        _expect(
            sorted(observed),
            sorted(applicable),
            f"the amounts applicable to policy type {policy_type}",
        )
    return (
        "M carries the motor premium only, C the four commercial premiums only, "
        "E and H no product premium"
    )


def _case_timestamp_window(field_map: FieldMap, raw: str, expected: str) -> str:
    """Confirm one returned timestamp window normalises to the expected value."""
    record = build_landing_record(
        _rendered_record(
            field_map, {**_MOTOR_WINDOWS, LANDING_LAST_CHANGED: raw}
        ),
        field_map,
        DEFAULT_SOURCE_SYSTEM_KEY,
    )
    _expect(
        record[LANDING_LAST_CHANGED],
        expected,
        f"the normalised timestamp of window {_shown(raw)}",
    )
    return f"{_shown(raw)} normalised to {_shown(expected)}"


def _case_timestamp_refused(
    field_map: FieldMap, raw: str, fragments: Sequence[str]
) -> str:
    """Confirm one impossible or unparsable returned timestamp is refused."""
    field = field_map.fields[LANDING_LAST_CHANGED]
    return _expect_raised(
        RecordError,
        EXIT_RECORD_REJECTED,
        fragments,
        lambda: normalise_timestamp(raw, field),
        f"normalising the timestamp {_shown(raw)}",
    )


def _case_date_accepted(field_map: FieldMap, name: str, value: str) -> str:
    """Confirm one real calendar date lands unchanged."""
    record = build_landing_record(
        _rendered_record(field_map, {**_MOTOR_WINDOWS, name: value}),
        field_map,
        DEFAULT_SOURCE_SYSTEM_KEY,
    )
    _expect(record[name], value, f"the landed value of {name}")
    return f"{name} {_shown(value)} landed unchanged"


def _case_date_refused(
    field_map: FieldMap, name: str, value: str, fragments: Sequence[str]
) -> str:
    """Confirm one impossible calendar date is refused before the record is landed."""
    return _case_record_refused(
        field_map,
        {**_MOTOR_WINDOWS, name: value},
        RecordError,
        EXIT_RECORD_REJECTED,
        fragments,
        f"a motor record whose {name} window holds {_shown(value)}",
    )


# ---------------------------------------------------------------------------
# Self-test cases: serialisation
# ---------------------------------------------------------------------------


def _case_serialised_line(field_map: FieldMap) -> str:
    """Confirm the landing record serialises to one JSON line in the map's order."""
    record = build_landing_record(
        _rendered_record(field_map, _COMMERCIAL_WINDOWS),
        field_map,
        DEFAULT_SOURCE_SYSTEM_KEY,
    )
    line = serialise_record(record, field_map.field_order)
    if not line.endswith("\n") or line.count("\n") != 1:
        raise _SelfTestFailure(
            f"the serialised record carries {line.count(chr(10))} line ending(s), "
            "expected 1"
        )
    parsed = json.loads(line)
    _expect_record(parsed, _COMMERCIAL_RECORD, "the parsed serialised record")
    positions = [line.index(f'"{name}"') for name in field_map.field_order]
    if positions != sorted(positions):
        raise _SelfTestFailure(
            "the serialised keys are not written in the field map's landing order"
        )
    _expect(line.isascii(), True, "whether the serialised line is ASCII")
    return f"{len(line)} characters, {len(parsed)} keys in the map's landing order"


def _case_serialised_rejects_non_string(field_map: FieldMap) -> str:
    """Confirm a landing value that is not a string or null is refused."""
    record: dict[str, Any] = dict(_COMMERCIAL_RECORD)
    record["payment_amount"] = 1750
    return _expect_raised(
        FieldMapError,
        EXIT_FIELD_MAP_INVALID,
        ["a string or null is required", "payment_amount"],
        lambda: serialise_record(record, field_map.field_order),
        "serialising a record carrying a number",
    )


def _case_serialised_rejects_wrong_order(field_map: FieldMap) -> str:
    """Confirm a landing record whose keys are out of order is refused."""
    record = dict(reversed(list(_COMMERCIAL_RECORD.items())))
    return _expect_raised(
        FieldMapError,
        EXIT_FIELD_MAP_INVALID,
        ["does not carry the field map's landing keys in order"],
        lambda: serialise_record(record, field_map.field_order),
        "serialising a record whose keys are reversed",
    )


# ---------------------------------------------------------------------------
# Self-test cases: destination, modes and output failures
# ---------------------------------------------------------------------------


def _prepared_capture(
    directory: Path, field_map: FieldMap, windows: Mapping[str, str]
) -> Path:
    """Write one rendered COMMAREA capture below ``directory`` and return its path."""
    record = _rendered_record(field_map, windows)
    return _written(
        directory, _SCRATCH_CAPTURE_NAME, (record + "\n").encode(CAPTURE_ENCODING)
    )


def _case_extraction_writes_record(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm one extraction lands the 17 keys of the record, in the map's order."""
    directory = _case_directory(scratch, "extraction")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / "landed" / "deeper" / _SCRATCH_RECORD_NAME
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    summary = _expect_cli_success(result, "the extraction of a motor capture")
    written = Path(os.path.realpath(destination.parent)) / destination.name
    _expect_holds(summary, str(written), "the summary line")
    text, parsed = _decoded_line(destination)
    _expect_record(parsed, _MOTOR_RECORD, "the landed record")
    return f"{len(parsed)} keys landed in {len(text)} characters"


def _case_created_modes(scratch: Path, map_path: Path, field_map: FieldMap) -> str:
    """Confirm the created directories and the landed record carry the private modes.

    The ambient umask is set to zero for the run, which is the setting under which a
    mode taken from the umask would leave the landed policy data world-readable. The
    expected modes are the required ones - 0700 for a created directory and 0600 for
    the landed record - rather than the constants the run applied.
    """
    directory = _case_directory(scratch, "modes")
    capture = _prepared_capture(directory, field_map, _COMMERCIAL_WINDOWS)
    created = directory / "landed"
    destination = created / "deeper" / _SCRATCH_RECORD_NAME
    previous = os.umask(0o000)
    try:
        result = _run_cli(_extraction_argv(capture, destination, map_path))
    finally:
        os.umask(previous)
    _expect_cli_success(result, "the extraction run under a zero umask")
    for path in (created, destination.parent):
        _expect(
            f"{stat.S_IMODE(os.stat(path).st_mode):04o}",
            "0700",
            f"the mode of the created directory {path.name}",
        )
    _expect(
        f"{stat.S_IMODE(os.stat(destination).st_mode):04o}",
        "0600",
        "the mode of the landed record",
    )
    return "two directories at 0700 and the record at 0600 under a zero umask"


def _case_existing_destination_refused(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm an existing destination is left in place without the overwrite option.

    The existing file carries content this tool never writes and mode 0644, so both its
    bytes and its permission bits are observable afterwards. The refusal names the
    destination and the option that replaces it.
    """
    directory = _case_directory(scratch, "existing-destination")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = _written(directory, _SCRATCH_RECORD_NAME, b"PRE-EXISTING CONTENT\n")
    os.chmod(destination, 0o644)
    before = _fingerprint(destination)
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    diagnostic = _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["the destination exists and is left in place", OVERWRITE_OPTION],
        "the extraction aimed at an existing file",
    )
    _expect_untouched(destination, before, "the existing destination")
    _expect(
        f"{stat.S_IMODE(os.stat(destination).st_mode):04o}",
        "0644",
        "the mode of the destination the refused run left in place",
    )
    return f"refused and unchanged at 0644: {diagnostic}"


def _case_overwrite_keeps_the_existing_mode(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm the overwrite option replaces a 0644 record and leaves its mode alone.

    The ambient umask is set to zero for the run, which is the setting under which a
    mode taken from the umask would be visible in the result, and the expected mode is
    the 0644 the replaced file carried rather than ``FILE_MODE``.
    """
    directory = _case_directory(scratch, "overwrite-existing")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = _written(directory, _SCRATCH_RECORD_NAME, b"PRE-EXISTING CONTENT\n")
    os.chmod(destination, 0o644)
    previous = os.umask(0o000)
    try:
        result = _run_cli(
            _extraction_argv(capture, destination, map_path, OVERWRITE_OPTION)
        )
    finally:
        os.umask(previous)
    _expect_cli_success(result, "the extraction over an existing record")
    _expect(
        f"{stat.S_IMODE(os.stat(destination).st_mode):04o}",
        "0644",
        "the mode of the replaced record",
    )
    _expect_record(_decoded_line(destination)[1], _MOTOR_RECORD, "the landed record")
    return "an existing 0644 record replaced at 0644"


def _case_overwrite_creates_at_the_private_mode(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm the overwrite option leaves a created record at the private mode."""
    directory = _case_directory(scratch, "overwrite-absent")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / _SCRATCH_RECORD_NAME
    previous = os.umask(0o000)
    try:
        result = _run_cli(
            _extraction_argv(capture, destination, map_path, OVERWRITE_OPTION)
        )
    finally:
        os.umask(previous)
    _expect_cli_success(result, "the extraction into an absent destination")
    _expect(
        f"{stat.S_IMODE(os.stat(destination).st_mode):04o}",
        f"{FILE_MODE:04o}",
        "the mode of the created record",
    )
    _expect_record(_decoded_line(destination)[1], _MOTOR_RECORD, "the landed record")
    return f"a created record carries {FILE_MODE:04o} with {OVERWRITE_OPTION} given"


def _case_generated_roots_accepted() -> str:
    """Confirm a destination below each generated root is accepted, creating nothing."""
    marker = f"extractor-selftest-{os.getpid()}"
    for relative in GENERATED_OUTPUT_ROOTS:
        candidate = REPOSITORY_ROOT / relative / marker / _SCRATCH_RECORD_NAME
        target = confine_destination(candidate)
        root = Path(os.path.realpath(REPOSITORY_ROOT / relative))
        if root not in target.parents:
            raise _SelfTestFailure(
                f"the destination below {relative} canonicalises to "
                f"{_path_shown(target)}, which does not stand below "
                f"{_path_shown(root)}"
            )
        if os.path.lexists(target) or os.path.lexists(candidate.parent):
            raise _SelfTestFailure(
                f"validating the destination below {relative} created "
                f"{_path_shown(candidate.parent)}"
            )
    return f"{len(GENERATED_OUTPUT_ROOTS)} generated roots accept a destination below"


def _case_out_of_tree_accepted(scratch: Path) -> str:
    """Confirm a destination outside the repository directory is accepted."""
    candidate = scratch / "out-of-tree" / _SCRATCH_RECORD_NAME
    target = confine_destination(candidate)
    repository = Path(os.path.realpath(REPOSITORY_ROOT))
    if _stands_inside(target, repository):
        raise _SelfTestFailure(
            f"the scratch destination {_path_shown(target)} stands inside "
            f"the repository directory {_path_shown(repository)}"
        )
    return f"{_path_shown(target)} accepted outside the repository"


def _case_authored_destination_refused(relative: str) -> str:
    """Confirm one authored in-tree path is refused as a destination."""
    candidate = REPOSITORY_ROOT / relative
    return _expect_raised(
        InputOutputError,
        EXIT_IO_ERROR,
        ["outside every generated root"],
        lambda: confine_destination(candidate),
        f"validating the authored destination {relative}",
    )


def _case_this_module_destination_refused(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm an extraction cannot replace this module, and does not modify it."""
    directory = _case_directory(scratch, "authored-destination")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = Path(__file__).resolve()
    before = _fingerprint(destination)
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    diagnostic = _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["outside every generated root", destination.name],
        "the extraction aimed at this module",
    )
    _expect_untouched(destination, before, "this module")
    return f"refused and unchanged: {diagnostic}"


def _case_committed_evidence_refused(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm no destination lands in the committed evidence directory.

    The destination stands inside modernization/validation/artifacts, the directory
    holding the committed harness evidence, and carries a name that does not exist
    there, so the case reads and writes no evidence file of that directory and depends
    on the content of none. It is validated directly and run through the command line
    with and without ``OVERWRITE_OPTION``; each attempt is refused for standing outside
    ``GENERATED_OUTPUT_ROOTS`` and creates nothing.
    """
    directory = _case_directory(scratch, "committed-evidence")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    evidence = REPOSITORY_ROOT / "modernization" / "validation" / "artifacts"
    destination = evidence / f"extractor-selftest-{os.getpid()}.json"
    diagnostic = _expect_raised(
        InputOutputError,
        EXIT_IO_ERROR,
        ["outside every generated root", destination.name],
        lambda: confine_destination(destination),
        "validating a destination inside the committed evidence directory",
    )
    for extra in ((), (OVERWRITE_OPTION,)):
        result = _run_cli(_extraction_argv(capture, destination, map_path, *extra))
        _expect_cli_failure(
            result,
            EXIT_IO_ERROR,
            ["outside every generated root", destination.name],
            f"the extraction aimed at the committed evidence directory "
            f"{'with' if extra else 'without'} {OVERWRITE_OPTION}",
        )
        if os.path.lexists(destination):
            raise _SelfTestFailure(
                f"the refused extraction created {_path_shown(destination)}"
            )
    return f"refused with and without {OVERWRITE_OPTION}: {diagnostic}"


def _case_read_only_source_refused() -> str:
    """Confirm a destination inside base/ is refused, and the source is unchanged."""
    destination = READ_ONLY_SOURCE_ROOT / "src" / "lgcmarea.cpy"
    before = _fingerprint(destination)
    diagnostic = _expect_raised(
        InputOutputError,
        EXIT_IO_ERROR,
        ["read-only source directory"],
        lambda: confine_destination(destination),
        "validating a destination inside the read-only source directory",
    )
    _expect_untouched(destination, before, "base/src/lgcmarea.cpy")
    return f"refused and unchanged: {diagnostic}"


def _case_symlink_alias_refused(scratch: Path) -> str:
    """Confirm a symbolic link into the repository cannot smuggle a destination in.

    The link stands in this run's scratch directory and names the authored directory
    holding this module; the destination it spells resolves onto this module, so the
    canonicalised path reaches the same refusal the module's own pathname reaches.
    """
    directory = _case_directory(scratch, "alias")
    alias = directory / "alias"
    alias.symlink_to(_THIS_DIR)
    victim = _THIS_DIR / Path(__file__).name
    before = _fingerprint(victim)
    candidate = alias / Path(__file__).name
    diagnostic = _expect_raised(
        InputOutputError,
        EXIT_IO_ERROR,
        ["outside every generated root"],
        lambda: confine_destination(candidate),
        "validating a destination spelled through a symbolic-link alias",
    )
    _expect_untouched(victim, before, "the module the alias names")
    return f"refused and unchanged: {diagnostic}"


def _case_final_symlink_refused(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm a destination whose final component is a symbolic link is refused."""
    directory = _case_directory(scratch, "final-link")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    victim = _written(directory, "victim.json", b"untouched\n")
    link = directory / "link.json"
    link.symlink_to(victim)
    before = _fingerprint(victim)
    result = _run_cli(_extraction_argv(capture, link, map_path))
    diagnostic = _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["the destination is a symbolic link"],
        "the extraction aimed at a symbolic link",
    )
    _expect_untouched(victim, before, "the file the link names")
    return f"refused and unchanged: {diagnostic}"


def _case_existing_directory_refused(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm a destination that is an existing directory is refused."""
    directory = _case_directory(scratch, "existing-directory")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / _SCRATCH_RECORD_NAME
    destination.mkdir(mode=DIRECTORY_MODE)
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    return _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["exists and is not a regular file"],
        "the extraction aimed at an existing directory",
    )


def _case_parent_is_a_file_refused(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm a destination whose parent is a regular file is refused."""
    directory = _case_directory(scratch, "parent-file")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    blocking = _written(directory, "blocking", b"not a directory\n")
    destination = blocking / _SCRATCH_RECORD_NAME
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    return _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["the destination cannot be examined"],
        "the extraction aimed below a regular file",
    )


def _case_destination_names_no_file_refused() -> str:
    """Confirm a destination naming a filesystem root, and no file, is refused."""
    return _expect_raised(
        InputOutputError,
        EXIT_IO_ERROR,
        ["names no file"],
        lambda: confine_destination(Path(os.sep)),
        "validating a destination that names the filesystem root",
    )


def _case_removed_parent_recreated(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm a destination directory removed before the write is created again."""
    directory = _case_directory(scratch, "removed-parent")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    parent = directory / "landed"
    parent.mkdir(mode=DIRECTORY_MODE)
    parent.rmdir()
    destination = parent / _SCRATCH_RECORD_NAME
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    _expect_cli_success(result, "the extraction into a removed directory")
    _expect_record(_decoded_line(destination)[1], _MOTOR_RECORD, "the landed record")
    return "the removed directory was created again and the record landed"


def _temporary_candidates(directory: Path, name: str) -> list[Path]:
    """Return the temporary entries the write tries beside a destination, in order."""
    return [
        directory / f".{name}.{os.getpid()}.{attempt}.tmp"
        for attempt in range(MAX_TEMPORARY_ATTEMPTS)
    ]


def _case_temporary_collision_retried(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm an occupied first temporary name is stepped over rather than followed."""
    directory = _case_directory(scratch, "temporary-collision")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / _SCRATCH_RECORD_NAME
    occupied = _temporary_candidates(directory, _SCRATCH_RECORD_NAME)[0]
    occupied.mkdir(mode=DIRECTORY_MODE)
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    _expect_cli_success(result, "the extraction past an occupied temporary name")
    _expect_record(_decoded_line(destination)[1], _MOTOR_RECORD, "the landed record")
    if not occupied.is_dir():
        raise _SelfTestFailure(
            f"the occupied temporary name {_path_shown(occupied)} was replaced"
        )
    return "the first temporary name was left in place and the record landed"


def _case_temporary_candidates_exhausted(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm the write is refused when every temporary name is occupied."""
    directory = _case_directory(scratch, "temporary-exhausted")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / _SCRATCH_RECORD_NAME
    for candidate in _temporary_candidates(directory, _SCRATCH_RECORD_NAME):
        candidate.mkdir(mode=DIRECTORY_MODE)
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    diagnostic = _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["no temporary entry could be created"],
        "the extraction with every temporary name occupied",
    )
    if os.path.lexists(destination):
        raise _SelfTestFailure(
            f"the refused write created {_path_shown(destination)}"
        )
    return f"refused after {MAX_TEMPORARY_ATTEMPTS} attempts: {diagnostic}"


def _case_temporary_entry_refused(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm a directory that refuses the temporary entry refuses the write.

    The destination name is long enough that the temporary name beside it exceeds the
    length the directory accepts, which is the failure of the temporary open a directory
    refusing the creation raises. Nothing is landed and nothing is left behind.
    """
    directory = _case_directory(scratch, "temporary-refused")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / ("L" * 250)
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    diagnostic = _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["cannot be written through a temporary entry"],
        "the extraction into a directory refusing the temporary entry",
    )
    if os.path.lexists(destination):
        raise _SelfTestFailure(
            f"the refused write created {_path_shown(destination)}"
        )
    remaining = sorted(entry.name for entry in directory.iterdir())
    if remaining != [capture.name]:
        raise _SelfTestFailure(
            f"the refused write left {_quote_all(remaining)} in the case directory, "
            f"expected the capture {_shown(capture.name)} alone"
        )
    return f"refused before anything was created: {diagnostic}"


# ---------------------------------------------------------------------------
# Self-test cases: summary, return-code refusal and command line
# ---------------------------------------------------------------------------


def _case_summary_redacted(scratch: Path, map_path: Path, field_map: FieldMap) -> str:
    """Confirm the default summary names no business identifier."""
    directory = _case_directory(scratch, "summary-redacted")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / _SCRATCH_RECORD_NAME
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    summary = _expect_cli_success(result, "the extraction summarised by default")
    for fragment in (
        f"{LANDING_SOURCE_SYSTEM_KEY}={DEFAULT_SOURCE_SYSTEM_KEY} "
        "from --source-system-key",
        f"{LANDING_POLICY_TYPE}=M",
        "keys=17",
        "identifiers=redacted",
    ):
        _expect_holds(summary, fragment, "the default summary line")
    for fragment in (
        *IDENTIFIER_FIELDS,
        str(_MOTOR_RECORD[LANDING_POLICY_NUMBER]),
        str(_MOTOR_RECORD[LANDING_BROKERS_REFERENCE]),
    ):
        _expect_lacks(summary, fragment, "the default summary line")
    return f"summary carries no identifier: {_escaped(summary, 96)}"


def _case_summary_identifiers(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm --show-identifiers restores the identifier line."""
    directory = _case_directory(scratch, "summary-identifiers")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / _SCRATCH_RECORD_NAME
    result = _run_cli(
        _extraction_argv(capture, destination, map_path, "--show-identifiers")
    )
    summary = _expect_cli_success(result, "the extraction summarised with identifiers")
    for name in (
        LANDING_REQUEST_ID,
        LANDING_POLICY_TYPE,
        LANDING_POLICY_NUMBER,
        LANDING_CUSTOMER_NUMBER,
        LANDING_BROKER_ID,
        LANDING_BROKERS_REFERENCE,
        LANDING_RETURN_CODE,
    ):
        _expect_holds(
            summary, f"{name}={_MOTOR_RECORD[name]}", "the identifier summary line"
        )
    _expect_holds(
        summary,
        f"{LANDING_SOURCE_SYSTEM_KEY}={DEFAULT_SOURCE_SYSTEM_KEY} "
        "from --source-system-key",
        "the identifier summary line",
    )
    return f"summary carries seven named values: {_escaped(summary, 96)}"


def _case_summary_environment(
    scratch: Path,
    map_path: Path,
    field_map: FieldMap,
    carried: str,
    enabling: bool,
    label: str,
) -> str:
    """Confirm the environment variable selects the same summary line as the option.

    ``carried`` is the value ``SHOW_IDENTIFIERS_VARIABLE`` holds for the run. An
    enabling value must yield the identifier line the option yields, naming all seven
    values; any other value must yield the redacted line, which names the digest of the
    policy number and no identifier at all. The landed record is checked in both cases,
    so the summary line is the only thing the setting changes. The variable and the
    resolved setting are restored before the case returns.
    """
    directory = _case_directory(scratch, f"summary-environment-{label}")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    destination = directory / _SCRATCH_RECORD_NAME
    previous_value = os.environ.get(SHOW_IDENTIFIERS_VARIABLE)
    previous_setting = show_identifiers_enabled()
    try:
        os.environ[SHOW_IDENTIFIERS_VARIABLE] = carried
        result = _run_cli(_extraction_argv(capture, destination, map_path))
    finally:
        if previous_value is None:
            os.environ.pop(SHOW_IDENTIFIERS_VARIABLE, None)
        else:
            os.environ[SHOW_IDENTIFIERS_VARIABLE] = previous_value
        set_show_identifiers(previous_setting)
    summary = _expect_cli_success(
        result,
        f"the extraction run with {SHOW_IDENTIFIERS_VARIABLE} carrying "
        f"{_shown(carried)}",
    )
    named = (
        LANDING_REQUEST_ID,
        LANDING_POLICY_TYPE,
        LANDING_POLICY_NUMBER,
        LANDING_CUSTOMER_NUMBER,
        LANDING_BROKER_ID,
        LANDING_BROKERS_REFERENCE,
        LANDING_RETURN_CODE,
    )
    if enabling:
        for name in named:
            _expect_holds(
                summary,
                f"{name}={_MOTOR_RECORD[name]}",
                f"the summary line under {SHOW_IDENTIFIERS_VARIABLE}",
            )
        _expect_lacks(
            summary,
            "identifiers=redacted",
            f"the summary line under {SHOW_IDENTIFIERS_VARIABLE}",
        )
    else:
        for fragment in ("identifiers=redacted", IDENTIFIER_DIGEST_PREFIX):
            _expect_holds(
                summary,
                fragment,
                f"the summary line under {SHOW_IDENTIFIERS_VARIABLE}",
            )
        for fragment in (
            *IDENTIFIER_FIELDS,
            str(_MOTOR_RECORD[LANDING_POLICY_NUMBER]),
            str(_MOTOR_RECORD[LANDING_BROKERS_REFERENCE]),
        ):
            _expect_lacks(
                summary,
                fragment,
                f"the summary line under {SHOW_IDENTIFIERS_VARIABLE}",
            )
    _expect_record(_decoded_line(destination)[1], _MOTOR_RECORD, "the landed record")
    return (
        f"{SHOW_IDENTIFIERS_VARIABLE}={_shown(carried)} "
        f"{'names' if enabling else 'withholds'} the identifiers: "
        f"{_escaped(summary, 96)}"
    )


def _case_summary_redacted_line_carries_no_identifier() -> str:
    """Confirm the redacted summary line carries a digest under either resolution.

    ``summarise`` is called with display withheld while the resolved setting is first
    withheld and then enabled, and the line must carry the digest of the policy number
    and neither the number itself nor any other identifier in both runs. The setting is
    restored before the case returns.
    """
    destination = Path(_SCRATCH_RECORD_NAME)
    policy_number = str(_MOTOR_RECORD[LANDING_POLICY_NUMBER])
    previous = show_identifiers_enabled()
    try:
        for resolved in (False, True):
            set_show_identifiers(resolved)
            line = summarise(
                destination,
                _MOTOR_RECORD,
                source_system_key_origin="the built-in default",
                show_identifiers=False,
            )
            what = f"the redacted summary line with the setting {resolved}"
            for fragment in (
                "identifiers=redacted",
                f"policy_digest={_digest(policy_number)}",
            ):
                _expect_holds(line, fragment, what)
            for fragment in (
                *IDENTIFIER_FIELDS,
                policy_number,
                str(_MOTOR_RECORD[LANDING_BROKERS_REFERENCE]),
            ):
                _expect_lacks(line, fragment, what)
        set_show_identifiers(False)
        named = summarise(
            destination,
            _MOTOR_RECORD,
            source_system_key_origin="the built-in default",
            show_identifiers=True,
        )
        _expect_holds(
            named,
            f"{LANDING_POLICY_NUMBER}={policy_number}",
            "the identifier summary line with the setting False",
        )
    finally:
        set_show_identifiers(previous)
    return (
        f"the redacted line carries {_digest(policy_number)} under either resolution "
        "and the identifier line carries the values"
    )


def _case_cli_control_character_refused(
    scratch: Path, map_path: Path, field_map: FieldMap, character: str
) -> str:
    """Confirm a control character in a capture lands nothing at the command line."""
    escaped = _escaped_character(character)
    directory = _case_directory(scratch, f"control-character-{escaped}")
    capture = _prepared_capture(
        directory,
        field_map,
        {**_MOTOR_WINDOWS, LANDING_BROKERS_REFERENCE: f"AB{character}CD"},
    )
    destination = directory / _SCRATCH_RECORD_NAME
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    diagnostic = _expect_cli_failure(
        result,
        EXIT_RECORD_REJECTED,
        ["CA-BROKERSREF", "carries a control character", _shown(
            LANDING_BROKERS_REFERENCE)],
        f"the extraction of a capture carrying {_shown(escaped)}",
    )
    _expect_lacks(diagnostic, character, "the command line diagnostic")
    if os.path.lexists(destination):
        raise _SelfTestFailure(
            f"the refused extraction created {_path_shown(destination)}"
        )
    return f"status {EXIT_RECORD_REJECTED}, nothing written: {diagnostic}"


def _case_cli_blank_broker_id_lands_null(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm a blank broker-id window lands null and every other key is unchanged."""
    directory = _case_directory(scratch, "blank-broker-id")
    capture = _prepared_capture(
        directory, field_map, {**_MOTOR_WINDOWS, LANDING_BROKER_ID: ""}
    )
    destination = directory / _SCRATCH_RECORD_NAME
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    summary = _expect_cli_success(
        result, "the extraction of a capture whose broker-id window is blank"
    )
    text, parsed = _decoded_line(destination)
    _expect_record(
        parsed, {**_MOTOR_RECORD, LANDING_BROKER_ID: None}, "the landed record"
    )
    _expect_holds(text, f'"{LANDING_BROKER_ID}": null', "the landed line")
    _expect_holds(summary, "nulls=5", "the summary line")
    return (
        f"{len(parsed)} keys landed, {LANDING_BROKER_ID} null, in {len(text)} "
        "characters"
    )


def _case_cli_blank_amount_window_refused(
    scratch: Path, map_path: Path, field_map: FieldMap, name: str, item: str
) -> str:
    """Confirm a blank applicable amount window lands nothing at the command line."""
    directory = _case_directory(scratch, f"blank-amount-{name}")
    capture = _prepared_capture(directory, field_map, {**_MOTOR_WINDOWS, name: ""})
    destination = directory / _SCRATCH_RECORD_NAME
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    diagnostic = _expect_cli_failure(
        result,
        EXIT_RECORD_REJECTED,
        [item, "not all digits"],
        f"the extraction of a capture whose {name} window is blank",
    )
    if os.path.lexists(destination):
        raise _SelfTestFailure(
            f"the refused extraction created {_path_shown(destination)}"
        )
    return f"status {EXIT_RECORD_REJECTED}, nothing written: {diagnostic}"


def _case_environment_guard() -> str:
    """Confirm the environment check accepts this run and refuses the others.

    The interpreter running the matrix carries the pinned series and the pinned version
    of every distribution named, so the unpatched check returns without writing. Each
    refusal is then observed with the pinned values replaced for the duration of one
    call: another series, a distribution that is not installed and a distribution at
    another version each end the run with ``EXIT_ENVIRONMENT_REJECTED`` and one line
    naming what was found, the pin and the interpreter to run this tool through.
    """
    _expect(confirm_pinned_environment(), None, "the check of a pinned environment")
    observed: list[str] = []
    for what, series, distributions, expected in (
        (
            "another interpreter series",
            (sys.version_info[0], sys.version_info[1] + 1),
            PINNED_DISTRIBUTIONS,
            "series, and the interpreter running it is Python",
        ),
        (
            "a distribution that is not installed",
            PINNED_PYTHON_SERIES,
            (("genapp-rqi-absent-distribution", "1.0.0"),),
            "is not installed for the interpreter at",
        ),
        (
            "a distribution at another version",
            PINNED_PYTHON_SERIES,
            (("PyYAML", "0.0.1"),),
            "pins PyYAML 0.0.1; run this tool through",
        ),
    ):
        original_series = globals()["PINNED_PYTHON_SERIES"]
        original_distributions = globals()["PINNED_DISTRIBUTIONS"]
        globals()["PINNED_PYTHON_SERIES"] = series
        globals()["PINNED_DISTRIBUTIONS"] = distributions
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured):
                try:
                    confirm_pinned_environment()
                except SystemExit as request:
                    status = request.code
                else:
                    status = None
        finally:
            globals()["PINNED_PYTHON_SERIES"] = original_series
            globals()["PINNED_DISTRIBUTIONS"] = original_distributions
        _expect(status, EXIT_ENVIRONMENT_REJECTED, f"the status of {what}")
        lines = [line for line in captured.getvalue().splitlines() if line]
        _expect(len(lines), 1, f"the lines reported for {what}")
        line = lines[0]
        if not line.startswith(f"{_PROGRAM}: ") or expected not in line:
            raise _SelfTestFailure(
                f"the line reported for {what} is {_shown(line, 200)}"
            )
        if line != _one_line(line):
            raise _SelfTestFailure(f"the line reported for {what} is not one line")
        observed.append(what)
    return (
        f"the pinned environment accepted, {len(observed)} environments refused with "
        f"status {EXIT_ENVIRONMENT_REJECTED}"
    )


def _case_summary_names_the_key_origin(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm the summary names the source-system key and each origin it comes from.

    The option is omitted for both runs, so the resolution the summary reports is the
    one the environment and then the built-in default supply; the landed record is read
    back each time to confirm the line names the key the record carries.
    """
    directory = _case_directory(scratch, "summary-key-origin")
    capture = _prepared_capture(directory, field_map, _MOTOR_WINDOWS)
    previous = os.environ.get(SOURCE_SYSTEM_KEY_VARIABLE)
    observed: list[str] = []
    try:
        for value, origin, name in (
            (
                "FROM_ENVIRONMENT",
                f"the {SOURCE_SYSTEM_KEY_VARIABLE} environment variable",
                "environment.json",
            ),
            (None, "the built-in default", "default.json"),
        ):
            if value is None:
                os.environ.pop(SOURCE_SYSTEM_KEY_VARIABLE, None)
            else:
                os.environ[SOURCE_SYSTEM_KEY_VARIABLE] = value
            destination = directory / name
            result = _run_cli(
                [
                    "--commarea",
                    str(capture),
                    "--output",
                    str(destination),
                    "--field-map",
                    str(map_path),
                ]
            )
            summary = _expect_cli_success(
                result, f"the extraction summarised with the key from {origin}"
            )
            landed = value if value is not None else DEFAULT_SOURCE_SYSTEM_KEY
            _expect_holds(
                summary,
                f"{LANDING_SOURCE_SYSTEM_KEY}={landed} from {origin}",
                "the summary line",
            )
            _expect(
                _decoded_line(destination)[1][LANDING_SOURCE_SYSTEM_KEY],
                landed,
                f"the {LANDING_SOURCE_SYSTEM_KEY} of the record landed from {origin}",
            )
            observed.append(origin)
    finally:
        if previous is None:
            os.environ.pop(SOURCE_SYSTEM_KEY_VARIABLE, None)
        else:
            os.environ[SOURCE_SYSTEM_KEY_VARIABLE] = previous
    return f"the summary named the key from {_quote_all(observed)}"


def _case_cli_return_code_refused(
    scratch: Path, map_path: Path, field_map: FieldMap, code: str
) -> str:
    """Confirm the command line refuses an unsuccessful capture and writes nothing."""
    directory = _case_directory(scratch, f"return-code-{code}")
    capture = _prepared_capture(
        directory, field_map, {**_MOTOR_WINDOWS, LANDING_RETURN_CODE: code}
    )
    destination = directory / _SCRATCH_RECORD_NAME
    result = _run_cli(_extraction_argv(capture, destination, map_path))
    diagnostic = _expect_cli_failure(
        result,
        EXIT_CHAIN_NOT_SUCCESSFUL,
        [f"'{code}'", field_map.return_code_meanings[code]],
        f"the extraction of a capture whose return code is {code}",
    )
    if os.path.lexists(destination):
        raise _SelfTestFailure(
            f"the refused extraction created {_path_shown(destination)}"
        )
    return f"status {EXIT_CHAIN_NOT_SUCCESSFUL}, nothing written: {diagnostic}"


def _case_cli_self_test_rejects_extraction_arguments(scratch: Path) -> str:
    """Confirm --self-test accepts neither --commarea nor --output."""
    destination = scratch / "never-written.json"
    result = _run_cli(["--self-test", "--output", str(destination)])
    diagnostic = _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["--self-test accepts neither --commarea nor --output"],
        "a self-test command line naming an output",
    )
    if os.path.lexists(destination):
        raise _SelfTestFailure("the rejected command line created its output")
    return diagnostic


def _case_cli_requires_capture_and_output(map_path: Path) -> str:
    """Confirm an extraction command line without a capture or output is rejected."""
    result = _run_cli(["--field-map", str(map_path)])
    return _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["--commarea and --output are required unless --self-test is given"],
        "a command line naming neither a capture nor an output",
    )


def _case_cli_rejects_withdrawn_option(
    scratch: Path, map_path: Path, field_map: FieldMap
) -> str:
    """Confirm the withdrawn failure-landing option is no longer accepted."""
    directory = _case_directory(scratch, "withdrawn-option")
    capture = _prepared_capture(
        directory, field_map, {**_MOTOR_WINDOWS, LANDING_RETURN_CODE: "90"}
    )
    destination = directory / _SCRATCH_RECORD_NAME
    result = _run_cli(
        _extraction_argv(
            capture, destination, map_path, "--allow-nonzero-return-code"
        )
    )
    diagnostic = _expect_cli_failure(
        result,
        EXIT_IO_ERROR,
        ["command line rejected", "allow-nonzero-return-code"],
        "a command line asking to land a failure record",
    )
    if os.path.lexists(destination):
        raise _SelfTestFailure("the rejected command line created its output")
    return diagnostic


def _case_source_system_key(
    supplied: str | None, expected: str, expected_origin: str, what: str
) -> str:
    """Confirm one accepted source-system key resolves to the value and the origin."""
    resolved = resolve_source_system_key(supplied)
    _expect(resolved.value, expected, f"the key from {what}")
    _expect(resolved.origin, expected_origin, f"the origin of the key from {what}")
    return f"{what} resolved to {_shown(expected)} from {expected_origin}"


def _case_source_system_key_refused(
    supplied: str, fragments: Sequence[str], what: str
) -> str:
    """Confirm one rejected source-system key is refused as a usage error."""
    return _expect_raised(
        UsageError,
        EXIT_IO_ERROR,
        fragments,
        lambda: resolve_source_system_key(supplied),
        f"resolving {what}",
    )


def _case_source_system_key_from_environment() -> str:
    """Confirm an omitted option reads the environment, then the built-in default.

    Each resolution is checked with the origin it reports, which is the wording the
    summary line carries beside the key.
    """
    previous = os.environ.get(SOURCE_SYSTEM_KEY_VARIABLE)
    try:
        os.environ[SOURCE_SYSTEM_KEY_VARIABLE] = "FROM_ENVIRONMENT"
        _expect(
            resolve_source_system_key(None),
            ResolvedSourceSystemKey(
                "FROM_ENVIRONMENT",
                f"the {SOURCE_SYSTEM_KEY_VARIABLE} environment variable",
            ),
            "the key taken from the environment",
        )
        del os.environ[SOURCE_SYSTEM_KEY_VARIABLE]
        _expect(
            resolve_source_system_key(None),
            ResolvedSourceSystemKey(DEFAULT_SOURCE_SYSTEM_KEY, "the built-in default"),
            "the key taken from the built-in default",
        )
    finally:
        if previous is None:
            os.environ.pop(SOURCE_SYSTEM_KEY_VARIABLE, None)
        else:
            os.environ[SOURCE_SYSTEM_KEY_VARIABLE] = previous
    return (
        f"the {SOURCE_SYSTEM_KEY_VARIABLE} variable is read first and "
        f"{_shown(DEFAULT_SOURCE_SYSTEM_KEY)} last"
    )


def _case_scratch_removed(scratch: Path) -> str:
    """Confirm the private scratch directory of this run no longer exists."""
    if os.path.lexists(scratch):
        raise _SelfTestFailure(
            f"the self-test scratch directory {_path_shown(scratch)} was left behind"
        )
    return f"{_path_shown(scratch)} removed"


# ---------------------------------------------------------------------------
# Self-test runner
# ---------------------------------------------------------------------------


def _run_case(
    results: list[_CaseResult],
    stream: Any,
    name: str,
    case: Callable[[], str],
) -> None:
    """Run one case, record its outcome and write one line naming it to ``stream``."""
    try:
        detail = case()
    except _SelfTestFailure as failure:
        result = _CaseResult(name=name, passed=False, detail=str(failure))
    except ExtractError as error:
        result = _CaseResult(
            name=name, passed=False, detail=f"{_type_name(error)}: {error}"
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
            detail=f"unexpected {_type_name(error)}: {_display(error)}",
        )
    else:
        result = _CaseResult(name=name, passed=True, detail=detail)
    results.append(result)
    verdict = "PASS" if result.passed else "FAIL"
    print(f"self-test {verdict} {result.name} -- {_one_line(result.detail)}",
          file=stream)


def _field_map_cases(
    results: list[_CaseResult],
    out: Any,
    field_map: FieldMap,
    map_text: str,
    directory: Path,
) -> None:
    """Run the field-map cases: the real map, and every contradiction it can carry."""
    _run_case(results, out, "field_map_members", lambda: _case_field_map_members(
        field_map))
    _run_case(
        results, out, "field_map_return_code_meanings",
        lambda: _case_return_code_meanings(field_map),
    )
    refusals: tuple[tuple[str, Callable[[Any], None], tuple[str, ...]], ...] = (
        (
            "missing_record_section",
            lambda document: document.pop("record"),
            ("the field map is missing 'record'",),
        ),
        (
            "missing_landing_section",
            lambda document: document.pop("landing"),
            ("the field map is missing 'landing'",),
        ),
        (
            "missing_return_codes_section",
            lambda document: document.pop("return_codes"),
            ("the field map is missing 'return_codes'",),
        ),
        (
            "record_length_changed",
            lambda document: document["record"].update({"length": 32499}),
            ("records 'record.length' as 32499", "32500 is required"),
        ),
        (
            "offset_past_record",
            lambda document: document["layout"]["header"]["items"][0].update(
                {"offset": 32499}
            ),
            ("past the 32500-character record",),
        ),
        (
            "length_below_one",
            lambda document: document["layout"]["header"]["items"][0].update(
                {"length": 0}
            ),
            ("an integer of at least 1 is required",),
        ),
        (
            "kind_unknown",
            lambda document: document["layout"]["header"]["items"][0].update(
                {"kind": "packed_decimal"}
            ),
            ("'packed_decimal'", "is required"),
        ),
        (
            "pic_empty",
            lambda document: _field_entry(document, LANDING_POLICY_NUMBER)[
                "commarea"
            ].update({"pic": ""}),
            ("commarea.pic", "a non-empty string is required"),
        ),
        (
            "window_disagrees_with_layout",
            lambda document: _field_entry(document, LANDING_POLICY_NUMBER)[
                "commarea"
            ].update({"offset": 20}),
            ("under 'layout'",),
        ),
        (
            "landing_key_recorded_twice",
            lambda document: document["fields"].append(
                copy.deepcopy(_field_entry(document, LANDING_REQUEST_ID))
            ),
            ("on two entries",),
        ),
        (
            "landing_order_carries_unknown_key",
            lambda document: document["landing"]["field_order"].append("extra_key"),
            ("does not match its recorded landing keys", "extra_key"),
        ),
        (
            "landing_order_repeats_a_key",
            lambda document: document["landing"]["field_order"].append(
                LANDING_POLICY_NUMBER
            ),
            ("repeats", LANDING_POLICY_NUMBER),
        ),
        (
            "nullability_contradicts_applicability",
            lambda document: document["product_premium_nullability"][
                "by_policy_type"
            ]["E"].update(
                {
                    "populated": ["motor_premium_amount"],
                    "null_fields": [
                        "fire_premium_amount",
                        "crime_premium_amount",
                        "flood_premium_amount",
                        "weather_premium_amount",
                    ],
                }
            ),
            ("motor_premium_amount", "inapplicable to policy type 'E'"),
        ),
        (
            "zero_substitution_permitted",
            lambda document: document["product_premium_nullability"].update(
                {"zero_substitution_permitted": True}
            ),
            ("zero_substitution_permitted", "false is required"),
        ),
        (
            "inapplicable_value_not_null",
            lambda document: document["product_premium_nullability"].update(
                {"inapplicable_value": 0}
            ),
            ("inapplicable_value", "null is required"),
        ),
        (
            "return_code_domain_without_success",
            lambda document: _field_entry(document, LANDING_RETURN_CODE).update(
                {"domain": ["70", "80", "90", "98", "99"]}
            ),
            ("omits '00'",),
        ),
        (
            "return_code_meaning_absent",
            lambda document: document["return_codes"]["80"].pop("meaning"),
            ("return_codes.80.meaning",),
        ),
        (
            "return_codes_do_not_cover_the_domain",
            lambda document: document["return_codes"].pop("99"),
            ("does not cover the recorded domain", "'99'"),
        ),
        (
            "landing_key_sourced_from_excluded_item",
            lambda document: _field_entry(document, "fire_premium_amount")[
                "commarea"
            ].update({"item": "CA-B-FirePeril", "offset": 896, "length": 4}),
            ("under 'excluded'",),
        ),
        (
            "source_system_run_value_changed",
            lambda document: document[LANDING_SOURCE_SYSTEM_KEY].update(
                {"run_value": "OTHER_SYSTEM"}
            ),
            ("run_value", DEFAULT_SOURCE_SYSTEM_KEY),
        ),
        (
            "source_system_runtime_status_changed",
            lambda document: document[LANDING_SOURCE_SYSTEM_KEY].update(
                {"runtime_status": "active"}
            ),
            ("runtime_status", RUNTIME_STATUS_WAREHOUSE_ASSIGNED),
        ),
        (
            "policy_type_read_from_the_record",
            lambda document: _field_entry(document, LANDING_POLICY_TYPE).update(
                {
                    "commarea": {
                        "item": "CA-REQUEST-ID",
                        "copybook": "base/src/lgcmarea.cpy",
                        "line": 10,
                        "pic": "X(6)",
                        "offset": 1,
                        "length": 6,
                    }
                }
            ),
            ("is derived from the request id",),
        ),
        (
            "blank_window_rule_is_not_a_boolean",
            lambda document: _field_entry(document, LANDING_BROKER_ID).update(
                {"blank_window_lands_null": "yes"}
            ),
            (
                "blank_window_lands_null",
                "true, false or no member at all is required",
            ),
        ),
        (
            "blank_window_rule_without_a_window",
            lambda document: _field_entry(document, LANDING_POLICY_TYPE).update(
                {"blank_window_lands_null": True}
            ),
            ("blank_window_lands_null", "no window to find blank"),
        ),
        (
            "blank_window_rule_on_a_chain_assigned_key",
            lambda document: _field_entry(document, LANDING_LAST_CHANGED).update(
                {"blank_window_lands_null": True}
            ),
            ("blank_window_lands_null", f"as {_shown(POPULATED_BY_CHAIN)}"),
        ),
        (
            "blank_window_rule_on_an_amount",
            lambda document: _field_entry(document, "payment_amount").update(
                {"blank_window_lands_null": True}
            ),
            ("blank_window_lands_null", "blank window is refused rather than landed"),
        ),
        (
            "blank_window_rule_with_a_target_that_is_not_nullable",
            lambda document: _field_entry(document, LANDING_BROKER_ID)["targets"][
                0
            ].update({"nullable": False}),
            ("blank_window_lands_null", "feeds a nullable column alone"),
        ),
    )
    for name, mutate, fragments in refusals:
        _run_case(
            results,
            out,
            f"field_map_{name}_refused",
            lambda name=name, mutate=mutate, fragments=fragments: _case_map_refused(
                directory, map_text, name, mutate, fragments
            ),
        )
    documents: tuple[
        tuple[str, bytes, type[ExtractError], int, tuple[str, ...]], ...
    ] = (
        (
            "duplicate_key_at_the_root",
            (map_text + "\nrecord:\n  length: 32500\n").encode("utf-8"),
            FieldMapError,
            EXIT_FIELD_MAP_INVALID,
            ("cannot be parsed", "duplicate key"),
        ),
        (
            "duplicate_nested_key",
            map_text.replace(
                "  name: DFHCOMMAREA", "  name: DFHCOMMAREA\n  name: DFHCOMMAREA", 1
            ).encode("utf-8"),
            FieldMapError,
            EXIT_FIELD_MAP_INVALID,
            ("cannot be parsed", "duplicate key 'name'"),
        ),
        (
            "not_a_mapping",
            b"- one\n- two\n",
            FieldMapError,
            EXIT_FIELD_MAP_INVALID,
            ("a mapping is required",),
        ),
        (
            "not_utf8_text",
            b"\xffrecord:\n  length: 32500\n",
            InputOutputError,
            EXIT_IO_ERROR,
            ("is not UTF-8 text",),
        ),
        (
            "above_the_byte_limit",
            b" " * (MAX_FIELD_MAP_BYTES + 1),
            InputOutputError,
            EXIT_IO_ERROR,
            (f"holds more than {MAX_FIELD_MAP_BYTES} bytes",),
        ),
    )
    for name, payload, kind, status, fragments in documents:
        _run_case(
            results,
            out,
            f"field_map_{name}_refused",
            lambda name=name, payload=payload, kind=kind, status=status,
            fragments=fragments: _case_map_bytes_refused(
                directory, name, payload, kind, status, fragments
            ),
        )
    _run_case(
        results, out, "field_map_missing_file_refused",
        lambda: _case_map_missing_refused(directory),
    )


def _capture_cases(
    results: list[_CaseResult],
    out: Any,
    field_map: FieldMap,
    directory: Path,
) -> None:
    """Run the capture-reading cases at, below and above the declared record."""
    record = _rendered_record(field_map, _MOTOR_WINDOWS)
    accepted: tuple[tuple[str, bytes], ...] = (
        ("exact_length", record.encode(CAPTURE_ENCODING)),
        ("one_line_feed", (record + "\n").encode(CAPTURE_ENCODING)),
        ("one_carriage_return_line_feed", (record + "\r\n").encode(CAPTURE_ENCODING)),
    )
    for name, payload in accepted:
        _run_case(
            results,
            out,
            f"capture_{name}_accepted",
            lambda name=name, payload=payload: _case_capture_accepted(
                directory, f"{name}.dat", payload, field_map
            ),
        )
    refused: tuple[tuple[str, bytes, type[ExtractError], int, tuple[str, ...]], ...] = (
        (
            "short_by_one",
            record[:-1].encode(CAPTURE_ENCODING),
            RecordError,
            EXIT_RECORD_REJECTED,
            ("holds 32499 characters", "exactly 32500 characters are required"),
        ),
        (
            "long_by_one",
            (record + "X").encode(CAPTURE_ENCODING),
            RecordError,
            EXIT_RECORD_REJECTED,
            ("holds 32501 characters",),
        ),
        (
            "two_line_endings",
            (record + "\n\n").encode(CAPTURE_ENCODING),
            RecordError,
            EXIT_RECORD_REJECTED,
            ("holds 32501 characters",),
        ),
        (
            "non_ascii_byte",
            record[:-1].encode(CAPTURE_ENCODING) + b"\xff",
            RecordError,
            EXIT_RECORD_REJECTED,
            (f"is not {CAPTURE_ENCODING} text",),
        ),
        (
            "above_the_byte_limit",
            b"0" * (MAX_CAPTURE_BYTES + 1),
            InputOutputError,
            EXIT_IO_ERROR,
            (f"holds more than {MAX_CAPTURE_BYTES} bytes",),
        ),
    )
    for name, payload, kind, status, fragments in refused:
        _run_case(
            results,
            out,
            f"capture_{name}_refused",
            lambda name=name, payload=payload, kind=kind, status=status,
            fragments=fragments: _case_capture_refused(
                directory, f"{name}.dat", payload, kind, status, fragments, field_map
            ),
        )
    _run_case(
        results, out, "capture_directory_refused",
        lambda: _case_capture_directory_refused(directory, field_map),
    )
    _run_case(
        results, out, "capture_missing_file_refused",
        lambda: _case_capture_missing_refused(directory, field_map),
    )


def _record_cases(results: list[_CaseResult], out: Any, field_map: FieldMap) -> None:
    """Run the decoding, routing, return-code, calendar and serialisation cases."""
    inactive_commercial = {
        name: _INACTIVE_OVERLAY_TEXT
        for name in (
            "fire_premium_amount",
            "crime_premium_amount",
            "flood_premium_amount",
            "weather_premium_amount",
        )
    }
    endowment_windows = {
        name: value
        for name, value in _MOTOR_WINDOWS.items()
        if name != "motor_premium_amount"
    }
    endowment_record = {
        **_MOTOR_RECORD,
        LANDING_REQUEST_ID: "01AEND",
        LANDING_POLICY_TYPE: "E",
        "motor_premium_amount": None,
    }
    landed: tuple[tuple[str, Mapping[str, str], Mapping[str, str | None]], ...] = (
        ("motor", _MOTOR_WINDOWS, _MOTOR_RECORD),
        ("commercial", _COMMERCIAL_WINDOWS, _COMMERCIAL_RECORD),
        (
            "motor_over_filled_commercial_windows",
            {**_MOTOR_WINDOWS, **inactive_commercial},
            _MOTOR_RECORD,
        ),
        (
            "commercial_over_filled_motor_window",
            {**_COMMERCIAL_WINDOWS, "motor_premium_amount": "MODEL1"},
            _COMMERCIAL_RECORD,
        ),
        (
            "endowment",
            {**endowment_windows, LANDING_REQUEST_ID: "01AEND"},
            endowment_record,
        ),
        (
            "house",
            {**endowment_windows, LANDING_REQUEST_ID: "01AHOU"},
            {
                **endowment_record,
                LANDING_REQUEST_ID: "01AHOU",
                LANDING_POLICY_TYPE: "H",
            },
        ),
        (
            "blank_brokers_reference",
            {**_MOTOR_WINDOWS, LANDING_BROKERS_REFERENCE: ""},
            {**_MOTOR_RECORD, LANDING_BROKERS_REFERENCE: None},
        ),
        (
            "blank_issue_date",
            {**_MOTOR_WINDOWS, LANDING_ISSUE_DATE: ""},
            {**_MOTOR_RECORD, LANDING_ISSUE_DATE: None},
        ),
        (
            "blank_broker_id",
            {**_MOTOR_WINDOWS, LANDING_BROKER_ID: ""},
            {**_MOTOR_RECORD, LANDING_BROKER_ID: None},
        ),
        (
            "all_zero_broker_id_window",
            {**_MOTOR_WINDOWS, LANDING_BROKER_ID: "0"},
            {**_MOTOR_RECORD, LANDING_BROKER_ID: "0"},
        ),
        (
            "all_zero_payment_window",
            {**_MOTOR_WINDOWS, "payment_amount": "0"},
            {**_MOTOR_RECORD, "payment_amount": "0"},
        ),
        (
            "all_zero_motor_premium_window",
            {**_MOTOR_WINDOWS, "motor_premium_amount": "0"},
            {**_MOTOR_RECORD, "motor_premium_amount": "0"},
        ),
    )
    for name, windows, expected in landed:
        _run_case(
            results,
            out,
            f"record_{name}_lands",
            lambda windows=windows, expected=expected, name=name: _case_landing_record(
                field_map, windows, expected, name
            ),
        )
    for name, windows, expected in landed[:2]:
        _run_case(
            results,
            out,
            f"windows_{name}_decode",
            lambda windows=windows, expected=expected, name=name: _case_window_decoding(
                field_map, windows, expected, name
            ),
        )
    _run_case(
        results, out, "records_motor_and_commercial_share_no_value",
        lambda: _case_distinct_records(),
    )
    _run_case(
        results, out, "product_premium_null_pattern",
        lambda: _case_product_null_pattern(field_map),
    )
    for request_id, policy_type in sorted(_ROUTED_REQUEST_IDS.items()):
        _run_case(
            results,
            out,
            f"request_id_{request_id}_routes_to_{policy_type}",
            lambda request_id=request_id, policy_type=policy_type:
            _case_request_routing(field_map, request_id, policy_type),
        )
    refused: tuple[tuple[str, Mapping[str, str], type[ExtractError], int,
                         tuple[str, ...]], ...] = (
        (
            "unrouted_request_id",
            {**_MOTOR_WINDOWS, LANDING_REQUEST_ID: _UNROUTED_REQUEST_ID},
            RecordError,
            EXIT_RECORD_REJECTED,
            (_UNROUTED_REQUEST_ID, "request routing does not recognise", "'99'"),
        ),
        (
            "blank_request_id",
            {**_MOTOR_WINDOWS, LANDING_REQUEST_ID: ""},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("is blank; the chain routes on it",),
        ),
        (
            "return_code_outside_the_domain",
            {**_MOTOR_WINDOWS, LANDING_RETURN_CODE: "55"},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("'55'", "outside the recorded domain"),
        ),
        (
            "return_code_not_all_digits",
            {**_MOTOR_WINDOWS, LANDING_RETURN_CODE: "0A"},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("not all digits",),
        ),
        (
            "blank_customer_number",
            {**_MOTOR_WINDOWS, LANDING_CUSTOMER_NUMBER: ""},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-CUSTOMER-NUM", "not all digits", "lie outside 0-9"),
        ),
        (
            "non_numeric_payment",
            {**_MOTOR_WINDOWS, "payment_amount": "50A"},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-PAYMENT", "not all digits", "window positions 6"),
        ),
        (
            "non_numeric_motor_premium",
            {**_MOTOR_WINDOWS, "motor_premium_amount": "45A"},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-M-PREMIUM", "not all digits", "window positions 6"),
        ),
        (
            "non_numeric_commercial_premium",
            {**_COMMERCIAL_WINDOWS, "flood_premium_amount": "780A"},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-B-FloodPremium", "not all digits"),
        ),
        (
            "blank_policy_number",
            {**_MOTOR_WINDOWS, LANDING_POLICY_NUMBER: ""},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-POLICY-NUM", "is blank", "on every execution returning '00'"),
        ),
        (
            "all_zero_policy_number",
            {**_MOTOR_WINDOWS, LANDING_POLICY_NUMBER: "0"},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-POLICY-NUM", "holds only zeros"),
        ),
        (
            "blank_last_changed",
            {**_MOTOR_WINDOWS, LANDING_LAST_CHANGED: ""},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-LASTCHANGED", "is blank", "on every execution returning '00'"),
        ),
        (
            "blank_payment",
            {**_MOTOR_WINDOWS, "payment_amount": ""},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-PAYMENT", "not all digits", "lie outside 0-9"),
        ),
        (
            "blank_motor_premium",
            {**_MOTOR_WINDOWS, "motor_premium_amount": ""},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-M-PREMIUM", "not all digits", "lie outside 0-9"),
        ),
        (
            "blank_commercial_premium",
            {**_COMMERCIAL_WINDOWS, "fire_premium_amount": ""},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-B-FirePremium", "not all digits", "lie outside 0-9"),
        ),
        (
            "broker_id_mixing_spaces_and_digits",
            {**_MOTOR_WINDOWS, LANDING_BROKER_ID: "4 2"},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-BROKERID", "not all digits", "window positions 9"),
        ),
        (
            "broker_id_carrying_a_letter",
            {**_MOTOR_WINDOWS, LANDING_BROKER_ID: "4A"},
            RecordError,
            EXIT_RECORD_REJECTED,
            ("CA-BROKERID", "not all digits", "window positions 10"),
        ),
    )
    for name, windows, kind, status, fragments in refused:
        _run_case(
            results,
            out,
            f"record_{name}_refused",
            lambda windows=windows, kind=kind, status=status, fragments=fragments,
            name=name: _case_record_refused(
                field_map, windows, kind, status, fragments, name
            ),
        )
    _run_case(
        results,
        out,
        "record_refusal_names_values_under_the_option",
        lambda: _case_refusal_names_values_under_the_option(field_map),
    )
    alphanumeric_keys = tuple(
        name
        for name in field_map.field_order
        if name in field_map.fields
        and field_map.fields[name].is_read_from_record
        and field_map.fields[name].kind == KIND_ALPHANUMERIC
    )
    for name in alphanumeric_keys:
        for character in _CONTROL_CHARACTER_CASES:
            _run_case(
                results,
                out,
                f"record_{name}_carrying_{_escaped_character(character)}_refused",
                lambda name=name, character=character: (
                    _case_control_character_refused(field_map, name, character)
                ),
            )
    _run_case(
        results,
        out,
        "record_control_character_named_under_the_option",
        lambda: _case_control_character_names_itself_under_the_option(
            field_map, "\x00"
        ),
    )
    for code in field_map.return_code_domain:
        if code == RETURN_CODE_SUCCESS:
            continue
        _run_case(
            results,
            out,
            f"record_return_code_{code}_refused",
            lambda code=code: _case_return_code_refused(field_map, code),
        )
    normalised: tuple[tuple[str, str], ...] = (
        ("2026-08-19-12.00.00.000000", "2026-08-19T12:00:00.000000"),
        ("2026-08-19-23.59.59.999999", "2026-08-19T23:59:59.999999"),
        ("2026-08-19-12.00.00.1", "2026-08-19T12:00:00.100000"),
        ("2026-08-19-12.00.00", "2026-08-19T12:00:00.000000"),
        ("2026-08-19T12:00:00.000000", "2026-08-19T12:00:00.000000"),
        ("2026-08-19 12:00:00.000000", "2026-08-19T12:00:00.000000"),
        ("2024-02-29-12.00.00.000000", "2024-02-29T12:00:00.000000"),
        ("2026-01-01-00.00.00.000000", "2026-01-01T00:00:00.000000"),
    )
    for raw, expected in normalised:
        _run_case(
            results,
            out,
            f"timestamp_{raw}_normalised",
            lambda raw=raw, expected=expected: _case_timestamp_window(
                field_map, raw, expected
            ),
        )
    impossible: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("2023-02-29-12.00.00.000000", ("day 29 of month 02",)),
        ("2026-00-19-12.00.00.000000", ("whose month is 00",)),
        ("2026-13-19-12.00.00.000000", ("whose month is 13",)),
        ("2026-08-00-12.00.00.000000", ("whose day is 00",)),
        ("2026-08-32-12.00.00.000000", ("whose day is 32",)),
        ("2026-08-19-24.00.00.000000", ("whose hour is 24",)),
        ("2026-08-19-12.60.00.000000", ("whose minute is 60",)),
        ("2026-08-19-12.00.60.000000", ("whose second is 60",)),
        ("2026-08-19-12.00.00.1234567", ("matches none of the accepted timestamp",)),
        ("2026-08-19", ("matches none of the accepted timestamp",)),
        ("19/08/2026 12:00:00", ("matches none of the accepted timestamp",)),
    )
    for raw, fragments in impossible:
        _run_case(
            results,
            out,
            f"timestamp_{raw}_refused",
            lambda raw=raw, fragments=fragments: _case_timestamp_refused(
                field_map, raw, fragments
            ),
        )
    for name in CALENDAR_DATE_FIELDS:
        _run_case(
            results,
            out,
            f"{name}_leap_day_accepted",
            lambda name=name: _case_date_accepted(field_map, name, "2024-02-29"),
        )
        for value, fragments in (
            ("2023-02-29", ("day 29 of month 02",)),
            ("2026-13-01", ("whose month is 13",)),
            ("2026-00-01", ("whose month is 00",)),
            ("2026-08-32", ("whose day is 32",)),
            ("2026-08-00", ("whose day is 00",)),
            ("2026-8-19", (f"not written {CALENDAR_DATE_FORM}",)),
        ):
            _run_case(
                results,
                out,
                f"{name}_{value}_refused",
                lambda name=name, value=value, fragments=fragments: _case_date_refused(
                    field_map, name, value, fragments
                ),
            )
    _run_case(
        results, out, "serialised_line_is_one_json_object",
        lambda: _case_serialised_line(field_map),
    )
    _run_case(
        results, out, "serialised_rejects_a_number",
        lambda: _case_serialised_rejects_non_string(field_map),
    )
    _run_case(
        results, out, "serialised_rejects_reordered_keys",
        lambda: _case_serialised_rejects_wrong_order(field_map),
    )


def _case_distinct_records() -> str:
    """Confirm the motor and commercial fixtures share no identifier and no amount."""
    shared = [
        name
        for name in _EXPECTED_FIELD_ORDER
        if name not in (LANDING_SOURCE_SYSTEM_KEY, LANDING_RETURN_CODE)
        and _MOTOR_RECORD[name] is not None
        and _MOTOR_RECORD[name] == _COMMERCIAL_RECORD[name]
    ]
    unexpected = [
        name
        for name in shared
        if name not in (LANDING_ISSUE_DATE, LANDING_EXPIRY_DATE, LANDING_LAST_CHANGED)
    ]
    if unexpected:
        raise _SelfTestFailure(
            f"the motor and commercial fixtures share {_quote_all(unexpected)}"
        )
    _expect(
        _MOTOR_RECORD["motor_premium_amount"] is not None
        and _COMMERCIAL_RECORD["motor_premium_amount"] is None,
        True,
        "whether only the motor fixture carries a motor premium",
    )
    _expect(
        _MOTOR_RECORD["fire_premium_amount"] is None
        and _COMMERCIAL_RECORD["fire_premium_amount"] is not None,
        True,
        "whether only the commercial fixture carries a fire premium",
    )
    return "the two fixtures share no key, no amount and no identifier"


def _output_cases(
    results: list[_CaseResult],
    out: Any,
    field_map: FieldMap,
    map_path: Path,
    scratch: Path,
) -> None:
    """Run the destination, mode, summary, refusal and command line cases."""
    _run_case(
        results, out, "extraction_lands_the_record",
        lambda: _case_extraction_writes_record(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "created_directory_and_record_modes",
        lambda: _case_created_modes(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "existing_destination_refused",
        lambda: _case_existing_destination_refused(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "overwrite_keeps_the_existing_mode",
        lambda: _case_overwrite_keeps_the_existing_mode(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "overwrite_creates_at_the_private_mode",
        lambda: _case_overwrite_creates_at_the_private_mode(
            scratch, map_path, field_map
        ),
    )
    _run_case(
        results, out, "destination_generated_roots_accepted",
        lambda: _case_generated_roots_accepted(),
    )
    _run_case(
        results, out, "destination_outside_the_repository_accepted",
        lambda: _case_out_of_tree_accepted(scratch),
    )
    for relative in (
        "modernization/extraction/copybook_field_map.yml",
        "modernization/landing/landing-schema.json",
        "modernization/dbt/genapp_rqi/dbt_project.yml",
        "modernization/validation/verify_readonly.sh",
        "modernization/requirements.txt",
    ):
        _run_case(
            results,
            out,
            f"destination_authored_{Path(relative).name}_refused",
            lambda relative=relative: _case_authored_destination_refused(relative),
        )
    _run_case(
        results, out, "destination_this_module_refused",
        lambda: _case_this_module_destination_refused(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "destination_committed_evidence_refused",
        lambda: _case_committed_evidence_refused(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "destination_read_only_source_refused",
        lambda: _case_read_only_source_refused(),
    )
    _run_case(
        results, out, "destination_symlink_alias_refused",
        lambda: _case_symlink_alias_refused(scratch),
    )
    _run_case(
        results, out, "destination_final_component_symlink_refused",
        lambda: _case_final_symlink_refused(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "destination_existing_directory_refused",
        lambda: _case_existing_directory_refused(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "destination_below_a_regular_file_refused",
        lambda: _case_parent_is_a_file_refused(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "destination_naming_no_file_refused",
        lambda: _case_destination_names_no_file_refused(),
    )
    _run_case(
        results, out, "destination_removed_parent_created_again",
        lambda: _case_removed_parent_recreated(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "temporary_name_collision_stepped_over",
        lambda: _case_temporary_collision_retried(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "temporary_names_exhausted_refused",
        lambda: _case_temporary_candidates_exhausted(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "temporary_entry_refused_by_the_directory",
        lambda: _case_temporary_entry_refused(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "summary_redacts_identifiers",
        lambda: _case_summary_redacted(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "summary_shows_identifiers_on_request",
        lambda: _case_summary_identifiers(scratch, map_path, field_map),
    )
    for carried, enabling, label in (
        ("1", True, "1"),
        ("true", True, "true"),
        ("yes", True, "yes"),
        ("on", True, "on"),
        ("TRUE", True, "upper-true"),
        (" on ", True, "spaced-on"),
        ("0", False, "0"),
        ("false", False, "false"),
        ("off", False, "off"),
        ("bogus", False, "bogus"),
        ("", False, "empty"),
    ):
        _run_case(
            results,
            out,
            f"summary_environment_{label}_"
            f"{'shows' if enabling else 'redacts'}_identifiers",
            lambda carried=carried, enabling=enabling, label=label:
            _case_summary_environment(
                scratch, map_path, field_map, carried, enabling, label
            ),
        )
    _run_case(
        results, out, "summary_redacted_line_carries_no_identifier",
        lambda: _case_summary_redacted_line_carries_no_identifier(),
    )
    for character in _CONTROL_CHARACTER_CASES:
        _run_case(
            results,
            out,
            f"command_line_control_character_{_escaped_character(character)}_refused",
            lambda character=character: _case_cli_control_character_refused(
                scratch, map_path, field_map, character
            ),
        )
    _run_case(
        results, out, "command_line_blank_broker_id_lands_null",
        lambda: _case_cli_blank_broker_id_lands_null(scratch, map_path, field_map),
    )
    for name, item in (
        ("payment_amount", "CA-PAYMENT"),
        ("motor_premium_amount", "CA-M-PREMIUM"),
    ):
        _run_case(
            results,
            out,
            f"command_line_blank_{name}_refused",
            lambda name=name, item=item: _case_cli_blank_amount_window_refused(
                scratch, map_path, field_map, name, item
            ),
        )
    _run_case(
        results, out, "summary_names_the_source_system_key_origin",
        lambda: _case_summary_names_the_key_origin(scratch, map_path, field_map),
    )
    _run_case(results, out, "environment_guard", _case_environment_guard)
    for code in field_map.return_code_domain:
        if code == RETURN_CODE_SUCCESS:
            continue
        _run_case(
            results,
            out,
            f"command_line_return_code_{code}_refused",
            lambda code=code: _case_cli_return_code_refused(
                scratch, map_path, field_map, code
            ),
        )
    _run_case(
        results, out, "command_line_self_test_rejects_extraction_arguments",
        lambda: _case_cli_self_test_rejects_extraction_arguments(scratch),
    )
    _run_case(
        results, out, "command_line_requires_capture_and_output",
        lambda: _case_cli_requires_capture_and_output(map_path),
    )
    _run_case(
        results, out, "command_line_rejects_withdrawn_failure_option",
        lambda: _case_cli_rejects_withdrawn_option(scratch, map_path, field_map),
    )
    _run_case(
        results, out, "source_system_key_from_option",
        lambda: _case_source_system_key("OTHER_SYSTEM.1-2", "OTHER_SYSTEM.1-2",
                                        "--source-system-key", "the option"),
    )
    _run_case(
        results, out, "source_system_key_from_environment_then_default",
        lambda: _case_source_system_key_from_environment(),
    )
    for supplied, fragments, what in (
        ("", ("is empty",), "an empty source-system key"),
        (
            "K" * (MAX_SOURCE_SYSTEM_KEY_CHARACTERS + 1),
            (f"holds {MAX_SOURCE_SYSTEM_KEY_CHARACTERS + 1} characters",),
            "an over-long source-system key",
        ),
        (
            "GENAPP/CLASS",
            ("outside ASCII letters, digits, underscore, dot and hyphen",),
            "a source-system key carrying a path separator",
        ),
    ):
        _run_case(
            results,
            out,
            f"source_system_key_{what.replace(' ', '_')}_refused",
            lambda supplied=supplied, fragments=fragments,
            what=what: _case_source_system_key_refused(supplied, fragments, what),
        )


def run_self_test(
    field_map_path: str | os.PathLike[str] | None = None,
    *,
    stream: Any = None,
) -> int:
    """Run every self-test case and return ``EXIT_OK`` or ``EXIT_SELF_TEST_FAILED``.

    The field map is loaded once, and its bytes are read once to seed the mutated maps,
    so a field map that cannot be read or does not validate raises its own diagnostic
    before any case runs. Each case then writes one line to ``stream``, which defaults
    to stdout, followed by one summary line naming the case count. Every capture,
    mutated map and destination a case writes sits inside one private scratch directory
    this run creates outside the repository and removes before it returns; the cases
    that exercise an in-tree destination validate the path without creating anything.
    """
    out = sys.stdout if stream is None else stream
    selected = DEFAULT_FIELD_MAP if field_map_path is None else Path(field_map_path)
    field_map = load_field_map(selected)
    map_text = _read_bounded_bytes(
        selected, MAX_FIELD_MAP_BYTES, "the field map"
    ).decode("utf-8")
    results: list[_CaseResult] = []
    scratch = Path(tempfile.mkdtemp(prefix=_SCRATCH_PREFIX))
    try:
        _field_map_cases(
            results, out, field_map, map_text, _case_directory(scratch, "field-maps")
        )
        _capture_cases(results, out, field_map, _case_directory(scratch, "captures"))
        _record_cases(results, out, field_map)
        _output_cases(results, out, field_map, selected, scratch)
    except BaseException:
        shutil.rmtree(scratch, ignore_errors=True)
        raise
    shutil.rmtree(scratch, ignore_errors=True)
    _run_case(
        results,
        out,
        "self_test_scratch_removed",
        lambda: _case_scratch_removed(scratch),
    )

    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    print(
        f"self-test summary cases={len(results)} passed={passed} failed={failed}",
        file=out,
    )
    return EXIT_OK if failed == 0 else EXIT_SELF_TEST_FAILED


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


class _CommandLineParser(argparse.ArgumentParser):
    """Command line parser that raises ``UsageError`` instead of printing usage text.

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
    """Return the non-interactive command line parser for this tool.

    Abbreviated option names are not accepted, as in every other command-line tool of
    this bridge, so an option this tool later gains can never change what an existing
    command line means.
    """
    parser = _CommandLineParser(
        prog=_PROGRAM,
        allow_abbrev=False,
        description=(
            "Decode the post-chain GenApp Policy-Issue COMMAREA capture and write the\n"
            "landing JSON record: one object holding the landing keys the field map\n"
            "lists, as JSON strings or null, on one line terminated by one line feed.\n"
            "Successful extractions only: a capture whose returned CA-RETURN-CODE is\n"
            f"not {RETURN_CODE_SUCCESS} is refused and nothing is written.\n"
            "\n"
            "Exit status: 0 success, 2 capture rejected, 3 field map invalid, 4 input\n"
            "failure, output refused or command line rejected, 5 self-test case\n"
            "failure, 6 returned CA-RETURN-CODE is a recorded unsuccessful code,\n"
            "130 interrupted."
        ),
        epilog=(
            "Every offset, length, kind, routing entry, nullability rule, return-code "
            "meaning and landing key is read from the field map; none is written into "
            "this tool. The capture must hold exactly "
            f"{COMMAREA_RECORD_LENGTH} characters, optionally followed by one line "
            "ending, and is decoded as "
            f"{CAPTURE_ENCODING}. policy_type is derived from the request id through "
            "the map's request_routing table and is the only derived value; no amount "
            "is derived, and a premium the derived policy type does not apply to is "
            "written as null rather than as a zero. Both landed dates must be real "
            "calendar dates and CA-LASTCHANGED is normalised to ISO-8601 after its "
            "date and clock components are checked; the current time is never "
            "substituted. Neither input is modified, and no path outside the "
            "destination is written.\n"
            f"Only a successful chain execution is landed: a returned CA-RETURN-CODE "
            f"other than {RETURN_CODE_SUCCESS} is rejected and nothing is written, and "
            "the evidence of a run that returned another code is the harness captures "
            "and driver logs under modernization/validation/artifacts/.\n"
            "The destination is canonicalised before anything is created. One that "
            "resolves inside the repository directory holding this script is accepted "
            "only below "
            f"{_quote_all(str(root) for root in GENERATED_OUTPUT_ROOTS)}; an authored "
            "file, the committed evidence under modernization/validation/artifacts, "
            "anything below the repository's base directory, a final component "
            "that is a symbolic link and an existing entry that is not a regular file "
            "are refused. A destination outside that repository is accepted. An "
            "existing regular file is refused wherever it stands unless "
            f"{OVERWRITE_OPTION} is given, and is then replaced keeping the mode it "
            f"carries. Each directory this tool creates carries mode "
            f"{DIRECTORY_MODE:04o} and a record this tool creates carries mode "
            f"{FILE_MODE:04o}, both set on the created entry so the ambient umask "
            "cannot widen them.\n"
            "The summary line names the resolved source-system key and the origin it "
            "was taken from.\n"
            "A record value reaches a diagnostic, and a business identifier reaches "
            f"the summary, only under {SHOW_IDENTIFIERS_OPTION} or the "
            f"{SHOW_IDENTIFIERS_VARIABLE} environment variable carrying one of "
            f"{', '.join(SHOW_IDENTIFIERS_ENABLING)}, which select the same "
            "diagnostics and the same summary line; without either a rejected "
            "value is reported by field, COBOL item, byte range, breached constraint "
            "and character count, and the policy number is reported as a digest.\n"
            "Every failure writes one control-free line to stderr and returns 2 for a "
            "rejected capture, 3 for an unpinned runtime environment or an "
            "inconsistent field map, 4 for an unreadable "
            "input, a refused output or a usage error, 5 for a failed self-test case, "
            "6 for a capture the chain did not complete, or 130 for an interrupt.\n"
            "Decision rationale: modernization/docs/decision-log.md"
            " (planned deliverable; not present at this milestone)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--commarea",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "post-chain COMMAREA capture written by the harness driver: "
            f"{COMMAREA_RECORD_LENGTH} characters and at most one trailing line "
            "ending; required unless --self-test is given"
        ),
    )
    parser.add_argument(
        "--field-map",
        default=DEFAULT_FIELD_MAP,
        type=Path,
        metavar="PATH",
        help=(
            "field map supplying every offset, length, kind, routing entry, "
            "return-code meaning and landing key (default: "
            f"{DEFAULT_FIELD_MAP.name} beside this script)"
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "destination for the landing JSON record; it must canonicalise outside the "
            "repository directory holding this script or below one of its generated "
            f"roots, its parent directories are created with mode {DIRECTORY_MODE:04o} "
            f"and a record this tool creates is written with mode {FILE_MODE:04o}; a "
            f"path that already exists is refused unless {OVERWRITE_OPTION} is given; "
            "required unless --self-test is given"
        ),
    )
    parser.add_argument(
        OVERWRITE_OPTION,
        action="store_true",
        help=(
            "replace an existing regular file at the destination, which keeps the mode "
            "it carries; without it a destination that already exists is refused by "
            "name and nothing is written. It never widens where a record may land: a "
            "path inside the repository directory holding this script and outside "
            "every generated root, a path below that repository's base directory, a "
            "symbolic link and an entry that is not a regular file stay refused"
        ),
    )
    parser.add_argument(
        "--source-system-key",
        default=None,
        metavar="VALUE",
        help=(
            "source-system discriminator written to the record; defaults to the "
            f"{SOURCE_SYSTEM_KEY_VARIABLE} environment variable, then to "
            f"{DEFAULT_SOURCE_SYSTEM_KEY}. A variable holding the empty string or "
            "whitespace alone counts as unset. At most "
            f"{MAX_SOURCE_SYSTEM_KEY_CHARACTERS} characters drawn from ASCII letters, "
            "digits, underscore, dot and hyphen. The resolved value and the origin it "
            "was taken from are named on the summary line"
        ),
    )
    parser.add_argument(
        SHOW_IDENTIFIERS_OPTION,
        action="store_true",
        help=(
            "carry record values in diagnostics and the request id, policy type, "
            "policy number, customer number, broker id, broker's reference and return "
            "code on the summary line; withheld by default, when the summary names the "
            "policy type, the return code, the landed key counts and the digest of the "
            "policy number only, and enabled with the same effect on the diagnostics "
            f"and on the summary line by the {SHOW_IDENTIFIERS_VARIABLE} environment "
            f"variable carrying one of {', '.join(SHOW_IDENTIFIERS_ENABLING)}, in any "
            "case and ignoring surrounding spaces"
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run the built-in case matrix against the field map and the records this "
            "module renders from its windows, then exit; it accepts --field-map and "
            "neither --commarea nor --output, works inside one private scratch "
            "directory it creates and removes, and returns "
            f"{EXIT_SELF_TEST_FAILED} when a case fails"
        ),
    )
    return parser


class ResolvedSourceSystemKey(NamedTuple):
    """One accepted source-system key and the origin it was taken from.

    ``value`` is the key written to the record and carried in the landing prefix.
    ``origin`` names where it came from - the option, the environment variable or the
    built-in default - in the wording the summary line and every diagnostic about the
    key carry.
    """

    value: str
    origin: str


def resolve_source_system_key(supplied: str | None) -> ResolvedSourceSystemKey:
    """Return the source-system key to write, taking the first value that is present.

    ``supplied`` is the ``--source-system-key`` value, or None when the option was
    omitted, in which case the ``SOURCE_SYSTEM_KEY`` environment variable is consulted
    and then ``DEFAULT_SOURCE_SYSTEM_KEY``. A variable holding the empty string or
    whitespace alone counts as unset and the default applies, which is the empty-value
    resolution modernization/landing/land_to_s3.py,
    modernization/landing/load_local.py and the local output of
    modernization/dbt/genapp_rqi/profiles.example.yml all apply. A value the option
    itself carries is never passed over: an empty option value is a rejected command
    line rather than a silent default.

    The returned ``ResolvedSourceSystemKey`` carries the accepted value and the origin
    it was taken from, which the summary line names beside the value and every
    diagnostic about the key already names.

    Raises ``UsageError`` when the resolved value is empty, longer than
    ``MAX_SOURCE_SYSTEM_KEY_CHARACTERS`` or carries a character outside the accepted
    set.
    """
    if supplied is not None:
        value = supplied
        origin = "--source-system-key"
    else:
        from_environment = os.environ.get(SOURCE_SYSTEM_KEY_VARIABLE)
        if from_environment is not None and from_environment.strip():
            value = from_environment
            origin = f"the {SOURCE_SYSTEM_KEY_VARIABLE} environment variable"
        else:
            value = DEFAULT_SOURCE_SYSTEM_KEY
            origin = "the built-in default"
    if not value:
        raise UsageError(f"the source-system key from {origin} is empty")
    if len(value) > MAX_SOURCE_SYSTEM_KEY_CHARACTERS:
        raise UsageError(
            f"the source-system key from {origin} holds {len(value)} characters: "
            f"{_shown(value)}; at most {MAX_SOURCE_SYSTEM_KEY_CHARACTERS} are accepted"
        )
    if not _SOURCE_SYSTEM_KEY_SHAPE.fullmatch(value):
        raise UsageError(
            f"the source-system key from {origin} carries a character outside ASCII "
            f"letters, digits, underscore, dot and hyphen: {_shown(value)}"
        )
    return ResolvedSourceSystemKey(value=value, origin=origin)


def main(argv: list[str] | None = None) -> int:
    """Decode one capture and write one landing record, returning the exit status.

    ``argv`` defaults to the process arguments. Every diagnostic reaches stderr as one
    control-free line and the success summary reaches stdout the same way, naming the
    resolved source-system key and the origin it was taken from. Whether record values
    may appear in either is resolved once from ``--show-identifiers`` and the
    environment before the capture is read, so no value reaches a diagnostic before the
    setting applies and the summary line carries that same resolution: the option and
    the ``SHOW_IDENTIFIERS_VARIABLE`` environment variable select the identifier line
    alike, and neither absent leaves the redacted line, which names no identifier.
    A rejected command line is reported through that same single line,
    without a usage block, and returns the status a refused input or output returns,
    while ``--help`` prints the full help and exits with status 0. ``--self-test`` runs
    the case matrix instead of an extraction and returns ``EXIT_SELF_TEST_FAILED`` when
    a case fails. An interrupt is reported through that same single line and returns
    ``EXIT_INTERRUPTED``; the temporary entry ``write_record`` writes through is removed
    on that path by its own cleanup, so an interrupted run leaves neither a partial
    record nor a stray temporary file.
    """
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        show_identifiers = resolve_show_identifiers(args.show_identifiers)
        set_show_identifiers(show_identifiers)
        if args.self_test:
            if args.commarea is not None or args.output is not None:
                parser.error("--self-test accepts neither --commarea nor --output")
            return run_self_test(args.field_map)
        if args.commarea is None or args.output is None:
            parser.error(
                "--commarea and --output are required unless --self-test is given"
            )
        source_system_key = resolve_source_system_key(args.source_system_key)
        field_map = load_field_map(args.field_map)
        capture = read_commarea(args.commarea, field_map.record_length)
        record = build_landing_record(capture, field_map, source_system_key.value)
        written = write_record(
            record,
            args.output,
            field_map.field_order,
            overwrite=args.overwrite,
        )
    except ExtractError as error:
        print(f"{_PROGRAM}: {_one_line(str(error))}", file=sys.stderr)
        return error.exit_status
    except KeyboardInterrupt:
        print(f"{_PROGRAM}: interrupted before completion", file=sys.stderr)
        return EXIT_INTERRUPTED

    print(
        _one_line(
            summarise(
                written,
                record,
                source_system_key_origin=source_system_key.origin,
                show_identifiers=show_identifiers,
            )
        )
    )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
