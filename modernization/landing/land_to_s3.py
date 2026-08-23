#!/usr/bin/env python3
"""Land one GenApp Policy-Issue record as a single S3 object with its COPY manifest.

WHAT THIS TOOL DOES
    Reads the landing JSON record written by
    modernization/extraction/extract_commarea.py, validates it against
    modernization/landing/landing-schema.json, writes it to exactly one S3 object
    under the landing prefix this module builds, and writes beside it the one-entry
    COPY manifest modernization/landing/load_redshift.sql binds its load to.
    Validation applies every constraint the schema declares, including its
    enumerations, lengths, patterns and its semantic
    date and timestamp formats, and a document repeating a member name is refused
    rather than resolved to its last value, so the document validated here and the
    bytes uploaded carry the same members. The bytes read from the record file
    are the bytes uploaded: no value is computed, scaled, rounded, padded, zero-filled
    or defaulted, no key is added, removed, renamed or reordered, and the parsed
    document is never re-serialised, so the object a loader reads is byte-identical to
    the record the harness produced. The six amount values pass through untouched.
    Each of them reaches the record through one MOVE, at base/src/lgapdb01.cbl:265,
    445, 489, 491, 493 and 495, and the three named programs carry no COMPUTE,
    MULTIPLY or DIVIDE statement and no COMP-3 item, so a landed amount is the digit
    string the chain moved and nothing else.

WHICH BYTES IT ACCEPTS AS A RECORD
    The uploaded bytes are the bytes on disk, and they are checked to be the canonical
    landed form before the upload: the ASCII-escaped JSON serialisation of the parsed
    object followed by one line feed, holding the landed keys in the order the landing
    schema's required list fixes. One comparison against that form refuses a
    pretty-printed or multi-line record, leading, surrounding or repeated whitespace, a
    carriage return, an absent or repeated terminal line feed, and a re-ordered key,
    and the diagnostic names the byte counts and the first differing offset. A repeated
    member name is refused by name while the record is parsed, so no member is resolved
    to a last-wins value. Each of these is a rejected record, reported as such, and
    nothing is uploaded. The schema admits return_code 00 alone, so a valid record is
    one successful execution of the LGAPOL01, LGAPDB01 and LGAPVS01 chain, carrying the
    policy number and the last-changed timestamp the chain assigned; a record carrying
    any other code is rejected by validation, which runs before any S3 client exists.

WHICH TARGET IT ADDRESSES
    One code path serves both targets, and one setting selects between them: the run
    mode, taken from --run-mode or the DBT_TARGET environment variable and defaulting
    to RUN_MODE_LOCAL. It is the same selector, with the same two values, that
    modernization/landing/load_local.py consumes and that the target key of
    modernization/dbt/genapp_rqi/profiles.example.yml resolves, so landing, raw loading
    and the dbt run cannot address different branches of the bridge.

    Run mode RUN_MODE_LOCAL requires a resolved S3 endpoint and addresses that
    endpoint. Run mode RUN_MODE_REAL forbids one and addresses AWS S3. Any other
    combination is refused, by name and origin, before a client exists, before a
    request is signed and before anything is written. An endpoint override is accepted
    only for a loopback address: http or https, a host of 127.0.0.0/8, ::1 or
    localhost, an explicit port of 1024 or above, no user information, no query, no
    fragment and no path beyond "/", and only when the resolved credentials came from
    the environment. Any other endpoint is refused, and no endpoint value reaches
    stdout, stderr or a diagnostic. Nothing else
    in this tool varies with the target. Access is established from resolved
    credentials, a resolved region and a bucket that answers a head request; the
    presence of an environment variable whose name begins with AWS is never read as
    evidence of access, and no variable is matched on that prefix.

    A supplied endpoint is accepted only as a local substitute: it must be an http or
    https URL whose host is a loopback literal (127.0.0.0/8 or ::1) or exactly
    localhost, carrying an explicit port, no userinfo, no path beyond '/', no query and
    no fragment. Every other endpoint is refused by name before a client exists, so no
    credential is signed and no request is sent to it: a remote host, a name that
    merely resolves to loopback, a host that only looks like a loopback literal, an
    embedded credential, a path, a query, a fragment, a missing port and any scheme
    other than http or https are all refused. With no endpoint supplied the client
    resolves the real AWS endpoint and every endpoint the environment or a
    configuration profile carries is ignored, so an AWS_ENDPOINT_URL or
    AWS_ENDPOINT_URL_S3 variable cannot redirect a credentialed request.

    --probe-redshift addresses the real target only. It requires run mode
    RUN_MODE_REAL and no endpoint override, and it refuses a loopback Redshift host,
    each by the setting it came from and before a socket is opened: a probe of
    something serving this machine can never be reported as a Redshift target that
    answered. It reads no bucket, region or credential setting of the S3 side at all.

WHICH MODES IT RUNS
    landing         the default: validate one record, write it as one object and
                    write the COPY manifest naming that object beside it.
    --probe         confirm access and exit, writing no landing object.
    --probe-redshift
                    confirm access to the real Redshift target and exit, which is
                    the second half of the precondition gate: connect with the
                    REDSHIFT_* settings the dbt profile of this bridge documents,
                    run one connectivity statement, then create, write, count and
                    roll back one temporary relation. It reads no record, makes no
                    S3 request and provisions nothing.
    --render-redshift-load
                    substitute modernization/landing/load_redshift.sql, or the
                    manifest that load binds to, for one validated record; no S3
                    request is made and no object is written.
    --self-test     run the built-in case matrix and exit; it reads no record of the
                    caller's, makes no request to any endpoint, and keeps every
                    document it writes inside one private temporary directory it
                    creates and removes.

WHICH INPUTS IT ACCEPTS
    --record        path to the landing JSON record, read as bytes and uploaded
                    unchanged, in a file of at most MAX_RECORD_BYTES bytes. Required
                    unless --probe, --probe-redshift or --self-test is given, which read
                    no record. It
                    holds one JSON object in the canonical landed form described above,
                    whose member names are unique, and that object must satisfy
                    modernization/landing/landing-schema.json including its date format,
                    must carry a normalised last_changed timestamp that names a real
                    moment, must carry no control character in any value, and must carry
                    the amounts its policy type populates and null in every other amount.
    --run-mode      branch of the bridge to address, RUN_MODE_LOCAL or RUN_MODE_REAL,
                    defaulting to the DBT_TARGET environment variable and then to
                    DEFAULT_RUN_MODE.
    --bucket        destination bucket, defaulting to the S3_BUCKET environment
                    variable. There is no built-in bucket name.
    --source-system-key
                    source-system element of the landing prefix, defaulting to the
                    SOURCE_SYSTEM_KEY environment variable and then to
                    DEFAULT_SOURCE_SYSTEM_KEY. It must equal the record's own
                    source_system_key value.
    --extract-date  extract-date element of the landing prefix as YYYY-MM-DD,
                    defaulting to the current UTC date.
    --entity        entity element of the landing prefix, which is the fixed literal
                    LANDING_ENTITY. Supplying any other value is refused rather than
                    landing the record outside the canonical prefix.
    --part          part element of the landed object name, written as 1 to
                    PART_NUMBER_DIGITS decimal digits and reaching the name zero-padded
                    to that width. Omitted, DEFAULT_PART_NUMBER applies and the object
                    name is OBJECT_NAME, so a caller that names no part writes the key
                    this contract has always fixed.
    --endpoint-url  loopback S3 endpoint to address, defaulting to the S3_ENDPOINT_URL
                    environment variable. Required in run mode RUN_MODE_LOCAL and
                    refused in run mode RUN_MODE_REAL.
    --region        region to address, defaulting to the AWS_REGION and then the
                    AWS_DEFAULT_REGION environment variable, and then to whatever the
                    boto3 session resolves for itself. --render-redshift-load requires
                    a region and resolves none from the session.
    --probe         confirm access and exit, writing no landing object.
    --probe-redshift
                    confirm access to the real Redshift target and exit. Every
                    setting is read from the environment: REDSHIFT_HOST,
                    REDSHIFT_USER, REDSHIFT_PASSWORD, REDSHIFT_DATABASE and
                    REDSHIFT_SCHEMA are required, REDSHIFT_PORT defaults to
                    DEFAULT_REDSHIFT_PORT and REDSHIFT_CONNECT_TIMEOUT to
                    DEFAULT_REDSHIFT_CONNECT_TIMEOUT seconds. No option carries
                    any of them, a password on a command line being readable by
                    every process on the host, and no value of any of them is
                    printed. Exclusive with --record, --probe,
                    --render-redshift-load and --self-test.
    --show-identifiers   carry record values in diagnostics. Withheld by default; also
                    enabled by the GENAPP_SHOW_IDENTIFIERS environment variable.
    --render-redshift-load
                    sql to render the Redshift load statements, manifest to render the
                    COPY manifest they bind to. Both require --record.
    --template      Redshift load template to substitute, defaulting to
                    load_redshift.sql beside this script.
    --iam-role      IAM role ARN written into the rendered load, defaulting to the
                    REDSHIFT_IAM_ROLE environment variable.
    --object-etag   ETag the landed object carries, defaulting to the ETag the record's
                    own bytes produce for a single-part upload.
    --object-version-id
                    version id the landed object carries on a versioned bucket,
                    defaulting to the literal recorded when a bucket keeps no versions.
    --self-test     run the built-in case matrix and exit.
    --quiet         with --self-test, print only the failing case lines and the summary.

    A setting supplied through an environment variable that holds the empty string or
    whitespace alone counts as unset, so the documented default applies; that is the
    empty-value resolution every command-line tool of this bridge applies.

HOW IT VALIDATES THE RECORD
    The record file is parsed with duplicate member names refused: a document carrying
    the same key twice is rejected rather than silently collapsed to its last
    occurrence, so the 17 keys the landing contract fixes cannot be smuggled past
    validation by a later duplicate. Its nesting is measured before it is parsed and a
    document nesting deeper than MAX_JSON_NESTING_DEPTH is refused unparsed, so a
    document built to exhaust a parser is a rejected record - one line and the record
    status - rather than an interpreter that ran out of stack; the same line reports a
    value the parser refuses without it being a syntax error, an integer literal longer
    than the interpreter converts being one. The parsed document is then checked against
    the landing schema as a Draft 2020-12 document with format assertion enabled, which
    holds every date-formatted value to the calendar as well as to its written shape,
    and each timestamp-carrying value is parsed against the exact written form the
    contract fixes, since that form carries no UTC offset and no format keyword of the
    dialect describes it. The schema admits a successful execution only: return_code is
    00 on every landed record, so a record carrying any other code is refused before
    anything is written.

    Two contract rules the schema declares are then applied again to the parsed
    document. No landed value carries a control character: every value is scanned for
    the C0 controls, DEL and the C1 controls, and a line feed or carriage return at the
    end of a value is refused along with one inside it. The six amounts carry the
    allocation the record's own policy type fixes: the payment amount on every policy
    type, the motor premium on M, the four commercial premiums on C, no product premium
    on E or H, and null - never a zero - in every amount the policy type does not
    populate. Both are reported by key and constraint, and both run before any client
    exists.

    A schema violation is reported by the JSON Pointer of the offending value, the
    constraint it breached and the value's JSON type and size. Violations that render
    identically - the same pointer, the same breached constraint and the same message -
    are reported once, and the count of the violations withheld past the reported bound
    counts each of them once, so a record omitting several landed keys carries one
    paragraph for the constraint it breached rather than one per omitted key, and every
    violation that reads differently is still reported. The value itself is
    reported only under --show-identifiers: these records carry policy, customer and broker
    identifiers, and this output is retained in run evidence.

WHAT --self-test CHECKS
    Schema loading and every way it can fail, record validation against the schema in
    both directions, the reporting of violations that render identically as one
    violation with every distinct one kept, rejection of a repeated JSON member at every
    nesting level of the
    record and of the schema, the nesting bound over a document at it, one past it, one
    far past it and one carrying brackets inside a landed value, the interpreter's own
    nesting bound reached with the real parser, an integer literal longer than the
    interpreter converts, rejection of a control character in each of the 17 landed
    values by the schema and by the tool with nothing uploaded, the product premium
    allocation over every policy type in both directions, the endpoint policy over
    accepted and refused forms, the access probe and its cleanup on success and on
    failure, one successful upload of the record and of the COPY manifest beside it, the
    digest and byte count a landing records on the object it writes, the
    replacement notice over a key that already carries an object and a key that does
    not, a head request that does not answer leaving the landing successful and silent
    about a replacement, two parts of one extract date landed as four coexisting objects
    each bound by its own manifest, the part option over every accepted and refused
    value, the
    upload failures botocore reports, the Redshift renderer over a byte-compared
    successful render and every rejected placeholder value, the rendered statement
    sequence and column list, the emitted manifest, the Redshift probe over every
    refused setting, the two settings that carry a default, the statements it runs and
    the write probe it rolls back, an interrupt reported as one line and status 130,
    and that every documented exit status is reachable. Collaborators are the pinned
    boto3 and botocore clients, driven through moto and through botocore's own stubber,
    so a call this matrix makes is a call the pinned client models; the Redshift probe
    is driven through a stand-in for the pinned driver, so the matrix opens no socket
    and reaches no warehouse.

WHERE IT WRITES
    Two objects of one landing prefix, the record

        landing/source_system_key=<KEY>/entity=policy_issue/extract_date=<YYYY-MM-DD>/part-<NNNN>.json

    giving the URI s3://<bucket>/<key>, and beside it the COPY manifest

        landing/source_system_key=<KEY>/entity=policy_issue/extract_date=<YYYY-MM-DD>/part-<NNNN>.manifest.json

    that modernization/landing/load_redshift.sql binds its load to. The segments are
    Hive-style key=value pairs in that order, <NNNN> is the part --part names written
    zero-padded to four digits and 0000 with no part named, neither key
    carries a leading slash, an empty segment or percent-encoding, and both objects are
    written with content type application/json. The source-system element is the value
    the validated record itself carries, the entity element is the fixed literal, and no
    element of either key is taken from a value that has not been validated.
    Partitioning applies to this key prefix alone, in the three Hive-style segments and
    no fourth: the part is an element of the object name, and this tool states no
    distribution, sort or partition property for any warehouse relation.

    The record object also carries its own land-time identity as user metadata of the
    one request that writes it: the SHA-256 digest of the bytes written under
    RECORDED_SHA256_METADATA and their byte count under RECORDED_LENGTH_METADATA. That
    is what modernization/landing/load_local.py holds the bytes it downloads to before
    it parses them, so an object rewritten under this key after the landing fails that
    load rather than reaching the raw relation. It is metadata of the record object, not
    a third object and not a member of the COPY manifest, so a landing still writes two
    objects and the manifest stays in the shape Amazon Redshift's manifest schema fixes.

    The record is written first and the manifest second, so a manifest on the bucket
    never names an object that was not written. The manifest holds one entry carrying
    the record's own URI, "mandatory" true and the byte count of the bytes just
    written, and is byte-identical to what --render-redshift-load manifest prints for
    the same record. Both objects are written in run mode RUN_MODE_LOCAL and in run mode
    RUN_MODE_REAL, so the real-branch order is land, then bootstrap the raw relation,
    then run the COPY of modernization/landing/load_redshift.sql, with no manifest to
    place by hand. A manifest write that does not succeed after the record was written
    fails the landing, names the manifest key and leaves the record object in place.

    One key carries one object per source system, entity, extract date and part, so
    every part of one extract date coexists under one prefix and the landing zone can be
    replayed to rebuild every raw row of that date: a run that lands two records names
    two parts and leaves two records and two manifests. A second landing of the same
    part addresses that same key and replaces the object it carries. The key is
    head-requested before the record is written, and an object already there is named in
    one warning line stating that this landing replaces it and that each record of one
    source system, entity and extract date is landed under its own part number. A head
    request that does not answer, whatever the reason, writes no line and changes
    nothing else: the record and the manifest are written and the landing succeeds.

    In landing mode stdout carries exactly one line, the s3:// URI of the object
    written. In probe mode stdout carries exactly one line, the probe verdict, and in
    --probe-redshift mode exactly one line, that probe's verdict, carrying no value of
    the settings it addressed. In --render-redshift-load mode stdout carries the
    rendered document and nothing else.
    Every other message reaches stderr. No credential, token, session value or
    environment listing is ever printed, on any path, and no value the landing record
    carries is printed unless --show-identifiers is given: a rejected record is reported by
    field, constraint and shape. No endpoint value is printed either: a refused
    endpoint is reported by the setting it came from and the element that was refused.

HOW IT FAILS
    Every failure writes one control-free line to stderr and returns a non-zero status:
    2 for a record that breaches the landing contract, 3 for a runtime environment that
    is not the pinned one, a rejected command line, an unresolved setting or a rejected
    template, 4 for an S3 endpoint, bucket or object
    operation that did not succeed or a Redshift target that did not answer or refused
    the probe, 5 for a failed self-test case, 130 for an interrupt, which is one line
    and that status wherever the interrupt arrives, the imports of this module included.
    A missing setting is named in the diagnostic. A record value never reaches a
    diagnostic unless --show-identifiers is given: without it a rejected value is
    reported by its JSON pointer, the schema keyword that rejected it, what the schema
    declares for that keyword and the value's JSON type and size. The tool never prompts
    and requires no TTY.

WHAT IT NEVER DOES
    It creates no bucket, cluster, workgroup, role, policy, network or key, and sets no
    versioning, encryption, lifecycle or bucket policy; a bucket that does not answer a
    head request is reported, never created. The Redshift probe creates no durable
    object either: its one relation is temporary, belongs to the session that created it
    and is withdrawn by the rollback of the transaction it was created in, and no
    database, schema, user or grant is added or changed. It writes no canonical
    relation, no object outside the landing prefix of the record it landed, and no
    provenance object: the record and the COPY manifest naming it are the two objects a
    landing writes, and no third object, no manifest of any other extract and no index
    of them is written. In landing, probe and render modes it writes nothing to the
    local filesystem, and it reads nothing under base/ in any mode. The probe object it
    writes in --probe mode is deleted in a finally block
    before the tool returns; a delete that does not succeed is a probe failure whose
    diagnostic names the probe key, which is then the one object the run may have left
    on the bucket.

WHERE THIS STEP SITS
    Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge, and
    Figure 5 — Validation Harness Control Flow, both in
    modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md.
"""

from __future__ import annotations

import sys

_PROGRAM = "land_to_s3"

# Status an interrupted run returns, and the one line it writes. Both are declared
# before every import but sys, and those imports are covered by the same reporting, so
# an interrupt that arrives while the standard library, boto3 or jsonschema is still
# loading is reported as that single line and that status rather than as a traceback of
# import frames. The run itself reports an interrupt through the same line.
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
    import os
    import re
    import shutil
    import tempfile
    import urllib.parse
    import uuid
    from collections.abc import Callable, Iterable, Mapping, Sequence
    from pathlib import Path
    from typing import Any, NamedTuple, NoReturn

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
    from jsonschema import FormatChecker
    from jsonschema.validators import Draft202012Validator
except KeyboardInterrupt:
    _report_interrupt()
    raise SystemExit(EXIT_INTERRUPTED) from None

# Landing schema used for validation, resolved from this script's own directory rather
# than from the working directory, so every working directory validates the same
# contract.
_THIS_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA = _THIS_DIR / "landing-schema.json"
DEFAULT_REDSHIFT_TEMPLATE = _THIS_DIR / "load_redshift.sql"

# Environment variables consulted when the matching option is omitted. No value read
# from any of them is ever printed.
BUCKET_VARIABLE = "S3_BUCKET"
ENDPOINT_URL_VARIABLE = "S3_ENDPOINT_URL"
SOURCE_SYSTEM_KEY_VARIABLE = "SOURCE_SYSTEM_KEY"
REGION_VARIABLES = ("AWS_REGION", "AWS_DEFAULT_REGION")
RUN_MODE_VARIABLE = "DBT_TARGET"
IAM_ROLE_VARIABLE = "REDSHIFT_IAM_ROLE"

# Run modes, which are the output names of
# modernization/dbt/genapp_rqi/profiles.example.yml. RUN_MODE_LOCAL addresses the local
# substitute - a loopback S3 endpoint and the DuckDB database - and RUN_MODE_REAL
# addresses AWS S3 and Redshift. The same two names select the branch in
# modernization/landing/load_local.py and in the dbt profile, so one setting selects
# the branch for the whole of landing, raw loading and the dbt run.
RUN_MODE_LOCAL = "local_substitute"
RUN_MODE_REAL = "redshift"
RUN_MODES = (RUN_MODE_LOCAL, RUN_MODE_REAL)
DEFAULT_RUN_MODE = RUN_MODE_LOCAL

# Environment variables naming the credentials a boto3 session resolves for itself.
# They are named in diagnostics and are never read by this module.
CREDENTIAL_VARIABLES = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")

# Landing prefix parts. The key is LANDING_KEY_ROOT, then one Hive-style segment per
# entry of PARTITION_FIELDS in this order, then the object name of the part being
# landed. PARTITION_FIELDS is the whole of the partitioning: the part is an element of
# the object name and never a fourth Hive-style segment.
LANDING_KEY_ROOT = "landing"
PARTITION_FIELDS = ("source_system_key", "entity", "extract_date")
KEY_SEPARATOR = "/"

# Object name of one landed part. One prefix carries one object per part, so two
# records of the same source system, entity and extract date coexist under distinct
# part numbers and the landing zone can be replayed to rebuild every raw row of that
# extract date. The part is written zero-padded to PART_NUMBER_DIGITS digits, so the
# name is the same width whatever the number; DEFAULT_PART_NUMBER applies when no part
# is named, which makes OBJECT_NAME and MANIFEST_OBJECT_NAME below the names a landing
# that names no part writes.
OBJECT_NAME_TEMPLATE = "part-{part}.json"
MANIFEST_OBJECT_NAME_TEMPLATE = "part-{part}.manifest.json"
PART_NUMBER_DIGITS = 4
MIN_PART_NUMBER = 0
MAX_PART_NUMBER = 10 ** PART_NUMBER_DIGITS - 1
DEFAULT_PART_NUMBER = 0
_PART_NUMBER_SHAPE = re.compile(r"\A[0-9]{1,%d}\Z" % PART_NUMBER_DIGITS)
_PART_TEXT_SHAPE = re.compile(r"\A[0-9]{%d}\Z" % PART_NUMBER_DIGITS)
DEFAULT_PART_TEXT = f"{DEFAULT_PART_NUMBER:0{PART_NUMBER_DIGITS}d}"
OBJECT_NAME = OBJECT_NAME_TEMPLATE.format(part=DEFAULT_PART_TEXT)

# Value used when the matching option and environment variable are both absent.
DEFAULT_SOURCE_SYSTEM_KEY = "GENAPP_CLASS_EXEMPLAR"

# Entity element of the landing prefix. One entity is landed by this bridge, so the
# value is fixed: --entity is accepted only when it repeats this literal.
LANDING_ENTITY = "policy_issue"

# Record key whose value must equal the resolved source-system key, and the key the
# landing prefix's source-system element is taken from once the record is validated.
SOURCE_SYSTEM_KEY_FIELD = "source_system_key"

# Record keys carrying a calendar date, and the key carrying the normalised
# last-changed timestamp. Each is parsed before the record reaches the network, so a
# value of the right shape that names no day or no moment is refused here rather than
# at the DATE or TIMESTAMP cast of the downstream dbt models. The date keys also carry
# the landing schema's "date" format, which build_format_checker asserts.
DATE_FIELDS = ("issue_date", "expiry_date")
TIMESTAMP_FIELD = "last_changed"

# Record key carrying the product discriminator, the six amount keys, and which of
# those amounts carry a value for each policy type the discriminator may hold. The
# payment amount sits in the fixed policy header at base/src/lgcmarea.cpy:43 and is
# carried by every policy type; each product premium sits in the overlay its own
# request selects and is null on every other policy type. The overlays redefine the
# same COMMAREA bytes from offset 101, so the window of an inapplicable premium can
# hold the selected overlay's content: the policy type decides which amount is carried
# and blank or zero window content is not that test. The same allocation is recorded by
# the product_premium_nullability block of
# modernization/extraction/copybook_field_map.yml and declared by the allOf block of
# modernization/landing/landing-schema.json.
POLICY_TYPE_FIELD = "policy_type"
PAYMENT_FIELD = "payment_amount"
MOTOR_PREMIUM_FIELD = "motor_premium_amount"
COMMERCIAL_PREMIUM_FIELDS = (
    "fire_premium_amount",
    "crime_premium_amount",
    "flood_premium_amount",
    "weather_premium_amount",
)
AMOUNT_FIELDS = (PAYMENT_FIELD, MOTOR_PREMIUM_FIELD, *COMMERCIAL_PREMIUM_FIELDS)
PREMIUM_ALLOCATION: dict[str, tuple[str, ...]] = {
    "M": (PAYMENT_FIELD, MOTOR_PREMIUM_FIELD),
    "C": (PAYMENT_FIELD, *COMMERCIAL_PREMIUM_FIELDS),
    "E": (PAYMENT_FIELD,),
    "H": (PAYMENT_FIELD,),
}

# Forms the date and timestamp values are written in. The timestamp form carries no UTC
# offset, so it is not an RFC 3339 date-time and is parsed with this exact pattern
# rather than by a schema format.
DATE_FORM = "YYYY-MM-DD"
TIMESTAMP_FORM = "YYYY-MM-DDTHH:MM:SS.ffffff"
TIMESTAMP_PATTERN = "%Y-%m-%dT%H:%M:%S.%f"
TIMESTAMP_OUTPUT_SEPARATOR = "T"
TIMESTAMP_OUTPUT_PRECISION = "microseconds"

# Service addressed, and the content type the landed object carries.
SERVICE_NAME = "s3"
OBJECT_CONTENT_TYPE = "application/json"

# User-metadata names the landed object carries its own land-time identity under: the
# SHA-256 digest of the body written, as 64 lower-case hexadecimal characters, and the
# byte count of that body, as decimal digits. Both are written by the one PutObject
# that writes the record, so a landing still writes exactly two objects, and
# modernization/landing/load_local.py requires them to equal what it downloaded before
# it parses anything. Object metadata names reach the wire as x-amz-meta-<name> and are
# reported back lower-cased, so both are written lower-case here and compared
# lower-cased there.
# Decision rationale: modernization/docs/decision-log.md, row D-124.
RECORDED_SHA256_METADATA = "genapp-sha256"
RECORDED_LENGTH_METADATA = "genapp-content-length"

# Semantic formats the landing schema asserts, and the exact representation the
# genapp-timestamp checker parses.
DATE_FORMAT_NAME = "date"
TIMESTAMP_FORMAT_NAME = "genapp-timestamp"
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

# Accepted shapes. A partition segment value becomes one path segment, so it carries
# no separator, no whitespace and no equals sign. A landed column name is compared
# against SQL text, so it is confirmed usable as one unquoted SQL identifier. The
# bucket naming rules are declared below, with the service's own restrictions.
_SEGMENT_SHAPE = re.compile(r"\A[A-Za-z0-9_.\-]+\Z")
_IDENTIFIER_SHAPE = re.compile(r"\A[a-z][a-z0-9_]*\Z")
MAX_SEGMENT_CHARACTERS = 64

# General-purpose bucket naming rules, which a bucket name must satisfy to be
# addressable at all: 3 to 63 characters drawn from lowercase letters, digits, dot and
# hyphen, beginning and ending with a letter or a digit, carrying no two adjacent dots,
# not written as an IPv4 address, and carrying none of the prefixes or suffixes the
# service reserves for its own name spaces. A name outside these rules cannot name an
# existing bucket, so it is refused here rather than sent as a request that cannot
# succeed.
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
MAX_IDENTIFIER_CHARACTERS = 63

# Endpoint overrides accepted. An override sends signed requests and the landing
# payload wherever it names, so only a local S3-compatible endpoint is accepted: one of
# these schemes, a loopback host, an explicit port at or above ENDPOINT_PORT_FLOOR, no
# user information, no query, no fragment and no path beyond a single separator, within
# MAX_ENDPOINT_CHARACTERS characters. Every port from that floor up is accepted, so
# concurrent local endpoints on different ports are all reachable, while no override can
# address a privileged loopback service. With no override the SDK resolves the AWS
# endpoint itself.
ENDPOINT_PORT_FLOOR = 1024
MAX_ENDPOINT_CHARACTERS = 256

# Text a redacted endpoint value is replaced by, and the URLs redacted out of a
# diagnostic. A library diagnostic can quote the endpoint it addressed, so every http
# and https URL is replaced before the text reaches stderr.
REDACTED_ENDPOINT = "<endpoint>"
_URL_IN_TEXT = re.compile(r"(?i)https?://[^\s\"'<>,]*")

# Credential resolution methods accepted while a custom endpoint is addressed. The
# method is the name botocore records on the credentials it resolved: 'env' for the
# AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY variables and 'explicit' for values
# passed to the session directly. Any other method - a shared credentials file, a
# configured profile, single sign-on, an assumed role, container or instance metadata -
# names credentials that belong to a real account, and those are never signed against a
# local endpoint.
LOCAL_CREDENTIAL_METHODS = ("env", "explicit")

# Extract date form accepted on the command line and emitted into the key.
EXTRACT_DATE_FORM = "YYYY-MM-DD"

# Endpoint policy. A supplied endpoint is a local substitute and must carry one of
# these schemes, an explicit port, and a host that is either a loopback IP literal or
# exactly LOOPBACK_HOST_NAME compared without case. No name is resolved: a host is
# accepted for the literal it is, never for the address it resolves to.
ACCEPTED_ENDPOINT_SCHEMES = ("http", "https")
LOOPBACK_HOST_NAME = "localhost"
ACCEPTED_ENDPOINT_PATHS = ("", KEY_SEPARATOR)

# Statement timeout the rendered load sets, in whole milliseconds: digits alone, with
# no leading zero, so the bound is positive. DEFAULT_STATEMENT_TIMEOUT_MS is the value
# modernization/landing/load_redshift.sql records for a caller that names none.
_TIMEOUT_SHAPE = re.compile(r"\A[1-9][0-9]{0,8}\Z")
MAX_TIMEOUT_DIGITS = 9
DEFAULT_STATEMENT_TIMEOUT_MS = "900000"

# Shape of one ${NAME} placeholder of the Redshift load template, and the opening
# sequence a rendered document must no longer carry.
_PLACEHOLDER_SHAPE = re.compile(r"\$\{([^{}]*)\}")
PLACEHOLDER_OPENER = "${"

# Object name of the COPY manifest the Redshift load binds to, written beside the
# landed object under the same landing prefix and carrying the same part number, so
# each landed part is bound by its own manifest.
MANIFEST_OBJECT_NAME = MANIFEST_OBJECT_NAME_TEMPLATE.format(part=DEFAULT_PART_TEXT)

# Documents --render-redshift-load emits, and the value naming each of them.
RENDER_DOCUMENT_SQL = "sql"
RENDER_DOCUMENT_MANIFEST = "manifest"
RENDER_DOCUMENTS = (RENDER_DOCUMENT_SQL, RENDER_DOCUMENT_MANIFEST)

# Value recorded as the object version when the bucket keeps no versions.
NOT_VERSIONED = "not-versioned"

# Keys of the landing record, whose count is the invariant the schema's properties
# block is read against, and the record field carrying the policy number the delete
# guard of the rendered load matches.
EXPECTED_COLUMN_COUNT = 17
POLICY_NUMBER_FIELD = "policy_number"

# Shapes every placeholder value is validated against before it is substituted, and
# the longest value each accepts. A bucket name is validated against the S3 bucket
# naming rules rather than the wider shape a reported URI accepts.
_BUCKET_NAME_SHAPE = re.compile(r"\A[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9]\Z")
_IPV4_SHAPE = re.compile(r"\A[0-9]{1,3}(\.[0-9]{1,3}){3}\Z")
_POLICY_NUMBER_SHAPE = re.compile(r"\A[0-9]{1,10}\Z")
_IAM_ROLE_ARN_SHAPE = re.compile(
    r"\Aarn:aws[a-z0-9\-]*:iam::[0-9]{12}:role/[A-Za-z0-9+=,.@_/\-]{1,512}\Z"
)
_REGION_SHAPE = re.compile(r"\A[a-z]{2}(-[a-z]+){1,3}-[0-9]\Z")
_CONTENT_LENGTH_SHAPE = re.compile(r"\A[1-9][0-9]{0,11}\Z")
_SHA256_SHAPE = re.compile(r"\A[0-9a-f]{64}\Z")
_ETAG_SHAPE = re.compile(r"\A[0-9a-f]{32}(-[1-9][0-9]{0,4})?\Z")
_VERSION_ID_SHAPE = re.compile(r"\A[A-Za-z0-9._\-]{1,1024}\Z")
MAX_IAM_ROLE_CHARACTERS = 2048
MAX_REGION_CHARACTERS = 32
MAX_VERSION_ID_CHARACTERS = 1024

# Fragments no substituted value may carry. Every allowlist above already excludes
# them; a value is checked against them again immediately before it is escaped.
_FORBIDDEN_LITERAL_FRAGMENTS = ("'", '"', ";", "--", "/*", "*/", "\\")

# Statement sequence the rendered Redshift load carries, by leading keyword.
RENDERED_TRANSACTION_FRAME = ("BEGIN", "COMMIT")
RENDERED_REQUIRED_KEYWORDS = ("DELETE", "COPY")
DELETE_BOUND_MARKERS = ("%(source_system_key)s", "%(policy_number)s")

# Statement sequence the authored template renders to: the timeout, the transaction, the
# staging relation, the manifest COPY, the staged-record assertions, the delete keyed on
# the staged natural key, the write, the post-write assertion and the drop.
RENDERED_AUTHORED_SEQUENCE = (
    "SET",
    "BEGIN",
    "CREATE",
    "COPY",
    "SELECT",
    "SELECT",
    "DELETE",
    "INSERT",
    "SELECT",
    "DROP",
    "COMMIT",
)

# Bytes one read takes from the record and from the schema before anything parses
# them, and the bytes one read asks for at a time.
MAX_RECORD_BYTES = 1024 * 1024
MAX_SCHEMA_BYTES = 4 * 1024 * 1024
READ_CHUNK_BYTES = 65536

# Arrays and objects one JSON document this tool parses may nest inside one another,
# and the structural characters that count. A landed record is one flat object, so it
# nests one level; the landing schema nests six; the bound leaves that room many times
# over and is reached only by a document built to exhaust a parser. It is measured
# before the document is handed to the parser, so a document past it is refused as a
# rejected input rather than by the interpreter running out of stack.
# Decision rationale: modernization/docs/decision-log.md, row D-122.
MAX_JSON_NESTING_DEPTH = 64
_JSON_STRING_DELIMITER = '"'
_JSON_STRING_ESCAPE = "\\"
_JSON_OPENERS = "[{"
_JSON_CLOSERS = "]}"

# Prefix, object name shape and payload of the object written by --probe. The prefix
# is outside LANDING_KEY_ROOT, so a probe object can never be read as landed data.
PROBE_KEY_ROOT = "_genapp_rqi_access_probe"
PROBE_NAME_TEMPLATE = "probe-{token}.tmp"
PROBE_BODY = b"genapp-rqi-access-probe\n"
PROBE_CONTENT_TYPE = "text/plain"

# Leading text of the single stdout line --probe writes when every step succeeded.
PROBE_VERDICT = "s3-access-probe ok"

# Settings the Redshift probe resolves, which are the variables the redshift output of
# modernization/dbt/genapp_rqi/profiles.example.yml reads for the same connection. The
# probe reads them from the environment alone: a password on a command line is visible
# to every process on the host, so no option carries one.
REDSHIFT_PROFILE_DOCUMENT = "modernization/dbt/genapp_rqi/profiles.example.yml"
REDSHIFT_HOST_VARIABLE = "REDSHIFT_HOST"
REDSHIFT_PORT_VARIABLE = "REDSHIFT_PORT"
REDSHIFT_USER_VARIABLE = "REDSHIFT_USER"
REDSHIFT_PASSWORD_VARIABLE = "REDSHIFT_PASSWORD"
REDSHIFT_DATABASE_VARIABLE = "REDSHIFT_DATABASE"
REDSHIFT_SCHEMA_VARIABLE = "REDSHIFT_SCHEMA"
REDSHIFT_CONNECT_TIMEOUT_VARIABLE = "REDSHIFT_CONNECT_TIMEOUT"

# Defaults the same profile carries for the two settings that have one, and the bounds
# every resolved number is held to. A connect timeout is bounded above as well as
# below, so a probe that cannot reach the endpoint fails rather than waiting without
# limit.
DEFAULT_REDSHIFT_PORT = 5439
DEFAULT_REDSHIFT_CONNECT_TIMEOUT = 30
MIN_PORT_NUMBER = 1
MAX_PORT_NUMBER = 65535
MIN_CONNECT_TIMEOUT_SECONDS = 1
MAX_CONNECT_TIMEOUT_SECONDS = 3600

# Transport security the probe requires, which is the sslmode the same profile sets:
# the server certificate has to be issued for the host being addressed and to chain to
# a trusted authority, so a probe cannot succeed against an endpoint standing in for
# the real target.
REDSHIFT_SSL_MODE = "verify-full"
REDSHIFT_APPLICATION_NAME = "genapp_rqi_access_probe"

# Shapes the resolved Redshift settings are held to before a socket is opened. A host
# is a DNS name or an IPv4 literal, which admits no scheme, port, path, user
# information or whitespace; a database, user or schema name is the shape the driver
# carries as a connection parameter; a password is bounded and control-free, and its
# value is neither shaped further nor ever echoed.
_REDSHIFT_HOST_SHAPE = re.compile(r"\A[A-Za-z0-9]([A-Za-z0-9.\-]{0,253}[A-Za-z0-9])?\Z")
_REDSHIFT_NAME_SHAPE = re.compile(r"\A[A-Za-z0-9_][A-Za-z0-9_$.@\-]{0,126}\Z")
_REDSHIFT_NUMBER_SHAPE = re.compile(r"\A[0-9]{1,5}\Z")
MAX_REDSHIFT_HOST_CHARACTERS = 255
MAX_REDSHIFT_NAME_CHARACTERS = 127
MAX_REDSHIFT_PASSWORD_CHARACTERS = 256

# The write probe --probe-redshift performs: one temporary relation of one column,
# created, written, counted and then withdrawn by the rollback of the transaction it
# was created in. A temporary relation belongs to the session that created it and no
# durable object is created, so the probe provisions nothing and leaves nothing behind.
REDSHIFT_PROBE_RELATION_TEMPLATE = "genapp_rqi_access_probe_{token}"
REDSHIFT_PROBE_COLUMN = "probe"
REDSHIFT_PROBE_VALUE = "genapp-rqi-access-probe"
REDSHIFT_PROBE_COLUMN_WIDTH = 64
REDSHIFT_PROBE_STATEMENT = "SELECT 1"
REDSHIFT_PROBE_STATEMENT_VALUE = 1
REDSHIFT_PROBE_ROWS = 1

# Leading text of the single stdout line --probe-redshift writes when every step
# succeeded, and the outcome it records for the write probe. No setting value reaches
# that line: the host, the port, the user, the database, the schema and the password
# are all withheld from stdout, stderr and every diagnostic.
REDSHIFT_PROBE_VERDICT = "redshift-access-probe ok"
REDSHIFT_PROBE_WRITE_OUTCOME = "rolled-back"

# Text a redacted setting value is replaced by in a reason the driver supplied.
REDACTED_SETTING = "<redacted>"

# Connection behaviour applied to every request, bounding the time a failing endpoint
# can hold up the caller. MAX_ATTEMPTS is the number of calls one request makes in
# total, the first included, and is applied through the client's total_max_attempts
# setting.
CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 3
RETRY_MODE = "standard"

EXIT_OK = 0
EXIT_RECORD_REJECTED = 2
EXIT_CONFIGURATION_REJECTED = EXIT_ENVIRONMENT_REJECTED
EXIT_S3_UNAVAILABLE = 4
EXIT_SELF_TEST_FAILED = 5
# A Redshift target that did not answer or refused the probe returns the same status as
# an S3 endpoint that did not answer: the run established no access to the target it
# addressed. EXIT_INTERRUPTED is declared above the imports, with the reporting that
# covers them.
EXIT_REDSHIFT_UNAVAILABLE = EXIT_S3_UNAVAILABLE

# Characters of untrusted text one diagnostic fragment carries before truncation, the
# number of schema violations one diagnostic reports, and the property names one
# violation names.
MAX_DIAGNOSTIC_CHARACTERS = 64
MAX_DIAGNOSTIC_PATH_CHARACTERS = 160
MAX_DIAGNOSTIC_MESSAGE_CHARACTERS = 200
MAX_REPORTED_SCHEMA_ERRORS = 5
MAX_REPORTED_PROPERTY_NAMES = 8

# Opt-in carrying record values into diagnostics, the environment variable consulted
# when the option is omitted, and the values that variable may carry to enable it.
# Without the opt-in a rejected value is reported by its JSON pointer, the constraint
# it breached and its size, never by its content.
SHOW_IDENTIFIERS_OPTION = "--show-identifiers"
SHOW_IDENTIFIERS_VARIABLE = "GENAPP_SHOW_IDENTIFIERS"
SHOW_IDENTIFIERS_ENABLING = ("1", "true", "yes", "on")

# Characters escaped out of a diagnostic, and refused in a landed value: the C0
# controls, DEL and the C1 controls. confirm_control_free_values scans every landed
# value against this class, and the landing schema's own patterns and enumerations
# admit none of these characters either.
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


class TemplateError(ConfigurationError):
    """The Redshift load template cannot be read or cannot be substituted."""

    exit_status = EXIT_CONFIGURATION_REJECTED


class AccessError(LandingError):
    """A target refused access: an S3 operation or the Redshift probe did not succeed."""

    exit_status = EXIT_S3_UNAVAILABLE


# Whether a diagnostic may carry record values. Set once from the command line and the
# environment before any record is read.
_show_identifiers = False


def set_show_identifiers(enabled: bool) -> None:
    """Record whether a diagnostic may carry record values."""
    global _show_identifiers
    _show_identifiers = bool(enabled)


def show_identifiers_enabled() -> bool:
    """Return True when a diagnostic may carry record values."""
    return _show_identifiers


def resolve_show_identifiers(supplied: bool) -> bool:
    """Return whether record values are shown, from the option then the environment.

    ``supplied`` is the ``--show-identifiers`` flag, which enables display on its own. With
    the flag absent the ``SHOW_IDENTIFIERS_VARIABLE`` environment variable enables display
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


def _quote_all(names: Iterable[Any]) -> str:
    """Return ``names`` quoted, escaped and joined by a comma, in the order given."""
    return ", ".join(_shown(str(name)) for name in names)


def _display(value: Any) -> str:
    """Return any value rendered for a diagnostic, quoting text and naming a type."""
    if isinstance(value, str):
        return _shown(value)
    if value is None or isinstance(value, (bool, int, float)):
        return str(value)
    return f"a {_type_name(value)}"


def _redacted(text: str) -> str:
    """Return ``text`` with every http and https URL replaced by ``REDACTED_ENDPOINT``.

    A client-library diagnostic can quote the endpoint it addressed, and the endpoint is
    a setting this tool never discloses, so the URL is removed rather than truncated.
    """
    return _URL_IN_TEXT.sub(REDACTED_ENDPOINT, text)
def _withheld(length: int) -> str:
    """Return the fragment standing for a withheld value of ``length`` characters."""
    return f"<redacted {length} chars>"


def _value(value: str, limit: int = MAX_DIAGNOSTIC_CHARACTERS) -> str:
    """Return one record value for a diagnostic, withheld unless display is enabled.

    With display enabled the value is quoted and escaped as any other fragment. With
    display withheld the fragment carries the character count alone, so a diagnostic
    still states how long the rejected value was without carrying it.
    """
    if show_identifiers_enabled():
        return _shown(value, limit)
    return _withheld(len(value))


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


def _reason(error: BaseException) -> str:
    """Return the reason text of ``error`` as one bounded diagnostic fragment.

    Any endpoint URL the error text quotes is redacted before the fragment is bounded.
    """
    text = str(error) or _type_name(error)
    return _escaped(_redacted(text), MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)


def _names_shown(names: Sequence[str]) -> str:
    """Return ``names`` quoted and joined, at most ``MAX_REPORTED_PROPERTY_NAMES``.

    Names past the limit are dropped and the fragment records how many were dropped, so
    a wildly wrong document cannot produce an unbounded diagnostic. A member name is
    part of the landing contract rather than a landed value, so each reported name is
    named in full.
    """
    kept = [_shown(str(name)) for name in names[:MAX_REPORTED_PROPERTY_NAMES]]
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
# Record and schema
# ---------------------------------------------------------------------------


class DuplicateMemberError(ValueError):
    """A JSON object carries the same member name twice.

    ``name`` is the member that repeated. The error is raised out of the parser, from
    the nesting level that carried the repetition, before the document is returned.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f"the JSON object carries the member {name!r} more than once")
        self.name = name


def _distinct_members(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    """Return the members of one JSON object, refusing a name that repeats.

    This is the object hook every JSON document this tool reads is parsed with, so a
    repeated member is refused at every nesting level of the document rather than
    silently resolved to the last occurrence.

    Raises ``DuplicateMemberError`` naming the first member that repeats.
    """
    members: dict[str, Any] = {}
    for name, value in pairs:
        if name in members:
            raise DuplicateMemberError(name)
        members[name] = value
    return members


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


def _end_of_json_string(text: str, opening: int) -> int:
    """Return the index just past the string literal ``text`` opens at ``opening``.

    The closing delimiter is the first one not escaped by an odd number of preceding
    backslashes, which is the escaping the JSON grammar fixes, so a structural
    character inside a string value is never counted as nesting. An unterminated
    literal returns the end of ``text``: that document is not well-formed and the
    parser reports it, and counting no nesting past the opener cannot admit a
    document the parser would then nest deeply into.
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

    One pass over ``text`` counts an opening bracket or brace as one level and the
    matching closing one as the end of that level, skipping every string literal, so
    a bracket inside a landed value is not counted. Counting stops as soon as the
    depth passes ``limit`` and the value returned is then ``limit + 1``: a document
    built to exhaust a parser is refused after its first ``limit + 1`` characters
    rather than being scanned in full. The pass is linear in the length of ``text``
    and allocates nothing beyond the loop's own indices, so it cannot itself be the
    denial of service it guards against.

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

    The nesting of ``text`` is measured before it is parsed and a document nesting
    deeper than ``depth_limit`` is refused unparsed, so no document this tool reads
    can drive the parser into the interpreter's own nesting bound. Two further
    outcomes of the parser itself are reported the same way rather than as a
    traceback: the interpreter's nesting bound, which a document within
    ``depth_limit`` reaches only when the stack was already nearly spent, and a value
    the parser refuses without it being a syntax error, which an integer literal
    longer than the interpreter converts to an int is. ``depth_limit`` is the module's
    bound for every caller of this tool; a larger one is passed only by the self-test
    case that exercises the interpreter's own bound with the real parser.

    Raises ``json.JSONDecodeError`` when ``text`` is not one well-formed JSON document,
    ``DuplicateMemberError`` when any object in it carries a member name twice, and
    ``UnparsableDocumentError`` when it is past one of the three bounds above.
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


def _rendered_byte(value: int) -> str:
    """Return one printable 7-bit ASCII rendering of the byte ``value``."""
    if 0x20 <= value <= 0x7E:
        return chr(value)
    return f"\\x{value:02x}"


def _byte_difference(actual: bytes, expected: bytes) -> str:
    """Return one bounded description of the first difference between two byte strings.

    The description names the byte counts when they differ, the offset of the first
    differing byte, and that byte and its canonical counterpart, each rendered as one
    printable 7-bit ASCII fragment. No record content beyond the differing byte is
    reported. An empty string is returned when the two are equal.
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


def landed_key_order(
    schema: Mapping[str, Any], path: Path = DEFAULT_SCHEMA
) -> tuple[str, ...]:
    """Return the landed key order the schema's ``required`` list fixes.

    ``path`` names the schema in any diagnostic.

    Raises ``SchemaError`` when ``required`` is absent, is not a list of strings, is
    empty or repeats a name.
    """
    required = schema.get("required")
    if not isinstance(required, list) or not required:
        raise SchemaError(
            f"the landing schema carries {_display(required)} as 'required': "
            f"{_path_shown(path)}; a non-empty list of landed key names is required"
        )
    names: list[str] = []
    for name in required:
        if not isinstance(name, str) or not name:
            raise SchemaError(
                f"the landing schema lists {_display(name)} in 'required': "
                f"{_path_shown(path)}; every entry is a landed key name"
            )
        if name in names:
            raise SchemaError(
                f"the landing schema lists {_shown(name)} twice in 'required': "
                f"{_path_shown(path)}"
            )
        names.append(name)
    return tuple(names)


def confirm_key_order(
    record: Mapping[str, Any], order: Sequence[str], path: Path
) -> None:
    """Confirm ``record`` carries its keys in ``order``, and return None when it does.

    ``order`` is the landed key order the landing schema fixes and ``path`` names the
    record in any diagnostic. The count is compared first, then the position of every
    key.

    Raises ``RecordError`` naming the first position that differs, or the counts when
    they differ.
    """
    carried = tuple(record)
    if len(carried) != len(order):
        raise RecordError(
            f"the landing record carries {len(carried)} keys where the landing "
            f"contract fixes {len(order)}: {_path_shown(path)}"
        )
    for position, (found, wanted) in enumerate(zip(carried, order, strict=True)):
        if found != wanted:
            raise RecordError(
                f"the landing record carries its keys out of the order the landing "
                f"contract fixes: {_path_shown(path)}; at position {position} it "
                f"carries {_shown(found)} where {_shown(wanted)} is required"
            )


def canonical_record_bytes(record: Mapping[str, Any]) -> bytes:
    """Return the canonical landed bytes of ``record``.

    The canonical form is the ASCII-escaped JSON serialisation of ``record``, with the
    keys in the order ``record`` carries them and the separators ``json.dumps``
    applies, followed by one line feed. This is the form
    modernization/extraction/extract_commarea.py writes.
    """
    return (json.dumps(dict(record), ensure_ascii=True) + "\n").encode("ascii")


def confirm_canonical_bytes(
    raw: bytes, record: Mapping[str, Any], path: Path
) -> None:
    """Confirm ``raw`` is the canonical landed form of ``record``, and return None.

    ``raw`` are the bytes read from the record file, which are the bytes uploaded, and
    ``record`` is the object parsed from them. One comparison against
    ``canonical_record_bytes`` covers the whole byte contract: one line, no
    pretty-printing, no surrounding or repeated whitespace, no carriage return, exactly
    one terminal line feed, the separators the extractor emits and the landed key
    order. ``path`` names the record in any diagnostic.

    Raises ``RecordError`` describing the first difference when ``raw`` is not that
    form.
    """
    expected = canonical_record_bytes(record)
    if raw == expected:
        return
    raise RecordError(
        f"the landing record is not the canonical one-line form the landing contract "
        f"fixes: {_path_shown(path)}: {_byte_difference(raw, expected)}"
    )


def parse_record(raw: bytes, path: Path) -> Mapping[str, Any]:
    """Return the single JSON object ``raw`` carries, decoded as UTF-8.

    ``raw`` is inspected only; the caller keeps it for upload unchanged. ``path`` names
    the input in any diagnostic. The members of every object are kept in document order,
    and a member name that repeats at any nesting level is refused and named, so
    validation and every later reader see the same members.

    Raises ``RecordError`` when ``raw`` is not valid UTF-8, is not one well-formed JSON
    document, nests deeper than ``MAX_JSON_NESTING_DEPTH``, carries a value the parser
    refuses, carries a second document, carries a repeated member name, or carries a
    JSON value that is not an object.
    """
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RecordError(
            f"the landing record is not valid UTF-8: {_path_shown(path)}: "
            f"{_reason(error)}"
        ) from error
    try:
        document = parse_json_document(text)
    except DuplicateMemberError as error:
        raise RecordError(
            f"the landing record carries the member {_shown(error.name)} more than "
            f"once: {_path_shown(path)}; one value per member is required"
        ) from error
    except UnparsableDocumentError as error:
        raise RecordError(
            f"the landing record is not a document this tool parses: "
            f"{_path_shown(path)}: {error.reason}; the landed record is one flat JSON "
            "object of the 17 keys the landing contract fixes"
        ) from error
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
            f"the landing record carries {_json_shape(document)} at its top level: "
            f"{_path_shown(path)}; one JSON object is required"
        )
    return document


def load_schema(path: Path = DEFAULT_SCHEMA) -> Mapping[str, Any]:
    """Return the landing schema document read from ``path``.

    The document is returned as parsed; no constraint of it is restated in this module.
    A member name that repeats at any nesting level of the schema is refused and named.

    Raises ``SchemaError`` when the file is missing, empty, larger than
    ``MAX_SCHEMA_BYTES``, not valid UTF-8, not well-formed JSON, nests deeper than
    ``MAX_JSON_NESTING_DEPTH``, carries a value the parser refuses, carries a repeated
    member name, or is not a JSON object.
    """
    try:
        raw = _read_bounded_bytes(path, MAX_SCHEMA_BYTES, "landing schema")
    except RecordError as error:
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

    The checker carries the dialect's own ``date`` checker, which accepts a calendar
    date and rejects a value such as 2026-99-99 that a date pattern alone admits, and a
    ``genapp-timestamp`` checker parsing the exact ``TIMESTAMP_FORMAT`` representation
    the landing contract carries. A non-string instance passes both, as a format
    assertion applies to strings only.

    Raises ``SchemaError`` when the installed library publishes no ``date`` checker,
    since the schema's date assertions would otherwise be annotations that assert
    nothing.
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

    ``schema`` must declare the 2020-12 dialect in ``$schema``, which is the dialect
    the returned validator applies, and must itself satisfy that dialect's
    meta-schema. ``path`` names the schema in any diagnostic. The validator carries the
    checker ``build_format_checker`` returns, so every ``format`` the schema declares is
    asserted rather than annotated.

    The returned validator asserts the ``format`` keyword rather than treating it as an
    annotation, so a value the landing schema declares as a date is held to the calendar
    as well as to its written shape and a value such as ``2026-02-31`` is refused. The
    timestamp-carrying values are parsed separately, by ``confirm_calendar_values``,
    because their written form carries no UTC offset and no format keyword of this
    dialect describes it.

    Raises ``SchemaError`` when the declared dialect is absent or differs from the one
    applied, when the document is not a valid schema, or when the format checker cannot
    be built.
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


def _declared_shown(validator_value: Any) -> str:
    """Return the schema value one keyword declares, as one bounded JSON fragment.

    The fragment is schema text rather than record content, so it is reported whether
    or not record values are shown.
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
    declare. Both are member names, which are part of the landing contract rather than
    landed values. Every other keyword yields an empty fragment.
    """
    instance = error.instance
    if not isinstance(instance, Mapping):
        return ""
    if error.validator == "required" and isinstance(error.validator_value, list):
        return _names_shown(
            [str(name) for name in error.validator_value if name not in instance]
        )
    if error.validator == "additionalProperties":
        declared = (
            error.schema.get("properties", {})
            if isinstance(error.schema, Mapping)
            else {}
        )
        return _names_shown(
            sorted(str(name) for name in instance if name not in declared)
        )
    return ""


def _violation(error: jsonschema.exceptions.ValidationError) -> str:
    """Return one schema violation as a pointer, the breached constraint and a shape.

    The fragment names the JSON Pointer of the rejected value, the schema keyword that
    rejected it, the value the schema declares for that keyword, the property names the
    keyword is about where it has any, and the JSON type and size of the rejected value.
    The library's own message is used only when record values are shown, since it embeds
    the value it rejected.
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


def _counted(count: int, noun: str) -> str:
    """Return ``count`` and ``noun``, with the noun pluralised by an 's' when needed."""
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _json_shape(value: Any) -> str:
    """Return the JSON type of ``value``, and its length where that carries no content.

    A string is described by its type and character count, an array and an object by
    their element and member counts, and every other value by its JSON type alone. No
    character of a string, no element of an array and no member name of an object is
    rendered, so the description of a value never carries the value.
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


def validate_record(
    record: Mapping[str, Any],
    validator: Draft202012Validator,
    path: Path,
    limit: int = MAX_REPORTED_SCHEMA_ERRORS,
) -> None:
    """Confirm ``record`` satisfies the landing schema, reporting every violation.

    Every constraint the schema declares is applied, including its enumerations,
    lengths, patterns and semantic formats. Violations are reported in JSON Pointer and
    keyword order, at most ``limit`` of them, with the number withheld recorded when
    there are more. Violations that render identically - the same JSON Pointer, the same
    breached keyword and the same message - are reported once, and both ``limit`` and
    the withheld count are applied to the violations that remain, so a record omitting
    several landed keys carries one paragraph for the keyword it breached while every
    violation that reads differently is reported. ``path`` names the record in the
    diagnostic. Returns None when the record satisfies the schema.

    Raises ``RecordError`` carrying the violations when it does not.
    """
    errors = sorted(
        validator.iter_errors(record),
        key=lambda error: (
            _json_pointer(error.absolute_path),
            str(error.validator),
        ),
    )
    if not errors:
        return
    violations: list[str] = []
    rendered: set[tuple[str, str, str]] = set()
    for error in errors:
        message = _violation(error)
        marker = (_json_pointer(error.absolute_path), str(error.validator), message)
        if marker in rendered:
            continue
        rendered.add(marker)
        violations.append(message)
    reported = "; ".join(violations[:limit])
    withheld = len(violations) - min(len(violations), limit)
    if withheld:
        reported = f"{reported}; (+{withheld} further violations)"
    raise RecordError(
        f"the landing record does not satisfy the landing schema: "
        f"{_path_shown(path)}: {reported}"
    )


def confirm_control_free_values(record: Mapping[str, Any], path: Path) -> None:
    """Confirm no value of ``record`` carries a control character, and return None.

    Every string value the record carries is scanned against ``_CONTROL_CHARACTERS``,
    which is the C0 control characters, DEL and the C1 control characters, and the scan
    covers the whole value: a line feed or carriage return at the end of a value is
    refused along with one inside it, and a NUL, tab or DEL is refused wherever it sits.
    A value that is not a string carries no character and is passed over, having already
    been reported by the schema keyword that rejects it. The keys are scanned in the
    order the record carries them, so the key named is the first one carrying such a
    character.

    The landing schema declares the same rule, holding each string-valued property to a
    pattern or an enumeration closed at both ends of the value; this scan applies that
    rule to the parsed document again, before the bytes are uploaded.

    Raises ``RecordError`` naming the key, the position and the escaped character when
    one carries a control character, before any client exists and before any byte
    reaches the network.
    """
    for name, value in record.items():
        if not isinstance(value, str):
            continue
        found = _CONTROL_CHARACTERS.search(value)
        if found is None:
            continue
        raise RecordError(
            f"the landing record carries the control character "
            f"{_shown(_escaped_character(found.group()))} at position "
            f"{found.start()} of {_shown(str(name))}: {_path_shown(path)}; a landed "
            f"value carries printable characters alone"
        )


def confirm_calendar_values(record: Mapping[str, Any], path: Path) -> None:
    """Confirm every date and the timestamp of ``record`` name a real day and moment.

    Each key of ``DATE_FIELDS`` that carries a value is parsed with
    ``datetime.date.fromisoformat`` and must round-trip to the same text, so a value
    written in another ISO 8601 form is refused along with one that names no day. The
    ``TIMESTAMP_FIELD`` value is parsed with ``TIMESTAMP_PATTERN`` and must round-trip
    the same way, which asserts the calendar and clock values the schema's pattern can
    only shape. A null date is accepted, since the landing contract carries a blank
    window as null. Returns None when every value names a real day and moment.

    Raises ``RecordError`` naming the key and the value when one does not, before any
    client exists and before any byte reaches the network.
    """
    for name in DATE_FIELDS:
        value = record.get(name)
        if value is None:
            continue
        if not isinstance(value, str):
            raise RecordError(
                f"the landing record carries {_display(value)} as {_shown(name)}: "
                f"{_path_shown(path)}; a date written {DATE_FORM} or null is required"
            )
        try:
            parsed_date = datetime.date.fromisoformat(value)
        except ValueError as error:
            raise RecordError(
                f"the landing record carries {_shown(value)} as {_shown(name)}: "
                f"{_path_shown(path)}; it is not a calendar date written {DATE_FORM}: "
                f"{_reason(error)}"
            ) from error
        if parsed_date.isoformat() != value:
            raise RecordError(
                f"the landing record carries {_shown(value)} as {_shown(name)}: "
                f"{_path_shown(path)}; it is not written {DATE_FORM}, whose form for "
                f"that date is {_shown(parsed_date.isoformat())}"
            )
    carried = record.get(TIMESTAMP_FIELD)
    if not isinstance(carried, str):
        raise RecordError(
            f"the landing record carries {_display(carried)} as "
            f"{_shown(TIMESTAMP_FIELD)}: {_path_shown(path)}; a timestamp written "
            f"{TIMESTAMP_FORM} is required"
        )
    try:
        moment = datetime.datetime.strptime(carried, TIMESTAMP_PATTERN)
    except ValueError as error:
        raise RecordError(
            f"the landing record carries {_shown(carried)} as "
            f"{_shown(TIMESTAMP_FIELD)}: {_path_shown(path)}; it is not a timestamp "
            f"written {TIMESTAMP_FORM}: {_reason(error)}"
        ) from error
    normalised = moment.isoformat(
        sep=TIMESTAMP_OUTPUT_SEPARATOR, timespec=TIMESTAMP_OUTPUT_PRECISION
    )
    if normalised != carried:
        raise RecordError(
            f"the landing record carries {_shown(carried)} as "
            f"{_shown(TIMESTAMP_FIELD)}: {_path_shown(path)}; it is not written "
            f"{TIMESTAMP_FORM}, whose form for that moment is {_shown(normalised)}"
        )


def confirm_product_premium_allocation(
    record: Mapping[str, Any], path: Path
) -> None:
    """Confirm the amounts ``record`` carries are the ones its policy type populates.

    ``PREMIUM_ALLOCATION`` names, for the policy type the record carries, which of
    ``AMOUNT_FIELDS`` hold a value: the payment amount on every policy type, the motor
    premium on M, the four commercial premiums on C, and no product premium on E or H.
    Each amount that policy type populates must carry a string and each amount it does
    not must carry null; a zero does not stand in for an inapplicable premium. The
    landing schema declares the same allocation in its allOf block, and this check
    applies it to the parsed document again. Returns None when the record carries
    exactly the amounts its policy type populates.

    Raises ``RecordError`` naming the amount key and the policy type when one carries a
    value the policy type does not populate or omits one it does, and when the record
    carries no policy type this allocation is recorded for, before any client exists and
    before any byte reaches the network.
    """
    policy_type = record.get(POLICY_TYPE_FIELD)
    if not isinstance(policy_type, str) or policy_type not in PREMIUM_ALLOCATION:
        raise RecordError(
            f"the landing record carries {_value_display(policy_type)} as "
            f"{_shown(POLICY_TYPE_FIELD)}: {_path_shown(path)}; the product premium "
            f"allocation is recorded for "
            f"{_quote_all(sorted(PREMIUM_ALLOCATION))} alone"
        )
    populated = PREMIUM_ALLOCATION[policy_type]
    for name in AMOUNT_FIELDS:
        value = record.get(name)
        if name in populated:
            if not isinstance(value, str):
                raise RecordError(
                    f"the landing record carries {_json_shape(value)} for "
                    f"{_shown(name)} while its {_shown(POLICY_TYPE_FIELD)} is "
                    f"{_shown(policy_type)}: {_path_shown(path)}; that policy type "
                    f"populates it"
                )
            continue
        if value is not None:
            raise RecordError(
                f"the landing record carries {_value_display(value)} for "
                f"{_shown(name)} while its {_shown(POLICY_TYPE_FIELD)} is "
                f"{_shown(policy_type)}: {_path_shown(path)}; that policy type "
                f"populates {_names_shown(populated)}, and every other amount is null"
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
            f"the landing record carries {_value_display(carried)} for "
            f"{_shown(SOURCE_SYSTEM_KEY_FIELD)}: {_path_shown(path)}; a string is "
            "required"
        )
    if carried != resolved:
        raise RecordError(
            f"the landing record carries {_value(carried)} for "
            f"{_shown(SOURCE_SYSTEM_KEY_FIELD)} while the landing prefix would carry "
            f"{_shown(resolved)}: {_path_shown(path)}; the two must agree"
        )



# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


def _from_environment(names: Sequence[str]) -> tuple[str | None, str | None]:
    """Return the first value among ``names`` that carries content, and its name.

    A variable that is set to the empty string or to whitespace alone counts as unset
    and is passed over, so the documented default applies to it; that is the empty-value
    resolution every command-line tool of this bridge applies. The value carried is
    returned exactly as the environment holds it: nothing is trimmed, so a setting that
    would be invalid with surrounding whitespace is reported rather than silently
    repaired. Returns ``(None, None)`` when no name carries content. Only the name is
    ever quoted in a diagnostic.
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

    The resolved name is held to the general-purpose bucket naming rules, which every
    addressable bucket satisfies whichever endpoint serves it: ``MIN_BUCKET_CHARACTERS``
    to ``MAX_BUCKET_CHARACTERS`` characters drawn from lowercase letters, digits, dot
    and hyphen, beginning and ending with a letter or a digit, carrying no two adjacent
    dots, not written as an IPv4 address, and carrying none of the prefixes or suffixes
    the service reserves. A name outside those rules names no bucket that could be
    addressed, so it is refused before a request is sent rather than reported as a
    failed request; the same rules apply in both run modes, so a name that works
    against the local endpoint works against AWS S3 as well.

    Raises ``ConfigurationError`` when neither setting carries a value, or when the
    resolved name breaches any of those rules.
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
            f"the bucket name from {origin} is not a general-purpose bucket name: "
            f"{_shown(value)}; it carries lowercase letters, digits, dot and hyphen "
            "only, and begins and ends with a letter or a digit"
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
    """Return the entity element of the landing prefix, which is ``LANDING_ENTITY``.

    ``supplied`` is the ``--entity`` value. Omitted, the literal applies; supplied, it
    must repeat that literal, so a validated record cannot land outside the canonical
    policy-issue prefix.

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


def part_number_text(part: int) -> str:
    """Return ``part`` as the digits the object name of that part carries.

    The value is written zero-padded to ``PART_NUMBER_DIGITS`` digits, so every object
    name of a landing prefix carries the same width and sorts in part order.

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


def manifest_object_name(part: int = DEFAULT_PART_NUMBER) -> str:
    """Return the object name of the COPY manifest of ``part``.

    Raises ``ConfigurationError`` when ``part`` is not an accepted part number.
    """
    return MANIFEST_OBJECT_NAME_TEMPLATE.format(part=part_number_text(part))


def resolve_part(supplied: str | None) -> int:
    """Return the part element of the landed object name, as a number.

    ``supplied`` is the ``--part`` value, written as 1 to ``PART_NUMBER_DIGITS``
    decimal digits with or without leading zeros; ``DEFAULT_PART_NUMBER`` applies when
    it is absent, and the key a run that names no part writes is therefore the one
    ending in ``OBJECT_NAME``. The number reaches the object name zero-padded to
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


def resolve_iam_role(supplied: str | None) -> str:
    """Return the IAM role ARN written into the rendered Redshift load.

    ``supplied`` is the ``--iam-role`` value and the ``REDSHIFT_IAM_ROLE`` environment
    variable is consulted when it is absent. The value's shape is confirmed when it is
    substituted.

    Raises ``ConfigurationError`` when neither carries a value.
    """
    value, _ = _resolved(supplied, "--iam-role", (IAM_ROLE_VARIABLE,))
    if value is None:
        raise ConfigurationError(
            "no IAM role is set: supply --iam-role or set the "
            f"{IAM_ROLE_VARIABLE} environment variable to the ARN of the role that "
            "authorises the COPY to read the bucket; this tool creates none"
        )
    return value


def require_region(resolved: str | None) -> str:
    """Return ``resolved`` confirmed present, for a mode that resolves none itself.

    Raises ``ConfigurationError`` naming the settings to supply when ``resolved`` is
    None.
    """
    if resolved is None:
        raise ConfigurationError(
            f"{_missing_region_message()}. The rendered load names the bucket's region "
            "and no session is created to resolve one"
        )
    return resolved


def resolve_template_path(supplied: Path | None) -> Path:
    """Return the Redshift load template to substitute.

    ``supplied`` is the ``--template`` value and ``DEFAULT_REDSHIFT_TEMPLATE`` applies
    when it is absent.
    """
    return DEFAULT_REDSHIFT_TEMPLATE if supplied is None else supplied


def _is_loopback_host(host: str) -> bool:
    """Return whether ``host`` is a loopback literal or exactly the loopback name.

    A host is accepted for the literal it is: an IPv4 address in 127.0.0.0/8, the IPv6
    address ::1 or any other loopback IPv6 literal, or ``LOOPBACK_HOST_NAME`` compared
    without case. No name is resolved, so a name that resolves to a loopback address is
    not a loopback host under this test.
    """
    if host.casefold() == LOOPBACK_HOST_NAME:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _refuse_endpoint(origin: str, fault: str) -> NoReturn:
    """Raise ``ConfigurationError`` reporting ``fault`` without echoing the endpoint.

    The endpoint is a setting this tool never discloses, so the diagnostic names where
    the value came from and what is accepted, never the value itself.
    """
    raise ConfigurationError(
        f"the endpoint from {origin} is not accepted: {fault}. A local endpoint is "
        f"{' or '.join(ACCEPTED_ENDPOINT_SCHEMES)} on a loopback host "
        f"(127.0.0.0/8, ::1 or {LOOPBACK_HOST_NAME}) with an explicit port of "
        f"{ENDPOINT_PORT_FLOOR} or above, no embedded credentials, no query, no "
        "fragment and no path; leave the setting unset to address AWS S3. The value is "
        "not echoed"
    )


def require_loopback_endpoint(value: str, origin: str) -> str:
    """Return ``value`` confirmed to be a local-substitute S3 endpoint.

    An accepted endpoint holds at most ``MAX_ENDPOINT_CHARACTERS`` characters and
    carries a scheme from ``ACCEPTED_ENDPOINT_SCHEMES``, a host that
    ``_is_loopback_host`` accepts, an explicit port at or above
    ``ENDPOINT_PORT_FLOOR``, no userinfo, a path in ``ACCEPTED_ENDPOINT_PATHS``, no
    query and no fragment. Every port from that floor up is accepted, so several local
    endpoints can run side by side, and no override reaches a privileged loopback
    service. Every check runs before any client, credential or request exists, and each
    names the element it refused without echoing the value.

    Raises ``ConfigurationError`` naming the rejected element for every other value.
    """
    if len(value) > MAX_ENDPOINT_CHARACTERS:
        _refuse_endpoint(
            origin,
            f"it holds {len(value)} characters, and at most "
            f"{MAX_ENDPOINT_CHARACTERS} are accepted",
        )
    if any(character.isspace() for character in value) or _CONTROL_CHARACTERS.search(
        value
    ):
        _refuse_endpoint(origin, "it carries whitespace or a control character")
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        _refuse_endpoint(origin, "it cannot be parsed as a URL")
    if parsed.scheme not in ACCEPTED_ENDPOINT_SCHEMES:
        _refuse_endpoint(
            origin,
            f"its scheme is {_shown(parsed.scheme) if parsed.scheme else 'absent'}",
        )
    if "@" in parsed.netloc:
        _refuse_endpoint(origin, "it carries embedded credentials before the host")
    if parsed.path not in ACCEPTED_ENDPOINT_PATHS:
        _refuse_endpoint(origin, "it carries a path")
    if parsed.query:
        _refuse_endpoint(origin, "it carries a query")
    if parsed.fragment:
        _refuse_endpoint(origin, "it carries a fragment")
    try:
        host = parsed.hostname
        port = parsed.port
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
    environment variable is consulted when it is absent. A returned value directs the
    client at that endpoint and is a local substitute confirmed by
    ``require_loopback_endpoint``; None leaves the client addressing AWS S3, where the
    client resolves the endpoint itself and ignores every endpoint the environment or a
    profile configures. The origin names where the value came from, so
    ``confirm_run_mode_endpoint`` can report the setting that selected a branch of the
    bridge without echoing the endpoint.

    Raises ``ConfigurationError`` naming the rejected element when the resolved value
    is not an accepted local-substitute endpoint.
    """
    value, origin = _resolved(supplied, "--endpoint-url", (ENDPOINT_URL_VARIABLE,))
    if value is None:
        return None, origin
    return require_loopback_endpoint(value, origin), origin


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


def resolve_run_mode(supplied: str | None) -> tuple[str, str]:
    """Return the run mode this run addresses and the origin it came from.

    ``supplied`` is the ``--run-mode`` value, which wins whenever it is present, and the
    ``DBT_TARGET`` environment variable is consulted when it is absent;
    ``DEFAULT_RUN_MODE`` applies when neither carries a value. The accepted values are
    ``RUN_MODES``, which are the output names of
    modernization/dbt/genapp_rqi/profiles.example.yml, so the one setting that selects
    the dbt output also selects the branch this tool and
    modernization/landing/load_local.py address.

    Raises ``ConfigurationError`` when the resolved value is not one of ``RUN_MODES``. A
    value outside that set is never mapped onto the nearest one: a misspelled setting
    would otherwise decide silently whether this run addresses the local substitute or
    AWS S3.
    """
    value, origin = _resolved(supplied, "--run-mode", (RUN_MODE_VARIABLE,))
    if value is None:
        return DEFAULT_RUN_MODE, "the built-in default"
    if value not in RUN_MODES:
        raise ConfigurationError(
            f"the run mode from {origin} is {_shown(value)}: "
            f"{_quote_all(RUN_MODES)} are accepted; {_shown(RUN_MODE_LOCAL)} addresses "
            f"the local substitute and {_shown(RUN_MODE_REAL)} addresses AWS S3"
        )
    return value, origin


def confirm_run_mode_endpoint(
    run_mode: str, run_mode_origin: str, endpoint_url: str | None, endpoint_origin: str
) -> None:
    """Confirm the resolved endpoint is the one the resolved run mode requires.

    ``RUN_MODE_LOCAL`` addresses the local substitute, so it requires an endpoint: with
    none resolved the run would address AWS S3 while every other step of the run
    addressed the local branch. ``RUN_MODE_REAL`` addresses AWS S3, so it forbids one:
    with an endpoint resolved the run would land the object at the local substitute
    while reporting the real branch. Returns None when the two agree.

    This is checked before a session, a client or a credential exists, so a conflicting
    pair is reported without a request being signed or sent.

    Raises ``ConfigurationError`` naming both settings and where each came from when
    they do not agree. No endpoint value reaches the diagnostic.
    """
    if run_mode == RUN_MODE_LOCAL and endpoint_url is None:
        raise ConfigurationError(
            f"run mode {_shown(run_mode)} from {run_mode_origin} addresses the local "
            f"substitute, but no endpoint is set: supply --endpoint-url or set the "
            f"{ENDPOINT_URL_VARIABLE} environment variable to the loopback endpoint "
            f"serving it, or select run mode {_shown(RUN_MODE_REAL)} to address AWS S3"
        )
    if run_mode == RUN_MODE_REAL and endpoint_url is not None:
        raise ConfigurationError(
            f"run mode {_shown(run_mode)} from {run_mode_origin} addresses AWS S3, but "
            f"an endpoint is set from {endpoint_origin}; unset it to address AWS S3, "
            f"or select run mode {_shown(RUN_MODE_LOCAL)} to address the local "
            "substitute. The endpoint value is not echoed"
        )


def confirm_redshift_probe_branch(
    run_mode: str, run_mode_origin: str, endpoint_url: str | None, endpoint_origin: str
) -> None:
    """Confirm the resolved branch is the real target the Redshift probe addresses.

    The Redshift probe is the second half of the precondition gate, and the gate's
    real branch is the one this tool addresses with no endpoint override and run mode
    ``RUN_MODE_REAL``. A resolved endpoint serves the local substitute, and run mode
    ``RUN_MODE_LOCAL`` carries no Redshift target at all: either of them alongside
    this probe is a run whose settings describe two different branches, and each is
    refused by the setting it came from before a socket is opened, so no run can
    report a local substitute as a Redshift target that answered.

    Returns None when the resolved branch is the real target.

    Raises ``ConfigurationError`` naming the setting and where it came from when it is
    not. No endpoint value reaches the diagnostic.
    """
    if endpoint_url is not None:
        raise ConfigurationError(
            f"an endpoint is set from {endpoint_origin}, which serves the local "
            "substitute, and --probe-redshift addresses Amazon Redshift: unset that "
            "setting to probe the real target, and probe the local substitute with "
            "--probe instead. The endpoint value is not echoed"
        )
    if run_mode != RUN_MODE_REAL:
        raise ConfigurationError(
            f"run mode {_shown(run_mode)} from {run_mode_origin} addresses the local "
            "substitute, which carries no Redshift target: select run mode "
            f"{_shown(RUN_MODE_REAL)} through --run-mode or the "
            f"{RUN_MODE_VARIABLE} environment variable to probe the real target"
        )


class RedshiftSettings(NamedTuple):
    """The resolved Redshift connection settings one probe addresses.

    Each value is the one the environment carried, held to its shape by
    ``resolve_redshift_settings``. No value of this tuple reaches the output on any
    path: ``__repr__`` carries none of them, so neither does a diagnostic that
    formats this tuple, and ``redacted_values`` names the values replaced out of a
    reason the driver supplied.
    """

    host: str
    port: int
    database: str
    user: str
    password: str
    schema: str
    connect_timeout: int

    def __repr__(self) -> str:
        """Return a representation carrying no value of these settings."""
        return f"RedshiftSettings(<{len(self._fields)} settings resolved>)"

    def redacted_values(self) -> tuple[str, ...]:
        """Return the values replaced out of any text the driver supplied."""
        return (self.password, self.host, self.user, self.database, self.schema)


def _redshift_origin(variable: str) -> str:
    """Return the phrase naming the environment variable one setting came from."""
    return f"the {variable} environment variable"


def _require_redshift_setting(variable: str, what: str) -> str:
    """Return the value ``variable`` carries for a setting that has no default.

    The empty-value resolution is the one every setting of this tool applies: a
    variable holding the empty string or whitespace alone counts as unset, and a
    setting with no default is then absent rather than empty.

    Raises ``ConfigurationError`` naming the variable to set and what it carries.
    """
    value, name = _from_environment((variable,))
    if value is None or name is None:
        raise ConfigurationError(
            f"no Redshift {what} is set: set {variable} in the environment. It is the "
            f"same variable the redshift output of {REDSHIFT_PROFILE_DOCUMENT} reads, "
            "so one setting serves the probe and the run it gates"
        )
    return value


def _shaped_redshift_setting(
    value: str, variable: str, what: str, shape: re.Pattern[str], limit: int
) -> str:
    """Return ``value`` confirmed usable as one Redshift connection parameter.

    The value is not echoed: a host names the target, a user and a database name the
    account being addressed, and a diagnostic carries the variable to correct and what
    it must hold instead.

    Raises ``ConfigurationError`` when ``value`` is longer than ``limit`` or lies
    outside ``shape``.
    """
    origin = _redshift_origin(variable)
    if len(value) > limit:
        raise ConfigurationError(
            f"the Redshift {what} from {origin} holds {len(value)} characters; at most "
            f"{limit} are accepted. The value is not echoed"
        )
    if not shape.fullmatch(value):
        raise ConfigurationError(
            f"the Redshift {what} from {origin} is not accepted: it carries a "
            "character, a leading or trailing separator or whitespace that no "
            f"{what} carries. A {what} is written on its own, with no scheme, port, "
            "path, query or user information. The value is not echoed"
        )
    return value


def _bounded_redshift_number(
    variable: str, what: str, default: int, minimum: int, maximum: int
) -> int:
    """Return the whole number ``variable`` carries, or ``default`` when unset.

    A variable holding the empty string or whitespace alone counts as unset, so the
    default applies to it. A value carrying content is accepted only as decimal digits
    alone naming a number between ``minimum`` and ``maximum``: text, a signed value, a
    fractional value and a number outside those bounds are each refused rather than
    converted, which is the resolution the redshift output of
    modernization/dbt/genapp_rqi/profiles.example.yml applies to the same variable.
    The refused number is quoted, since it is neither a credential nor an address.

    Raises ``ConfigurationError`` naming the variable and the accepted values.
    """
    value, name = _from_environment((variable,))
    if value is None or name is None:
        return default
    if not _REDSHIFT_NUMBER_SHAPE.fullmatch(value) or not (
        minimum <= int(value) <= maximum
    ):
        raise ConfigurationError(
            f"the Redshift {what} from {_redshift_origin(variable)} is not a decimal "
            f"whole number between {minimum} and {maximum}: {_shown(value)}; leave the "
            f"variable unset for the default of {default}"
        )
    return int(value)


def resolve_redshift_settings() -> RedshiftSettings:
    """Return the Redshift connection settings the probe addresses.

    Every value comes from the environment, from the variables the redshift output of
    modernization/dbt/genapp_rqi/profiles.example.yml reads, so the probe and the run
    it gates are configured by one set of settings and no credential is passed on a
    command line where every process on the host could read it. ``REDSHIFT_PORT``
    defaults to ``DEFAULT_REDSHIFT_PORT`` and ``REDSHIFT_CONNECT_TIMEOUT`` to
    ``DEFAULT_REDSHIFT_CONNECT_TIMEOUT``; the host, user, password, database and
    schema carry no default and are required. Every value is held to its shape and
    its bounds here, before the driver is imported and before a socket is opened.

    The host is required to be a DNS name or an IPv4 literal that is not a loopback
    address: a loopback host serves something on this machine, which cannot be the
    Amazon Redshift target this probe reports on.

    No resolved value is echoed. A diagnostic names the variable to correct and what
    it has to carry, and for the two numeric settings the number that was refused.

    Raises ``ConfigurationError`` naming the variable when a required setting is
    absent, when a value lies outside its shape or bounds, or when the host names a
    loopback address.
    """
    host = _shaped_redshift_setting(
        _require_redshift_setting(REDSHIFT_HOST_VARIABLE, "host"),
        REDSHIFT_HOST_VARIABLE,
        "host",
        _REDSHIFT_HOST_SHAPE,
        MAX_REDSHIFT_HOST_CHARACTERS,
    )
    if _is_loopback_host(host):
        raise ConfigurationError(
            f"the Redshift host from {_redshift_origin(REDSHIFT_HOST_VARIABLE)} names "
            "a loopback address, which serves this machine rather than Amazon "
            "Redshift; this probe reports on the real target alone, and the local "
            "substitute is probed with --probe against its own endpoint. The value is "
            "not echoed"
        )
    user = _shaped_redshift_setting(
        _require_redshift_setting(REDSHIFT_USER_VARIABLE, "user"),
        REDSHIFT_USER_VARIABLE,
        "user",
        _REDSHIFT_NAME_SHAPE,
        MAX_REDSHIFT_NAME_CHARACTERS,
    )
    password = _require_redshift_setting(REDSHIFT_PASSWORD_VARIABLE, "password")
    if len(password) > MAX_REDSHIFT_PASSWORD_CHARACTERS:
        raise ConfigurationError(
            f"the Redshift password from "
            f"{_redshift_origin(REDSHIFT_PASSWORD_VARIABLE)} holds "
            f"{len(password)} characters; at most {MAX_REDSHIFT_PASSWORD_CHARACTERS} "
            "are accepted. The value is never echoed"
        )
    if _CONTROL_CHARACTERS.search(password):
        raise ConfigurationError(
            f"the Redshift password from "
            f"{_redshift_origin(REDSHIFT_PASSWORD_VARIABLE)} carries a control "
            "character, which no password of a connection parameter carries. The "
            "value is never echoed"
        )
    database = _shaped_redshift_setting(
        _require_redshift_setting(REDSHIFT_DATABASE_VARIABLE, "database"),
        REDSHIFT_DATABASE_VARIABLE,
        "database",
        _REDSHIFT_NAME_SHAPE,
        MAX_REDSHIFT_NAME_CHARACTERS,
    )
    schema = _shaped_redshift_setting(
        _require_redshift_setting(REDSHIFT_SCHEMA_VARIABLE, "schema"),
        REDSHIFT_SCHEMA_VARIABLE,
        "schema",
        _REDSHIFT_NAME_SHAPE,
        MAX_REDSHIFT_NAME_CHARACTERS,
    )
    port = _bounded_redshift_number(
        REDSHIFT_PORT_VARIABLE,
        "port",
        DEFAULT_REDSHIFT_PORT,
        MIN_PORT_NUMBER,
        MAX_PORT_NUMBER,
    )
    connect_timeout = _bounded_redshift_number(
        REDSHIFT_CONNECT_TIMEOUT_VARIABLE,
        "connect timeout in seconds",
        DEFAULT_REDSHIFT_CONNECT_TIMEOUT,
        MIN_CONNECT_TIMEOUT_SECONDS,
        MAX_CONNECT_TIMEOUT_SECONDS,
    )
    return RedshiftSettings(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        schema=schema,
        connect_timeout=connect_timeout,
    )


# ---------------------------------------------------------------------------
# Key construction
# ---------------------------------------------------------------------------


def build_landing_prefix(
    source_system_key: str, entity: str, extract_date: datetime.date
) -> str:
    """Return the landing key prefix of one extract, ending in ``KEY_SEPARATOR``.

    The prefix is ``LANDING_KEY_ROOT`` followed by one Hive-style ``field=value``
    segment per entry of ``PARTITION_FIELDS``, in that order, with no leading
    separator, no empty segment and no percent-encoding of the equals sign. The date is
    written as ``EXTRACT_DATE_FORM``. ``entity`` must be ``LANDING_ENTITY``, so every
    prefix this function returns addresses the canonical policy-issue prefix. Every
    object name of one extract sits directly under it.

    Raises ``ConfigurationError`` when a supplied value cannot form one path segment or
    when ``entity`` is not ``LANDING_ENTITY``.
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
    return KEY_SEPARATOR.join(segments) + KEY_SEPARATOR


def build_landing_key(
    source_system_key: str,
    entity: str,
    extract_date: datetime.date,
    part: int = DEFAULT_PART_NUMBER,
) -> str:
    """Return the landing object key for one part of one extract.

    The key is

        landing/source_system_key=<KEY>/entity=policy_issue/extract_date=<YYYY-MM-DD>/part-<NNNN>.json

    which is ``build_landing_prefix`` followed by the object name of ``part``. With no
    part supplied the name is ``OBJECT_NAME``, so a caller that names no part addresses
    the key this contract has always fixed; a second part of the same source system,
    entity and extract date addresses its own key beside it rather than replacing it.

    Raises ``ConfigurationError`` when a supplied value cannot form one path segment,
    when ``entity`` is not ``LANDING_ENTITY``, or when ``part`` is not an accepted part
    number.
    """
    prefix = build_landing_prefix(source_system_key, entity, extract_date)
    return f"{prefix}{object_name(part)}"


def build_object_uri(bucket: str, key: str) -> str:
    """Return the ``s3://`` URI naming the object ``key`` in ``bucket``."""
    return f"{SERVICE_NAME}://{bucket}{KEY_SEPARATOR}{key}"


def build_manifest_key(
    source_system_key: str,
    entity: str,
    extract_date: datetime.date,
    part: int = DEFAULT_PART_NUMBER,
) -> str:
    """Return the key of the COPY manifest naming the landed object of one part.

    The manifest sits beside the landed object under the same landing prefix, carrying
    ``manifest_object_name`` of the same part in place of ``object_name``, so each
    landed part is bound by its own manifest and a COPY reading one manifest reads one
    object.

    Raises ``ConfigurationError`` when a supplied value cannot form one path segment or
    when ``part`` is not an accepted part number.
    """
    prefix = build_landing_prefix(source_system_key, entity, extract_date)
    return f"{prefix}{manifest_object_name(part)}"


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
    response after ``READ_TIMEOUT_SECONDS``. ``total_max_attempts`` bounds the calls one
    request makes at ``MAX_ATTEMPTS`` including the first, which is the bound
    ``max_attempts`` would have exceeded by one, so an unreachable target cannot hold
    the caller open indefinitely and the bound the code states is the bound the client
    applies. Every endpoint configured in the environment or in a profile, including
    AWS_ENDPOINT_URL and AWS_ENDPOINT_URL_S3, is ignored: the only endpoint that can
    apply is the one ``resolve_endpoint_url`` accepted and this module passes to the
    client explicitly.
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


def _failure_for(error: BaseException, bucket: str, action: str) -> LandingError:
    """Return the diagnostic for an S3 ``action`` on ``bucket`` that did not succeed.

    A credential problem becomes a ``ConfigurationError`` naming the settings to
    supply; every other failure becomes an ``AccessError``. The returned diagnostic
    carries no credential or token value; a reason text the endpoint library supplied
    may name the endpoint it addressed, which is the setting the reader has to
    correct.
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


def confirm_credentials(session: boto3.session.Session) -> Any:
    """Confirm ``session`` resolves a usable set of credentials, and return them.

    The session's own providers do the resolving, so a variable whose name merely
    begins with AWS is never taken for a credential. An incomplete set surfaces as
    ``PartialCredentialsError`` from that resolution. The resolved credentials are
    returned so their provenance can be confirmed before a request is signed; no
    credential value is read beyond confirming one is present, and none is ever printed.

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
    return credentials


def confirm_credential_provenance(credentials: Any, endpoint_url: str | None) -> None:
    """Confirm the resolved credentials may be signed against the endpoint addressed.

    With no endpoint addressed the request goes to AWS S3, where every credential
    provider is appropriate, and this returns None. With a custom endpoint addressed the
    request goes to the loopback host serving the local substitute, and only credentials
    that came from the environment or were passed to the session directly are signed
    against it: those are the throwaway values a local endpoint is driven with. A
    credential resolved from a shared credentials file, a configured profile, single
    sign-on, an assumed role, container metadata or instance metadata belongs to a real
    account, and sending a request signed with it to a process listening on a local port
    would disclose that account's signature to whatever holds the port. Such a run is
    refused rather than downgraded. The method name is read from the credentials
    botocore resolved; no credential value is read or printed.

    Raises ``ConfigurationError`` naming the resolution method when the credentials did
    not come from an accepted provider.
    """
    if endpoint_url is None:
        return
    method = getattr(credentials, "method", None)
    if not isinstance(method, str) or not method:
        raise ConfigurationError(
            "the resolved credentials record no resolution method, so they cannot be "
            "confirmed as local-substitute credentials while a custom endpoint is "
            f"addressed: set {' and '.join(CREDENTIAL_VARIABLES)} in the environment "
            "for the local endpoint"
        )
    if method not in LOCAL_CREDENTIAL_METHODS:
        raise ConfigurationError(
            f"the resolved credentials came from {_shown(method)} while a custom "
            "endpoint is addressed: those credentials belong to a real account and are "
            "never signed against a local endpoint. Set "
            f"{' and '.join(CREDENTIAL_VARIABLES)} in the environment for the local "
            f"endpoint, which resolves as {_quote_all(LOCAL_CREDENTIAL_METHODS)}, or "
            "unset the endpoint to address AWS S3"
        )


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

    A session is created, its region is confirmed, its credentials are confirmed, their
    provenance is confirmed against the endpoint being addressed, and a client is built
    against ``endpoint_url`` when one was supplied. Nothing is requested from the service
    here and nothing is created, so a credential that may not be signed against the
    endpoint is refused before any request exists. The resolved region is noted on
    stderr; neither the endpoint nor any credential value is printed.

    Raises ``ConfigurationError`` naming the setting to supply when the region, the
    credentials or the client cannot be resolved, or when the resolved credentials may
    not be signed against the endpoint being addressed.
    """
    session = build_session(region)
    resolved_region = resolve_session_region(session)
    credentials = confirm_credentials(session)
    confirm_credential_provenance(credentials, endpoint_url)
    client = build_s3_client(session, endpoint_url)
    target = (
        "a loopback endpoint" if endpoint_url is not None else "AWS S3"
    )
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
    from ``build_probe_key`` unless ``probe_key`` names one, and the delete of that
    object is attempted in a finally block. Returning the key means the write and the
    delete both succeeded. A delete that does not succeed after a successful write
    leaves that one object on the bucket and raises, and its diagnostic names the key
    to remove; a delete that does not succeed after a failed write is reported as a
    warning naming the same key, and the write failure is the one raised. The probe key
    sits outside the landing prefix. Nothing is created beyond that one object and
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
                    cleanup_error,
                    bucket,
                    "delete the access probe object "
                    f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}, which the probe "
                    "wrote and which remains on the bucket for removal by hand",
                ) from cleanup_error
            _warn(
                f"the access probe object {_shown(key)} could not be deleted after the "
                f"write failed: {_reason(cleanup_error)}"
            )
    return key


def note_object_replaced(client: Any, bucket: str, key: str) -> bool:
    """Note that ``key`` already carries an object this landing replaces, and report it.

    One head request is made for ``key`` and nothing on the bucket is written, deleted
    or configured. When it answers, one warning line names the key, states that the
    object already there is replaced by this landing, and states that each record of one
    source system, entity and extract date is landed under its own part number. The line
    carries the key alone: no value the landing record carries, and no content of the
    object already there, reaches it.

    Returns True when the head request answered and the line was written, and False when
    it did not answer. No outcome of the head request reaches the caller as a failure -
    an absent object, a refused read, an endpoint that did not answer and any other
    outcome are all reported as False - so this call never turns a landing that would
    have succeeded into one that fails.
    """
    try:
        client.head_object(Bucket=bucket, Key=key)
    except Exception:  # noqa: BLE001 - reported as False, never as a landing failure
        return False
    _warn(
        f"the landing key {_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)} already "
        "carries an object, which this landing replaces; one key carries one object "
        "per source system, entity, extract date and part, so a second record of that "
        "source system and extract date is landed under its own --part number rather "
        "than over this key"
    )
    return True


def recorded_object_metadata(body: bytes) -> dict[str, str]:
    """Return the land-time identity written as user metadata of the landed object.

    The digest is the SHA-256 of ``body`` as 64 lower-case hexadecimal characters,
    which is the same digest ``object_identity`` records for the same bytes and the
    same form ``modernization/landing/load_redshift.sql`` documents for its
    OBJECT_SHA256 provenance line, and the byte count is the length of ``body`` in
    decimal digits. Both are values of ``body`` alone: no setting, credential,
    endpoint or record value reaches the metadata, so the object carries nothing a
    diagnostic would have to redact.
    """
    return {
        RECORDED_SHA256_METADATA: hashlib.sha256(body).hexdigest(),
        RECORDED_LENGTH_METADATA: str(len(body)),
    }


def put_record(client: Any, bucket: str, key: str, body: bytes) -> None:
    """Write ``body`` to ``key`` in ``bucket`` as one object, and return None.

    ``body`` is written exactly as given, with content type ``OBJECT_CONTENT_TYPE``, so
    the stored object is byte-identical to the record file the caller read. The one
    request also carries ``recorded_object_metadata`` of those bytes, so the object
    itself records the digest and byte count of what was landed and a loader can hold
    the bytes that arrive to the bytes that were validated. Recording it as metadata of
    this same PutObject keeps a landing at two objects and leaves the COPY manifest in
    the shape Amazon Redshift's manifest schema fixes. One object is written and nothing
    else on the bucket is read, written or configured.

    Raises ``AccessError`` when the write did not succeed, and ``ConfigurationError``
    when a credential setting is missing.
    """
    try:
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=OBJECT_CONTENT_TYPE,
            Metadata=recorded_object_metadata(body),
        )
    except (ClientError, BotoCoreError) as error:
        raise _failure_for(
            error, bucket, f"write the landing object {_shown(key)}"
        ) from error


def put_manifest(client: Any, bucket: str, key: str, body: bytes) -> None:
    """Write ``body`` to ``key`` in ``bucket`` as the COPY manifest, and return None.

    ``body`` is written exactly as given, with content type ``OBJECT_CONTENT_TYPE``, so
    the stored manifest is byte-identical to the document ``build_copy_manifest``
    returned for the same landed object. One object is written and nothing else on the
    bucket is read, written or configured. A write that does not succeed is reported
    with the whole manifest key, which the reader needs to place or remove the object
    by hand.

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
            error,
            bucket,
            f"write the COPY manifest {_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}",
        ) from error


# ---------------------------------------------------------------------------
# Redshift access probe
# ---------------------------------------------------------------------------


def _redshift_driver() -> Any:
    """Return the pinned redshift-connector module, imported on this call alone.

    The import happens here rather than at module level, so a landing run, a probe of
    the local substitute and a render load nothing this probe needs.

    Raises ``ConfigurationError`` when the pinned distribution is not installed.
    """
    try:
        import redshift_connector
    except ImportError as error:
        raise ConfigurationError(
            "the Redshift driver is not installed: install the pinned "
            "redshift-connector of modernization/requirements.txt into "
            f"modernization/.venv and run this probe through it: {_reason(error)}"
        ) from error
    return redshift_connector


def _redshift_reason(error: BaseException, settings: RedshiftSettings) -> str:
    """Return the reason ``error`` reported, carrying no resolved setting value.

    A driver diagnostic can quote the host it addressed, the database it opened or the
    user it authenticated as, and this tool discloses none of them, so every value
    ``redacted_values`` names is replaced before the text is bounded. Any URL the text
    carries is redacted as it is everywhere else in this tool.

    The replacement is one left-to-right pass over one alternation of the values,
    longest first, so a value that is a substring of another is replaced as part of the
    longer one and the placeholder this pass writes is never scanned again. Each value
    matches only where it is not surrounded by further identifier characters, so a
    one-character setting value is replaced where the driver quoted it as a value and
    not inside an unrelated word of the driver's own wording.
    """
    text = str(error) or _type_name(error)
    values = sorted({value for value in settings.redacted_values() if value}, key=len)
    if values:
        pattern = "|".join(
            rf"(?<![0-9A-Za-z_]){re.escape(value)}(?![0-9A-Za-z_])"
            for value in reversed(values)
        )
        text = re.sub(pattern, REDACTED_SETTING, text)
    return _escaped(_redacted(text), MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)


def _redshift_failure(
    error: BaseException, settings: RedshiftSettings, action: str
) -> LandingError:
    """Return the diagnostic for a Redshift ``action`` that did not succeed.

    Every driver failure is an ``AccessError``: an endpoint that does not resolve, a
    connection that is refused or times out, a certificate that does not verify and a
    credential the target rejected all leave this run without access to the target it
    addressed, which is the one thing the probe reports on.
    """
    return AccessError(f"cannot {action}: {_redshift_reason(error, settings)}")


def build_redshift_probe_relation() -> str:
    """Return the name of the temporary relation one write probe creates.

    The name carries ``REDSHIFT_PROBE_RELATION_TEMPLATE`` with a random token, so two
    probes never name the same relation, and it reaches the statement as SQL text
    rather than as a bound value, so it is confirmed usable as one unquoted SQL
    identifier first.

    Raises ``ConfigurationError`` when the name built is not one unquoted identifier.
    """
    name = REDSHIFT_PROBE_RELATION_TEMPLATE.format(token=uuid.uuid4().hex)
    if not _IDENTIFIER_SHAPE.fullmatch(name) or len(name) > MAX_IDENTIFIER_CHARACTERS:
        raise ConfigurationError(
            f"the write probe relation name is not one unquoted SQL identifier of at "
            f"most {MAX_IDENTIFIER_CHARACTERS} characters: {_shown(name)}"
        )
    return name


def _redshift_statement_rows(
    driver: Any,
    connection: Any,
    settings: RedshiftSettings,
    statement: str,
    action: str,
    *,
    arguments: Sequence[Any] | None = None,
    expect_rows: bool = False,
) -> tuple[tuple[Any, ...], ...]:
    """Run ``statement`` on one cursor of ``connection``, returning the rows it made.

    ``arguments`` are bound rather than joined into the statement text, and the rows
    are read only for a statement that produces them, so a statement that produces
    none is not asked for a result set. The cursor is closed on the way out whatever
    happened, and a close that did not succeed is a warning rather than a failure of
    the probe.

    Raises ``AccessError`` when the cursor could not be opened or the statement did
    not succeed, with no resolved setting value in the diagnostic.
    """
    try:
        cursor = connection.cursor()
    except (driver.Error, OSError) as error:
        raise _redshift_failure(error, settings, action) from error
    try:
        try:
            if arguments is None:
                cursor.execute(statement)
            else:
                cursor.execute(statement, tuple(arguments))
            if not expect_rows:
                return ()
            return tuple(tuple(row) for row in cursor.fetchall())
        except (driver.Error, OSError) as error:
            raise _redshift_failure(error, settings, action) from error
    finally:
        try:
            cursor.close()
        except (driver.Error, OSError) as close_error:
            _warn(
                "the Redshift cursor could not be closed after "
                f"{action}: {_redshift_reason(close_error, settings)}"
            )


def _redshift_single_value(
    rows: Sequence[Sequence[Any]], what: str
) -> Any:
    """Return the one value ``rows`` carries, for a statement that answers with one.

    Raises ``AccessError`` when the target answered with no row, more than one row or
    a row that does not carry exactly one value, so a probe never reads a verdict out
    of an answer of another shape.
    """
    if len(rows) != 1 or len(rows[0]) != 1:
        raise AccessError(
            f"cannot read {what}: the target answered "
            f"{_counted(len(rows), 'row')} rather than exactly one row of one value"
        )
    return rows[0][0]


def _withdraw_redshift_probe(
    driver: Any, connection: Any, settings: RedshiftSettings, relation: str
) -> BaseException | None:
    """Withdraw everything the write probe made, and return what stopped that.

    The rollback of the transaction the temporary relation was created in withdraws
    the relation and the row together, which is the withdrawal this probe relies on.
    A rollback that did not succeed is followed by the drop of that one relation, so a
    session that survived the rollback carries no probe relation either. Returns None
    when the probe was withdrawn, and the failure that stopped the drop otherwise.
    """
    try:
        connection.rollback()
        return None
    except (driver.Error, OSError) as rollback_error:
        _warn(
            "the write probe transaction could not be rolled back: "
            f"{_redshift_reason(rollback_error, settings)}; dropping the probe "
            f"relation {_shown(relation)} instead"
        )
    try:
        _redshift_statement_rows(
            driver,
            connection,
            settings,
            f"DROP TABLE IF EXISTS {relation}",
            f"drop the write probe relation {_shown(relation)}",
        )
    except LandingError as drop_error:
        return drop_error
    return None


def _probe_redshift_write(
    driver: Any, connection: Any, settings: RedshiftSettings, relation: str
) -> None:
    """Create, write and count one temporary relation, then withdraw all of it.

    The relation is temporary, so it belongs to this session alone and no durable
    object is created: this probe provisions nothing, on the target or anywhere else.
    One row is written and counted, which is what establishes that the target accepts
    a write rather than only a connection, and the rollback that follows withdraws the
    row and the relation together. A withdrawal that did not succeed after the probe's
    own steps succeeded is the failure raised, naming the relation to drop by hand; a
    withdrawal that did not succeed after a failed step is a warning, and the step's
    own failure is the one raised.

    Returns None when the write probe succeeded and was withdrawn.

    Raises ``AccessError`` when a step did not succeed, when the row written was not
    counted back, or when the probe could not be withdrawn.
    """
    probe_failure: BaseException | None = None
    try:
        _redshift_statement_rows(
            driver,
            connection,
            settings,
            f"CREATE TEMPORARY TABLE {relation} "
            f"({REDSHIFT_PROBE_COLUMN} VARCHAR({REDSHIFT_PROBE_COLUMN_WIDTH}))",
            "create the write probe relation",
        )
        _redshift_statement_rows(
            driver,
            connection,
            settings,
            f"INSERT INTO {relation} ({REDSHIFT_PROBE_COLUMN}) VALUES (%s)",
            "write the write probe row",
            arguments=(REDSHIFT_PROBE_VALUE,),
        )
        rows = _redshift_statement_rows(
            driver,
            connection,
            settings,
            f"SELECT count(*) FROM {relation}",
            "read the write probe row back",
            expect_rows=True,
        )
        written = _redshift_single_value(rows, "the write probe row count")
        if written != REDSHIFT_PROBE_ROWS:
            raise AccessError(
                f"cannot confirm the write probe: {relation} carried "
                f"{_display(written)} rows after one write, expected "
                f"{REDSHIFT_PROBE_ROWS}"
            )
    except BaseException as error:
        probe_failure = error
        raise
    finally:
        withdrawal_failure = _withdraw_redshift_probe(
            driver, connection, settings, relation
        )
        if withdrawal_failure is not None:
            if probe_failure is None:
                raise AccessError(
                    f"cannot withdraw the write probe relation {_shown(relation)}, "
                    "which the probe created and which the session may still carry "
                    f"for removal by hand: {_one_line(str(withdrawal_failure))}"
                ) from withdrawal_failure
            _warn(
                f"the write probe relation {_shown(relation)} could not be withdrawn "
                f"after the probe failed: {_one_line(str(withdrawal_failure))}"
            )


def probe_redshift_access(
    settings: RedshiftSettings, driver: Any | None = None
) -> str:
    """Confirm the Redshift target answers and accepts one withdrawn write.

    The probe opens one connection with the settings resolved from the environment and
    the transport security the dbt profile of this bridge sets, runs
    ``REDSHIFT_PROBE_STATEMENT`` and requires the value that statement declares, and
    then performs the write probe: one temporary relation created, written, counted and
    withdrawn by the rollback of its own transaction. That is the whole of the second
    half of the precondition gate. Returning the verdict means every one of those
    steps succeeded.

    ``driver`` names the module the connection is opened through, and defaults to the
    pinned redshift-connector imported on the call. Nothing is created on the target,
    on AWS or on this machine: no cluster, workgroup, database, schema, durable
    relation, network or IAM object, and no bucket. The connection is closed on the way
    out whatever happened.

    The verdict is one line carrying no setting value, and no diagnostic of this probe
    carries the host, the port, the user, the database, the schema or the password.

    Raises ``ConfigurationError`` when the driver cannot be imported, and
    ``AccessError`` when the target did not answer, refused the connection, refused a
    credential, answered the connectivity statement with anything else, refused the
    write probe or could not withdraw it.
    """
    driver = _redshift_driver() if driver is None else driver
    _note(
        "addressing the Redshift target named by "
        f"{REDSHIFT_HOST_VARIABLE} on the port from {REDSHIFT_PORT_VARIABLE}, as the "
        f"user from {REDSHIFT_USER_VARIABLE} against the database from "
        f"{REDSHIFT_DATABASE_VARIABLE}, with {_shown(REDSHIFT_SSL_MODE)} transport "
        f"and a {settings.connect_timeout} second connect timeout; no value of those "
        "settings is printed"
    )
    try:
        connection = driver.connect(
            host=settings.host,
            port=settings.port,
            database=settings.database,
            user=settings.user,
            password=settings.password,
            timeout=settings.connect_timeout,
            ssl=True,
            sslmode=REDSHIFT_SSL_MODE,
            application_name=REDSHIFT_APPLICATION_NAME,
        )
    except (driver.Error, OSError) as error:
        raise _redshift_failure(
            error, settings, "reach the Redshift target"
        ) from error
    try:
        answered = _redshift_single_value(
            _redshift_statement_rows(
                driver,
                connection,
                settings,
                REDSHIFT_PROBE_STATEMENT,
                f"run {REDSHIFT_PROBE_STATEMENT} on the Redshift target",
                expect_rows=True,
            ),
            f"the answer to {REDSHIFT_PROBE_STATEMENT}",
        )
        if answered != REDSHIFT_PROBE_STATEMENT_VALUE:
            raise AccessError(
                f"cannot confirm the Redshift target: {REDSHIFT_PROBE_STATEMENT} "
                f"answered {_display(answered)}, expected "
                f"{REDSHIFT_PROBE_STATEMENT_VALUE}"
            )
        relation = build_redshift_probe_relation()
        _note(
            f"the connectivity statement answered {REDSHIFT_PROBE_STATEMENT_VALUE}; "
            f"writing the temporary probe relation {_shown(relation)}, which the "
            "rollback that follows withdraws"
        )
        _probe_redshift_write(driver, connection, settings, relation)
        _note(
            f"the write probe wrote {REDSHIFT_PROBE_ROWS} row of {_shown(relation)} "
            "and withdrew it; nothing was provisioned"
        )
    finally:
        try:
            connection.close()
        except (driver.Error, OSError) as close_error:
            _warn(
                "the Redshift connection could not be closed: "
                f"{_redshift_reason(close_error, settings)}"
            )
    return (
        f"{REDSHIFT_PROBE_VERDICT} "
        f"select={REDSHIFT_PROBE_STATEMENT_VALUE} "
        f"write-probe={REDSHIFT_PROBE_WRITE_OUTCOME}"
    )


# ---------------------------------------------------------------------------
# Redshift load rendering
# ---------------------------------------------------------------------------


def read_column_names(
    schema: Mapping[str, Any], path: Path = DEFAULT_SCHEMA
) -> tuple[str, ...]:
    """Return the landed column names, in the order the schema declares them.

    The order is the order of the schema's ``properties`` block, which is the order of
    the COPY column list the rendered load carries. The count is confirmed to be
    ``EXPECTED_COLUMN_COUNT`` and every name is confirmed usable as one unquoted SQL
    identifier of at most ``MAX_IDENTIFIER_CHARACTERS`` characters.

    Raises ``SchemaError`` when the schema carries no usable ``properties`` block,
    declares a name that is not such an identifier, or declares another number of
    columns.
    """
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise SchemaError(
            f"the landing schema carries no properties object: {_path_shown(path)}; "
            "the landed column names and their order are read from it"
        )
    names: list[str] = []
    for name in properties:
        text = str(name)
        if len(text) > MAX_IDENTIFIER_CHARACTERS or not _IDENTIFIER_SHAPE.fullmatch(
            text
        ):
            raise SchemaError(
                f"the landing schema declares the property {_shown(text)}: "
                f"{_path_shown(path)}; a landed column name is an ASCII lower-case "
                "letter followed by ASCII lower-case letters, digits and underscores"
            )
        names.append(text)
    if len(names) != EXPECTED_COLUMN_COUNT:
        raise SchemaError(
            f"the landing schema declares {len(names)} properties: "
            f"{_path_shown(path)}; {EXPECTED_COLUMN_COUNT} landed columns are expected"
        )
    return tuple(names)


class ObjectIdentity(NamedTuple):
    """The immutable identity of one landed object.

    ``content_length`` is the byte count of the object body, ``sha256`` the digest of
    those bytes, ``etag`` the entity tag the store reports for them, and ``version_id``
    the version the store assigned, or ``NOT_VERSIONED`` on a bucket that keeps none.
    """

    content_length: int
    sha256: str
    etag: str
    version_id: str


def object_identity(
    body: bytes, etag: str | None = None, version_id: str | None = None
) -> ObjectIdentity:
    """Return the identity of the object whose body is ``body``.

    ``content_length`` and ``sha256`` are computed from ``body``. ``etag`` defaults to
    the entity tag a single-part upload of ``body`` produces, which is the hex MD5 of
    those bytes, and any surrounding double quotes a store reported are removed before
    it is used. ``version_id`` defaults to ``NOT_VERSIONED``.

    Raises ``ConfigurationError`` when a supplied ``etag`` or ``version_id`` is not of
    the accepted form.
    """
    if etag is None:
        digest = hashlib.md5(body, usedforsecurity=False).hexdigest()
    else:
        digest = etag.strip().strip('"')
    version = NOT_VERSIONED if version_id is None else version_id
    return ObjectIdentity(
        content_length=len(body),
        sha256=_validated_placeholder(
            "OBJECT_SHA256", hashlib.sha256(body).hexdigest()
        ),
        etag=_validated_placeholder("OBJECT_ETAG", digest),
        version_id=_validated_placeholder("OBJECT_VERSION_ID", version),
    )


def _rejected(name: str, value: str, requirement: str) -> ConfigurationError:
    """Return the diagnostic refusing ``value`` as the value of placeholder ``name``."""
    return ConfigurationError(
        f"the value of the {name} placeholder is not accepted: {_shown(value)}; "
        f"{requirement}"
    )


def _validate_bucket_name(name: str, value: str) -> str:
    """Return ``value`` confirmed to be an S3 bucket name.

    An accepted name holds ``MIN_BUCKET_CHARACTERS`` to ``MAX_BUCKET_CHARACTERS``
    characters of ASCII lower-case letters, digits, dot and hyphen, starts and ends with
    a letter or a digit, carries no consecutive dots, and is not written as an IPv4
    address.

    Raises ``ConfigurationError`` for every other value.
    """
    if not (MIN_BUCKET_CHARACTERS <= len(value) <= MAX_BUCKET_CHARACTERS):
        raise _rejected(
            name,
            value,
            f"between {MIN_BUCKET_CHARACTERS} and {MAX_BUCKET_CHARACTERS} characters "
            "are accepted",
        )
    if not _BUCKET_NAME_SHAPE.fullmatch(value):
        raise _rejected(
            name,
            value,
            "ASCII lower-case letters, digits, dot and hyphen are accepted, starting "
            "and ending with a letter or a digit",
        )
    if ".." in value:
        raise _rejected(name, value, "consecutive dots are not accepted")
    if _IPV4_SHAPE.fullmatch(value):
        raise _rejected(
            name, value, "a name written as an IPv4 address is not accepted"
        )
    return value


def _validate_key_segment(name: str, value: str) -> str:
    """Return ``value`` confirmed usable as one segment of the landed object key.

    Raises ``ConfigurationError`` when the value is empty, longer than
    ``MAX_SEGMENT_CHARACTERS``, or carries a character outside ASCII letters, digits,
    underscore, dot and hyphen.
    """
    if not value or len(value) > MAX_SEGMENT_CHARACTERS:
        raise _rejected(
            name,
            value,
            f"1 to {MAX_SEGMENT_CHARACTERS} characters are accepted",
        )
    if not _SEGMENT_SHAPE.fullmatch(value):
        raise _rejected(
            name,
            value,
            "ASCII letters, digits, underscore, dot and hyphen are accepted; it becomes "
            "one segment of the landed object key",
        )
    return value


def _validate_extract_date(name: str, value: str) -> str:
    """Return ``value`` confirmed to be a calendar date written ``EXTRACT_DATE_FORM``.

    Raises ``ConfigurationError`` when the value is not such a date, which refuses an
    impossible calendar day as well as any other spelling of a real one.
    """
    try:
        parsed = datetime.date.fromisoformat(value)
    except ValueError as error:
        raise _rejected(
            name,
            value,
            f"a calendar date written {EXTRACT_DATE_FORM} is required: "
            f"{_reason(error)}",
        ) from error
    if parsed.isoformat() != value:
        raise _rejected(
            name,
            value,
            f"{_shown(parsed.isoformat())} is the accepted spelling of that date",
        )
    return value


def _validate_landing_part(name: str, value: str) -> str:
    """Return ``value`` confirmed to be the part element of a landed object name.

    An accepted value is exactly ``PART_NUMBER_DIGITS`` decimal digits, which is the
    form the object name carries, so the key the rendered load reads is the key the
    landing writer wrote character for character.

    Raises ``ConfigurationError`` for every other value.
    """
    if not _PART_TEXT_SHAPE.fullmatch(value):
        raise _rejected(
            name,
            value,
            f"exactly {PART_NUMBER_DIGITS} decimal digits are accepted, the form the "
            "landed object name carries",
        )
    return value


def _validate_policy_number(name: str, value: str) -> str:
    """Return ``value`` confirmed to be a policy number.

    An accepted value is 1 to 10 digits, the width of CA-POLICY-NUM PIC 9(10) at
    base/src/lgcmarea.cpy:35.

    Raises ``ConfigurationError`` for every other value.
    """
    if not _POLICY_NUMBER_SHAPE.fullmatch(value):
        raise _rejected(
            name,
            value,
            "1 to 10 digits are accepted, the width of CA-POLICY-NUM PIC 9(10) at "
            "base/src/lgcmarea.cpy:35",
        )
    return value


def _validate_iam_role(name: str, value: str) -> str:
    """Return ``value`` confirmed to be an IAM role ARN.

    Raises ``ConfigurationError`` when the value is longer than
    ``MAX_IAM_ROLE_CHARACTERS`` or is not written as an IAM role ARN.
    """
    if len(value) > MAX_IAM_ROLE_CHARACTERS:
        raise _rejected(
            name, value, f"at most {MAX_IAM_ROLE_CHARACTERS} characters are accepted"
        )
    if not _IAM_ROLE_ARN_SHAPE.fullmatch(value):
        raise _rejected(
            name,
            value,
            "an IAM role ARN is required, written arn, the aws partition, iam, twelve "
            "account digits and role/ followed by the role path and name",
        )
    return value


def _validate_region(name: str, value: str) -> str:
    """Return ``value`` confirmed to be an AWS region code.

    Raises ``ConfigurationError`` when the value is longer than
    ``MAX_REGION_CHARACTERS`` or is not written as a region code.
    """
    if len(value) > MAX_REGION_CHARACTERS:
        raise _rejected(
            name, value, f"at most {MAX_REGION_CHARACTERS} characters are accepted"
        )
    if not _REGION_SHAPE.fullmatch(value):
        raise _rejected(
            name,
            value,
            "an AWS region code such as eu-west-2 is required",
        )
    return value


def _validate_content_length(name: str, value: str) -> str:
    """Return ``value`` confirmed to be the byte count of the landed object.

    Raises ``ConfigurationError`` when the value is not 1 to 12 digits without a
    leading zero.
    """
    if not _CONTENT_LENGTH_SHAPE.fullmatch(value):
        raise _rejected(
            name, value, "1 to 12 digits without a leading zero are accepted"
        )
    return value


def _validate_sha256(name: str, value: str) -> str:
    """Return ``value`` confirmed to be a SHA-256 digest in lower-case hex.

    Raises ``ConfigurationError`` for every other value.
    """
    if not _SHA256_SHAPE.fullmatch(value):
        raise _rejected(name, value, "64 lower-case hex characters are required")
    return value


def _validate_etag(name: str, value: str) -> str:
    """Return ``value`` confirmed to be an S3 entity tag.

    An accepted value is 32 lower-case hex characters, optionally followed by a hyphen
    and the part count a multipart upload reports.

    Raises ``ConfigurationError`` for every other value.
    """
    if not _ETAG_SHAPE.fullmatch(value):
        raise _rejected(
            name,
            value,
            "32 lower-case hex characters, optionally followed by a hyphen and a part "
            "count, are required",
        )
    return value


def _validate_version_id(name: str, value: str) -> str:
    """Return ``value`` confirmed to be an S3 version id or ``NOT_VERSIONED``.

    Raises ``ConfigurationError`` when the value is empty, longer than
    ``MAX_VERSION_ID_CHARACTERS``, or carries a character outside ASCII letters,
    digits, dot, underscore and hyphen.
    """
    if not _VERSION_ID_SHAPE.fullmatch(value):
        raise _rejected(
            name,
            value,
            f"1 to {MAX_VERSION_ID_CHARACTERS} characters of ASCII letters, digits, "
            f"dot, underscore and hyphen are accepted, or {_shown(NOT_VERSIONED)}",
        )
    return value


# Validator applied to each placeholder value before it is substituted. The keys are
# the placeholder names the Redshift load template carries, and the tuple below fixes
# the order they are reported in.
def _validate_statement_timeout(name: str, value: str) -> str:
    """Return ``value`` confirmed to be the statement timeout in whole milliseconds.

    The value is 1 to ``MAX_TIMEOUT_DIGITS`` digits carrying no leading zero, so it
    names a positive bound: a zero would remove the bound the load sets.

    Raises ``TemplateError`` naming the placeholder for every other value.
    """
    if not _TIMEOUT_SHAPE.fullmatch(value):
        raise TemplateError(
            f"the {name} placeholder value is not a positive whole number of "
            f"milliseconds of at most {MAX_TIMEOUT_DIGITS} digits: {_shown(value)}"
        )
    return value


_PLACEHOLDER_VALIDATORS: dict[str, Callable[[str, str], str]] = {
    "S3_BUCKET": _validate_bucket_name,
    "SOURCE_SYSTEM_KEY": _validate_key_segment,
    "ENTITY": _validate_key_segment,
    "EXTRACT_DATE": _validate_extract_date,
    "LANDING_PART": _validate_landing_part,
    "POLICY_NUMBER": _validate_policy_number,
    "REDSHIFT_IAM_ROLE": _validate_iam_role,
    "AWS_REGION": _validate_region,
    "OBJECT_CONTENT_LENGTH": _validate_content_length,
    "OBJECT_SHA256": _validate_sha256,
    "OBJECT_ETAG": _validate_etag,
    "OBJECT_VERSION_ID": _validate_version_id,
    "STATEMENT_TIMEOUT_MS": _validate_statement_timeout,
}
SUPPORTED_PLACEHOLDERS = tuple(_PLACEHOLDER_VALIDATORS)


def _validated_placeholder(name: str, value: Any) -> str:
    """Return ``value`` validated as the value of the placeholder ``name``.

    The value must be a non-empty string carrying no control character and none of
    ``_FORBIDDEN_LITERAL_FRAGMENTS``, and must satisfy the allowlist recorded for
    ``name``.

    Raises ``ConfigurationError`` when ``name`` is not a supported placeholder, when
    the value is not a non-empty string, when it carries a refused character or
    fragment, or when the allowlist refuses it.
    """
    validator = _PLACEHOLDER_VALIDATORS.get(name)
    if validator is None:
        raise ConfigurationError(
            f"{_shown(name)} is not a placeholder of the Redshift load template; the "
            f"accepted placeholders are {', '.join(SUPPORTED_PLACEHOLDERS)}"
        )
    if not isinstance(value, str):
        raise ConfigurationError(
            f"the value of the {name} placeholder is {_display(value)}; a non-empty "
            "string is required"
        )
    if not value:
        raise ConfigurationError(
            f"the value of the {name} placeholder is empty; a non-empty string is "
            "required"
        )
    if _CONTROL_CHARACTERS.search(value):
        raise _rejected(name, value, "a control character is not accepted")
    for fragment in _FORBIDDEN_LITERAL_FRAGMENTS:
        if fragment in value:
            raise _rejected(
                name, value, f"the fragment {_shown(fragment)} is not accepted"
            )
    return validator(name, value)


def _sql_literal_body(name: str, value: str) -> str:
    """Return the validated ``value`` escaped for a single-quoted SQL literal.

    ``_validated_placeholder`` has already refused every quote, comment sequence,
    semicolon, backslash and control character, and this doubles any single quote that
    reached this point.

    Raises ``ConfigurationError`` when the escaped text still carries an unbalanced
    quote.
    """
    escaped = value.replace("'", "''")
    if escaped.count("'") % 2 != 0:
        raise _rejected(name, value, "an unbalanced quote is not accepted")
    return escaped


def split_sql_statements(text: str, what: str) -> tuple[str, ...]:
    """Return the statements of ``text``, in order and as written.

    Statements are separated by semicolons outside quoted text and outside comments. A
    single-quoted literal, a double-quoted identifier, a ``--`` line comment and a
    ``/* */`` block comment, including nested block comments, are carried through
    without their contents being read as a separator. A statement is returned exactly as
    written with surrounding whitespace removed, and a run holding only comments and
    whitespace is not returned as a statement. ``what`` names the text in any
    diagnostic.

    Raises ``TemplateError`` when a quoted literal, quoted identifier or block comment
    is left unterminated.
    """
    statements: list[str] = []
    verbatim: list[str] = []
    code: list[str] = []
    index = 0
    length = len(text)
    line = 1

    def _fail(construct: str, opened_at: int) -> NoReturn:
        """Raise ``TemplateError`` for ``construct`` left open from ``opened_at``."""
        raise TemplateError(
            f"the {what} leaves {construct} unterminated from line {opened_at}; its "
            "statement boundaries cannot be established"
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
            if depth != 0:
                _fail("a block comment", opened_at)
            verbatim.append(text[start:index])
            code.append(" ")
            continue
        if character in {"'", '"'}:
            opened_at = line
            start = index
            index += 1
            closed = False
            while index < length:
                if text[index] == "\n":
                    line += 1
                if text[index] == character:
                    if text[index : index + 2] == character * 2:
                        index += 2
                        continue
                    index += 1
                    closed = True
                    break
                index += 1
            if not closed:
                _fail(
                    "a quoted literal" if character == "'" else "a quoted identifier",
                    opened_at,
                )
            fragment = text[start:index]
            verbatim.append(fragment)
            code.append(fragment)
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


def _statement_keyword(statement: str) -> str:
    """Return the leading keyword of ``statement``, in upper case.

    Leading comments and whitespace are stepped over, so the keyword returned is the
    first word of executable text.
    """
    text = statement
    while text:
        stripped = text.lstrip()
        if stripped.startswith("--"):
            end = stripped.find("\n")
            text = "" if end < 0 else stripped[end + 1 :]
            continue
        if stripped.startswith("/*"):
            end = stripped.find("*/")
            text = "" if end < 0 else stripped[end + 2 :]
            continue
        word = re.match(r"[A-Za-z_]+", stripped)
        return word.group().upper() if word is not None else ""
    return ""


def _statement_code(statement: str) -> str:
    """Return ``statement`` with every ``--`` line comment removed.

    A ``--`` sequence inside a quoted literal is retained, so the text returned carries
    the statement's literals as written.
    """
    kept: list[str] = []
    for line in statement.splitlines():
        index = 0
        quote: str | None = None
        cut = len(line)
        while index < len(line):
            character = line[index]
            if quote is not None:
                if character == quote:
                    quote = None
                index += 1
                continue
            if character in {"'", '"'}:
                quote = character
                index += 1
                continue
            if line[index : index + 2] == "--":
                cut = index
                break
            index += 1
        kept.append(line[:cut])
    return "\n".join(kept)


def _copy_column_names(statement: str) -> tuple[str, ...]:
    """Return the column names the COPY statement lists, in the order it lists them.

    Comments are removed first, then the names are read from the parenthesised list
    following the relation name.

    Raises ``TemplateError`` when the statement carries no such list.
    """
    code = _statement_code(statement)
    opened = code.find("(")
    if opened < 0:
        raise TemplateError("the rendered COPY statement carries no column list")
    depth = 0
    closed = -1
    for index in range(opened, len(code)):
        if code[index] == "(":
            depth += 1
            continue
        if code[index] == ")":
            depth -= 1
            if depth == 0:
                closed = index
                break
    if closed < 0:
        raise TemplateError(
            "the rendered COPY statement leaves its column list unclosed"
        )
    inner = code[opened + 1 : closed]
    return tuple(part.strip() for part in inner.split(",") if part.strip())


def build_copy_manifest(object_uri: str, content_length: int) -> str:
    """Return the COPY manifest binding one load to one landed object.

    The manifest carries exactly one entry, in the shape Amazon Redshift's manifest
    schema fixes: the validated object's URL, ``mandatory`` true, and a nested
    ``meta`` member holding ``content_length``. ``mandatory`` true makes a COPY
    reading this manifest fail on a removed object rather than load nothing. The byte
    count sits under ``meta`` because that is where the manifest schema places it, and
    where Redshift verifies it for a columnar format; the load this manifest serves is
    ``FORMAT AS JSON``, for which Redshift performs no content-length check, so the
    value records the byte count of the object the manifest was written for rather
    than being enforced by the COPY.

    Decision rationale: modernization/docs/decision-log.md, row D-40.
    """
    document = {
        "entries": [
            {
                "url": object_uri,
                "mandatory": True,
                "meta": {"content_length": content_length},
            }
        ]
    }
    return json.dumps(document, indent=2, sort_keys=False) + "\n"


class RenderedLoad(NamedTuple):
    """The documents one render produced, and the object identity they are bound to.

    ``sql`` is the substituted Redshift load, ``manifest`` the COPY manifest it reads,
    ``object_key`` and ``manifest_key`` the two keys under the landing prefix,
    ``object_uri`` the URI the manifest entry names, ``manifest_uri`` the URI the COPY
    reads, and ``values`` the validated placeholder values both documents carry.
    """

    sql: str
    manifest: str
    object_key: str
    manifest_key: str
    object_uri: str
    manifest_uri: str
    values: Mapping[str, str]


def template_placeholders(text: str, template_path: Path) -> tuple[str, ...]:
    """Return the distinct placeholder names ``text`` carries, in first-seen order.

    Raises ``TemplateError`` when the text carries a placeholder that is not on the
    allowlist, or an unterminated placeholder opener.
    """
    found: list[str] = []
    for match in _PLACEHOLDER_SHAPE.finditer(text):
        name = match.group(1)
        if name not in _PLACEHOLDER_VALIDATORS:
            raise TemplateError(
                f"the Redshift load template carries the unsupported placeholder "
                f"{_shown(name)}: {_path_shown(template_path)}; the accepted "
                f"placeholders are {', '.join(SUPPORTED_PLACEHOLDERS)}"
            )
        if name not in found:
            found.append(name)
    remainder = _PLACEHOLDER_SHAPE.sub("", text)
    if PLACEHOLDER_OPENER in remainder:
        raise TemplateError(
            f"the Redshift load template leaves a placeholder unterminated: "
            f"{_path_shown(template_path)}; every placeholder is a name in braces "
            f"after {_shown(PLACEHOLDER_OPENER)}"
        )
    return tuple(found)


def render_redshift_load(
    template_text: str,
    values: Mapping[str, Any],
    record: Mapping[str, Any],
    columns: Sequence[str],
    template_path: Path = DEFAULT_REDSHIFT_TEMPLATE,
) -> RenderedLoad:
    """Return the Redshift load and manifest rendered for one validated record.

    Every value of ``values`` is validated against the allowlist of its placeholder and
    escaped for a SQL string literal before substitution; the placeholder set of
    ``values`` and of the template must both equal ``SUPPORTED_PLACEHOLDERS``. The
    rendered load is then confirmed to carry no remaining placeholder, the statement
    frame ``RENDERED_TRANSACTION_FRAME``, a delete guard keyed on the record's own
    source-system key and policy number, the COPY column list ``columns`` in that exact
    order, and a COPY reading the manifest key derived from the record's own
    source-system key with the supplied entity, extract date and part. The part reaches
    both derived keys from the ``LANDING_PART`` value, so a load rendered for one part
    reads the manifest of that part and of no other object under the prefix.

    Raises ``ConfigurationError`` when a value is refused or contradicts ``record``, and
    ``TemplateError`` when the template or the rendered text is not as described.
    """
    supplied = set(values)
    supported = set(SUPPORTED_PLACEHOLDERS)
    missing = [name for name in SUPPORTED_PLACEHOLDERS if name not in supplied]
    if missing:
        raise TemplateError(
            f"no value was supplied for the placeholder(s) {', '.join(missing)}; every "
            f"placeholder of {_path_shown(template_path)} must carry a value"
        )
    unknown = sorted(supplied - supported)
    if unknown:
        raise TemplateError(
            f"a value was supplied for the unsupported placeholder(s) "
            f"{', '.join(unknown)}; the accepted placeholders are "
            f"{', '.join(SUPPORTED_PLACEHOLDERS)}"
        )
    validated = {
        name: _validated_placeholder(name, values[name])
        for name in SUPPORTED_PLACEHOLDERS
    }

    carried_key = record.get(SOURCE_SYSTEM_KEY_FIELD)
    if carried_key != validated["SOURCE_SYSTEM_KEY"]:
        raise ConfigurationError(
            f"the rendered load would carry {_shown(validated['SOURCE_SYSTEM_KEY'])} "
            f"as {_shown(SOURCE_SYSTEM_KEY_FIELD)} while the record carries "
            f"{_display(carried_key)}; the two must agree"
        )
    carried_policy = record.get(POLICY_NUMBER_FIELD)
    if carried_policy != validated["POLICY_NUMBER"]:
        raise ConfigurationError(
            f"the rendered delete guard would carry "
            f"{_shown(validated['POLICY_NUMBER'])} as {_shown(POLICY_NUMBER_FIELD)} "
            f"while the record carries {_display(carried_policy)}; the two must agree"
        )

    declared = set(template_placeholders(template_text, template_path))
    absent = [name for name in SUPPORTED_PLACEHOLDERS if name not in declared]
    if absent:
        raise TemplateError(
            f"the Redshift load template carries no {', '.join(absent)} placeholder: "
            f"{_path_shown(template_path)}; every accepted placeholder must appear in "
            "it"
        )

    escaped = {
        name: _sql_literal_body(name, value) for name, value in validated.items()
    }
    rendered = _PLACEHOLDER_SHAPE.sub(lambda match: escaped[match.group(1)],
                                      template_text)
    if PLACEHOLDER_OPENER in rendered:
        raise TemplateError(
            f"the rendered load still carries {_shown(PLACEHOLDER_OPENER)}: "
            f"{_path_shown(template_path)}"
        )

    extract_date = datetime.date.fromisoformat(validated["EXTRACT_DATE"])
    part = int(validated["LANDING_PART"], 10)
    object_key = build_landing_key(
        validated["SOURCE_SYSTEM_KEY"], validated["ENTITY"], extract_date, part
    )
    manifest_key = build_manifest_key(
        validated["SOURCE_SYSTEM_KEY"], validated["ENTITY"], extract_date, part
    )
    object_uri = build_object_uri(validated["S3_BUCKET"], object_key)
    manifest_uri = build_object_uri(validated["S3_BUCKET"], manifest_key)

    statements = split_sql_statements(rendered, "rendered Redshift load")
    keywords = tuple(_statement_keyword(statement) for statement in statements)
    opening, closing = RENDERED_TRANSACTION_FRAME
    if opening not in keywords or keywords[-1] != closing:
        raise TemplateError(
            f"the rendered load carries the statement sequence "
            f"{', '.join(keywords) if keywords else 'none'}: "
            f"{_path_shown(template_path)}; every statement of the load runs between "
            f"{opening} and a closing {closing}"
        )
    for required in RENDERED_REQUIRED_KEYWORDS:
        if keywords.count(required) != 1:
            raise TemplateError(
                f"the rendered load carries {keywords.count(required)} {required} "
                f"statements: {_path_shown(template_path)}; exactly one is required"
            )
    delete_statement = statements[keywords.index("DELETE")]
    delete_code = " ".join(_statement_code(delete_statement).split())
    for field, value, marker in (
        (SOURCE_SYSTEM_KEY_FIELD, escaped["SOURCE_SYSTEM_KEY"],
         DELETE_BOUND_MARKERS[0]),
        (POLICY_NUMBER_FIELD, escaped["POLICY_NUMBER"], DELETE_BOUND_MARKERS[1]),
    ):
        # The shipped template binds the natural key as a parameter, so the value never
        # enters statement text; a template that substitutes it must carry the record's
        # own value and no other.
        keyed_by_marker = marker in delete_code
        keyed_by_value = f"{field} = '{value}'" in delete_code
        if not (keyed_by_marker or keyed_by_value):
            raise TemplateError(
                f"the rendered delete guard does not match {_shown(field)} against "
                f"the record's own value: {_path_shown(template_path)}; the guard "
                f"keys it either as the bound parameter {marker} or as that value"
            )
    copy_statement = statements[keywords.index("COPY")]
    listed = _copy_column_names(copy_statement)
    if listed != tuple(columns):
        raise TemplateError(
            f"the rendered COPY lists {len(listed)} columns: "
            f"{_path_shown(template_path)}; the {len(columns)} landed column names in "
            "the landing order are required"
        )
    copy_code = " ".join(_statement_code(copy_statement).split())
    if f"'{manifest_uri}'" not in copy_code:
        raise TemplateError(
            f"the rendered COPY does not read the manifest of the record's own key: "
            f"{_path_shown(template_path)}; the key derived from the record is "
            f"{_shown(manifest_key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
        )
    if " MANIFEST" not in copy_code.upper():
        raise TemplateError(
            f"the rendered COPY does not read its object list from a manifest: "
            f"{_path_shown(template_path)}"
        )

    return RenderedLoad(
        sql=rendered,
        manifest=build_copy_manifest(
            object_uri, int(validated["OBJECT_CONTENT_LENGTH"])
        ),
        object_key=object_key,
        manifest_key=manifest_key,
        object_uri=object_uri,
        manifest_uri=manifest_uri,
        values=validated,
    )


def read_template(path: Path = DEFAULT_REDSHIFT_TEMPLATE) -> str:
    """Return the text of the Redshift load template at ``path``.

    Raises ``TemplateError`` when the file is missing, empty, larger than
    ``MAX_SCHEMA_BYTES`` or not valid UTF-8.
    """
    try:
        raw = _read_bounded_bytes(path, MAX_SCHEMA_BYTES, "Redshift load template")
    except RecordError as error:
        raise TemplateError(str(error)) from error
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise TemplateError(
            f"the Redshift load template is not valid UTF-8: {_path_shown(path)}: "
            f"{_reason(error)}"
        ) from error


def render_redshift_document(
    document: str,
    record_path: Path,
    bucket: str,
    source_system_key: str,
    entity: str,
    extract_date: datetime.date,
    region: str,
    iam_role: str,
    *,
    part: int = DEFAULT_PART_NUMBER,
    object_etag: str | None = None,
    object_version_id: str | None = None,
    statement_timeout_ms: str = DEFAULT_STATEMENT_TIMEOUT_MS,
    schema_path: Path = DEFAULT_SCHEMA,
    template_path: Path = DEFAULT_REDSHIFT_TEMPLATE,
) -> str:
    """Return one rendered document for the record at ``record_path``.

    ``document`` selects the document returned: ``RENDER_DOCUMENT_SQL`` for the load
    statements, ``RENDER_DOCUMENT_MANIFEST`` for the manifest they read. The record is
    read, parsed, validated against the schema at ``schema_path`` and confirmed to carry
    ``source_system_key`` before anything is rendered, and the object identity the
    documents bind to is computed from the record's own bytes, which are the bytes
    land_to_s3 uploads. ``part`` is the part element of the object name the documents
    bind to and defaults to ``DEFAULT_PART_NUMBER``, so a caller that names no part
    renders the load of the object a landing that names no part wrote.
    ``statement_timeout_ms`` bounds every statement of the rendered
    load and defaults to ``DEFAULT_STATEMENT_TIMEOUT_MS``. No S3 request is made and
    nothing is written.

    Raises ``RecordError`` when the record breaches the landing contract,
    ``SchemaError`` when the schema cannot be used, ``TemplateError`` when the template
    or the rendered text is not usable, ``ConfigurationError`` when a value is refused,
    and ``UsageError`` when ``document`` is not one of ``RENDER_DOCUMENTS``.
    """
    if document not in RENDER_DOCUMENTS:
        raise UsageError(
            f"the document to render is {_shown(document)}; "
            f"{' and '.join(RENDER_DOCUMENTS)} are accepted"
        )
    body = read_record_bytes(record_path)
    record = parse_record(body, record_path)
    schema = load_schema(schema_path)
    validate_record(record, build_validator(schema, schema_path), record_path)
    confirm_source_system_key(record, source_system_key, record_path)
    columns = read_column_names(schema, schema_path)
    identity = object_identity(body, object_etag, object_version_id)
    values = {
        "S3_BUCKET": bucket,
        "SOURCE_SYSTEM_KEY": source_system_key,
        "ENTITY": entity,
        "EXTRACT_DATE": extract_date.isoformat(),
        "LANDING_PART": part_number_text(part),
        "POLICY_NUMBER": record.get(POLICY_NUMBER_FIELD),
        "REDSHIFT_IAM_ROLE": iam_role,
        "AWS_REGION": region,
        "OBJECT_CONTENT_LENGTH": str(identity.content_length),
        "OBJECT_SHA256": identity.sha256,
        "OBJECT_ETAG": identity.etag,
        "OBJECT_VERSION_ID": identity.version_id,
        "STATEMENT_TIMEOUT_MS": statement_timeout_ms,
    }
    template_text = read_template(template_path)
    result = render_redshift_load(
        template_text, values, record, columns, template_path
    )
    _note(
        f"rendered the Redshift {document} for {identity.content_length} bytes "
        f"carrying sha256 {identity.sha256} and etag {identity.etag}"
    )
    return result.sql if document == RENDER_DOCUMENT_SQL else result.manifest


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
    part: int = DEFAULT_PART_NUMBER,
    region: str | None = None,
    endpoint_url: str | None = None,
    schema_path: Path = DEFAULT_SCHEMA,
) -> str:
    """Validate one landing record, write it with its COPY manifest, and return its URI.

    The record is read as bytes, parsed with a repeated member name refused, validated
    against the schema at ``schema_path``, confirmed to carry its keys in the order the
    schema's ``required`` list fixes, confirmed to be the canonical one-line bytes of
    that object, confirmed to carry no control character in any value, confirmed to carry
    a real date in each date key and a real moment in its timestamp, confirmed to carry
    the amounts its policy type populates and null in every other amount, and checked to
    carry ``source_system_key`` itself; the landing key is then built from the value the
    validated record carries, the fixed entity literal and ``part``, all before any
    client exists. The schema admits ``return_code`` 00 alone, so the record written is
    one successful execution of the chain, carrying the policy number and the
    last-changed timestamp the chain assigned; a record carrying any other code is
    rejected here. The bytes read are the bytes written, so the stored object is
    byte-identical to ``record_path``.

    Two objects are written under the landing prefix and nothing else is created on the
    bucket: the record at ``build_landing_key`` for ``part`` and, beside it, the COPY
    manifest modernization/landing/load_redshift.sql binds its load to, at
    ``build_manifest_key`` for that same part. ``part`` defaults to
    ``DEFAULT_PART_NUMBER``, whose two names are ``OBJECT_NAME`` and
    ``MANIFEST_OBJECT_NAME``; another part writes its own pair of objects beside them,
    so the records of one source system, entity and extract date coexist and the
    landing zone can be replayed to rebuild every raw row of that extract date. The
    record is written first and the manifest second, so no manifest on the bucket ever
    names an object that was not written, and the manifest
    is the document ``build_copy_manifest`` returns for that object: one entry carrying
    the record's own URI, ``mandatory`` true and the byte count of the bytes just
    written, which is what ``--render-redshift-load manifest`` prints for the same
    record. A manifest write that does not succeed after the record was written fails
    the landing and names the manifest key, leaving the record object in place. Both
    objects are written in either run mode.

    The record object carries ``recorded_object_metadata`` of the bytes written, so its
    land-time SHA-256 digest and byte count are stored with it by the same PutObject
    rather than as a third object: modernization/landing/load_local.py requires the
    recorded digest to equal the digest of the bytes it downloads, and the manifest to
    name that object and its real length, before it parses anything, so an object
    rewritten under this key after the landing fails that load instead of reaching the
    raw relation.

    The landing key is head-requested through ``note_object_replaced`` before the record
    is written, so an object already there - which is one landed for this same part - is
    named in one warning line as one this landing replaces. That head request cannot
    fail the landing: whatever it answers, the record and the manifest are written and
    the URI is returned.

    Raises ``RecordError`` when the record breaches the landing contract,
    ``SchemaError`` when the schema cannot be used, ``ConfigurationError`` when a
    setting cannot be resolved, and ``AccessError`` when the bucket or either write did
    not answer.
    """
    body = read_record_bytes(record_path)
    record = parse_record(body, record_path)
    schema = load_schema(schema_path)
    validate_record(record, build_validator(schema, schema_path), record_path)
    confirm_key_order(record, landed_key_order(schema, schema_path), record_path)
    confirm_canonical_bytes(body, record, record_path)
    confirm_control_free_values(record, record_path)
    confirm_calendar_values(record, record_path)
    confirm_product_premium_allocation(record, record_path)
    confirm_source_system_key(record, source_system_key, record_path)
    carried_key = str(record[SOURCE_SYSTEM_KEY_FIELD])
    key = build_landing_key(carried_key, entity, extract_date, part)
    manifest_key = build_manifest_key(carried_key, entity, extract_date, part)
    recorded = recorded_object_metadata(body)
    _note(
        f"validated {_path_shown(record_path)} carrying {len(body)} bytes with sha256 "
        f"{recorded[RECORDED_SHA256_METADATA]} for key "
        f"{_shown(key, MAX_DIAGNOSTIC_PATH_CHARACTERS)}"
    )
    client = resolve_s3_access(bucket, region, endpoint_url)
    confirm_bucket_reachable(client, bucket)
    note_object_replaced(client, bucket, key)
    put_record(client, bucket, key, body)
    object_uri = build_object_uri(bucket, key)
    manifest = build_copy_manifest(object_uri, len(body)).encode("ascii")
    put_manifest(client, bucket, manifest_key, manifest)
    _note(
        "wrote the COPY manifest "
        f"{_shown(manifest_key, MAX_DIAGNOSTIC_PATH_CHARACTERS)} carrying "
        f"{len(manifest)} bytes, naming the landed object and its {len(body)} bytes"
    )
    return object_uri


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


# Members of the motor landing record every case reads, in the landing order, and the
# commercial record used where a second distinct key is needed. Both carry return code
# 00, the outcome the landing contract carries.
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

# Settings every case that resolves a setting or renders a document uses. The bucket
# name satisfies the S3 bucket naming rules the renderer validates against.
_SELF_TEST_BUCKET = "genapp-rqi-landing-selftest"
_SELF_TEST_REGION = "eu-west-2"
_SELF_TEST_IAM_ROLE = "arn:aws:iam::123456789012:role/genapp-rqi-redshift-copy"
_SELF_TEST_EXTRACT_DATE = datetime.date(2026, 8, 19)
_SELF_TEST_CREDENTIALS = {
    "AWS_ACCESS_KEY_ID": "selftest-access-key",
    "AWS_SECRET_ACCESS_KEY": "selftest-secret-key",
}

# The two documents the parse-bound case is put to. The nesting is far past
# MAX_JSON_NESTING_DEPTH and past what the interpreter's own parser takes, so one
# document exercises this tool's bound and, with the bound raised to its own depth, the
# fallback that reports the interpreter's; the digit count is past the 4300 digits the
# interpreter converts to an int, which the parser refuses as a value rather than as
# syntax. Both stay well inside MAX_RECORD_BYTES, so each is refused for what it is
# rather than for its size.
_SELF_TEST_DEEP_NESTING = 50000
_SELF_TEST_LONG_INTEGER_DIGITS = 5000

# The Redshift settings every probe case resolves, each shaped as the resolution
# accepts it. Every value is distinctive, and no case may leave one of them in a
# verdict, a progress line or a diagnostic.
_SELF_TEST_REDSHIFT = {
    REDSHIFT_HOST_VARIABLE: (
        "genapp-rqi-selftest.abc123.eu-west-2.redshift.amazonaws.com"
    ),
    REDSHIFT_USER_VARIABLE: "genapp_rqi_loader_selftest",
    REDSHIFT_PASSWORD_VARIABLE: "selftest-redshift-canary-password",
    REDSHIFT_DATABASE_VARIABLE: "genapp_selftest",
    REDSHIFT_SCHEMA_VARIABLE: "raw_selftest",
}

# Every environment variable a case controls. The three at the end keep a session from
# reading a profile, a credentials file or an instance metadata service.
_CONSULTED_VARIABLES = (
    BUCKET_VARIABLE,
    ENDPOINT_URL_VARIABLE,
    SOURCE_SYSTEM_KEY_VARIABLE,
    *REGION_VARIABLES,
    IAM_ROLE_VARIABLE,
    REDSHIFT_HOST_VARIABLE,
    REDSHIFT_PORT_VARIABLE,
    REDSHIFT_USER_VARIABLE,
    REDSHIFT_PASSWORD_VARIABLE,
    REDSHIFT_DATABASE_VARIABLE,
    REDSHIFT_SCHEMA_VARIABLE,
    REDSHIFT_CONNECT_TIMEOUT_VARIABLE,
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

# Endpoints the policy accepts, each a loopback literal or the loopback name with an
# explicit port and nothing else.
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
    ("http://evil.example.com:80", "host"),
    ("http://127.0.0.1.attacker.tld:80", "host"),
    ("http://localhost.attacker.tld:80", "host"),
    ("http://localhost.:5112", "host"),
    ("http://0177.0.0.1:5112", "host"),
    ("http://2130706433:5112", "host"),
    ("http://169.254.169.254:80", "host"),
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

# Values no placeholder accepts, each paired with the fragment or character it carries.
_HOSTILE_PLACEHOLDER_VALUES = (
    ("quote", "value's"),
    ("terminating quote", "value' --"),
    ("semicolon", "value;DROP TABLE raw.genapp_policy_issue"),
    ("comment", "value--comment"),
    ("block comment", "value/*comment*/"),
    ("newline", "value\nSELECT 1"),
    ("carriage return", "value\rSELECT 1"),
    ("nul", "value\x00"),
    ("control character", "value\x07"),
    ("delete character", "value\x7f"),
    ("double quote", 'value"'),
    ("backslash", "value\\"),
    ("empty", ""),
    ("over-length", "v" * 4097),
)

# Template every byte-compared render case substitutes, and the text that render must
# produce for _FIXTURE_VALUES. The column list is written out in full, so the render
# case also establishes that the landing schema still declares those 17 names in that
# order: the renderer compares the list against the schema's own order.
_FIXTURE_TEMPLATE_TEXT = """\
-- fixture load template
-- bucket ${S3_BUCKET} region ${AWS_REGION} role ${REDSHIFT_IAM_ROLE}
-- bytes ${OBJECT_CONTENT_LENGTH} sha256 ${OBJECT_SHA256} etag ${OBJECT_ETAG}
-- version ${OBJECT_VERSION_ID}
SET statement_timeout TO ${STATEMENT_TIMEOUT_MS};
BEGIN;
DELETE FROM raw.genapp_policy_issue
 WHERE source_system_key = '${SOURCE_SYSTEM_KEY}'
   AND policy_number = '${POLICY_NUMBER}';
COPY raw.genapp_policy_issue (
    source_system_key,
    policy_number,
    policy_type,
    customer_number,
    request_id,
    return_code,
    issue_date,
    expiry_date,
    last_changed,
    broker_id,
    brokers_reference,
    payment_amount,
    motor_premium_amount,
    fire_premium_amount,
    crime_premium_amount,
    flood_premium_amount,
    weather_premium_amount
)
FROM 's3://${S3_BUCKET}/landing/source_system_key=${SOURCE_SYSTEM_KEY}/entity=${ENTITY}/extract_date=${EXTRACT_DATE}/part-${LANDING_PART}.manifest.json'
IAM_ROLE '${REDSHIFT_IAM_ROLE}'
FORMAT AS JSON 'auto'
MANIFEST
REGION '${AWS_REGION}';
COMMIT;
"""

_FIXTURE_VALUES: dict[str, str] = {
    "S3_BUCKET": _SELF_TEST_BUCKET,
    "SOURCE_SYSTEM_KEY": DEFAULT_SOURCE_SYSTEM_KEY,
    "ENTITY": LANDING_ENTITY,
    "EXTRACT_DATE": _SELF_TEST_EXTRACT_DATE.isoformat(),
    "LANDING_PART": DEFAULT_PART_TEXT,
    "POLICY_NUMBER": "1000301",
    "REDSHIFT_IAM_ROLE": _SELF_TEST_IAM_ROLE,
    "AWS_REGION": _SELF_TEST_REGION,
    "OBJECT_CONTENT_LENGTH": "499",
    "STATEMENT_TIMEOUT_MS": "900000",
    "OBJECT_SHA256": (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    ),
    "OBJECT_ETAG": "d41d8cd98f00b204e9800998ecf8427e",
    "OBJECT_VERSION_ID": NOT_VERSIONED,
}

_FIXTURE_RENDERED_TEXT = """\
-- fixture load template
-- bucket genapp-rqi-landing-selftest region eu-west-2 role arn:aws:iam::123456789012:role/genapp-rqi-redshift-copy
-- bytes 499 sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 etag d41d8cd98f00b204e9800998ecf8427e
-- version not-versioned
SET statement_timeout TO 900000;
BEGIN;
DELETE FROM raw.genapp_policy_issue
 WHERE source_system_key = 'GENAPP_CLASS_EXEMPLAR'
   AND policy_number = '1000301';
COPY raw.genapp_policy_issue (
    source_system_key,
    policy_number,
    policy_type,
    customer_number,
    request_id,
    return_code,
    issue_date,
    expiry_date,
    last_changed,
    broker_id,
    brokers_reference,
    payment_amount,
    motor_premium_amount,
    fire_premium_amount,
    crime_premium_amount,
    flood_premium_amount,
    weather_premium_amount
)
FROM 's3://genapp-rqi-landing-selftest/landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-19/part-0000.manifest.json'
IAM_ROLE 'arn:aws:iam::123456789012:role/genapp-rqi-redshift-copy'
FORMAT AS JSON 'auto'
MANIFEST
REGION 'eu-west-2';
COMMIT;
"""


class _Absent:
    """Marker naming a record member that a fixture removes."""


_ABSENT = _Absent()


def _json_object_text(members: Sequence[tuple[str, Any]]) -> str:
    """Return one JSON object holding ``members`` in the order given, on one line.

    A member name that appears twice in ``members`` appears twice in the text, which is
    how a duplicate-member document is produced without a parser that would collapse
    it.
    """
    body = ", ".join(
        f"{json.dumps(name)}: {json.dumps(value)}" for name, value in members
    )
    return "{" + body + "}\n"


def _motor_record_text(**changes: Any) -> str:
    """Return the motor landing record, with ``changes`` applied to its members.

    A change whose value is ``_ABSENT`` removes that member; every other change
    replaces the value of an existing member or appends a new one.
    """
    members: list[tuple[str, Any]] = []
    for name, value in _MOTOR_RECORD_MEMBERS:
        if name in changes:
            replacement = changes.pop(name)
            if replacement is _ABSENT:
                continue
            members.append((name, replacement))
            continue
        members.append((name, value))
    members.extend(changes.items())
    return _json_object_text(members)


def _record_members(**changes: Any) -> dict[str, Any]:
    """Return the motor record's members as a mapping, with ``changes`` applied."""
    return {**dict(_MOTOR_RECORD_MEMBERS), **changes}


# The members that turn the motor record into a record of another product, each
# carrying the amounts PREMIUM_ALLOCATION populates for its policy type and null in
# every other amount. The policy number differs from the motor record's, so a case
# needing a second natural key has one.
_COMMERCIAL_CHANGES: dict[str, Any] = {
    "policy_number": "1000302",
    "policy_type": "C",
    "request_id": "01ACOM",
    "payment_amount": "1750",
    "motor_premium_amount": None,
    "fire_premium_amount": "13500",
    "crime_premium_amount": "9400",
    "flood_premium_amount": "7200",
    "weather_premium_amount": "5100",
}
_ENDOWMENT_CHANGES: dict[str, Any] = {
    "policy_number": "1000303",
    "policy_type": "E",
    "request_id": "01AEND",
    "motor_premium_amount": None,
}
_HOUSE_CHANGES: dict[str, Any] = {
    "policy_number": "1000304",
    "policy_type": "H",
    "request_id": "01AHOU",
    "motor_premium_amount": None,
}

# Fragments of the warning line a landing writes for a key that already carries an
# object: the replacement itself and the part contract the line states. One case
# requires both present, and the cases of a first landing, of a landing of another part
# and of a head request that does not answer require the first absent.
_REPLACEMENT_FRAGMENT = "already carries an object, which this landing replaces"
_REPLACEMENT_SEQUENCE_FRAGMENT = (
    "one key carries one object per source system, entity, extract date and part"
)

# Members of the replacing record that no line of a landing carries: its identifiers,
# its request id and its amounts. Its dates and its policy type are not among them; the
# extract date of that case stands in the landing key itself, and the policy type is one
# letter.
_WITHHELD_RECORD_MEMBERS = (
    POLICY_NUMBER_FIELD,
    "customer_number",
    "request_id",
    "brokers_reference",
    PAYMENT_FIELD,
    *COMMERCIAL_PREMIUM_FIELDS,
)

# Control characters a case places inside a landed value, each paired with the name the
# case reports it by. Every one of them is refused wherever it sits in a value.
_EMBEDDED_CONTROL_CHARACTERS = (
    ("nul", "\x00"),
    ("tab", "\t"),
    ("carriage-return", "\r"),
    ("line-feed", "\n"),
    ("delete", "\x7f"),
    ("c1-control", "\x85"),
)

# ---------------------------------------------------------------------------
# Self-test: support
# ---------------------------------------------------------------------------


class _Scratch:
    """One private directory a self-test run reads and writes inside.

    The directory is created below the system temporary directory under
    ``_SCRATCH_PREFIX``, so a run reaches no path inside the repository and two runs in
    parallel never share a name. ``write`` places one document in it and returns the
    path; ``removed`` deletes the whole directory and reports whether it is gone.
    """

    def __init__(self) -> None:
        self.path = Path(tempfile.mkdtemp(prefix=_SCRATCH_PREFIX))

    def write(self, name: str, content: str | bytes) -> Path:
        """Return the path of ``name`` inside this directory, holding ``content``."""
        destination = self.path / name
        payload = content.encode("utf-8") if isinstance(content, str) else content
        destination.write_bytes(payload)
        return destination

    def absent(self, name: str) -> Path:
        """Return the path of ``name`` inside this directory without creating it."""
        return self.path / name

    def removed(self) -> bool:
        """Remove this directory with everything in it and report that it is gone."""
        shutil.rmtree(self.path, ignore_errors=True)
        return not self.path.exists()


# Prefix of the private temporary directory one self-test run works inside.
_SCRATCH_PREFIX = "land-to-s3-selftest-"


class _RecordingClient:
    """One S3 client that records every call it is asked to make and delegates it.

    ``calls`` holds one ``(operation, arguments)`` pair per call, in call order. Every
    call reaches the wrapped client unchanged, so the operation, its parameters and its
    response stay those of the pinned boto3 client.
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


class _RefusingHeadClient:
    """One S3 client whose head request raises, delegating every other call.

    ``failure`` is what ``head_object`` raises. Every other attribute is the wrapped
    client's own, so a landing driven through this client performs every step against
    the service it wraps and only its head request does not answer.
    """

    def __init__(self, client: Any, failure: BaseException) -> None:
        self._client = client
        self._failure = failure

    def head_object(self, **arguments: Any) -> Any:
        """Raise the failure this client carries, requesting nothing."""
        raise self._failure

    def __getattr__(self, name: str) -> Any:
        """Return the wrapped client's attribute unchanged."""
        return getattr(self._client, name)


class _StandInRedshiftError(Exception):
    """The class a stand-in Redshift driver raises its own failures as."""


def _stand_in_step(statement: str) -> str:
    """Return the name of the probe step ``statement`` performs."""
    if statement == REDSHIFT_PROBE_STATEMENT:
        return "select"
    for opening, step in (
        ("CREATE TEMPORARY TABLE", "create"),
        ("INSERT INTO", "insert"),
        ("SELECT count(*)", "count"),
        ("DROP TABLE", "drop"),
    ):
        if statement.startswith(opening):
            return step
    return "statement"


class _StandInRedshiftCursor:
    """One cursor of a stand-in connection, answering from what its driver holds."""

    def __init__(self, connection: "_StandInRedshiftConnection") -> None:
        self.connection = connection
        self.rows: tuple[tuple[Any, ...], ...] = ()
        self.closed = False

    def execute(self, statement: str, arguments: Sequence[Any] | None = None) -> None:
        """Record one statement with the arguments bound to it and hold its answer."""
        self.connection.record(statement, arguments)
        self.rows = self.connection.answer(statement)

    def fetchall(self) -> tuple[tuple[Any, ...], ...]:
        """Return the rows the statement executed last answered with."""
        return self.rows

    def close(self) -> None:
        """Record this cursor closed, then fail when that step was told to fail."""
        self.closed = True
        self.connection.driver.refuse("cursor-close")


class _StandInRedshiftConnection:
    """One connection of a stand-in driver, recording every statement it was given."""

    def __init__(self, driver: "_StandInRedshiftDriver") -> None:
        self.driver = driver
        self.statements: list[tuple[str, tuple[Any, ...] | None]] = []
        self.cursors: list[_StandInRedshiftCursor] = []
        self.rolled_back = 0
        self.committed = 0
        self.closed = False

    def cursor(self) -> _StandInRedshiftCursor:
        """Return one cursor, failing first when that step was told to fail."""
        self.driver.refuse("cursor")
        cursor = _StandInRedshiftCursor(self)
        self.cursors.append(cursor)
        return cursor

    def record(self, statement: str, arguments: Sequence[Any] | None) -> None:
        """Record one statement, then fail when the step it performs was told to."""
        self.statements.append(
            (statement, None if arguments is None else tuple(arguments))
        )
        self.driver.refuse(_stand_in_step(statement))

    def answer(self, statement: str) -> tuple[tuple[Any, ...], ...]:
        """Return the rows the step ``statement`` performs answers with."""
        return self.driver.answer(_stand_in_step(statement))

    def rollback(self) -> None:
        """Count one rollback, failing first when that step was told to fail."""
        self.driver.refuse("rollback")
        self.rolled_back += 1

    def commit(self) -> None:
        """Count one commit, which no step of this probe performs."""
        self.committed += 1

    def close(self) -> None:
        """Record this connection closed, then fail when that step was told to."""
        self.closed = True
        self.driver.refuse("close")

    def steps(self) -> tuple[str, ...]:
        """Return the probe steps this connection ran statements for, in order."""
        return tuple(_stand_in_step(statement) for statement, _ in self.statements)


class _StandInRedshiftDriver:
    """One stand-in for the pinned redshift-connector that opens no socket.

    ``connect`` records the parameters it was called with and returns one
    ``_StandInRedshiftConnection``, and ``Error`` is the class the probe catches a
    driver failure as. ``refusals`` names the steps that fail and the failure each
    raises - connect, cursor, cursor-close, select, create, insert, count, drop,
    rollback and close - and ``answers`` names the answer a step that produces rows
    gives: a tuple is the rows verbatim, and any other value is one row of one value.
    A case therefore drives the connect, statement, write, rollback, drop and close
    paths of the probe with no socket, no credential and no warehouse.
    """

    Error = _StandInRedshiftError

    def __init__(
        self,
        *,
        refusals: dict[str, BaseException] | None = None,
        answers: dict[str, Any] | None = None,
    ) -> None:
        self.refusals = dict(refusals or {})
        self.answers: dict[str, Any] = {
            "select": REDSHIFT_PROBE_STATEMENT_VALUE,
            "count": REDSHIFT_PROBE_ROWS,
        }
        self.answers.update(answers or {})
        self.connect_arguments: dict[str, Any] = {}
        self.connections: list[_StandInRedshiftConnection] = []

    def connect(self, **arguments: Any) -> _StandInRedshiftConnection:
        """Record the connection parameters and return one stand-in connection."""
        self.connect_arguments = dict(arguments)
        self.refuse("connect")
        connection = _StandInRedshiftConnection(self)
        self.connections.append(connection)
        return connection

    def refuse(self, step: str) -> None:
        """Raise the failure ``step`` was told to fail with, when it was told to."""
        failure = self.refusals.get(step)
        if failure is not None:
            raise failure

    def answer(self, step: str) -> tuple[tuple[Any, ...], ...]:
        """Return the rows ``step`` answers with, or none for a step that has none."""
        answer = self.answers.get(step)
        if isinstance(answer, tuple):
            return answer
        return () if answer is None else ((answer,),)


@contextlib.contextmanager
def _controlled_environment(
    scratch: _Scratch, **overrides: str
) -> Any:
    """Run a case with every consulted environment variable set by that case alone.

    Every name in ``_CONSULTED_VARIABLES`` is removed, ``overrides`` are applied, and a
    profile file, a credentials file and the instance metadata service are pointed at
    paths inside ``scratch`` that do not exist, so a session resolves only what the case
    supplied. The previous environment is restored on the way out, whatever happened.
    """
    previous = {name: os.environ.get(name) for name in _CONSULTED_VARIABLES}
    for name in _CONSULTED_VARIABLES:
        os.environ.pop(name, None)
    os.environ["AWS_CONFIG_FILE"] = str(scratch.absent("no-such-config"))
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(scratch.absent("no-such-credentials"))
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

    The run sees only the environment ``_controlled_environment`` establishes for it.
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

    The client carries this module's own connection behaviour, so a stubbed call is
    validated against the same client the tool builds for a real run.
    """
    session = boto3.session.Session(
        region_name=region,
        aws_access_key_id=_SELF_TEST_CREDENTIALS["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=_SELF_TEST_CREDENTIALS["AWS_SECRET_ACCESS_KEY"],
    )
    return session.client(SERVICE_NAME, config=_client_config())


def _assert(condition: bool, message: str) -> None:
    """Raise ``_SelfTestFailure`` carrying ``message`` unless ``condition`` holds."""
    if not condition:
        raise _SelfTestFailure(message)


def _assert_equal(observed: Any, expected: Any, what: str) -> None:
    """Raise ``_SelfTestFailure`` unless ``observed`` equals ``expected``."""
    if observed != expected:
        raise _SelfTestFailure(
            f"{what} is {observed!r}, expected {expected!r}"
        )


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

# ---------------------------------------------------------------------------
# Self-test: cases
# ---------------------------------------------------------------------------


def _test_collaborators() -> tuple[Any, Any]:
    """Return the moto in-process S3 context manager and botocore's stubber class.

    Both are test collaborators of the pinned distributions and are imported here, so
    no mode but ``--self-test`` loads them.
    """
    from botocore.stub import Stubber
    from moto import mock_aws

    return mock_aws, Stubber


@contextlib.contextmanager
def _captured_stderr() -> Any:
    """Capture the progress and warning lines a direct call writes to stderr."""
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        yield buffer


def _case_schema_present() -> str:
    """The landing schema loads, is a 2020-12 schema, and declares the 17 columns."""
    schema = load_schema()
    validator = build_validator(schema, DEFAULT_SCHEMA)
    columns = read_column_names(schema, DEFAULT_SCHEMA)
    _assert_equal(len(columns), EXPECTED_COLUMN_COUNT, "landed column count")
    _assert_equal(columns[0], SOURCE_SYSTEM_KEY_FIELD, "first landed column")
    _assert_equal(columns[1], POLICY_NUMBER_FIELD, "second landed column")
    _assert(
        isinstance(validator, Draft202012Validator),
        "the validator built for the landing schema is not a 2020-12 validator",
    )
    return f"{len(columns)} landed columns, first {columns[0]!r}"


def _case_schema_failures(scratch: _Scratch) -> str:
    """Every way the landing schema can be unusable is refused and named."""
    checks = (
        (
            "a missing schema",
            scratch.absent("no-such-schema.json"),
            "cannot be read",
        ),
        (
            "an empty schema",
            scratch.write("empty-schema.json", ""),
            "is empty",
        ),
        (
            "an unparseable schema",
            scratch.write("broken-schema.json", "{\"type\": "),
            "not readable JSON",
        ),
        (
            "a schema that is not an object",
            scratch.write("array-schema.json", "[]"),
            "at its top level",
        ),
        (
            "a schema declaring no dialect",
            scratch.write("no-dialect-schema.json", "{\"type\": \"object\"}"),
            "declares no '$schema' dialect",
        ),
        (
            "a schema declaring another dialect",
            scratch.write(
                "other-dialect-schema.json",
                "{\"$schema\": \"https://json-schema.org/draft-07/schema#\"}",
            ),
            "declares dialect",
        ),
        (
            "a schema that is not valid under its dialect",
            scratch.write(
                "invalid-schema.json",
                _json_object_text(
                    (
                        ("$schema", Draft202012Validator.META_SCHEMA["$id"]),
                        ("type", 7),
                    )
                ),
            ),
            "not a valid 2020-12 schema",
        ),
    )
    for what, path, fragment in checks:
        _assert_raises(
            what,
            SchemaError,
            fragment,
            lambda path=path: build_validator(load_schema(path), path),
        )
    oversized = scratch.write(
        "huge-schema.json", "{\"pad\": \"" + "p" * MAX_SCHEMA_BYTES + "\"}"
    )
    _assert_raises(
        "an oversized schema",
        SchemaError,
        "more than the accepted",
        lambda: load_schema(oversized),
    )
    return f"{len(checks) + 1} unusable schemas refused"


def _case_record_accepted(scratch: _Scratch) -> str:
    """A landing record satisfying the schema passes validation and the key check."""
    path = scratch.write("record-valid.json", _motor_record_text())
    body = read_record_bytes(path)
    record = parse_record(body, path)
    schema = load_schema()
    validate_record(record, build_validator(schema, DEFAULT_SCHEMA), path)
    confirm_source_system_key(record, DEFAULT_SOURCE_SYSTEM_KEY, path)
    _assert_equal(
        tuple(record), read_column_names(schema, DEFAULT_SCHEMA), "record key order"
    )
    return f"{len(record)} members accepted from {len(body)} bytes"


def _case_record_refusals(scratch: _Scratch) -> str:
    """Every landing record that breaches the contract is refused and named."""
    schema = load_schema()
    validator = build_validator(schema, DEFAULT_SCHEMA)

    def _validated(path: Path) -> None:
        """Read, parse and validate the record at ``path``."""
        body = read_record_bytes(path)
        record = parse_record(body, path)
        validate_record(record, validator, path)
        confirm_source_system_key(record, DEFAULT_SOURCE_SYSTEM_KEY, path)

    checks = (
        (
            "a record omitting a landed key",
            scratch.write("record-missing.json", _motor_record_text(broker_id=_ABSENT)),
            "does not satisfy",
        ),
        (
            "a record carrying an undeclared key",
            scratch.write(
                "record-extra.json", _motor_record_text(load_timestamp="2026-08-19")
            ),
            "does not satisfy",
        ),
        (
            "a record carrying a number where the contract carries text",
            scratch.write("record-number.json", _motor_record_text(payment_amount=500)),
            "does not satisfy",
        ),
        (
            "a record carrying an impossible policy type",
            scratch.write("record-type.json", _motor_record_text(policy_type="X")),
            "does not satisfy",
        ),
        (
            "a record whose top level is not an object",
            scratch.write("record-array.json", "[]\n"),
            "at its top level",
        ),
        (
            "a record carrying a second document",
            scratch.write(
                "record-two.json", _motor_record_text() + _motor_record_text()
            ),
            "more than one JSON document",
        ),
        (
            "an empty record",
            scratch.write("record-empty.json", ""),
            "is empty",
        ),
        (
            "a record that is not valid UTF-8",
            scratch.write("record-bytes.json", b"{\"a\": \"\xff\"}"),
            "not valid UTF-8",
        ),
        (
            "a record contradicting the resolved source-system key",
            scratch.write(
                "record-key.json", _motor_record_text(source_system_key="OTHER_SYSTEM")
            ),
            "the two must agree",
        ),
    )
    for what, path, fragment in checks:
        _assert_raises(what, RecordError, fragment, lambda path=path: _validated(path))
    oversized = scratch.write(
        "record-huge.json", "{\"pad\": \"" + "p" * MAX_RECORD_BYTES + "\"}"
    )
    _assert_raises(
        "an oversized record",
        RecordError,
        "more than the accepted",
        lambda: read_record_bytes(oversized),
    )
    _assert_raises(
        "a missing record",
        RecordError,
        "cannot be read",
        lambda: read_record_bytes(scratch.absent("no-such-record.json")),
    )
    return f"{len(checks) + 2} rejected records named"


def _case_schema_violations_reported_once(scratch: _Scratch) -> str:
    """Identically rendered violations are reported once and distinct ones all reported.

    A record omitting every landed key but two breaches one keyword once per omitted
    key, and the three assertions of this case are that the diagnostic carries that
    keyword once, that it withholds nothing it reported once, and that it carries no
    landed value. A record breaching several keywords is then required to report each of
    them, and a record breaching more of them than the reported bound admits is required
    to report the bound and to count the remainder from the violations that were kept.
    """
    schema = load_schema()
    validator = build_validator(schema, DEFAULT_SCHEMA)

    def _distinct(record: Mapping[str, Any]) -> list[str]:
        """Return the violations of ``record`` that render differently, in order."""
        kept: list[str] = []
        for error in sorted(
            validator.iter_errors(record),
            key=lambda one: (_json_pointer(one.absolute_path), str(one.validator)),
        ):
            rendered = _violation(error)
            if rendered not in kept:
                kept.append(rendered)
        return kept

    omitted = {name: _ABSENT for name, _ in _MOTOR_RECORD_MEMBERS[2:]}
    truncated = scratch.write("record-truncated.json", _motor_record_text(**omitted))
    record = parse_record(read_record_bytes(truncated), truncated)
    raised = len(list(validator.iter_errors(record)))
    _assert(
        raised > 1,
        f"a record omitting {len(omitted)} landed keys raised {raised} violations",
    )
    _assert_equal(len(_distinct(record)), 1, "the violations that render differently")
    message = str(
        _assert_raises(
            "a record omitting every landed key but two",
            RecordError,
            "does not satisfy",
            lambda: validate_record(record, validator, truncated),
        )
    )
    _assert_equal(
        message.count("constraint is not satisfied"),
        1,
        "the paragraphs one repeatedly rendered violation is reported as",
    )
    _assert(
        "further violations" not in message,
        f"the diagnostic withholds a violation it reported once: {message!r}",
    )
    _assert(
        str(dict(_MOTOR_RECORD_MEMBERS)[POLICY_NUMBER_FIELD]) not in message,
        f"the diagnostic carries the record's policy number: {message!r}",
    )

    several = scratch.write(
        "record-several-violations.json",
        _motor_record_text(policy_type="X", payment_amount="500.00", broker_id=""),
    )
    several_record = parse_record(read_record_bytes(several), several)
    pointers = ("/broker_id", "/payment_amount", "/policy_type")
    _assert_equal(
        len(_distinct(several_record)), len(pointers), "the distinct violations raised"
    )
    several_message = str(
        _assert_raises(
            "a record breaching several keywords",
            RecordError,
            "does not satisfy",
            lambda: validate_record(several_record, validator, several),
        )
    )
    for pointer in pointers:
        _assert_in(f"at {pointer}:", several_message, "the reported violations")
    _assert_equal(
        several_message.count("constraint is not satisfied"),
        len(pointers),
        "the paragraphs several distinct violations are reported as",
    )

    beyond = scratch.write(
        "record-beyond-limit.json",
        _motor_record_text(
            policy_number="x1",
            customer_number="x2",
            request_id="x3",
            issue_date="x4",
            expiry_date="x5",
            broker_id="x6",
            payment_amount="x7",
        ),
    )
    beyond_record = parse_record(read_record_bytes(beyond), beyond)
    kept = _distinct(beyond_record)
    _assert(
        len(kept) > MAX_REPORTED_SCHEMA_ERRORS,
        f"a record breaching seven keywords rendered {len(kept)} distinct violations",
    )
    beyond_message = str(
        _assert_raises(
            "a record breaching more keywords than the reported bound admits",
            RecordError,
            "does not satisfy",
            lambda: validate_record(beyond_record, validator, beyond),
        )
    )
    _assert_equal(
        beyond_message.count("constraint is not satisfied"),
        MAX_REPORTED_SCHEMA_ERRORS,
        "the violations reported up to the bound",
    )
    _assert_in(
        f"(+{len(kept) - MAX_REPORTED_SCHEMA_ERRORS} further violations)",
        beyond_message,
        "the count withheld from the violations that were kept",
    )
    return (
        f"{raised} identically rendered violations reported once, {len(pointers)} "
        f"distinct violations all reported, {MAX_REPORTED_SCHEMA_ERRORS} of "
        f"{len(kept)} reported with {len(kept) - MAX_REPORTED_SCHEMA_ERRORS} counted"
    )


def _case_duplicate_members_refused(scratch: _Scratch) -> str:
    """A repeated JSON member is refused in the record and in the schema."""
    top_level = scratch.write(
        "record-duplicate.json",
        _json_object_text((*_MOTOR_RECORD_MEMBERS, ("policy_number", "9999999"))),
    )
    error = _assert_raises(
        "a record repeating a top-level member",
        RecordError,
        "more than once",
        lambda: parse_record(read_record_bytes(top_level), top_level),
    )
    _assert_in("policy_number", str(error), "the duplicate-member diagnostic")
    nested = scratch.write(
        "record-nested-duplicate.json",
        "{\"source_system_key\": \"GENAPP_CLASS_EXEMPLAR\", "
        "\"nested\": {\"inner\": {\"leaf\": \"1\", \"leaf\": \"2\"}}}\n",
    )
    _assert_raises(
        "a record repeating a member three levels down",
        RecordError,
        "'leaf'",
        lambda: parse_record(read_record_bytes(nested), nested),
    )
    schema_path = scratch.write(
        "schema-duplicate.json",
        "{\"$schema\": \"https://json-schema.org/draft/2020-12/schema\", "
        "\"properties\": {\"a\": {\"type\": \"string\"}}, "
        "\"properties\": {\"b\": {\"type\": \"string\"}}}\n",
    )
    _assert_raises(
        "a schema repeating a member",
        SchemaError,
        "'properties'",
        lambda: load_schema(schema_path),
    )
    valid = scratch.write("record-still-valid.json", _motor_record_text())
    record = parse_record(read_record_bytes(valid), valid)
    _assert_equal(len(record), EXPECTED_COLUMN_COUNT, "members of the valid record")
    _assert_equal(
        parse_json_document("{\"a\": {\"b\": \"1\"}, \"c\": [{\"d\": \"2\"}]}"),
        {"a": {"b": "1"}, "c": [{"d": "2"}]},
        "a nested document without repetition",
    )
    return "3 repeated members refused, 2 documents still parsed"


def _case_nesting_bounded(scratch: _Scratch) -> str:
    """A document past a parser bound is a rejected input, never a traceback.

    The depth scan is put to a document nested exactly at the bound, one nested one
    level past it, a document whose brackets sit inside a string value, and one
    carrying an escaped quote before them, so the bound admits every document of the
    landing contract and counts nothing a landed value carries. The record funnel and
    the schema funnel are then put to a document nested far past the bound and to an
    integer literal longer than the interpreter converts, each of which reached the
    caller as a parser traceback and a status outside this tool's contract before the
    bound existed. The interpreter's own nesting bound is exercised with the real
    parser, by admitting a document deeper than it can take, so the fallback that
    reports it is the one a run would take.
    """
    at_bound = "[" * MAX_JSON_NESTING_DEPTH + "1" + "]" * MAX_JSON_NESTING_DEPTH
    _assert_equal(
        json_nesting_depth(at_bound),
        MAX_JSON_NESTING_DEPTH,
        "the depth of a document nested at the bound",
    )
    innermost = parse_json_document(at_bound)
    for _ in range(MAX_JSON_NESTING_DEPTH):
        innermost = innermost[0]
    _assert_equal(
        innermost, 1, "the value a document nested at the bound carries"
    )
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
        ("brackets inside a string value", '{"a": "[[[[[[["}', 1),
        ("an escaped quote before them", '{"a": "\\"[[[[["}', 1),
        ("a landed record", _motor_record_text(), 1),
        ("the landing schema", DEFAULT_SCHEMA.read_text(encoding="utf-8"), 6),
    ):
        _assert_equal(json_nesting_depth(text), depth, f"the depth of {label}")

    deep = "[" * _SELF_TEST_DEEP_NESTING + "]" * _SELF_TEST_DEEP_NESTING
    record_path = scratch.write("record-deep.json", deep)
    deep_error = _assert_raises(
        "a record nested far past the bound",
        RecordError,
        "is not a document this tool parses",
        lambda: parse_record(read_record_bytes(record_path), record_path),
    )
    _assert_in(
        f"nest more than {MAX_JSON_NESTING_DEPTH} levels deep",
        str(deep_error),
        "the diagnostic of a record nested past the bound",
    )
    schema_path = scratch.write("schema-deep.json", deep)
    _assert_raises(
        "a schema nested far past the bound",
        SchemaError,
        "is not a document this tool parses",
        lambda: load_schema(schema_path),
    )

    long_integer = f"{{\"policy_number\": {'9' * _SELF_TEST_LONG_INTEGER_DIGITS}}}\n"
    integer_path = scratch.write("record-long-integer.json", long_integer)
    integer_error = _assert_raises(
        "a record carrying an integer literal longer than the interpreter converts",
        RecordError,
        "the parser refused a value it carries",
        lambda: parse_record(read_record_bytes(integer_path), integer_path),
    )
    _assert_equal(
        integer_error.exit_status,
        EXIT_RECORD_REJECTED,
        "the status a refused parse returns",
    )

    beyond_interpreter = "[" * _SELF_TEST_DEEP_NESTING + "]" * _SELF_TEST_DEEP_NESTING
    interpreter_error = _assert_raises(
        "a document within a raised bound that the interpreter cannot parse",
        UnparsableDocumentError,
        "which the interpreter running this tool cannot parse",
        lambda: parse_json_document(
            beyond_interpreter, depth_limit=_SELF_TEST_DEEP_NESTING
        ),
    )
    _assert_in(
        f"nests {_SELF_TEST_DEEP_NESTING} levels deep",
        str(interpreter_error),
        "the diagnostic naming the depth the interpreter refused",
    )

    def _rendered(path: Path) -> _CliResult:
        """Return the result of a command line reading ``path`` as its record.

        The render mode reads and parses the record and reaches no endpoint, so the
        status and the single line a command line reports for a document past a parser
        bound are established without a client, a bucket or a credential.
        """
        return _run_cli(
            scratch,
            [
                "--render-redshift-load",
                RENDER_DOCUMENT_SQL,
                "--record",
                str(path),
                "--bucket",
                _SELF_TEST_BUCKET,
                "--region",
                _SELF_TEST_REGION,
                "--iam-role",
                _SELF_TEST_IAM_ROLE,
            ],
        )

    run = _rendered(record_path)
    _assert_equal(run.status, EXIT_RECORD_REJECTED, "the status of a deep record")
    _assert_equal(run.stdout, "", "the stdout of a deep record")
    line = _assert_one_diagnostic(run.stderr)
    _assert_in("is not a document this tool parses", line, "the reported diagnostic")
    _assert_absent("Traceback", run.stderr, "the stderr of a deep record")
    _assert_equal(
        len([reported for reported in run.stderr.splitlines() if reported]),
        1,
        "the lines a deep record reports",
    )
    integer_run = _rendered(integer_path)
    _assert_equal(
        integer_run.status, EXIT_RECORD_REJECTED, "the status of a long integer literal"
    )
    _assert_equal(integer_run.stdout, "", "the stdout of a long integer literal")
    _assert_absent("Traceback", integer_run.stderr, "the stderr of a long integer")
    _assert_one_diagnostic(integer_run.stderr)
    return (
        f"the bound of {MAX_JSON_NESTING_DEPTH} admits every contract document, "
        f"{_SELF_TEST_DEEP_NESTING}-deep and {_SELF_TEST_LONG_INTEGER_DIGITS}-digit "
        f"documents refused as records with status {EXIT_RECORD_REJECTED}"
    )


def _case_control_characters_refused(scratch: _Scratch) -> str:
    """A control character in any landed value is refused, and nothing is uploaded.

    Each of the 17 landed keys is given its own value with one line feed appended, which
    is the trailing-newline form, and ``brokers_reference`` is also given each embedded
    control character. Every case is put to the schema and to the value scan, and one
    landing run against the mocked service establishes that such a record reaches no
    object.
    """
    mock_aws, _ = _test_collaborators()
    schema = load_schema()
    validator = build_validator(schema, DEFAULT_SCHEMA)
    order = landed_key_order(schema, DEFAULT_SCHEMA)
    motor = _record_members()
    commercial = _record_members(**_COMMERCIAL_CHANGES)

    def _refused(label: str, name: str, text: str) -> None:
        """Require the schema and the value scan to refuse ``text``, naming ``name``."""
        path = scratch.write(f"record-control-{label}.json", text)
        record = parse_record(read_record_bytes(path), path)
        schema_error = _assert_raises(
            f"a control character in {name!r} against the schema",
            RecordError,
            "does not satisfy",
            lambda: validate_record(record, validator, path),
        )
        _assert_in(name, str(schema_error), f"the schema diagnostic for {name!r}")
        scan_error = _assert_raises(
            f"a control character in {name!r} against the value scan",
            RecordError,
            "control character",
            lambda: confirm_control_free_values(record, path),
        )
        _assert_in(name, str(scan_error), f"the value-scan diagnostic for {name!r}")

    for name in order:
        carried = motor[name] if isinstance(motor[name], str) else commercial[name]
        changes = {} if isinstance(motor[name], str) else dict(_COMMERCIAL_CHANGES)
        changes[name] = f"{carried}\n"
        _refused(f"trailing-{name}", name, _motor_record_text(**changes))
    for label, character in _EMBEDDED_CONTROL_CHARACTERS:
        _refused(
            f"embedded-{label}",
            "brokers_reference",
            _motor_record_text(brokers_reference=f"AB{character}CD"),
        )
    accepted = scratch.write("record-control-accepted.json", _motor_record_text())
    confirm_control_free_values(
        parse_record(read_record_bytes(accepted), accepted), accepted
    )
    path = scratch.write(
        "record-control-upload.json", _motor_record_text(policy_number="1000301\n")
    )
    with mock_aws():
        with _controlled_environment(
            scratch, AWS_DEFAULT_REGION=_SELF_TEST_REGION, **_SELF_TEST_CREDENTIALS
        ):
            raw = boto3.session.Session(region_name=_SELF_TEST_REGION).client(
                SERVICE_NAME, config=_client_config()
            )
            raw.create_bucket(
                Bucket=_SELF_TEST_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": _SELF_TEST_REGION},
            )
            with _captured_stderr():
                error = _assert_raises(
                    "a landing whose record carries a control character",
                    RecordError,
                    "policy_number",
                    lambda: land_record(
                        path,
                        _SELF_TEST_BUCKET,
                        DEFAULT_SOURCE_SYSTEM_KEY,
                        LANDING_ENTITY,
                        _SELF_TEST_EXTRACT_DATE,
                    ),
                )
            _assert_equal(
                error.exit_status, EXIT_RECORD_REJECTED, "the status of the refusal"
            )
            listing = raw.list_objects_v2(Bucket=_SELF_TEST_BUCKET)
            _assert_equal(listing.get("KeyCount"), 0, "objects in the bucket")
    return (
        f"{len(order)} trailing and {len(_EMBEDDED_CONTROL_CHARACTERS)} embedded "
        "control characters refused, nothing uploaded"
    )


def _case_product_premium_allocation(scratch: _Scratch) -> str:
    """Each policy type carries the amounts it populates and null in every other.

    The allocation table is confirmed to cover exactly the policy types the schema's
    enumeration admits, then one record per policy type is accepted and every
    contradiction of the allocation is refused by the schema and by the allocation
    check.
    """
    schema = load_schema()
    validator = build_validator(schema, DEFAULT_SCHEMA)
    declared = schema["properties"][POLICY_TYPE_FIELD]["enum"]
    _assert_equal(
        sorted(PREMIUM_ALLOCATION), sorted(declared), "the policy types allocated"
    )

    def _accepted(label: str, text: str) -> None:
        """Require the schema and the allocation check to accept ``text``."""
        path = scratch.write(f"record-premium-{label}.json", text)
        record = parse_record(read_record_bytes(path), path)
        validate_record(record, validator, path)
        confirm_product_premium_allocation(record, path)

    def _refused(label: str, text: str, name: str) -> None:
        """Require both layers to refuse ``text``, naming the amount ``name``."""
        path = scratch.write(f"record-premium-{label}.json", text)
        record = parse_record(read_record_bytes(path), path)
        schema_error = _assert_raises(
            f"{label} against the schema",
            RecordError,
            "does not satisfy",
            lambda: validate_record(record, validator, path),
        )
        _assert_in(name, str(schema_error), f"the schema diagnostic for {label}")
        allocation_error = _assert_raises(
            f"{label} against the allocation check",
            RecordError,
            POLICY_TYPE_FIELD,
            lambda: confirm_product_premium_allocation(record, path),
        )
        _assert_in(name, str(allocation_error), f"the allocation diagnostic for {label}")

    for label, changes in (
        ("motor", {}),
        ("commercial", _COMMERCIAL_CHANGES),
        ("endowment", _ENDOWMENT_CHANGES),
        ("house", _HOUSE_CHANGES),
    ):
        _accepted(label, _motor_record_text(**dict(changes)))
    refusals = (
        (
            "commercial-carrying-a-motor-premium",
            {**_COMMERCIAL_CHANGES, "motor_premium_amount": "450"},
            "motor_premium_amount",
        ),
        (
            "commercial-carrying-a-zero-motor-premium",
            {**_COMMERCIAL_CHANGES, "motor_premium_amount": "0"},
            "motor_premium_amount",
        ),
        (
            "commercial-omitting-a-commercial-premium",
            {**_COMMERCIAL_CHANGES, "crime_premium_amount": None},
            "crime_premium_amount",
        ),
        (
            "motor-carrying-a-commercial-premium",
            {"fire_premium_amount": "13500"},
            "fire_premium_amount",
        ),
        (
            "motor-omitting-the-motor-premium",
            {"motor_premium_amount": None},
            "motor_premium_amount",
        ),
        (
            "motor-omitting-the-payment",
            {"payment_amount": None},
            "payment_amount",
        ),
        (
            "endowment-carrying-a-motor-premium",
            {**_ENDOWMENT_CHANGES, "motor_premium_amount": "450"},
            "motor_premium_amount",
        ),
        (
            "house-carrying-a-commercial-premium",
            {**_HOUSE_CHANGES, "flood_premium_amount": "7200"},
            "flood_premium_amount",
        ),
    )
    for label, changes, name in refusals:
        _refused(label, _motor_record_text(**dict(changes)), name)
    unallocated = scratch.write(
        "record-premium-unallocated.json", _motor_record_text(policy_type="X")
    )
    _assert_raises(
        "a record carrying a policy type the allocation does not cover",
        RecordError,
        "allocation is recorded for",
        lambda: confirm_product_premium_allocation(
            parse_record(read_record_bytes(unallocated), unallocated), unallocated
        ),
    )
    return (
        f"{len(PREMIUM_ALLOCATION)} policy types allocated, {len(refusals)} "
        "contradictions refused"
    )


def _case_endpoint_accepted() -> str:
    """Every loopback endpoint form the policy accepts is returned unchanged."""
    for endpoint in _ACCEPTED_ENDPOINTS:
        observed, origin = resolve_endpoint_url(endpoint)
        _assert_equal(observed, endpoint, f"the endpoint {endpoint!r}")
        _assert_equal(origin, "--endpoint-url", f"the origin of {endpoint!r}")
    return f"{len(_ACCEPTED_ENDPOINTS)} loopback endpoints accepted"


def _case_endpoint_refused() -> str:
    """Every endpoint outside the loopback policy is refused, naming what it carried."""
    for endpoint, element in _REFUSED_ENDPOINTS:
        error = _assert_raises(
            f"the endpoint {endpoint!r}",
            ConfigurationError,
            element,
            lambda endpoint=endpoint: resolve_endpoint_url(endpoint),
        )
        _assert(
            "the endpoint from --endpoint-url" in str(error),
            f"the diagnostic for {endpoint!r} does not name the origin: {error}",
        )
    return f"{len(_REFUSED_ENDPOINTS)} endpoints refused before any client existed"


def _case_endpoint_resolving_name_refused() -> str:
    """A name that resolves to loopback but is not a loopback literal is refused."""
    import socket

    name = "localhost."
    try:
        infos = socket.getaddrinfo(name, 80, proto=socket.IPPROTO_TCP)
    except OSError as error:
        raise _SelfTestFailure(
            f"the resolving-name case cannot resolve {name!r}: {error}"
        ) from error
    addresses = sorted({info[4][0] for info in infos})
    _assert(
        bool(addresses)
        and all(ipaddress.ip_address(one).is_loopback for one in addresses),
        f"{name!r} resolves to {addresses}, which is not loopback",
    )
    _assert_raises(
        f"the endpoint http://{name}:5112",
        ConfigurationError,
        "host",
        lambda: resolve_endpoint_url(f"http://{name}:5112"),
    )
    _assert(not _is_loopback_host(name), f"{name!r} was taken for a loopback literal")
    return f"{name!r} resolves to {addresses} and is still refused"


def _case_configured_endpoint_ignored(scratch: _Scratch) -> str:
    """A configured endpoint variable cannot redirect a client this tool builds."""
    remote = "http://endpoint.attacker.example:9999"
    with _controlled_environment(
        scratch,
        AWS_ENDPOINT_URL=remote,
        AWS_ENDPOINT_URL_S3=remote,
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
        local = build_s3_client(session, "http://127.0.0.1:5112")
        _assert_equal(
            local.meta.endpoint_url,
            "http://127.0.0.1:5112",
            "the endpoint of a client built with a loopback override",
        )
    return f"configured endpoints ignored, client addressed {observed!r}"


def _case_probe_writes_and_deletes(scratch: _Scratch) -> str:
    """The access probe heads the bucket, writes one object and deletes it."""
    mock_aws, _ = _test_collaborators()
    with mock_aws():
        raw = boto3.session.Session(
            region_name=_SELF_TEST_REGION,
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        ).client(SERVICE_NAME, config=_client_config())
        raw.create_bucket(
            Bucket=_SELF_TEST_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": _SELF_TEST_REGION},
        )
        client = _RecordingClient(raw)
        with _captured_stderr():
            key = probe_bucket_access(client, _SELF_TEST_BUCKET)
        _assert_equal(
            client.operations(),
            ("head_bucket", "put_object", "delete_object"),
            "the operations the probe called",
        )
        _assert(
            key.startswith(f"{PROBE_KEY_ROOT}{KEY_SEPARATOR}"),
            f"the probe key {key!r} is not under the probe prefix",
        )
        _assert(
            not key.startswith(LANDING_KEY_ROOT),
            f"the probe key {key!r} sits under the landing prefix",
        )
        listing = raw.list_objects_v2(Bucket=_SELF_TEST_BUCKET)
        _assert_equal(listing.get("KeyCount"), 0, "objects left in the bucket")
        written = dict(client.calls[1][1])
        _assert_equal(written["Body"], PROBE_BODY, "the probe object body")
        _assert_equal(written["ContentType"], PROBE_CONTENT_TYPE, "the probe type")
        _assert(
            build_probe_key() != build_probe_key(),
            "two probe keys are the same",
        )
    return f"probe wrote and deleted {len(PROBE_BODY)} bytes, bucket left empty"


def _case_probe_cleanup_failures(scratch: _Scratch) -> str:
    """A probe object that cannot be deleted is reported, or warned about."""
    _, Stubber = _test_collaborators()
    client = _stubbed_client()
    with Stubber(client) as stubber:
        stubber.add_response("head_bucket", {}, {"Bucket": _SELF_TEST_BUCKET})
        stubber.add_response("put_object", {})
        stubber.add_client_error(
            "delete_object", service_error_code="AccessDenied", http_status_code=403
        )
        with _captured_stderr():
            _assert_raises(
                "a probe object that cannot be deleted",
                AccessError,
                "delete the access probe object",
                lambda: probe_bucket_access(client, _SELF_TEST_BUCKET),
            )
    client = _stubbed_client()
    with Stubber(client) as stubber:
        stubber.add_response("head_bucket", {}, {"Bucket": _SELF_TEST_BUCKET})
        stubber.add_client_error(
            "put_object", service_error_code="AccessDenied", http_status_code=403
        )
        stubber.add_client_error(
            "delete_object", service_error_code="AccessDenied", http_status_code=403
        )
        with _captured_stderr() as captured:
            _assert_raises(
                "a probe object that cannot be written",
                AccessError,
                "write the access probe object",
                lambda: probe_bucket_access(client, _SELF_TEST_BUCKET),
            )
        _assert_in(
            "could not be deleted after the write failed",
            captured.getvalue(),
            "the cleanup warning",
        )
    return "2 probe cleanup paths reported"


def _case_bucket_failures_reported() -> str:
    """Every bucket answer botocore reports becomes the diagnostic it belongs to."""
    _, Stubber = _test_collaborators()
    checks = (
        ("404", 404, AccessError, "does not exist"),
        ("NoSuchBucket", 404, AccessError, "does not exist"),
        ("AccessDenied", 403, AccessError, "not permitted"),
        ("PermanentRedirect", 301, AccessError, "not in the region"),
        ("InvalidAccessKeyId", 403, ConfigurationError, "rejected the resolved"),
        ("InternalError", 500, AccessError, "the endpoint answered"),
    )
    for code, status, expected, fragment in checks:
        client = _stubbed_client()
        with Stubber(client) as stubber:
            stubber.add_client_error(
                "head_bucket", service_error_code=code, http_status_code=status
            )
            _assert_raises(
                f"a bucket answering {code}",
                expected,
                fragment,
                lambda client=client: confirm_bucket_reachable(
                    client, _SELF_TEST_BUCKET
                ),
            )
    return f"{len(checks)} bucket answers mapped"


def _case_failure_mapping() -> str:
    """Every botocore failure class maps to the diagnostic and status it belongs to."""
    checks = (
        (NoCredentialsError(), ConfigurationError, "no credentials are resolved"),
        (
            PartialCredentialsError(provider="env", cred_var="AWS_SECRET_ACCESS_KEY"),
            ConfigurationError,
            "incomplete",
        ),
        (NoRegionError(), ConfigurationError, "no region is resolved"),
        (
            EndpointConnectionError(endpoint_url="http://127.0.0.1:1"),
            AccessError,
            "refused the connection",
        ),
        (BotoCoreError(), AccessError, "cannot write"),
    )
    for error, expected, fragment in checks:
        mapped = _failure_for(error, _SELF_TEST_BUCKET, "write the landing object")
        _assert(
            isinstance(mapped, expected),
            f"{_type_name(error)} mapped to {_type_name(mapped)}, expected "
            f"{expected.__name__}",
        )
        _assert_in(fragment, str(mapped), f"the diagnostic for {_type_name(error)}")
        _assert(
            "127.0.0.1" not in str(mapped),
            f"the diagnostic for {_type_name(error)} carries the endpoint",
        )
    _assert_equal(
        _failure_for(
            NoCredentialsError(), _SELF_TEST_BUCKET, "write"
        ).exit_status,
        EXIT_CONFIGURATION_REJECTED,
        "the status of a credential failure",
    )
    _assert_equal(
        _failure_for(BotoCoreError(), _SELF_TEST_BUCKET, "write").exit_status,
        EXIT_S3_UNAVAILABLE,
        "the status of an access failure",
    )
    return f"{len(checks)} botocore failures mapped"


def _case_credentials_and_region_required(scratch: _Scratch) -> str:
    """An unresolved credential set and an unresolved region are named, not guessed."""
    with _controlled_environment(scratch):
        session = build_session(_SELF_TEST_REGION)
        _assert_raises(
            "a session resolving no credentials",
            ConfigurationError,
            "no credentials are resolved",
            lambda: confirm_credentials(session),
        )
        bare = build_session(None)
        _assert_raises(
            "a session resolving no region",
            ConfigurationError,
            "no region is resolved",
            lambda: resolve_session_region(bare),
        )
    with _controlled_environment(
        scratch, AWS_DEFAULT_REGION=_SELF_TEST_REGION, **_SELF_TEST_CREDENTIALS
    ):
        session = build_session(None)
        _assert_equal(
            resolve_session_region(session), _SELF_TEST_REGION, "the resolved region"
        )
        confirm_credentials(session)
    return "credentials and region required, then resolved"


def _case_landing_uploads_bytes(scratch: _Scratch) -> str:
    """One landing writes the record's bytes and its manifest, and nothing else."""
    mock_aws, _ = _test_collaborators()
    path = scratch.write("record-upload.json", _motor_record_text())
    body = path.read_bytes()
    with mock_aws():
        with _controlled_environment(
            scratch, AWS_DEFAULT_REGION=_SELF_TEST_REGION, **_SELF_TEST_CREDENTIALS
        ):
            raw = boto3.session.Session(region_name=_SELF_TEST_REGION).client(
                SERVICE_NAME, config=_client_config()
            )
            raw.create_bucket(
                Bucket=_SELF_TEST_BUCKET,
                CreateBucketConfiguration={
                    "LocationConstraint": _SELF_TEST_REGION
                },
            )
            with _captured_stderr():
                uri = land_record(
                    path,
                    _SELF_TEST_BUCKET,
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                )
            key = build_landing_key(
                DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
            )
            _assert_equal(uri, build_object_uri(_SELF_TEST_BUCKET, key), "the URI")
            stored = raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=key)
            _assert_equal(stored["Body"].read(), body, "the stored object body")
            _assert_equal(
                stored["ContentType"], OBJECT_CONTENT_TYPE, "the stored content type"
            )
            manifest_key = build_manifest_key(
                DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
            )
            expected_manifest = build_copy_manifest(uri, len(body)).encode("ascii")
            stored_manifest = raw.get_object(
                Bucket=_SELF_TEST_BUCKET, Key=manifest_key
            )
            manifest_bytes = stored_manifest["Body"].read()
            _assert_equal(manifest_bytes, expected_manifest, "the stored manifest")
            _assert_equal(
                stored_manifest["ContentType"],
                OBJECT_CONTENT_TYPE,
                "the stored manifest content type",
            )
            entries = json.loads(manifest_bytes.decode("ascii"))["entries"]
            _assert_equal(len(entries), 1, "entries the manifest names")
            _assert_equal(entries[0]["url"], uri, "the URI the manifest entry names")
            _assert_equal(entries[0]["mandatory"], True, "the entry's mandatory flag")
            _assert_equal(
                entries[0]["meta"]["content_length"],
                len(body),
                "the entry's nested content length",
            )
            _assert(
                "content_length" not in entries[0],
                "the manifest entry carries a top-level content_length member",
            )
            listing = raw.list_objects_v2(Bucket=_SELF_TEST_BUCKET)
            _assert_equal(listing.get("KeyCount"), 2, "objects in the bucket")
            _assert_equal(
                sorted(entry["Key"] for entry in listing["Contents"]),
                sorted((key, manifest_key)),
                "the keys the landing wrote",
            )
            _assert_equal(
                raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=key)["Body"].read(),
                body,
                "the record's bytes after the manifest was written",
            )
    return (
        f"{len(body)} bytes stored unchanged at the derived key, "
        f"{len(expected_manifest)} manifest bytes beside them"
    )


def _case_landing_records_object_identity(scratch: _Scratch) -> str:
    """The landed object carries its own land-time digest and byte count.

    One landing is performed and the stored object is read back, by a head request and
    by a download, and both are required to report the digest of the bytes that were
    written and their byte count as user metadata, in the names
    modernization/landing/load_local.py requires before it parses anything. The
    landing is still two objects: the metadata rides on the request that writes the
    record, so no third object appears and the COPY manifest keeps the members Amazon
    Redshift's manifest schema fixes. The recorded digest is required to equal what
    ``object_identity`` records for the same bytes, which is the digest the rendered
    Redshift load carries as its OBJECT_SHA256 provenance, so the local loader and a
    real-target operator check the same value.
    """
    mock_aws, _ = _test_collaborators()
    path = scratch.write("record-recorded-identity.json", _motor_record_text())
    body = path.read_bytes()
    expected = recorded_object_metadata(body)
    _assert_equal(
        expected[RECORDED_SHA256_METADATA],
        object_identity(body).sha256,
        "the recorded digest against the rendered object identity",
    )
    _assert_equal(
        expected[RECORDED_LENGTH_METADATA],
        str(len(body)),
        "the recorded byte count",
    )
    with mock_aws():
        with _controlled_environment(
            scratch, AWS_DEFAULT_REGION=_SELF_TEST_REGION, **_SELF_TEST_CREDENTIALS
        ):
            raw = boto3.session.Session(region_name=_SELF_TEST_REGION).client(
                SERVICE_NAME, config=_client_config()
            )
            raw.create_bucket(
                Bucket=_SELF_TEST_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": _SELF_TEST_REGION},
            )
            with _captured_stderr() as progress:
                land_record(
                    path,
                    _SELF_TEST_BUCKET,
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                )
            key = build_landing_key(
                DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
            )
            for label, response in (
                ("head", raw.head_object(Bucket=_SELF_TEST_BUCKET, Key=key)),
                ("get", raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=key)),
            ):
                metadata = {
                    name.lower(): value
                    for name, value in response.get("Metadata", {}).items()
                }
                _assert_equal(
                    metadata.get(RECORDED_SHA256_METADATA),
                    expected[RECORDED_SHA256_METADATA],
                    f"the digest the {label} response reports",
                )
                _assert_equal(
                    metadata.get(RECORDED_LENGTH_METADATA),
                    expected[RECORDED_LENGTH_METADATA],
                    f"the byte count the {label} response reports",
                )
            listing = raw.list_objects_v2(Bucket=_SELF_TEST_BUCKET)
            _assert_equal(
                listing.get("KeyCount"), 2, "objects a recorded landing wrote"
            )
            manifest_key = build_manifest_key(
                DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
            )
            manifest = raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=manifest_key)[
                "Body"
            ].read()
            entry = parse_json_document(manifest.decode("ascii"))["entries"][0]
            _assert_equal(
                tuple(entry), ("url", "mandatory", "meta"), "the manifest entry members"
            )
            _assert_absent(
                RECORDED_SHA256_METADATA,
                manifest.decode("ascii"),
                "the COPY manifest",
            )
            _assert_in(
                expected[RECORDED_SHA256_METADATA],
                progress.getvalue(),
                "the progress line of a landing",
            )
    return (
        f"sha256 and {len(body)} bytes recorded on the record object, 2 objects "
        "written, manifest members unchanged"
    )


def _case_landing_replacement_noted(scratch: _Scratch) -> str:
    """A landing over a key that already carries an object names the replacement.

    Two records of different byte counts are landed for one source system, entity and
    extract date. The first landing writes no replacement line; the second writes one
    naming the key it replaces and the loading sequence one key per extract implies,
    carrying no identifier and no amount of the record it landed. The key, the stored
    bytes, the object count and the byte count the manifest names are all confirmed
    after the replacement.
    """
    mock_aws, _ = _test_collaborators()
    first = scratch.write("record-replaced-first.json", _motor_record_text())
    second = scratch.write(
        "record-replaced-second.json", _motor_record_text(**_COMMERCIAL_CHANGES)
    )
    first_body = first.read_bytes()
    second_body = second.read_bytes()
    _assert(
        len(first_body) != len(second_body),
        f"both records of this case carry {len(first_body)} bytes",
    )
    key = build_landing_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    manifest_key = build_manifest_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    with mock_aws():
        with _controlled_environment(
            scratch, AWS_DEFAULT_REGION=_SELF_TEST_REGION, **_SELF_TEST_CREDENTIALS
        ):
            raw = boto3.session.Session(region_name=_SELF_TEST_REGION).client(
                SERVICE_NAME, config=_client_config()
            )
            raw.create_bucket(
                Bucket=_SELF_TEST_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": _SELF_TEST_REGION},
            )
            with _captured_stderr() as opening:
                first_uri = land_record(
                    first,
                    _SELF_TEST_BUCKET,
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                )
            _assert(
                _REPLACEMENT_FRAGMENT not in opening.getvalue(),
                "the first landing named a replacement",
            )
            with _captured_stderr() as replacing:
                second_uri = land_record(
                    second,
                    _SELF_TEST_BUCKET,
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                )
            notice = replacing.getvalue()
            _assert_in(_REPLACEMENT_FRAGMENT, notice, "the replacement notice")
            _assert_in(
                _REPLACEMENT_SEQUENCE_FRAGMENT, notice, "the loading sequence stated"
            )
            lines = [
                line for line in notice.splitlines() if _REPLACEMENT_FRAGMENT in line
            ]
            _assert_equal(len(lines), 1, "the replacement lines the landing wrote")
            line = lines[0]
            _assert(
                line.startswith(f"{_PROGRAM}: warning: "),
                f"the replacement notice is not one warning line: {line!r}",
            )
            _assert_in(key, line, "the key the replacement notice names")
            members = _record_members(**_COMMERCIAL_CHANGES)
            for name in _WITHHELD_RECORD_MEMBERS:
                _assert(
                    str(members[name]) not in line,
                    f"the replacement notice carries the {name} value: {line!r}",
                )
            _assert_equal(second_uri, first_uri, "the URI of the replacing landing")
            _assert_equal(
                second_uri, build_object_uri(_SELF_TEST_BUCKET, key), "the landed URI"
            )
            stored = raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=key)
            _assert_equal(stored["Body"].read(), second_body, "the replaced bytes")
            listing = raw.list_objects_v2(Bucket=_SELF_TEST_BUCKET)
            _assert_equal(listing.get("KeyCount"), 2, "objects in the bucket")
            _assert_equal(
                sorted(entry["Key"] for entry in listing["Contents"]),
                sorted((key, manifest_key)),
                "the keys the two landings wrote",
            )
            manifest = json.loads(
                raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=manifest_key)["Body"]
                .read()
                .decode("ascii")
            )
            _assert_equal(
                manifest["entries"][0]["meta"]["content_length"],
                len(second_body),
                "the byte count the manifest names after the replacement",
            )
            _assert(
                "content_length" not in manifest["entries"][0],
                "the replaced manifest entry carries a top-level content_length "
                "member",
            )
    return (
        f"{len(first_body)} bytes replaced by {len(second_body)} at one key, the "
        "replacement named once and the manifest naming the bytes in the bucket"
    )


def _case_landing_parts_coexist(scratch: _Scratch) -> str:
    """Two parts of one extract date land as four objects that all stand together.

    The motor record is landed under the default part and the commercial record under
    part 1, for one source system, entity and extract date. The bucket is then required
    to carry four objects - two records and two manifests - each record byte-identical
    to the file it was landed from and each manifest naming its own record's URI and
    byte count. Neither landing writes a replacement line, because neither addresses a
    key the other wrote, which is what makes the landing zone replayable: both raw rows
    of one extract date can be rebuilt from object storage alone.
    """
    mock_aws, _ = _test_collaborators()
    first = scratch.write("record-part-0000.json", _motor_record_text())
    second = scratch.write(
        "record-part-0001.json", _motor_record_text(**_COMMERCIAL_CHANGES)
    )
    bodies = {DEFAULT_PART_NUMBER: first.read_bytes(), 1: second.read_bytes()}
    _assert(
        bodies[DEFAULT_PART_NUMBER] != bodies[1],
        "both records of this case carry the same bytes",
    )
    with mock_aws():
        with _controlled_environment(
            scratch, AWS_DEFAULT_REGION=_SELF_TEST_REGION, **_SELF_TEST_CREDENTIALS
        ):
            raw = boto3.session.Session(region_name=_SELF_TEST_REGION).client(
                SERVICE_NAME, config=_client_config()
            )
            raw.create_bucket(
                Bucket=_SELF_TEST_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": _SELF_TEST_REGION},
            )
            landed: dict[int, str] = {}
            for part, path in ((DEFAULT_PART_NUMBER, first), (1, second)):
                with _captured_stderr() as reported:
                    landed[part] = land_record(
                        path,
                        _SELF_TEST_BUCKET,
                        DEFAULT_SOURCE_SYSTEM_KEY,
                        LANDING_ENTITY,
                        _SELF_TEST_EXTRACT_DATE,
                        part=part,
                    )
                _assert(
                    _REPLACEMENT_FRAGMENT not in reported.getvalue(),
                    f"landing part {part} named a replacement",
                )
            expected_keys: list[str] = []
            for part, body in bodies.items():
                key = build_landing_key(
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                    part,
                )
                manifest_key = build_manifest_key(
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                    part,
                )
                expected_keys.extend((key, manifest_key))
                _assert_equal(
                    landed[part],
                    build_object_uri(_SELF_TEST_BUCKET, key),
                    f"the URI of part {part}",
                )
                _assert_equal(
                    raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=key)["Body"].read(),
                    body,
                    f"the stored bytes of part {part}",
                )
                manifest = json.loads(
                    raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=manifest_key)["Body"]
                    .read()
                    .decode("ascii")
                )
                entries = manifest["entries"]
                _assert_equal(len(entries), 1, f"manifest entries of part {part}")
                _assert_equal(
                    entries[0]["url"],
                    build_object_uri(_SELF_TEST_BUCKET, key),
                    f"the URI the manifest of part {part} names",
                )
                _assert_equal(
                    entries[0]["meta"]["content_length"],
                    len(body),
                    f"the byte count the manifest of part {part} names",
                )
            listing = raw.list_objects_v2(
                Bucket=_SELF_TEST_BUCKET,
                Prefix=build_landing_prefix(
                    DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
                ),
            )
            _assert_equal(listing.get("KeyCount"), 4, "objects under one prefix")
            _assert_equal(
                sorted(entry["Key"] for entry in listing["Contents"]),
                sorted(expected_keys),
                "the keys the two landings wrote",
            )
            with _captured_stderr() as replacing:
                land_record(
                    first,
                    _SELF_TEST_BUCKET,
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                    part=DEFAULT_PART_NUMBER,
                )
            notice = replacing.getvalue()
            _assert_in(
                _REPLACEMENT_FRAGMENT, notice, "the notice of a repeated same part"
            )
            _assert_in(
                _REPLACEMENT_SEQUENCE_FRAGMENT, notice, "the part contract stated"
            )
            still_there = raw.list_objects_v2(Bucket=_SELF_TEST_BUCKET)
            _assert_equal(
                still_there.get("KeyCount"), 4, "objects after the repeated landing"
            )
            _assert_equal(
                raw.get_object(
                    Bucket=_SELF_TEST_BUCKET,
                    Key=build_landing_key(
                        DEFAULT_SOURCE_SYSTEM_KEY,
                        LANDING_ENTITY,
                        _SELF_TEST_EXTRACT_DATE,
                        1,
                    ),
                )["Body"].read(),
                bodies[1],
                "the bytes of part 1 after part 0000 was landed again",
            )
    return (
        "2 records and 2 manifests coexist under one prefix, and a repeated landing "
        "of one part replaced that part alone"
    )


def _case_landing_replacement_probe_non_fatal(scratch: _Scratch) -> str:
    """A head request that does not answer writes no notice and fails no landing.

    The head request is put to a stubbed client that answers it, to one refusing it with
    each answer a service gives, and to a client raising a failure no client models.
    A landing is then driven end to end through a client whose head request raises, over
    a key that already carries an object, and is required to succeed silently and to
    replace the bytes at that key.
    """
    mock_aws, Stubber = _test_collaborators()
    key = build_landing_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    client = _stubbed_client()
    with Stubber(client) as stubber:
        stubber.add_response(
            "head_object", {}, {"Bucket": _SELF_TEST_BUCKET, "Key": key}
        )
        with _captured_stderr() as answered:
            noted = note_object_replaced(client, _SELF_TEST_BUCKET, key)
        stubber.assert_no_pending_responses()
    _assert_equal(noted, True, "the answer for a key carrying an object")
    _assert_in(_REPLACEMENT_FRAGMENT, answered.getvalue(), "the replacement notice")
    refusals = (
        ("404", 404),
        ("NoSuchKey", 404),
        ("AccessDenied", 403),
        ("InternalError", 500),
    )
    for code, status in refusals:
        client = _stubbed_client()
        with Stubber(client) as stubber:
            stubber.add_client_error(
                "head_object", service_error_code=code, http_status_code=status
            )
            with _captured_stderr() as refused:
                answer = note_object_replaced(client, _SELF_TEST_BUCKET, key)
        _assert_equal(
            answer, False, f"the answer for a head request refused with {code}"
        )
        _assert_equal(
            refused.getvalue(), "", f"what a head request refused with {code} wrote"
        )
    unmodelled = _RefusingHeadClient(
        _stubbed_client(), RuntimeError("the head request did not answer")
    )
    with _captured_stderr() as silent:
        _assert_equal(
            note_object_replaced(unmodelled, _SELF_TEST_BUCKET, key),
            False,
            "the answer for a head request raising a failure no client models",
        )
    _assert_equal(silent.getvalue(), "", "what a head request that raised wrote")

    first = scratch.write("record-probe-first.json", _motor_record_text())
    second = scratch.write(
        "record-probe-second.json", _motor_record_text(**_COMMERCIAL_CHANGES)
    )
    second_body = second.read_bytes()
    original = globals()["resolve_s3_access"]

    def _refusing_access(*arguments: Any, **keywords: Any) -> Any:
        """Return the client the tool resolves, with a head request that raises."""
        return _RefusingHeadClient(
            original(*arguments, **keywords),
            RuntimeError("the head request did not answer"),
        )

    with mock_aws():
        with _controlled_environment(
            scratch, AWS_DEFAULT_REGION=_SELF_TEST_REGION, **_SELF_TEST_CREDENTIALS
        ):
            raw = boto3.session.Session(region_name=_SELF_TEST_REGION).client(
                SERVICE_NAME, config=_client_config()
            )
            raw.create_bucket(
                Bucket=_SELF_TEST_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": _SELF_TEST_REGION},
            )
            with _captured_stderr():
                land_record(
                    first,
                    _SELF_TEST_BUCKET,
                    DEFAULT_SOURCE_SYSTEM_KEY,
                    LANDING_ENTITY,
                    _SELF_TEST_EXTRACT_DATE,
                )
            globals()["resolve_s3_access"] = _refusing_access
            try:
                run = _run_cli(
                    scratch,
                    [
                        "--record",
                        str(second),
                        "--bucket",
                        _SELF_TEST_BUCKET,
                        "--run-mode",
                        RUN_MODE_REAL,
                        "--extract-date",
                        _SELF_TEST_EXTRACT_DATE.isoformat(),
                    ],
                    AWS_DEFAULT_REGION=_SELF_TEST_REGION,
                    **_SELF_TEST_CREDENTIALS,
                )
            finally:
                globals()["resolve_s3_access"] = original
            _assert_equal(
                run.status, EXIT_OK, "the status of a landing whose head request raised"
            )
            _assert_equal(
                run.stdout.strip(),
                build_object_uri(_SELF_TEST_BUCKET, key),
                "the URI the landing wrote to stdout",
            )
            _assert(
                _REPLACEMENT_FRAGMENT not in run.stderr,
                f"a head request that raised named a replacement: {run.stderr!r}",
            )
            _assert_equal(
                raw.get_object(Bucket=_SELF_TEST_BUCKET, Key=key)["Body"].read(),
                second_body,
                "the bytes stored after a landing whose head request raised",
            )
    return (
        f"1 answered head request noted, {len(refusals)} refused and 1 raising "
        "swallowed, a landing over an existing object still successful and silent"
    )


def _case_upload_failure_reported(scratch: _Scratch) -> str:
    """A record or manifest upload the endpoint refuses is reported with its key."""
    _, Stubber = _test_collaborators()
    client = _stubbed_client()
    key = build_landing_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    with Stubber(client) as stubber:
        stubber.add_client_error(
            "put_object", service_error_code="AccessDenied", http_status_code=403
        )
        error = _assert_raises(
            "an upload the endpoint refuses",
            AccessError,
            "not permitted",
            lambda: put_record(client, _SELF_TEST_BUCKET, key, b"{}\n"),
        )
    _assert_equal(error.exit_status, EXIT_S3_UNAVAILABLE, "the status of the failure")
    client = _stubbed_client()
    with Stubber(client) as stubber:
        stubber.add_response(
            "put_object",
            {},
            {
                "Bucket": _SELF_TEST_BUCKET,
                "Key": key,
                "Body": b"{}\n",
                "ContentType": OBJECT_CONTENT_TYPE,
                "Metadata": recorded_object_metadata(b"{}\n"),
            },
        )
        put_record(client, _SELF_TEST_BUCKET, key, b"{}\n")
        stubber.assert_no_pending_responses()
    manifest_key = build_manifest_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    manifest = build_copy_manifest(
        build_object_uri(_SELF_TEST_BUCKET, key), 499
    ).encode("ascii")
    client = _stubbed_client()
    with Stubber(client) as stubber:
        stubber.add_client_error(
            "put_object", service_error_code="AccessDenied", http_status_code=403
        )
        manifest_error = _assert_raises(
            "a manifest upload the endpoint refuses",
            AccessError,
            "not permitted",
            lambda: put_manifest(
                client, _SELF_TEST_BUCKET, manifest_key, manifest
            ),
        )
    _assert(
        MANIFEST_OBJECT_NAME in str(manifest_error),
        f"the manifest failure {str(manifest_error)!r} does not name the manifest key",
    )
    _assert_equal(
        manifest_error.exit_status,
        EXIT_S3_UNAVAILABLE,
        "the status of the manifest failure",
    )
    client = _stubbed_client()
    with Stubber(client) as stubber:
        stubber.add_response(
            "put_object",
            {},
            {
                "Bucket": _SELF_TEST_BUCKET,
                "Key": manifest_key,
                "Body": manifest,
                "ContentType": OBJECT_CONTENT_TYPE,
            },
        )
        put_manifest(client, _SELF_TEST_BUCKET, manifest_key, manifest)
        stubber.assert_no_pending_responses()
    return (
        "record and manifest upload failures reported, both sets of upload parameters "
        "confirmed against the model"
    )


def _case_keys_built() -> str:
    """The landing key, the manifest key and the object URI carry the documented shape."""
    key = build_landing_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    _assert_equal(
        key,
        "landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/"
        "extract_date=2026-08-19/part-0000.json",
        "the landing key",
    )
    manifest = build_manifest_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    _assert_equal(
        manifest,
        key[: -len(OBJECT_NAME)] + MANIFEST_OBJECT_NAME,
        "the manifest key",
    )
    _assert_equal(
        build_object_uri(_SELF_TEST_BUCKET, key),
        f"s3://{_SELF_TEST_BUCKET}/{key}",
        "the object URI",
    )
    for segment in ("with/separator", "with=equals", "with space", "", "s" * 65):
        _assert_raises(
            f"the key segment {segment!r}",
            ConfigurationError,
            "",
            lambda segment=segment: build_landing_key(
                segment, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
            ),
        )
    return "landing, manifest and URI shapes confirmed; 5 segments refused"


def _case_part_option_resolved() -> str:
    """The part element resolves, names its own objects and refuses every other value.

    The key a caller that names no part builds is required to equal the key of the
    default part character for character, so the object name of a landing that names no
    part is the one the landing contract has always fixed.
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
        "the key of a caller naming no part",
    )
    _assert_equal(
        build_manifest_key(
            DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
        ),
        build_manifest_key(
            DEFAULT_SOURCE_SYSTEM_KEY,
            LANDING_ENTITY,
            _SELF_TEST_EXTRACT_DATE,
            DEFAULT_PART_NUMBER,
        ),
        "the manifest key of a caller naming no part",
    )
    for supplied, expected in (
        ("0", 0),
        ("0000", 0),
        ("1", 1),
        ("0001", 1),
        ("42", 42),
        ("9999", MAX_PART_NUMBER),
    ):
        _assert_equal(resolve_part(supplied), expected, f"the part from {supplied!r}")
    _assert_equal(object_name(0), OBJECT_NAME, "the object name of the default part")
    _assert_equal(
        manifest_object_name(0),
        MANIFEST_OBJECT_NAME,
        "the manifest name of the default part",
    )
    _assert_equal(object_name(1), "part-0001.json", "the object name of part 1")
    _assert_equal(
        manifest_object_name(1),
        "part-0001.manifest.json",
        "the manifest name of part 1",
    )
    _assert_equal(
        object_name(MAX_PART_NUMBER), "part-9999.json", "the object name of part 9999"
    )
    prefix = build_landing_prefix(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    _assert_equal(
        prefix,
        "landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/"
        "extract_date=2026-08-19/",
        "the landing prefix",
    )
    _assert_equal(
        len(prefix.rstrip(KEY_SEPARATOR).split(KEY_SEPARATOR)),
        len(PARTITION_FIELDS) + 1,
        "the segments of the landing prefix",
    )
    for part in (1, MAX_PART_NUMBER):
        key = build_landing_key(
            DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE, part
        )
        _assert_equal(key, f"{prefix}{object_name(part)}", f"the key of part {part}")
        _assert_equal(
            build_manifest_key(
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                part,
            ),
            f"{prefix}{manifest_object_name(part)}",
            f"the manifest key of part {part}",
        )
    refused_settings = (
        "-1",
        "1.0",
        "0x1",
        "00001",
        "10000",
        " 1",
        "1 ",
        "",
        "one",
        "1e3",
        "+1",
        "١",
    )
    for supplied in refused_settings:
        _assert_raises(
            f"the part setting {supplied!r}",
            ConfigurationError,
            "--part",
            lambda supplied=supplied: resolve_part(supplied),
        )
    refused_numbers: tuple[Any, ...] = (
        -1,
        MAX_PART_NUMBER + 1,
        True,
        "0000",
        None,
        1.0,
    )
    for value in refused_numbers:
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
    return (
        f"{len(refused_settings)} part settings and {len(refused_numbers)} part "
        "numbers refused; the default part key is unchanged"
    )


def _case_render_identity() -> str:
    """The object identity is derived from the record's own bytes, with overrides."""
    body = _motor_record_text().encode("utf-8")
    identity = object_identity(body)
    _assert_equal(identity.content_length, len(body), "the recorded byte count")
    _assert_equal(
        identity.sha256, hashlib.sha256(body).hexdigest(), "the recorded digest"
    )
    _assert_equal(
        identity.etag,
        hashlib.md5(body, usedforsecurity=False).hexdigest(),
        "the recorded ETag",
    )
    _assert_equal(identity.version_id, NOT_VERSIONED, "the recorded version")
    quoted = object_identity(
        body, etag='"d41d8cd98f00b204e9800998ecf8427e"', version_id="aBc.1_2-3"
    )
    _assert_equal(
        quoted.etag, "d41d8cd98f00b204e9800998ecf8427e", "a quoted ETag as recorded"
    )
    _assert_equal(quoted.version_id, "aBc.1_2-3", "a supplied version id")
    _assert_raises(
        "an ETag that is not a hex digest",
        ConfigurationError,
        "hex characters",
        lambda: object_identity(body, etag="not-a-digest"),
    )
    _assert_raises(
        "a version id carrying a quote",
        ConfigurationError,
        "not accepted",
        lambda: object_identity(body, version_id="a'b"),
    )
    return f"{identity.content_length} bytes, digest and ETag derived"


def _case_render_fixture_bytes(scratch: _Scratch) -> str:
    """A successful render equals the expected text byte for byte."""
    path = scratch.write("record-render.json", _motor_record_text())
    record = parse_record(read_record_bytes(path), path)
    columns = read_column_names(load_schema(), DEFAULT_SCHEMA)
    rendered = render_redshift_load(
        _FIXTURE_TEMPLATE_TEXT, _FIXTURE_VALUES, record, columns
    )
    if rendered.sql != _FIXTURE_RENDERED_TEXT:
        for index, (observed, expected) in enumerate(
            zip(rendered.sql.splitlines(), _FIXTURE_RENDERED_TEXT.splitlines())
        ):
            if observed != expected:
                raise _SelfTestFailure(
                    f"rendered line {index + 1} is {observed!r}, expected {expected!r}"
                )
        raise _SelfTestFailure(
            f"the rendered load holds {len(rendered.sql)} characters, expected "
            f"{len(_FIXTURE_RENDERED_TEXT)}"
        )
    _assert(
        PLACEHOLDER_OPENER not in rendered.sql,
        "the rendered load still carries a placeholder opener",
    )
    _assert(
        PLACEHOLDER_OPENER not in rendered.manifest,
        "the rendered manifest still carries a placeholder opener",
    )
    _assert_equal(
        rendered.object_key,
        build_landing_key(
            DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
        ),
        "the object key the render bound to",
    )
    return f"{len(rendered.sql)} characters rendered byte for byte"


def _case_render_real_template(scratch: _Scratch) -> str:
    """Rendering the authored template gives the documented statements and columns."""
    path = scratch.write("record-real.json", _motor_record_text())
    body = path.read_bytes()
    with _captured_stderr():
        sql = render_redshift_document(
            RENDER_DOCUMENT_SQL,
            path,
            _SELF_TEST_BUCKET,
            DEFAULT_SOURCE_SYSTEM_KEY,
            LANDING_ENTITY,
            _SELF_TEST_EXTRACT_DATE,
            _SELF_TEST_REGION,
            _SELF_TEST_IAM_ROLE,
        )
    _assert(
        PLACEHOLDER_OPENER not in sql,
        "the rendered authored template still carries a placeholder opener",
    )
    statements = split_sql_statements(sql, "rendered Redshift load")
    keywords = tuple(_statement_keyword(statement) for statement in statements)
    _assert_equal(
        keywords,
        RENDERED_AUTHORED_SEQUENCE,
        "the rendered statement sequence of the authored template",
    )
    columns = read_column_names(load_schema(), DEFAULT_SCHEMA)
    copy_statement = statements[keywords.index("COPY")]
    _assert_equal(
        _copy_column_names(copy_statement), columns, "the rendered COPY column list"
    )
    delete_code = " ".join(
        _statement_code(statements[keywords.index("DELETE")]).split()
    )
    # The authored template binds the natural key as parameters, so neither value
    # reaches statement text; a template that substitutes them must carry the record's
    # own values instead.
    for field, value, marker in (
        (SOURCE_SYSTEM_KEY_FIELD, DEFAULT_SOURCE_SYSTEM_KEY, DELETE_BOUND_MARKERS[0]),
        (
            POLICY_NUMBER_FIELD,
            dict(_MOTOR_RECORD_MEMBERS)[POLICY_NUMBER_FIELD],
            DELETE_BOUND_MARKERS[1],
        ),
    ):
        _assert(
            marker in delete_code or f"{field} = '{value}'" in delete_code,
            f"the rendered delete guard keys {field} neither on {marker} nor on the "
            f"record's own value",
        )
    manifest_uri = build_object_uri(
        _SELF_TEST_BUCKET,
        build_manifest_key(
            DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
        ),
    )
    copy_code = " ".join(_statement_code(copy_statement).split())
    _assert_in(f"'{manifest_uri}'", copy_code, "the rendered COPY source")
    _assert_in(" MANIFEST", copy_code.upper(), "the rendered COPY options")
    _assert_in(f"'{_SELF_TEST_IAM_ROLE}'", copy_code, "the rendered COPY credentials")
    _assert_in(f"'{_SELF_TEST_REGION}'", copy_code, "the rendered COPY region")
    identity = object_identity(body)
    for recorded in (str(identity.content_length), identity.sha256, identity.etag):
        _assert_in(recorded, sql, "the rendered object identity")
    _assert_equal(
        sql.count(f"'{manifest_uri}'"), 1, "manifest references in the rendered load"
    )
    return (
        f"{len(statements)} statements, {len(columns)} columns, identity "
        f"{identity.content_length} bytes recorded"
    )


def _case_render_manifest(scratch: _Scratch) -> str:
    """The rendered manifest binds the load to the validated object and its length."""
    path = scratch.write("record-manifest.json", _motor_record_text())
    body = path.read_bytes()
    with _captured_stderr():
        text = render_redshift_document(
            RENDER_DOCUMENT_MANIFEST,
            path,
            _SELF_TEST_BUCKET,
            DEFAULT_SOURCE_SYSTEM_KEY,
            LANDING_ENTITY,
            _SELF_TEST_EXTRACT_DATE,
            _SELF_TEST_REGION,
            _SELF_TEST_IAM_ROLE,
        )
    document = parse_json_document(text)
    _assert_equal(tuple(document), ("entries",), "the manifest members")
    entries = document["entries"]
    _assert_equal(len(entries), 1, "manifest entries")
    entry = entries[0]
    _assert_equal(tuple(entry), ("url", "mandatory", "meta"), "the entry members")
    _assert_equal(tuple(entry["meta"]), ("content_length",), "the entry meta members")
    _assert(
        "content_length" not in entry,
        "the entry carries a top-level content_length member beside its meta",
    )
    object_key = build_landing_key(
        DEFAULT_SOURCE_SYSTEM_KEY, LANDING_ENTITY, _SELF_TEST_EXTRACT_DATE
    )
    _assert_equal(
        entry["url"],
        build_object_uri(_SELF_TEST_BUCKET, object_key),
        "the entry URL",
    )
    _assert_equal(entry["mandatory"], True, "the entry mandatory flag")
    _assert_equal(
        entry["meta"]["content_length"], len(body), "the entry content length"
    )
    _assert(
        MANIFEST_OBJECT_NAME not in entry["url"],
        "the manifest names itself instead of the landed object",
    )
    return f"one mandatory entry pinned to {len(body)} bytes"


def _case_render_non_default_part(scratch: _Scratch) -> str:
    """A load and a manifest rendered for a non-default part name that part's object.

    Both documents are rendered for part 1 through the authored template, and each is
    required to name the object and the manifest of part 1 and no other object under the
    prefix, with the byte count of the record's own bytes. The same record rendered for
    the default part is required to name the default object, so the part reaches the
    rendered documents from the setting alone.
    """
    path = scratch.write("record-part.json", _motor_record_text())
    body = path.read_bytes()
    rendered: dict[int, tuple[str, str]] = {}
    for part in (DEFAULT_PART_NUMBER, 1):
        with _captured_stderr():
            sql = render_redshift_document(
                RENDER_DOCUMENT_SQL,
                path,
                _SELF_TEST_BUCKET,
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                _SELF_TEST_REGION,
                _SELF_TEST_IAM_ROLE,
                part=part,
            )
            manifest = render_redshift_document(
                RENDER_DOCUMENT_MANIFEST,
                path,
                _SELF_TEST_BUCKET,
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                _SELF_TEST_REGION,
                _SELF_TEST_IAM_ROLE,
                part=part,
            )
        rendered[part] = (sql, manifest)
        object_uri = build_object_uri(
            _SELF_TEST_BUCKET,
            build_landing_key(
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                part,
            ),
        )
        manifest_uri = build_object_uri(
            _SELF_TEST_BUCKET,
            build_manifest_key(
                DEFAULT_SOURCE_SYSTEM_KEY,
                LANDING_ENTITY,
                _SELF_TEST_EXTRACT_DATE,
                part,
            ),
        )
        _assert_equal(
            sql.count(f"'{manifest_uri}'"),
            1,
            f"manifest references of the load of part {part}",
        )
        _assert_in(
            f"part-{part_number_text(part)}.json",
            sql,
            f"the object the load of part {part} records",
        )
        entry = parse_json_document(manifest)["entries"][0]
        _assert_equal(entry["url"], object_uri, f"the URI the manifest of {part} names")
        _assert_equal(
            entry["meta"]["content_length"],
            len(body),
            f"the byte count the manifest of part {part} names",
        )
    other_name = f"part-{part_number_text(1)}"
    _assert(
        other_name not in rendered[DEFAULT_PART_NUMBER][0],
        f"the load of the default part names {other_name}",
    )
    _assert(
        other_name not in rendered[DEFAULT_PART_NUMBER][1],
        f"the manifest of the default part names {other_name}",
    )
    for supplied in ("1", "00001", "10000", "-1", "x"):
        _assert_raises(
            f"the LANDING_PART value {supplied!r}",
            ConfigurationError,
            "LANDING_PART",
            lambda supplied=supplied: _validated_placeholder(
                "LANDING_PART", supplied
            ),
        )
    return "the load and the manifest of part 0001 name that part's object alone"


def _case_render_rejects_hostile_values() -> str:
    """No placeholder accepts a quote, a comment, a separator or a control character."""
    refused = 0
    for name in SUPPORTED_PLACEHOLDERS:
        for what, value in _HOSTILE_PLACEHOLDER_VALUES:
            _assert_raises(
                f"the {name} placeholder carrying a {what}",
                ConfigurationError,
                "",
                lambda name=name, value=value: _validated_placeholder(name, value),
            )
            refused += 1
    _assert_raises(
        "a placeholder value that is not a string",
        ConfigurationError,
        "a non-empty string is required",
        lambda: _validated_placeholder("S3_BUCKET", 7),
    )
    _assert_raises(
        "an unsupported placeholder name",
        ConfigurationError,
        "is not a placeholder",
        lambda: _validated_placeholder("DROP_TABLE", "x"),
    )
    for name, value in (
        ("S3_BUCKET", "Upper-Case"),
        ("S3_BUCKET", "ab"),
        ("S3_BUCKET", "a..b"),
        ("S3_BUCKET", "127.0.0.1"),
        ("SOURCE_SYSTEM_KEY", "key with space"),
        ("ENTITY", "e" * 65),
        ("EXTRACT_DATE", "2026-02-30"),
        ("EXTRACT_DATE", "2026-8-19"),
        ("POLICY_NUMBER", "12345678901"),
        ("POLICY_NUMBER", "100A301"),
        ("REDSHIFT_IAM_ROLE", "arn:aws:iam::12345:role/short-account"),
        ("REDSHIFT_IAM_ROLE", "genapp-rqi-redshift-copy"),
        ("AWS_REGION", "EU-WEST-2"),
        ("AWS_REGION", "eu_west_2"),
        ("OBJECT_CONTENT_LENGTH", "0499"),
        ("OBJECT_CONTENT_LENGTH", "many"),
        ("OBJECT_SHA256", "abc"),
        ("OBJECT_ETAG", "D41D8CD98F00B204E9800998ECF8427E"),
        ("OBJECT_VERSION_ID", "v" * 1025),
    ):
        _assert_raises(
            f"the {name} placeholder carrying {value!r}",
            ConfigurationError,
            "is not accepted",
            lambda name=name, value=value: _validated_placeholder(name, value),
        )
        refused += 1
    _assert_equal(
        _sql_literal_body("SOURCE_SYSTEM_KEY", "already''doubled"),
        "already''''doubled",
        "the escape a value reaching a literal receives",
    )
    return f"{refused} placeholder values refused"


def _case_render_rejects_mismatch(scratch: _Scratch) -> str:
    """A rendered key or delete guard that is not the record's own is refused."""
    path = scratch.write("record-mismatch.json", _motor_record_text())
    record = parse_record(read_record_bytes(path), path)
    columns = read_column_names(load_schema(), DEFAULT_SCHEMA)
    for name, value, fragment in (
        ("SOURCE_SYSTEM_KEY", "OTHER_SYSTEM", SOURCE_SYSTEM_KEY_FIELD),
        ("POLICY_NUMBER", "9999999", POLICY_NUMBER_FIELD),
    ):
        values = dict(_FIXTURE_VALUES)
        values[name] = value
        _assert_raises(
            f"a render carrying {value!r} as {name}",
            ConfigurationError,
            fragment,
            lambda values=values: render_redshift_load(
                _FIXTURE_TEMPLATE_TEXT, values, record, columns
            ),
        )
    hostile = dict(_FIXTURE_VALUES)
    hostile["SOURCE_SYSTEM_KEY"] = "KEY';DROP TABLE raw.genapp_policy_issue;--"
    _assert_raises(
        "a render carrying a statement in a placeholder",
        ConfigurationError,
        "is not accepted",
        lambda: render_redshift_load(
            _FIXTURE_TEMPLATE_TEXT, hostile, record, columns
        ),
    )
    return "2 key mismatches and 1 injected statement refused"


def _case_render_rejects_template_faults(scratch: _Scratch) -> str:
    """A template or a value set that cannot be substituted safely is refused."""
    path = scratch.write("record-template.json", _motor_record_text())
    record = parse_record(read_record_bytes(path), path)
    columns = read_column_names(load_schema(), DEFAULT_SCHEMA)

    def _rendered(template: str, values: Mapping[str, Any] | None = None) -> Any:
        """Render ``template`` for the fixture record."""
        return render_redshift_load(
            template, _FIXTURE_VALUES if values is None else values, record, columns
        )

    checks = (
        (
            "a template carrying an unsupported placeholder",
            _FIXTURE_TEMPLATE_TEXT + "-- ${DROP_EVERYTHING}\n",
            None,
            "unsupported placeholder",
        ),
        (
            "a template leaving a placeholder unterminated",
            _FIXTURE_TEMPLATE_TEXT + "-- ${S3_BUCKET\n",
            None,
            "unterminated",
        ),
        (
            "a template carrying no region placeholder",
            _FIXTURE_TEMPLATE_TEXT.replace("${AWS_REGION}", "eu-west-2"),
            None,
            "carries no AWS_REGION placeholder",
        ),
        (
            "a value set omitting a placeholder",
            _FIXTURE_TEMPLATE_TEXT,
            {
                name: value
                for name, value in _FIXTURE_VALUES.items()
                if name != "OBJECT_ETAG"
            },
            "no value was supplied",
        ),
        (
            "a value set carrying an unsupported placeholder",
            _FIXTURE_TEMPLATE_TEXT,
            {**_FIXTURE_VALUES, "EXTRA_VALUE": "x"},
            "unsupported placeholder",
        ),
        (
            "a template whose statements are not the documented sequence",
            _FIXTURE_TEMPLATE_TEXT.replace("BEGIN;\n", ""),
            None,
            "statement sequence",
        ),
        (
            "a template omitting a landed column",
            _FIXTURE_TEMPLATE_TEXT.replace("    broker_id,\n", ""),
            None,
            "lists 16 columns",
        ),
        (
            "a template reading the object instead of its manifest",
            _FIXTURE_TEMPLATE_TEXT.replace(
                "part-${LANDING_PART}.manifest.json", "part-${LANDING_PART}.json"
            ),
            None,
            "does not read the manifest",
        ),
        (
            "a template reading no manifest",
            _FIXTURE_TEMPLATE_TEXT.replace("MANIFEST\n", ""),
            None,
            "does not read its object list from a manifest",
        ),
        (
            "a template whose delete guard drops the policy number",
            _FIXTURE_TEMPLATE_TEXT.replace(
                "   AND policy_number = '${POLICY_NUMBER}';",
                ";\n-- ${POLICY_NUMBER}",
            ),
            None,
            "does not match 'policy_number'",
        ),
    )
    for what, template, values, fragment in checks:
        _assert_raises(
            what,
            (TemplateError, ConfigurationError),
            fragment,
            lambda template=template, values=values: _rendered(template, values),
        )
    _assert_raises(
        "a missing template file",
        TemplateError,
        "cannot be read",
        lambda: read_template(scratch.absent("no-such-template.sql")),
    )
    _assert_raises(
        "a template that is not valid UTF-8",
        TemplateError,
        "not valid UTF-8",
        lambda: read_template(scratch.write("template-bytes.sql", b"\xff\xfe")),
    )
    _assert_raises(
        "a document name that is not a rendered document",
        UsageError,
        "are accepted",
        lambda: render_redshift_document(
            "csv",
            path,
            _SELF_TEST_BUCKET,
            DEFAULT_SOURCE_SYSTEM_KEY,
            LANDING_ENTITY,
            _SELF_TEST_EXTRACT_DATE,
            _SELF_TEST_REGION,
            _SELF_TEST_IAM_ROLE,
        ),
    )
    return f"{len(checks) + 3} template faults refused"


def _case_sql_split_matrix() -> str:
    """Statement boundaries are read outside literals, identifiers and comments."""
    checks = (
        ("BEGIN;\nCOMMIT;\n", 2),
        ("SELECT ';' AS semicolon_in_a_literal;", 1),
        ("-- a comment; with a semicolon\nSELECT 1;", 1),
        ("/* a; /* nested */ comment; */ SELECT 1;", 1),
        ("SELECT 1", 1),
        ("-- only a comment\n", 0),
        ("SELECT \"quoted;identifier\";", 1),
        ("SELECT 'it''s here; still one';", 1),
        ("BEGIN;\n\n;\nCOMMIT;\n", 2),
    )
    for text, expected in checks:
        observed = split_sql_statements(text, "self-test text")
        _assert_equal(len(observed), expected, f"statements of {text!r}")
    for text, construct in (
        ("SELECT 'unterminated", "quoted literal"),
        ('SELECT "unterminated', "quoted identifier"),
        ("/* unterminated", "block comment"),
    ):
        _assert_raises(
            f"the text {text!r}",
            TemplateError,
            construct,
            lambda text=text: split_sql_statements(text, "self-test text"),
        )
    _assert_equal(
        _statement_keyword("-- leading comment\n/* another */\n  copy raw.t (a)"),
        "COPY",
        "the keyword behind two comments",
    )
    _assert_equal(
        _copy_column_names("COPY raw.t (\n a, -- first\n b\n)"),
        ("a", "b"),
        "columns read past a comment",
    )
    return f"{len(checks)} split cases and 3 unterminated constructs"


def _case_render_cli(scratch: _Scratch) -> str:
    """The render mode writes one document, needing no credential and no endpoint."""
    path = scratch.write("record-cli.json", _motor_record_text())
    arguments = [
        "--record",
        str(path),
        "--bucket",
        _SELF_TEST_BUCKET,
        "--region",
        _SELF_TEST_REGION,
        "--iam-role",
        _SELF_TEST_IAM_ROLE,
        "--extract-date",
        _SELF_TEST_EXTRACT_DATE.isoformat(),
    ]
    sql_run = _run_cli(
        scratch, ["--render-redshift-load", RENDER_DOCUMENT_SQL, *arguments]
    )
    _assert_equal(sql_run.status, EXIT_OK, "the status of a rendered load")
    _assert(
        PLACEHOLDER_OPENER not in sql_run.stdout,
        "the rendered load on stdout still carries a placeholder opener",
    )
    _assert_in("COPY genapp_policy_issue_load", sql_run.stdout, "the rendered load")
    _assert_in(
        "INSERT INTO raw.genapp_policy_issue",
        sql_run.stdout,
        "the rendered promotion",
    )
    _assert(
        sql_run.stdout.endswith("COMMIT;\n"),
        f"the rendered load ends {sql_run.stdout[-40:]!r}",
    )
    manifest_run = _run_cli(
        scratch, ["--render-redshift-load", RENDER_DOCUMENT_MANIFEST, *arguments]
    )
    _assert_equal(manifest_run.status, EXIT_OK, "the status of a rendered manifest")
    document = parse_json_document(manifest_run.stdout)
    _assert_equal(
        document["entries"][0]["meta"]["content_length"],
        len(path.read_bytes()),
        "the content length on stdout",
    )
    _assert(
        "content_length" not in document["entries"][0],
        "the manifest on stdout carries a top-level content_length member",
    )
    for extra, fragment, status in (
        ([], f"{IAM_ROLE_VARIABLE} environment variable", EXIT_CONFIGURATION_REJECTED),
    ):
        run = _run_cli(
            scratch,
            [
                "--render-redshift-load",
                RENDER_DOCUMENT_SQL,
                "--record",
                str(path),
                "--bucket",
                _SELF_TEST_BUCKET,
                "--region",
                _SELF_TEST_REGION,
                *extra,
            ],
        )
        _assert_equal(run.status, status, "the status of a render without a role")
        _assert_in(fragment, run.stderr, "the diagnostic naming the missing role")
    no_region = _run_cli(
        scratch,
        [
            "--render-redshift-load",
            RENDER_DOCUMENT_SQL,
            "--record",
            str(path),
            "--bucket",
            _SELF_TEST_BUCKET,
            "--iam-role",
            _SELF_TEST_IAM_ROLE,
        ],
    )
    _assert_equal(
        no_region.status, EXIT_CONFIGURATION_REJECTED, "the status without a region"
    )
    _assert_in("no region is resolved", no_region.stderr, "the region diagnostic")
    from_environment = _run_cli(
        scratch,
        ["--render-redshift-load", RENDER_DOCUMENT_SQL, "--record", str(path)],
        S3_BUCKET=_SELF_TEST_BUCKET,
        AWS_REGION=_SELF_TEST_REGION,
        REDSHIFT_IAM_ROLE=_SELF_TEST_IAM_ROLE,
        SOURCE_SYSTEM_KEY=DEFAULT_SOURCE_SYSTEM_KEY,
    )
    _assert_equal(
        from_environment.status, EXIT_OK, "the status of a render from the environment"
    )
    _assert_in(
        f"'{_SELF_TEST_REGION}'", from_environment.stdout, "the rendered region"
    )
    with_part = _run_cli(
        scratch,
        ["--render-redshift-load", RENDER_DOCUMENT_SQL, "--part", "1", *arguments],
    )
    _assert_equal(with_part.status, EXIT_OK, "the status of a render naming a part")
    _assert_in(
        "part-0001.manifest.json", with_part.stdout, "the manifest the part reads"
    )
    _assert(
        "part-0000" not in with_part.stdout,
        "the render of part 1 names the default part",
    )
    refused_part = _run_cli(
        scratch,
        [
            "--render-redshift-load",
            RENDER_DOCUMENT_SQL,
            "--part",
            "10000",
            *arguments,
        ],
    )
    _assert_equal(
        refused_part.status,
        EXIT_CONFIGURATION_REJECTED,
        "the status of a render naming a part outside the accepted range",
    )
    _assert_in("--part", refused_part.stderr, "the diagnostic naming the part setting")
    return (
        "sql and manifest rendered from options, from the environment and for a "
        "named part"
    )


def _case_redshift_settings_resolved(scratch: _Scratch) -> str:
    """Every Redshift setting resolves from the environment, two of them by default."""
    with _controlled_environment(scratch, **_SELF_TEST_REDSHIFT):
        settings = resolve_redshift_settings()
    for value, variable, what in (
        (settings.host, REDSHIFT_HOST_VARIABLE, "host"),
        (settings.user, REDSHIFT_USER_VARIABLE, "user"),
        (settings.password, REDSHIFT_PASSWORD_VARIABLE, "password"),
        (settings.database, REDSHIFT_DATABASE_VARIABLE, "database"),
        (settings.schema, REDSHIFT_SCHEMA_VARIABLE, "schema"),
    ):
        _assert_equal(value, _SELF_TEST_REDSHIFT[variable], f"the resolved {what}")
    _assert_equal(
        settings.port, DEFAULT_REDSHIFT_PORT, "the port with its variable unset"
    )
    _assert_equal(
        settings.connect_timeout,
        DEFAULT_REDSHIFT_CONNECT_TIMEOUT,
        "the connect timeout with its variable unset",
    )
    blank = {REDSHIFT_PORT_VARIABLE: "   ", REDSHIFT_CONNECT_TIMEOUT_VARIABLE: "\t"}
    with _controlled_environment(scratch, **_SELF_TEST_REDSHIFT, **blank):
        unset = resolve_redshift_settings()
    _assert_equal(unset.port, DEFAULT_REDSHIFT_PORT, "the port from a blank variable")
    _assert_equal(
        unset.connect_timeout,
        DEFAULT_REDSHIFT_CONNECT_TIMEOUT,
        "the connect timeout from a blank variable",
    )
    supplied = {
        REDSHIFT_PORT_VARIABLE: "5451",
        REDSHIFT_CONNECT_TIMEOUT_VARIABLE: "7",
    }
    with _controlled_environment(scratch, **_SELF_TEST_REDSHIFT, **supplied):
        carried = resolve_redshift_settings()
    _assert_equal(carried.port, 5451, "the port the environment carried")
    _assert_equal(carried.connect_timeout, 7, "the timeout the environment carried")
    shown = f"{settings!r} {settings} {settings.host!s:.0}"
    for variable, value in _SELF_TEST_REDSHIFT.items():
        _assert(
            value not in shown,
            f"a representation of the settings carries the {variable} value",
        )
    _assert_equal(
        len(settings.redacted_values()), 5, "the values withheld from a driver reason"
    )
    return (
        f"5 settings resolved, port {DEFAULT_REDSHIFT_PORT} and timeout "
        f"{DEFAULT_REDSHIFT_CONNECT_TIMEOUT} by default, no value in a representation"
    )


def _case_redshift_settings_refused(scratch: _Scratch) -> str:
    """Every unusable Redshift setting is refused by name, before any socket exists."""
    def _without(variable: str) -> dict[str, str]:
        """Return the settings with ``variable`` carrying nothing at all."""
        return {
            name: value
            for name, value in _SELF_TEST_REDSHIFT.items()
            if name != variable
        }

    def _carrying(variable: str, value: str) -> dict[str, str]:
        """Return the settings with ``variable`` carrying ``value``."""
        return {**_SELF_TEST_REDSHIFT, variable: value}

    checks: list[tuple[str, dict[str, str], str, str]] = []
    for variable, what in (
        (REDSHIFT_HOST_VARIABLE, "host"),
        (REDSHIFT_USER_VARIABLE, "user"),
        (REDSHIFT_PASSWORD_VARIABLE, "password"),
        (REDSHIFT_DATABASE_VARIABLE, "database"),
        (REDSHIFT_SCHEMA_VARIABLE, "schema"),
    ):
        absent = f"no Redshift {what} is set: set {variable}"
        checks.append((f"an absent {what}", _without(variable), absent, ""))
        checks.append((f"a blank {what}", _carrying(variable, "   "), absent, ""))
    refused_shape = "is not accepted"
    for variable, value, fragment in (
        (REDSHIFT_HOST_VARIABLE, "https://warehouse.example.aws", refused_shape),
        (REDSHIFT_HOST_VARIABLE, "warehouse.example.aws:5439", refused_shape),
        (REDSHIFT_HOST_VARIABLE, "warehouse .example.aws", refused_shape),
        (REDSHIFT_HOST_VARIABLE, "-warehouse.example.aws", refused_shape),
        (REDSHIFT_HOST_VARIABLE, "warehouse.example.aws/genapp", refused_shape),
        (REDSHIFT_HOST_VARIABLE, "w" * 260, "at most 255"),
        (REDSHIFT_HOST_VARIABLE, "127.0.0.1", "names a loopback address"),
        (REDSHIFT_HOST_VARIABLE, "127.9.9.9", "names a loopback address"),
        (REDSHIFT_HOST_VARIABLE, LOOPBACK_HOST_NAME, "names a loopback address"),
        (REDSHIFT_USER_VARIABLE, "genapp loader", refused_shape),
        (REDSHIFT_USER_VARIABLE, "u" * 130, "at most 127"),
        (REDSHIFT_DATABASE_VARIABLE, "genapp;drop", refused_shape),
        (REDSHIFT_DATABASE_VARIABLE, "genapp\ndrop", refused_shape),
        (REDSHIFT_SCHEMA_VARIABLE, "raw'--", refused_shape),
        (REDSHIFT_PASSWORD_VARIABLE, "p" * 300, "at most 256"),
        (REDSHIFT_PASSWORD_VARIABLE, "secret\npassword", "carries a control"),
    ):
        checks.append(
            (f"{variable} carrying an unusable value", _carrying(variable, value),
             fragment, value)
        )
    for variable, value in (
        (REDSHIFT_PORT_VARIABLE, "0"),
        (REDSHIFT_PORT_VARIABLE, "70000"),
        (REDSHIFT_PORT_VARIABLE, "abc"),
        (REDSHIFT_PORT_VARIABLE, "-1"),
        (REDSHIFT_PORT_VARIABLE, "54.39"),
        (REDSHIFT_CONNECT_TIMEOUT_VARIABLE, "0"),
        (REDSHIFT_CONNECT_TIMEOUT_VARIABLE, "99999"),
        (REDSHIFT_CONNECT_TIMEOUT_VARIABLE, "ten"),
    ):
        checks.append(
            (f"{variable} carrying {value!r}", _carrying(variable, value),
             "is not a decimal whole number between", "")
        )
    for what, overrides, fragment, withheld in checks:
        with _controlled_environment(scratch, **overrides):
            error = _assert_raises(
                what, ConfigurationError, fragment, resolve_redshift_settings
            )
        _assert_equal(
            error.exit_status,
            EXIT_CONFIGURATION_REJECTED,
            f"the status of {what}",
        )
        _assert_equal(
            _one_line(str(error)), str(error), f"the diagnostic of {what} as one line"
        )
        for variable, value in _SELF_TEST_REDSHIFT.items():
            _assert(
                value not in str(error),
                f"the diagnostic of {what} carries the {variable} value",
            )
        if withheld:
            _assert(
                withheld not in str(error),
                f"the diagnostic of {what} echoes the value it refused",
            )
    return f"{len(checks)} unusable Redshift settings refused by name, no value echoed"


def _case_redshift_probe_succeeds(scratch: _Scratch) -> str:
    """The probe runs SELECT 1, writes one temporary row and rolls the write back."""
    with _controlled_environment(scratch, **_SELF_TEST_REDSHIFT):
        settings = resolve_redshift_settings()
    driver = _StandInRedshiftDriver()
    with _captured_stderr() as captured:
        verdict = probe_redshift_access(settings, driver)
    _assert_equal(
        verdict,
        f"{REDSHIFT_PROBE_VERDICT} select={REDSHIFT_PROBE_STATEMENT_VALUE} "
        f"write-probe={REDSHIFT_PROBE_WRITE_OUTCOME}",
        "the probe verdict",
    )
    _assert_equal(
        driver.connect_arguments,
        {
            "host": settings.host,
            "port": DEFAULT_REDSHIFT_PORT,
            "database": settings.database,
            "user": settings.user,
            "password": settings.password,
            "timeout": DEFAULT_REDSHIFT_CONNECT_TIMEOUT,
            "ssl": True,
            "sslmode": REDSHIFT_SSL_MODE,
            "application_name": REDSHIFT_APPLICATION_NAME,
        },
        "the connection parameters the probe supplied",
    )
    _assert_equal(len(driver.connections), 1, "the connections the probe opened")
    connection = driver.connections[0]
    _assert_equal(
        connection.steps(),
        ("select", "create", "insert", "count"),
        "the steps the probe ran",
    )
    statements = [statement for statement, _ in connection.statements]
    _assert_equal(statements[0], REDSHIFT_PROBE_STATEMENT, "the connectivity statement")
    relation = statements[1].split()[3]
    _assert(
        bool(_IDENTIFIER_SHAPE.fullmatch(relation)),
        f"the probe relation {relation!r} is not one unquoted identifier",
    )
    _assert(
        relation.startswith(REDSHIFT_PROBE_RELATION_TEMPLATE.format(token="")),
        f"the probe relation {relation!r} is not named for this probe",
    )
    _assert_equal(
        statements[1],
        f"CREATE TEMPORARY TABLE {relation} "
        f"({REDSHIFT_PROBE_COLUMN} VARCHAR({REDSHIFT_PROBE_COLUMN_WIDTH}))",
        "the write probe relation statement",
    )
    _assert_equal(
        statements[2],
        f"INSERT INTO {relation} ({REDSHIFT_PROBE_COLUMN}) VALUES (%s)",
        "the write probe statement",
    )
    _assert_equal(
        connection.statements[2][1],
        (REDSHIFT_PROBE_VALUE,),
        "the value the write probe bound",
    )
    _assert_equal(
        statements[3], f"SELECT count(*) FROM {relation}", "the read-back statement"
    )
    _assert_equal(connection.rolled_back, 1, "the rollbacks the probe performed")
    _assert_equal(connection.committed, 0, "the commits the probe performed")
    _assert(connection.closed, "the probe left the connection open")
    _assert_equal(len(connection.cursors), 4, "the cursors the probe opened")
    _assert(
        all(cursor.closed for cursor in connection.cursors),
        "the probe left a cursor open",
    )
    _assert(
        build_redshift_probe_relation() != build_redshift_probe_relation(),
        "two write probes name the same relation",
    )
    reported = f"{verdict}\n{captured.getvalue()}"
    for variable, value in _SELF_TEST_REDSHIFT.items():
        _assert(
            value not in reported,
            f"the probe output carries the {variable} value",
        )
    return (
        f"{len(statements)} statements, {REDSHIFT_PROBE_ROWS} row written and rolled "
        "back, nothing provisioned, no setting value reported"
    )


def _case_redshift_reason_redaction(scratch: _Scratch) -> str:
    """A driver reason keeps its own wording while every setting value goes.

    The values are one character each, which is the shortest a setting can be and the
    length a driver's own wording carries everywhere: the reason has to lose the value
    the driver quoted, keep every word of the wording, and carry the placeholder once
    per quoted value rather than a placeholder written into a placeholder.
    """
    short = RedshiftSettings(
        host="h",
        port=5439,
        database="d",
        user="u",
        password="p",
        schema="s",
        connect_timeout=4,
    )
    reasons = (
        (
            "a name that did not resolve",
            "('communication error', gaierror(-2, 'Name or service not known'))",
            ("communication error", "gaierror", "Name or service not known"),
        ),
        (
            "a connection that timed out",
            "('connection time out', TimeoutError('timed out'))",
            ("connection time out", "TimeoutError", "timed out"),
        ),
        (
            "a quoted host, user and database",
            "could not connect to 'h' as 'u' on 'd'.'s' with password 'p'",
            ("could not connect to", "with password"),
        ),
    )
    for what, supplied, kept in reasons:
        reported = _redshift_reason(_StandInRedshiftError(supplied), short)
        for value in short.redacted_values():
            _assert(
                f"'{value}'" not in reported,
                f"the reason for {what} carries a quoted setting value",
            )
        for wording in kept:
            _assert_in(wording, reported, f"the wording of {what}")
        _assert(
            f"{REDACTED_SETTING[:2]}{REDACTED_SETTING}" not in reported,
            f"the reason for {what} carries a placeholder inside a placeholder",
        )
        _assert_equal(
            _one_line(reported), reported, f"the reason for {what} as one line"
        )
    quoted = _redshift_reason(
        _StandInRedshiftError("could not connect to 'h' as 'u' on 'd'.'s'"), short
    )
    _assert_equal(
        quoted.count(REDACTED_SETTING), 4, "the placeholders of the quoted reason"
    )
    long = _redshift_reason(
        _StandInRedshiftError("host genapp.example.com refused the connection"),
        short._replace(host="genapp.example.com"),
    )
    _assert(
        "genapp.example.com" not in long, "the reason carries the host it addressed"
    )
    return (
        f"{len(reasons)} driver reasons kept their wording, "
        f"{len(short.redacted_values())} setting values replaced once each"
    )


def _case_redshift_probe_failures(scratch: _Scratch) -> str:
    """Every step of the probe that can fail is reported without a setting value."""
    with _controlled_environment(scratch, **_SELF_TEST_REDSHIFT):
        settings = resolve_redshift_settings()
    quoted = (
        f"could not connect to {settings.host} port {settings.port} as "
        f"{settings.user} on {settings.database}.{settings.schema} with password "
        f"{settings.password}"
    )
    checks: tuple[tuple[str, dict[str, BaseException], dict[str, Any], str], ...] = (
        (
            "a refused connection",
            {"connect": _StandInRedshiftError(quoted)},
            {},
            "cannot reach the Redshift target",
        ),
        (
            "an endpoint that does not answer",
            {"connect": OSError(quoted)},
            {},
            "cannot reach the Redshift target",
        ),
        (
            "a refused cursor",
            {"cursor": _StandInRedshiftError("no cursor is available")},
            {},
            f"cannot run {REDSHIFT_PROBE_STATEMENT}",
        ),
        (
            "a refused connectivity statement",
            {"select": _StandInRedshiftError("the statement was refused")},
            {},
            f"cannot run {REDSHIFT_PROBE_STATEMENT}",
        ),
        (
            "a connectivity answer of another shape",
            {},
            {"select": ()},
            "rather than exactly one row",
        ),
        (
            "a connectivity answer of another value",
            {},
            {"select": 2},
            f"{REDSHIFT_PROBE_STATEMENT} answered 2",
        ),
        (
            "a refused write probe relation",
            {"create": _StandInRedshiftError("the relation was refused")},
            {},
            "cannot create the write probe relation",
        ),
        (
            "a refused write",
            {"insert": _StandInRedshiftError("the write was refused")},
            {},
            "cannot write the write probe row",
        ),
        (
            "a refused read back",
            {"count": _StandInRedshiftError("the read was refused")},
            {},
            "cannot read the write probe row back",
        ),
        (
            "a row that was not counted back",
            {},
            {"count": 0},
            "rows after one write",
        ),
        (
            "a withdrawal that did not succeed",
            {
                "rollback": _StandInRedshiftError("no transaction is active"),
                "drop": _StandInRedshiftError("the relation cannot be dropped"),
            },
            {},
            "cannot withdraw the write probe relation",
        ),
    )
    for what, refusals, answers, fragment in checks:
        driver = _StandInRedshiftDriver(refusals=refusals, answers=answers)
        with _captured_stderr() as captured:
            error = _assert_raises(
                what,
                AccessError,
                fragment,
                lambda driver=driver: probe_redshift_access(settings, driver),
            )
        _assert_equal(
            error.exit_status, EXIT_REDSHIFT_UNAVAILABLE, f"the status of {what}"
        )
        _assert_equal(
            _one_line(str(error)), str(error), f"the diagnostic of {what} as one line"
        )
        reported = f"{error}\n{captured.getvalue()}"
        for variable, value in _SELF_TEST_REDSHIFT.items():
            _assert(
                value not in reported,
                f"the report of {what} carries the {variable} value",
            )
        if "connect" in refusals:
            _assert_in(
                REDACTED_SETTING, str(error), f"the reason reported for {what}"
            )
        for connection in driver.connections:
            _assert(connection.closed, f"the connection was left open after {what}")

    warned: list[str] = []
    for what, refusals, fragment, steps in (
        (
            "a rollback that did not succeed",
            {"rollback": _StandInRedshiftError("no transaction is active")},
            "could not be rolled back",
            ("select", "create", "insert", "count", "drop"),
        ),
        (
            "a cursor that could not be closed",
            {"cursor-close": _StandInRedshiftError("the cursor is gone")},
            "cursor could not be closed",
            ("select", "create", "insert", "count"),
        ),
        (
            "a connection that could not be closed",
            {"close": _StandInRedshiftError("the connection is gone")},
            "connection could not be closed",
            ("select", "create", "insert", "count"),
        ),
    ):
        driver = _StandInRedshiftDriver(refusals=refusals)
        with _captured_stderr() as captured:
            verdict = probe_redshift_access(settings, driver)
        _assert_in(REDSHIFT_PROBE_VERDICT, verdict, f"the verdict after {what}")
        _assert_in(fragment, captured.getvalue(), f"the warning after {what}")
        _assert_equal(
            driver.connections[0].steps(), steps, f"the steps run after {what}"
        )
        for variable, value in _SELF_TEST_REDSHIFT.items():
            _assert(
                value not in captured.getvalue(),
                f"the warning after {what} carries the {variable} value",
            )
        warned.append(what)
    return (
        f"{len(checks)} refused steps reported as access failures and "
        f"{len(warned)} warned about, no setting value in any of them"
    )


def _case_redshift_probe_branch(scratch: _Scratch) -> str:
    """The Redshift probe addresses the real branch alone and stands on its own."""
    record = scratch.write("record-redshift-probe.json", _motor_record_text())
    local = _run_cli(scratch, ["--probe-redshift"], **_SELF_TEST_REDSHIFT)
    _assert_equal(
        local.status, EXIT_CONFIGURATION_REJECTED, "the status in the local branch"
    )
    _assert_in(RUN_MODE_VARIABLE, local.stderr, "the local-branch diagnostic")
    _assert_one_diagnostic(local.stderr)
    for what, argv, overrides, fragment in (
        (
            "an endpoint on the command line",
            ["--probe-redshift", "--run-mode", RUN_MODE_REAL,
             "--endpoint-url", "http://127.0.0.1:5000"],
            _SELF_TEST_REDSHIFT,
            "--endpoint-url",
        ),
        (
            "an endpoint in the environment",
            ["--probe-redshift", "--run-mode", RUN_MODE_REAL],
            {**_SELF_TEST_REDSHIFT, ENDPOINT_URL_VARIABLE: "http://127.0.0.1:5000"},
            ENDPOINT_URL_VARIABLE,
        ),
        (
            "no Redshift setting at all",
            ["--probe-redshift", "--run-mode", RUN_MODE_REAL],
            {},
            REDSHIFT_HOST_VARIABLE,
        ),
        (
            "a loopback Redshift host",
            ["--probe-redshift", "--run-mode", RUN_MODE_REAL],
            {**_SELF_TEST_REDSHIFT, REDSHIFT_HOST_VARIABLE: "127.0.0.1"},
            "loopback address",
        ),
        (
            "--record alongside the probe",
            ["--probe-redshift", "--run-mode", RUN_MODE_REAL, "--record", str(record)],
            _SELF_TEST_REDSHIFT,
            "--probe-redshift accepts no --record",
        ),
        (
            "--probe alongside the probe",
            ["--probe-redshift", "--run-mode", RUN_MODE_REAL, "--probe"],
            _SELF_TEST_REDSHIFT,
            "--probe-redshift accepts no --probe",
        ),
        (
            "--render-redshift-load alongside the probe",
            ["--probe-redshift", "--run-mode", RUN_MODE_REAL,
             "--render-redshift-load", RENDER_DOCUMENT_SQL],
            _SELF_TEST_REDSHIFT,
            "--probe-redshift accepts no --render-redshift-load",
        ),
        (
            "--self-test alongside the probe",
            ["--self-test", "--probe-redshift"],
            _SELF_TEST_REDSHIFT,
            "--self-test accepts no --probe-redshift",
        ),
    ):
        run = _run_cli(scratch, argv, **overrides)
        _assert_equal(
            run.status, EXIT_CONFIGURATION_REJECTED, f"the status with {what}"
        )
        _assert_equal(run.stdout, "", f"stdout with {what}")
        _assert_in(fragment, run.stderr, f"the diagnostic with {what}")
        _assert_one_diagnostic(run.stderr)
        _assert(
            "addressing the Redshift target" not in run.stderr,
            f"the run with {what} addressed the target before refusing the settings",
        )
        _assert(
            BUCKET_VARIABLE not in run.stderr,
            f"the run with {what} resolved a bucket setting before its own",
        )
        for variable, value in _SELF_TEST_REDSHIFT.items():
            _assert(
                value not in run.stderr,
                f"the diagnostic with {what} carries the {variable} value",
            )
    return "the probe refused 9 runs that did not address the real Redshift branch"


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
            (("jsonschema", "0.0.1"),),
            "pins jsonschema 0.0.1; run this tool through",
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

    The line is the one the reporting installed above the imports writes, which is the
    line a run interrupted anywhere else writes as well: the command-line case reaches
    it through a resolution step that is interrupted, and the probe cases through a
    driver step that is.
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
    record = scratch.write("record-interrupted.json", _motor_record_text())

    def _interrupt(_supplied: str | None) -> str:
        """Interrupt the run at the first setting it resolves."""
        raise KeyboardInterrupt

    original = globals()["resolve_bucket"]
    globals()["resolve_bucket"] = _interrupt
    try:
        run = _run_cli(scratch, ["--record", str(record)])
    finally:
        globals()["resolve_bucket"] = original
    _assert_equal(run.status, EXIT_INTERRUPTED, "the status of an interrupted run")
    _assert_equal(run.stdout, "", "stdout of an interrupted run")
    _assert_equal(
        [line for line in run.stderr.splitlines() if line],
        [INTERRUPTED_MESSAGE],
        "the stderr of an interrupted run",
    )
    with _controlled_environment(scratch, **_SELF_TEST_REDSHIFT):
        settings = resolve_redshift_settings()
    for step in ("connect", "select", "insert"):
        driver = _StandInRedshiftDriver(refusals={step: KeyboardInterrupt()})
        with _captured_stderr():
            _assert_raises(
                f"an interrupt at the {step} step of the probe",
                KeyboardInterrupt,
                "",
                lambda driver=driver: probe_redshift_access(settings, driver),
            )
        for connection in driver.connections:
            _assert(
                connection.closed,
                f"the connection was left open by an interrupt at {step}",
            )
        if step == "insert":
            _assert_equal(
                driver.connections[0].rolled_back,
                1,
                "the rollbacks after an interrupted write",
            )
    return f"{INTERRUPTED_MESSAGE!r} and status {EXIT_INTERRUPTED}"


def _case_exit_codes(scratch: _Scratch) -> str:
    """Every documented exit status is reachable, and none is reported for a success."""
    mock_aws, _ = _test_collaborators()
    record = scratch.write("record-status.json", _motor_record_text())
    rejected = scratch.write("record-rejected.json", _motor_record_text(broker_id=_ABSENT))
    observed: dict[int, str] = {}

    success = _run_cli(
        scratch,
        [
            "--render-redshift-load",
            RENDER_DOCUMENT_SQL,
            "--record",
            str(record),
            "--bucket",
            _SELF_TEST_BUCKET,
            "--region",
            _SELF_TEST_REGION,
            "--iam-role",
            _SELF_TEST_IAM_ROLE,
        ],
    )
    _assert_equal(success.status, EXIT_OK, "the status of a successful render")
    observed[EXIT_OK] = "render"

    refused = _run_cli(
        scratch,
        [
            "--render-redshift-load",
            RENDER_DOCUMENT_SQL,
            "--record",
            str(rejected),
            "--bucket",
            _SELF_TEST_BUCKET,
            "--region",
            _SELF_TEST_REGION,
            "--iam-role",
            _SELF_TEST_IAM_ROLE,
        ],
    )
    _assert_equal(
        refused.status, EXIT_RECORD_REJECTED, "the status of a rejected record"
    )
    _assert_one_diagnostic(refused.stderr)
    observed[EXIT_RECORD_REJECTED] = "record"

    no_bucket = _run_cli(scratch, ["--record", str(record)])
    _assert_equal(
        no_bucket.status, EXIT_CONFIGURATION_REJECTED, "the status without a bucket"
    )
    _assert_in(BUCKET_VARIABLE, no_bucket.stderr, "the bucket diagnostic")
    observed[EXIT_CONFIGURATION_REJECTED] = "setting"

    with mock_aws():
        # The mocked service stands in for AWS S3 itself, so the run selects the mode
        # that addresses AWS S3 and sets no endpoint.
        unreachable = _run_cli(
            scratch,
            [
                "--record",
                str(record),
                "--bucket",
                "genapp-rqi-absent-bucket",
                "--run-mode",
                RUN_MODE_REAL,
                "--extract-date",
                _SELF_TEST_EXTRACT_DATE.isoformat(),
            ],
            AWS_DEFAULT_REGION=_SELF_TEST_REGION,
            **_SELF_TEST_CREDENTIALS,
        )
    _assert_equal(
        unreachable.status, EXIT_S3_UNAVAILABLE, "the status of an absent bucket"
    )
    _assert_in("does not exist", unreachable.stderr, "the absent-bucket diagnostic")
    observed[EXIT_S3_UNAVAILABLE] = "bucket"

    _assert_equal(
        _self_test_status(
            [_CaseResult(name="probe", passed=False, detail="observed a failure")]
        ),
        EXIT_SELF_TEST_FAILED,
        "the status a failing case produces",
    )
    _assert_equal(
        _self_test_status([_CaseResult(name="probe", passed=True, detail="held")]),
        EXIT_OK,
        "the status a passing matrix produces",
    )
    observed[EXIT_SELF_TEST_FAILED] = "self-test"

    rejected_combination = _run_cli(
        scratch,
        [
            "--self-test",
            "--record",
            str(record),
        ],
    )
    _assert_equal(
        rejected_combination.status,
        EXIT_CONFIGURATION_REJECTED,
        "the status of --self-test with --record",
    )
    exclusive = _run_cli(
        scratch,
        [
            "--probe",
            "--render-redshift-load",
            RENDER_DOCUMENT_SQL,
            "--bucket",
            _SELF_TEST_BUCKET,
        ],
    )
    _assert_equal(
        exclusive.status,
        EXIT_CONFIGURATION_REJECTED,
        "the status of --probe with --render-redshift-load",
    )
    return f"statuses reachable: {', '.join(str(status) for status in sorted(observed))}"


def _case_scratch_removed(scratch: _Scratch) -> str:
    """The private directory this run worked inside is removed with everything in it."""
    path = scratch.path
    _assert(path.is_dir(), f"the run directory {path} is not a directory")
    _assert(
        not str(path).startswith(str(_THIS_DIR.parent)),
        f"the run directory {path} sits inside the repository",
    )
    _assert(scratch.removed(), f"the run directory {path} was not removed")
    return f"removed {path}"


# ---------------------------------------------------------------------------
# Self-test: runner
# ---------------------------------------------------------------------------


def _run_case(
    results: list[_CaseResult],
    stream: Any,
    quiet: bool,
    name: str,
    body: Callable[[], str],
) -> None:
    """Run one case, record its outcome and print its line.

    A case that raises records a failure and the run continues with the next case.
    ``_SelfTestFailure`` carries the observation the case made; a ``LandingError`` or
    any of the listed defect classes is reported by type and message.
    """
    try:
        detail = body()
    except _SelfTestFailure as failure:
        result = _CaseResult(name=name, passed=False, detail=str(failure))
    except LandingError as error:
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
    print(f"self-test {verdict} {result.name} -- {_one_line(result.detail)}",
          file=stream)


def _self_test_status(results: Sequence[_CaseResult]) -> int:
    """Return ``EXIT_OK`` when every case passed and ``EXIT_SELF_TEST_FAILED`` else."""
    return (
        EXIT_OK
        if all(result.passed for result in results)
        else EXIT_SELF_TEST_FAILED
    )


def run_self_test(*, quiet: bool = False, stream: Any = None) -> int:
    """Run every self-test case and return ``EXIT_OK`` or ``EXIT_SELF_TEST_FAILED``.

    Each case prints one line to ``stream``, which defaults to stdout, followed by one
    summary line; ``quiet`` limits the case lines to the failing ones. Every document a
    case reads or writes sits inside one private temporary directory the run creates and
    the last case removes, so no case reads or writes a path inside the repository other
    than the landing schema and the Redshift load template it validates against. No case
    reaches a network endpoint: the S3 collaborators are the pinned boto3 client driven
    through moto in this process and through botocore's own stubber, the Redshift probe
    is driven through a stand-in for the pinned driver, so no case opens a socket to a
    warehouse or carries a credential to one, and every environment variable this tool
    consults is set by the case that needs it and restored afterwards.
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
        _run_case(
            results, out, quiet, "record_accepted",
            lambda: _case_record_accepted(scratch),
        )
        _run_case(
            results, out, quiet, "record_refusals",
            lambda: _case_record_refusals(scratch),
        )
        _run_case(
            results, out, quiet, "schema_violations_reported_once",
            lambda: _case_schema_violations_reported_once(scratch),
        )
        _run_case(
            results, out, quiet, "duplicate_members_refused",
            lambda: _case_duplicate_members_refused(scratch),
        )
        _run_case(
            results, out, quiet, "nesting_bounded",
            lambda: _case_nesting_bounded(scratch),
        )
        _run_case(
            results, out, quiet, "control_characters_refused",
            lambda: _case_control_characters_refused(scratch),
        )
        _run_case(
            results, out, quiet, "product_premium_allocation",
            lambda: _case_product_premium_allocation(scratch),
        )
        _run_case(results, out, quiet, "endpoint_accepted", _case_endpoint_accepted)
        _run_case(results, out, quiet, "endpoint_refused", _case_endpoint_refused)
        _run_case(
            results, out, quiet, "endpoint_resolving_name_refused",
            _case_endpoint_resolving_name_refused,
        )
        _run_case(
            results, out, quiet, "configured_endpoint_ignored",
            lambda: _case_configured_endpoint_ignored(scratch),
        )
        _run_case(
            results, out, quiet, "probe_writes_and_deletes",
            lambda: _case_probe_writes_and_deletes(scratch),
        )
        _run_case(
            results, out, quiet, "probe_cleanup_failures",
            lambda: _case_probe_cleanup_failures(scratch),
        )
        _run_case(
            results, out, quiet, "bucket_failures_reported",
            _case_bucket_failures_reported,
        )
        _run_case(results, out, quiet, "failure_mapping", _case_failure_mapping)
        _run_case(
            results, out, quiet, "credentials_and_region_required",
            lambda: _case_credentials_and_region_required(scratch),
        )
        _run_case(
            results, out, quiet, "landing_uploads_bytes",
            lambda: _case_landing_uploads_bytes(scratch),
        )
        _run_case(
            results, out, quiet, "landing_records_object_identity",
            lambda: _case_landing_records_object_identity(scratch),
        )
        _run_case(
            results, out, quiet, "landing_replacement_noted",
            lambda: _case_landing_replacement_noted(scratch),
        )
        _run_case(
            results, out, quiet, "landing_parts_coexist",
            lambda: _case_landing_parts_coexist(scratch),
        )
        _run_case(
            results, out, quiet, "landing_replacement_probe_non_fatal",
            lambda: _case_landing_replacement_probe_non_fatal(scratch),
        )
        _run_case(
            results, out, quiet, "upload_failure_reported",
            lambda: _case_upload_failure_reported(scratch),
        )
        _run_case(results, out, quiet, "keys_built", _case_keys_built)
        _run_case(
            results, out, quiet, "part_option_resolved", _case_part_option_resolved
        )
        _run_case(results, out, quiet, "render_identity", _case_render_identity)
        _run_case(
            results, out, quiet, "render_fixture_bytes",
            lambda: _case_render_fixture_bytes(scratch),
        )
        _run_case(
            results, out, quiet, "render_real_template",
            lambda: _case_render_real_template(scratch),
        )
        _run_case(
            results, out, quiet, "render_manifest",
            lambda: _case_render_manifest(scratch),
        )
        _run_case(
            results, out, quiet, "render_non_default_part",
            lambda: _case_render_non_default_part(scratch),
        )
        _run_case(
            results, out, quiet, "render_rejects_hostile_values",
            _case_render_rejects_hostile_values,
        )
        _run_case(
            results, out, quiet, "render_rejects_mismatch",
            lambda: _case_render_rejects_mismatch(scratch),
        )
        _run_case(
            results, out, quiet, "render_rejects_template_faults",
            lambda: _case_render_rejects_template_faults(scratch),
        )
        _run_case(results, out, quiet, "sql_split_matrix", _case_sql_split_matrix)
        _run_case(results, out, quiet, "render_cli", lambda: _case_render_cli(scratch))
        _run_case(
            results, out, quiet, "redshift_settings_resolved",
            lambda: _case_redshift_settings_resolved(scratch),
        )
        _run_case(
            results, out, quiet, "redshift_settings_refused",
            lambda: _case_redshift_settings_refused(scratch),
        )
        _run_case(
            results, out, quiet, "redshift_probe_succeeds",
            lambda: _case_redshift_probe_succeeds(scratch),
        )
        _run_case(
            results, out, quiet, "redshift_probe_failures",
            lambda: _case_redshift_probe_failures(scratch),
        )
        _run_case(
            results, out, quiet, "redshift_reason_redaction",
            lambda: _case_redshift_reason_redaction(scratch),
        )
        _run_case(
            results, out, quiet, "redshift_probe_branch",
            lambda: _case_redshift_probe_branch(scratch),
        )
        _run_case(
            results, out, quiet, "environment_guard",
            lambda: _case_environment_guard(scratch),
        )
        _run_case(
            results, out, quiet, "interrupt_reported",
            lambda: _case_interrupt_reported(scratch),
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
    key_prefix_template = KEY_SEPARATOR.join(
        (
            LANDING_KEY_ROOT,
            f"source_system_key=<{SOURCE_SYSTEM_KEY_VARIABLE}>",
            f"entity={LANDING_ENTITY}",
            f"extract_date=<{EXTRACT_DATE_FORM}>",
        )
    )
    part_form = "N" * PART_NUMBER_DIGITS
    key_template = (
        f"{key_prefix_template}{KEY_SEPARATOR}"
        f"{OBJECT_NAME_TEMPLATE.format(part=part_form)}"
    )
    manifest_key_template = (
        f"{key_prefix_template}{KEY_SEPARATOR}"
        f"{MANIFEST_OBJECT_NAME_TEMPLATE.format(part=part_form)}"
    )
    parser = _CommandLineParser(
        prog=_PROGRAM,
        allow_abbrev=False,
        description=(
            "Validate one GenApp Policy-Issue landing record, write it as a single "
            "S3 object under the landing prefix and write the COPY manifest naming "
            "that object beside it.\n"
            "The bytes of the record file are the bytes uploaded: no amount is "
            "derived, no key is added, removed, renamed or reordered, and the JSON is "
            "never re-serialised.\n"
            "A repeated JSON member name is refused, every date is held to the "
            "calendar, and every timestamp is parsed as one real instant.\n"
            "Exit status: 0 success, 2 record rejected, 3 runtime environment, "
            "command line or setting rejected, 4 S3 endpoint, bucket or object "
            "operation unsuccessful or "
            "Redshift target unreachable or refusing, 5 self-test case failed, 130 "
            "interrupted, which is that status and one line wherever the interrupt "
            "arrives, the imports of this tool included."
        ),
        epilog=(
            f"Object key: {key_template}\n"
            f"Manifest key: {manifest_key_template}\n"
            f"Object URI: {SERVICE_NAME}://<bucket>/<key>, both written with content "
            f"type {OBJECT_CONTENT_TYPE}. Partitioning applies to this key prefix "
            "alone.\n"
            "A landing writes the record first and the manifest second, in either run "
            "mode. The manifest carries one entry naming the record's own URI, "
            "mandatory true and the byte count written, and is byte-identical to what "
            f"--render-redshift-load {RENDER_DOCUMENT_MANIFEST} prints for the same "
            "record, so the real-branch order is land, bootstrap the raw relation, "
            "then run the COPY of load_redshift.sql.\n"
            "One key carries one object per source system, entity, extract date and "
            f"part: --part names the part, {DEFAULT_PART_TEXT} applies when it is "
            "omitted, and every part of one extract date coexists under one prefix, so "
            "the landing zone can be replayed to rebuild every raw row of that date. A "
            "second landing of the same part addresses that same key and replaces the "
            "object it carries, naming it in one warning line; a head request that "
            "does not answer writes no such line and the landing still succeeds.\n"
            "In landing mode stdout carries exactly one line, the URI of the object "
            "written; in either probe mode it carries exactly one line, that probe's "
            "verdict. "
            "Every other message reaches stderr, no credential, token or endpoint "
            "value is ever printed, and a rejected record is reported by field, "
            "validation keyword and value shape rather than by value.\n"
            f"Run mode {RUN_MODE_LOCAL} requires a loopback endpoint from "
            f"--endpoint-url or {ENDPOINT_URL_VARIABLE} and addresses it; run mode "
            f"{RUN_MODE_REAL} forbids one and addresses AWS S3. A custom endpoint is "
            "accepted only as an http or https URL naming a loopback host, with no "
            "userinfo, query, fragment or path, and only with credentials resolved "
            "from the environment.\n"
            "Access is established from resolved credentials, a resolved region and a "
            "bucket that answers a head request, and an environment variable whose "
            "name merely begins with AWS is never read as a credential.\n"
            f"--probe-redshift is the gate's second half and addresses the real target "
            f"alone: it requires run mode {RUN_MODE_REAL}, no endpoint override and a "
            "Redshift host that is not a loopback address, each refused by the setting "
            "it came from before a socket is opened. It connects with the REDSHIFT_* "
            f"settings {REDSHIFT_PROFILE_DOCUMENT} documents, runs "
            f"{REDSHIFT_PROBE_STATEMENT}, and creates, writes, counts and rolls back "
            "one temporary relation. No host, port, user, database, schema or password "
            "value reaches stdout, stderr or a diagnostic, and a reason the driver "
            "supplied is carried with every one of those values removed.\n"
            "This tool creates no bucket and provisions nothing: no cluster, "
            "workgroup, database, schema, durable relation, network or IAM object. It "
            "writes those two objects and nothing to the local filesystem.\n"
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
            f"byte, of at most {MAX_RECORD_BYTES} bytes; required unless --probe or "
            "--probe-redshift is given, which read no record"
        ),
    )
    parser.add_argument(
        "--run-mode",
        default=None,
        choices=RUN_MODES,
        help=(
            "branch of the bridge to address; defaults to the "
            f"{RUN_MODE_VARIABLE} environment variable, then to {DEFAULT_RUN_MODE}. "
            f"{RUN_MODE_LOCAL} requires a loopback endpoint and addresses it; "
            f"{RUN_MODE_REAL} forbids one and addresses AWS S3. It is the same setting "
            "that selects the dbt output and the raw loader branch"
        ),
    )
    parser.add_argument(
        "--bucket",
        default=None,
        metavar="NAME",
        help=(
            "destination bucket, which must already exist; defaults to the "
            f"{BUCKET_VARIABLE} environment variable. There is no built-in bucket "
            "name. A general-purpose bucket name: "
            f"{MIN_BUCKET_CHARACTERS} to {MAX_BUCKET_CHARACTERS} characters drawn from "
            "lowercase letters, digits, dot and hyphen, beginning and ending with a "
            "letter or a digit"
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
            "entity element of the landing prefix, which is the fixed literal "
            f"{LANDING_ENTITY}; omitted, that literal applies, and any other value is "
            "refused rather than landing the record outside the canonical prefix"
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
            f"and the object name is {OBJECT_NAME}. Each part of one source system, "
            "entity and extract date is its own object with its own COPY manifest, so "
            "two records of one extract date coexist under one prefix instead of the "
            "second replacing the first"
        ),
    )
    parser.add_argument(
        "--endpoint-url",
        default=None,
        metavar="URL",
        help=(
            "loopback S3 endpoint serving the local substitute, selecting a local "
            f"S3-compatible endpoint; defaults to the {ENDPOINT_URL_VARIABLE} "
            f"environment variable. Required in run mode {RUN_MODE_LOCAL} and refused "
            f"in run mode {RUN_MODE_REAL}, where AWS S3 is addressed by setting no "
            "endpoint at all. Accepted values are "
            f"{' or '.join(ACCEPTED_ENDPOINT_SCHEMES)} on 127.0.0.0/8, ::1 or "
            f"{LOOPBACK_HOST_NAME} with an explicit port of "
            f"{ENDPOINT_PORT_FLOOR} or above, carrying no user information, query, "
            "fragment or path"
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
            "probe object outside the landing prefix, then exit; no landing object and "
            "no manifest are written and no record is read"
        ),
    )
    parser.add_argument(
        "--probe-redshift",
        action="store_true",
        help=(
            "confirm access to the real Redshift target and exit, which is the second "
            "half of the precondition gate: connect with the REDSHIFT_* settings "
            f"{REDSHIFT_PROFILE_DOCUMENT} documents, run "
            f"{REDSHIFT_PROBE_STATEMENT}, then create, write, count and roll back one "
            "temporary relation. Nothing is provisioned: no cluster, workgroup, "
            "database, schema, durable relation, network or IAM object, and no bucket. "
            f"Every setting is read from the environment - {REDSHIFT_HOST_VARIABLE}, "
            f"{REDSHIFT_USER_VARIABLE}, {REDSHIFT_PASSWORD_VARIABLE}, "
            f"{REDSHIFT_DATABASE_VARIABLE} and {REDSHIFT_SCHEMA_VARIABLE} are "
            f"required, {REDSHIFT_PORT_VARIABLE} defaults to {DEFAULT_REDSHIFT_PORT} "
            f"and {REDSHIFT_CONNECT_TIMEOUT_VARIABLE} to "
            f"{DEFAULT_REDSHIFT_CONNECT_TIMEOUT} seconds - and no value of any of them "
            "is printed. It requires run mode "
            f"{RUN_MODE_REAL} and no endpoint override, reads no record, writes no "
            "object, and is exclusive with --record, --probe, "
            "--render-redshift-load and --self-test"
        ),
    )
    parser.add_argument(
        SHOW_IDENTIFIERS_OPTION,
        action="store_true",
        help=(
            "carry record values in diagnostics, including the library's own schema "
            "messages; withheld by default, and also enabled by the "
            f"{SHOW_IDENTIFIERS_VARIABLE} environment variable carrying one of "
            f"{', '.join(SHOW_IDENTIFIERS_ENABLING)}"
        ),
    )
    parser.add_argument(
        "--render-redshift-load",
        default=None,
        choices=RENDER_DOCUMENTS,
        metavar="DOCUMENT",
        help=(
            f"substitute {DEFAULT_REDSHIFT_TEMPLATE.name} for the record named by "
            f"--record and write one document to stdout: {RENDER_DOCUMENT_SQL} for the "
            f"load statements, {RENDER_DOCUMENT_MANIFEST} for the COPY manifest they "
            "read. Every placeholder value is validated against the allowlist that "
            "template records, escaped for a SQL string literal, and refused when it "
            "carries a control character, a quote, a semicolon, a backslash or a SQL "
            "comment sequence; an unsupported placeholder, a placeholder without a "
            "value, a rendered key that is not the record's own and a rendered delete "
            "guard that is not keyed on the record's own policy number are all "
            "refused. The manifest carries one mandatory entry naming the validated "
            "object, with that object's byte count under the entry's nested meta "
            "member, so the COPY fails on a removed object. No S3 request is made, no "
            "object is written and no credential is used"
        ),
    )
    parser.add_argument(
        "--template",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "Redshift load template --render-redshift-load substitutes (default: "
            f"{DEFAULT_REDSHIFT_TEMPLATE})"
        ),
    )
    parser.add_argument(
        "--iam-role",
        default=None,
        metavar="ARN",
        help=(
            "ARN of the IAM role the rendered COPY reads the bucket with; defaults to "
            f"the {IAM_ROLE_VARIABLE} environment variable. Required by "
            "--render-redshift-load and used by no other mode"
        ),
    )
    parser.add_argument(
        "--object-etag",
        default=None,
        metavar="ETAG",
        help=(
            "ETag the landed object carries, with or without its surrounding quotes; "
            "defaults to the ETag a single-part upload of the record's own bytes "
            "produces. Used by --render-redshift-load only"
        ),
    )
    parser.add_argument(
        "--object-version-id",
        default=None,
        metavar="ID",
        help=(
            "version id the landed object carries on a versioned bucket; defaults to "
            f"{NOT_VERSIONED}, the value recorded for a bucket that keeps no versions. "
            "Used by --render-redshift-load only"
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run the built-in case matrix and exit, reading no record of the caller's "
            "and making no request to any endpoint; every document a case reads or "
            "writes sits inside one private temporary directory the run creates and "
            "removes, and the S3 collaborators are the pinned boto3 client driven "
            "through moto and through botocore's own stubber"
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="with --self-test, print only the failing case lines and the summary",
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
            "--probe and --probe-redshift, which read no record, may omit it"
        )
    return supplied


def _run(args: argparse.Namespace) -> str:
    """Run one probe, one render or one landing, returning what stdout carries.

    In Redshift probe mode nothing of the S3 side is resolved at all - no bucket, no
    region, no credential and no client - since that probe addresses the warehouse: the
    endpoint and run-mode settings are resolved only to establish that the run selects
    the real branch, the Redshift settings are resolved and shaped, and one connection
    is then opened, questioned and closed. Otherwise the bucket, region and endpoint
    settings resolve first, so an unresolved setting is
    reported before anything else runs, and the run mode is reconciled with the resolved
    endpoint before any session, client or credential exists. In probe mode the client and
    its credentials are resolved next and one probe object is written and deleted: no
    record is read and neither landing object is written. In landing mode
    ``land_record`` reads, parses and validates the record and builds the landing and
    manifest keys next, and only then are the client and its credentials resolved, the
    bucket confirmed reachable, the record written and the manifest written beside it.
    A record that breaches the landing contract is therefore reported
    before any client exists, and an unresolved credential is reported after the record
    has been read and validated. In render mode no session, client, credential or request
    is involved at all, and the rendered document is returned as written.
    """
    if args.probe_redshift:
        endpoint_url, endpoint_origin = resolve_endpoint_url(args.endpoint_url)
        run_mode, run_mode_origin = resolve_run_mode(args.run_mode)
        confirm_redshift_probe_branch(
            run_mode, run_mode_origin, endpoint_url, endpoint_origin
        )
        _note(
            f"run mode {_shown(run_mode)} from {run_mode_origin}, probing the real "
            "Redshift target"
        )
        return probe_redshift_access(resolve_redshift_settings())
    bucket = resolve_bucket(args.bucket)
    region = resolve_region(args.region)
    if args.render_redshift_load is not None:
        return render_redshift_document(
            args.render_redshift_load,
            _require_record_path(args.record),
            bucket,
            resolve_source_system_key(args.source_system_key),
            resolve_entity(args.entity),
            resolve_extract_date(args.extract_date),
            require_region(region),
            resolve_iam_role(args.iam_role),
            part=resolve_part(args.part),
            object_etag=args.object_etag,
            object_version_id=args.object_version_id,
            template_path=resolve_template_path(args.template),
        )
    endpoint_url, endpoint_origin = resolve_endpoint_url(args.endpoint_url)
    run_mode, run_mode_origin = resolve_run_mode(args.run_mode)
    confirm_run_mode_endpoint(run_mode, run_mode_origin, endpoint_url, endpoint_origin)
    _note(
        f"run mode {_shown(run_mode)} from {run_mode_origin}, addressing "
        + ("the loopback endpoint" if endpoint_url is not None else "AWS S3")
    )
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
        part=resolve_part(args.part),
        region=region,
        endpoint_url=endpoint_url,
    )


def main(argv: list[str] | None = None) -> int:
    """Land one record, probe access, render the Redshift load, or run the self-test.

    ``argv`` defaults to the process arguments. Exactly one line reaches stdout on a
    successful landing or probe: the URI of the object written, or the probe verdict. A
    successful render writes the document itself and nothing else, and the self-test
    writes one line per case and one summary line. Every diagnostic reaches stderr as
    one control-free line, names the setting to supply when one is missing, and carries
    no credential, token or endpoint value and no value the landing record carries. A
    rejected command line is reported through that same single line, without a usage
    block, while ``--help`` prints the full help and exits with status 0.
    """
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        set_show_identifiers(resolve_show_identifiers(args.show_identifiers))
        if args.self_test:
            for option, present in (
                ("--record", args.record is not None),
                ("--probe", args.probe),
                ("--probe-redshift", args.probe_redshift),
                ("--render-redshift-load", args.render_redshift_load is not None),
            ):
                if present:
                    parser.error(f"--self-test accepts no {option}")
            return run_self_test(quiet=args.quiet)
        if args.probe and args.render_redshift_load is not None:
            parser.error("--probe and --render-redshift-load are exclusive")
        if args.probe_redshift:
            for option, present in (
                ("--record", args.record is not None),
                ("--probe", args.probe),
                ("--render-redshift-load", args.render_redshift_load is not None),
            ):
                if present:
                    parser.error(f"--probe-redshift accepts no {option}")
        result = _run(args)
    except LandingError as error:
        print(f"{_PROGRAM}: {_one_line(str(error))}", file=sys.stderr)
        return error.exit_status
    except KeyboardInterrupt:
        _report_interrupt()
        return EXIT_INTERRUPTED

    if args.render_redshift_load is not None:
        sys.stdout.write(result)
    else:
        print(result)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
