#!/usr/bin/env python3
"""Load one landed GenApp Policy-Issue object into the local raw relation.

WHAT THIS TOOL DOES
    Downloads the single S3 object modernization/landing/land_to_s3.py wrote, reads
    the COPY manifest that landing wrote beside it to confirm the two are the pair
    one landing produced, confirms the object still carries the landing contract -
    the complete
    modernization/landing/landing-schema.json document, its date format, a real
    last_changed moment, unique member names and a key equal to the one the
    object's own source-system key rebuilds - and writes it as one row of
    raw.genapp_policy_issue in a DuckDB database. The object is bound to its own
    immutable metadata before it is read: a head request records its ETag, its
    version id where the bucket keeps versions and its byte count, the download
    then requires that same ETag and version, and the bytes that arrive are
    confirmed against the byte count and entity tag that head request reported.
    Those bytes are then held to what the landing step recorded for them, still
    before anything is parsed: the SHA-256 digest and byte count
    modernization/landing/land_to_s3.py wrote as user metadata of the object at
    land time must both equal what arrived, and the COPY manifest that landing
    wrote beside the object - the sibling part-<NNNN>.manifest.json of the same
    part - must name exactly this object's URI and exactly the byte count that
    arrived. An ETag and a byte count describe whatever the bucket holds now, so an
    object rewritten under the landing key after the landing satisfies them; the
    recorded digest was computed before the upload, so it does not, and such an
    object fails the load with the object status and nothing written rather than
    reaching the raw relation. An object carrying no recorded digest is refused for
    the same reason: it cannot be shown to be the object that was landed.
    The landing schema is applied in full to the bytes that were downloaded, not
    only to the object that was headed, so an object replaced between the two
    requests fails the load instead of reaching the relation. Every one of those
    checks happens before the database is opened, so a rejected object never
    reaches it. The values written are the values the object carries: every one
    is bound as text or as SQL NULL exactly as landed, and no value is computed,
    scaled, rounded, padded, zero-filled, trimmed, defaulted or backfilled. The
    six amount values pass through
    untouched. Each of them reaches the landed object through one MOVE, at
    base/src/lgapdb01.cbl:265, 445, 489, 491, 493 and 495, and the three named
    programs carry no COMPUTE, MULTIPLY or DIVIDE statement and no COMP-3 item,
    so a loaded amount is the digit string the chain moved and nothing else.
    Typing is applied by the dbt models downstream, never here.

WHICH BYTES IT ACCEPTS AS AN OBJECT
    The downloaded body is checked to be the bytes the landing step recorded and
    then to be the canonical landed form before the row is written. Recorded means
    the SHA-256 digest and byte count land_to_s3.py wrote as user metadata of the
    object itself, both required and both compared with the bytes that arrived, and
    the COPY manifest of the same part, required to name this object's URI and the
    byte count that arrived; an object carrying no recorded digest, one whose digest
    disagrees, and one whose manifest names another object or another length are all
    refused unparsed. Canonical means the ASCII-escaped JSON serialisation of the
    parsed object followed by one line feed, holding the landed keys in the order the
    landing schema fixes. One comparison against that form refuses a pretty-printed or
    multi-line object, leading, surrounding or repeated whitespace, a carriage
    return, an absent or repeated terminal line feed, and a re-ordered key, and
    the diagnostic names the byte counts and the first differing offset. A
    repeated member name is refused by name while the object is parsed, so no
    member is resolved to a last-wins value. These are the same checks
    modernization/landing/land_to_s3.py applies before the upload. Each of these
    is a rejected object, reported as such, and nothing is written to the
    database.

WHICH TARGET IT ADDRESSES
    The local branch of the bridge, and only that branch. The run mode, taken
    from --run-mode or the DBT_TARGET environment variable and defaulting to
    RUN_MODE_LOCAL, is the same selector modernization/landing/land_to_s3.py
    consumes and the target key of
    modernization/dbt/genapp_rqi/profiles.example.yml resolves. This tool runs
    only in RUN_MODE_LOCAL: in RUN_MODE_REAL the same object and the same
    17-column row shape reach the raw relation through
    modernization/landing/load_redshift.sql instead, and this tool refuses to run
    rather than write the local DuckDB database while the rest of the run
    addresses the real target.

    RUN_MODE_LOCAL requires a resolved S3 endpoint, so a run that resolved none
    is refused before the download and before the database is opened. An endpoint
    override is accepted only for a loopback address: http or https, a host of
    127.0.0.0/8, ::1 or localhost, an explicit port of 1024 or above, no user
    information, no query, no fragment and no path beyond "/", and only when the
    resolved credentials came from the environment. Any other endpoint is
    refused, and no endpoint value reaches stdout, stderr or a diagnostic. Access
    is established from resolved credentials and a resolved region; the presence
    of an environment variable whose name begins with AWS is never read as
    evidence of access, and no variable is matched on that prefix. Results this
    tool produces are local-substitute results and establish nothing about a
    real-target run.

    A supplied endpoint is accepted only as a local substitute: it must be an
    http or https URL whose host is a loopback literal (127.0.0.0/8 or ::1) or
    exactly localhost, carrying an explicit port, no userinfo, no path beyond
    '/', no query and no fragment. Every other endpoint is refused by name
    before a client exists, so no credential is signed and no request is sent to
    it: a remote host, a name that merely resolves to loopback, a host that only
    looks like a loopback literal, an embedded credential, a path, a query, a
    fragment, a missing port and any scheme other than http or https are all
    refused. With no endpoint supplied the client resolves the real AWS endpoint
    and every endpoint the environment or a configuration profile carries is
    ignored, so an AWS_ENDPOINT_URL or AWS_ENDPOINT_URL_S3 variable cannot
    redirect a credentialed request.

WHICH MODES IT RUNS
    load            the default: download one object and write it as one row.
    --self-test     run the built-in case matrix and exit; it downloads nothing
                    from any network endpoint, opens only DuckDB databases
                    inside one private temporary directory it creates and
                    removes, and touches no database of the caller's.

WHICH INPUTS IT ACCEPTS
    --run-mode      branch of the bridge to address, RUN_MODE_LOCAL or
                    RUN_MODE_REAL, defaulting to the DBT_TARGET environment
                    variable and then to DEFAULT_RUN_MODE. Only RUN_MODE_LOCAL
                    runs this tool.
    --bucket        bucket holding the landed object, defaulting to the
                    S3_BUCKET environment variable. There is no built-in bucket
                    name.
    --key           exact object key, or the s3:// URI land_to_s3.py printed. It
                    must equal the key --source-system-key, the fixed entity
                    literal and --extract-date rebuild, so it confirms the
                    object to load rather than selecting another one. Omitted,
                    that rebuilt key is used.
    --source-system-key
                    source-system element of the landing prefix, defaulting to
                    the SOURCE_SYSTEM_KEY environment variable and then to
                    DEFAULT_SOURCE_SYSTEM_KEY. It must equal the object's own
                    source_system_key value.
    --entity        entity element of the landing prefix, which is the fixed
                    literal LANDING_ENTITY. Supplying any other value is
                    refused rather than loading an object outside the canonical
                    prefix.
    --extract-date  extract-date element of the landing prefix as YYYY-MM-DD,
                    defaulting to the current UTC date.
    --endpoint-url  loopback S3 endpoint to address, defaulting to the
                    S3_ENDPOINT_URL environment variable. It is required, since
                    this tool runs on the local branch alone.
    --region        region to address, defaulting to the AWS_REGION and then the
                    AWS_DEFAULT_REGION environment variable.
    --database      DuckDB database file, defaulting to the LOCAL_DUCKDB_PATH
                    and then the DUCKDB_DATABASE environment variable, and then
                    to modernization/validation/local.duckdb. Every component of
                    the requested path is canonicalised first, so a symbolic
                    link, a /proc/self/cwd alias and a relative path all resolve
                    to the file they name. The resolved path must name a file
                    directly inside modernization/validation/, not inside a
                    directory below it, must not be a symbolic link or an
                    existing non-regular file, and must not name one of the
                    authored files that directory carries. Each of those is a
                    rejected setting, reported with the configuration status and
                    naming the setting it came from, before the object is
                    downloaded.
    --no-ddl        apply none of the shared warehouse scripts, for a database
                    whose relation is already present. There is no option
                    naming a script: the scripts applied are the fixed
                    allowlist DDL_SCRIPT_NAMES holds, read from
                    modernization/warehouse/ddl in that order, and no other SQL
                    file is read or executed.
    --show-identifiers
                    carry record values in diagnostics and the natural-key
                    values and object URI in the report, which are redacted by
                    default. Also enabled by the GENAPP_SHOW_IDENTIFIERS
                    environment variable.
    --self-test     run the built-in case matrix and exit.
    --quiet         with --self-test, print only the failing case lines and the
                    summary.

    A setting supplied through an environment variable that holds the empty
    string or whitespace alone counts as unset, so the documented default
    applies; that is the empty-value resolution every command-line tool of this
    bridge applies.

HOW IT VALIDATES THE LANDED OBJECT
    The object is parsed with duplicate member names refused, so a document
    carrying the same key twice is rejected rather than silently collapsed to its
    last occurrence. Its nesting is measured before it is parsed and a document
    nesting deeper than MAX_JSON_NESTING_DEPTH is refused unparsed, so an object
    built to exhaust a parser is a rejected object - one line and the object status -
    rather than an interpreter that ran out of stack; the same line reports a value
    the parser refuses without it being a syntax error, an integer literal longer
    than the interpreter converts being one. The parsed document is then checked against
    modernization/landing/landing-schema.json as a Draft 2020-12 document with
    format assertion enabled - the same schema, the same dialect and the same
    assertions modernization/landing/land_to_s3.py applies - so enums, patterns,
    lengths and the calendar semantics of every date are all enforced here as
    well, and each timestamp is parsed against the exact written form the
    contract fixes. All of it happens before the database is opened.

    A schema violation is reported by the JSON Pointer of the offending value,
    the constraint it breached and the value's JSON type and size. The value
    itself is reported only under --show-identifiers: these objects carry policy,
    customer and broker identifiers, and this output is retained in run
    evidence.

WHAT --self-test CHECKS
    Schema loading and every way it can fail, the landed column names and their
    order, record validation against the schema in both directions, rejection of
    a repeated JSON member at every nesting level of the object and of the
    schema, the endpoint policy over accepted and refused forms, the download
    failures botocore reports, an object replaced between the head request and
    the download, a digest that does not match the recorded one, the land-time
    digest and byte count required of every object and each way they can fail, the
    COPY manifest required to name this object and its length and each way it can
    fail, the nesting bound over a document at it, one past it and one far past it,
    the interpreter's own nesting bound reached with the real parser, an integer
    literal longer than the interpreter converts, the option and the environment
    variable that carry identifiers producing the same output, the database
    path policy over accepted and refused paths, a path in a directory below the
    one directory a database may sit in refused as a setting before any request
    is made, SQL statement splitting, the physical shape of
    raw.genapp_policy_issue as the catalog reports it, one load, a repeated load
    of the same record, a load of a second record, the part option over every
    accepted and refused value with a key of another part refused, two parts of
    one extract date replayed out of one prefix into two coexisting rows, a
    failure mid-transaction with
    the rollback that follows it, an interrupt reported as one line and status 130
    from the command line and from an interrupted statement, the row counts the
    tool reports against the relation, redaction of business identifiers in both
    modes, and that every documented exit status is reachable. Collaborators are
    the pinned boto3 and botocore clients, driven through moto and through
    botocore's own stubber, and the pinned DuckDB, so a call this matrix makes is
    a call the pinned distribution models. The moto server a case starts serves
    that case alone and logs no request of its own, so the lines the matrix writes
    are the matrix's own.

WHERE IT WRITES
    One relation, raw.genapp_policy_issue, whose column names, column order and
    VARCHAR widths are defined by the two allowlisted scripts in
    modernization/warehouse/ddl and whose 17 column names and order this tool
    reads from modernization/landing/landing-schema.json. One transaction covers
    the whole load: the two allowlisted scripts are applied inside it, any row
    already carrying the natural key (source_system_key, policy_number) of the
    object just downloaded is removed, and that object is written as one row, so
    a repeated run leaves one row rather than two. No statement removes a row
    carrying any other natural key, so a row loaded from an earlier object
    survives every later run.

    On any failure the transaction is rolled back, which withdraws every change
    it made: the row written, the row removed, and any schema or relation the
    allowlisted scripts created inside it. DuckDB holds data and catalogue
    changes in the same transaction, so a failed load leaves the database exactly
    as it was found; a database file the connection created because it was absent
    stays on disk, holding no schema and no row.

    stdout carries exactly one line, naming the relation written, the rows
    removed and written and the digest of the object loaded. Every other message
    reaches stderr. No credential, token, session value or environment listing is
    ever printed, on any path.

    Business identifiers are redacted by default: the natural-key values on
    stdout and the object URI on stderr are replaced by a fixed marker, and no
    policy number, customer number, broker identifier or broker reference is
    printed. --show-identifiers restores them for a run whose output is not
    retained. The rows removed and written, the byte count, the digest and the
    relation name are printed in both modes.

HOW IT FAILS
    Every failure writes one control-free line to stderr and returns a non-zero
    status: 2 for a landed object that breaches the landing contract, 3 for a
    runtime environment that is not the pinned one, a rejected command line or an
    unresolved setting, 4 for an S3 endpoint, bucket
    or object operation that did not succeed, 5 for a database or SQL operation
    that did not succeed or a failed self-test case, 130 for an interrupt. A
    missing setting is named in the diagnostic. A SQL statement that the database
    refused is reported as written, with its script and its position in that
    script. A record value never reaches a diagnostic unless --show-identifiers
    is given: without it a rejected value is reported by its JSON pointer, the
    constraint it breached and its JSON type and size. The tool never prompts and
    requires no TTY.

    An interrupt is one line, "load_local: interrupted before completion", and
    status 130 wherever it arrives: while the third-party modules this tool
    imports are still loading, while a setting is resolving, while the object is
    downloading, and while the transaction is running, where DuckDB reports the
    interrupt as an interrupted query rather than as a refused statement. Nothing
    is written on any of those paths.

WHAT IT NEVER DOES
    It creates no bucket, cluster, workgroup, role, policy, network or key, and
    provisions nothing; a bucket that does not answer is reported, never
    created. It defines no relation of its own and restates no column type: the
    two allowlisted scripts are applied exactly as they are written, this tool
    adds no statement to them beyond the transaction it wraps them in, a script
    carrying its own transaction control is refused rather than applied, and no
    other SQL file can be named or run. It writes no relation but the one named
    above, no 18th column, no load timestamp, no batch identifier and no audit
    column. It reads nothing under base/, writes nothing under
    modernization/landing/, and opens or creates a database only as a regular
    file directly inside modernization/validation, the one directory a database
    file may sit in, re-examining that file after it is opened.

WHERE THIS STEP SITS
    Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge, and
    Figure 5 — Validation Harness Control Flow, both in
    modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md.
"""

from __future__ import annotations

import sys

_PROGRAM = "load_local"

# Status an interrupted run returns, and the one line it writes. Both are declared
# before every import but sys, and those imports are covered by the same reporting,
# so an interrupt that arrives while the standard library, boto3, duckdb or
# jsonschema is still loading is reported as that single line and that status rather
# than as a traceback of import frames. The run itself reports an interrupt through
# the same line.
EXIT_INTERRUPTED = 130
INTERRUPTED_MESSAGE = f"{_PROGRAM}: interrupted before completion"


def _report_interrupt() -> None:
    """Write the one line an interrupted run reports to stderr, and return None."""
    print(INTERRUPTED_MESSAGE, file=sys.stderr)


# Status a run returns when the interpreter running it, or a version installed for it,
# is not the one the project pins. It is the status of a rejected setting, declared here
# because the check it belongs to runs before the imports it covers.
EXIT_ENVIRONMENT_REJECTED = 3

# Python release series and distribution versions this tool runs under: the series
# modernization/requirements.txt is installed against and the exact version it pins for
# every distribution this module imports. The interpreter carrying them is
# modernization/.venv/bin/python.
PINNED_PYTHON_SERIES = (3, 12)
PINNED_DISTRIBUTIONS = (
    ("boto3", "1.43.74"),
    ("botocore", "1.43.74"),
    ("duckdb", "1.5.5"),
    ("jsonschema", "4.26.0"),
)
PINNED_INTERPRETER = "modernization/.venv/bin/python"
PINNED_REQUIREMENTS = "modernization/requirements.txt"


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
    import datetime
    import hashlib
    import io
    import ipaddress
    import json
    import logging
    import os
    import re
    import shutil
    import stat
    import tempfile
    import urllib.parse
    from collections.abc import Callable, Iterable, Mapping, Sequence
    from pathlib import Path
    from typing import Any, NamedTuple, NoReturn

    import boto3.session
    import duckdb
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
except KeyboardInterrupt:
    _report_interrupt()
    raise SystemExit(EXIT_INTERRUPTED) from None

# Paths resolved from this script's own directory rather than from the working
# directory, so every working directory reads the same contract and reaches the
# same default database.
_THIS_DIR = Path(__file__).resolve().parent
_MODERNIZATION_DIR = _THIS_DIR.parent
_REPOSITORY_DIR = _MODERNIZATION_DIR.parent
DEFAULT_SCHEMA = _THIS_DIR / "landing-schema.json"
DDL_DIRECTORY = _MODERNIZATION_DIR / "warehouse" / "ddl"

# The one directory a database file may sit in, and the database file the bridge keeps
# there. Every --database value resolves to a name directly inside this directory or is
# refused, so no run creates or opens a file anywhere else.
ALLOWED_DATABASE_ROOT = _MODERNIZATION_DIR / "validation"
DATABASE_DIRECTORY = ALLOWED_DATABASE_ROOT
DEFAULT_DATABASE = ALLOWED_DATABASE_ROOT / "local.duckdb"

# The SQL scripts this tool applies, in apply order. The list is fixed: the two shared
# scripts creating the schemas and the raw relation are the only SQL files this tool
# reads, and no option names another. A file added to DDL_DIRECTORY later is not read,
# and no statement outside these two scripts is ever executed.
DDL_SCRIPT_NAMES = ("01_schemas.sql", "02_raw_genapp_policy_issue.sql")

# Names in DATABASE_DIRECTORY that a database path may never resolve to: the authored
# files of that directory, which this tool must not open as a database or overwrite.
# All three are present: diff_harness_vs_warehouse.py, validation-evidence.md and
# verify_readonly.sh sit beside the database file this tool opens.
RESERVED_DATABASE_NAMES = (
    "diff_harness_vs_warehouse.py",
    "validation-evidence.md",
    "verify_readonly.sh",
)

# Environment variables consulted when the matching option is omitted. No value
# read from any of them is ever printed.
BUCKET_VARIABLE = "S3_BUCKET"
ENDPOINT_URL_VARIABLE = "S3_ENDPOINT_URL"
SOURCE_SYSTEM_KEY_VARIABLE = "SOURCE_SYSTEM_KEY"
REGION_VARIABLES = ("AWS_REGION", "AWS_DEFAULT_REGION")
DATABASE_VARIABLES = ("LOCAL_DUCKDB_PATH", "DUCKDB_DATABASE")
RUN_MODE_VARIABLE = "DBT_TARGET"

# Run modes, which are the output names of
# modernization/dbt/genapp_rqi/profiles.example.yml. RUN_MODE_LOCAL addresses the
# local substitute - a loopback S3 endpoint and this DuckDB database - and
# RUN_MODE_REAL addresses AWS S3 and Redshift, where
# modernization/landing/load_redshift.sql is the loader instead of this tool. The
# same two names select the branch in modernization/landing/land_to_s3.py and in
# the dbt profile.
RUN_MODE_LOCAL = "local_substitute"
RUN_MODE_REAL = "redshift"
RUN_MODES = (RUN_MODE_LOCAL, RUN_MODE_REAL)
DEFAULT_RUN_MODE = RUN_MODE_LOCAL
REAL_MODE_LOADER = "modernization/landing/load_redshift.sql"

# Environment variables naming the credentials a boto3 session resolves for
# itself. They are named in diagnostics and are never read by this module.
CREDENTIAL_VARIABLES = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")

# Landing prefix parts. The key is LANDING_KEY_ROOT, then one Hive-style segment
# per entry of PARTITION_FIELDS in this order, then the object name of the part being
# loaded. PARTITION_FIELDS is the whole of the partitioning: the part is an element of
# the object name and never a fourth Hive-style segment.
LANDING_KEY_ROOT = "landing"
PARTITION_FIELDS = ("source_system_key", "entity", "extract_date")
KEY_SEPARATOR = "/"

# Object name of one landed part, in the form modernization/landing/land_to_s3.py
# writes. One prefix carries one object per part, so the records of one source system,
# entity and extract date coexist under distinct part numbers and each is loaded by its
# own run of this tool; DEFAULT_PART_NUMBER applies when no part is named, which makes
# OBJECT_NAME the name a run that names no part reads.
OBJECT_NAME_TEMPLATE = "part-{part}.json"
PART_NUMBER_DIGITS = 4
MIN_PART_NUMBER = 0
MAX_PART_NUMBER = 10 ** PART_NUMBER_DIGITS - 1
DEFAULT_PART_NUMBER = 0
_PART_NUMBER_SHAPE = re.compile(r"\A[0-9]{1,%d}\Z" % PART_NUMBER_DIGITS)
_OBJECT_NAME_SHAPE = re.compile(
    r"\Apart-[0-9]{%d}\.json\Z" % PART_NUMBER_DIGITS
)
DEFAULT_PART_TEXT = f"{DEFAULT_PART_NUMBER:0{PART_NUMBER_DIGITS}d}"
OBJECT_NAME = OBJECT_NAME_TEMPLATE.format(part=DEFAULT_PART_TEXT)

# Object name of the COPY manifest modernization/landing/land_to_s3.py writes beside
# each landed part, and the members that manifest carries. The manifest is the second
# of the two objects a landing writes and the document
# modernization/landing/load_redshift.sql binds its real-target COPY to; this tool
# reads it to confirm that the object it downloaded is the object the landing bound
# that load to, and requires exactly one entry, in the shape Amazon Redshift's manifest
# schema fixes, whose url is this object's own URI and whose nested content_length is
# this object's real byte count.
MANIFEST_OBJECT_NAME_TEMPLATE = "part-{part}.manifest.json"
MANIFEST_OBJECT_NAME = MANIFEST_OBJECT_NAME_TEMPLATE.format(part=DEFAULT_PART_TEXT)
MANIFEST_ENTRIES_MEMBER = "entries"
MANIFEST_URL_MEMBER = "url"
MANIFEST_MANDATORY_MEMBER = "mandatory"
MANIFEST_META_MEMBER = "meta"
MANIFEST_CONTENT_LENGTH_MEMBER = "content_length"
MANIFEST_ENTRY_COUNT = 1

# User-metadata names modernization/landing/land_to_s3.py records the land-time
# identity of the landed object under: the SHA-256 digest of the bytes it wrote, as 64
# lower-case hexadecimal characters, and their byte count, as decimal digits. Both are
# required here and are compared with the bytes that arrive before anything is parsed,
# so an object rewritten under the landing key after the landing fails this load
# instead of reaching the raw relation. Object metadata names reach the wire as
# x-amz-meta-<name> and are reported back lower-cased, so both are compared
# lower-cased.
# Decision rationale: modernization/docs/decision-log.md, row D-124.
RECORDED_SHA256_METADATA = "genapp-sha256"
RECORDED_LENGTH_METADATA = "genapp-content-length"
_RECORDED_SHA256_SHAPE = re.compile(r"\A[0-9a-f]{64}\Z")
_RECORDED_LENGTH_SHAPE = re.compile(r"\A[0-9]{1,12}\Z")

# Value used when the matching option and environment variable are both absent.
DEFAULT_SOURCE_SYSTEM_KEY = "GENAPP_CLASS_EXEMPLAR"

# Entity element of the landing prefix. One entity is landed by this bridge, so the
# value is fixed: --entity is accepted only when it repeats this literal.
LANDING_ENTITY = "policy_issue"

# Service addressed, and the URI form --key also accepts.
SERVICE_NAME = "s3"
URI_SCHEME_SEPARATOR = "://"

# Semantic formats the landing schema asserts, and the exact representation the
# genapp-timestamp checker parses. Both match modernization/landing/land_to_s3.py, so
# the two tools reach the same verdict for the same bytes.
DATE_FORMAT_NAME = "date"
TIMESTAMP_FORMAT_NAME = "genapp-timestamp"
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

# Relation written, and the fields whose values identify one row of it. Both
# names are confirmed against _IDENTIFIER_SHAPE before they reach any statement.
RAW_SCHEMA_NAME = "raw"
RAW_TABLE_NAME = "genapp_policy_issue"
NATURAL_KEY_FIELDS = ("source_system_key", "policy_number")

# Keys the landed object carries. The names and their order are read from the
# properties block of the landing schema; this count is the invariant that
# reading is confirmed against.
EXPECTED_COLUMN_COUNT = 17

# Object keys carrying a calendar date, and the key carrying the normalised
# last-changed timestamp. Each is parsed before the database is opened, so a value
# of the right shape that names no day or no moment is refused here rather than at
# the DATE or TIMESTAMP cast of the downstream dbt models. The date keys also carry
# the landing schema's "date" format, which build_format_checker asserts.
DATE_FIELDS = ("issue_date", "expiry_date")
TIMESTAMP_FIELD = "last_changed"

# Forms the date and timestamp values are written in. The timestamp form carries no
# UTC offset, so it is not an RFC 3339 date-time and is parsed with this exact
# pattern rather than by a schema format.
DATE_FORM = "YYYY-MM-DD"
TIMESTAMP_FORM = "YYYY-MM-DDTHH:MM:SS.ffffff"
TIMESTAMP_PATTERN = "%Y-%m-%dT%H:%M:%S.%f"
TIMESTAMP_OUTPUT_SEPARATOR = "T"
TIMESTAMP_OUTPUT_PRECISION = "microseconds"

# Accepted shapes. A partition segment value becomes one path segment, so it
# carries no separator, no whitespace and no equals sign. An identifier becomes
# SQL text and so is confirmed rather than bound.
_SEGMENT_SHAPE = re.compile(r"\A[A-Za-z0-9_.\-]+\Z")
_IDENTIFIER_SHAPE = re.compile(r"\A[a-z][a-z0-9_]*\Z")
MAX_SEGMENT_CHARACTERS = 64
MAX_IDENTIFIER_CHARACTERS = 63

# General-purpose bucket naming rules, which a bucket name must satisfy to be
# addressable at all: 3 to 63 characters drawn from lowercase letters, digits,
# dot and hyphen, beginning and ending with a letter or a digit, carrying no two
# adjacent dots, not written as an IPv4 address, and carrying none of the
# prefixes or suffixes the service reserves for its own name spaces. These are
# the rules modernization/landing/land_to_s3.py applies to the same setting, so a
# name that landed the object can address it here.
_BUCKET_SHAPE = re.compile(r"\A[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9]\Z")
_BUCKET_ADJACENT_DOTS = ".."
_BUCKET_IPV4_SHAPE = re.compile(r"\A[0-9]{1,3}(\.[0-9]{1,3}){3}\Z")
BUCKET_RESERVED_PREFIXES = (
    "xn--",
    "sthree-",
    "amzn-s3-demo-",
)
BUCKET_RESERVED_SUFFIXES = (
    "-s3alias",
    "--ol-s3",
    ".mrap",
    "--x-s3",
    "--table-s3",
)
MIN_BUCKET_CHARACTERS = 3
MAX_BUCKET_CHARACTERS = 63

# Credential resolution methods accepted while a custom endpoint is addressed.
# The method is the name botocore records on the credentials it resolved: 'env'
# for the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY variables and 'explicit'
# for values passed to the session directly. Any other method - a shared
# credentials file, a configured profile, single sign-on, an assumed role,
# container or instance metadata - names credentials that belong to a real
# account, and those are never signed against a local endpoint.
LOCAL_CREDENTIAL_METHODS = ("env", "explicit")

# Endpoint overrides accepted. An override sends signed requests wherever it names,
# so only a local S3-compatible endpoint is accepted: one of these schemes, a
# loopback host, an explicit port at or above ENDPOINT_PORT_FLOOR, no user
# information, no query, no fragment and no path beyond a single separator, within
# MAX_ENDPOINT_CHARACTERS characters. Every port from that floor up is accepted, so
# concurrent local endpoints on different ports are all reachable, while no override can
# address a privileged loopback service. With no override the SDK resolves the AWS
# endpoint itself.
ACCEPTED_ENDPOINT_SCHEMES = ("http", "https")
LOOPBACK_HOST_NAME = "localhost"
ACCEPTED_ENDPOINT_PATHS = ("", KEY_SEPARATOR)
ENDPOINT_PORT_FLOOR = 1024
MAX_ENDPOINT_CHARACTERS = 256

# Text a redacted endpoint value is replaced by, and the URLs redacted out of a
# diagnostic. A library diagnostic can quote the endpoint it addressed, so every
# http and https URL is replaced before the text reaches stderr.
REDACTED_ENDPOINT = "<endpoint>"
_URL_IN_TEXT = re.compile(r"(?i)https?://[^\s\"'<>,]*")

# Extract date form accepted on the command line and emitted into the key.
EXTRACT_DATE_FORM = "YYYY-MM-DD"

# SQL keywords that open, close or abandon a transaction. The load runs as one
# transaction, so a supplied script carrying any of them would commit or discard
# part of it; such a script is refused rather than applied.
TRANSACTION_CONTROL_KEYWORDS = (
    "begin",
    "start",
    "commit",
    "end",
    "rollback",
    "abort",
)

# In-memory database name a DuckDB connection accepts, which this tool refuses:
# the following step reads the database as a file.
IN_MEMORY_DATABASE = ":memory:"

# Value recorded as the object version when the bucket keeps no versions, and the
# marker printed in place of a business identifier unless --show-identifiers is
# given.
NOT_VERSIONED = "not-versioned"
REDACTED_TEXT = "<redacted>"

# Bytes one read takes from the landed object and from the schema before
# anything parses them, and the bytes one read asks for at a time.
MAX_OBJECT_BYTES = 1024 * 1024
MAX_SCHEMA_BYTES = 4 * 1024 * 1024
MAX_DDL_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 64 * 1024
READ_CHUNK_BYTES = 65536

# Arrays and objects one JSON document this tool parses may nest inside one another,
# and the structural characters that count. A landed object is one flat object, so it
# nests one level; the landing schema nests six and the COPY manifest four. The bound
# leaves that room many times over and is reached only by a document built to exhaust a
# parser. It is measured before the document is handed to the parser, so a document
# past it is refused as a rejected object rather than by the interpreter running out of
# stack. The value matches modernization/landing/land_to_s3.py, so the tool that wrote
# an object and the tool that reads it apply the same bound.
# Decision rationale: modernization/docs/decision-log.md, row D-122.
MAX_JSON_NESTING_DEPTH = 64
_JSON_STRING_DELIMITER = '"'
_JSON_STRING_ESCAPE = "\\"
_JSON_OPENERS = "[{"
_JSON_CLOSERS = "]}"

# Rows one load removes and writes. A load carries one object, which carries one
# record.
EXPECTED_INSERTED_ROWS = 1

# Reason DuckDB reports for a statement stopped by the process's own interrupt. The
# driver consumes that interrupt while the statement runs and reports it as a
# RuntimeError carrying this text, which is neither a KeyboardInterrupt nor one of the
# driver's own errors, so _interrupted names it explicitly.
INTERRUPTED_STATEMENT_TEXT = "Query interrupted"

# Connection behaviour applied to every request, bounding the time a failing
# endpoint can hold up the caller. MAX_ATTEMPTS is the number of calls one request
# makes in total, the first included, and is applied through the client's
# total_max_attempts setting.
CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 3
RETRY_MODE = "standard"

EXIT_OK = 0
EXIT_OBJECT_REJECTED = 2
EXIT_CONFIGURATION_REJECTED = EXIT_ENVIRONMENT_REJECTED
EXIT_S3_UNAVAILABLE = 4
EXIT_WAREHOUSE_UNAVAILABLE = 5
# A failed self-test case returns the same status as a warehouse failure, since a
# case that did not hold is a load that would not have succeeded. EXIT_INTERRUPTED is
# declared above the third-party imports, with the reporting that covers them.
EXIT_SELF_TEST_FAILED = EXIT_WAREHOUSE_UNAVAILABLE

# Characters of untrusted text one diagnostic fragment carries before
# truncation, the keys one diagnostic names, and the schema violations one
# diagnostic reports.
MAX_DIAGNOSTIC_CHARACTERS = 64
MAX_DIAGNOSTIC_PATH_CHARACTERS = 160
MAX_DIAGNOSTIC_MESSAGE_CHARACTERS = 200
MAX_DIAGNOSTIC_STATEMENT_CHARACTERS = 400
MAX_REPORTED_KEYS = 8
MAX_REPORTED_SCHEMA_ERRORS = 5

# Opt-in carrying record values into diagnostics and the policy number into the
# report, the environment variable consulted when the option is omitted, and the
# values that variable may carry to enable it. Without the opt-in a rejected
# value is reported by its JSON pointer, the constraint it breached and its size,
# and a business identifier by its digest.
SHOW_IDENTIFIERS_OPTION = "--show-identifiers"
SHOW_IDENTIFIERS_VARIABLE = "GENAPP_SHOW_IDENTIFIERS"
SHOW_IDENTIFIERS_ENABLING = ("1", "true", "yes", "on")
IDENTIFIER_DIGEST_CHARACTERS = 12
IDENTIFIER_DIGEST_PREFIX = "sha256-"

# Fields of NATURAL_KEY_FIELDS reported as a digest rather than as their value.
# The source-system key is a configured discriminator that also forms the landing
# prefix; the policy number is a business identifier.
DIGESTED_KEY_FIELDS = ("policy_number",)

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
_CODES_PRECONDITION_FAILED = frozenset({"412", "PreconditionFailed"})

# Shape of the entity tag a single-part upload carries, which is the hex MD5 of
# the object body. A tag carrying a part count after a hyphen is a multipart tag
# and stands for a digest of digests rather than of the body.
_SINGLE_PART_ETAG_SHAPE = re.compile(r"\A[0-9a-fA-F]{32}\Z")


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


class DuplicateMemberError(ValueError):
    """A JSON object carries the same member name twice.

    ``name`` is the member that repeated. The error is raised out of the parser,
    from the nesting level that carried the repetition, before the document is
    returned.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f"the JSON object carries the member {name!r} more than once")
        self.name = name


class UnparsableDocumentError(ValueError):
    """A JSON document is past what this tool parses, rather than malformed.

    ``reason`` is the bounded fragment naming which bound was reached: the nesting
    bound this tool applies, the interpreter's own nesting bound, or a value the
    parser refused that is not a syntax error, such as an integer literal longer
    than the interpreter converts. Each is a rejected input, reported as one line
    with the tool's own status, never as a traceback of parser frames.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


# Whether a diagnostic and the report may carry record values. Set once from the
# command line and the environment before any object is downloaded.
_show_identifiers = False


def set_show_identifiers(enabled: bool) -> None:
    """Record whether a diagnostic and the report may carry record values."""
    global _show_identifiers
    _show_identifiers = bool(enabled)


def show_identifiers_enabled() -> bool:
    """Return True when a diagnostic and the report may carry record values."""
    return _show_identifiers


def resolve_show_identifiers(supplied: bool) -> bool:
    """Return whether record values are shown, from the option then the environment.

    ``supplied`` is the ``--show-identifiers`` flag, which enables display on its own.
    With the flag absent the ``SHOW_IDENTIFIERS_VARIABLE`` environment variable
    enables display when it carries one of ``SHOW_IDENTIFIERS_ENABLING``, in any case
    and ignoring surrounding spaces; every other value, including an empty one
    and an absent variable, leaves record values withheld.

    ``main`` resolves this once and holds it in the module through
    ``set_show_identifiers``, and every caller reads it back through
    ``show_identifiers_enabled`` rather than the option, so the option and the
    variable select the same diagnostics, the same progress lines and the same
    summary line.
    Decision rationale: modernization/docs/decision-log.md, row D-123.
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


def _redacted(text: str) -> str:
    """Return ``text`` with every http and https URL replaced by ``REDACTED_ENDPOINT``.

    A client-library diagnostic can quote the endpoint it addressed, and the
    endpoint is a setting this tool never discloses, so the URL is removed rather
    than truncated.
    """
    return _URL_IN_TEXT.sub(REDACTED_ENDPOINT, text)
def _withheld(length: int) -> str:
    """Return the fragment standing for a withheld value of ``length`` characters."""
    return f"<redacted {length} chars>"


def _value_display(value: Any) -> str:
    """Return any landed value for a diagnostic, withholding its content.

    Text is reported by its character count, a number and a boolean by their JSON
    type, and null as null, so a diagnostic names the shape a value had without
    naming the value. With display enabled the value itself is rendered.
    """
    if show_identifiers_enabled():
        return _display(value)
    if isinstance(value, str):
        return _withheld(len(value))
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, (int, float)):
        return f"a {_type_name(value)}"
    return f"a {_type_name(value)}"


def _digest(value: str) -> str:
    """Return a stable short digest of ``value``, standing in for the value itself.

    The digest is the leading ``IDENTIFIER_DIGEST_CHARACTERS`` hexadecimal
    characters of the SHA-256 of the UTF-8 encoding of ``value``, so two runs
    carrying the same identifier report the same fragment.
    """
    encoded = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return IDENTIFIER_DIGEST_PREFIX + encoded[:IDENTIFIER_DIGEST_CHARACTERS]


def _identifier(value: str) -> str:
    """Return one business identifier for output: the value, or its digest."""
    if show_identifiers_enabled():
        return value
    return _digest(value)


def _reason(error: BaseException) -> str:
    """Return the reason text of ``error`` as one bounded diagnostic fragment.

    Any endpoint URL the error text quotes is redacted before the fragment is
    bounded.
    """
    text = str(error) or _type_name(error)
    return _escaped(_redacted(text), MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)


def _interrupted(error: BaseException) -> bool:
    """Return whether ``error`` is the database's report of an interrupted statement.

    DuckDB reports an interrupt that arrives while a statement is running in one of
    two ways, neither of them a ``KeyboardInterrupt``: as
    ``duckdb.InterruptException`` when the connection itself was interrupted, and as a
    ``RuntimeError`` carrying ``INTERRUPTED_STATEMENT_TEXT`` when the driver consumed
    the pending interrupt of this process while the statement ran, which is the shape
    a run stopped by hand at the keyboard meets. A run stopped mid-statement therefore
    reaches the database error paths, and each of them asks this question first so such
    a run is reported as the interrupt it is rather than as a database refusal.
    """
    if isinstance(error, duckdb.InterruptException):
        return True
    return isinstance(error, RuntimeError) and str(error) == INTERRUPTED_STATEMENT_TEXT


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


def _quote_all(names: Iterable[Any]) -> str:
    """Return ``names`` quoted, escaped and joined by a comma, in the order given."""
    return ", ".join(_shown(str(name)) for name in names)


def _counted(count: int, noun: str) -> str:
    """Return ``count`` and ``noun``, with the noun pluralised by an 's' when needed."""
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _json_shape(value: Any) -> str:
    """Return the JSON type of ``value``, and its length where that carries no content.

    A string is described by its type and character count, an array and an object
    by their element and member counts, and every other value by its JSON type
    alone. No character of a string, no element of an array and no member name of
    an object is rendered, so the description of a value never carries the value.
    A landed object carries policy, customer and broker identifiers, and this
    output is retained in run evidence.
    """
    if isinstance(value, str):
        return f"a string of {_counted(len(value), 'character')}"
    if isinstance(value, bool):
        return "a boolean"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return "a number"
    if isinstance(value, Mapping):
        return f"an object of {_counted(len(value), 'member')}"
    if isinstance(value, Sequence):
        return f"an array of {_counted(len(value), 'element')}"
    return f"a {_type_name(value)}"


def _reported_uri(uri: str, show_identifiers: bool) -> str:
    """Return the object URI as a progress line carries it.

    With ``show_identifiers`` false, which is the default, the bucket, the
    landing prefix and the object name are replaced by ``REDACTED_TEXT``: the
    prefix carries the source-system key, so a captured run log holds no
    identifier of the source system or of the record. With it true the URI is
    carried as it is.
    """
    if show_identifiers:
        return uri
    return f"{SERVICE_NAME}{URI_SCHEME_SEPARATOR}{REDACTED_TEXT}"


def _warn(message: str) -> None:
    """Write one control-free warning line to stderr."""
    print(f"{_PROGRAM}: warning: {_one_line(message)}", file=sys.stderr)


def _note(message: str) -> None:
    """Write one control-free progress line to stderr."""
    print(f"{_PROGRAM}: {_one_line(message)}", file=sys.stderr)


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------


def _distinct_members(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    """Return the members of one JSON object, refusing a name that repeats.

    This is the object hook every JSON document this tool reads is parsed with,
    so a repeated member is refused at every nesting level of the document
    rather than silently resolved to the last occurrence.

    Raises ``DuplicateMemberError`` naming the first member that repeats.
    """
    members: dict[str, Any] = {}
    for name, value in pairs:
        if name in members:
            raise DuplicateMemberError(name)
        members[name] = value
    return members


def _end_of_json_string(text: str, opening: int) -> int:
    """Return the index just past the string literal ``text`` opens at ``opening``.

    The closing delimiter is the first one not escaped by an odd number of
    preceding backslashes, which is the escaping the JSON grammar fixes, so a
    structural character inside a landed value is never counted as nesting. An
    unterminated literal returns the end of ``text``: that document is not
    well-formed and the parser reports it, and counting no nesting past the
    opener cannot admit a document the parser would then nest deeply into.
    """
    index = opening + 1
    while True:
        closing = text.find(_JSON_STRING_DELIMITER, index)
        if closing < 0:
            return len(text)
        backslashes = 0
        probe = closing - 1
        while probe > opening and text[probe] == _JSON_STRING_ESCAPE:
            backslashes += 1
            probe -= 1
        if backslashes % 2 == 0:
            return closing + 1
        index = closing + 1


def json_nesting_depth(text: str, limit: int = MAX_JSON_NESTING_DEPTH) -> int:
    """Return how deeply the arrays and objects of ``text`` nest, bounded by ``limit``.

    One pass over ``text`` counts an opening bracket or brace as one level and
    the matching closing one as the end of that level, skipping every string
    literal, so a bracket inside a landed value is not counted. Counting stops as
    soon as the depth passes ``limit`` and the value returned is then
    ``limit + 1``: an object built to exhaust a parser is refused after its first
    ``limit + 1`` characters rather than being scanned in full. The pass is
    linear in the length of ``text`` and allocates nothing beyond the loop's own
    indices, so it cannot itself be the denial of service it guards against.

    A document this returns a depth for is not thereby well-formed; the parser is
    what decides that. This is a bound, applied before parsing, and nothing else.
    """
    depth = 0
    deepest = 0
    index = 0
    length = len(text)
    while index < length:
        character = text[index]
        if character == _JSON_STRING_DELIMITER:
            index = _end_of_json_string(text, index)
            continue
        if character in _JSON_OPENERS:
            depth += 1
            if depth > deepest:
                deepest = depth
                if deepest > limit:
                    return limit + 1
        elif character in _JSON_CLOSERS and depth > 0:
            depth -= 1
        index += 1
    return deepest


def parse_json_document(
    text: str, *, depth_limit: int = MAX_JSON_NESTING_DEPTH
) -> Any:
    """Return the JSON value ``text`` carries, refusing a repeated member.

    The nesting of ``text`` is measured before it is parsed and a document
    nesting deeper than ``depth_limit`` is refused unparsed, so no document this
    tool downloads or reads can drive the parser into the interpreter's own
    nesting bound. Two further outcomes of the parser itself are reported the
    same way rather than as a traceback: the interpreter's nesting bound, which a
    document within ``depth_limit`` reaches only when the stack was already
    nearly spent, and a value the parser refuses without it being a syntax error,
    which an integer literal longer than the interpreter converts to an int is.
    ``depth_limit`` is the module's bound for every caller of this tool; a larger
    one is passed only by the self-test case that exercises the interpreter's own
    bound with the real parser.

    Raises ``json.JSONDecodeError`` when ``text`` is not one well-formed JSON
    document, ``DuplicateMemberError`` when any object in it carries a member
    name twice, and ``UnparsableDocumentError`` when it is past one of the three
    bounds above.
    """
    depth = json_nesting_depth(text, depth_limit)
    if depth > depth_limit:
        raise UnparsableDocumentError(
            f"its arrays and objects nest more than {depth_limit} levels deep, which "
            f"is deeper than any document of the landing contract"
        )
    try:
        return json.loads(text, object_pairs_hook=_distinct_members)
    except (DuplicateMemberError, json.JSONDecodeError):
        raise
    except RecursionError as error:
        raise UnparsableDocumentError(
            f"it nests {depth} levels deep, which the interpreter running this tool "
            f"cannot parse: {_reason(error)}"
        ) from error
    except ValueError as error:
        raise UnparsableDocumentError(
            f"the parser refused a value it carries: {_reason(error)}"
        ) from error


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

    The document is returned as parsed; no constraint of it is restated in this
    module. A member name that repeats at any nesting level of the schema is
    refused and named.

    Raises ``SchemaError`` when the file is missing, empty, larger than
    ``MAX_SCHEMA_BYTES``, not valid UTF-8, not well-formed JSON, nests deeper than
    ``MAX_JSON_NESTING_DEPTH``, carries a value the parser refuses, carries a
    repeated member name, or is not a JSON object.
    """
    try:
        raw = _read_bounded_bytes(path, MAX_SCHEMA_BYTES, "landing schema")
    except ConfigurationError as error:
        raise SchemaError(str(error)) from error
    try:
        document = parse_json_document(raw.decode("utf-8"))
    except DuplicateMemberError as error:
        raise SchemaError(
            f"the landing schema carries the member {_shown(error.name)} more than "
            f"once: {_path_shown(path)}; one value per member is required"
        ) from error
    except UnparsableDocumentError as error:
        raise SchemaError(
            f"the landing schema is not a document this tool parses: "
            f"{_path_shown(path)}: {error.reason}"
        ) from error
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


def build_format_checker() -> jsonschema.FormatChecker:
    """Return the checker applying the landing schema's semantic format assertions.

    The checker carries the dialect's own ``date`` checker, which accepts a
    calendar date and rejects a value such as 2026-99-99 that a date pattern
    alone admits, and a ``genapp-timestamp`` checker parsing the exact
    ``TIMESTAMP_FORMAT`` representation the landing contract carries. A
    non-string instance passes both, as a format assertion applies to strings
    only. The construction matches modernization/landing/land_to_s3.py, so the
    landing tool and this loader reach the same verdict for the same bytes.

    Raises ``SchemaError`` when the installed library publishes no ``date``
    checker, since the schema's date assertions would otherwise be annotations
    that assert nothing.
    """
    if DATE_FORMAT_NAME not in jsonschema.FormatChecker.checkers:
        raise SchemaError(
            f"the installed jsonschema library publishes no {_shown(DATE_FORMAT_NAME)} "
            "format checker, so the landing schema's date assertions cannot be applied"
        )
    checker = jsonschema.FormatChecker(formats=(DATE_FORMAT_NAME,))

    @checker.checks(TIMESTAMP_FORMAT_NAME, raises=ValueError)
    def _conforms(instance: Any) -> bool:
        """Return True when ``instance`` is a timestamp written TIMESTAMP_FORMAT."""
        if not isinstance(instance, str):
            return True
        datetime.datetime.strptime(instance, TIMESTAMP_FORMAT)
        return True

    return checker


def build_validator(
    schema: Mapping[str, Any], path: Path = DEFAULT_SCHEMA
) -> Draft202012Validator:
    """Return a validator for ``schema``, confirming its declared dialect first.

    ``schema`` must declare the 2020-12 dialect in ``$schema``, which is the
    dialect the returned validator applies, and must itself satisfy that
    dialect's meta-schema. ``path`` names the schema in any diagnostic. The
    validator carries the checker ``build_format_checker`` returns, so every
    ``format`` the schema declares is asserted rather than annotated.

    Raises ``SchemaError`` when the declared dialect is absent or differs from
    the one applied, when the document is not a valid schema, or when the format
    checker cannot be built.
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
    return Draft202012Validator(schema, format_checker=build_format_checker())


def _json_pointer(path: Iterable[Any]) -> str:
    """Return the RFC 6901 JSON Pointer for ``path``, rendering the root as ``/``.

    Each element is escaped as RFC 6901 requires, with ``~`` written ``~0`` and
    ``/`` written ``~1``.
    """
    parts = [
        str(element).replace("~", "~0").replace(KEY_SEPARATOR, "~1")
        for element in path
    ]
    if not parts:
        return KEY_SEPARATOR
    return KEY_SEPARATOR + KEY_SEPARATOR.join(parts)


def _declared_shown(validator_value: Any) -> str:
    """Return the schema value one keyword declares, as one bounded JSON fragment.

    The fragment is schema text rather than record content, so it is reported
    whether or not record values are shown.
    """
    try:
        rendered = json.dumps(validator_value, ensure_ascii=True, sort_keys=True)
    except (TypeError, ValueError):
        rendered = str(validator_value)
    return _escaped(rendered, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)


def _rejected_shape(instance: Any) -> str:
    """Return the JSON type and size of a rejected value, carrying no part of it."""
    if isinstance(instance, str):
        return f"a string of {len(instance)} characters"
    if instance is None:
        return "null"
    if isinstance(instance, bool):
        return "a boolean"
    if isinstance(instance, (int, float)):
        return f"a {_type_name(instance)}"
    if isinstance(instance, Mapping):
        return f"an object of {len(instance)} members"
    if isinstance(instance, (list, tuple)):
        return f"an array of {len(instance)} elements"
    return f"a {_type_name(instance)}"


def _offending_names(error: jsonschema.exceptions.ValidationError) -> str:
    """Return the property names the breached keyword is about, or an empty fragment.

    A ``required`` violation names the properties the object omits and an
    ``additionalProperties`` violation names the properties the schema does not
    declare. Both are member names, which are part of the landing contract rather
    than landed values. Every other keyword yields an empty fragment.
    """
    instance = error.instance
    if not isinstance(instance, Mapping):
        return ""
    if error.validator == "required" and isinstance(error.validator_value, list):
        return _listed(
            [str(name) for name in error.validator_value if name not in instance]
        )
    if error.validator == "additionalProperties":
        declared = (
            error.schema.get("properties", {})
            if isinstance(error.schema, Mapping)
            else {}
        )
        return _listed(sorted(str(name) for name in instance if name not in declared))
    return ""


def _violation(error: jsonschema.exceptions.ValidationError) -> str:
    """Return one schema violation as a pointer, the breached constraint and a shape.

    The fragment names the JSON Pointer of the rejected value, the schema keyword
    that rejected it, the value the schema declares for that keyword, the
    property names the keyword is about where it has any, and the JSON type and
    size of the rejected value. The library's own message is used only when record
    values are shown, since it embeds the value it rejected.
    """
    pointer = _json_pointer(error.absolute_path)
    if show_identifiers_enabled():
        return (
            f"at {pointer}: "
            f"{_escaped(error.message, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}"
        )
    fragments = [
        f"the {_shown(str(error.validator))} constraint is not satisfied",
        f"the schema declares {_declared_shown(error.validator_value)}",
    ]
    names = _offending_names(error)
    if names:
        fragments.append(f"the properties at issue are {names}")
    fragments.append(f"the rejected value is {_rejected_shape(error.instance)}")
    return f"at {pointer}: " + "; ".join(fragments)


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


class LandingContract(NamedTuple):
    """The landing contract one run validates its object against.

    ``columns`` are the landed column names in the order the schema declares them,
    which is the order of the row written, and ``validator`` applies every constraint
    of the same schema document.
    """

    columns: tuple[str, ...]
    validator: Draft202012Validator


def landing_contract(path: Path = DEFAULT_SCHEMA) -> LandingContract:
    """Return the landed column names and the validator of the schema at ``path``.

    The schema is read once, so the columns the row is written from and the
    constraints the object is validated against come from the same document.

    Raises ``SchemaError`` when the schema cannot be read, does not declare the
    landed columns, or is not a usable 2020-12 schema.
    """
    schema = load_schema(path)
    return LandingContract(
        read_column_names(schema, path), build_validator(schema, path)
    )

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


def _from_environment(names: Sequence[str]) -> tuple[str | None, str | None]:
    """Return the first value among ``names`` that carries content, and its name.

    A variable that is set to the empty string or to whitespace alone counts as
    unset and is passed over, so the next name is consulted and then the
    documented default applies; that is the empty-value resolution every
    command-line tool of this bridge applies, and the local output of
    modernization/dbt/genapp_rqi/profiles.example.yml resolves
    ``DATABASE_VARIABLES`` the same way. The value carried is returned exactly as
    the environment holds it: nothing is trimmed, so a setting that would be
    invalid with surrounding whitespace is reported rather than silently
    repaired. Returns ``(None, None)`` when no name carries content. Only the name
    is ever quoted in a diagnostic.
    """
    for name in names:
        value = os.environ.get(name)
        if value is not None and value.strip():
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

    The name is held to the general-purpose bucket naming rules, which every
    addressable bucket satisfies whichever endpoint serves it:
    ``MIN_BUCKET_CHARACTERS`` to ``MAX_BUCKET_CHARACTERS`` characters drawn from
    lowercase letters, digits, dot and hyphen, beginning and ending with a letter
    or a digit, carrying no two adjacent dots, not written as an IPv4 address,
    and carrying none of the prefixes or suffixes the service reserves. A name
    outside those rules names no bucket that could be addressed, so it is refused
    before a client exists rather than reported as a failed request.

    Raises ``ConfigurationError`` when the name breaches any of those rules.
    """
    if not (MIN_BUCKET_CHARACTERS <= len(value) <= MAX_BUCKET_CHARACTERS):
        raise ConfigurationError(
            f"the bucket name from {origin} holds {len(value)} characters: "
            f"{_shown(value)}; between {MIN_BUCKET_CHARACTERS} and "
            f"{MAX_BUCKET_CHARACTERS} are accepted"
        )
    if not _BUCKET_SHAPE.fullmatch(value):
        raise ConfigurationError(
            f"the bucket name from {origin} is not a general-purpose bucket name: "
            f"{_shown(value)}; it carries lowercase letters, digits, dot and "
            "hyphen only, and begins and ends with a letter or a digit"
        )
    if _BUCKET_ADJACENT_DOTS in value:
        raise ConfigurationError(
            f"the bucket name from {origin} carries two adjacent dots: "
            f"{_shown(value)}; a general-purpose bucket name does not"
        )
    if _BUCKET_IPV4_SHAPE.fullmatch(value):
        raise ConfigurationError(
            f"the bucket name from {origin} is written as an IPv4 address: "
            f"{_shown(value)}; a general-purpose bucket name is not"
        )
    for prefix in BUCKET_RESERVED_PREFIXES:
        if value.startswith(prefix):
            raise ConfigurationError(
                f"the bucket name from {origin} begins with the reserved prefix "
                f"{_shown(prefix)}: {_shown(value)}"
            )
    for suffix in BUCKET_RESERVED_SUFFIXES:
        if value.endswith(suffix):
            raise ConfigurationError(
                f"the bucket name from {origin} ends with the reserved suffix "
                f"{_shown(suffix)}: {_shown(value)}"
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
    """Return the entity element of the landing prefix, which is ``LANDING_ENTITY``.

    ``supplied`` is the ``--entity`` value. Omitted, the literal applies;
    supplied, it must repeat that literal, so this loader can only address the
    canonical policy-issue prefix land_to_s3.py writes to.

    Raises ``ConfigurationError`` when ``supplied`` carries any other value.
    """
    if supplied is not None and supplied != LANDING_ENTITY:
        raise ConfigurationError(
            f"the entity from --entity is {_shown(supplied)}: this bridge lands one "
            f"entity and the landing prefix carries {_shown(LANDING_ENTITY)}; omit "
            "--entity or repeat that literal"
        )
    return _require_segment(LANDING_ENTITY, "entity", "the landing contract")


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


def part_number_text(part: int) -> str:
    """Return ``part`` as the digits the object name of that part carries.

    The value is written zero-padded to ``PART_NUMBER_DIGITS`` digits, which is the
    width modernization/landing/land_to_s3.py writes, so the name rebuilt here is the
    name that step wrote.

    Raises ``ConfigurationError`` when ``part`` is not a whole number between
    ``MIN_PART_NUMBER`` and ``MAX_PART_NUMBER``.
    """
    if isinstance(part, bool) or not isinstance(part, int):
        raise ConfigurationError(
            f"the landing part is {_display(part)}; a whole number between "
            f"{MIN_PART_NUMBER} and {MAX_PART_NUMBER} is required"
        )
    if not (MIN_PART_NUMBER <= part <= MAX_PART_NUMBER):
        raise ConfigurationError(
            f"the landing part is {part}; {MIN_PART_NUMBER} to {MAX_PART_NUMBER} are "
            f"accepted, which is what {PART_NUMBER_DIGITS} digits of the object name "
            "carry"
        )
    return f"{part:0{PART_NUMBER_DIGITS}d}"


def object_name(part: int = DEFAULT_PART_NUMBER) -> str:
    """Return the object name of the landed record of ``part``.

    Raises ``ConfigurationError`` when ``part`` is not an accepted part number.
    """
    return OBJECT_NAME_TEMPLATE.format(part=part_number_text(part))


def resolve_part(supplied: str | None) -> int:
    """Return the part element of the landed object name, as a number.

    ``supplied`` is the ``--part`` value, written as 1 to ``PART_NUMBER_DIGITS``
    decimal digits with or without leading zeros; ``DEFAULT_PART_NUMBER`` applies when
    it is absent, so a run that names no part reads the object a landing that named no
    part wrote. The number reaches the object name zero-padded to
    ``PART_NUMBER_DIGITS`` digits, so ``1`` and ``0001`` name the same object.

    Raises ``ConfigurationError`` when ``supplied`` is not such a number.
    """
    if supplied is None:
        return DEFAULT_PART_NUMBER
    if not _PART_NUMBER_SHAPE.fullmatch(supplied):
        raise ConfigurationError(
            f"the landing part from --part is not 1 to {PART_NUMBER_DIGITS} decimal "
            f"digits: {_shown(supplied)}; {MIN_PART_NUMBER} to {MAX_PART_NUMBER} are "
            f"accepted and the value reaches the object name as "
            f"{OBJECT_NAME_TEMPLATE.format(part='NNNN')}"
        )
    return int(supplied, 10)


def _is_loopback_host(host: str) -> bool:
    """Return whether ``host`` is a loopback literal or exactly the loopback name.

    A host is accepted for the literal it is: an IPv4 address in 127.0.0.0/8,
    the IPv6 address ::1 or any other loopback IPv6 literal, or
    ``LOOPBACK_HOST_NAME`` compared without case. No name is resolved, so a name
    that resolves to a loopback address is not a loopback host under this test,
    and an alternative spelling that is not itself a valid address literal, such
    as a bare integer, is refused.
    """
    if host.casefold() == LOOPBACK_HOST_NAME:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _refuse_endpoint(origin: str, fault: str) -> NoReturn:
    """Raise ``ConfigurationError`` reporting ``fault`` without echoing the endpoint.

    The endpoint is a setting this tool never discloses, so the diagnostic names
    where the value came from and what is accepted, never the value itself.
    """
    raise ConfigurationError(
        f"the endpoint from {origin} is not accepted: {fault}. A local endpoint is "
        f"{' or '.join(ACCEPTED_ENDPOINT_SCHEMES)} on a loopback host "
        f"(127.0.0.0/8, ::1 or {LOOPBACK_HOST_NAME}) with an explicit port of "
        f"{ENDPOINT_PORT_FLOOR} or above, no embedded credentials, no query, no "
        "fragment and no path; leave the setting unset to address AWS S3. The value "
        "is not echoed"
    )


def require_loopback_endpoint(value: str, origin: str) -> str:
    """Return ``value`` confirmed to be a local-substitute S3 endpoint.

    An accepted endpoint carries at most ``MAX_ENDPOINT_CHARACTERS`` characters, no
    control character, a scheme from ``ACCEPTED_ENDPOINT_SCHEMES``, a host that
    ``_is_loopback_host`` accepts, an explicit port at or above
    ``ENDPOINT_PORT_FLOOR``, no embedded credentials, a path in
    ``ACCEPTED_ENDPOINT_PATHS``, no query and no fragment. Every check runs before
    any client, credential or request exists, and every port from that floor up is
    accepted, so several local endpoints can run side by side while no override
    reaches a privileged loopback service.

    Raises ``ConfigurationError`` naming the rejected element, and never the value,
    for every other endpoint.
    """
    if len(value) > MAX_ENDPOINT_CHARACTERS:
        _refuse_endpoint(
            origin,
            f"it holds {len(value)} characters, and at most "
            f"{MAX_ENDPOINT_CHARACTERS} are accepted",
        )
    if _CONTROL_CHARACTERS.search(value):
        _refuse_endpoint(origin, "it carries a control character")
    if any(character.isspace() for character in value):
        _refuse_endpoint(origin, "it carries whitespace")
    try:
        parts = urllib.parse.urlsplit(value)
    except ValueError:
        _refuse_endpoint(origin, "it cannot be parsed as a URL")
    if parts.scheme not in ACCEPTED_ENDPOINT_SCHEMES:
        _refuse_endpoint(origin, "its scheme is not accepted")
    if "@" in parts.netloc:
        _refuse_endpoint(origin, "it carries embedded credentials before the host")
    if parts.query:
        _refuse_endpoint(origin, "it carries a query")
    if parts.fragment:
        _refuse_endpoint(origin, "it carries a fragment")
    if parts.path not in ACCEPTED_ENDPOINT_PATHS:
        _refuse_endpoint(origin, "it carries a path")
    try:
        host = parts.hostname
        port = parts.port
    except ValueError:
        _refuse_endpoint(origin, "its port is not a number")
    if not host:
        _refuse_endpoint(origin, "it names no host")
    if not _is_loopback_host(host):
        _refuse_endpoint(origin, "its host is not a loopback address")
    if port is None:
        _refuse_endpoint(origin, "it names no port")
    if port < ENDPOINT_PORT_FLOOR:
        _refuse_endpoint(origin, f"its port is below {ENDPOINT_PORT_FLOOR}")
    return value


def resolve_endpoint_url(supplied: str | None) -> tuple[str | None, str]:
    """Return the S3 endpoint to address and the origin it came from.

    ``supplied`` is the ``--endpoint-url`` value and the ``S3_ENDPOINT_URL``
    environment variable is consulted when it is absent. A returned value
    directs the client at that endpoint and is a local substitute confirmed by
    ``require_loopback_endpoint``; None means no endpoint was resolved, which
    ``confirm_run_mode`` then refuses, since this tool runs on the local branch
    alone. The origin names where the value came from, so a refusal can name the
    setting that carried it without echoing the endpoint.

    Raises ``ConfigurationError``, carrying no endpoint value, when the resolved
    value is not an accepted local-substitute endpoint.
    """
    value, origin = _resolved(supplied, "--endpoint-url", (ENDPOINT_URL_VARIABLE,))
    if value is None:
        return None, origin
    return require_loopback_endpoint(value, origin), origin


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


def resolve_run_mode(supplied: str | None) -> tuple[str, str]:
    """Return the run mode this run addresses and the origin it came from.

    ``supplied`` is the ``--run-mode`` value, which wins whenever it is present,
    and the ``DBT_TARGET`` environment variable is consulted when it is absent;
    ``DEFAULT_RUN_MODE`` applies when neither carries a value. The accepted values
    are ``RUN_MODES``, which are the output names of
    modernization/dbt/genapp_rqi/profiles.example.yml, so the one setting that
    selects the dbt output also selects the branch this tool and
    modernization/landing/land_to_s3.py address.

    Raises ``ConfigurationError`` when the resolved value is not one of
    ``RUN_MODES``. A value outside that set is never mapped onto the nearest one: a
    misspelled setting would otherwise decide silently whether this run writes the
    local database.
    """
    value, origin = _resolved(supplied, "--run-mode", (RUN_MODE_VARIABLE,))
    if value is None:
        return DEFAULT_RUN_MODE, "the built-in default"
    if value not in RUN_MODES:
        raise ConfigurationError(
            f"the run mode from {origin} is {_shown(value)}: "
            f"{_quote_all(RUN_MODES)} are accepted; {_shown(RUN_MODE_LOCAL)} runs "
            f"this loader and {_shown(RUN_MODE_REAL)} loads the raw relation "
            f"through {REAL_MODE_LOADER} instead"
        )
    return value, origin


def confirm_run_mode(
    run_mode: str, run_mode_origin: str, endpoint_url: str | None, endpoint_origin: str
) -> None:
    """Confirm this tool is the loader the resolved run mode calls for.

    This tool writes the DuckDB database of the local substitute, so it runs in
    ``RUN_MODE_LOCAL`` alone: in ``RUN_MODE_REAL`` the raw relation is loaded by
    ``REAL_MODE_LOADER`` against Redshift, and running this tool there would leave
    a local row that no step of that run reads while the real relation stayed
    empty. ``RUN_MODE_LOCAL`` also requires a resolved endpoint, since the object
    to load sits at the local substitute. Returns None when the run mode and the
    endpoint agree with each other and with this tool.

    This is checked before a session, a client or a credential exists and before
    the database is opened, so a conflicting pair is reported without a request
    being signed and without a database file being created.

    Raises ``ConfigurationError`` naming both settings and where each came from
    when they do not agree.
    """
    if run_mode == RUN_MODE_REAL:
        raise ConfigurationError(
            f"run mode {_shown(run_mode)} from {run_mode_origin} addresses the real "
            f"target, whose raw relation is loaded by {REAL_MODE_LOADER}, not by "
            f"this tool; select run mode {_shown(RUN_MODE_LOCAL)} to load the local "
            "DuckDB database"
        )
    if endpoint_url is None:
        raise ConfigurationError(
            f"run mode {_shown(run_mode)} from {run_mode_origin} loads the object "
            "from the local substitute, but no endpoint is set: supply "
            f"--endpoint-url or set the {ENDPOINT_URL_VARIABLE} environment "
            "variable to the loopback endpoint serving it"
        )






def resolved_database_root() -> Path:
    """Return ``ALLOWED_DATABASE_ROOT`` resolved through every symbolic link.

    This is the one directory a database file may sit in, in the form every path
    check compares against.
    """
    return Path(os.path.realpath(ALLOWED_DATABASE_ROOT))


def is_database_root(candidate: str | os.PathLike[str]) -> bool:
    """Report whether ``candidate`` resolves to ``resolved_database_root``.

    ``candidate`` is resolved through every symbolic link, so a link, a
    ``/proc/self/cwd`` alias and a relative path are judged as the directory they
    reach. A sub-directory of that root is not that root and is reported false.

    This predicate is the whole containment rule: ``resolve_database_path`` applies
    it to the parent of the ``--database`` value before any client exists, and
    ``open_database`` applies it again to the path it is handed, so the setting a
    caller supplies and the file the connection opens are held to one rule.
    """
    return Path(os.path.realpath(candidate)) == resolved_database_root()


def resolve_database_path(supplied: str | None) -> Path:
    """Return the DuckDB database file to open, named inside the validation directory.

    ``supplied`` is the ``--database`` value; ``LOCAL_DUCKDB_PATH`` and then
    ``DUCKDB_DATABASE`` are consulted when it is absent, and ``DEFAULT_DATABASE``
    when none carries a value. An in-memory database is refused, so a load always
    reaches a file a later step can read.

    The resolved path is the one this tool creates parent directories for and
    writes, so it is contained rather than merely inspected: the candidate and its
    parent are resolved through every symbolic link, and ``is_database_root`` must
    hold for that parent, which keeps a destination out of ``base/``, out of the
    authored source tree, out of any directory a link points at, out of the
    directories that hold this bridge's committed evidence and out of any
    sub-directory of ``DATABASE_DIRECTORY`` itself. A path in a directory below
    ``DATABASE_DIRECTORY`` is a rejected setting, and it is rejected here, where
    every other ``--database`` fault is rejected, rather than at the open that
    ``open_database`` guards: the whole policy is applied before the object is
    downloaded. The path itself may not be a symbolic link, may not name an existing
    entry that is not a regular file, and may not name one of
    ``RESERVED_DATABASE_NAMES``. The returned path is absolute and its parent is
    ``resolved_database_root``, which is the path ``open_database`` accepts.

    Every one of these refusals is a ``ConfigurationError``, so a database setting a
    caller cannot use is reported with the configuration status before any session,
    client or credential exists, before the object is downloaded and before a
    database file is created.

    Raises ``ConfigurationError`` when the resolved value is empty, names an
    in-memory database, does not name a file directly inside ``DATABASE_DIRECTORY``,
    resolves into a directory below it, is a symbolic link, names an existing
    non-regular entry, or names an authored file of that directory.
    """
    value, origin = _resolved(supplied, "--database", DATABASE_VARIABLES)
    if value is None:
        value, origin = str(DEFAULT_DATABASE), "the built-in default"
    if not value.strip():
        raise ConfigurationError(f"the database path from {origin} is empty")
    if value == IN_MEMORY_DATABASE:
        raise ConfigurationError(
            f"the database path from {origin} names an in-memory database: "
            f"{_shown(value)}; a file the following step can read is required"
        )
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    if candidate.is_symlink():
        raise ConfigurationError(
            f"the database path from {origin} is a symbolic link: "
            f"{_path_shown(value)}; the database is written to a regular file inside "
            f"{_path_shown(DATABASE_DIRECTORY)}"
        )
    if not candidate.name:
        raise ConfigurationError(
            f"the database path from {origin} names a directory rather than a file: "
            f"{_path_shown(value)}"
        )
    contained_root = resolved_database_root()
    parent = Path(os.path.realpath(candidate.parent))
    if not is_database_root(candidate.parent):
        raise ConfigurationError(
            f"the database path from {origin} does not name a file directly inside "
            f"{_path_shown(contained_root)}: {_path_shown(value)} resolves into "
            f"{_path_shown(parent)}, which is outside that one directory; name a file "
            f"in it instead, and {_path_shown(DEFAULT_DATABASE)} is the path this "
            f"bridge keeps its database at"
        )
    resolved = parent / candidate.name
    if resolved.name in RESERVED_DATABASE_NAMES:
        raise ConfigurationError(
            f"the database path from {origin} names {_shown(resolved.name)}: "
            f"{_path_shown(value)}; that is an authored file of "
            f"{_path_shown(contained_root)} and is never opened as a database"
        )
    if resolved.is_symlink():
        raise ConfigurationError(
            f"the database path from {origin} resolves to a symbolic link: "
            f"{_path_shown(value)}; the database is written to a regular file"
        )
    if resolved.exists() and not resolved.is_file():
        raise ConfigurationError(
            f"the database path from {origin} names an entry that is not a regular "
            f"file: {_path_shown(value)}"
        )
    return resolved


def resolve_ddl_paths(apply_ddl: bool) -> tuple[Path, ...]:
    """Return the SQL scripts to apply before the row is written, in apply order.

    The scripts are exactly ``DDL_SCRIPT_NAMES``, read from ``DDL_DIRECTORY`` in
    that order: the shared script creating the schemas and the shared script
    creating the raw relation. The list is fixed in this module, so no caller and no
    file added to that directory can introduce another script, and no SQL beyond
    those two files is ever executed. With ``apply_ddl`` false no script is returned
    and none is read.

    Raises ``ConfigurationError`` when one of the two scripts is absent, is a
    symbolic link, is not a regular file, or does not resolve inside
    ``DDL_DIRECTORY``.
    """
    if not apply_ddl:
        return ()
    directory = Path(os.path.realpath(DDL_DIRECTORY))
    paths: list[Path] = []
    for name in DDL_SCRIPT_NAMES:
        path = DDL_DIRECTORY / name
        if path.is_symlink():
            raise ConfigurationError(
                f"the shared SQL script {_shown(name)} is a symbolic link: "
                f"{_path_shown(path)}; the two scripts this tool applies are regular "
                f"files of {_path_shown(DDL_DIRECTORY)}"
            )
        if not path.is_file():
            raise ConfigurationError(
                f"the shared SQL script {_shown(name)} is absent or is not a regular "
                f"file: {_path_shown(path)}; this tool applies "
                f"{_listed(list(DDL_SCRIPT_NAMES))} from "
                f"{_path_shown(DDL_DIRECTORY)}, or --no-ddl to apply none"
            )
        resolved = Path(os.path.realpath(path))
        if resolved.parent != directory:
            raise ConfigurationError(
                f"the shared SQL script {_shown(name)} resolves outside "
                f"{_path_shown(directory)}: {_path_shown(resolved)}"
            )
        paths.append(resolved)
    return tuple(paths)


# ---------------------------------------------------------------------------
# Key construction
# ---------------------------------------------------------------------------


def build_landing_key(
    source_system_key: str,
    entity: str,
    extract_date: datetime.date,
    part: int = DEFAULT_PART_NUMBER,
) -> str:
    """Return the landing object key for one part of one extract.

    The key is ``LANDING_KEY_ROOT``, then one Hive-style ``field=value`` segment
    per entry of ``PARTITION_FIELDS`` in that order, then the object name of
    ``part``, with no leading separator, no empty segment and no percent-encoding
    of the equals sign. The date is written as ``EXTRACT_DATE_FORM``. This is the
    key land_to_s3.py writes for the same values, and with no part supplied it is
    the key that step writes for a landing that named no part. ``entity`` must be
    ``LANDING_ENTITY``, so every key this function returns addresses the canonical
    policy-issue prefix.

    Raises ``ConfigurationError`` when a supplied value cannot form one path
    segment, when ``entity`` is not ``LANDING_ENTITY``, or when ``part`` is not an
    accepted part number.
    """
    if entity != LANDING_ENTITY:
        raise ConfigurationError(
            f"the entity element of the landing key is {_shown(entity)}; the landing "
            f"prefix carries {_shown(LANDING_ENTITY)}"
        )
    values = {
        "source_system_key": _require_segment(
            source_system_key, "source-system key", "the caller"
        ),
        "entity": _require_segment(entity, "entity", "the caller"),
        "extract_date": extract_date.isoformat(),
    }
    segments = [LANDING_KEY_ROOT]
    segments.extend(f"{field}={values[field]}" for field in PARTITION_FIELDS)
    segments.append(object_name(part))
    return KEY_SEPARATOR.join(segments)


def build_object_uri(bucket: str, key: str) -> str:
    """Return the ``s3://`` URI naming the object ``key`` in ``bucket``."""
    return f"{SERVICE_NAME}{URI_SCHEME_SEPARATOR}{bucket}{KEY_SEPARATOR}{key}"


def manifest_object_name(part: int = DEFAULT_PART_NUMBER) -> str:
    """Return the name of the COPY manifest of the landed part ``part``.

    The name is ``MANIFEST_OBJECT_NAME_TEMPLATE`` carrying the part zero-padded to
    ``PART_NUMBER_DIGITS`` digits, which is the name
    modernization/landing/land_to_s3.py writes beside the record of that part.

    Raises ``ConfigurationError`` when ``part`` is not an accepted part number.
    """
    return MANIFEST_OBJECT_NAME_TEMPLATE.format(part=part_number_text(part))


def sibling_manifest_key(object_key: str) -> str:
    """Return the key of the COPY manifest written beside ``object_key``.

    The manifest sits under the same landing prefix with the object name replaced by
    the manifest name of the same part, which is where
    modernization/landing/land_to_s3.py writes it. Deriving it from the key that was
    downloaded, rather than rebuilding it from the run's settings, keeps the manifest
    read the sibling of the object read: the two differ in their object name alone,
    the part they carry is the same, and no setting can point this read at the
    manifest of another part or prefix.

    Raises ``ObjectError`` when ``object_key`` is not the key of one landed record,
    which the caller has already confirmed it is, so this states that invariant
    rather than trusting it.
    """
    prefix, separator, name = object_key.rpartition(KEY_SEPARATOR)
    if not separator or not _OBJECT_NAME_SHAPE.fullmatch(name):
        raise ObjectError(
            f"the landed object {_shown(object_key, MAX_DIAGNOSTIC_PATH_CHARACTERS)} "
            f"is not named {OBJECT_NAME_TEMPLATE.format(part='NNNN')} under a landing "
            "prefix, so the COPY manifest that binds it cannot be named"
        )
    carried_part = name[len("part-") : -len(".json")]
    return (
        f"{prefix}{separator}"
        f"{MANIFEST_OBJECT_NAME_TEMPLATE.format(part=carried_part)}"
    )


def parse_object_reference(supplied: str, bucket: str) -> str:
    """Return the object key ``supplied`` names, confirming any bucket it carries.

    ``supplied`` is either a bare object key or the ``s3://bucket/key`` URI
    land_to_s3.py prints, so the line that step wrote can be passed straight in.
    A URI's authority must equal ``bucket``. A leading separator is refused
    rather than trimmed, and so is a key carrying an empty segment, whitespace or
    a control character, so the key requested is the key the caller wrote. The
    key's own segments are reconciled with the resolved settings separately, by
    ``confirm_landing_key``.

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


def confirm_landing_key(
    key: str,
    source_system_key: str,
    entity: str,
    extract_date: datetime.date,
    origin: str,
    part: int = DEFAULT_PART_NUMBER,
) -> str:
    """Confirm ``key`` is the landing key the resolved settings describe, and return it.

    The key is split on ``KEY_SEPARATOR`` and matched against the landing template
    segment by segment: ``LANDING_KEY_ROOT``, one ``field=value`` segment per entry
    of ``PARTITION_FIELDS`` in that order, and the object name of ``part``. Each
    field name must be the expected one and each value must equal the resolved
    ``source_system_key``, ``entity`` or ``extract_date``, and the object name must
    be the name of one landed record - ``part-<NNNN>.json`` - carrying the resolved
    part. The key therefore
    confirms the settings rather than replacing them: a key naming another
    source system, another entity, another day or another part is refused, so a row
    can never be loaded from an object the run's own settings do not
    describe, and the prefix the row came from is always the prefix the run
    resolved.

    Returns the key unchanged when every segment matches.

    Raises ``ConfigurationError`` naming the segment that differs, the value it
    carries and the resolved value it was compared with, so the caller can see
    which setting to supply.
    """
    expected = {
        "source_system_key": source_system_key,
        "entity": entity,
        "extract_date": extract_date.isoformat(),
    }
    template = build_landing_key(source_system_key, entity, extract_date, part)
    segments = key.split(KEY_SEPARATOR)
    wanted = len(PARTITION_FIELDS) + 2
    if len(segments) != wanted:
        raise ConfigurationError(
            f"the object from {origin} carries {len(segments)} key segments: "
            f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; the landing key carries "
            f"{wanted}, as {_shown(template, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
        )
    if segments[0] != LANDING_KEY_ROOT:
        raise ConfigurationError(
            f"the object from {origin} begins with {_shown(segments[0])} rather than "
            f"{_shown(LANDING_KEY_ROOT)}: "
            f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
        )
    for position, field in enumerate(PARTITION_FIELDS, start=1):
        segment = segments[position]
        name, separator, carried = segment.partition("=")
        if not separator:
            raise ConfigurationError(
                f"the object from {origin} carries {_shown(segment)} where the "
                f"landing key carries {_shown(f'{field}={expected[field]}')}: "
                f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; each partition "
                "segment is written field=value"
            )
        if name != field:
            raise ConfigurationError(
                f"the object from {origin} carries partition field {_shown(name)} "
                f"where the landing key carries {_shown(field)}: "
                f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; the fields are "
                f"{_quote_all(PARTITION_FIELDS)}, in that order"
            )
        if carried != expected[field]:
            raise ConfigurationError(
                f"the object from {origin} carries {_shown(name)} "
                f"{_shown(carried)} while the resolved value is "
                f"{_shown(expected[field])}: the two must agree, so supply the "
                f"matching --{field.replace('_', '-')} or omit {origin} to build "
                "the key from the resolved settings"
            )
    carried_name = segments[-1]
    if not _OBJECT_NAME_SHAPE.fullmatch(carried_name):
        raise ConfigurationError(
            f"the object from {origin} is named {_shown(carried_name)}, which is not "
            f"the name of a landed record: "
            f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; one record is written per "
            f"part, as {OBJECT_NAME_TEMPLATE.format(part='NNNN')}"
        )
    if carried_name != object_name(part):
        raise ConfigurationError(
            f"the object from {origin} is named {_shown(carried_name)} while the "
            f"resolved part names {_shown(object_name(part))}: "
            f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; supply the matching "
            f"--part or omit {origin} to build the key from the resolved settings"
        )
    return key


def resolve_object_key(
    supplied: str | None,
    bucket: str,
    source_system_key: str,
    entity: str,
    extract_date: datetime.date,
    part: int = DEFAULT_PART_NUMBER,
) -> str:
    """Return the key of the object to download.

    The key is always the one ``build_landing_key`` rebuilds from
    ``source_system_key``, ``entity``, ``extract_date`` and ``part``, which is the
    key land_to_s3.py wrote for those values. ``supplied`` is the ``--key``
    value, accepted as a bare key or as the ``s3://`` URI that step printed, and it
    must equal that rebuilt key: it confirms which object is being loaded rather
    than selecting a different one, so no stale object, object of another part or
    object of another entity can be loaded under this run's settings. A key naming
    another part of the same prefix is refused here rather than loaded, and the
    diagnostic names ``--part``, which is the setting that selects it.

    Raises ``ConfigurationError`` when ``supplied`` is not a usable object
    reference, when it does not equal the rebuilt key, or when a rebuilt segment is
    not usable.
    """
    rebuilt = build_landing_key(source_system_key, entity, extract_date, part)
    if supplied is None:
        return rebuilt
    requested = parse_object_reference(supplied, bucket)
    if requested != rebuilt:
        confirm_landing_key(
            requested, source_system_key, entity, extract_date, "--key", part
        )
        raise ConfigurationError(
            "the object from --key is not the object this run's settings name: "
            f"--key asks for {_shown(requested, MAX_DIAGNOSTIC_PATH_CHARACTERS)} and "
            f"this run names "
            f"{_shown(rebuilt, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; supply the "
            "--source-system-key, --extract-date, --part and bucket the object was "
            "landed with, or omit --key"
        )
    return rebuilt


# ---------------------------------------------------------------------------
# Client, credentials and access
# ---------------------------------------------------------------------------


def _client_config() -> Config:
    """Return the connection behaviour applied to every request.

    A failing endpoint is abandoned after ``CONNECT_TIMEOUT_SECONDS`` and a
    stalled response after ``READ_TIMEOUT_SECONDS``. ``total_max_attempts`` bounds
    the calls one request makes at ``MAX_ATTEMPTS`` including the first, which is the
    bound ``max_attempts`` would have exceeded by one, so an unreachable target
    cannot hold the caller open indefinitely and the bound the code states is the
    bound the client applies. Every endpoint configured in the environment or in a
    profile, including AWS_ENDPOINT_URL and AWS_ENDPOINT_URL_S3, is ignored: the
    only endpoint that can apply is the one ``resolve_endpoint_url`` accepted and
    this module passes to the client explicitly.
    """
    return Config(
        connect_timeout=CONNECT_TIMEOUT_SECONDS,
        read_timeout=READ_TIMEOUT_SECONDS,
        retries={"total_max_attempts": MAX_ATTEMPTS, "mode": RETRY_MODE},
        ignore_configured_endpoint_urls=True,
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
    diagnostic carries no credential or token value; a reason text the endpoint
    library supplied may name the endpoint it addressed, which is the setting the
    reader has to correct.
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


def confirm_credentials(session: boto3.session.Session) -> Any:
    """Confirm ``session`` resolves a usable set of credentials, and return them.

    The session's own providers do the resolving, so a variable whose name
    merely begins with AWS is never taken for a credential. An incomplete set
    surfaces as ``PartialCredentialsError`` from that resolution. The resolved
    credentials are returned so their provenance can be confirmed before a request
    is signed; no credential value is read beyond confirming one is present, and
    none is ever printed.

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
    return credentials


def confirm_credential_provenance(credentials: Any, endpoint_url: str | None) -> None:
    """Confirm the resolved credentials may be signed against the endpoint addressed.

    With no endpoint addressed the request goes to AWS S3, where every credential
    provider is appropriate, and this returns None. With a custom endpoint
    addressed the request goes to the loopback host serving the local substitute,
    and only credentials that came from the environment or were passed to the
    session directly are signed against it: those are the throwaway values a local
    endpoint is driven with. A credential resolved from a shared credentials file,
    a configured profile, single sign-on, an assumed role, container metadata or
    instance metadata belongs to a real account, and sending a request signed with
    it to a process listening on a local port would disclose that account's
    signature to whatever holds the port. Such a run is refused rather than
    downgraded. The method name is read from the credentials botocore resolved; no
    credential value is read or printed.

    Raises ``ConfigurationError`` naming the resolution method when the credentials
    did not come from an accepted provider.
    """
    if endpoint_url is None:
        return
    method = getattr(credentials, "method", None)
    if not isinstance(method, str) or not method:
        raise ConfigurationError(
            "the resolved credentials record no resolution method, so they cannot "
            "be confirmed as local-substitute credentials while a custom endpoint "
            f"is addressed: set {' and '.join(CREDENTIAL_VARIABLES)} in the "
            "environment for the local endpoint"
        )
    if method not in LOCAL_CREDENTIAL_METHODS:
        raise ConfigurationError(
            f"the resolved credentials came from {_shown(method)} while a custom "
            "endpoint is addressed: those credentials belong to a real account and "
            "are never signed against a local endpoint. Set "
            f"{' and '.join(CREDENTIAL_VARIABLES)} in the environment for the local "
            f"endpoint, which resolves as {_quote_all(LOCAL_CREDENTIAL_METHODS)}"
        )


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

    A session is created, its region is confirmed, its credentials are confirmed,
    their provenance is confirmed against the endpoint being addressed, and a
    client is built against ``endpoint_url`` when one was supplied. Nothing is
    requested from the service here and nothing is created, so a credential that
    may not be signed against the endpoint is refused before any request exists.
    The resolved region is noted on stderr; neither the endpoint nor any credential
    value is printed.

    Raises ``ConfigurationError`` naming the setting to supply when the region,
    the credentials or the client cannot be resolved, or when the resolved
    credentials may not be signed against the endpoint being addressed.
    """
    session = build_session(region)
    resolved_region = resolve_session_region(session)
    credentials = confirm_credentials(session)
    confirm_credential_provenance(credentials, endpoint_url)
    client = build_s3_client(session, endpoint_url)
    target = "a loopback endpoint" if endpoint_url is not None else "AWS S3"
    _note(
        f"reading bucket {_shown(bucket)} in region {_shown(resolved_region)} "
        f"through {target}"
    )
    return client


class ObjectIdentity(NamedTuple):
    """The immutable identity a head request recorded for one landed object.

    ``etag`` is the entity tag the store reported, with any surrounding double
    quotes removed, ``version_id`` the version the store assigned or
    ``NOT_VERSIONED`` on a bucket that keeps none, and ``content_length`` the
    byte count the store reported. ``recorded_sha256`` and
    ``recorded_content_length`` are the land-time digest and byte count
    modernization/landing/land_to_s3.py wrote as user metadata of the object, or
    None where the object carries no usable value under that name, which
    ``confirm_recorded_identity`` refuses: the store computes neither of them, so
    they are what the landing step recorded rather than what this request
    observed.
    """

    etag: str
    version_id: str
    content_length: int
    recorded_sha256: str | None = None
    recorded_content_length: int | None = None


class DownloadedObject(NamedTuple):
    """The bytes of one landed object and the identity they were confirmed against.

    ``body`` is the object body exactly as stored, ``identity`` is what the head
    request recorded before the download, and ``sha256`` is the digest of
    ``body`` as computed after it arrived.
    """

    body: bytes
    identity: ObjectIdentity
    sha256: str


def _reported_etag(value: Any) -> str:
    """Return the entity tag ``value`` carries, without its surrounding quotes.

    Raises ``AccessError`` when the store reported no usable entity tag, since
    the download is conditioned on it.
    """
    if not isinstance(value, str) or not value.strip().strip('"'):
        raise AccessError(
            f"the endpoint reported {_display(value)} as the entity tag of the "
            "landed object; an entity tag is required to bind the download to the "
            "object that was checked"
        )
    return value.strip().strip('"')


def _reported_content_length(value: Any) -> int:
    """Return the byte count ``value`` carries.

    Raises ``AccessError`` when the store reported no usable byte count, since
    the bytes that arrive are confirmed against it.
    """
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AccessError(
            f"the endpoint reported {_display(value)} as the byte count of the "
            "landed object; a whole number is required to bind the download to the "
            "object that was checked"
        )
    return value


def _recorded_metadata(response: Mapping[str, Any]) -> dict[str, str]:
    """Return the user metadata ``response`` carries, keyed lower-case.

    A store reports metadata names in the case it chooses, and the names this tool
    compares are written lower-case, so the mapping is keyed lower-case and every
    value that is not text is dropped: an absent name and a name carrying a
    non-text value are then the same absence, which
    ``confirm_recorded_identity`` refuses.
    """
    carried = response.get("Metadata")
    if not isinstance(carried, Mapping):
        return {}
    return {
        str(name).lower(): value
        for name, value in carried.items()
        if isinstance(value, str)
    }


def _recorded_sha256(metadata: Mapping[str, str]) -> str | None:
    """Return the land-time digest ``metadata`` records, or None when it carries none.

    A value of any other shape than 64 lower-case hexadecimal characters is
    reported as absent rather than compared, so a digest this returns is one that
    can equal the digest of the bytes that arrived.
    """
    carried = metadata.get(RECORDED_SHA256_METADATA, "").strip().lower()
    if not _RECORDED_SHA256_SHAPE.fullmatch(carried):
        return None
    return carried


def _recorded_content_length(metadata: Mapping[str, str]) -> int | None:
    """Return the land-time byte count ``metadata`` records, or None for none.

    A value of any other shape than 1 to 12 decimal digits is reported as absent
    rather than compared, so a count this returns is one that can equal the byte
    count of the bytes that arrived.
    """
    carried = metadata.get(RECORDED_LENGTH_METADATA, "").strip()
    if not _RECORDED_LENGTH_SHAPE.fullmatch(carried):
        return None
    return int(carried, 10)


def head_object_identity(client: Any, bucket: str, key: str) -> ObjectIdentity:
    """Return the immutable identity of the object ``key`` in ``bucket``.

    One head request records the entity tag, the version the store assigned
    where the bucket keeps versions, the byte count, and the land-time digest and
    byte count modernization/landing/land_to_s3.py wrote as user metadata of the
    object. Nothing is written to the bucket, no body is transferred and nothing
    else in it is read. The download that follows requires this same identity, so
    the bytes that are parsed are the bytes this request described, and
    ``confirm_recorded_identity`` holds those bytes to the recorded digest.

    Raises ``AccessError`` when the object or the bucket did not answer or
    reported no usable identity, and ``ConfigurationError`` when a credential or
    region setting is missing.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    try:
        response = client.head_object(Bucket=bucket, Key=key)
    except (ClientError, BotoCoreError) as error:
        raise _failure_for(
            error, bucket, f"read the identity of the landed object {shown_key}"
        ) from error
    if not isinstance(response, Mapping):
        raise AccessError(
            f"the endpoint returned {_display(response)} for the identity of the "
            f"landed object {shown_key}; a response object is required"
        )
    version = response.get("VersionId")
    metadata = _recorded_metadata(response)
    return ObjectIdentity(
        etag=_reported_etag(response.get("ETag")),
        version_id=version if isinstance(version, str) and version else NOT_VERSIONED,
        content_length=_reported_content_length(response.get("ContentLength")),
        recorded_sha256=_recorded_sha256(metadata),
        recorded_content_length=_recorded_content_length(metadata),
    )


def fetch_object_bytes(
    client: Any, bucket: str, key: str, identity: ObjectIdentity
) -> DownloadedObject:
    """Return the body of the object ``key`` in ``bucket``, bound to ``identity``.

    The download requires the entity tag ``identity`` recorded, and the version
    it recorded when the bucket keeps versions, so an object replaced between
    the head request and this one fails rather than being read. The bytes that
    arrive are confirmed against the recorded byte count and their digest is
    computed and returned; the entity tag of a single-part upload is the MD5 of
    the body, so where the store reported one it is recomputed and compared as
    well. One byte past ``MAX_OBJECT_BYTES`` is requested, so an oversized
    object is reported without being held in memory in full. The bytes are
    returned unchanged; nothing re-encodes or reformats them. Nothing is written
    to the bucket and nothing else in it is read.

    Raises ``AccessError`` when the object or the bucket did not answer or was
    replaced between the two requests, ``ConfigurationError`` when a credential
    or region setting is missing, and ``ObjectError`` when the object is empty,
    larger than ``MAX_OBJECT_BYTES``, or does not carry the recorded byte count
    or digest.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    arguments: dict[str, Any] = {
        "Bucket": bucket,
        "Key": key,
        "IfMatch": identity.etag,
    }
    if identity.version_id != NOT_VERSIONED:
        arguments["VersionId"] = identity.version_id
    try:
        response = client.get_object(**arguments)
    except ClientError as error:
        if _client_error_code(error) in _CODES_PRECONDITION_FAILED:
            raise AccessError(
                f"the landed object {shown_key} in bucket {_shown(bucket)} was "
                "replaced between the identity check and the download; the load is "
                "abandoned rather than reading an object that was not checked"
            ) from error
        raise _failure_for(
            error, bucket, f"read the landed object {shown_key}"
        ) from error
    except BotoCoreError as error:
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
            f"the endpoint returned {_json_shape(content)} as the body of the landed "
            f"object {shown_key}; bytes are required"
        )
    if not content:
        raise ObjectError(f"the landed object {shown_key} is empty")
    if len(content) > MAX_OBJECT_BYTES:
        raise ObjectError(
            f"the landed object {shown_key} holds more than the accepted "
            f"{MAX_OBJECT_BYTES} bytes"
        )
    if len(content) != identity.content_length:
        raise ObjectError(
            f"the landed object {shown_key} arrived as {len(content)} bytes while its "
            f"identity records {identity.content_length}; the object changed between "
            "the identity check and the download"
        )
    _confirm_single_part_etag(content, identity, shown_key)
    return DownloadedObject(
        body=content,
        identity=identity,
        sha256=hashlib.sha256(content).hexdigest(),
    )


def _confirm_single_part_etag(
    content: bytes, identity: ObjectIdentity, shown_key: str
) -> None:
    """Confirm ``content`` carries the digest the recorded entity tag stands for.

    A single-part upload carries the hex MD5 of the body as its entity tag, so
    where the recorded tag is of that form it is recomputed from the bytes that
    arrived and compared. A multipart tag, which carries a part count after a
    hyphen, stands for a digest of digests rather than of the body, so the byte
    count and the version already checked are what bind such an object.

    Raises ``ObjectError`` when a single-part tag and the bytes disagree.
    """
    if not _SINGLE_PART_ETAG_SHAPE.fullmatch(identity.etag):
        return
    computed = hashlib.md5(content, usedforsecurity=False).hexdigest()
    if computed != identity.etag.casefold():
        raise ObjectError(
            f"the landed object {shown_key} arrived with the digest "
            f"{_shown(computed)} while its identity records the entity tag "
            f"{_shown(identity.etag)}; the bytes that arrived are not the bytes that "
            "were checked"
        )


def confirm_recorded_identity(downloaded: DownloadedObject, key: str) -> None:
    """Confirm the bytes that arrived are the bytes the landing step recorded.

    modernization/landing/land_to_s3.py writes the SHA-256 digest of the record it
    landed, and that record's byte count, as user metadata of the landed object
    itself. Both are required here and both are compared with the bytes that
    arrived: the digest with their SHA-256 and the byte count with their length.
    The entity tag and byte count the head request reported describe whatever the
    bucket holds now, so they cannot detect an object rewritten under this key
    after the landing; the recorded digest was computed before the upload and is
    what makes that rewrite visible. An object carrying no recorded digest, or one
    of an unusable shape, is refused rather than loaded on the strength of the
    store's own headers: this loader is the step that admits data into the
    warehouse, and an unverifiable object fails closed. Returns None when both
    values agree.

    Raises ``ObjectError`` naming the key, the recorded value and the observed one
    when a value is absent or disagrees, before the database is opened and before
    any statement runs.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    identity = downloaded.identity
    if identity.recorded_sha256 is None:
        raise ObjectError(
            f"the landed object {shown_key} carries no land-time digest under the "
            f"{_shown(RECORDED_SHA256_METADATA)} metadata name; the landing step "
            "records one on every object it writes, so an object without it cannot "
            "be confirmed to be the object that was landed and is not loaded"
        )
    if identity.recorded_sha256 != downloaded.sha256:
        raise ObjectError(
            f"the landed object {shown_key} arrived with the digest "
            f"{_shown(downloaded.sha256)} while the landing step recorded "
            f"{_shown(identity.recorded_sha256)}; the bytes on the bucket are not the "
            "bytes that were landed, so nothing is loaded"
        )
    recorded_length = identity.recorded_content_length
    if recorded_length is None:
        raise ObjectError(
            f"the landed object {shown_key} carries no land-time byte count under the "
            f"{_shown(RECORDED_LENGTH_METADATA)} metadata name; the landing step "
            "records one on every object it writes, so an object without it cannot "
            "be confirmed to be the object that was landed and is not loaded"
        )
    if recorded_length != len(downloaded.body):
        raise ObjectError(
            f"the landed object {shown_key} arrived as {len(downloaded.body)} bytes "
            f"while the landing step recorded {recorded_length}; the bytes on the "
            "bucket are not the bytes that were landed, so nothing is loaded"
        )


def fetch_manifest_bytes(client: Any, bucket: str, key: str) -> bytes:
    """Return the bytes of the COPY manifest ``key`` in ``bucket``.

    One read takes at most ``MAX_MANIFEST_BYTES`` plus one byte, so an object
    written at this key that is not a manifest is reported without being held in
    memory in full. Nothing is written to the bucket and nothing else in it is
    read.

    Raises ``AccessError`` when the manifest or the bucket did not answer,
    ``ConfigurationError`` when a credential or region setting is missing, and
    ``ObjectError`` when the manifest is empty or longer than
    ``MAX_MANIFEST_BYTES``.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    try:
        response = client.get_object(Bucket=bucket, Key=key)
    except (ClientError, BotoCoreError) as error:
        raise _failure_for(
            error, bucket, f"read the COPY manifest {shown_key}"
        ) from error
    body = response.get("Body") if isinstance(response, Mapping) else None
    if body is None:
        raise AccessError(
            f"the endpoint returned no body for the COPY manifest {shown_key} in "
            f"bucket {_shown(bucket)}"
        )
    try:
        content = body.read(MAX_MANIFEST_BYTES + 1)
    except (ClientError, BotoCoreError, OSError) as error:
        raise _failure_for(
            error, bucket, f"read the body of the COPY manifest {shown_key}"
        ) from error
    finally:
        closer = getattr(body, "close", None)
        if callable(closer):
            try:
                closer()
            except (ClientError, BotoCoreError, OSError) as error:
                _warn(
                    f"the body of the COPY manifest {shown_key} could not be closed: "
                    f"{_reason(error)}"
                )
    if not isinstance(content, bytes):
        raise AccessError(
            f"the endpoint returned {_json_shape(content)} as the body of the COPY "
            f"manifest {shown_key}; bytes are required"
        )
    if not content:
        raise ObjectError(f"the COPY manifest {shown_key} is empty")
    if len(content) > MAX_MANIFEST_BYTES:
        raise ObjectError(
            f"the COPY manifest {shown_key} holds more than the accepted "
            f"{MAX_MANIFEST_BYTES} bytes"
        )
    return content


def confirm_manifest_binding(
    manifest: bytes, manifest_key: str, object_uri: str, content_length: int
) -> None:
    """Confirm the COPY manifest binds this load to the object that was downloaded.

    The manifest is the second object modernization/landing/land_to_s3.py writes
    for a landing and the document modernization/landing/load_redshift.sql binds
    its real-target COPY to. It is required to be one JSON object carrying exactly
    one entry whose ``url`` is ``object_uri`` and whose nested ``meta``
    ``content_length`` is ``content_length``, which is the byte count of the bytes
    that actually arrived. A manifest naming another object, naming a byte count
    the object does not carry, carrying a second entry or carrying no usable entry
    is refused: the manifest was written after the object, so a landed object whose
    manifest does not name it is not the object the landing bound the load to.
    Returns None when the entry names this object and its length.

    ``mandatory`` is required to be true, which is what makes a COPY of this
    manifest fail on a removed object rather than load nothing; this tool reads the
    object directly and does not depend on that flag, so it is confirmed rather
    than acted on.

    Raises ``ObjectError`` naming the manifest key and what disagreed when the
    document is not that manifest, before the database is opened.
    """
    shown_key = _shown(manifest_key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    try:
        text = manifest.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ObjectError(
            f"the COPY manifest {shown_key} is not valid UTF-8: {_reason(error)}"
        ) from error
    try:
        document = parse_json_document(text)
    except DuplicateMemberError as error:
        raise ObjectError(
            f"the COPY manifest {shown_key} carries the member "
            f"{_shown(error.name)} more than once; one value per member is required"
        ) from error
    except UnparsableDocumentError as error:
        raise ObjectError(
            f"the COPY manifest {shown_key} is not a document this tool parses: "
            f"{error.reason}"
        ) from error
    except json.JSONDecodeError as error:
        raise ObjectError(
            f"the COPY manifest {shown_key} is not well-formed JSON at line "
            f"{error.lineno} column {error.colno}: "
            f"{_escaped(error.msg, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}"
        ) from error
    if not isinstance(document, Mapping):
        raise ObjectError(
            f"the COPY manifest {shown_key} carries {_json_shape(document)} at its "
            "top level; one JSON object naming its entries is required"
        )
    entries = document.get(MANIFEST_ENTRIES_MEMBER)
    if not isinstance(entries, list):
        raise ObjectError(
            f"the COPY manifest {shown_key} carries {_json_shape(entries)} as "
            f"{_shown(MANIFEST_ENTRIES_MEMBER)}; an array of entries is required"
        )
    if len(entries) != MANIFEST_ENTRY_COUNT:
        raise ObjectError(
            f"the COPY manifest {shown_key} names {len(entries)} entries; the landing "
            f"step writes {MANIFEST_ENTRY_COUNT} naming the object of this part alone"
        )
    entry = entries[0]
    if not isinstance(entry, Mapping):
        raise ObjectError(
            f"the COPY manifest {shown_key} carries {_json_shape(entry)} as its "
            "entry; one JSON object naming the landed object is required"
        )
    named = entry.get(MANIFEST_URL_MEMBER)
    if named != object_uri:
        shown_named = (
            _shown(named, MAX_DIAGNOSTIC_PATH_CHARACTERS)
            if isinstance(named, str)
            else _value_display(named)
        )
        raise ObjectError(
            f"the COPY manifest {shown_key} names {shown_named} as the object of this "
            f"load while the object downloaded is "
            f"{_shown(object_uri, MAX_DIAGNOSTIC_PATH_CHARACTERS)}; the manifest and "
            "the object must be the pair one landing wrote"
        )
    if entry.get(MANIFEST_MANDATORY_MEMBER) is not True:
        raise ObjectError(
            f"the COPY manifest {shown_key} carries "
            f"{_value_display(entry.get(MANIFEST_MANDATORY_MEMBER))} as "
            f"{_shown(MANIFEST_MANDATORY_MEMBER)}; the landing step writes true, so a "
            "COPY of this manifest fails on a removed object rather than loading "
            "nothing"
        )
    meta = entry.get(MANIFEST_META_MEMBER)
    if not isinstance(meta, Mapping):
        raise ObjectError(
            f"the COPY manifest {shown_key} carries {_json_shape(meta)} as "
            f"{_shown(MANIFEST_META_MEMBER)}; one JSON object carrying "
            f"{_shown(MANIFEST_CONTENT_LENGTH_MEMBER)} is required"
        )
    named_length = meta.get(MANIFEST_CONTENT_LENGTH_MEMBER)
    if isinstance(named_length, bool) or not isinstance(named_length, int):
        raise ObjectError(
            f"the COPY manifest {shown_key} carries {_value_display(named_length)} as "
            f"{_shown(MANIFEST_CONTENT_LENGTH_MEMBER)}; the byte count of the landed "
            "object is required"
        )
    if named_length != content_length:
        raise ObjectError(
            f"the COPY manifest {shown_key} names {named_length} bytes while the "
            f"object downloaded holds {content_length}; the manifest and the object "
            "must be the pair one landing wrote"
        )


# ---------------------------------------------------------------------------
# Landed record
# ---------------------------------------------------------------------------


def _rendered_byte(value: int) -> str:
    """Return one printable 7-bit ASCII rendering of the byte ``value``."""
    if 0x20 <= value <= 0x7E:
        return chr(value)
    return f"\\x{value:02x}"


def _byte_difference(actual: bytes, expected: bytes) -> str:
    """Return one bounded description of the first difference between two byte strings.

    The description names the byte counts when they differ, the offset of the
    first differing byte, and that byte and its canonical counterpart, each
    rendered as one printable 7-bit ASCII fragment. No object content beyond the
    differing byte is reported. An empty string is returned when the two are
    equal.
    """
    if actual == expected:
        return ""
    shared = min(len(actual), len(expected))
    offset = next(
        (index for index in range(shared) if actual[index] != expected[index]), shared
    )
    parts: list[str] = []
    if len(actual) != len(expected):
        parts.append(
            f"it holds {len(actual)} bytes where the canonical form holds "
            f"{len(expected)}"
        )
    if offset < shared:
        parts.append(
            f"at offset {offset} it holds {_shown(_rendered_byte(actual[offset]))} "
            f"where the canonical form holds "
            f"{_shown(_rendered_byte(expected[offset]))}"
        )
    elif offset < len(actual):
        parts.append(
            f"the canonical form ends at offset {offset}, where it holds "
            f"{_shown(_rendered_byte(actual[offset]))}"
        )
    else:
        parts.append(
            f"it ends at offset {offset}, where the canonical form holds "
            f"{_shown(_rendered_byte(expected[offset]))}"
        )
    return "; ".join(parts)


def confirm_key_order(
    record: Mapping[str, Any], columns: Sequence[str], key: str
) -> None:
    """Confirm ``record`` carries its keys in ``columns`` order, and return None.

    ``columns`` is the landed key order read from the landing schema, which
    ``read_column_names`` has already confirmed to equal that schema's
    ``required`` list. ``key`` names the object in any diagnostic. The count is
    compared first, then the position of every key.

    Raises ``ObjectError`` naming the first position that differs, or the counts
    when they differ.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    carried = tuple(record)
    if len(carried) != len(columns):
        raise ObjectError(
            f"the landed object {shown_key} carries {len(carried)} keys where the "
            f"landing contract fixes {len(columns)}"
        )
    for position, (found, wanted) in enumerate(zip(carried, columns, strict=True)):
        if found != wanted:
            raise ObjectError(
                f"the landed object {shown_key} carries its keys out of the order "
                f"the landing contract fixes: at position {position} it carries "
                f"{_shown(found)} where {_shown(wanted)} is required"
            )


def canonical_record_bytes(record: Mapping[str, Any]) -> bytes:
    """Return the canonical landed bytes of ``record``.

    The canonical form is the ASCII-escaped JSON serialisation of ``record``,
    with the keys in the order ``record`` carries them and the separators
    ``json.dumps`` applies, followed by one line feed. This is the form
    modernization/extraction/extract_commarea.py writes and
    modernization/landing/land_to_s3.py uploads.
    """
    return (json.dumps(dict(record), ensure_ascii=True) + "\n").encode("ascii")


def confirm_canonical_bytes(
    raw: bytes, record: Mapping[str, Any], key: str
) -> None:
    """Confirm ``raw`` is the canonical landed form of ``record``, and return None.

    ``raw`` is the body downloaded from the landed object and ``record`` is the
    object parsed from it. One comparison against ``canonical_record_bytes``
    covers the whole byte contract: one line, no pretty-printing, no surrounding
    or repeated whitespace, no carriage return, exactly one terminal line feed,
    the separators the extractor emits and the landed key order. ``key`` names
    the object in any diagnostic.

    Raises ``ObjectError`` describing the first difference when ``raw`` is not
    that form.
    """
    expected = canonical_record_bytes(record)
    if raw == expected:
        return
    raise ObjectError(
        f"the landed object {_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)} is not the "
        f"canonical one-line form the landing contract fixes: "
        f"{_byte_difference(raw, expected)}"
    )


def parse_record(raw: bytes, key: str) -> Mapping[str, Any]:
    """Return the single JSON object ``raw`` carries, decoded as UTF-8.

    ``raw`` is the body of the landed object, one JSON object on a single line
    terminated by one line feed. ``key`` names the object in any diagnostic. The
    members of every object are kept in document order, and a member name that
    repeats at any nesting level is refused and named, so the 17 keys the landing
    contract fixes cannot be smuggled past validation by a later duplicate and no
    document is resolved to its last occurrence.

    Raises ``ObjectError`` when ``raw`` is not valid UTF-8, is not one
    well-formed JSON document, nests deeper than ``MAX_JSON_NESTING_DEPTH``,
    carries a value the parser refuses, carries a repeated member name, carries a
    second document, or carries a JSON value that is not an object.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ObjectError(
            f"the landed object {shown_key} is not valid UTF-8: {_reason(error)}"
        ) from error
    try:
        document = parse_json_document(text)
    except DuplicateMemberError as error:
        raise ObjectError(
            f"the landed object {shown_key} carries the member "
            f"{_shown(error.name)} more than once; one value per member is required"
        ) from error
    except UnparsableDocumentError as error:
        raise ObjectError(
            f"the landed object {shown_key} is not a document this tool parses: "
            f"{error.reason}; the landed object is one flat JSON object of the "
            f"{EXPECTED_COLUMN_COUNT} keys the landing contract fixes"
        ) from error
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
            f"the landed object {shown_key} carries {_json_shape(document)} at its "
            "top level; one JSON object is required"
        )
    return document


def validate_record(
    record: Mapping[str, Any],
    validator: Draft202012Validator,
    key: str,
    limit: int = MAX_REPORTED_SCHEMA_ERRORS,
) -> None:
    """Confirm ``record`` satisfies the landing schema, reporting every violation.

    Every constraint of the schema document applies here, not only the key set and
    the string-or-null rule: the enumerated request ids, policy types and landable
    return codes, the required non-null values, the digit patterns and lengths of the
    identifiers and amounts, and the asserted date format. The object is external
    input, so it is validated in full before the database is opened. Violations are
    reported in JSON Pointer order, at most ``limit`` of them, with the number
    withheld recorded when there are more. ``key`` names the object in the
    diagnostic. Returns None when the record satisfies the schema.

    Several violations can describe one breach: ``required`` rejects an object once
    per property it omits, and each branch of the schema's ``allOf`` holds the same
    value to its own constraint. Every violation is therefore rendered before the
    count is taken, a rendering that repeats is reported once, and both ``limit``
    and the withheld count are taken over the renderings that remain. Two
    violations that render differently are both reported.

    Raises ``ObjectError`` carrying the violations when it does not.
    """
    errors = sorted(
        validator.iter_errors(record),
        key=lambda error: (_json_pointer(error.absolute_path), error.message),
    )
    violations: list[str] = []
    seen: set[str] = set()
    for error in errors:
        rendered = _violation(error)
        if rendered in seen:
            continue
        seen.add(rendered)
        violations.append(rendered)
    if not violations:
        return
    reported = "; ".join(violations[:limit])
    withheld = len(violations) - min(len(violations), limit)
    if withheld:
        reported = f"{reported}; (+{withheld} further violations)"
    raise ObjectError(
        f"the landed object {_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)} does not "
        f"satisfy the landing schema: {reported}"
    )


def confirm_calendar_values(record: Mapping[str, Any], key: str) -> None:
    """Confirm every date and the timestamp of ``record`` name a real day and moment.

    Each key of ``DATE_FIELDS`` that carries a value is parsed with
    ``datetime.date.fromisoformat`` and must round-trip to the same text, so a value
    written in another ISO 8601 form is refused along with one that names no day. The
    ``TIMESTAMP_FIELD`` value is parsed with ``TIMESTAMP_PATTERN`` and must round-trip
    the same way, which asserts the calendar and clock values the schema's pattern can
    only shape. A null date is accepted, since the landing contract carries a blank
    window as null. Returns None when every value names a real day and moment.

    Raises ``ObjectError`` naming the key and the value when one does not, before the
    database is opened and before any statement runs.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    for name in DATE_FIELDS:
        value = record.get(name)
        if value is None:
            continue
        if not isinstance(value, str):
            raise ObjectError(
                f"the landed object {shown_key} carries {_display(value)} as "
                f"{_shown(name)}; a date written {DATE_FORM} or null is required"
            )
        try:
            parsed_date = datetime.date.fromisoformat(value)
        except ValueError as error:
            raise ObjectError(
                f"the landed object {shown_key} carries {_shown(value)} as "
                f"{_shown(name)}; it is not a calendar date written {DATE_FORM}: "
                f"{_reason(error)}"
            ) from error
        if parsed_date.isoformat() != value:
            raise ObjectError(
                f"the landed object {shown_key} carries {_shown(value)} as "
                f"{_shown(name)}; it is not written {DATE_FORM}, whose form for that "
                f"date is {_shown(parsed_date.isoformat())}"
            )
    carried = record.get(TIMESTAMP_FIELD)
    if not isinstance(carried, str):
        raise ObjectError(
            f"the landed object {shown_key} carries {_display(carried)} as "
            f"{_shown(TIMESTAMP_FIELD)}; a timestamp written {TIMESTAMP_FORM} is "
            "required"
        )
    try:
        moment = datetime.datetime.strptime(carried, TIMESTAMP_PATTERN)
    except ValueError as error:
        raise ObjectError(
            f"the landed object {shown_key} carries {_shown(carried)} as "
            f"{_shown(TIMESTAMP_FIELD)}; it is not a timestamp written "
            f"{TIMESTAMP_FORM}: {_reason(error)}"
        ) from error
    normalised = moment.isoformat(
        sep=TIMESTAMP_OUTPUT_SEPARATOR, timespec=TIMESTAMP_OUTPUT_PRECISION
    )
    if normalised != carried:
        raise ObjectError(
            f"the landed object {shown_key} carries {_shown(carried)} as "
            f"{_shown(TIMESTAMP_FIELD)}; it is not written {TIMESTAMP_FORM}, whose "
            f"form for that moment is {_shown(normalised)}"
        )


def confirm_record_contract(
    record: Mapping[str, Any], columns: Sequence[str], key: str
) -> None:
    """Confirm ``record`` carries exactly ``columns``, each as text or as null.

    The key set must equal ``columns`` exactly: a missing key and an extra key
    are both refused and named. Every value must be a JSON string or JSON null,
    which is what a number, a boolean, an object and an array are refused for.
    This is the row shape the INSERT depends on, confirmed against the column
    names read from the schema's own properties block; the values themselves are
    held to the schema by ``validate_record``. Returns None once the record
    matches.

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
                f"the landed object {shown_key} carries {_value_display(value)} as "
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
) -> tuple[str | None, ...]:
    """Return the natural-key values of ``record``, in ``NATURAL_KEY_FIELDS`` order.

    A value is returned exactly as the object carries it, as text or as None. Which
    values the record must carry is decided by the landing schema, which admits only
    a successful execution and requires every chain-assigned value on it, including
    the ``policy_number`` recovered after the policy insert at
    base/src/lgapdb01.cbl:308-311; this function does not restate that rule. The
    predicate that removes an earlier row matches null to null, so a row is replaced
    on a repeated run rather than duplicated whatever the values are.

    Raises ``ObjectError`` when a natural-key field is absent from the record, or
    carries a value that is neither text nor null, or carries the empty string,
    which is a value the landing contract never lands.
    """
    shown_key = _shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)
    values: list[str | None] = []
    for field in NATURAL_KEY_FIELDS:
        if field not in record:
            raise ObjectError(
                f"the landed object {shown_key} omits {_shown(field)}; it is part of "
                f"the natural key ({', '.join(NATURAL_KEY_FIELDS)}) of the loaded row"
            )
        value = record[field]
        if value is not None and not isinstance(value, str):
            raise ObjectError(
                f"the landed object {shown_key} carries {_json_shape(value)} as "
                f"{_shown(field)}; it is part of the natural key "
                f"({', '.join(NATURAL_KEY_FIELDS)}) of the loaded row and carries "
                "text or null"
            )
        if value == "":
            raise ObjectError(
                f"the landed object {shown_key} carries the empty string as "
                f"{_shown(field)}; it is part of the natural key "
                f"({', '.join(NATURAL_KEY_FIELDS)}) of the loaded row, and a value "
                "the chain never assigned is landed as null rather than as an empty "
                "string"
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
            f"{_value_display(carried)} as {_shown(field)} while the resolved "
            f"source-system key is {_shown(expected)}; the two must agree"
        )


def confirm_object_key(
    record: Mapping[str, Any],
    key: str,
    extract_date: datetime.date,
    part: int = DEFAULT_PART_NUMBER,
) -> None:
    """Confirm ``key`` is the key ``record``'s own source-system key rebuilds.

    The key is rebuilt from the value the validated object carries, the fixed
    ``LANDING_ENTITY`` literal, ``extract_date`` and ``part``, and must equal the key
    that was downloaded, so the row written comes from the exact object the landing
    contract names rather than from any other object that answered, including any
    other part of the same prefix. Returns None when the two agree.

    Raises ``ObjectError`` when they do not, and ``ConfigurationError`` when the
    object's own source-system key cannot form a path segment.
    """
    field = NATURAL_KEY_FIELDS[0]
    carried = record.get(field)
    if not isinstance(carried, str):
        raise ObjectError(
            f"the landed object {_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)} carries "
            f"{_display(carried)} as {_shown(field)}; the landing key is rebuilt from "
            "it"
        )
    rebuilt = build_landing_key(carried, LANDING_ENTITY, extract_date, part)
    if rebuilt != key:
        raise ObjectError(
            f"the landed object {_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)} is not "
            "the object its own contents name: the key its "
            f"{_shown(field)} and the landing contract rebuild is "
            f"{_shown(rebuilt, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
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


def _after_leading_comments(statement: str) -> str:
    """Return ``statement`` from its first character of code, comments removed.

    A statement is returned by ``split_sql_statements`` exactly as the script
    writes it, so it can open with a ``--`` line comment, with one or more
    ``/* */`` block comments, including nested ones, and with whitespace between
    them. Those carry no code, and the caller reads the first word of code, so
    they are stepped over here rather than mistaken for that word. Scanning stops
    at the first character that is not whitespace and does not open a comment; a
    statement that is only comments and whitespace yields the empty string, and so
    does one whose block comment is unterminated, which ``split_sql_statements``
    has already refused for any statement it returns.
    """
    index = 0
    length = len(statement)
    while index < length:
        if statement[index].isspace():
            index += 1
            continue
        pair = statement[index : index + 2]
        if pair == "--":
            end = statement.find("\n", index)
            if end < 0:
                return ""
            index = end + 1
            continue
        if pair == "/*":
            depth = 0
            while index < length:
                inner = statement[index : index + 2]
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
                index += 1
            if depth != 0:
                return ""
            continue
        return statement[index:]
    return ""


def _leading_keyword(statement: str) -> str:
    """Return the first word of code in ``statement``, lower-cased, or the empty string.

    Leading comments and whitespace are stepped over first, so a statement whose
    transaction control follows a comment yields that control rather than the
    comment's first word. An opening parenthesis is treated as a separator, so a
    statement written with no space after its first word still yields that word.
    """
    tokens = _after_leading_comments(statement).replace("(", " ").split()
    return tokens[0].lower() if tokens else ""


def confirm_no_transaction_control(
    statements: Sequence[str], path: Path
) -> None:
    """Confirm no statement of a supplied script opens, ends or abandons a transaction.

    The load runs as one transaction, and a statement carrying its own transaction
    control inside it would commit part of the load, discard part of it, or fail on
    a nesting the database does not accept. The scripts of this bridge carry none;
    a supplied script that does is refused before the transaction opens, so a
    rejected script never leaves the database half-loaded. Returns None when no
    statement carries one.

    Raises ``ConfigurationError`` naming the script, the statement's position in it
    and the keyword found.
    """
    for ordinal, statement in enumerate(statements, start=1):
        keyword = _leading_keyword(statement)
        if keyword in TRANSACTION_CONTROL_KEYWORDS:
            raise ConfigurationError(
                f"statement {ordinal} of {len(statements)} in {_path_shown(path)} "
                f"begins with {_shown(keyword)}, which opens, ends or abandons a "
                "transaction: the whole load runs as one transaction, so a script "
                "applied inside it carries none of "
                f"{_quote_all(TRANSACTION_CONTROL_KEYWORDS)}"
            )


def read_sql_statements(path: Path) -> tuple[str, ...]:
    """Return the statements of the SQL script at ``path``, in file order.

    Raises ``ConfigurationError`` when the script is missing, empty, larger than
    ``MAX_DDL_BYTES``, not valid UTF-8, leaves a quoted literal or comment
    unterminated, or carries its own transaction control.
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
    confirm_no_transaction_control(statements, path)
    return statements


def apply_sql_script(
    connection: duckdb.DuckDBPyConnection, path: Path
) -> int:
    """Apply every statement of the script at ``path`` in order, and return the count.

    Each statement is executed exactly as the script writes it; none is
    rewritten, reordered, substituted or skipped. The scripts this tool is given
    are written to be re-runnable, so applying them to a database that already
    holds their objects changes nothing. The caller has already opened the
    transaction the statements run inside, and a script carrying its own
    transaction control has already been refused by ``read_sql_statements``.

    Raises ``ConfigurationError`` when the script cannot be read or split,
    ``KeyboardInterrupt`` when the statement was interrupted rather than refused,
    and ``WarehouseError`` naming the script, the statement's position in it and
    the statement as written when the database refuses a statement.
    """
    statements = read_sql_statements(path)
    for ordinal, statement in enumerate(statements, start=1):
        try:
            connection.execute(statement)
        except RuntimeError as error:
            if not _interrupted(error):
                raise
            raise KeyboardInterrupt from error
        except duckdb.Error as error:
            if _interrupted(error):
                raise KeyboardInterrupt from error
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


def _open_allowed_root() -> int:
    """Return a descriptor on ``ALLOWED_DATABASE_ROOT``, creating it when absent.

    The directory is opened without following a symbolic link, and the descriptor
    the kernel reports is confirmed to be the resolved allowed root, so every
    later check and creation happens inside the one directory a database may sit
    in. The caller closes the descriptor.

    Raises ``WarehouseError`` when the directory cannot be created, cannot be
    opened as a directory, or is not the allowed root.
    """
    try:
        ALLOWED_DATABASE_ROOT.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise WarehouseError(
            f"the database directory cannot be created: "
            f"{_path_shown(ALLOWED_DATABASE_ROOT)}: {_reason(error)}"
        ) from error
    try:
        descriptor = os.open(
            ALLOWED_DATABASE_ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        )
    except OSError as error:
        raise WarehouseError(
            f"the database directory cannot be opened: "
            f"{_path_shown(ALLOWED_DATABASE_ROOT)}: {_reason(error)}"
        ) from error
    expected = os.path.realpath(ALLOWED_DATABASE_ROOT)
    try:
        reported = os.readlink(f"/proc/self/fd/{descriptor}")
    except OSError:
        reported = None
    try:
        if reported is not None and reported != expected:
            raise WarehouseError(
                f"the opened database directory is {_path_shown(reported)} rather "
                f"than {_path_shown(expected)}; only a file directly inside "
                f"{_path_shown(ALLOWED_DATABASE_ROOT)} is written"
            )
        held = os.stat(descriptor)
        root = os.stat(expected)
        if (held.st_dev, held.st_ino) != (root.st_dev, root.st_ino):
            raise WarehouseError(
                f"the opened database directory is not {_path_shown(expected)}; only "
                f"a file directly inside {_path_shown(ALLOWED_DATABASE_ROOT)} is "
                "written"
            )
    except OSError as error:
        os.close(descriptor)
        raise WarehouseError(
            f"the database directory cannot be examined: {_path_shown(expected)}: "
            f"{_reason(error)}"
        ) from error
    except WarehouseError:
        os.close(descriptor)
        raise
    return descriptor


def _database_entry(name: str, descriptor: int) -> os.stat_result | None:
    """Return the entry ``name`` inside the held directory, or None when absent.

    The entry is examined relative to ``descriptor`` and without following a
    symbolic link, so what is examined is the entry inside the directory the
    caller holds.

    Raises ``WarehouseError`` when the entry cannot be examined, is a symbolic
    link, or is not a regular file.
    """
    try:
        info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise WarehouseError(
            f"the database file cannot be examined: "
            f"{_path_shown(ALLOWED_DATABASE_ROOT / name)}: {_reason(error)}"
        ) from error
    if stat.S_ISLNK(info.st_mode):
        raise WarehouseError(
            f"the database path is a symbolic link: "
            f"{_path_shown(ALLOWED_DATABASE_ROOT / name)}; a regular file directly "
            f"inside {_path_shown(ALLOWED_DATABASE_ROOT)} is required"
        )
    if not stat.S_ISREG(info.st_mode):
        raise WarehouseError(
            f"the database path exists and is not a regular file: "
            f"{_path_shown(ALLOWED_DATABASE_ROOT / name)}"
        )
    return info


def open_database(path: Path) -> duckdb.DuckDBPyConnection:
    """Return a read-write connection to the DuckDB database file at ``path``.

    ``path`` is the absolute path ``resolve_database_path`` returned, whose parent
    is ``ALLOWED_DATABASE_ROOT``. That directory is created when absent and is
    then held open as a descriptor, opened without following a symbolic link and
    confirmed to be the allowed root, and the database name is examined relative
    to that descriptor before the connection is made: an existing entry must be a
    regular file that is not a symbolic link. The connection then creates the file
    when it is absent, DuckDB writing its own header and refusing an empty file,
    and the entry is examined once more afterwards: it must be a regular file
    that is not a symbolic link, and where it existed before, its device and inode
    numbers must be the ones that were checked. DuckDB opens the file by name, so
    an entry replaced in the window between the check and that open is detected by
    the second examination rather than prevented: such a run is refused, the
    connection is closed and nothing is written through it.

    The parent is held to ``is_database_root``, the same predicate
    ``resolve_database_path`` applies to the ``--database`` value: a path that
    resolver returned satisfies it, and a path reaching this function by any other
    route is refused here. Because that resolver has already refused every
    ``--database`` value whose parent is not the allowed root, the check repeated
    here guards the window between that resolution and this open rather than a
    rejected setting.

    Raises ``KeyboardInterrupt`` when the open was interrupted rather than refused,
    and ``WarehouseError`` when the parent is not the allowed root, when the name is
    refused, or when the database cannot be opened or confirmed.
    """
    name = path.name
    parent = os.path.realpath(path.parent)
    if not is_database_root(path.parent):
        raise WarehouseError(
            f"the database path resolves to a file in {_path_shown(parent)}: "
            f"{_path_shown(path)}; only a file directly inside "
            f"{_path_shown(ALLOWED_DATABASE_ROOT)} is opened"
        )
    descriptor = _open_allowed_root()
    try:
        before = _database_entry(name, descriptor)
        try:
            connection = duckdb.connect(str(path))
        except RuntimeError as error:
            if not _interrupted(error):
                raise
            raise KeyboardInterrupt from error
        except (duckdb.Error, OSError) as error:
            if _interrupted(error):
                raise KeyboardInterrupt from error
            raise WarehouseError(
                f"the database cannot be opened: {_path_shown(path)}: {_reason(error)}"
            ) from error
        try:
            after = _database_entry(name, descriptor)
            if after is None:
                raise WarehouseError(
                    f"the database file is not present after it was opened: "
                    f"{_path_shown(path)}"
                )
            if before is not None and (after.st_dev, after.st_ino) != (
                before.st_dev,
                before.st_ino,
            ):
                raise WarehouseError(
                    f"the database file was replaced while it was being opened: "
                    f"{_path_shown(path)}"
                )
        except WarehouseError:
            try:
                connection.close()
            except (duckdb.Error, RuntimeError) as close_error:
                _warn(
                    "the database connection could not be closed after the database "
                    f"file was refused: {_reason(close_error)}"
                )
            raise
    finally:
        os.close(descriptor)
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


def build_delete_statement(
    relation: str, key_values: Sequence[str | None]
) -> str:
    """Return the statement removing the rows carrying one natural key.

    The predicate names every field of ``NATURAL_KEY_FIELDS`` and binds each
    value as a parameter, so a row carrying any other natural key is out of its
    reach and no whole-relation form is ever issued. Every field is compared with
    ``IS NOT DISTINCT FROM``, which matches null to null and agrees with ``=``
    against a value: the predicate is written once for the whole
    ``NATURAL_KEY_FIELDS`` tuple, whose members are nullable columns of
    ``raw.genapp_policy_issue``, so it is null-safe by construction.

    Decision rationale: modernization/docs/decision-log.md, row D-38.
    """
    predicate = " AND ".join(
        f"{field} IS NOT DISTINCT FROM ?" for field in NATURAL_KEY_FIELDS
    )
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
    key_values: Sequence[str | None],
    ddl_paths: Sequence[Path] = (),
) -> tuple[int, int]:
    """Apply the bootstrap and write one landed record, in one transaction.

    One transaction covers the whole load: the scripts in ``ddl_paths`` are applied
    inside it, the rows already carrying ``key_values`` as their natural key are
    removed, and ``values`` is written as one row. A repeated run therefore leaves
    one row rather than two, and a row carrying any other natural key is untouched.
    Every value is bound rather than joined into statement text, and a None binds
    as SQL NULL rather than as an empty string or a zero, matching an earlier null
    of the same field. The transaction is committed once every statement has
    succeeded; a failure in any of them rolls it back and leaves the database as it
    was found.

    Starting the transaction is part of the protected work: a database that refuses
    ``BEGIN TRANSACTION`` is reported as the actionable ``WarehouseError`` naming
    that step, never as an unhandled database traceback, and no rollback is attempted
    for a transaction that never started.

    The transaction is committed once every statement has succeeded. Any failure
    rolls it back, and the rollback withdraws every change the transaction made:
    the row written, the row removed, and any schema or relation a bootstrap script
    created inside it, because DuckDB holds catalogue changes and data changes in
    the same transaction. A database file the connection created because it was
    absent is not withdrawn by the rollback; it stays on disk holding no schema and
    no row.

    An interrupt that arrives while a statement is running is a run stopped by
    hand rather than a database that refused the load: DuckDB reports it as an
    interrupted query, ``_interrupted`` recognises it, the transaction is rolled
    back as for any other failure and ``KeyboardInterrupt`` leaves this function,
    so the caller reports the interrupt and nothing is written.

    Raises ``ConfigurationError`` when a bootstrap script cannot be read,
    ``KeyboardInterrupt`` when a statement was interrupted, ``WarehouseError`` when
    the transaction cannot be started, when a statement or the commit did not
    succeed, or when the write did not report exactly ``EXPECTED_INSERTED_ROWS``
    rows, and ``SchemaError`` when the relation name is not usable. Whatever the
    failure, a started transaction is rolled back before the diagnostic leaves this
    function.
    """
    if len(values) != len(columns):
        raise WarehouseError(
            f"the landed record carries {len(values)} values for {len(columns)} "
            "columns; the two must agree"
        )
    relation = qualified_relation_name()
    delete_statement = build_delete_statement(relation, key_values)
    delete_bindings = [value for value in key_values if value is not None]
    insert_statement = build_insert_statement(relation, columns)
    started = False
    try:
        connection.execute("BEGIN TRANSACTION")
        started = True
        apply_sql_scripts(connection, ddl_paths)
        removed = _affected_rows(
            connection.execute(delete_statement, delete_bindings).fetchall(),
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
        if started:
            try:
                connection.execute("ROLLBACK")
            except (duckdb.Error, RuntimeError) as rollback_error:
                _warn(
                    "the transaction could not be rolled back after the load failed: "
                    f"{_reason(rollback_error)}"
                )
        if isinstance(error, (LoadError, KeyboardInterrupt, SystemExit)):
            raise
        if _interrupted(error):
            raise KeyboardInterrupt from error
        if not started:
            raise WarehouseError(
                f"the database refused the start of the transaction writing one row "
                f"of {relation}: {_reason(error)}. The database was left as it was "
                "found and no statement of this load ran"
            ) from error
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
    ``NATURAL_KEY_FIELDS`` the object carried, in that order, each as text or None
    where the chain assigned nothing, ``removed`` is the rows carrying that natural
    key that the load removed, ``written`` is the rows it wrote, ``identity`` is the
    immutable identity the download was bound to, and ``sha256`` is the digest of
    the bytes that arrived.
    """

    uri: str
    key_values: tuple[str | None, ...]
    removed: int
    written: int
    identity: ObjectIdentity
    sha256: str


def load_record(
    bucket: str,
    key: str,
    source_system_key: str,
    extract_date: datetime.date,
    database_path: Path,
    ddl_paths: Sequence[Path],
    *,
    part: int = DEFAULT_PART_NUMBER,
    region: str | None = None,
    endpoint_url: str | None = None,
    schema_path: Path = DEFAULT_SCHEMA,
    show_identifiers: bool = False,
) -> LoadOutcome:
    """Load one landed object as one row, and return what the load did.

    The landed column names, their order and the constraints the object is held to
    are read from the landing schema at ``schema_path``, so the columns the row is
    written from and the contract the object is admitted by come from the same
    document. The object is bound to its own immutable identity before it is read:
    a head request records the entity tag, the version where the bucket keeps
    versions and the byte count, the download requires that same identity, and the
    bytes that arrive are confirmed against the byte count and entity tag that
    head request reported.

    The bytes are then confirmed to be the bytes that were landed, before anything
    is parsed: ``confirm_recorded_identity`` holds them to the SHA-256 digest and
    byte count modernization/landing/land_to_s3.py recorded as user metadata of the
    object at land time, and ``confirm_manifest_binding`` holds the COPY manifest of
    this same part - the second object that landing wrote, at
    ``sibling_manifest_key`` of the key being read - to naming exactly this object's
    URI and exactly the byte count that arrived. The entity tag and byte count a
    head request reports describe whatever the bucket holds now, so an object
    rewritten under this key after the landing passes them; the recorded digest was
    computed before the upload, so it does not. Either check failing ends the load
    with the object status, one line and nothing written.

    Only then is the record parsed and validated in full: unique member names,
    every constraint of that schema including its asserted date format, a real
    last_changed moment, exactly the declared keys as text or null and in the order
    the schema fixes, the canonical one-line bytes of the object it parses to, the
    run's source-system key, and a key equal to the one its own source-system key,
    ``extract_date`` and ``part`` rebuild. Every one of those checks runs before the
    database is opened, so a rejected object reaches neither the database file nor a
    statement. The two shared scripts in ``ddl_paths`` are then applied inside the
    same transaction that writes the row.

    With ``show_identifiers`` false, which is the default, the progress lines
    name no business identifier and no full object URI.

    Raises ``ObjectError`` when the landed object breaches the landing contract,
    carries no land-time digest or one that disagrees with the bytes that arrived,
    or is not the object its own COPY manifest names, ``SchemaError`` when the
    landing schema cannot be used, ``ConfigurationError`` when a setting or a script
    cannot be resolved, ``AccessError`` when the bucket, the object or the manifest
    did not answer or the object was replaced between the identity check and the
    download, and ``WarehouseError`` when the database or a statement did not
    succeed.
    """
    contract = landing_contract(schema_path)
    columns = contract.columns
    uri = build_object_uri(bucket, key)
    client = resolve_s3_access(bucket, region, endpoint_url)
    identity = head_object_identity(client, bucket, key)
    _note(
        f"bound the download to {identity.content_length} bytes, etag "
        f"{identity.etag} and version {identity.version_id} of "
        f"{_reported_uri(uri, show_identifiers)}"
    )
    downloaded = fetch_object_bytes(client, bucket, key, identity)
    confirm_recorded_identity(downloaded, key)
    manifest_key = sibling_manifest_key(key)
    confirm_manifest_binding(
        fetch_manifest_bytes(client, bucket, manifest_key),
        manifest_key,
        uri,
        len(downloaded.body),
    )
    _note(
        f"confirmed the land-time digest {downloaded.sha256} and the COPY manifest "
        f"{_shown(manifest_object_name(part))} naming {len(downloaded.body)} bytes of "
        f"{_reported_uri(uri, show_identifiers)}"
    )
    record = parse_record(downloaded.body, key)
    validate_record(record, contract.validator, key)
    confirm_calendar_values(record, key)
    confirm_record_contract(record, columns, key)
    confirm_key_order(record, columns, key)
    confirm_canonical_bytes(downloaded.body, record, key)
    confirm_source_system_key(record, source_system_key, key)
    confirm_object_key(record, key, extract_date, part)
    key_values = natural_key_values(record, key)
    values = record_values(record, columns)
    _note(
        f"read {len(downloaded.body)} bytes carrying {len(columns)} landed columns "
        f"with sha256 {downloaded.sha256} from "
        f"{_reported_uri(uri, show_identifiers)}"
    )
    connection = open_database(database_path)
    try:
        removed, written = upsert_record(
            connection, columns, values, key_values, ddl_paths
        )
    finally:
        try:
            connection.close()
        except (duckdb.Error, RuntimeError) as error:
            _warn(f"the database connection could not be closed: {_reason(error)}")
    return LoadOutcome(
        uri, key_values, removed, written, identity, downloaded.sha256
    )


# ---------------------------------------------------------------------------
# Self-test: fixtures
# ---------------------------------------------------------------------------


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


# Members of the motor landing record every case reads, in the landing order, and
# of the commercial record used wherever a second distinct natural key is needed.
# Both carry return code 00, the outcome the landing contract carries, and the
# product-specific null pattern: a motor row carries the motor premium and no
# commercial premium, and a commercial row carries the four commercial premiums
# and no motor premium.
_MOTOR_RECORD_MEMBERS: tuple[tuple[str, Any], ...] = (
    ("source_system_key", DEFAULT_SOURCE_SYSTEM_KEY),
    ("policy_number", "1000301"),
    ("policy_type", "M"),
    ("customer_number", "1001"),
    ("request_id", "01AMOT"),
    ("return_code", "00"),
    ("issue_date", "2026-08-19"),
    ("expiry_date", "2027-08-18"),
    ("last_changed", "2026-08-19T12:00:00.000000"),
    ("broker_id", "42"),
    ("brokers_reference", "BRMOT001"),
    ("payment_amount", "500"),
    ("motor_premium_amount", "450"),
    ("fire_premium_amount", None),
    ("crime_premium_amount", None),
    ("flood_premium_amount", None),
    ("weather_premium_amount", None),
)
_COMMERCIAL_RECORD_MEMBERS: tuple[tuple[str, Any], ...] = (
    ("source_system_key", DEFAULT_SOURCE_SYSTEM_KEY),
    ("policy_number", "1000302"),
    ("policy_type", "C"),
    ("customer_number", "1002"),
    ("request_id", "01ACOM"),
    ("return_code", "00"),
    ("issue_date", "2026-08-19"),
    ("expiry_date", "2027-08-18"),
    ("last_changed", "2026-08-19T12:00:01.000000"),
    ("broker_id", "43"),
    ("brokers_reference", "BRCOM001"),
    ("payment_amount", "1750"),
    ("motor_premium_amount", None),
    ("fire_premium_amount", "13500"),
    ("crime_premium_amount", "9400"),
    ("flood_premium_amount", "7200"),
    ("weather_premium_amount", "5100"),
)

# Settings every case that resolves a setting or reaches a collaborator uses.
_SELF_TEST_BUCKET = "genapp-rqi-landing-selftest"
_SELF_TEST_REGION = "eu-west-2"
_SELF_TEST_EXTRACT_DATE = datetime.date(2026, 8, 19)
_SELF_TEST_CREDENTIALS = {
    "AWS_ACCESS_KEY_ID": "selftest-access-key",
    "AWS_SECRET_ACCESS_KEY": "selftest-secret-key",
}

# Content type modernization/landing/land_to_s3.py writes both objects of a landing
# with. A seeded fixture repeats it so the bucket a case reads is the bucket a landing
# leaves; this tool reads the body and the recorded metadata and never the content type,
# so no check of this module depends on it.
_SELF_TEST_CONTENT_TYPE = "application/json"

# The two documents the parse-bound case is put to. The nesting is far past
# MAX_JSON_NESTING_DEPTH and past what the interpreter's own parser takes, so one
# document exercises this tool's bound and, with the bound raised to its own depth, the
# fallback that reports the interpreter's; the digit count is past the 4300 digits the
# interpreter converts to an int, which the parser refuses as a value rather than as
# syntax. Both stay well inside MAX_OBJECT_BYTES, so each is refused for what it is
# rather than for its size.
_SELF_TEST_DEEP_NESTING = 50000
_SELF_TEST_LONG_INTEGER_DIGITS = 5000

# Address moto's server binds for a command-line case. This tool runs on the local
# branch alone, so such a case has to name a loopback endpoint; the port is assigned
# by the operating system and nothing leaves this machine.
_LOOPBACK_ADDRESS = "127.0.0.1"

# Logger the WSGI server under moto's own server writes one request line to. It is
# disabled while a case's server runs, and restored afterwards, so a served request
# adds no line to the output of a self-test run.
_REQUEST_LOGGER_NAME = "werkzeug"

# Bucket name no case creates, which is how a run reaches a bucket that does not
# answer.
_ABSENT_BUCKET = "genapp-rqi-absent-bucket"

# Every environment variable a case controls. The names after the credentials keep
# a session from reading a profile, a credentials file or an instance metadata
# service, and the two endpoint names establish that a configured endpoint cannot
# redirect a request. SHOW_IDENTIFIERS_VARIABLE is among them so a case that sets
# it governs its own run alone: the variable is removed before every other case and
# restored on the way out, and no case inherits the disclosure another one selected.
_CONSULTED_VARIABLES = (
    BUCKET_VARIABLE,
    ENDPOINT_URL_VARIABLE,
    SOURCE_SYSTEM_KEY_VARIABLE,
    SHOW_IDENTIFIERS_VARIABLE,
    *REGION_VARIABLES,
    *DATABASE_VARIABLES,
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_PROFILE",
    "AWS_DEFAULT_PROFILE",
    "AWS_ENDPOINT_URL",
    "AWS_ENDPOINT_URL_S3",
    "AWS_CONFIG_FILE",
    "AWS_SHARED_CREDENTIALS_FILE",
    "AWS_EC2_METADATA_DISABLED",
)

# Endpoints the policy accepts, each a loopback literal or the loopback name with
# an explicit port and nothing else.
_ACCEPTED_ENDPOINTS = (
    "http://127.0.0.1:5112",
    "http://127.0.0.1:5112/",
    "http://127.9.8.7:1024",
    "http://localhost:5112",
    "https://localhost:8443",
    "http://[::1]:5112",
    "https://[::1]:5112/",
)

# Endpoints the policy refuses, each paired with the element the diagnostic names.
_REFUSED_ENDPOINTS = (
    ("http://evil.example.com", "host"),
    ("http://evil.example.com:1080", "host"),
    ("http://127.0.0.1.attacker.tld:1080", "host"),
    ("http://localhost.attacker.tld:1080", "host"),
    ("http://localhost.:5112", "host"),
    ("http://0177.0.0.1:5112", "host"),
    ("http://2130706433:5112", "host"),
    ("http://169.254.169.254:1080", "host"),
    ("http://user:pass@127.0.0.1:5112", "credentials"),
    ("file:///tmp", "scheme"),
    ("ftp://127.0.0.1:21", "scheme"),
    ("//127.0.0.1:5112", "scheme"),
    ("http://127.0.0.1:5112/path", "path"),
    ("http://127.0.0.1:5112/?a=b", "query"),
    ("http://127.0.0.1:5112/#f", "fragment"),
    ("http://127.0.0.1", "port"),
    ("http://localhost", "port"),
    ("http://[::1]", "port"),
    ("http://127.0.0.1:port", "port"),
    ("http://127.0.0.1:80", "port"),
    ("http://localhost:443", "port"),
    ("http://[::1]:1023", "port"),
    ("http://127.0.0.1:5112\n", "control character"),
    ("http://127.0.0.1 :5112", "whitespace"),
)

# Business identifiers no default-mode output may carry: the natural-key values,
# the customer number, the broker id, the broker's reference and the object URI's
# own prefix.
_REDACTED_FRAGMENTS = (
    "1000301",
    "1001",
    "42",
    "BRMOT001",
    DEFAULT_SOURCE_SYSTEM_KEY,
)

# Prefix of the private temporary directory one self-test run works inside.
_SCRATCH_PREFIX = "load-local-selftest-"

# Fragment that stands in for one text a case supplied to a run - a path, an
# endpoint, a bucket, a region, an extract date or a digest of the object the case
# served - while that run's output is searched for a business identifier. It
# carries no digit and no upper-case letter, so it forms no fragment of
# _REDACTED_FRAGMENTS, and it is not empty, so replacing a fragment with it never
# joins the characters either side of that fragment.
_INCIDENTAL_MARKER = "<incidental>"


class _Absent:
    """Marker naming a record member that a fixture removes."""


_ABSENT = _Absent()


def _json_object_text(members: Sequence[tuple[str, Any]]) -> str:
    """Return one JSON object holding ``members`` in the order given, on one line.

    A member name that appears twice in ``members`` appears twice in the text,
    which is how a duplicate-member document is produced without a parser that
    would collapse it.
    """
    body = ", ".join(
        f"{json.dumps(name)}: {json.dumps(value)}" for name, value in members
    )
    return "{" + body + "}\n"


def _record_text(
    members: Sequence[tuple[str, Any]] = _MOTOR_RECORD_MEMBERS, **changes: Any
) -> str:
    """Return one landing record built from ``members``, with ``changes`` applied.

    A change whose value is ``_ABSENT`` removes that member; every other change
    replaces the value of an existing member or appends a new one.
    """
    built: list[tuple[str, Any]] = []
    remaining = dict(changes)
    for name, value in members:
        if name in remaining:
            replacement = remaining.pop(name)
            if replacement is _ABSENT:
                continue
            built.append((name, replacement))
            continue
        built.append((name, value))
    built.extend(remaining.items())
    return _json_object_text(built)


def _record_bytes(
    members: Sequence[tuple[str, Any]] = _MOTOR_RECORD_MEMBERS, **changes: Any
) -> bytes:
    """Return the bytes of one landing record, as an object body carries them."""
    return _record_text(members, **changes).encode("utf-8")


# ---------------------------------------------------------------------------
# Self-test: support
# ---------------------------------------------------------------------------


class _Scratch:
    """One private directory a self-test run reads and writes inside.

    The directory is created below the system temporary directory under
    ``_SCRATCH_PREFIX``, so two runs in parallel never share a name. ``write``
    places one document in it and returns the path and ``absent`` names a path in
    it without creating it. ``database`` names a database directly inside
    ``DATABASE_DIRECTORY``, because that is the one directory this tool opens a
    database in, under a name of this run alone, and ``removed`` deletes the
    directory and every database this run named and reports that they are gone.
    """

    def __init__(self) -> None:
        self.path = Path(tempfile.mkdtemp(prefix=_SCRATCH_PREFIX))
        DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        self.database_prefix = f"{_SCRATCH_PREFIX}{self.path.name.rsplit('-', 1)[-1]}"
        self._databases: list[Path] = []

    def write(self, name: str, content: str | bytes) -> Path:
        """Return the path of ``name`` inside this directory, holding ``content``."""
        destination = self.path / name
        payload = content.encode("utf-8") if isinstance(content, str) else content
        destination.write_bytes(payload)
        return destination

    def absent(self, name: str) -> Path:
        """Return the path of ``name`` inside this directory without creating it."""
        return self.path / name

    def database(self, name: str) -> Path:
        """Return a database path this run may open, removing any earlier one.

        Every database a case opens sits directly inside ``DATABASE_DIRECTORY``,
        which is the one directory ``open_database`` opens a file in, under a name
        carrying this run's own prefix: no case reaches the database the bridge
        keeps at ``DEFAULT_DATABASE`` or any other path of the caller's, and
        ``removed`` deletes every one this run named.
        """
        destination = DATABASE_DIRECTORY / f"{self.database_prefix}-{name}"
        if destination not in self._databases:
            self._databases.append(destination)
        for path in (destination, Path(f"{destination}.wal")):
            if path.exists():
                path.unlink()
        return destination

    def removed(self) -> bool:
        """Remove this directory and every database this run named, and report it."""
        shutil.rmtree(self.path, ignore_errors=True)
        remaining = []
        for database in self._databases:
            for path in (database, Path(f"{database}.wal")):
                if path.exists():
                    try:
                        path.unlink()
                    except OSError:
                        pass
                if path.exists():
                    remaining.append(path)
        return not self.path.exists() and not remaining


class _RecordingClient:
    """One S3 client that records every call it is asked to make and delegates it.

    ``calls`` holds one ``(operation, arguments)`` pair per call, in call order.
    Every call reaches the wrapped client unchanged, so the operation, its
    parameters and its response stay those of the pinned boto3 client.
    """

    def __init__(self, client: Any) -> None:
        self._client = client
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def __getattr__(self, name: str) -> Any:
        """Return the wrapped attribute, wrapping a callable to record its call."""
        attribute = getattr(self._client, name)
        if not callable(attribute):
            return attribute

        def _call(**arguments: Any) -> Any:
            self.calls.append((name, arguments))
            return attribute(**arguments)

        return _call

    def operations(self) -> tuple[str, ...]:
        """Return the operations called so far, in call order."""
        return tuple(operation for operation, _ in self.calls)

    def arguments(self, operation: str) -> dict[str, Any]:
        """Return the arguments of the last call to ``operation``.

        Raises ``_SelfTestFailure`` when that operation was never called.
        """
        for name, arguments in reversed(self.calls):
            if name == operation:
                return arguments
        raise _SelfTestFailure(f"{operation} was never called")


class _ReplacingClient(_RecordingClient):
    """One S3 client that replaces the object under the key before it is read.

    Every ``get_object`` call first writes ``replacement`` to the key it names,
    so the object the download asks for is not the object the head request
    described. This is the race a version-pinned, entity-tag-conditioned read
    exists to fail on, driven here rather than waited for.
    """

    def __init__(self, client: Any, replacement: bytes) -> None:
        super().__init__(client)
        self._replacement = replacement

    def get_object(self, **arguments: Any) -> Any:
        """Replace the object named by ``arguments`` and then read it."""
        self.calls.append(("put_object", dict(arguments)))
        self._client.put_object(
            Bucket=arguments["Bucket"],
            Key=arguments["Key"],
            Body=self._replacement,
        )
        self.calls.append(("get_object", dict(arguments)))
        return self._client.get_object(**arguments)


class _InterruptingConnection:
    """One DuckDB connection that reports an interrupt for one statement.

    Every call reaches the wrapped connection unchanged except an ``execute`` whose
    statement carries ``fragment``: that one raises one of the two errors DuckDB
    raises when a statement is stopped by hand, named by ``shape``, and records the
    statement it was raised for. This is the interrupt a run stopped mid-transaction
    meets, driven here rather than waited for.
    """

    def __init__(
        self,
        connection: duckdb.DuckDBPyConnection,
        fragment: str,
        shape: type[BaseException] = duckdb.InterruptException,
    ) -> None:
        self._connection = connection
        self._fragment = fragment
        self._shape = shape
        self.interrupted: list[str] = []

    def execute(self, statement: str, *arguments: Any) -> Any:
        """Execute ``statement`` unless it carries the fragment, which interrupts it."""
        if self._fragment in statement:
            self.interrupted.append(statement)
            raise self._shape(INTERRUPTED_STATEMENT_TEXT)
        return self._connection.execute(statement, *arguments)

    def __getattr__(self, name: str) -> Any:
        """Return the wrapped attribute unchanged."""
        return getattr(self._connection, name)


# The two shapes DuckDB reports an interrupted statement as: its own interrupt error,
# and the RuntimeError it raises for the interrupt of this process that it consumed.
_INTERRUPT_SHAPES = (duckdb.InterruptException, RuntimeError)


class _RecordingHandler(logging.Handler):
    """One logging handler that keeps every record it is given.

    ``records`` holds them in emission order, so a case can establish both that a
    silenced logger emitted nothing and that the same logger emits while it is not
    silenced.
    """

    def __init__(self) -> None:
        super().__init__(level=logging.NOTSET)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Keep ``record`` and return None."""
        self.records.append(record)

    def messages(self) -> tuple[str, ...]:
        """Return the formatted message of every record kept, in emission order."""
        return tuple(record.getMessage() for record in self.records)


@contextlib.contextmanager
def _controlled_environment(scratch: _Scratch, **overrides: str) -> Any:
    """Run a case with every consulted environment variable set by that case alone.

    Every name in ``_CONSULTED_VARIABLES`` is removed, ``overrides`` are applied,
    and a profile file, a credentials file and the instance metadata service are
    pointed at paths inside ``scratch`` that do not exist, so a session resolves
    only what the case supplied. The previous environment is restored on the way
    out, whatever happened.
    """
    previous = {name: os.environ.get(name) for name in _CONSULTED_VARIABLES}
    for name in _CONSULTED_VARIABLES:
        os.environ.pop(name, None)
    os.environ["AWS_CONFIG_FILE"] = str(scratch.absent("no-such-config"))
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(
        scratch.absent("no-such-credentials")
    )
    os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
    os.environ.update(overrides)
    try:
        yield
    finally:
        for name in _CONSULTED_VARIABLES:
            os.environ.pop(name, None)
        for name, value in previous.items():
            if value is not None:
                os.environ[name] = value


def _run_cli(scratch: _Scratch, argv: list[str], **overrides: str) -> _CliResult:
    """Run one command line in this process and capture its status and streams.

    The run sees only the environment ``_controlled_environment`` establishes for
    it.
    """
    out = io.StringIO()
    err = io.StringIO()
    with _controlled_environment(scratch, **overrides):
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                status = main(argv)
            except SystemExit as request:
                status = request.code if isinstance(request.code, int) else 1
    return _CliResult(status=status, stdout=out.getvalue(), stderr=err.getvalue())


def _stubbed_client(region: str = _SELF_TEST_REGION) -> Any:
    """Return an S3 client of the pinned boto3 session, ready for a stubber.

    The client carries this module's own connection behaviour, so a stubbed call
    is validated against the same client the tool builds for a real run.
    """
    session = boto3.session.Session(
        region_name=region,
        aws_access_key_id=_SELF_TEST_CREDENTIALS["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=_SELF_TEST_CREDENTIALS["AWS_SECRET_ACCESS_KEY"],
    )
    return session.client(SERVICE_NAME, config=_client_config())


def _test_collaborators() -> tuple[Any, Any, Any]:
    """Return moto's in-process S3 context, botocore's stubber and its body type.

    All three are test collaborators of the pinned distributions and are imported
    here, so no mode but ``--self-test`` loads them.
    """
    from botocore.response import StreamingBody
    from botocore.stub import Stubber
    from moto import mock_aws

    return mock_aws, Stubber, StreamingBody


@contextlib.contextmanager
def _served_bucket(body: bytes | None = None, **overrides: Any) -> Any:
    """Serve one bucket over a loopback endpoint, yielding the endpoint URL.

    moto's in-process mock patches the client and answers no HTTP request, so a
    command line naming a loopback endpoint - which is what the run-mode contract
    requires of this loader - is served by moto's own server instead. The server
    listens on 127.0.0.1 on a port the operating system assigns, holds the bucket in
    memory, and is stopped on the way out whatever happened. ``body`` is written as
    the landed object when it is given, with the recorded metadata and the COPY
    manifest one landing writes beside it, so a command-line case reads the bucket a
    landing leaves; ``overrides`` reaches ``_put_landed_pair`` for a case that
    requires one element of that pair replaced or absent. With ``body`` None the
    bucket stays absent, which is the path an unreachable object takes.

    The server writes nothing of its own to this run's output. ``verbose=False``
    silences moto, and the request log of the WSGI server underneath it - one line
    per served request, on stderr, outside this tool's diagnostic form - is disabled
    for the lifetime of the server and restored to the state it was found in
    afterwards, whatever happened, so nothing this manager does outlives it.
    """
    from moto.server import ThreadedMotoServer

    request_log = logging.getLogger(_REQUEST_LOGGER_NAME)
    previous_disabled = request_log.disabled
    previous_level = request_log.level
    request_log.disabled = True
    request_log.setLevel(logging.CRITICAL)
    server = ThreadedMotoServer(ip_address=_LOOPBACK_ADDRESS, port=0, verbose=False)
    try:
        server.start()
    except BaseException:
        request_log.setLevel(previous_level)
        request_log.disabled = previous_disabled
        raise
    try:
        host, port = server.get_host_and_port()
        endpoint = f"http://{host}:{port}"
        if body is not None:
            client = boto3.session.Session(
                region_name=_SELF_TEST_REGION,
                aws_access_key_id=_SELF_TEST_CREDENTIALS["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=_SELF_TEST_CREDENTIALS["AWS_SECRET_ACCESS_KEY"],
            ).client(SERVICE_NAME, endpoint_url=endpoint, config=_client_config())
            try:
                client.create_bucket(
                    Bucket=_SELF_TEST_BUCKET,
                    CreateBucketConfiguration={
                        "LocationConstraint": _SELF_TEST_REGION
                    },
                )
            except ClientError as error:
                code = error.response.get("Error", {}).get("Code")
                if code not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                    raise
            _put_landed_pair(
                client, _SELF_TEST_BUCKET, _selftest_key(), body, **overrides
            )
        yield endpoint
    finally:
        server.stop()
        request_log.setLevel(previous_level)
        request_log.disabled = previous_disabled


def _read_served_object(endpoint: str) -> bytes:
    """Return the bytes of the landed object a served bucket holds at ``endpoint``.

    The read is one request to that endpoint through the pinned boto3 client
    carrying this module's own connection behaviour, so what a case establishes is
    what the server did with a request rather than what a patched client did.
    """
    client = boto3.session.Session(
        region_name=_SELF_TEST_REGION,
        aws_access_key_id=_SELF_TEST_CREDENTIALS["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=_SELF_TEST_CREDENTIALS["AWS_SECRET_ACCESS_KEY"],
    ).client(SERVICE_NAME, endpoint_url=endpoint, config=_client_config())
    response = client.get_object(Bucket=_SELF_TEST_BUCKET, Key=_selftest_key())
    return bytes(response["Body"].read())


@contextlib.contextmanager
def _captured_stderr() -> Any:
    """Capture the progress and warning lines a direct call writes to stderr."""
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        yield buffer


def _assert(condition: bool, message: str) -> None:
    """Raise ``_SelfTestFailure`` carrying ``message`` unless ``condition`` holds."""
    if not condition:
        raise _SelfTestFailure(message)


def _assert_equal(observed: Any, expected: Any, what: str) -> None:
    """Raise ``_SelfTestFailure`` unless ``observed`` equals ``expected``."""
    if observed != expected:
        raise _SelfTestFailure(f"{what} is {observed!r}, expected {expected!r}")


def _assert_in(fragment: str, text: str, what: str) -> None:
    """Raise ``_SelfTestFailure`` unless ``text`` carries ``fragment``."""
    if fragment not in text:
        raise _SelfTestFailure(
            f"{what} does not carry {fragment!r}: {_escaped(text, 240)}"
        )


def _assert_absent(fragment: str, text: str, what: str) -> None:
    """Raise ``_SelfTestFailure`` when ``text`` carries ``fragment``."""
    if fragment in text:
        raise _SelfTestFailure(
            f"{what} carries {fragment!r}: {_escaped(text, 240)}"
        )


def _incidental_text(
    scratch: _Scratch,
    database: Path,
    *,
    endpoint: str | None = None,
    body: bytes | None = None,
) -> tuple[str, ...]:
    """Return every text of a case's own making that this tool's output carries back.

    The private directory of the run, the database the case named, the directory a
    database sits in, the repository directory, the two shared DDL scripts, the
    bucket, the region and the extract date reach the progress lines as the case
    supplied them, and a temporary directory name assigned by the operating
    system carries characters of its own. ``endpoint`` and the port inside it, both
    assigned when a case starts a server, reach a diagnostic that names the
    endpoint. The digest and the entity tag of ``body`` are the digests of the
    object the case served, and the short digest of every fragment of
    ``_REDACTED_FRAGMENTS`` is what a redacted summary line carries in place of
    that identifier.

    Each text is returned as it stands and in the bounded renderings ``_escaped``
    produces for it, which is the form a diagnostic carries a long path in, longest
    first.
    """
    texts = [
        str(scratch.path),
        str(database),
        str(DATABASE_DIRECTORY),
        str(_REPOSITORY_DIR),
        _SELF_TEST_BUCKET,
        _SELF_TEST_REGION,
        _SELF_TEST_EXTRACT_DATE.isoformat(),
    ]
    texts.extend(str(path) for path in resolve_ddl_paths(True))
    if endpoint is not None:
        texts.append(endpoint)
        texts.append(endpoint.rsplit(":", 1)[-1])
    if body is not None:
        texts.append(hashlib.sha256(body).hexdigest())
        texts.append(_single_part_etag(body))
    texts.extend(_digest(fragment) for fragment in _REDACTED_FRAGMENTS)
    forms = {
        rendering
        for text in texts
        if text
        for rendering in (
            text,
            _escaped(text, MAX_DIAGNOSTIC_CHARACTERS),
            _escaped(text, MAX_DIAGNOSTIC_PATH_CHARACTERS),
        )
    }
    return tuple(sorted(forms, key=len, reverse=True))


def _without_incidental_text(text: str, incidental: Sequence[str]) -> str:
    """Return ``text`` with every fragment of ``incidental`` replaced by a marker.

    ``incidental`` is applied longest fragment first, so a path is replaced as a
    whole before any directory it sits under is.
    """
    remaining = text
    for fragment in incidental:
        remaining = remaining.replace(fragment, _INCIDENTAL_MARKER)
    return remaining


def _assert_identifiers_withheld(
    text: str, incidental: Sequence[str], what: str
) -> None:
    """Require no fragment of ``_REDACTED_FRAGMENTS`` outside ``incidental`` text.

    Every text of ``incidental`` is replaced by ``_INCIDENTAL_MARKER`` first, and
    every fragment is then required to be absent from what remains: a temporary
    directory name, an operating-system-assigned port, a repository path and a
    digest carry digits of their own, and none of them is a value this tool
    disclosed. An identifier carried anywhere else fails the case.
    """
    remaining = _without_incidental_text(text, incidental)
    for fragment in _REDACTED_FRAGMENTS:
        _assert_absent(fragment, remaining, what)


def _assert_raises(
    what: str,
    expected: type[BaseException] | tuple[type[BaseException], ...],
    fragment: str,
    body: Callable[[], Any],
) -> BaseException:
    """Run ``body``, requiring it to raise ``expected`` carrying ``fragment``.

    Returns the exception raised, so a case can inspect it further.
    """
    try:
        result = body()
    except expected as error:
        if fragment and fragment not in str(error):
            raise _SelfTestFailure(
                f"{what} was refused with {str(error)!r}, which does not carry "
                f"{fragment!r}"
            ) from error
        return error
    except _SelfTestFailure:
        raise
    except BaseException as error:  # noqa: BLE001 - reported as a failed case
        raise _SelfTestFailure(
            f"{what} raised {_type_name(error)}: {error}, expected "
            f"{getattr(expected, '__name__', expected)}"
        ) from error
    raise _SelfTestFailure(f"{what} was accepted, returning {result!r}")


def _assert_one_diagnostic(stderr: str) -> str:
    """Return the last stderr line, requiring one control-free diagnostic naming us."""
    _assert(bool(stderr), "the run wrote no diagnostic to stderr")
    lines = [line for line in stderr.splitlines() if line]
    _assert(bool(lines), "the run wrote only blank lines to stderr")
    line = lines[-1]
    _assert(
        line.startswith(f"{_PROGRAM}: "),
        f"the diagnostic does not name this tool: {line!r}",
    )
    _assert(
        _one_line(line) == line,
        f"the diagnostic carries a control character: {line!r}",
    )
    return line


def _single_part_etag(body: bytes) -> str:
    """Return the entity tag a single-part upload of ``body`` carries."""
    return hashlib.md5(body, usedforsecurity=False).hexdigest()


def _quoted_etag(body: bytes) -> str:
    """Return that entity tag as a store reports it, in double quotes."""
    return f'"{_single_part_etag(body)}"'


def _identity_of(body: bytes, version_id: str = NOT_VERSIONED) -> ObjectIdentity:
    """Return the identity a head request records for an object holding ``body``.

    The recorded digest and byte count are the ones land_to_s3.py writes as user
    metadata of an object holding ``body``, so this is the identity of a landed
    object rather than of one that carries no recorded provenance.
    """
    return ObjectIdentity(
        etag=_single_part_etag(body),
        version_id=version_id,
        content_length=len(body),
        recorded_sha256=hashlib.sha256(body).hexdigest(),
        recorded_content_length=len(body),
    )


def _recorded_object_metadata(body: bytes) -> dict[str, str]:
    """Return the user metadata land_to_s3.py records on an object holding ``body``.

    The two names and the two forms are the ones this module requires of every
    landed object, so a fixture written with this metadata is a fixture a landing
    would have produced.
    """
    return {
        RECORDED_SHA256_METADATA: hashlib.sha256(body).hexdigest(),
        RECORDED_LENGTH_METADATA: str(len(body)),
    }


def _copy_manifest_bytes(bucket: str, key: str, content_length: int) -> bytes:
    """Return the COPY manifest land_to_s3.py writes beside a landed object.

    The document carries one entry naming the object's URI, ``mandatory`` true and
    the byte count under a nested ``meta`` member, indented by two spaces and
    terminated by one line feed, which is byte for byte what that step writes for
    the same object.
    """
    document = {
        MANIFEST_ENTRIES_MEMBER: [
            {
                MANIFEST_URL_MEMBER: build_object_uri(bucket, key),
                MANIFEST_MANDATORY_MEMBER: True,
                MANIFEST_META_MEMBER: {
                    MANIFEST_CONTENT_LENGTH_MEMBER: content_length
                },
            }
        ]
    }
    text = json.dumps(document, indent=2, sort_keys=False) + "\n"
    return text.encode("ascii")


def _put_landed_pair(
    client: Any, bucket: str, key: str, body: bytes, **overrides: Any
) -> None:
    """Write the two objects one landing writes: the record and its COPY manifest.

    The record carries ``_recorded_object_metadata`` of ``body`` and the manifest
    sits at ``sibling_manifest_key`` of ``key`` naming that object and its byte
    count, so a seeded bucket holds what a successful landing left behind and a
    case exercises the confirmations a run performs rather than a fixture the run
    would refuse. ``overrides`` replaces one element of that pair for a case that
    requires a bucket a landing would not have produced: ``metadata`` for the
    record's user metadata, ``manifest`` for the manifest bytes, and ``manifest``
    of None for a prefix carrying no manifest at all.
    """
    metadata = overrides.get("metadata", _recorded_object_metadata(body))
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType=_SELF_TEST_CONTENT_TYPE,
        Metadata=metadata,
    )
    manifest = overrides.get(
        "manifest", _copy_manifest_bytes(bucket, key, len(body))
    )
    if manifest is None:
        return
    client.put_object(
        Bucket=bucket,
        Key=sibling_manifest_key(key),
        Body=manifest,
        ContentType=_SELF_TEST_CONTENT_TYPE,
    )


def _selftest_key(source_system_key: str = DEFAULT_SOURCE_SYSTEM_KEY) -> str:
    """Return the landing key every case that names an object uses."""
    return build_landing_key(
        source_system_key, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )


@contextlib.contextmanager
def _seeded_bucket(
    body: bytes, *, versioned: bool = False, **overrides: Any
) -> Any:
    """Run a case against an in-process bucket holding one landed object.

    The bucket is created inside moto's in-process S3, so no request leaves this
    process and no AWS resource is created. ``versioned`` turns on bucket
    versioning before the object is written, which is how a case reaches the
    version-pinned read. The object and its COPY manifest are written by
    ``_put_landed_pair``, so the bucket holds what a successful landing left
    behind; ``overrides`` reaches that helper for a case that requires one element
    of the pair replaced or absent. The client yielded is the pinned boto3 client
    carrying this module's own connection behaviour.
    """
    mock_aws, _, _ = _test_collaborators()
    with mock_aws():
        client = _stubbed_client()
        client.create_bucket(
            Bucket=_SELF_TEST_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": _SELF_TEST_REGION},
        )
        if versioned:
            client.put_bucket_versioning(
                Bucket=_SELF_TEST_BUCKET,
                VersioningConfiguration={"Status": "Enabled"},
            )
        _put_landed_pair(
            client, _SELF_TEST_BUCKET, _selftest_key(), body, **overrides
        )
        yield client


def _relation_shape(
    connection: duckdb.DuckDBPyConnection,
) -> tuple[tuple[int, str, str, str], ...]:
    """Return the physical shape of the raw relation as the catalog reports it.

    Each entry is the ordinal position, the column name, the data type and
    whether the column accepts null, read from ``information_schema.columns`` in
    ordinal order. Reading the catalog rather than the script establishes the
    shape the database actually holds, so an extra column, a missing column, a
    renamed column and a reordered column are all visible.
    """
    rows = connection.execute(
        "SELECT ordinal_position, column_name, data_type, is_nullable "
        "FROM information_schema.columns "
        "WHERE table_schema = ? AND table_name = ? "
        "ORDER BY ordinal_position",
        [RAW_SCHEMA_NAME, RAW_TABLE_NAME],
    ).fetchall()
    return tuple(
        (int(position), str(name), str(data_type), str(nullable))
        for position, name, data_type, nullable in rows
    )


def _row_count(connection: duckdb.DuckDBPyConnection) -> int:
    """Return the number of rows the raw relation holds."""
    result = connection.execute(
        f"SELECT count(*) FROM {qualified_relation_name()}"
    ).fetchall()
    return int(result[0][0])


def _rows_for_key(
    connection: duckdb.DuckDBPyConnection,
    columns: Sequence[str],
    key_values: Sequence[str],
) -> tuple[tuple[Any, ...], ...]:
    """Return every row carrying ``key_values`` as its natural key, in column order."""
    predicate = " AND ".join(f"{field} = ?" for field in NATURAL_KEY_FIELDS)
    result = connection.execute(
        f"SELECT {', '.join(columns)} FROM {qualified_relation_name()} "
        f"WHERE {predicate}",
        list(key_values),
    ).fetchall()
    return tuple(tuple(row) for row in result)


def _load_into(
    scratch: _Scratch,
    database: Path,
    body: bytes,
    *,
    show_identifiers: bool = False,
) -> LoadOutcome:
    """Load one landed object into ``database`` through the whole load path.

    The object is served by moto's in-process S3, so the head request, the
    version-pinned conditional read, the digest check, the schema validation and
    the transactional write are all the ones a real run performs.
    """
    ddl_paths = resolve_ddl_paths(True)
    with _seeded_bucket(body):
        with _controlled_environment(scratch, **_SELF_TEST_CREDENTIALS):
            with _captured_stderr():
                return load_record(
                    _SELF_TEST_BUCKET,
                    _selftest_key(),
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    _SELF_TEST_EXTRACT_DATE,
                    database,
                    ddl_paths,
                    region=_SELF_TEST_REGION,
                    show_identifiers=show_identifiers,
                )

# ---------------------------------------------------------------------------
# Self-test: cases
# ---------------------------------------------------------------------------


def _case_schema_present() -> str:
    """The landing schema loads, is a 2020-12 schema, and declares the 17 columns."""
    schema = load_schema()
    columns = read_column_names(schema, DEFAULT_SCHEMA)
    validator = build_validator(schema, DEFAULT_SCHEMA)
    _assert_equal(len(columns), EXPECTED_COLUMN_COUNT, "landed column count")
    _assert_equal(
        columns,
        tuple(name for name, _ in _MOTOR_RECORD_MEMBERS),
        "the landed column names and their order",
    )
    _assert_equal(
        columns[: len(NATURAL_KEY_FIELDS)],
        NATURAL_KEY_FIELDS,
        "the leading landed columns",
    )
    _assert_equal(read_column_names(load_schema()), columns, "the columns read from the schema")
    _assert(
        isinstance(validator, Draft202012Validator),
        "the validator built for the landing schema is not a 2020-12 validator",
    )
    return f"{len(columns)} landed columns, first {columns[0]!r}"


def _case_schema_failures(scratch: _Scratch) -> str:
    """Every way the landing schema can be unusable is refused and named."""
    checks = (
        ("a missing schema", scratch.absent("no-such-schema.json"), "cannot be read"),
        ("an empty schema", scratch.write("empty-schema.json", ""), "is empty"),
        (
            "an unparseable schema",
            scratch.write("broken-schema.json", "{"),
            "not readable JSON",
        ),
        (
            "a schema that is not an object",
            scratch.write("array-schema.json", "[]"),
            "at its top level",
        ),
        (
            "a schema carrying a repeated member",
            scratch.write(
                "duplicate-schema.json",
                '{"$schema": "a", "$schema": "b", "properties": {}}',
            ),
            "more than once",
        ),
    )
    for what, path, fragment in checks:
        _assert_raises(what, SchemaError, fragment, lambda path=path: load_schema(path))
    structural = (
        (
            "a schema with no properties block",
            {"$schema": Draft202012Validator.META_SCHEMA["$id"]},
            "no properties object",
        ),
        (
            "a schema declaring too few columns",
            {
                "$schema": Draft202012Validator.META_SCHEMA["$id"],
                "properties": {"source_system_key": {}, "policy_number": {}},
            },
            f"{EXPECTED_COLUMN_COUNT} landed columns are expected",
        ),
        (
            "a schema declaring a name that is not an identifier",
            {
                "$schema": Draft202012Validator.META_SCHEMA["$id"],
                "properties": {f"Column {index}": {} for index in range(17)},
            },
            "not an unquoted SQL identifier",
        ),
    )
    for what, document, fragment in structural:
        _assert_raises(
            what,
            SchemaError,
            fragment,
            lambda document=document: read_column_names(document, DEFAULT_SCHEMA),
        )
    dialects = (
        (
            "a schema declaring no dialect",
            {"properties": {}},
            "declares no '$schema' dialect",
        ),
        (
            "a schema declaring another dialect",
            {"$schema": "https://json-schema.org/draft-07/schema"},
            "this tool applies",
        ),
        (
            "a document that is not a valid schema",
            {
                "$schema": Draft202012Validator.META_SCHEMA["$id"],
                "properties": {"a": {"type": "not-a-type"}},
            },
            "not a valid 2020-12 schema",
        ),
    )
    for what, document, fragment in dialects:
        _assert_raises(
            what,
            SchemaError,
            fragment,
            lambda document=document: build_validator(document, DEFAULT_SCHEMA),
        )
    real_columns = read_column_names(load_schema(), DEFAULT_SCHEMA)
    mismatched = {
        "$schema": Draft202012Validator.META_SCHEMA["$id"],
        "properties": {name: {} for name in real_columns},
        "required": list(reversed(real_columns)),
    }
    _assert_raises(
        "a schema whose required list disagrees with its properties",
        SchemaError,
        "do not agree",
        lambda: read_column_names(mismatched, DEFAULT_SCHEMA),
    )
    return f"{len(checks) + len(structural) + len(dialects) + 1} schema faults refused"


def _case_record_accepted() -> str:
    """Both landed records parse, satisfy the schema and yield the values as landed."""
    schema = load_schema()
    columns = read_column_names(schema, DEFAULT_SCHEMA)
    validator = build_validator(schema, DEFAULT_SCHEMA)
    key = _selftest_key()
    checks = (
        ("motor", _MOTOR_RECORD_MEMBERS, "1000301", "450", None),
        ("commercial", _COMMERCIAL_RECORD_MEMBERS, "1000302", None, "13500"),
    )
    for what, members, policy_number, motor, fire in checks:
        record = parse_record(_record_bytes(members), key)
        validate_record(record, validator, key)
        confirm_record_contract(record, columns, key)
        confirm_source_system_key(record, DEFAULT_SOURCE_SYSTEM_KEY, key)
        _assert_equal(
            natural_key_values(record, key),
            (DEFAULT_SOURCE_SYSTEM_KEY, policy_number),
            f"the natural key of the {what} record",
        )
        values = record_values(record, columns)
        _assert_equal(len(values), EXPECTED_COLUMN_COUNT, f"{what} value count")
        _assert_equal(
            values[columns.index("motor_premium_amount")],
            motor,
            f"the motor premium of the {what} record",
        )
        _assert_equal(
            values[columns.index("fire_premium_amount")],
            fire,
            f"the fire premium of the {what} record",
        )
        _assert_equal(
            values[columns.index("payment_amount")],
            dict(members)["payment_amount"],
            f"the payment amount of the {what} record",
        )
    return f"{len(checks)} records accepted with values as landed"


def _case_record_refusals() -> str:
    """Every breach of the landed record contract is refused and named."""
    schema = load_schema()
    columns = read_column_names(schema, DEFAULT_SCHEMA)
    validator = build_validator(schema, DEFAULT_SCHEMA)
    key = _selftest_key()
    parse_failures = (
        ("a body that is not UTF-8", b"\xff\xfe{}", "not valid UTF-8"),
        ("an unparseable body", b"{", "not well-formed JSON"),
        (
            "a body carrying two documents",
            _record_bytes() + _record_bytes(),
            "more than one JSON document",
        ),
        ("a body carrying an array", b"[]\n", "at its top level"),
    )
    for what, body, fragment in parse_failures:
        _assert_raises(
            what, ObjectError, fragment, lambda body=body: parse_record(body, key)
        )
    contract_failures = (
        (
            "a record omitting a landed column",
            _record_text(policy_type=_ABSENT),
            "omits",
        ),
        (
            "a record carrying an undeclared key",
            _record_text(extra_column="x"),
            "does not declare",
        ),
        (
            "a record carrying a number",
            _record_text(payment_amount=500),
            "the landing contract carries every value",
        ),
        (
            "a record carrying a boolean",
            _record_text(payment_amount=True),
            "the landing contract carries every value",
        ),
        (
            "a record carrying a nested object",
            _record_text(payment_amount={"amount": "500"}),
            "the landing contract carries every value",
        ),
    )
    for what, text, fragment in contract_failures:
        record = parse_record(text.encode("utf-8"), key)
        _assert_raises(
            what,
            ObjectError,
            fragment,
            lambda record=record: confirm_record_contract(record, columns, key),
        )
    schema_failures = (
        ("a record carrying an unknown policy type", _record_text(policy_type="X")),
        ("a record carrying a policy number of zero", _record_text(policy_number="0")),
        (
            "a record carrying a truncated timestamp",
            _record_text(last_changed="2026-08-19T12:00:00"),
        ),
        (
            "a record carrying an unsuccessful return code",
            _record_text(return_code="99"),
        ),
        (
            "a record carrying a null policy number",
            _record_text(policy_number=None),
        ),
    )
    for what, text in schema_failures:
        record = parse_record(text.encode("utf-8"), key)
        _assert_raises(
            what,
            ObjectError,
            "does not satisfy the landing schema",
            lambda record=record: validate_record(record, validator, key),
        )
    key_failures = (
        ("a record carrying an empty policy number", _record_text(policy_number="")),
    )
    for what, text in key_failures:
        record = parse_record(text.encode("utf-8"), key)
        _assert_raises(
            what,
            ObjectError,
            "natural key",
            lambda record=record: natural_key_values(record, key),
        )
    other_key = parse_record(
        _record_text(source_system_key="OTHER_SYSTEM").encode("utf-8"), key
    )
    _assert_raises(
        "a record carrying another source-system key",
        ObjectError,
        "the two must agree",
        lambda: confirm_source_system_key(other_key, DEFAULT_SOURCE_SYSTEM_KEY, key),
    )
    return (
        f"{len(parse_failures)} parse, {len(contract_failures)} contract, "
        f"{len(schema_failures)} schema and {len(key_failures) + 1} key faults refused"
    )


def _case_schema_violations_reported_once() -> str:
    """One breach is reported once and every distinct violation is reported.

    A record carrying only the two natural-key columns breaches ``required`` once
    per omitted column, and each of those violations renders as the same
    constraint, declared list, omitted properties and rejected shape; the
    diagnostic carries that rendering once and withholds nothing. A record
    breaching four different constraints carries all four. With record values shown
    the library's own message distinguishes each omission, and every one of those
    messages is kept, so the report stays bounded by its limit rather than
    collapsed.
    """
    validator = build_validator(load_schema(), DEFAULT_SCHEMA)
    key = _selftest_key()
    omitting = parse_record(
        _json_object_text(
            _MOTOR_RECORD_MEMBERS[: len(NATURAL_KEY_FIELDS)]
        ).encode("utf-8"),
        key,
    )
    breaching = parse_record(
        _record_text(
            issue_date="19-08-2026", payment_amount="500.00", extra_column="x"
        ).encode("utf-8"),
        key,
    )
    omitted_count = EXPECTED_COLUMN_COUNT - len(NATURAL_KEY_FIELDS)
    previously_shown = show_identifiers_enabled()
    set_show_identifiers(False)
    try:
        omissions = str(
            _assert_raises(
                f"a record carrying {len(NATURAL_KEY_FIELDS)} landed columns",
                ObjectError,
                "does not satisfy the landing schema",
                lambda: validate_record(omitting, validator, key),
            )
        )
        _assert_equal(
            omissions.count("the 'required' constraint is not satisfied"),
            1,
            "the times one omission constraint is reported",
        )
        _assert_absent("further violations", omissions, "the omission diagnostic")
        _assert_absent("1000301", omissions, "the omission diagnostic")
        _assert_in(
            "the properties at issue are", omissions, "the omission diagnostic"
        )
        distinct = str(
            _assert_raises(
                "a record breaching four constraints",
                ObjectError,
                "does not satisfy the landing schema",
                lambda: validate_record(breaching, validator, key),
            )
        )
        breaches = (
            "at /: the 'additionalProperties' constraint",
            "at /issue_date: the 'pattern' constraint",
            "at /issue_date: the 'format' constraint",
            "at /payment_amount: the 'pattern' constraint",
        )
        for breach in breaches:
            _assert_equal(
                distinct.count(breach), 1, f"the times {breach!r} is reported"
            )
        _assert_absent("further violations", distinct, "the four-breach diagnostic")
        for value in ("19-08-2026", "500.00", "1000301"):
            _assert_absent(value, distinct, "the four-breach diagnostic")
        set_show_identifiers(True)
        shown = str(
            _assert_raises(
                "the same omissions with record values shown",
                ObjectError,
                "does not satisfy the landing schema",
                lambda: validate_record(omitting, validator, key),
            )
        )
        _assert_in(
            f"(+{omitted_count - MAX_REPORTED_SCHEMA_ERRORS} further violations)",
            shown,
            "the omission diagnostic under --show-identifiers",
        )
        for name in ("broker_id", "customer_number"):
            _assert_in(
                f"'{name}' is a required property",
                shown,
                "the omission diagnostic under --show-identifiers",
            )
    finally:
        set_show_identifiers(previously_shown)
    return (
        f"{omitted_count} omission violations reported as 1, {len(breaches)} "
        f"distinct violations each reported once, and {omitted_count} distinct "
        "messages kept under --show-identifiers"
    )


def _case_duplicate_members_refused(scratch: _Scratch) -> str:
    """A repeated member is refused at every nesting level of every document read."""
    key = _selftest_key()
    duplicates = (
        (
            "a record carrying a repeated landed column",
            _json_object_text(
                (*_MOTOR_RECORD_MEMBERS, ("policy_number", "9999999"))
            ),
            "policy_number",
        ),
        (
            "a record carrying a repeated member below the top level",
            '{"source_system_key": {"a": "1", "a": "2"}}\n',
            "a",
        ),
        (
            "a record carrying a repeated member in a nested array",
            '{"source_system_key": [{"b": "1", "b": "2"}]}\n',
            "b",
        ),
    )
    for what, text, member in duplicates:
        error = _assert_raises(
            what,
            ObjectError,
            "more than once",
            lambda text=text: parse_record(text.encode("utf-8"), key),
        )
        _assert_in(member, str(error), f"the diagnostic for {what}")
    nested_schema = scratch.write(
        "nested-duplicate-schema.json",
        '{"$schema": "x", "properties": {"a": {"type": "string", "type": "null"}}}',
    )
    error = _assert_raises(
        "a schema carrying a repeated member below the top level",
        SchemaError,
        "more than once",
        lambda: load_schema(nested_schema),
    )
    _assert_in("type", str(error), "the diagnostic for a nested schema duplicate")
    _assert_equal(
        parse_json_document('{"a": "1", "b": {"c": "2"}}'),
        {"a": "1", "b": {"c": "2"}},
        "a document carrying no repeated member",
    )
    _assert_equal(
        len(parse_record(_record_bytes(), key)),
        EXPECTED_COLUMN_COUNT,
        "the members of the landed record",
    )
    return f"{len(duplicates) + 1} repeated members refused, valid documents parsed"


def _case_nesting_bounded(scratch: _Scratch) -> str:
    """An object past a parser bound is a rejected object, never a traceback.

    The depth scan is put to a document nested exactly at the bound, one nested one
    level past it, and documents whose brackets sit inside a landed value, so the
    bound admits every document of the landing contract - the landed object, the
    landing schema and the COPY manifest - and counts nothing a value carries. The
    object funnel and the schema funnel are then put to a document nested far past
    the bound and to an integer literal longer than the interpreter converts, each of
    which reached the caller as a parser traceback and a status outside this tool's
    contract before the bound existed. The command line is put to the same document
    served as the landed object, with the digest and the manifest of a real landing,
    so the object passes every integrity check and is refused for what it carries
    rather than for its provenance; nothing reaches the database. The interpreter's
    own nesting bound is exercised with the real parser, by admitting a document
    deeper than it can take, so the fallback that reports it is the one a run would
    take.
    """
    key = _selftest_key()
    at_bound = "[" * MAX_JSON_NESTING_DEPTH + "1" + "]" * MAX_JSON_NESTING_DEPTH
    _assert_equal(
        json_nesting_depth(at_bound),
        MAX_JSON_NESTING_DEPTH,
        "the depth of a document nested at the bound",
    )
    innermost = parse_json_document(at_bound)
    for _ in range(MAX_JSON_NESTING_DEPTH):
        innermost = innermost[0]
    _assert_equal(innermost, 1, "the value a document nested at the bound carries")
    past_bound = "[" * (MAX_JSON_NESTING_DEPTH + 1) + "]" * (
        MAX_JSON_NESTING_DEPTH + 1
    )
    _assert_equal(
        json_nesting_depth(past_bound),
        MAX_JSON_NESTING_DEPTH + 1,
        "the depth reported for a document one level past the bound",
    )
    _assert_raises(
        "a document nested one level past the bound",
        UnparsableDocumentError,
        f"nest more than {MAX_JSON_NESTING_DEPTH} levels deep",
        lambda: parse_json_document(past_bound),
    )
    for label, text, depth in (
        ("brackets inside a landed value", '{"a": "[[[[[[["}', 1),
        ("an escaped quote before them", '{"a": "\\"[[[[["}', 1),
        ("a landed object", _record_text(), 1),
        ("a COPY manifest", _copy_manifest_bytes(
            _SELF_TEST_BUCKET, key, 499
        ).decode("ascii"), 4),
        ("the landing schema", DEFAULT_SCHEMA.read_text(encoding="utf-8"), 6),
    ):
        _assert_equal(json_nesting_depth(text), depth, f"the depth of {label}")

    deep = "[" * _SELF_TEST_DEEP_NESTING + "]" * _SELF_TEST_DEEP_NESTING
    deep_error = _assert_raises(
        "an object nested far past the bound",
        ObjectError,
        "is not a document this tool parses",
        lambda: parse_record(deep.encode("utf-8"), key),
    )
    _assert_in(
        f"nest more than {MAX_JSON_NESTING_DEPTH} levels deep",
        str(deep_error),
        "the diagnostic of an object nested past the bound",
    )
    _assert_equal(
        deep_error.exit_status,
        EXIT_OBJECT_REJECTED,
        "the status a refused parse returns",
    )
    schema_path = scratch.write("deep-schema.json", deep)
    _assert_raises(
        "a schema nested far past the bound",
        SchemaError,
        "is not a document this tool parses",
        lambda: load_schema(schema_path),
    )
    long_integer = f"{{\"policy_number\": {'9' * _SELF_TEST_LONG_INTEGER_DIGITS}}}\n"
    _assert_raises(
        "an object carrying an integer literal longer than the interpreter converts",
        ObjectError,
        "the parser refused a value it carries",
        lambda: parse_record(long_integer.encode("utf-8"), key),
    )
    interpreter_error = _assert_raises(
        "a document within a raised bound that the interpreter cannot parse",
        UnparsableDocumentError,
        "which the interpreter running this tool cannot parse",
        lambda: parse_json_document(deep, depth_limit=_SELF_TEST_DEEP_NESTING),
    )
    _assert_in(
        f"nests {_SELF_TEST_DEEP_NESTING} levels deep",
        str(interpreter_error),
        "the diagnostic naming the depth the interpreter refused",
    )

    database = scratch.database("nesting.duckdb")
    for label, served in (
        ("nested far past the bound", deep.encode("utf-8")),
        ("carrying a long integer literal", long_integer.encode("utf-8")),
    ):
        with _served_bucket(served) as endpoint:
            run = _run_cli(
                scratch,
                [
                    "--bucket",
                    _SELF_TEST_BUCKET,
                    "--region",
                    _SELF_TEST_REGION,
                    "--endpoint-url",
                    endpoint,
                    "--extract-date",
                    _SELF_TEST_EXTRACT_DATE.isoformat(),
                    "--database",
                    str(database),
                ],
                **_SELF_TEST_CREDENTIALS,
            )
        _assert_equal(
            run.status,
            EXIT_OBJECT_REJECTED,
            f"the status of a command line reading an object {label}",
        )
        _assert_equal(run.stdout, "", f"the stdout of an object {label}")
        _assert_absent("Traceback", run.stderr, f"the stderr of an object {label}")
        _assert_one_diagnostic(run.stderr)
        _assert(
            not database.exists(),
            f"an object {label} reached the database at {database}",
        )
    return (
        f"the bound of {MAX_JSON_NESTING_DEPTH} admits every contract document, "
        f"{_SELF_TEST_DEEP_NESTING}-deep and {_SELF_TEST_LONG_INTEGER_DIGITS}-digit "
        f"objects refused with status {EXIT_OBJECT_REJECTED} and no database opened"
    )


def _case_recorded_identity_confirmed(scratch: _Scratch) -> str:
    """An object that is not the bytes the landing recorded is never loaded.

    The land-time digest and byte count modernization/landing/land_to_s3.py records
    as user metadata of the landed object are required and are compared with the
    bytes that arrived. One bucket holds the object a landing left and loads; the
    others hold an object whose metadata was rewritten out of band - absent, of an
    unusable shape, the digest of other bytes, and a byte count the object does not
    carry - and every one of them is refused with the object status and no database
    opened. The tampered body is the same length as the landed one and is written
    with its own entity tag, so neither the recorded byte count of the head request
    nor the ETag check detects it: the land-time digest is what does.
    """
    body = _record_bytes()
    tampered = _record_bytes(brokers_reference="TAMPERED")
    _assert_equal(
        len(tampered), len(body), "the tampered fixture's length against the landed one"
    )
    recorded = _recorded_object_metadata(body)
    database = scratch.database("recorded-identity.duckdb")
    ddl_paths = resolve_ddl_paths(True)

    def _load(served: bytes, **overrides: Any) -> Any:
        """Return what one load of ``served`` did, or raise what refused it."""
        with _seeded_bucket(served, **overrides):
            with _controlled_environment(scratch, **_SELF_TEST_CREDENTIALS):
                with _captured_stderr():
                    return load_record(
                        _SELF_TEST_BUCKET,
                        _selftest_key(),
                        DEFAULT_SOURCE_SYSTEM_KEY,
                        _SELF_TEST_EXTRACT_DATE,
                        database,
                        ddl_paths,
                        region=_SELF_TEST_REGION,
                    )

    outcome = _load(body)
    _assert_equal(outcome.written, 1, "the rows a recorded object wrote")
    _assert_equal(
        outcome.identity.recorded_sha256,
        recorded[RECORDED_SHA256_METADATA],
        "the digest the head request recorded",
    )
    _assert_equal(
        outcome.identity.recorded_content_length,
        len(body),
        "the byte count the head request recorded",
    )
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(_row_count(connection), 1, "the row a recorded object left")
    finally:
        connection.close()

    faults = (
        (
            "an object carrying no recorded metadata",
            body,
            {"metadata": {}},
            "carries no land-time digest",
        ),
        (
            "an object whose recorded digest is not 64 hex characters",
            body,
            {
                "metadata": {
                    RECORDED_SHA256_METADATA: "not-a-digest",
                    RECORDED_LENGTH_METADATA: str(len(body)),
                }
            },
            "carries no land-time digest",
        ),
        (
            "an object carrying no recorded byte count",
            body,
            {"metadata": {RECORDED_SHA256_METADATA: recorded[
                RECORDED_SHA256_METADATA
            ]}},
            "carries no land-time byte count",
        ),
        (
            "an object rewritten out of band to the same length",
            tampered,
            {"metadata": recorded},
            "are not the bytes that were landed",
        ),
        (
            "an object whose recorded byte count is not its length",
            body,
            {
                "metadata": {
                    RECORDED_SHA256_METADATA: recorded[RECORDED_SHA256_METADATA],
                    RECORDED_LENGTH_METADATA: str(len(body) + 1),
                }
            },
            "are not the bytes that were landed",
        ),
    )
    for what, served, overrides, fragment in faults:
        error = _assert_raises(
            what,
            ObjectError,
            fragment,
            lambda served=served, overrides=overrides: _load(served, **overrides),
        )
        _assert_equal(
            error.exit_status,
            EXIT_OBJECT_REJECTED,
            f"the status {what} returns",
        )
        _assert_absent("TAMPERED", str(error), f"the diagnostic of {what}")
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(
            _row_count(connection), 1, "the rows the refused loads left behind"
        )
        _assert_equal(
            _rows_for_key(
                connection, ("brokers_reference",), outcome.key_values
            ),
            (("BRMOT001",),),
            "the value the row still carries after every refused load",
        )
    finally:
        connection.close()
    return (
        f"1 recorded object loaded, {len(faults)} unverifiable or rewritten objects "
        "refused with the landed row unchanged"
    )


def _case_manifest_binds_object(scratch: _Scratch) -> str:
    """The COPY manifest of the part must name the object that was downloaded.

    modernization/landing/land_to_s3.py writes the manifest after the object, so an
    object whose manifest does not name it, or names another byte count, is not the
    pair one landing produced. Every way that manifest can fail to bind this load -
    absent, empty, malformed, not an object, naming no entries, naming two, naming
    another object, carrying mandatory false, carrying no usable byte count and
    carrying the wrong one - is refused with the object status and no database
    opened, and the manifest of the part is derived from the key that was
    downloaded rather than from a setting.
    """
    body = _record_bytes()
    key = _selftest_key()
    database = scratch.database("manifest-binding.duckdb")
    ddl_paths = resolve_ddl_paths(True)
    _assert_equal(
        sibling_manifest_key(key),
        key[: -len(OBJECT_NAME)] + MANIFEST_OBJECT_NAME,
        "the manifest key derived from the object key",
    )
    _assert_equal(
        sibling_manifest_key(
            build_landing_key(
                DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE, 7
            )
        ).rsplit(KEY_SEPARATOR, 1)[-1],
        manifest_object_name(7),
        "the manifest name derived for another part",
    )
    _assert_raises(
        "a key that is not the key of one landed record",
        ObjectError,
        "cannot be named",
        lambda: sibling_manifest_key("landing/part-0000.manifest.json"),
    )

    def _load(**overrides: Any) -> Any:
        """Return what one load did with ``overrides`` applied to the seeded pair."""
        with _seeded_bucket(body, **overrides):
            with _controlled_environment(scratch, **_SELF_TEST_CREDENTIALS):
                with _captured_stderr():
                    return load_record(
                        _SELF_TEST_BUCKET,
                        key,
                        DEFAULT_SOURCE_SYSTEM_KEY,
                        _SELF_TEST_EXTRACT_DATE,
                        database,
                        ddl_paths,
                        region=_SELF_TEST_REGION,
                    )

    def _manifest(
        url: Any, mandatory: Any, content_length: Any, entries: int = 1
    ) -> bytes:
        """Return a manifest carrying ``entries`` copies of one entry, as bytes."""
        entry = {
            MANIFEST_URL_MEMBER: url,
            MANIFEST_MANDATORY_MEMBER: mandatory,
            MANIFEST_META_MEMBER: {
                MANIFEST_CONTENT_LENGTH_MEMBER: content_length
            },
        }
        document = {MANIFEST_ENTRIES_MEMBER: [dict(entry) for _ in range(entries)]}
        return (json.dumps(document, indent=2) + "\n").encode("ascii")

    outcome = _load()
    _assert_equal(outcome.written, 1, "the rows a bound object wrote")
    uri = build_object_uri(_SELF_TEST_BUCKET, key)
    other_uri = build_object_uri(
        _SELF_TEST_BUCKET,
        build_landing_key(
            DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE, 1
        ),
    )
    faults = (
        ("no manifest beside the object", None, AccessError, "COPY manifest"),
        ("an empty manifest", b"", ObjectError, "is empty"),
        (
            "a manifest that is not well-formed JSON",
            b'{"entries": [',
            ObjectError,
            "not well-formed JSON",
        ),
        (
            "a manifest carrying an array at its top level",
            b"[]\n",
            ObjectError,
            "at its top level",
        ),
        (
            "a manifest naming no entries",
            b'{"entries": null}\n',
            ObjectError,
            "an array of entries is required",
        ),
        (
            "a manifest naming two entries",
            _manifest(uri, True, len(body), entries=2),
            ObjectError,
            "names 2 entries",
        ),
        (
            "a manifest whose entry is not an object",
            b'{"entries": ["s3://elsewhere"]}\n',
            ObjectError,
            "as its entry",
        ),
        (
            "a manifest naming another object",
            _manifest(other_uri, True, len(body)),
            ObjectError,
            "as the object of this load",
        ),
        (
            "a manifest naming no object at all",
            _manifest(None, True, len(body)),
            ObjectError,
            "as the object of this load",
        ),
        (
            "a manifest carrying mandatory false",
            _manifest(uri, False, len(body)),
            ObjectError,
            f"as {_shown(MANIFEST_MANDATORY_MEMBER)}",
        ),
        (
            "a manifest carrying no usable byte count",
            _manifest(uri, True, str(len(body))),
            ObjectError,
            "the byte count of the landed object is required",
        ),
        (
            "a manifest carrying a boolean byte count",
            _manifest(uri, True, True),
            ObjectError,
            "the byte count of the landed object is required",
        ),
        (
            "a manifest naming another byte count",
            _manifest(uri, True, len(body) + 1),
            ObjectError,
            f"names {len(body) + 1} bytes",
        ),
        (
            "a manifest carrying no meta member",
            (
                json.dumps(
                    {
                        MANIFEST_ENTRIES_MEMBER: [
                            {
                                MANIFEST_URL_MEMBER: uri,
                                MANIFEST_MANDATORY_MEMBER: True,
                            }
                        ]
                    },
                    indent=2,
                )
                + "\n"
            ).encode("ascii"),
            ObjectError,
            f"as {_shown(MANIFEST_META_MEMBER)}",
        ),
        (
            "a manifest carrying its entry twice",
            b'{"entries": [], "entries": []}\n',
            ObjectError,
            "more than once",
        ),
        (
            "a manifest nested far past the parse bound",
            ("[" * _SELF_TEST_DEEP_NESTING).encode("ascii"),
            ObjectError,
            "is not a document this tool parses",
        ),
    )
    for what, manifest, expected, fragment in faults:
        error = _assert_raises(
            what,
            expected,
            fragment,
            lambda manifest=manifest: _load(manifest=manifest),
        )
        _assert_equal(
            error.exit_status,
            EXIT_OBJECT_REJECTED if expected is ObjectError else EXIT_S3_UNAVAILABLE,
            f"the status {what} returns",
        )
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(
            _row_count(connection), 1, "the rows the refused loads left behind"
        )
    finally:
        connection.close()
    return (
        f"1 bound object loaded, {len(faults)} manifests that do not bind it refused"
    )


def _case_show_identifiers_environment_matches_flag(scratch: _Scratch) -> str:
    """The option and the environment variable select the same output.

    The same object is loaded three times over the same database: once with
    ``--show-identifiers``, once with ``SHOW_IDENTIFIERS_VARIABLE`` carrying an
    enabling value and no option, and once with neither. The two disclosing runs
    are required to write byte-identical stdout, which is what this tool's help
    states, and the third to withhold every identifier. The rows removed and
    written differ between runs of one database, so the counts of each run are
    replaced by a marker before the two lines are compared and the counts
    themselves are asserted separately.
    """
    database = scratch.database("show-identifiers.duckdb")
    body = _record_bytes()

    def _arguments(endpoint: str, *extra: str) -> list[str]:
        """Return the command line loading the served object into this database."""
        return [
            "--bucket",
            _SELF_TEST_BUCKET,
            "--region",
            _SELF_TEST_REGION,
            "--endpoint-url",
            endpoint,
            "--extract-date",
            _SELF_TEST_EXTRACT_DATE.isoformat(),
            "--database",
            str(database),
            *extra,
        ]

    with _served_bucket(body) as endpoint:
        by_option = _run_cli(
            scratch,
            _arguments(endpoint, "--show-identifiers"),
            **_SELF_TEST_CREDENTIALS,
        )
    with _served_bucket(body) as endpoint:
        by_variable = _run_cli(
            scratch,
            _arguments(endpoint),
            **{
                **_SELF_TEST_CREDENTIALS,
                SHOW_IDENTIFIERS_VARIABLE: SHOW_IDENTIFIERS_ENABLING[0],
            },
        )
    with _served_bucket(body) as endpoint:
        withheld = _run_cli(
            scratch, _arguments(endpoint), **_SELF_TEST_CREDENTIALS
        )
    for what, run in (
        ("--show-identifiers", by_option),
        (SHOW_IDENTIFIERS_VARIABLE, by_variable),
        ("neither", withheld),
    ):
        _assert_equal(run.status, EXIT_OK, f"the status of the load with {what}")
    counts = ("removed=0 written=1", "removed=1 written=1")
    _assert_in(counts[0], by_option.stdout, "the summary line of the first load")
    for run in (by_variable, withheld):
        _assert_in(counts[1], run.stdout, "the summary line of a repeated load")
    _assert_equal(
        by_option.stdout.replace(counts[0], "<counts>"),
        by_variable.stdout.replace(counts[1], "<counts>"),
        "the summary line the variable wrote against the one the option wrote",
    )
    for fragment in ("1000301", DEFAULT_SOURCE_SYSTEM_KEY):
        for what, run in (
            ("--show-identifiers", by_option),
            (SHOW_IDENTIFIERS_VARIABLE, by_variable),
        ):
            _assert_in(fragment, run.stdout, f"the summary line with {what}")
    for what, run in (
        ("--show-identifiers", by_option),
        (SHOW_IDENTIFIERS_VARIABLE, by_variable),
    ):
        _assert_absent(
            "identifiers=redacted", run.stdout, f"the summary line with {what}"
        )
        _assert_in(
            build_object_uri(_SELF_TEST_BUCKET, _selftest_key()),
            run.stderr,
            f"the progress lines with {what}",
        )
    incidental = _incidental_text(scratch, database, body=body)
    _assert_identifiers_withheld(
        withheld.stdout, incidental, "the summary line with neither"
    )
    _assert_identifiers_withheld(
        withheld.stderr, incidental, "the progress lines with neither"
    )
    _assert_in(
        "identifiers=redacted", withheld.stdout, "the summary line with neither"
    )
    return (
        "the option and the variable wrote the same summary line and the same "
        "progress lines, and neither withheld nothing"
    )


def _case_endpoint_accepted() -> str:
    """Every loopback endpoint form the policy accepts is returned unchanged."""
    for value in _ACCEPTED_ENDPOINTS:
        _assert_equal(
            require_loopback_endpoint(value, "the self-test"),
            value,
            f"the accepted endpoint {value!r}",
        )
        observed, origin = resolve_endpoint_url(value)
        _assert_equal(observed, value, f"the endpoint resolved from {value!r}")
        _assert_equal(
            origin, "--endpoint-url", f"the origin of the endpoint {value!r}"
        )
    return f"{len(_ACCEPTED_ENDPOINTS)} loopback endpoint forms accepted"


def _case_endpoint_refused() -> str:
    """Every non-local endpoint form is refused, naming the element refused."""
    for value, element in _REFUSED_ENDPOINTS:
        _assert_raises(
            f"the endpoint {value!r}",
            ConfigurationError,
            element,
            lambda value=value: require_loopback_endpoint(value, "the self-test"),
        )
        _assert_raises(
            f"the endpoint setting {value!r}",
            ConfigurationError,
            element,
            lambda value=value: resolve_endpoint_url(value),
        )
    return f"{len(_REFUSED_ENDPOINTS)} endpoint forms refused by element"


def _case_endpoint_resolving_name_refused(scratch: _Scratch) -> str:
    """A name that resolves to loopback is still refused, and no request is signed."""
    import socket

    resolving = []
    for candidate in ("localhost.localdomain", "ip6-localhost", "localhost."):
        try:
            resolved = socket.getaddrinfo(candidate, None)
        except socket.gaierror:
            continue
        if any(entry[4][0] in {"127.0.0.1", "::1"} for entry in resolved):
            resolving.append(candidate)
    _assert(
        bool(resolving),
        "no name resolving to loopback is available to establish the policy",
    )
    for name in resolving:
        _assert_raises(
            f"the resolving name {name!r}",
            ConfigurationError,
            "host",
            lambda name=name: require_loopback_endpoint(
                f"http://{name}:5112", "the self-test"
            ),
        )
        _assert(
            not _is_loopback_host(name),
            f"the name {name!r} was accepted as a loopback literal",
        )
    run = _run_cli(
        scratch,
        ["--bucket", _SELF_TEST_BUCKET, "--region", _SELF_TEST_REGION],
        **{ENDPOINT_URL_VARIABLE: f"http://{resolving[0]}:5112"},
        **_SELF_TEST_CREDENTIALS,
    )
    _assert_equal(run.status, EXIT_CONFIGURATION_REJECTED, "the status of that run")
    _assert_in("host", _assert_one_diagnostic(run.stderr), "the diagnostic")
    _assert_equal(run.stdout, "", "stdout of a refused endpoint run")
    return f"{len(resolving)} resolving names refused before a client existed"


def _case_configured_endpoint_ignored(scratch: _Scratch) -> str:
    """An endpoint configured in the environment cannot redirect a request."""
    with _controlled_environment(
        scratch,
        AWS_ENDPOINT_URL="http://attacker.example.com:9999",
        AWS_ENDPOINT_URL_S3="http://attacker-s3.example.com:9999",
        AWS_DEFAULT_REGION=_SELF_TEST_REGION,
        **_SELF_TEST_CREDENTIALS,
    ):
        _assert(
            resolve_endpoint_url(None)[0] is None,
            "an AWS endpoint variable was read as this tool's endpoint setting",
        )
        session = build_session(_SELF_TEST_REGION)
        client = build_s3_client(session, None)
        observed = client.meta.endpoint_url
        _assert(
            "attacker" not in observed,
            f"the client addresses the configured endpoint {observed!r}",
        )
        local = build_s3_client(session, _ACCEPTED_ENDPOINTS[0])
        _assert_equal(
            local.meta.endpoint_url,
            _ACCEPTED_ENDPOINTS[0],
            "the endpoint of a client built for the accepted local endpoint",
        )
    return f"configured endpoints ignored, client addressed {observed}"


def _case_credentials_and_region_required(scratch: _Scratch) -> str:
    """A missing credential or region is named before any request is attempted."""
    with _controlled_environment(scratch, AWS_DEFAULT_REGION=_SELF_TEST_REGION):
        _assert_raises(
            "a session with no credentials",
            ConfigurationError,
            "no credentials are resolved",
            lambda: confirm_credentials(build_session(_SELF_TEST_REGION)),
        )
    with _controlled_environment(scratch, **_SELF_TEST_CREDENTIALS):
        _assert_raises(
            "a session with no region",
            ConfigurationError,
            "no region is resolved",
            lambda: resolve_session_region(build_session(None)),
        )
        _assert_equal(
            resolve_session_region(build_session(_SELF_TEST_REGION)),
            _SELF_TEST_REGION,
            "the region of a session pinned to one",
        )
    with _controlled_environment(
        scratch, AWS_REGION=_SELF_TEST_REGION, **_SELF_TEST_CREDENTIALS
    ):
        _assert_equal(
            resolve_region(None), _SELF_TEST_REGION, "the region read from AWS_REGION"
        )
    _assert_raises(
        "a region carrying whitespace",
        ConfigurationError,
        "whitespace",
        lambda: resolve_region("eu west 2"),
    )
    return "3 unresolved settings named and 2 resolved ones confirmed"


def _case_object_identity_recorded() -> str:
    """The head request records the entity tag, the byte count and the version."""
    body = _record_bytes()
    with _seeded_bucket(body) as raw:
        client = _RecordingClient(raw)
        identity = head_object_identity(client, _SELF_TEST_BUCKET, _selftest_key())
        _assert_equal(client.operations(), ("head_object",), "the operations called")
        _assert_equal(
            identity.content_length, len(body), "the recorded byte count"
        )
        _assert_equal(identity.etag, _single_part_etag(body), "the recorded entity tag")
        _assert_equal(identity.version_id, NOT_VERSIONED, "the recorded version")
    with _seeded_bucket(body, versioned=True) as raw:
        identity = head_object_identity(raw, _SELF_TEST_BUCKET, _selftest_key())
        _assert(
            identity.version_id != NOT_VERSIONED,
            "a versioned bucket reported no version to bind the download to",
        )
    _assert_equal(
        _reported_etag(_quoted_etag(body)),
        _single_part_etag(body),
        "the entity tag read from the quoted form a store reports",
    )
    absent = ({}, {"ETag": '""', "ContentLength": 1}, {"ETag": '"a" '})
    for response in absent:
        _assert_raises(
            f"a head response of {response!r}",
            AccessError,
            "landed object",
            lambda response=response: head_object_identity(
                _FixedResponseClient(response), _SELF_TEST_BUCKET, _selftest_key()
            ),
        )
    return f"identity recorded for both bucket kinds, {len(absent)} faults refused"


class _FixedResponseClient:
    """One client whose ``head_object`` answers with a fixed mapping.

    The mapping stands for a store that reported an identity this tool cannot
    bind a download to, which no real store returns and which must still be
    refused rather than assumed.
    """

    def __init__(self, response: Mapping[str, Any]) -> None:
        self._response = response

    def head_object(self, **_arguments: Any) -> Mapping[str, Any]:
        """Return the fixed response this client was built with."""
        return self._response


def _case_download_bound_to_identity() -> str:
    """The download names the recorded entity tag, and the version where one is kept."""
    body = _record_bytes()
    with _seeded_bucket(body) as raw:
        client = _RecordingClient(raw)
        identity = head_object_identity(client, _SELF_TEST_BUCKET, _selftest_key())
        downloaded = fetch_object_bytes(
            client, _SELF_TEST_BUCKET, _selftest_key(), identity
        )
        _assert_equal(
            client.operations(), ("head_object", "get_object"), "the operations called"
        )
        arguments = client.arguments("get_object")
        _assert_equal(arguments.get("IfMatch"), identity.etag, "the IfMatch condition")
        _assert(
            "VersionId" not in arguments,
            "an unversioned read named a version the store does not keep",
        )
        _assert_equal(downloaded.body, body, "the bytes downloaded")
        _assert_equal(
            downloaded.sha256, hashlib.sha256(body).hexdigest(), "the digest computed"
        )
        _assert_equal(downloaded.identity, identity, "the identity bound to")
    with _seeded_bucket(body, versioned=True) as raw:
        client = _RecordingClient(raw)
        identity = head_object_identity(client, _SELF_TEST_BUCKET, _selftest_key())
        fetch_object_bytes(client, _SELF_TEST_BUCKET, _selftest_key(), identity)
        arguments = client.arguments("get_object")
        _assert_equal(
            arguments.get("VersionId"), identity.version_id, "the version read"
        )
        _assert_equal(arguments.get("IfMatch"), identity.etag, "the IfMatch condition")
    return "the read named the recorded entity tag, and the version when kept"


def _case_replacement_refused() -> str:
    """An object replaced between the identity check and the download is refused."""
    body = _record_bytes()
    replacement = _record_bytes(policy_number="9999999")
    _assert(
        len(replacement) == len(body),
        "the replacement fixture differs in length, so length alone would catch it",
    )
    with _seeded_bucket(body) as raw:
        client = _ReplacingClient(raw, replacement)
        identity = head_object_identity(client, _SELF_TEST_BUCKET, _selftest_key())
        error = _assert_raises(
            "a read of an object replaced after the identity check",
            AccessError,
            "was replaced between the identity check and the download",
            lambda: fetch_object_bytes(
                client, _SELF_TEST_BUCKET, _selftest_key(), identity
            ),
        )
        _assert_absent("9999999", str(error), "the replacement diagnostic")
        _assert_equal(
            client.operations(),
            ("head_object", "put_object", "get_object"),
            "the operations called",
        )
    with _seeded_bucket(body, versioned=True) as raw:
        client = _ReplacingClient(raw, replacement)
        identity = head_object_identity(client, _SELF_TEST_BUCKET, _selftest_key())
        downloaded = fetch_object_bytes(
            client, _SELF_TEST_BUCKET, _selftest_key(), identity
        )
        _assert_equal(
            downloaded.body,
            body,
            "the bytes a version-pinned read returned after a replacement",
        )
    return "a replaced object was refused, and a pinned version still read as landed"


def _case_digest_and_length_confirmed() -> str:
    """Bytes that do not carry the recorded length or digest never reach the record."""
    _, Stubber, StreamingBody = _test_collaborators()
    body = _record_bytes()
    identity = _identity_of(body)
    faults = (
        (
            "a body of another length",
            _record_bytes(policy_number="1"),
            "the object changed between the identity check and the download",
        ),
        (
            "a body of the recorded length carrying other bytes",
            _record_bytes(policy_number="9999999"),
            "are not the bytes that were checked",
        ),
    )
    for what, served, fragment in faults:
        client = _stubbed_client()
        with Stubber(client) as stub:
            stub.add_response(
                "get_object",
                {
                    "Body": StreamingBody(io.BytesIO(served), len(served)),
                    "ETag": f'"{identity.etag}"',
                    "ContentLength": len(served),
                },
                {
                    "Bucket": _SELF_TEST_BUCKET,
                    "Key": _selftest_key(),
                    "IfMatch": identity.etag,
                },
            )
            _assert_raises(
                what,
                ObjectError,
                fragment,
                lambda client=client: fetch_object_bytes(
                    client, _SELF_TEST_BUCKET, _selftest_key(), identity
                ),
            )
    client = _stubbed_client()
    with Stubber(client) as stub:
        stub.add_response(
            "get_object",
            {
                "Body": StreamingBody(io.BytesIO(body), len(body)),
                "ETag": f'"{identity.etag}"',
                "ContentLength": len(body),
            },
            {
                "Bucket": _SELF_TEST_BUCKET,
                "Key": _selftest_key(),
                "IfMatch": identity.etag,
            },
        )
        downloaded = fetch_object_bytes(
            client, _SELF_TEST_BUCKET, _selftest_key(), identity
        )
    _assert_equal(downloaded.body, body, "the bytes of a matching object")
    multipart = ObjectIdentity(
        etag=f"{_single_part_etag(body)}-2",
        version_id=NOT_VERSIONED,
        content_length=len(body),
    )
    client = _stubbed_client()
    with Stubber(client) as stub:
        stub.add_response(
            "get_object",
            {
                "Body": StreamingBody(io.BytesIO(body), len(body)),
                "ETag": f'"{multipart.etag}"',
                "ContentLength": len(body),
            },
            {
                "Bucket": _SELF_TEST_BUCKET,
                "Key": _selftest_key(),
                "IfMatch": multipart.etag,
            },
        )
        downloaded = fetch_object_bytes(
            client, _SELF_TEST_BUCKET, _selftest_key(), multipart
        )
    _assert_equal(
        downloaded.identity.etag, multipart.etag, "the multipart tag bound to"
    )
    return f"{len(faults)} mismatches refused, matching and multipart objects read"


def _case_download_failures_reported() -> str:
    """Every download failure botocore reports becomes the diagnostic it deserves."""
    _, Stubber, StreamingBody = _test_collaborators()
    body = _record_bytes()
    identity = _identity_of(body)
    failures = (
        ("NoSuchKey", 404, AccessError, "no such object"),
        ("AccessDenied", 403, AccessError, "not permitted"),
        ("NoSuchBucket", 404, AccessError, "does not"),
        ("PreconditionFailed", 412, AccessError, "was replaced between"),
        ("InvalidAccessKeyId", 403, ConfigurationError, "rejected the resolved"),
        ("PermanentRedirect", 301, AccessError, "not in the region"),
        ("InternalError", 500, AccessError, "the endpoint answered"),
    )
    for code, status, expected, fragment in failures:
        client = _stubbed_client()
        with Stubber(client) as stub:
            stub.add_client_error(
                "get_object",
                service_error_code=code,
                http_status_code=status,
                expected_params={
                    "Bucket": _SELF_TEST_BUCKET,
                    "Key": _selftest_key(),
                    "IfMatch": identity.etag,
                },
            )
            error = _assert_raises(
                f"a download answered {code}",
                expected,
                fragment,
                lambda client=client: fetch_object_bytes(
                    client, _SELF_TEST_BUCKET, _selftest_key(), identity
                ),
            )
        _assert_equal(
            error.exit_status,
            EXIT_S3_UNAVAILABLE
            if expected is AccessError
            else EXIT_CONFIGURATION_REJECTED,
            f"the status of a {code} failure",
        )
    head_failures = (("NoSuchKey", 404), ("AccessDenied", 403))
    for code, status in head_failures:
        client = _stubbed_client()
        with Stubber(client) as stub:
            stub.add_client_error(
                "head_object",
                service_error_code=code,
                http_status_code=status,
                expected_params={"Bucket": _SELF_TEST_BUCKET, "Key": _selftest_key()},
            )
            _assert_raises(
                f"an identity check answered {code}",
                AccessError,
                "cannot read the identity",
                lambda client=client: head_object_identity(
                    client, _SELF_TEST_BUCKET, _selftest_key()
                ),
            )
    empty = b""
    client = _stubbed_client()
    with Stubber(client) as stub:
        stub.add_response(
            "get_object",
            {
                "Body": StreamingBody(io.BytesIO(empty), 0),
                "ETag": f'"{_single_part_etag(empty)}"',
                "ContentLength": 0,
            },
            {
                "Bucket": _SELF_TEST_BUCKET,
                "Key": _selftest_key(),
                "IfMatch": _single_part_etag(empty),
            },
        )
        _assert_raises(
            "an empty object",
            ObjectError,
            "is empty",
            lambda: fetch_object_bytes(
                client, _SELF_TEST_BUCKET, _selftest_key(), _identity_of(empty)
            ),
        )
    return (
        f"{len(failures)} download failures, {len(head_failures)} identity failures "
        "and an empty object reported"
    )


def _case_failure_mapping() -> str:
    """A credential, region or connection failure names the setting to supply."""
    mapping = (
        (NoCredentialsError(), ConfigurationError, "no credentials are resolved"),
        (
            PartialCredentialsError(provider="env", cred_var="AWS_SECRET_ACCESS_KEY"),
            ConfigurationError,
            "incomplete",
        ),
        (NoRegionError(), ConfigurationError, "no region is resolved"),
        (
            EndpointConnectionError(endpoint_url="http://127.0.0.1:5112"),
            AccessError,
            "refused the connection",
        ),
    )
    for error, expected, fragment in mapping:
        produced = _failure_for(error, _SELF_TEST_BUCKET, "read the landed object")
        _assert(
            isinstance(produced, expected),
            f"{_type_name(error)} became {_type_name(produced)}",
        )
        _assert_in(fragment, str(produced), f"the diagnostic for {_type_name(error)}")
        _assert_absent(
            "127.0.0.1", str(produced), f"the diagnostic for {_type_name(error)}"
        )
    return f"{len(mapping)} collaborator failures mapped without an endpoint value"


def _case_raw_relation_shape(scratch: _Scratch) -> str:
    """The relation the scripts define carries exactly the 17 landed columns."""
    database = scratch.database("shape.duckdb")
    columns = read_column_names(load_schema())
    with _captured_stderr():
        connection = open_database(database)
    try:
        with _captured_stderr():
            apply_sql_scripts(connection, resolve_ddl_paths(True))
        shape = _relation_shape(connection)
        _assert_equal(
            tuple(entry[1] for entry in shape),
            columns,
            "the column names and their order in the catalog",
        )
        _assert_equal(
            tuple(entry[0] for entry in shape),
            tuple(range(1, EXPECTED_COLUMN_COUNT + 1)),
            "the ordinal positions in the catalog",
        )
        for position, name, data_type, nullable in shape:
            _assert_equal(data_type, "VARCHAR", f"the type of column {position} {name}")
            _assert_equal(nullable, "YES", f"the nullability of column {name}")
        tables = connection.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = ? ORDER BY table_name",
            [RAW_SCHEMA_NAME],
        ).fetchall()
        _assert_equal(
            tuple(str(name) for (name,) in tables),
            (RAW_TABLE_NAME,),
            f"the relations in schema {RAW_SCHEMA_NAME}",
        )
        _assert_equal(_row_count(connection), 0, "the rows a fresh relation holds")
        with _captured_stderr():
            apply_sql_scripts(connection, resolve_ddl_paths(True))
        _assert_equal(
            _relation_shape(connection), shape, "the shape after a second application"
        )
    finally:
        connection.close()
    return f"{len(shape)} columns, all VARCHAR and nullable, in landing order"


def _case_load_one_row(scratch: _Scratch) -> str:
    """One landed object becomes exactly one row carrying the values as landed."""
    database = scratch.database("one-row.duckdb")
    columns = read_column_names(load_schema())
    body = _record_bytes()
    outcome = _load_into(scratch, database, body)
    _assert_equal(outcome.removed, 0, "the rows a first load removed")
    _assert_equal(outcome.written, EXPECTED_INSERTED_ROWS, "the rows it wrote")
    _assert_equal(
        outcome.key_values,
        (DEFAULT_SOURCE_SYSTEM_KEY, "1000301"),
        "the natural key it loaded",
    )
    _assert_equal(outcome.identity.content_length, len(body), "the byte count bound")
    _assert_equal(outcome.sha256, hashlib.sha256(body).hexdigest(), "the digest bound")
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(_row_count(connection), 1, "the rows the relation holds")
        rows = _rows_for_key(connection, columns, outcome.key_values)
        _assert_equal(len(rows), 1, "the rows carrying that natural key")
        expected = tuple(value for _, value in _MOTOR_RECORD_MEMBERS)
        _assert_equal(rows[0], expected, "the row as stored")
        nulls = sum(1 for value in rows[0] if value is None)
        _assert_equal(nulls, 4, "the null values of a motor row")
    finally:
        connection.close()
    return f"1 row written, {nulls} product premiums left null"


def _case_repeated_load_idempotent(scratch: _Scratch) -> str:
    """Loading the same object again leaves one row carrying the same values."""
    database = scratch.database("idempotent.duckdb")
    columns = read_column_names(load_schema())
    body = _record_bytes()
    first = _load_into(scratch, database, body)
    connection = duckdb.connect(str(database))
    try:
        before = _rows_for_key(connection, columns, first.key_values)
    finally:
        connection.close()
    second = _load_into(scratch, database, body)
    _assert_equal(second.removed, 1, "the rows the second load removed")
    _assert_equal(second.written, EXPECTED_INSERTED_ROWS, "the rows it wrote")
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(_row_count(connection), 1, "the rows after a repeated load")
        after = _rows_for_key(connection, columns, second.key_values)
        _assert_equal(after, before, "the row after a repeated load")
    finally:
        connection.close()
    third = _load_into(scratch, database, body)
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(_row_count(connection), 1, "the rows after a third load")
    finally:
        connection.close()
    return (
        f"3 loads of one object left 1 row, removing {second.removed} and writing "
        f"{third.written} each time after the first"
    )


def _case_second_key_coexists(scratch: _Scratch) -> str:
    """A second landed object adds its own row and leaves the first one alone."""
    database = scratch.database("two-rows.duckdb")
    columns = read_column_names(load_schema())
    motor = _load_into(scratch, database, _record_bytes())
    connection = duckdb.connect(str(database))
    try:
        motor_row = _rows_for_key(connection, columns, motor.key_values)
    finally:
        connection.close()
    commercial = _load_into(
        scratch, database, _record_bytes(_COMMERCIAL_RECORD_MEMBERS)
    )
    _assert_equal(commercial.removed, 0, "the rows the second object removed")
    _assert(
        commercial.key_values != motor.key_values,
        "the two fixtures carry the same natural key, so nothing distinguishes them",
    )
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(_row_count(connection), 2, "the rows two objects left")
        _assert_equal(
            _rows_for_key(connection, columns, motor.key_values),
            motor_row,
            "the first row after the second object was loaded",
        )
        commercial_row = _rows_for_key(connection, columns, commercial.key_values)
        _assert_equal(len(commercial_row), 1, "the rows of the second natural key")
        _assert_equal(
            commercial_row[0],
            tuple(value for _, value in _COMMERCIAL_RECORD_MEMBERS),
            "the second row as stored",
        )
        _assert_equal(
            commercial_row[0][columns.index("motor_premium_amount")],
            None,
            "the motor premium of a commercial row",
        )
        _assert_equal(
            motor_row[0][columns.index("fire_premium_amount")],
            None,
            "the fire premium of a motor row",
        )
    finally:
        connection.close()
    return "2 distinct natural keys coexist with the product-specific null pattern"


def _case_part_option_resolved() -> str:
    """The part element resolves, rebuilds its own key and refuses every other value.

    The key a run that names no part rebuilds is required to equal the key of the
    default part character for character, so a run that names no part reads the object
    modernization/landing/land_to_s3.py writes when it is given no part either. A
    ``--key`` naming another part of the same prefix is refused rather than loaded, and
    the diagnostic names the setting that selects it.
    """
    _assert_equal(resolve_part(None), DEFAULT_PART_NUMBER, "the part of no setting")
    _assert_equal(
        build_landing_key(
            DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
        ),
        build_landing_key(
            DEFAULT_SOURCE_SYSTEM_KEY,
            LANDING_ENTITY,
            _SELF_TEST_EXTRACT_DATE,
            DEFAULT_PART_NUMBER,
        ),
        "the key of a run naming no part",
    )
    for supplied, expected in (("0", 0), ("0000", 0), ("1", 1), ("0001", 1),
                              ("9999", MAX_PART_NUMBER)):
        _assert_equal(resolve_part(supplied), expected, f"the part from {supplied!r}")
    _assert_equal(object_name(0), OBJECT_NAME, "the object name of the default part")
    _assert_equal(object_name(1), "part-0001.json", "the object name of part 1")
    refused_settings = ("-1", "1.0", "00001", "10000", " 1", "", "one", "+1")
    for supplied in refused_settings:
        _assert_raises(
            f"the part setting {supplied!r}",
            ConfigurationError,
            "--part",
            lambda supplied=supplied: resolve_part(supplied),
        )
    for value in (-1, MAX_PART_NUMBER + 1, True, "0000", None):
        _assert_raises(
            f"the part number {value!r}",
            ConfigurationError,
            "",
            lambda value=value: build_landing_key(
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                value,
            ),
        )
    # Every part addresses its own key, and --key confirms the resolved settings
    # rather than selecting an object of its own.
    for part in (DEFAULT_PART_NUMBER, 1, MAX_PART_NUMBER):
        key = build_landing_key(
            DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE, part
        )
        _assert(
            key.endswith(f"{KEY_SEPARATOR}{object_name(part)}"),
            f"the key of part {part} is named {key.rsplit(KEY_SEPARATOR, 1)[-1]!r}",
        )
        _assert_equal(
            confirm_landing_key(
                key,
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                "--key",
                part,
            ),
            key,
            f"the confirmed key of part {part}",
        )
        _assert_equal(
            resolve_object_key(
                build_object_uri(_SELF_TEST_BUCKET, key),
                _SELF_TEST_BUCKET,
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                part,
            ),
            key,
            f"the key resolved from the URI of part {part}",
        )
    other_part = build_landing_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE, 1
    )
    _assert_raises(
        "a --key naming another part of the same prefix",
        ConfigurationError,
        "--part",
        lambda: resolve_object_key(
            other_part,
            _SELF_TEST_BUCKET,
            DEFAULT_SOURCE_SYSTEM_KEY,
            LANDING_ENTITY,
            _SELF_TEST_EXTRACT_DATE,
            DEFAULT_PART_NUMBER,
        ),
    )
    prefix = other_part.rsplit(KEY_SEPARATOR, 1)[0]
    for name, fragment in (
        ("part-0000.manifest.json", "not the name of a landed record"),
        ("part-000.json", "not the name of a landed record"),
        ("part-00001.json", "not the name of a landed record"),
        ("record.json", "not the name of a landed record"),
    ):
        _assert_raises(
            f"a --key named {name!r}",
            ConfigurationError,
            fragment,
            lambda name=name: confirm_landing_key(
                f"{prefix}{KEY_SEPARATOR}{name}",
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                "--key",
                DEFAULT_PART_NUMBER,
            ),
        )
    _assert_raises(
        "a --key naming another extract date",
        ConfigurationError,
        "extract_date",
        lambda: confirm_landing_key(
            build_landing_key(
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE + datetime.timedelta(days=1),
            ),
            DEFAULT_SOURCE_SYSTEM_KEY,
            LANDING_ENTITY,
            _SELF_TEST_EXTRACT_DATE,
            "--key",
        ),
    )
    return (
        f"{len(refused_settings)} part settings refused, every part addressing its "
        "own key and a key of another part refused"
    )


def _case_parts_replayed(scratch: _Scratch) -> str:
    """Two parts of one prefix are replayed out of object storage into two rows.

    One bucket is seeded with the two objects a two-sample run lands - the motor
    record at the default part and the commercial record at part 1 - and nothing else.
    Both are then loaded, in one database, from object storage alone: no landing runs
    between the two loads. The relation is required to hold both rows, each carrying the
    values of its own object, which is the replay the landing zone now supports.
    """
    database = scratch.database("parts-replayed.duckdb")
    columns = read_column_names(load_schema())
    bodies = {
        DEFAULT_PART_NUMBER: _record_bytes(),
        1: _record_bytes(_COMMERCIAL_RECORD_MEMBERS),
    }
    ddl_paths = resolve_ddl_paths(True)
    mock_aws, _, _ = _test_collaborators()
    outcomes: dict[int, LoadOutcome] = {}
    with mock_aws():
        client = _stubbed_client()
        client.create_bucket(
            Bucket=_SELF_TEST_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": _SELF_TEST_REGION},
        )
        for part, body in bodies.items():
            _put_landed_pair(
                client,
                _SELF_TEST_BUCKET,
                build_landing_key(
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                    part,
                ),
                body,
            )
        listing = client.list_objects_v2(Bucket=_SELF_TEST_BUCKET)
        # Two parts, each landed as its record and the COPY manifest naming it.
        _assert_equal(listing.get("KeyCount"), 4, "objects seeded under one prefix")
        with _controlled_environment(scratch, **_SELF_TEST_CREDENTIALS):
            for part in bodies:
                with _captured_stderr():
                    outcomes[part] = load_record(
                        _SELF_TEST_BUCKET,
                        build_landing_key(
                            DEFAULT_SOURCE_SYSTEM_KEY,
                            LANDING_ENTITY,
                            _SELF_TEST_EXTRACT_DATE,
                            part,
                        ),
                        DEFAULT_SOURCE_SYSTEM_KEY,
                        _SELF_TEST_EXTRACT_DATE,
                        database,
                        ddl_paths,
                        part=part,
                        region=_SELF_TEST_REGION,
                    )
    _assert_equal(outcomes[DEFAULT_PART_NUMBER].removed, 0, "rows the first load removed")
    _assert_equal(outcomes[1].removed, 0, "rows the second load removed")
    _assert_equal(outcomes[DEFAULT_PART_NUMBER].written, 1, "rows the first load wrote")
    _assert_equal(outcomes[1].written, 1, "rows the second load wrote")
    _assert(
        outcomes[DEFAULT_PART_NUMBER].key_values != outcomes[1].key_values,
        "both parts carry the same natural key, so nothing distinguishes them",
    )
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(_row_count(connection), 2, "the rows two replayed parts left")
        _assert_equal(
            _rows_for_key(connection, columns, outcomes[1].key_values)[0],
            tuple(value for _, value in _COMMERCIAL_RECORD_MEMBERS),
            "the row of part 1 as stored",
        )
        _assert_equal(
            _rows_for_key(connection, columns, outcomes[DEFAULT_PART_NUMBER].key_values)[0],
            tuple(value for _, value in _MOTOR_RECORD_MEMBERS),
            "the row of the default part as stored",
        )
    finally:
        connection.close()
    return "2 parts of one prefix replayed into 2 coexisting rows"


def _case_rollback_restores_state(scratch: _Scratch) -> str:
    """A failure between the removal and the write leaves the earlier state intact."""
    database = scratch.database("rollback.duckdb")
    columns = read_column_names(load_schema())
    loaded = _load_into(scratch, database, _record_bytes())
    values = tuple(value for _, value in _MOTOR_RECORD_MEMBERS)
    connection = duckdb.connect(str(database))
    try:
        before_shape = _relation_shape(connection)
        before_rows = _rows_for_key(connection, columns, loaded.key_values)
        before_count = _row_count(connection)
        _assert_equal(before_count, 1, "the rows before the failing write")
        with _captured_stderr():
            error = _assert_raises(
                "a write naming a column the relation does not carry",
                WarehouseError,
                "refused the load",
                lambda: upsert_record(
                    connection,
                    (*columns, "not_a_landed_column"),
                    (*values, "x"),
                    loaded.key_values,
                ),
            )
        _assert_equal(
            error.exit_status, EXIT_WAREHOUSE_UNAVAILABLE, "the status of that failure"
        )
        _assert_equal(
            _row_count(connection), before_count, "the rows after the rollback"
        )
        _assert_equal(
            _rows_for_key(connection, columns, loaded.key_values),
            before_rows,
            "the row after the rollback",
        )
        _assert_equal(
            _relation_shape(connection), before_shape, "the shape after the rollback"
        )
        _assert_raises(
            "a write carrying fewer values than columns",
            WarehouseError,
            "the two must agree",
            lambda: upsert_record(
                connection, columns, values[:-1], loaded.key_values
            ),
        )
        removed, written = upsert_record(
            connection, columns, values, loaded.key_values
        )
        _assert_equal((removed, written), (1, 1), "the counts of a recovered write")
        _assert_equal(_row_count(connection), 1, "the rows after the recovered write")
        _assert_equal(
            _rows_for_key(connection, columns, loaded.key_values),
            before_rows,
            "the row after the recovered write",
        )
    finally:
        connection.close()
    return "a failed write rolled back and the relation was writable afterwards"


def _case_row_counts_reported(scratch: _Scratch) -> str:
    """The counts a load reports are the counts the relation holds."""
    database = scratch.database("counts.duckdb")
    columns = read_column_names(load_schema())
    first = _load_into(scratch, database, _record_bytes())
    second = _load_into(scratch, database, _record_bytes())
    third = _load_into(scratch, database, _record_bytes(_COMMERCIAL_RECORD_MEMBERS))
    connection = duckdb.connect(str(database))
    try:
        total = _row_count(connection)
        _assert_equal(total, 2, "the rows three loads of two objects left")
        _assert_equal(
            sum(
                len(_rows_for_key(connection, columns, outcome.key_values))
                for outcome in (first, third)
            ),
            total,
            "the rows the two natural keys account for",
        )
        _assert_equal(
            (first.removed, second.removed, third.removed),
            (0, 1, 0),
            "the rows each load removed",
        )
        _assert_equal(
            (first.written, second.written, third.written),
            (1, 1, 1),
            "the rows each load wrote",
        )
    finally:
        connection.close()
    _assert_raises(
        "a row count the database did not report",
        WarehouseError,
        "no row count",
        lambda: _affected_rows([], "self-test action"),
    )
    _assert_raises(
        "a row count that is not a whole number",
        WarehouseError,
        "a whole number is required",
        lambda: _affected_rows([("many",)], "self-test action"),
    )
    return "reported counts matched the relation for 3 loads of 2 objects"


def _case_database_path_accepted(scratch: _Scratch) -> str:
    """The declared database and a name inside its own directory are accepted."""
    _assert_equal(
        resolve_database_path(None), DEFAULT_DATABASE, "the default database path"
    )
    declared = os.path.realpath(DEFAULT_DATABASE)
    _assert_equal(
        os.fspath(resolve_database_path(str(DEFAULT_DATABASE))),
        declared,
        "the declared database named explicitly",
    )
    beside = DATABASE_DIRECTORY / "selftest-beside.duckdb"
    _assert_equal(
        os.fspath(resolve_database_path(str(beside))),
        os.path.realpath(DATABASE_DIRECTORY) + os.sep + beside.name,
        "a new name inside the database directory",
    )
    accepted = scratch.database("accepted.duckdb")
    _assert_equal(
        os.fspath(resolve_database_path(str(accepted))),
        os.path.realpath(DATABASE_DIRECTORY) + os.sep + accepted.name,
        "a name of this run inside the database directory",
    )
    relative = os.path.relpath(accepted, Path.cwd())
    _assert_equal(
        os.fspath(resolve_database_path(relative)),
        os.path.realpath(DATABASE_DIRECTORY) + os.sep + accepted.name,
        "a relative path reaching the database directory",
    )
    _assert(
        not accepted.exists(),
        "an accepted path created a file before anything was written",
    )
    _assert(
        is_database_root(DATABASE_DIRECTORY)
        and is_database_root(os.path.realpath(DATABASE_DIRECTORY))
        and is_database_root(os.path.relpath(DATABASE_DIRECTORY, Path.cwd())),
        "the database directory is not recognised as the one root a database sits in",
    )
    _assert(
        not is_database_root(DATABASE_DIRECTORY / "sub")
        and not is_database_root(DATABASE_DIRECTORY.parent),
        "a sub-directory or the parent of the database directory is taken for the root",
    )
    for accepted_path in (
        resolve_database_path(None),
        resolve_database_path(str(beside)),
        resolve_database_path(relative),
    ):
        _assert(
            is_database_root(accepted_path.parent),
            f"the accepted path {accepted_path} has a parent open_database refuses",
        )
    return (
        "4 accepted database paths resolved inside the database directory, each with a "
        "parent the opener accepts"
    )


def _case_database_path_refused(scratch: _Scratch) -> str:
    """Every path that is not directly inside the database directory is refused."""
    authored = _THIS_DIR / "load_local.py"
    before = authored.read_bytes()
    refused = (
        ("this module itself", str(authored)),
        ("an authored SQL script", str(DDL_DIRECTORY / "01_schemas.sql")),
        ("the landing schema", str(DEFAULT_SCHEMA)),
        (
            "a read-only source file",
            str(_REPOSITORY_DIR / "base" / "src" / "lgapol01.cbl"),
        ),
        ("a new file beside this module", str(_THIS_DIR / "new.duckdb")),
        ("the repository root itself", str(_REPOSITORY_DIR / "in-tree.duckdb")),
        ("a path outside the repository", str(scratch.absent("outside.duckdb"))),
    )
    for what, value in refused:
        error = _assert_raises(
            what,
            ConfigurationError,
            "outside",
            lambda value=value: resolve_database_path(value),
        )
        _assert_equal(
            error.exit_status,
            EXIT_CONFIGURATION_REJECTED,
            f"the status refusing {what}",
        )
    _assert_equal(
        authored.read_bytes(), before, "the bytes of this module after the refusals"
    )
    nested = (
        (
            "a name in a sub-directory of the database directory",
            DATABASE_DIRECTORY / "sub" / "main.duckdb",
        ),
        (
            "a name two levels below the database directory",
            DATABASE_DIRECTORY / "sub" / "deeper" / "main.duckdb",
        ),
        (
            "a name in a sub-directory reached by a relative path",
            Path(os.path.relpath(DATABASE_DIRECTORY, Path.cwd())) / "sub" / "x.duckdb",
        ),
    )
    for what, value in nested:
        error = _assert_raises(
            what,
            ConfigurationError,
            "directly inside",
            lambda value=value: resolve_database_path(str(value)),
        )
        _assert_equal(
            error.exit_status,
            EXIT_CONFIGURATION_REJECTED,
            f"the status refusing {what}",
        )
        for named in (
            os.path.realpath(DATABASE_DIRECTORY),
            os.fspath(DEFAULT_DATABASE),
        ):
            _assert(
                named in str(error),
                f"{what} was refused with {str(error)!r}, naming no {named!r}",
            )
    _assert(
        not (DATABASE_DIRECTORY / "sub").exists(),
        "a refused sub-directory path created a directory in the database directory",
    )
    for name in RESERVED_DATABASE_NAMES:
        _assert_raises(
            f"the authored file {name!r} of the database directory",
            ConfigurationError,
            "authored file",
            lambda name=name: resolve_database_path(str(DATABASE_DIRECTORY / name)),
        )
    alias = scratch.absent("alias-to-authored")
    alias.symlink_to(authored)
    _assert_raises(
        "a symbolic link reaching an authored file",
        ConfigurationError,
        "symbolic link",
        lambda: resolve_database_path(str(alias)),
    )
    directory_alias = scratch.absent("alias-to-landing")
    directory_alias.symlink_to(_THIS_DIR)
    _assert_raises(
        "a symbolic link reaching an authored directory",
        ConfigurationError,
        "outside",
        lambda: resolve_database_path(str(directory_alias / "aliased.duckdb")),
    )
    cwd_alias = f"/proc/self/cwd/{os.path.relpath(authored, Path.cwd())}"
    _assert_raises(
        "a /proc/self/cwd alias reaching an authored file",
        ConfigurationError,
        "outside",
        lambda: resolve_database_path(cwd_alias),
    )
    _assert_raises(
        "an in-memory database",
        ConfigurationError,
        "in-memory",
        lambda: resolve_database_path(":memory:"),
    )
    _assert_raises(
        "an empty database path",
        ConfigurationError,
        "is empty",
        lambda: resolve_database_path("   "),
    )
    _assert_equal(
        authored.read_bytes(), before, "the bytes of this module after every refusal"
    )
    return (
        f"{len(refused) + len(nested) + len(RESERVED_DATABASE_NAMES) + 5} paths, "
        "authored names and aliases refused with status "
        f"{EXIT_CONFIGURATION_REJECTED}, this module untouched"
    )


def _case_database_path_below_root_refused(scratch: _Scratch) -> str:
    """A path in a directory below the database directory is a rejected setting.

    The refusal carries ``EXIT_CONFIGURATION_REJECTED``, names the setting the value
    came from, and reaches the caller before the object is read: a command line
    naming such a path writes no progress line about the bucket, the download or the
    database, and creates no file at the path it named.
    """
    below = (
        (
            "an existing directory below the database directory",
            DATABASE_DIRECTORY / "artifacts",
        ),
        (
            "a directory below it that does not exist",
            DATABASE_DIRECTORY / "no-such-directory",
        ),
        (
            "a directory two levels below it",
            DATABASE_DIRECTORY / "artifacts" / "deeper",
        ),
    )
    for what, directory in below:
        candidate = directory / "selftest-below-root.duckdb"
        error = _assert_raises(
            what,
            ConfigurationError,
            "directly inside",
            lambda candidate=candidate: resolve_database_path(str(candidate)),
        )
        _assert_equal(
            error.exit_status,
            EXIT_CONFIGURATION_REJECTED,
            f"the status of {what} refused",
        )
        _assert_in("--database", str(error), "the diagnostic")
        _assert(
            not candidate.exists(),
            f"the refused path was created: {candidate}",
        )
    named = DATABASE_DIRECTORY / "artifacts" / "selftest-below-root.duckdb"
    for variable in DATABASE_VARIABLES:
        with _controlled_environment(scratch, **{variable: str(named)}):
            error = _assert_raises(
                f"a path below the database directory from {variable}",
                ConfigurationError,
                "directly inside",
                lambda: resolve_database_path(None),
            )
        _assert_in(variable, str(error), "the diagnostic")
    with _served_bucket(_record_bytes()) as endpoint:
        run = _run_cli(
            scratch,
            [
                "--bucket",
                _SELF_TEST_BUCKET,
                "--region",
                _SELF_TEST_REGION,
                "--endpoint-url",
                endpoint,
                "--extract-date",
                _SELF_TEST_EXTRACT_DATE.isoformat(),
                "--database",
                str(named),
            ],
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(
        run.status,
        EXIT_CONFIGURATION_REJECTED,
        "the status of a command line naming a path below the database directory",
    )
    _assert_equal(run.stdout, "", "stdout of that command line")
    line = _assert_one_diagnostic(run.stderr)
    _assert_in("directly inside", line, "the diagnostic")
    _assert_in("--database", line, "the diagnostic")
    for absent in ("reading bucket", "bound the download", "opened database"):
        _assert_absent(absent, run.stderr, "the stderr of that command line")
    _assert(not named.exists(), f"the refused path was created: {named}")
    return (
        f"{len(below)} paths below the database directory and "
        f"{len(DATABASE_VARIABLES)} settings carrying one refused as settings, "
        "before any request"
    )


def _case_self_test_server_silent() -> str:
    """The server a case starts logs no request line, and leaves its logger as found.

    The request logger is collected rather than printed for the length of this case,
    so the negative control - the same request with the logger no longer silenced,
    which does record a line - adds nothing to the output of a self-test run either.
    """
    request_log = logging.getLogger(_REQUEST_LOGGER_NAME)
    found = (request_log.disabled, request_log.level)
    handlers = request_log.handlers[:]
    propagate = request_log.propagate
    collector = _RecordingHandler()
    request_log.handlers = [collector]
    request_log.propagate = False
    body = _record_bytes()
    try:
        with _served_bucket(body) as endpoint:
            _assert(
                request_log.disabled,
                "the request logger is not silenced while the server runs",
            )
            _assert_equal(
                len(_read_served_object(endpoint)),
                len(body),
                "the bytes the served object carries",
            )
            _assert_equal(
                collector.messages(), (), "the records a silenced request log emits"
            )
            request_log.disabled = False
            request_log.setLevel(logging.INFO)
            try:
                _read_served_object(endpoint)
            finally:
                request_log.setLevel(logging.CRITICAL)
                request_log.disabled = True
            _assert(
                any("GET" in message for message in collector.messages()),
                "the request log records no request while it is not silenced: "
                f"{collector.messages()}",
            )
    finally:
        request_log.handlers = handlers
        request_log.propagate = propagate
    _assert_equal(
        (request_log.disabled, request_log.level),
        found,
        "the request logger after the server stopped",
    )
    return (
        "0 request lines while the server ran, "
        f"{len(collector.records)} once the log was not silenced, logger restored"
    )


def _case_environment_guard(scratch: _Scratch) -> str:
    """Confirm the environment check accepts this run and refuses the others.

    The interpreter running the matrix carries the pinned series and the pinned version
    of every distribution named, so the unpatched check returns without writing. Each
    refusal is then observed with the pinned values replaced for the duration of one
    call: another series, a distribution that is not installed and a distribution at
    another version each end the run with ``EXIT_ENVIRONMENT_REJECTED`` and one line
    naming what was found, the pin and the interpreter to run this tool through.
    """
    _assert_equal(
        confirm_pinned_environment(), None, "the check of a pinned environment"
    )
    refused: list[str] = []
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
            (("duckdb", "0.0.1"),),
            "pins duckdb 0.0.1; run this tool through",
        ),
    ):
        original_series = globals()["PINNED_PYTHON_SERIES"]
        original_distributions = globals()["PINNED_DISTRIBUTIONS"]
        globals()["PINNED_PYTHON_SERIES"] = series
        globals()["PINNED_DISTRIBUTIONS"] = distributions
        status: Any = None
        with _captured_stderr() as captured:
            try:
                confirm_pinned_environment()
            except SystemExit as request:
                status = request.code
            finally:
                globals()["PINNED_PYTHON_SERIES"] = original_series
                globals()["PINNED_DISTRIBUTIONS"] = original_distributions
        _assert_equal(status, EXIT_ENVIRONMENT_REJECTED, f"the status of {what}")
        lines = [line for line in captured.getvalue().splitlines() if line]
        _assert_equal(len(lines), 1, f"the lines reported for {what}")
        _assert_in(expected, lines[0], f"the line reported for {what}")
        _assert(
            lines[0].startswith(f"{_PROGRAM}: "),
            f"the line reported for {what} names this tool",
        )
        _assert_equal(_one_line(lines[0]), lines[0], f"that line for {what}")
        refused.append(what)
    return (
        f"the pinned environment accepted, {len(refused)} environments refused with "
        f"status {EXIT_ENVIRONMENT_REJECTED}"
    )


def _case_interrupt_reported(scratch: _Scratch) -> str:
    """An interrupt is one line and status 130, from the report and from a run.

    The line is the one the reporting installed above the third-party imports
    writes, which is the line a run interrupted anywhere else writes as well: the
    command-line case reaches it through a resolution step that is interrupted.
    """
    with _captured_stderr() as captured:
        _report_interrupt()
    lines = [line for line in captured.getvalue().splitlines() if line]
    _assert_equal(lines, [INTERRUPTED_MESSAGE], "the lines an interrupt reports")
    _assert_equal(
        INTERRUPTED_MESSAGE,
        f"{_PROGRAM}: interrupted before completion",
        "the line an interrupt reports",
    )
    _assert_equal(
        _one_line(INTERRUPTED_MESSAGE), INTERRUPTED_MESSAGE, "that line as one line"
    )
    _assert_equal(EXIT_INTERRUPTED, 130, "the status an interrupt returns")
    for shape in _INTERRUPT_SHAPES:
        _assert(
            _interrupted(shape(INTERRUPTED_STATEMENT_TEXT)),
            f"an interrupted statement reported as {shape.__name__} is not "
            "recognised as an interrupt",
        )
    for other in (
        duckdb.Error("refused"),
        OSError("refused"),
        ValueError("refused"),
        RuntimeError("refused"),
    ):
        _assert(
            not _interrupted(other),
            f"{_type_name(other)} is recognised as an interrupt",
        )

    def _interrupt(_supplied: str | None) -> str:
        """Interrupt the run at the first setting it resolves."""
        raise KeyboardInterrupt

    original = globals()["resolve_bucket"]
    globals()["resolve_bucket"] = _interrupt
    try:
        run = _run_cli(scratch, ["--bucket", _SELF_TEST_BUCKET])
    finally:
        globals()["resolve_bucket"] = original
    _assert_equal(run.status, EXIT_INTERRUPTED, "the status of an interrupted run")
    _assert_equal(run.stdout, "", "stdout of an interrupted run")
    _assert_equal(
        [line for line in run.stderr.splitlines() if line],
        [INTERRUPTED_MESSAGE],
        "the stderr of an interrupted run",
    )
    return f"{INTERRUPTED_MESSAGE!r} and status {EXIT_INTERRUPTED}"


def _case_interrupt_in_transaction(scratch: _Scratch) -> str:
    """A statement interrupted mid-transaction is an interrupt, not a refusal.

    Both statement paths of the transaction are covered, each in both shapes DuckDB
    reports an interrupted statement as: a bootstrap script statement and the write
    itself, reported as the driver's own interrupt error and as the RuntimeError it
    raises for the interrupt of this process that it consumed. Each rolls the
    transaction back, leaves the rows the database held, and reports the interrupt
    rather than a database refusal.
    """
    database = scratch.database("interrupted.duckdb")
    columns = read_column_names(load_schema())
    loaded = _load_into(scratch, database, _record_bytes())
    values = tuple(value for _, value in _MOTOR_RECORD_MEMBERS)
    connection = duckdb.connect(str(database))
    try:
        before_count = _row_count(connection)
        before_rows = _rows_for_key(connection, columns, loaded.key_values)
        _assert_equal(before_count, 1, "the rows before the interrupted writes")
        interrupted = 0
        for step, fragment, ddl_paths in (
            ("the write itself", "INSERT INTO", ()),
            ("a bootstrap statement", "CREATE TABLE", resolve_ddl_paths(True)),
        ):
            for shape in _INTERRUPT_SHAPES:
                what = f"{step} reported as {shape.__name__}"
                interrupting = _InterruptingConnection(connection, fragment, shape)
                with _captured_stderr() as captured:
                    _assert_raises(
                        f"{what} interrupted",
                        KeyboardInterrupt,
                        "",
                        lambda interrupting=interrupting, ddl_paths=ddl_paths: (
                            upsert_record(
                                interrupting,
                                columns,
                                values,
                                loaded.key_values,
                                ddl_paths,
                            )
                        ),
                    )
                _assert_equal(
                    len(interrupting.interrupted),
                    1,
                    f"the statements {what} interrupted",
                )
                _assert_absent(
                    "refused the load", captured.getvalue(), f"the output of {what}"
                )
                _assert_absent(
                    "refused statement", captured.getvalue(), f"the output of {what}"
                )
                _assert_equal(
                    _row_count(connection), before_count, f"the rows after {what}"
                )
                _assert_equal(
                    _rows_for_key(connection, columns, loaded.key_values),
                    before_rows,
                    f"the row after {what}",
                )
                interrupted += 1
    finally:
        connection.close()
    return (
        f"{interrupted} interrupted statements reported as interrupts, no row written"
    )


def _case_sql_split_matrix(scratch: _Scratch) -> str:
    """Statement boundaries are read outside literals, identifiers and comments."""
    checks = (
        ("BEGIN;\nCOMMIT;\n", 2),
        ("SELECT ';' AS semicolon_in_a_literal;", 1),
        ("-- a comment; with a semicolon\nSELECT 1;", 1),
        ("/* a; /* nested */ comment; */ SELECT 1;", 1),
        ("SELECT 1", 1),
        ("-- only a comment\n", 0),
        ('SELECT "quoted;identifier";', 1),
        ("SELECT 'it''s here; still one';", 1),
        ("BEGIN;\n\n;\nCOMMIT;\n", 2),
        ("SELECT $tag$a; b$tag$;", 1),
    )
    for text, expected in checks:
        observed = split_sql_statements(text, DEFAULT_SCHEMA)
        _assert_equal(len(observed), expected, f"statements of {text!r}")
    _assert_equal(
        split_sql_statements("SELECT 1;\n  SELECT 2\n", DEFAULT_SCHEMA),
        ("SELECT 1", "SELECT 2"),
        "statements returned as written",
    )
    for text, construct in (
        ("SELECT 'unterminated", "quoted literal"),
        ('SELECT "unterminated', "quoted identifier"),
        ("/* unterminated", "block comment"),
        ("SELECT $tag$unterminated", "dollar-quoted literal"),
    ):
        _assert_raises(
            f"the text {text!r}",
            ConfigurationError,
            construct,
            lambda text=text: split_sql_statements(text, DEFAULT_SCHEMA),
        )
    file_faults = (
        ("a missing script", scratch.absent("no-such.sql"), "cannot be read"),
        ("an empty script", scratch.write("empty.sql", ""), "is empty"),
        (
            "a script carrying only comments",
            scratch.write("comments.sql", "-- nothing to run\n"),
            "carries no statement",
        ),
    )
    for what, path, fragment in file_faults:
        _assert_raises(
            what,
            ConfigurationError,
            fragment,
            lambda path=path: read_sql_statements(path),
        )
    refused = scratch.write("refused.sql", "CREATE SCHEMA raw;\nNOT SQL AT ALL;\n")
    database = scratch.database("sql-failure.duckdb")
    with _captured_stderr():
        connection = open_database(database)
    try:
        with _captured_stderr():
            error = _assert_raises(
                "a script the database refuses",
                WarehouseError,
                "refused statement 2 of 2",
                lambda: apply_sql_script(connection, refused),
            )
        _assert_in("NOT SQL AT ALL", str(error), "the diagnostic")
        _assert_in(refused.name, str(error), "the diagnostic")
    finally:
        connection.close()
    return (
        f"{len(checks)} split cases, 4 unterminated constructs and "
        f"{len(file_faults)} file faults"
    )


def _case_identifiers_redacted(scratch: _Scratch) -> str:
    """No business identifier and no object URI reaches the output by default."""
    database = scratch.database("redaction.duckdb")
    body = _record_bytes()
    ddl_paths = resolve_ddl_paths(True)
    with _seeded_bucket(body):
        with _controlled_environment(scratch, **_SELF_TEST_CREDENTIALS):
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                outcome = load_record(
                    _SELF_TEST_BUCKET,
                    _selftest_key(),
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    _SELF_TEST_EXTRACT_DATE,
                    database,
                    ddl_paths,
                    region=_SELF_TEST_REGION,
                )
    default_stderr = errors.getvalue()
    default_stdout = _report(
        qualified_relation_name(),
        outcome.key_values,
        outcome.removed,
        outcome.written,
        outcome.sha256,
    )
    incidental = _incidental_text(scratch, database, body=body)
    _assert_identifiers_withheld(
        default_stdout, incidental, "the default summary line"
    )
    _assert_absent(outcome.uri, default_stderr, "the default progress lines")
    _assert_identifiers_withheld(
        default_stderr, incidental, "the default progress lines"
    )
    _assert_in(REDACTED_TEXT, default_stderr, "the default progress lines")
    _assert_in("identifiers=redacted", default_stdout, "the default summary line")
    _assert_in(outcome.sha256, default_stdout, "the default summary line")
    with _seeded_bucket(body):
        with _controlled_environment(scratch, **_SELF_TEST_CREDENTIALS):
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                shown = load_record(
                    _SELF_TEST_BUCKET,
                    _selftest_key(),
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    _SELF_TEST_EXTRACT_DATE,
                    database,
                    ddl_paths,
                    region=_SELF_TEST_REGION,
                    show_identifiers=True,
                )
    shown_stderr = errors.getvalue()
    shown_stdout = _report(
        qualified_relation_name(),
        shown.key_values,
        shown.removed,
        shown.written,
        shown.sha256,
        show_identifiers=True,
    )
    _assert_in("1000301", shown_stdout, "the summary line under --show-identifiers")
    _assert_in(
        DEFAULT_SOURCE_SYSTEM_KEY,
        shown_stdout,
        "the summary line under --show-identifiers",
    )
    _assert_in(shown.uri, shown_stderr, "the progress lines under --show-identifiers")
    return (
        f"{len(_REDACTED_FRAGMENTS)} identifiers withheld by default and carried "
        "under --show-identifiers"
    )


def _case_cli_loads_and_redacts(scratch: _Scratch) -> str:
    """The command line loads one object, redacting identifiers unless asked."""
    database = scratch.database("cli.duckdb")
    body = _record_bytes()
    def _arguments(endpoint: str, *extra: str) -> list[str]:
        return [
            "--bucket",
            _SELF_TEST_BUCKET,
            "--region",
            _SELF_TEST_REGION,
            "--endpoint-url",
            endpoint,
            "--extract-date",
            _SELF_TEST_EXTRACT_DATE.isoformat(),
            "--database",
            str(database),
            *extra,
        ]

    with _served_bucket(body) as endpoint:
        run = _run_cli(scratch, _arguments(endpoint), **_SELF_TEST_CREDENTIALS)
    _assert_equal(run.status, EXIT_OK, "the status of a command line load")
    lines = [line for line in run.stdout.splitlines() if line]
    _assert_equal(len(lines), 1, f"the stdout lines of a load: {run.stdout!r}")
    _assert_in(qualified_relation_name(), lines[0], "the summary line")
    _assert_in("removed=0 written=1", lines[0], "the summary line")
    incidental = _incidental_text(scratch, database, endpoint=endpoint, body=body)
    _assert_identifiers_withheld(run.stdout, incidental, "the summary line")
    _assert_identifiers_withheld(run.stderr, incidental, "the progress lines")
    with _served_bucket(body) as endpoint:
        repeat = _run_cli(
            scratch,
            _arguments(endpoint, "--show-identifiers"),
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(repeat.status, EXIT_OK, "the status of a repeated load")
    _assert_in("removed=1 written=1", repeat.stdout, "the repeated summary line")
    _assert_in("1000301", repeat.stdout, "the summary line under --show-identifiers")
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(_row_count(connection), 1, "the rows two command lines left")
    finally:
        connection.close()
    with _served_bucket(body) as endpoint:
        by_uri = _run_cli(
            scratch,
            [
                "--bucket",
                _SELF_TEST_BUCKET,
                "--key",
                build_object_uri(_SELF_TEST_BUCKET, _selftest_key()),
                "--region",
                _SELF_TEST_REGION,
                "--endpoint-url",
                endpoint,
                "--extract-date",
                _SELF_TEST_EXTRACT_DATE.isoformat(),
                "--database",
                str(database),
                "--no-ddl",
            ],
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(by_uri.status, EXIT_OK, "the status of a load naming the URI")
    # A part the bucket does not carry is an absent object, not a rejected setting:
    # the key is built from --part and the download is what does not answer.
    with _served_bucket(body) as endpoint:
        absent_part = _run_cli(
            scratch,
            _arguments(endpoint, "--part", "1", "--no-ddl"),
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(
        absent_part.status,
        EXIT_S3_UNAVAILABLE,
        "the status of a load naming a part the bucket does not carry",
    )
    _assert_in(
        "part-0001.json",
        _assert_one_diagnostic(absent_part.stderr),
        "the diagnostic naming the part that was addressed",
    )
    refused_part = _run_cli(
        scratch, _arguments("http://127.0.0.1:5112", "--part", "10000")
    )
    _assert_equal(
        refused_part.status,
        EXIT_CONFIGURATION_REJECTED,
        "the status of a load naming a part outside the accepted range",
    )
    _assert_in(
        "--part",
        _assert_one_diagnostic(refused_part.stderr),
        "the diagnostic naming the part setting",
    )
    connection = duckdb.connect(str(database))
    try:
        _assert_equal(
            _row_count(connection), 1, "the rows after the two refused runs"
        )
    finally:
        connection.close()
    return (
        "2 command line loads left 1 row, the URI form named the same object, and a "
        "part the bucket does not carry and a part outside the range were refused"
    )


def _case_leaked_identifier_still_caught(scratch: _Scratch) -> str:
    """The redaction check passes a run's own text and fails on a carried identifier.

    The database name and the endpoint port this case supplies carry the redacted
    fragments themselves, and the progress and summary forms built from them are
    required to pass the check, which is what makes the check independent of the
    temporary directory name and the port a run is given. The same lines carrying
    one fragment in a value position are then required to fail it, one fragment at
    a time, as is the summary line ``--show-identifiers`` prints.
    """
    database = scratch.database("42-1001-BRMOT001-1000301.duckdb")
    endpoint = f"http://{_LOOPBACK_ADDRESS}:42101"
    body = _record_bytes()
    digest = hashlib.sha256(body).hexdigest()
    incidental = _incidental_text(scratch, database, endpoint=endpoint, body=body)
    key_values = (DEFAULT_SOURCE_SYSTEM_KEY, "1000301")
    previously_shown = show_identifiers_enabled()
    set_show_identifiers(False)
    try:
        redacted_summary = _report(
            qualified_relation_name(), key_values, 0, 1, digest
        )
    finally:
        set_show_identifiers(previously_shown)
    own_text = "\n".join(
        (
            (
                f"{_PROGRAM}: reading bucket {_shown(_SELF_TEST_BUCKET)} in region "
                f"{_shown(_SELF_TEST_REGION)} through {_shown(endpoint)}"
            ),
            (
                f"{_PROGRAM}: read {len(body)} bytes with sha256 {digest} and etag "
                f"{_single_part_etag(body)} for "
                f"{_SELF_TEST_EXTRACT_DATE.isoformat()}"
            ),
            f"{_PROGRAM}: opened database {_path_shown(database)}",
            f"{_PROGRAM}: the private directory is {_path_shown(scratch.path)}",
            redacted_summary,
        )
    )
    _assert_identifiers_withheld(
        own_text, incidental, "the lines naming this run's own text"
    )
    for fragment in _REDACTED_FRAGMENTS:
        carried = f"{own_text}\n{_PROGRAM}: carried the value {_shown(fragment)}"
        _assert_raises(
            f"a run carrying {fragment!r} in a value position",
            _SelfTestFailure,
            fragment,
            lambda carried=carried: _assert_identifiers_withheld(
                carried, incidental, "the progress lines"
            ),
        )
    disclosed = _report(
        qualified_relation_name(), key_values, 0, 1, digest, show_identifiers=True
    )
    _assert_raises(
        "a summary line naming its natural key",
        _SelfTestFailure,
        "1000301",
        lambda: _assert_identifiers_withheld(
            disclosed, incidental, "the summary line"
        ),
    )
    return (
        f"{len(_REDACTED_FRAGMENTS)} identifiers caught in a value position while "
        f"{len(incidental)} texts of this run's own carried every fragment"
    )


def _case_exit_codes(scratch: _Scratch) -> str:
    """Every documented exit status is reachable from the command line."""
    body = _record_bytes()
    database = scratch.database("statuses.duckdb")
    reached: dict[int, str] = {}
    with _served_bucket(body) as endpoint:
        run = _run_cli(
            scratch,
            [
                "--bucket",
                _SELF_TEST_BUCKET,
                "--region",
                _SELF_TEST_REGION,
                "--endpoint-url",
                endpoint,
                "--extract-date",
                _SELF_TEST_EXTRACT_DATE.isoformat(),
                "--database",
                str(database),
            ],
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(run.status, EXIT_OK, "the status of a successful load")
    reached[EXIT_OK] = "a load"
    with _served_bucket(_record_text(policy_type="X").encode("utf-8")) as endpoint:
        run = _run_cli(
            scratch,
            [
                "--bucket",
                _SELF_TEST_BUCKET,
                "--region",
                _SELF_TEST_REGION,
                "--endpoint-url",
                endpoint,
                "--extract-date",
                _SELF_TEST_EXTRACT_DATE.isoformat(),
                "--database",
                str(scratch.database("rejected.duckdb")),
            ],
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(run.status, EXIT_OBJECT_REJECTED, "the status of a rejected object")
    _assert_in("landing schema", _assert_one_diagnostic(run.stderr), "the diagnostic")
    reached[EXIT_OBJECT_REJECTED] = "an object breaching the contract"
    with _served_bucket() as endpoint:
        run = _run_cli(
            scratch,
            ["--region", _SELF_TEST_REGION, "--endpoint-url", endpoint],
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(
        run.status, EXIT_CONFIGURATION_REJECTED, "the status of a missing bucket"
    )
    _assert_in(BUCKET_VARIABLE, _assert_one_diagnostic(run.stderr), "the diagnostic")
    reached[EXIT_CONFIGURATION_REJECTED] = "a missing setting"
    run = _run_cli(scratch, ["--not-an-option"])
    _assert_equal(
        run.status, EXIT_CONFIGURATION_REJECTED, "the status of a rejected option"
    )
    _assert_in(
        "command line rejected", _assert_one_diagnostic(run.stderr), "the diagnostic"
    )
    with _served_bucket() as endpoint:
        run = _run_cli(
            scratch,
            [
                "--bucket",
                _ABSENT_BUCKET,
                "--region",
                _SELF_TEST_REGION,
                "--endpoint-url",
                endpoint,
                "--database",
                str(scratch.database("absent.duckdb")),
            ],
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(run.status, EXIT_S3_UNAVAILABLE, "the status of an absent bucket")
    reached[EXIT_S3_UNAVAILABLE] = "a bucket that does not answer"
    occupied = scratch.database("not-a-database.duckdb")
    occupied.write_bytes(b"NOT A DUCKDB DATABASE\n")
    with _served_bucket(body) as endpoint:
        run = _run_cli(
            scratch,
            [
                "--bucket",
                _SELF_TEST_BUCKET,
                "--region",
                _SELF_TEST_REGION,
                "--endpoint-url",
                endpoint,
                "--extract-date",
                _SELF_TEST_EXTRACT_DATE.isoformat(),
                "--database",
                str(occupied),
            ],
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(
        run.status, EXIT_WAREHOUSE_UNAVAILABLE, "the status of a database that is one"
    )
    reached[EXIT_WAREHOUSE_UNAVAILABLE] = "a database the file does not carry"
    _assert_equal(
        EXIT_SELF_TEST_FAILED,
        _self_test_status([_CaseResult("failing", False, "observed")]),
        "the status of a failed self-test case",
    )
    reached[EXIT_SELF_TEST_FAILED] = "a failed self-test case"
    _assert_equal(
        _self_test_status([_CaseResult("passing", True, "observed")]),
        EXIT_OK,
        "the status of a passing self-test run",
    )
    return "statuses reachable: " + ", ".join(
        str(status) for status in sorted(reached)
    )


def _case_scratch_removed(scratch: _Scratch) -> str:
    """The private directory this run worked inside is removed with everything in it."""
    path = scratch.path
    _assert(scratch.removed(), f"the scratch directory remains: {path}")
    return f"removed {path}"


def _run_case(
    results: list[_CaseResult],
    stream: Any,
    quiet: bool,
    name: str,
    body: Callable[[], str],
) -> None:
    """Run one case, record its outcome and print its line.

    A case that raises records a failure and the run continues with the next
    case. ``_SelfTestFailure`` carries the observation the case made; a
    ``LoadError`` or any of the listed defect classes is reported by type and
    message.
    """
    try:
        detail = body()
    except _SelfTestFailure as failure:
        result = _CaseResult(name=name, passed=False, detail=str(failure))
    except LoadError as error:
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
        BotoCoreError,
        ClientError,
        duckdb.Error,
    ) as error:
        result = _CaseResult(
            name=name,
            passed=False,
            detail=f"unexpected {_type_name(error)}: {error}",
        )
    else:
        result = _CaseResult(name=name, passed=True, detail=detail)
    results.append(result)
    if result.passed and quiet:
        return
    verdict = "PASS" if result.passed else "FAIL"
    print(
        f"self-test {verdict} {result.name} -- {_one_line(result.detail)}", file=stream
    )


def _self_test_status(results: Sequence[_CaseResult]) -> int:
    """Return ``EXIT_OK`` when every case passed and ``EXIT_SELF_TEST_FAILED`` else."""
    return (
        EXIT_OK
        if all(result.passed for result in results)
        else EXIT_SELF_TEST_FAILED
    )


def run_self_test(*, quiet: bool = False, stream: Any = None) -> int:
    """Run every self-test case and return ``EXIT_OK`` or ``EXIT_SELF_TEST_FAILED``.

    Each case prints one line to ``stream``, which defaults to stdout, followed
    by one summary line; ``quiet`` limits the case lines to the failing ones.
    Every database a case opens and every document a case writes sits inside one
    private temporary directory the run creates and the last case removes, so no
    case writes a path inside the repository and no case touches the database the
    bridge keeps at ``DEFAULT_DATABASE``. No case reaches a network endpoint: the
    S3 collaborators are the pinned boto3 client driven through moto in this
    process and through botocore's own stubber, the warehouse collaborator is the
    pinned DuckDB, and every environment variable this tool consults is set by
    the case that needs it and restored afterwards.
    """
    out = sys.stdout if stream is None else stream
    results: list[_CaseResult] = []
    scratch = _Scratch()
    try:
        _run_case(results, out, quiet, "schema_present", _case_schema_present)
        _run_case(
            results, out, quiet, "schema_failures",
            lambda: _case_schema_failures(scratch),
        )
        _run_case(results, out, quiet, "record_accepted", _case_record_accepted)
        _run_case(results, out, quiet, "record_refusals", _case_record_refusals)
        _run_case(
            results, out, quiet, "schema_violations_reported_once",
            _case_schema_violations_reported_once,
        )
        _run_case(
            results, out, quiet, "duplicate_members_refused",
            lambda: _case_duplicate_members_refused(scratch),
        )
        _run_case(
            results, out, quiet, "nesting_bounded",
            lambda: _case_nesting_bounded(scratch),
        )
        _run_case(results, out, quiet, "endpoint_accepted", _case_endpoint_accepted)
        _run_case(results, out, quiet, "endpoint_refused", _case_endpoint_refused)
        _run_case(
            results, out, quiet, "endpoint_resolving_name_refused",
            lambda: _case_endpoint_resolving_name_refused(scratch),
        )
        _run_case(
            results, out, quiet, "configured_endpoint_ignored",
            lambda: _case_configured_endpoint_ignored(scratch),
        )
        _run_case(
            results, out, quiet, "credentials_and_region_required",
            lambda: _case_credentials_and_region_required(scratch),
        )
        _run_case(
            results, out, quiet, "object_identity_recorded",
            _case_object_identity_recorded,
        )
        _run_case(
            results, out, quiet, "download_bound_to_identity",
            _case_download_bound_to_identity,
        )
        _run_case(results, out, quiet, "replacement_refused", _case_replacement_refused)
        _run_case(
            results, out, quiet, "digest_and_length_confirmed",
            _case_digest_and_length_confirmed,
        )
        _run_case(
            results, out, quiet, "recorded_identity_confirmed",
            lambda: _case_recorded_identity_confirmed(scratch),
        )
        _run_case(
            results, out, quiet, "manifest_binds_object",
            lambda: _case_manifest_binds_object(scratch),
        )
        _run_case(
            results, out, quiet, "download_failures_reported",
            _case_download_failures_reported,
        )
        _run_case(results, out, quiet, "failure_mapping", _case_failure_mapping)
        _run_case(
            results, out, quiet, "raw_relation_shape",
            lambda: _case_raw_relation_shape(scratch),
        )
        _run_case(
            results, out, quiet, "load_one_row", lambda: _case_load_one_row(scratch)
        )
        _run_case(
            results, out, quiet, "repeated_load_idempotent",
            lambda: _case_repeated_load_idempotent(scratch),
        )
        _run_case(
            results, out, quiet, "second_key_coexists",
            lambda: _case_second_key_coexists(scratch),
        )
        _run_case(
            results, out, quiet, "part_option_resolved", _case_part_option_resolved
        )
        _run_case(
            results, out, quiet, "parts_replayed",
            lambda: _case_parts_replayed(scratch),
        )
        _run_case(
            results, out, quiet, "rollback_restores_state",
            lambda: _case_rollback_restores_state(scratch),
        )
        _run_case(
            results, out, quiet, "row_counts_reported",
            lambda: _case_row_counts_reported(scratch),
        )
        _run_case(
            results, out, quiet, "database_path_accepted",
            lambda: _case_database_path_accepted(scratch),
        )
        _run_case(
            results, out, quiet, "database_path_refused",
            lambda: _case_database_path_refused(scratch),
        )
        _run_case(
            results, out, quiet, "database_path_below_root_refused",
            lambda: _case_database_path_below_root_refused(scratch),
        )
        _run_case(
            results, out, quiet, "self_test_server_silent",
            _case_self_test_server_silent,
        )
        _run_case(
            results, out, quiet, "environment_guard",
            lambda: _case_environment_guard(scratch),
        )
        _run_case(
            results, out, quiet, "interrupt_reported",
            lambda: _case_interrupt_reported(scratch),
        )
        _run_case(
            results, out, quiet, "interrupt_in_transaction",
            lambda: _case_interrupt_in_transaction(scratch),
        )
        _run_case(
            results, out, quiet, "sql_split_matrix",
            lambda: _case_sql_split_matrix(scratch),
        )
        _run_case(
            results, out, quiet, "identifiers_redacted",
            lambda: _case_identifiers_redacted(scratch),
        )
        _run_case(
            results, out, quiet, "cli_loads_and_redacts",
            lambda: _case_cli_loads_and_redacts(scratch),
        )
        _run_case(
            results, out, quiet, "show_identifiers_environment_matches_flag",
            lambda: _case_show_identifiers_environment_matches_flag(scratch),
        )
        _run_case(
            results, out, quiet, "leaked_identifier_still_caught",
            lambda: _case_leaked_identifier_still_caught(scratch),
        )
        _run_case(results, out, quiet, "exit_codes", lambda: _case_exit_codes(scratch))
    finally:
        _run_case(
            results, out, quiet, "scratch_removed",
            lambda: _case_scratch_removed(scratch),
        )

    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    print(
        f"self-test summary cases={len(results)} passed={passed} failed={failed}",
        file=out,
    )
    return _self_test_status(results)


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
            f"entity={LANDING_ENTITY}",
            f"extract_date=<{EXTRACT_DATE_FORM}>",
            OBJECT_NAME_TEMPLATE.format(part="N" * PART_NUMBER_DIGITS),
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
            "The object is bound to its own immutable identity first: its entity "
            "tag, its version where the bucket keeps versions and its byte count "
            "are recorded, the download requires them, and the bytes that arrive "
            "are confirmed and held to the whole landing schema before the "
            "database is opened: a repeated JSON member name is refused, every "
            "date is held to the calendar, and every timestamp is parsed as one "
            "real instant.\n"
            "Exit status: 0 success, 2 landed object rejected, 3 runtime "
            "environment, command line or "
            "setting rejected, 4 S3 endpoint, bucket or object operation "
            "unsuccessful, 5 database or SQL operation unsuccessful or a failed "
            "self-test case, 130 interrupted, which is that status and one line "
            "wherever the interrupt arrives, the third-party imports and the "
            "transaction included."
        ),
        epilog=(
            f"Object key: {key_template}\n"
            f"The landed column names, their order and the constraints the object "
            f"is validated against are read from {DEFAULT_SCHEMA.name}, and the "
            f"relation is defined by {', '.join(DDL_SCRIPT_NAMES)} in "
            f"{DDL_DIRECTORY}; this tool defines none of its own and runs no other "
            "SQL file.\n"
            f"One transaction covers the whole load: the two allowlisted scripts, "
            f"the removal of the rows carrying the natural key "
            f"({', '.join(NATURAL_KEY_FIELDS)}) of the downloaded object, and the "
            "write of that object as one row. A repeated run leaves one row, a row "
            "loaded from an earlier object survives, and a failure withdraws every "
            "change the transaction made.\n"
            f"One key carries one object per source system, entity, extract date and "
            f"part: --part names the part and {DEFAULT_PART_TEXT} applies when it is "
            "omitted, so a landing prefix holding several parts is replayed into the "
            "raw relation by running this loader once per part.\n"
            "stdout carries exactly one line, naming the relation written, the "
            "rows removed and written and the digest of the object loaded; the "
            "natural-key values are carried only under --show-identifiers. Every "
            "other message reaches stderr, and no credential, token or endpoint "
            "value is ever printed.\n"
            f"Run mode {RUN_MODE_LOCAL} runs this loader against a loopback "
            f"endpoint from --endpoint-url or {ENDPOINT_URL_VARIABLE}; run mode "
            f"{RUN_MODE_REAL} loads the raw relation through {REAL_MODE_LOADER} "
            "instead, and this tool refuses to run there. Every endpoint the "
            "environment or a profile configures is ignored, and an environment "
            "variable whose name merely begins with AWS is never read as a "
            "credential.\n"
            "This tool creates no bucket and provisions nothing. Results it "
            "produces are local-substitute results and establish nothing about a "
            "real-target run.\n"
            "Decision rationale: modernization/docs/decision-log.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--run-mode",
        default=None,
        choices=RUN_MODES,
        help=(
            "branch of the bridge to address; defaults to the "
            f"{RUN_MODE_VARIABLE} environment variable, then to "
            f"{DEFAULT_RUN_MODE}. Only {RUN_MODE_LOCAL} runs this loader: "
            f"{RUN_MODE_REAL} loads the raw relation through {REAL_MODE_LOADER}. "
            "It is the same setting that selects the dbt output and the landing "
            "endpoint"
        ),
    )
    parser.add_argument(
        "--bucket",
        default=None,
        metavar="NAME",
        help=(
            "bucket holding the landed object, which must already exist; defaults "
            f"to the {BUCKET_VARIABLE} environment variable. There is no built-in "
            "bucket name. A general-purpose bucket name: "
            f"{MIN_BUCKET_CHARACTERS} to {MAX_BUCKET_CHARACTERS} characters drawn "
            "from lowercase letters, digits, dot and hyphen, beginning and ending "
            "with a letter or a digit"
        ),
    )
    parser.add_argument(
        "--key",
        default=None,
        metavar="KEY",
        help=(
            "object to download, given as a bare key or as the "
            f"{SERVICE_NAME}{URI_SCHEME_SEPARATOR} URI land_to_s3.py printed, whose "
            "bucket must match --bucket. It must equal the key --source-system-key, "
            "the fixed entity literal, --extract-date and --part rebuild, so it "
            "confirms the object rather than selecting another; omitted, that rebuilt "
            "key is used"
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
            "entity element of the landing prefix, which is the fixed literal "
            f"{LANDING_ENTITY}; omitted, that literal applies, and any other value is "
            "refused rather than addressing an object outside the canonical prefix"
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
        "--part",
        default=None,
        metavar="NUMBER",
        help=(
            "part element of the landed object name, written as 1 to "
            f"{PART_NUMBER_DIGITS} decimal digits between {MIN_PART_NUMBER} and "
            f"{MAX_PART_NUMBER} and reaching the name zero-padded to "
            f"{PART_NUMBER_DIGITS} digits; omitted, part {DEFAULT_PART_TEXT} applies "
            f"and the object read is {OBJECT_NAME}. One prefix carries one record per "
            "part, so a prefix holding several parts is replayed by running this "
            "loader once per part; each load writes its own row and removes no row of "
            "another part"
        ),
    )
    parser.add_argument(
        "--endpoint-url",
        default=None,
        metavar="URL",
        help=(
            "loopback S3 endpoint serving the local substitute, selecting a local "
            f"S3-compatible endpoint; defaults to the {ENDPOINT_URL_VARIABLE} "
            f"environment variable. It is required, since this loader runs in run "
            f"mode {RUN_MODE_LOCAL} alone. Accepted values are "
            f"{' or '.join(ACCEPTED_ENDPOINT_SCHEMES)} on 127.0.0.0/8, ::1 or "
            f"{LOOPBACK_HOST_NAME} with an explicit port of "
            f"{ENDPOINT_PORT_FLOOR} or above, carrying no embedded credentials, "
            "query, fragment or path beyond '/'; every other endpoint is refused "
            "by name, and the value itself is never echoed"
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
            f"environment variable, and then to {DEFAULT_DATABASE}. Every "
            "component of the path is canonicalised, so a symbolic link, a "
            "/proc/self/cwd alias and a relative path are judged as the file they "
            f"reach; the result must name a file directly inside {DATABASE_DIRECTORY} "
            "rather than in a directory below it, must not be a symbolic link or an "
            "existing non-regular file, and must not name an authored file of that "
            "directory. Each of those is refused as a rejected setting, naming the "
            "setting it came from, with the configuration status before the object "
            "is downloaded"
        ),
    )
    parser.add_argument(
        "--no-ddl",
        dest="apply_ddl",
        action="store_false",
        help=(
            "apply neither shared warehouse script before writing the row, for a "
            "database whose relation is already present. Applied by default are "
            f"{', '.join(DDL_SCRIPT_NAMES)} from {DDL_DIRECTORY}, in that order and "
            "exactly as written; no option names another script"
        ),
    )
    parser.add_argument(
        SHOW_IDENTIFIERS_OPTION,
        action="store_true",
        help=(
            "carry record values in diagnostics, the natural-key values on the "
            "summary line and the object URI on the progress lines; without it none "
            "of them reaches the output, and no policy number, customer number, "
            "broker id or broker's reference is printed on any path. The "
            f"{SHOW_IDENTIFIERS_VARIABLE} environment variable carrying one of "
            f"{', '.join(SHOW_IDENTIFIERS_ENABLING)}, in any case and ignoring "
            "surrounding spaces, selects the same diagnostics and the same summary "
            "line as this option"
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run the built-in case matrix and exit, downloading nothing from any "
            "network endpoint and opening only databases inside one private "
            "temporary directory it creates and removes; the caller's database, "
            "bucket and settings are untouched"
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="with --self-test, print only the failing case lines and the summary",
    )
    parser.set_defaults(apply_ddl=True)
    return parser



def _report(
    relation: str,
    key_values: Sequence[str | None],
    removed: int,
    written: int,
    outcome_sha256: str,
    *,
    show_identifiers: bool = False,
) -> str:
    """Return the single stdout line naming what one load wrote.

    The line names the relation written, the rows removed and written and the
    digest of the object loaded, so a run can be audited from its own output.
    With ``show_identifiers`` false, which is the default, the natural-key values
    are replaced by a fixed marker and no business identifier reaches stdout,
    except that a field of ``DIGESTED_KEY_FIELDS`` is carried as the digest
    ``_identifier`` returns, which keeps the same run recognisable. With it true
    every field of ``NATURAL_KEY_FIELDS`` is named with the value it carried.
    """
    if show_identifiers:
        identity = " ".join(
            f"{field}={value}" for field, value in zip(NATURAL_KEY_FIELDS, key_values)
        )
        return (
            f"loaded {relation} {identity} removed={removed} written={written} "
            f"sha256={outcome_sha256}"
        )
    identity = " ".join(
        f"{field}="
        f"{_identifier(value) if field in DIGESTED_KEY_FIELDS else REDACTED_TEXT}"
        for field, value in zip(NATURAL_KEY_FIELDS, key_values)
        if value is not None
    )
    return (
        f"loaded {relation} {identity} keys={len(NATURAL_KEY_FIELDS)} "
        f"removed={removed} written={written} sha256={outcome_sha256} "
        "identifiers=redacted (--show-identifiers carries them)"
    )


def _run(args: argparse.Namespace) -> str:
    """Run one load and return the single line to write to stdout.

    Settings are resolved first, and the run mode is reconciled with the resolved
    endpoint before any session, client or credential exists, so a missing bucket,
    region, credential or script, a database path outside the one directory a
    database may sit in, and a run that belongs to the other branch are all
    reported before any object is downloaded and before the database is opened.

    Whether identifiers are carried is read from ``show_identifiers_enabled``, which
    ``main`` resolves once from ``--show-identifiers`` and the
    ``SHOW_IDENTIFIERS_VARIABLE`` environment variable, rather than from the option
    alone: the progress lines, the report and every diagnostic then answer to the same
    resolution, so the option and the variable select the same diagnostics and the
    same summary line, as this tool's help states and as
    modernization/extraction/extract_commarea.py and
    modernization/landing/land_to_s3.py already behave.
    """
    bucket = resolve_bucket(args.bucket)
    region = resolve_region(args.region)
    endpoint_url, endpoint_origin = resolve_endpoint_url(args.endpoint_url)
    run_mode, run_mode_origin = resolve_run_mode(args.run_mode)
    confirm_run_mode(run_mode, run_mode_origin, endpoint_url, endpoint_origin)
    _note(
        f"run mode {_shown(run_mode)} from {run_mode_origin}, loading from the "
        "loopback endpoint into the local database"
    )
    source_system_key = resolve_source_system_key(args.source_system_key)
    entity = resolve_entity(args.entity)
    extract_date = resolve_extract_date(args.extract_date)
    part = resolve_part(args.part)
    database_path = resolve_database_path(args.database)
    ddl_paths = resolve_ddl_paths(args.apply_ddl)
    key = resolve_object_key(
        args.key, bucket, source_system_key, entity, extract_date, part
    )
    relation = qualified_relation_name()
    show_identifiers = show_identifiers_enabled()
    outcome = load_record(
        bucket,
        key,
        source_system_key,
        extract_date,
        database_path,
        ddl_paths,
        part=part,
        region=region,
        endpoint_url=endpoint_url,
        show_identifiers=show_identifiers,
    )
    return _report(
        relation,
        outcome.key_values,
        outcome.removed,
        outcome.written,
        outcome.sha256,
        show_identifiers=show_identifiers,
    )


def main(argv: list[str] | None = None) -> int:
    """Load one landed object into the local raw relation, returning the exit status.

    ``argv`` defaults to the process arguments. Exactly one line reaches stdout
    on success, naming the relation written, the rows removed and written and the
    digest of the object loaded, with the natural-key values carried only under
    ``--show-identifiers``. Every diagnostic reaches stderr as one control-free
    line, names the setting to supply when one is missing, and carries no
    credential or token value and no policy, customer or broker identifier. A
    rejected command line is reported
    through that same single line, without a usage block, while ``--help``
    prints the full help and exits with status 0. With ``--self-test`` the case
    matrix runs instead of a load and its own lines reach stdout.
    """
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        set_show_identifiers(resolve_show_identifiers(args.show_identifiers))
        if args.self_test:
            return run_self_test(quiet=args.quiet)
        result = _run(args)
    except LoadError as error:
        print(f"{_PROGRAM}: {_one_line(str(error))}", file=sys.stderr)
        return error.exit_status
    except KeyboardInterrupt:
        _report_interrupt()
        return EXIT_INTERRUPTED

    print(result)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
