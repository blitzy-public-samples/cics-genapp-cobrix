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

WHAT IT REQUIRES OF THE WAREHOUSE STATE BEFORE IT COMPARES ANYTHING
    That the transform which produced that state is established as successful.
    Before the first row is read, the dbt run artifact named by
    --dbt-run-results is read and every node status it records is examined.
    "success" and "pass" are accepted; "warn" passes and is named in both
    reports; "error", "fail", "skipped", "runtime error" and any status this tool
    does not know are refused, and so are an absent, unreadable, oversized,
    non-UTF-8, non-JSON or non-object artifact, an artifact carrying no results
    member, a results member that is not a list, an empty results list, a result
    that is not an object and a result without a status. A refusal is recorded in
    both reports, no case is read, no row is compared, the verdict is FAIL and
    the run returns 3, so a warehouse state left behind by a dbt invocation that
    did not succeed cannot be certified by this gate - whether the gate was
    reached through the Makefile order or invoked on its own.

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
    --refresh-snapshot
                    rewrite the capture snapshot of every compared case from this
                    run instead of comparing it. The supported way to re-baseline
                    a snapshot; without it a snapshot on disk is compared and a
                    difference fails the run.
    --dbt-run-results
                    dbt run artifact holding the outcome of the transform that
                    produced the warehouse state. Default, resolved against this
                    file's own repository root like every other default,
                    modernization/dbt/genapp_rqi/target/run_results.json, the
                    target directory of the one dbt project of this bridge, so
                    the caller of the diff stage names no path.
    --self-test     run the built-in case matrix and exit; it opens no warehouse,
                    reaches no endpoint, reads no harness output and writes
                    nothing outside one private temporary directory it creates
                    and removes. It is refused alongside any other option but
                    --quiet.
    --quiet         print the verdict line alone; with --self-test, print the
                    failing case lines and the summary line alone.

    The Redshift target reads REDSHIFT_HOST, REDSHIFT_PORT, REDSHIFT_DATABASE,
    REDSHIFT_USER and REDSHIFT_PASSWORD, the variable contract of
    modernization/dbt/genapp_rqi/profiles.example.yml. An environment variable
    holding the empty string or whitespace alone counts as unset, so the
    documented default applies.

WHAT IT WRITES
    A Markdown report and a JSON report, each replaced in full on every run, both
    carrying the transform freshness precondition - its verdict, the dbt
    invocation the artifact records and every node status that refused it - and
    one capture snapshot per case at
    <expected-dir>/<case>/captures.normalized.json. A snapshot that is absent is
    written; a snapshot that is present is compared, and a difference is
    reported key by key and fails the run; --refresh-snapshot rewrites it
    instead, reports it as refreshed and names the cases it rewrote on the
    summary. Nothing else is written: no database is modified, no AWS resource is
    created and no path under base/ is opened for writing.

    Every one of those files carries mode 0600 and every directory this tool
    creates above one carries 0700, set on the entry itself, so the compared
    identifiers they hold are readable and writable by their owner alone whatever
    the ambient umask requested. A report is rewritten in full on every run and a
    matched snapshot holds the bytes the run would have written, so both are
    brought to that mode even when an earlier run created them under a wider one;
    a directory that already stands keeps its own mode.

WHERE IT MAY WRITE
    Three roots, and nothing else. Every output path - both reports and every
    capture snapshot - is canonicalised, so a symbolic-link chain, a
    symbolic-link parent directory, a ".." component and a "/proc/self/cwd" style
    alias are judged by the path they name rather than the path they spell, and is
    then held to one policy: a path inside base/ or synthetic_class/ is refused by
    that tree's name; a path inside the repository must stand below
    modernization/validation/artifacts or modernization/validation/expected, the
    roots of the two default reports and of the per-case snapshots, and every
    other path inside the repository is refused; a path outside the repository
    must stand below the temporary directory the run resolves, which reads TMPDIR,
    TEMP and TMP before the platform default; and a final component that is a
    symbolic link is refused. Every other path of the filesystem is refused by
    name, /etc/passwd and every other system file among them, and the refusal
    names the path, the canonical form it resolves to and the accepted roots on
    one line. The three destinations a command line names are validated together
    before the field map is read, the warehouse is opened or a report is
    rendered, so a refused --report, --json or --expected-dir ends the run with 4
    and writes nothing at all; the same guard runs again at the moment of each
    write.

    The snapshot carries a symbol where a value is one the seeds of the harness
    run determine: the assigned policy number, in the zero-padded form of its
    COMMAREA window, in the digits-alone form of the SQL capture and at the end
    of the composite VSAM key, and the assigned 26-character timestamp. Both
    seeds - HARNESS_POLICY_NUMBER and HARNESS_LASTCHANGED of
    modernization/harness/run_harness.sh - therefore leave the document
    unchanged, while every other value, and any of those values that is not the
    one the run assigned, is carried as it stands and reported when it moves.

    No credential, password, token, IAM role, endpoint URL or environment
    listing reaches stdout, stderr, the Markdown report or the JSON report. A
    Redshift connection is recorded as its host and database alone. The reports
    do carry policy, customer and broker identifiers, which are the values under
    comparison.

    While the run addresses the local substitute, every claimed result in the
    Markdown report carries the phrase "validated against local substitute, not
    AWS" and the report states that these results leave the formal AWS diff
    requirement OPEN.

WHAT --self-test CHECKS
    That this gate can fail, and on which inputs. The matrix drives the
    comparison functions in this process over built records: a non-amount value
    the warehouse carries differently, an amount delta of zero, one below the
    tolerance, one exactly at it, one just above it and one well above it, a
    capture snapshot built under two identity seeds and two timestamp seeds, the
    drift of a value no seed determines, the refusal of a tampered snapshot and
    the rewrite --refresh-snapshot performs over one, a
    warehouse amount carrying another scale, an absent harness authority and a
    column with no authority at all, the NULL expectation of a product premium
    in both directions, the blank-window path of a nullable column in both
    directions, two harness authorities that disagree, a warehouse NULL where the
    harness carries a value, a harness value and a warehouse value neither
    normalisation reads, and the five normalisations over values that do compare
    equal. It then drives the statuses those records produce: the status and
    verdict of one case and of the run, the precedence over every ordered pair of
    the declared statuses, the Markdown report, the JSON document and the summary
    line of a failing run. Every case asserts an observed value, and one case
    asserts that a failing case returns the self-test status.

    It drives the output confinement of WHERE IT MAY WRITE: an output path inside
    each protected tree, the two default reports and the default snapshot path of
    every supported case accepted, a path in the system configuration directory
    refused as a path, as a write, as --json and as --expected-dir, the system
    password file refused, four in-repository paths outside the output roots
    refused, --report inside base/src refused, a path spelled through a
    symbolic-link parent directory naming a directory outside every accepted root
    refused, and an output path that is itself a symbolic link refused with the
    file it names unchanged. Each refusal is asserted to create nothing and to
    leave the two default report paths at the size and modification time they
    stood at.

    It drives the field map loader over documents it writes in its private
    directory: an alias of an anchor, the merge key, a repeated mapping key and a
    document nested past MAX_DOCUMENT_DEPTH, all refused with the configuration
    status, and an ordinary mapping still composed.

    It drives the transform freshness precondition over dbt run artifacts it
    builds: a run of successful models, a test invocation of passing nodes and a
    warned node, all accepted; a failed model with its skipped consumers, a
    failed data test, a runtime error and an unrecognised status, all refused;
    and an artifact that is absent, a directory, not JSON, not a JSON object,
    without a results member, with a results member that is not a list, with an
    empty results list, with a result that is not an object and with a result
    without a status, all refused. One further case drives the refusal into both
    reports and asserts the status it returns.

    The matrix opens no warehouse, reaches no endpoint, reads no harness output
    and reads no field map of this repository; the loader cases read only the
    documents they write in the private directory. It writes two reports, those
    documents and one snapshot inside one
    private temporary directory it creates and the last case removes, so no path
    of this repository is written and the reports of the last comparison run
    stand untouched.

HOW IT FAILS
    0   every comparison passed. A non-zero delta inside the tolerance is
        reported in the unexpected_in_tolerance section and returns 0.
    1   a comparison failed.
    2   a harness input is missing or incomplete: an absent capture file or
        record, a COMMAREA of a length other than the one the field map
        declares, an unreadable capture line, a repeated capture key, an absent
        capture key a comparison needs, or a capture snapshot that differs from
        the one on disk.
    3   the warehouse content is refused. Either the transform freshness
        precondition refused the state before any comparison was made - the dbt
        run artifact is absent, unreadable, oversized, not UTF-8, not JSON, not a
        JSON object, carries no results member, carries a results member that is
        not a list, carries an empty results list, carries a result that is not
        an object, carries a result without a status, or records a node whose
        status is not "success", "pass" or "warn" - or the warehouse answered and
        its content is refused: a canonical relation set or column set other than
        the declared one, or other than exactly one row for the natural key of a
        case. Both reports are written and state which of the two it was.
    4   a connection, configuration or usage failure: an unknown option, a
        target that cannot be opened, an absent Redshift setting, an adapter
        that is not installed, an output path outside the accepted roots of
        WHERE IT MAY WRITE, a field map carrying an alias, the merge key, a
        repeated key or nesting past MAX_DOCUMENT_DEPTH, or a field map that
        disagrees with the byte grid this tool carries. Nothing is written on
        this path.
    5   one case of --self-test did not hold. It is returned by --self-test
        alone: a comparison run never returns it.

WHERE THIS STEP SITS
    Figure 5 — Validation Harness Control Flow in
    modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import io
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from collections.abc import Callable, Iterable, Mapping, Sequence
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

# Status --self-test returns when one of its cases did not hold. A comparison
# run never returns it, and it stands outside _EXIT_PRECEDENCE, which orders the
# statuses a comparison contributes.
EXIT_SELF_TEST_FAILED = 5

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

# Artifact dbt-core writes at the end of every invocation that reaches its first
# node, holding the status of each node of that invocation. It is the transform
# outcome this tool reads before it publishes any verdict, and the default resolves
# against REPO_ROOT like every other default above, so the target directory of the
# one dbt project of this bridge is read without a caller naming it.
DEFAULT_DBT_RUN_RESULTS = "modernization/dbt/genapp_rqi/target/run_results.json"

# Largest dbt run artifact this tool reads. It carries one entry per executed node,
# so it grows with the node count of the project rather than with the data, and this
# bound is above the whole model and test tree of this project by a wide margin.
MAX_RUN_RESULTS_BYTES = 16_777_216

# Node statuses of a dbt run artifact, by what each one means for the transform
# freshness precondition. dbt records "success" for a model that built and "pass"
# for a data test that held; both are accepted. "warn" is a data test that held
# under a warn-level severity: it passes the precondition and is named in both
# reports. Every status below is refused, and so is a status outside all three
# tuples, because a node that errored, failed, was skipped or recorded something
# this tool does not know leaves the warehouse state unestablished.
DBT_STATUSES_ACCEPTED = ("success", "pass")
DBT_STATUSES_WARNED = ("warn",)
DBT_STATUSES_REFUSED = ("error", "fail", "skipped", "runtime error")

# Verdicts of the transform freshness precondition, carried into both reports.
FRESHNESS_FRESH = "FRESH"
FRESHNESS_REFUSED = "REFUSED"

# Status a run returns when the precondition refuses. A warehouse state whose last
# transform is not established as successful is warehouse content this tool refuses,
# which is what EXIT_WAREHOUSE_REFUSED states; the precondition adds no status of
# its own.
FRESHNESS_REFUSED_STATUS = EXIT_WAREHOUSE_REFUSED

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

# Name of the per-case capture snapshot inside <expected-dir>/<case>, and the
# three states one run leaves it in: written where none stood there, matched
# where the one there holds this run's document, and refreshed where
# --refresh-snapshot replaced it.
SNAPSHOT_NAME = "captures.normalized.json"
SNAPSHOT_STATE_WRITTEN = "written"
SNAPSHOT_STATE_MATCHED = "matched"
SNAPSHOT_STATE_REFRESHED = "refreshed"

# Largest file this tool reads, applied to every input.
MAX_INPUT_BYTES = 1_048_576

# Container nesting one field map may reach while its nodes are composed. A document
# nesting deeper is refused at the level it breaches, so the parse is bounded before the
# interpreter's own recursion limit is reached. It is the bound
# modernization/extraction/build_sample_commarea.py and
# modernization/extraction/extract_commarea.py apply to the same document.
MAX_DOCUMENT_DEPTH = 32

# Trees no output path of this tool may resolve into. They are refused by name before
# the accepted roots below are considered, so a path inside one is reported as the tree
# it names rather than as a path outside the accepted set.
PROTECTED_TREES = ("base", "synthetic_class")

# The output roots of this tool, relative to REPO_ROOT: the artifacts directory holding
# DEFAULT_REPORT and DEFAULT_JSON_REPORT, and the expected directory holding the
# per-case capture snapshot DEFAULT_EXPECTED_DIR names. Every output path must
# canonicalise below one of them or below the temporary directory the run resolves; an
# authored file, a generated warehouse or dbt path, a protected tree and every path of
# the wider filesystem are refused by name.
# Decision rationale: modernization/docs/decision-log.md, row D-125.
OUTPUT_ROOTS = (ARTIFACTS_DIR, DEFAULT_EXPECTED_DIR)

# The one root outside the repository an output path may stand below, and the name the
# diagnostics give it. tempfile.gettempdir() reads TMPDIR, TEMP and TMP before the
# platform default, so a run directed at an operator's own temporary directory writes
# its reports and snapshots there and nowhere else.
TEMPORARY_OUTPUT_ROOT_SOURCE = "the temporary directory (TMPDIR, TEMP, TMP)"

# Modes every output of this tool is written with. A directory this tool creates
# carries DIRECTORY_MODE and a file it writes carries FILE_MODE, each set on the entry
# itself as well as requested at creation, so the ambient umask cannot widen either:
# the two comparison reports and every per-case capture snapshot carry the customer,
# policy and broker values of the compared fixtures, in the report as compared columns
# and in the snapshot as the captured values themselves.
#
# The mode is set on every write rather than on the creation of the name alone, and on
# a capture snapshot whose stored document a comparison confirms equals this run's own
# output, so a report or a snapshot standing at a wider mode carries FILE_MODE from the
# next run on. A snapshot a comparison refuses is left exactly as it stands, and a
# directory that already exists keeps the mode it carries.
# Decision rationale: modernization/docs/decision-log.md, row D-127.
DIRECTORY_MODE = 0o700
FILE_MODE = 0o600

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


class _FieldMapLoader(_DuplicateRejectingLoader):
    """Duplicate-rejecting loader that additionally refuses an alias and deep nesting.

    Mapping construction rejects a repeated key and a key it cannot compare exactly as
    ``_DuplicateRejectingLoader`` does, and rejects the merge key ``<<`` as well, so no
    anchored mapping is folded into another one. Node composition rejects every alias,
    so no anchor expands the document behind the byte bound ``_read_text`` applied, and
    bounds container nesting to ``MAX_DOCUMENT_DEPTH`` levels while the nodes are
    composed, so a document nested past the interpreter's recursion limit is named
    rather than parsed.

    Each refusal raises ``ConfigurationError``, which carries ``EXIT_CONFIGURATION``,
    and names the anchor, the merge key or the line that carries the offending node. It
    is the loader every consumer of the field map applies:
    modernization/extraction/build_sample_commarea.py,
    modernization/extraction/extract_commarea.py and this module, each raising its own
    error type. Decision rationale: modernization/docs/decision-log.md, row D-126.
    """

    def __init__(self, stream: Any) -> None:
        super().__init__(stream)
        self._depth = 0

    def compose_node(self, parent: Any, index: Any) -> Any:
        """Compose one node, refusing an alias and bounding the nesting depth."""
        if self.check_event(yaml.events.AliasEvent):
            event = self.peek_event()
            raise ConfigurationError(
                f"the field map refers to anchor '*{_printable(str(event.anchor))}' at "
                f"line {event.start_mark.line + 1}; an alias is not accepted"
            )
        self._depth += 1
        if self._depth > MAX_DOCUMENT_DEPTH:
            raise ConfigurationError(
                f"the field map nests deeper than the accepted {MAX_DOCUMENT_DEPTH} "
                f"levels at line {self.peek_event().start_mark.line + 1}"
            )
        try:
            return super().compose_node(parent, index)
        finally:
            self._depth -= 1

    def construct_mapping(
        self, node: yaml.MappingNode, deep: bool = False
    ) -> dict[Any, Any]:
        """Construct one mapping, refusing the merge key as well as a repeated key."""
        for key_node, _value_node in node.value:
            if (
                isinstance(key_node, yaml.nodes.ScalarNode)
                and key_node.tag == "tag:yaml.org,2002:merge"
            ):
                raise ConfigurationError(
                    f"the field map uses the merge key '<<' at line "
                    f"{key_node.start_mark.line + 1}; a merge key is not accepted"
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

    The document is parsed by ``_FieldMapLoader``, which refuses a repeated mapping
    key, a key it cannot compare, an alias, the merge key ``<<`` and nesting past
    ``MAX_DOCUMENT_DEPTH`` containers - the loader contract the field map's own header
    states and every consumer of the map applies - then
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
        document = yaml.load(text, Loader=_FieldMapLoader)
    except yaml.YAMLError as error:
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} is not a YAML document this tool "
            f"can read: {_printable(str(error).splitlines()[0] if str(error) else '')}"
        ) from error
    except RecursionError as error:
        raise ConfigurationError(
            f"the field map at {_path_shown(path)} nests containers too deeply to "
            f"parse: {_printable(type(error).__name__)}"
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


# COMMAREA items whose value the seeds of the run determine: the policy number
# the chain assigns, seeded by HARNESS_POLICY_NUMBER, and the timestamp it reads
# back, seeded by HARNESS_LASTCHANGED. Both seeds are documented in
# modernization/harness/run_harness.sh and both carry a default.
POLICY_NUMBER_ITEM = "CA-POLICY-NUM"
LASTCHANGED_ITEM = "CA-LASTCHANGED"

# Forms the assigned policy number stands in: zero-padded to the width of its
# COMMAREA window, as the digits of the number alone, and at the end of the
# composite VSAM key, behind the type letter and the customer number.
SNAPSHOT_FORM_PADDED = "padded"
SNAPSHOT_FORM_DECIMAL = "decimal"
SNAPSHOT_FORM_TRAILING = "trailing"

# Symbols a snapshot carries in place of a value the seeds of the run determine.
# The padded symbol states the window width the run resolved for the policy
# number, so the document records the width it was padded to.
SNAPSHOT_POLICY_NUMBER_SYMBOL = "<policy-number>"
SNAPSHOT_POLICY_NUMBER_PADDED_SYMBOL = "<policy-number:{width}>"
SNAPSHOT_LASTCHANGED_SYMBOL = "<last-changed>"

# Snapshot keys the assigned policy number reaches, with the form each one
# carries it in, and the keys the assigned timestamp reaches. A capture key is
# the COMMAREA item with its hyphens replaced, so the capture spelling and the
# window spelling of one item are two distinct keys and one mapping covers the
# capture keys, the COMMAREA windows and the driver-input windows of a document.
# A key of either mapping is symbolised only where its value equals the value the
# run assigned, so a window the request supplies - the driver input carries the
# policy number as zeros before the chain assigns one - stays compared as it
# stands.
SNAPSHOT_IDENTITY_KEYS = {
    POLICY_NUMBER_ITEM: SNAPSHOT_FORM_PADDED,
    _capture_key_of(POLICY_NUMBER_ITEM): SNAPSHOT_FORM_PADDED,
    VSAM_POLICY_NUM_KEY: SNAPSHOT_FORM_PADDED,
    SQL_CAPTURE_KEYS["policy_number"]: SNAPSHOT_FORM_DECIMAL,
    VSAM_KEY_KEY: SNAPSHOT_FORM_TRAILING,
}
SNAPSHOT_LASTCHANGED_KEYS = (
    LASTCHANGED_ITEM,
    _capture_key_of(LASTCHANGED_ITEM),
    SQL_CAPTURE_KEYS["last_changed"],
)


class SnapshotSeeds(NamedTuple):
    """The identity and the timestamp of one run, in the forms a snapshot holds.

    ``padded`` and ``decimal`` are the assigned policy number of the run,
    zero-padded to the width of its COMMAREA window and as its digits alone;
    ``padded_symbol`` is the symbol that replaces the padded form and states that
    width. ``last_changed`` is the timestamp the returned COMMAREA carries. A
    member holding the empty string leaves the values of its keys as they stand.
    """

    padded: str
    decimal: str
    padded_symbol: str
    last_changed: str


def snapshot_seeds(
    result: CaseResult, harness: HarnessCase, field_map: FieldMap
) -> SnapshotSeeds:
    """Return the seeded values of one compared case, read from its own output.

    The identity is the policy number this run resolved from the returned
    COMMAREA and compared against both canonical rows, and the timestamp is the
    window of that same record. Both are the authority of the case: a capture or
    a key that carries another value is left as it stands, so the snapshot still
    reports it.
    """
    window = field_map.window(POLICY_NUMBER_ITEM)
    padded, decimal = "", ""
    if result.policy_number is not None:
        decimal = str(result.policy_number)
        padded = decimal.zfill(window.length)
    return SnapshotSeeds(
        padded=padded,
        decimal=decimal,
        padded_symbol=SNAPSHOT_POLICY_NUMBER_PADDED_SYMBOL.format(
            width=window.length
        ),
        last_changed=slice_window(
            harness.commarea, field_map.window(LASTCHANGED_ITEM), "returned COMMAREA"
        ).strip(),
    )


def _snapshot_value(key: str, raw: str, seeds: SnapshotSeeds) -> str:
    """Return the snapshot form of ``raw`` under ``key``.

    A key of ``SNAPSHOT_IDENTITY_KEYS`` whose value is the assigned policy number
    in the form that key carries yields the symbol of that form, and the
    composite VSAM key yields its own leading characters followed by the symbol.
    A key of ``SNAPSHOT_LASTCHANGED_KEYS`` whose value is the assigned timestamp
    yields the timestamp symbol. Every other key, and every value that is not the
    value this run assigned, is returned unchanged.
    """
    form = SNAPSHOT_IDENTITY_KEYS.get(key)
    if form is not None and seeds.padded:
        if form == SNAPSHOT_FORM_PADDED and raw == seeds.padded:
            return seeds.padded_symbol
        if form == SNAPSHOT_FORM_DECIMAL and raw == seeds.decimal:
            return SNAPSHOT_POLICY_NUMBER_SYMBOL
        if form == SNAPSHOT_FORM_TRAILING and raw.endswith(seeds.padded):
            return f"{raw[: -len(seeds.padded)]}{seeds.padded_symbol}"
    if key in SNAPSHOT_LASTCHANGED_KEYS and seeds.last_changed:
        if raw == seeds.last_changed:
            return SNAPSHOT_LASTCHANGED_SYMBOL
    return raw


def build_snapshot(
    result: CaseResult, harness: HarnessCase, field_map: FieldMap
) -> dict[str, Any]:
    """Return the normalised harness capture snapshot of one compared case.

    It carries every capture key this run read with the value it held, every
    COMMAREA and driver-input window this run sliced, and the case identity the
    comparison used. Keys and window names are sorted, so two runs of the same
    harness output write the same document.

    A value the seeds of the run determine - the assigned policy number in each
    of the three forms it appears in and the assigned timestamp - is carried as
    the symbol of that position rather than as its digits, so a run under another
    HARNESS_POLICY_NUMBER or HARNESS_LASTCHANGED writes the same document while
    every other value, and any of those values that is not the one this run
    assigned, is carried as it stands.
    """
    seeds = snapshot_seeds(result, harness, field_map)
    captures: dict[str, str] = {}
    commarea_windows: dict[str, str] = {}
    driver_windows: dict[str, str] = {}
    for comparison in result.comparisons:
        for witness in comparison.witnesses:
            if witness.raw is None or witness.key is None:
                continue
            value = _snapshot_value(witness.key, witness.raw, seeds)
            if witness.family == "capture":
                captures[witness.key] = value
            elif witness.family == "commarea":
                commarea_windows[witness.key] = value
            elif witness.family == "driver-input":
                driver_windows[witness.key] = value
    for assertion in result.assertions:
        if (
            assertion.group in (GROUP_CHAIN, GROUP_VSAM)
            and not assertion.missing
            and assertion.name in harness.captures
        ):
            captures[assertion.name] = _snapshot_value(
                assertion.name, harness.captures[assertion.name], seeds
            )
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


def snapshot_path_of(case: str, expected_dir: Path) -> Path:
    """Return the capture snapshot path of ``case`` inside ``expected_dir``.

    It is the one path a case writes below the expected directory, and the path the
    startup confinement check of ``_confirm_output_destinations`` validates for every
    selected case, so the directory a command line names is judged by the file the run
    would write inside it.
    """
    return expected_dir / case.lower() / SNAPSHOT_NAME


def apply_snapshot(
    path: Path, document: Mapping[str, Any], *, refresh: bool = False
) -> str:
    """Write the snapshot at ``path``, or compare it with the one already there.

    A path that carries nothing is written and reported as written. A path that
    carries a snapshot is read and compared, and a difference raises
    ``HarnessInputError`` naming every key that differs with both values.

    ``refresh`` replaces the snapshot already there with ``document`` and reports
    it as refreshed. The path it writes is the snapshot of the case inside the
    expected directory of the run, and the write goes through the same guard every
    output of this tool goes through, which refuses a path resolving inside a
    protected tree.
    """
    rendered = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if not path.exists():
        _write_output(path, rendered)
        return SNAPSHOT_STATE_WRITTEN
    if refresh:
        _write_output(path, rendered)
        return SNAPSHOT_STATE_REFRESHED
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
    # A matched snapshot holds the bytes this run would have written, so it is brought
    # to the mode a write gives it. A snapshot that differs is left exactly as it
    # stands, above, together with everything else about the failed comparison.
    _narrow_output(path)
    return SNAPSHOT_STATE_MATCHED



# --------------------------------------------------------------------------
# Output paths
# --------------------------------------------------------------------------
def canonical_temporary_root() -> Path:
    """Return the temporary directory this run accepts, as the path it canonicalises to.

    ``tempfile.gettempdir()`` reads TMPDIR, TEMP and TMP in that order and falls back to
    the platform default, so the directory an operator points this run at is the one
    accepted here. The value is canonicalised, so a temporary directory reached through
    a symbolic link is compared in the same form a canonicalised output path carries.
    """
    return Path(os.path.realpath(tempfile.gettempdir()))


def _canonical_output_roots() -> tuple[Path, ...]:
    """Return the in-repository output roots as the canonical paths they name.

    Each root is resolved, so a symbolic-link component of the checkout is compared in
    the form a canonicalised output path carries. A root that does not exist yet
    resolves to the pathname itself, which is the form a path below it canonicalises to.
    """
    return tuple(
        Path(os.path.realpath(REPO_ROOT / relative)) for relative in OUTPUT_ROOTS
    )


def _accepted_output_roots() -> str:
    """Return the roots an output path may stand below, as one diagnostic fragment."""
    return (
        f"below {_quote_all(OUTPUT_ROOTS)} inside "
        f"{_printable(str(REPO_ROOT))}, or below "
        f"{_printable(str(canonical_temporary_root()))}"
    )


def _canonical_output_path(path: Path) -> Path:
    """Return the path ``path`` actually names, with its parent chain resolved.

    Every component above the final one is resolved, so a symbolic-link chain, a
    symbolic-link parent directory, a ``..`` component and a ``/proc/self/cwd`` style
    alias are all judged by the path they name rather than the path they spell. The
    final component is carried as spelled: a link standing there is refused by
    ``_refuse_protected_path`` before anything is written.
    """
    absolute = _resolved(path)
    return Path(os.path.realpath(absolute.parent)) / absolute.name


def _refuse_protected_path(path: Path) -> None:
    """Refuse an output path this tool does not write, before anything is created.

    The path is canonicalised by ``_canonical_output_path`` and then held to one
    confinement policy, in this order:

    * a path inside one of ``PROTECTED_TREES`` is refused by that tree's name;
    * a path inside the repository must stand below one of ``OUTPUT_ROOTS`` - the
      artifacts directory of the two reports and the expected directory of the per-case
      snapshots - and every other path inside the repository is refused, an authored
      file, a dbt or warehouse path and the harness build tree among them;
    * a path outside the repository must stand below ``canonical_temporary_root()``, and
      every other path of the filesystem is refused, /etc/passwd and every other system
      file among them;
    * a final component that is a symbolic link is refused, so a link cannot redirect
      the write to the file it names.

    Raises ``ConfigurationError`` naming the path, the canonical form it resolves to and
    the roots that are accepted, on one line.
    """
    canonical = _canonical_output_path(path)
    for tree in PROTECTED_TREES:
        root = Path(os.path.realpath(REPO_ROOT / tree))
        if canonical == root or root in canonical.parents:
            raise ConfigurationError(
                f"the output path {_path_shown(path)} resolves inside {tree}/, which "
                f"this tool never writes: it resolves to "
                f"{_printable(str(canonical))}"
            )
    repository = Path(os.path.realpath(REPO_ROOT))
    inside_repository = canonical == repository or repository in canonical.parents
    if inside_repository:
        if not any(root in canonical.parents for root in _canonical_output_roots()):
            raise ConfigurationError(
                f"the output path {_path_shown(path)} resolves inside the repository "
                f"directory {_printable(str(repository))} and outside every output "
                f"root {_quote_all(OUTPUT_ROOTS)}: it resolves to "
                f"{_printable(str(canonical))}; an output path stands "
                f"{_accepted_output_roots()}"
            )
    elif canonical_temporary_root() not in canonical.parents:
        raise ConfigurationError(
            f"the output path {_path_shown(path)} resolves outside the repository "
            f"directory {_printable(str(repository))} and outside the temporary "
            f"directory {_printable(str(canonical_temporary_root()))}: it resolves to "
            f"{_printable(str(canonical))}; an output path stands "
            f"{_accepted_output_roots()}"
        )
    if os.path.islink(canonical):
        raise ConfigurationError(
            f"the output path {_path_shown(path)} is a symbolic link, which this tool "
            f"never writes through: it resolves to {_printable(str(canonical))}"
        )


def _create_output_directory(directory: Path) -> None:
    """Create ``directory`` and every missing directory above it, mode DIRECTORY_MODE.

    Each missing component is created one at a time and its mode is then set on the
    created directory itself, so a directory holding a report or a snapshot carries
    ``DIRECTORY_MODE`` whatever the ambient umask requested rather than only the
    innermost one carrying it. A directory that already exists keeps the mode it
    carries, so the tracked artifacts and expected directories of a checkout are left
    as that checkout holds them.

    Raises ``ConfigurationError`` when a directory cannot be created or its mode
    cannot be set.
    """
    missing: list[Path] = []
    probe = directory
    while not probe.exists():
        missing.append(probe)
        if probe.parent == probe:
            break
        probe = probe.parent
    for component in reversed(missing):
        try:
            os.mkdir(component, DIRECTORY_MODE)
        except FileExistsError:
            continue
        except OSError as error:
            raise ConfigurationError(
                f"the directory at {_path_shown(component)} could not be created: "
                f"{_printable(error.strerror or type(error).__name__)}"
            ) from error
        try:
            descriptor = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            )
        except OSError as error:
            raise ConfigurationError(
                f"the directory at {_path_shown(component)} could not be opened to "
                f"set its mode: "
                f"{_printable(error.strerror or type(error).__name__)}"
            ) from error
        try:
            os.fchmod(descriptor, DIRECTORY_MODE)
        except OSError as error:
            raise ConfigurationError(
                f"the mode of the directory at {_path_shown(component)} could not be "
                f"set to {DIRECTORY_MODE:04o}: "
                f"{_printable(error.strerror or type(error).__name__)}"
            ) from error
        finally:
            os.close(descriptor)


def _narrow_output(path: Path) -> bool:
    """Set ``FILE_MODE`` on an output of this tool that already carries its content.

    It reaches the one output this tool leaves in place: a capture snapshot whose
    stored document this run has just confirmed equals the document it would have
    written, which carries the same bytes a rewrite would have left there. The two
    reports and a written or refreshed snapshot pass through ``_write_output``, which
    sets the mode at the creation instead.

    The entry is opened without following a symbolic link and the mode is set on that
    descriptor, so what is narrowed is the file the confinement check accepted. A mode
    that already reads ``FILE_MODE`` is left alone and reported as unchanged, and an
    entry that is not a regular file is left alone as well.

    Returns whether the mode was changed. Raises ``ConfigurationError`` when the entry
    cannot be opened or its mode cannot be set.
    """
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as error:
        raise ConfigurationError(
            f"the file at {_path_shown(path)} could not be opened to set its mode: "
            f"{_printable(error.strerror or type(error).__name__)}"
        ) from error
    try:
        information = os.fstat(descriptor)
        if not stat.S_ISREG(information.st_mode):
            return False
        if stat.S_IMODE(information.st_mode) == FILE_MODE:
            return False
        os.fchmod(descriptor, FILE_MODE)
    except OSError as error:
        raise ConfigurationError(
            f"the mode of the file at {_path_shown(path)} could not be set to "
            f"{FILE_MODE:04o}: "
            f"{_printable(error.strerror or type(error).__name__)}"
        ) from error
    finally:
        os.close(descriptor)
    return True


def _write_output(path: Path, text: str) -> None:
    """Write ``text`` to ``path``, creating the directories above it.

    ``_refuse_protected_path`` decides first, so a path outside the accepted roots is
    refused before a directory is created or a byte is written. It is the single funnel
    every output of this tool passes through: both reports and every capture snapshot.

    The name is opened without following a symbolic link, so a link standing there is
    refused here as well as by the guard above, and ``FILE_MODE`` is requested at the
    creation and set on the open descriptor before the text is written: a report or a
    snapshot is never readable by another user, not in the window between its creation
    and its content and not afterwards, and one written under an earlier umask is
    narrowed by the run that rewrites it.
    """
    _refuse_protected_path(path)
    _create_output_directory(path.parent)
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW,
            FILE_MODE,
        )
    except OSError as error:
        raise ConfigurationError(
            f"the file at {_path_shown(path)} could not be opened for writing: "
            f"{_printable(error.strerror or type(error).__name__)}"
        ) from error
    try:
        os.fchmod(descriptor, FILE_MODE)
        handle = os.fdopen(descriptor, "w", encoding="utf-8")
    except OSError as error:
        os.close(descriptor)
        raise ConfigurationError(
            f"the mode of the file at {_path_shown(path)} could not be set to "
            f"{FILE_MODE:04o}: "
            f"{_printable(error.strerror or type(error).__name__)}"
        ) from error
    # The handle owns the descriptor from here, so the context manager closes it
    # exactly once whether the write completes or fails.
    try:
        with handle:
            handle.write(text)
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
    refresh_snapshot: bool = False,
) -> CaseResult:
    """Compare one case against both canonical relations and return its result.

    The request id and the policy number come from the returned COMMAREA, the
    policy type from the request routing, and the two canonical rows from the
    natural key (source_system_key, policy_number). Every column of both relations
    is then compared, followed by the chain-completion assertions, the VSAM
    corroboration, the cross-relation identity of the three shared columns and the
    capture snapshot. ``refresh_snapshot`` rewrites that snapshot instead of
    comparing it; every other comparison of the case is made either way.
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

    snapshot_path = snapshot_path_of(case, expected_dir)
    result.snapshot_path = _path_shown(snapshot_path)
    result.snapshot_state = apply_snapshot(
        snapshot_path,
        build_snapshot(result, harness, field_map),
        refresh=refresh_snapshot,
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
    transform_freshness: dict[str, Any] = field(default_factory=dict)
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
            "transform_freshness": self.transform_freshness,
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
                    "transform freshness",
                    f"{report.transform_freshness.get('verdict', '—')} — "
                    f"{report.transform_freshness.get('note', 'not established')}",
                ),
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
    lines.extend(_render_transform_freshness(report, label))
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


def _render_transform_freshness(report: RunReport, label: str) -> list[str]:
    """Return the Markdown section of the transform freshness precondition.

    The section states the verdict of the precondition, the dbt invocation the
    artifact records and the node statuses it holds, and it is rendered whichever
    verdict the precondition reached, so a published report always states which
    transform outcome the comparison stands on.
    """
    document = report.transform_freshness
    lines = ["## Transform freshness precondition", ""]
    if not document:
        lines.extend(
            [
                (
                    "The precondition was not evaluated on this run, so no dbt "
                    f"transform outcome stands behind the values below — {label}."
                ),
                "",
            ]
        )
        return lines
    invocation = document.get("invocation", {})
    counts = document.get("nodes", {})
    lines.extend(
        _table(
            ("Item", "Value"),
            (
                ("verdict", document.get("verdict")),
                ("dbt run artifact", document.get("path")),
                ("dbt version", invocation.get("dbt_version")),
                ("artifact schema", invocation.get("schema_version")),
                ("invocation id", invocation.get("invocation_id")),
                ("recorded at", invocation.get("generated_at")),
                ("subcommand", invocation.get("command")),
                ("dbt target", invocation.get("dbt_target")),
                ("elapsed seconds", invocation.get("elapsed_time")),
                ("nodes recorded", counts.get("total")),
                ("nodes successful", counts.get("accepted")),
                ("nodes warned", counts.get("warned")),
                ("nodes refused", counts.get("refused")),
                (
                    "statuses accepted",
                    ", ".join(document.get("accepted_statuses", ())),
                ),
                ("statuses warned", ", ".join(document.get("warned_statuses", ()))),
                ("statuses refused", ", ".join(document.get("refused_statuses", ()))),
            ),
        )
    )
    lines.append("")
    warned = list(document.get("warned_nodes", ()))
    if warned:
        lines.extend(["### Nodes dbt recorded as warned", ""])
        lines.extend(
            _table(
                ("Node", "Status", "Message"),
                (
                    (node.get("unique_id"), node.get("status"), node.get("message"))
                    for node in warned
                ),
            )
        )
        lines.extend(
            [
                "",
                (
                    "A warned node passes this precondition and is named here — "
                    f"{label}."
                ),
                "",
            ]
        )
    refused = list(document.get("refused_nodes", ()))
    if refused:
        lines.extend(["### Nodes dbt did not record as successful", ""])
        lines.extend(
            _table(
                ("Node", "Status", "Message"),
                (
                    (node.get("unique_id"), node.get("status"), node.get("message"))
                    for node in refused
                ),
            )
        )
        lines.append("")
    if transform_is_fresh(document):
        lines.extend(
            [
                (
                    "Every node of the last dbt invocation recorded a successful "
                    f"status, so the warehouse state below is the state that "
                    f"invocation produced — {label}."
                ),
                "",
            ]
        )
        return lines
    lines.extend(
        [
            (
                f"**The precondition refused this warehouse state** (exit status "
                f"{FRESHNESS_REFUSED_STATUS}): no comparison was made and no "
                f"verdict is published for it — {label}."
            ),
            "",
        ]
    )
    lines.extend(f"- {_printable(reason)}" for reason in document.get("refusals", ()))
    lines.append("")
    return lines


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
# Transform freshness
# --------------------------------------------------------------------------
def _recorded(value: Any, limit: int = 200) -> str | None:
    """Return ``value`` as one printable line of at most ``limit`` characters.

    A value that is absent yields None, so a report records the absence rather
    than a placeholder. Only the members named by ``read_transform_freshness`` are
    passed through here; no other member of the artifact is read or reported.
    """
    if value is None:
        return None
    text = _printable(str(value).replace("\r", " ").replace("\n", " ")).strip()
    if not text:
        return None
    return text if len(text) <= limit else f"{text[:limit]}...({len(text)} characters)"


def _freshness_refused(document: dict[str, Any], reason: str) -> dict[str, Any]:
    """Record ``reason`` against ``document``, note it and return it refused."""
    document["verdict"] = FRESHNESS_REFUSED
    document["refusals"].append(reason)
    document["note"] = _freshness_note(document)
    return document


def read_transform_freshness(path: Path) -> dict[str, Any]:
    """Return what dbt recorded for the transform that produced the warehouse state.

    ``path`` names the run_results.json of the one dbt project of this bridge. The
    document returned carries the verdict of the precondition, FRESHNESS_FRESH or
    FRESHNESS_REFUSED, the reason of every refusal, the invocation dbt recorded and
    the node statuses it holds. Nothing is raised and nothing is written: a caller
    records this document in both reports whichever verdict it carries.

    The verdict is FRESHNESS_REFUSED where the artifact is absent, cannot be
    examined, is larger than MAX_RUN_RESULTS_BYTES, cannot be read, is not UTF-8
    text, is not JSON, is not a JSON object, carries no results member, carries a
    results member that is not a list, carries an empty results list, carries a
    result that is not an object, carries a result without a usable status, or
    carries a node whose status is not one of DBT_STATUSES_ACCEPTED. A node status
    of DBT_STATUSES_WARNED passes and is named in the document and in both reports.

    What the artifact establishes, and what it does not. dbt-core writes it at the
    end of every invocation that reaches its first node, so it states the outcome
    of that invocation and of no other; an invocation that ends before its first
    node - a refused connection, a profile that does not render, a target name that
    does not exist - leaves the previous artifact in place. The invocation
    identifier, the recorded moment, the dbt version, the subcommand and the dbt
    target name are therefore carried into both reports, and
    modernization/dbt/genapp_rqi/dbt_project.yml states the "dbt clean" contract
    that leaves no earlier artifact behind.

    Only metadata.dbt_schema_version, metadata.dbt_version,
    metadata.invocation_id, metadata.generated_at, elapsed_time, args.which,
    args.target and the unique_id, status and message of each result are read. No
    other member is read, so no connection value, credential or environment listing
    of the artifact reaches a report.
    """
    document: dict[str, Any] = {
        "path": _path_shown(path),
        "verdict": FRESHNESS_FRESH,
        "refusals": [],
        "accepted_statuses": list(DBT_STATUSES_ACCEPTED),
        "warned_statuses": list(DBT_STATUSES_WARNED),
        "refused_statuses": list(DBT_STATUSES_REFUSED),
        "invocation": {},
        "nodes": {"total": 0, "accepted": 0, "warned": 0, "refused": 0},
        "warned_nodes": [],
        "refused_nodes": [],
    }
    shown = _path_shown(path)
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        return _freshness_refused(
            document,
            f"no dbt run artifact stands at {shown}, so no transform outcome is "
            f"recorded for the warehouse state this run would compare",
        )
    except OSError as error:
        return _freshness_refused(
            document,
            f"the dbt run artifact at {shown} cannot be examined: "
            f"{_printable(error.strerror or type(error).__name__)}",
        )
    if size > MAX_RUN_RESULTS_BYTES:
        return _freshness_refused(
            document,
            f"the dbt run artifact at {shown} holds {size} bytes, beyond the "
            f"{MAX_RUN_RESULTS_BYTES} bytes this tool reads",
        )
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        return _freshness_refused(
            document,
            f"the dbt run artifact at {shown} is not UTF-8 text at byte "
            f"{error.start}",
        )
    except OSError as error:
        return _freshness_refused(
            document,
            f"the dbt run artifact at {shown} cannot be read: "
            f"{_printable(error.strerror or type(error).__name__)}",
        )
    try:
        loaded = json.loads(text)
    except ValueError as error:
        return _freshness_refused(
            document,
            f"the dbt run artifact at {shown} is not JSON: {_first_line(error)}",
        )
    if not isinstance(loaded, dict):
        return _freshness_refused(
            document,
            f"the dbt run artifact at {shown} is not a JSON object but a "
            f"{type(loaded).__name__}",
        )
    metadata = loaded.get("metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    arguments = loaded.get("args")
    arguments = arguments if isinstance(arguments, Mapping) else {}
    document["invocation"] = {
        "schema_version": _recorded(metadata.get("dbt_schema_version")),
        "dbt_version": _recorded(metadata.get("dbt_version")),
        "invocation_id": _recorded(metadata.get("invocation_id")),
        "generated_at": _recorded(metadata.get("generated_at")),
        "command": _recorded(arguments.get("which")),
        "dbt_target": _recorded(arguments.get("target")),
        "elapsed_time": _recorded(loaded.get("elapsed_time")),
    }
    results = loaded.get("results")
    if results is None:
        return _freshness_refused(
            document,
            f"the dbt run artifact at {shown} carries no results member, so it "
            f"records the outcome of no node",
        )
    if not isinstance(results, list):
        return _freshness_refused(
            document,
            f"the results member of the dbt run artifact at {shown} is not a list "
            f"but a {type(results).__name__}",
        )
    if not results:
        return _freshness_refused(
            document,
            f"the dbt run artifact at {shown} records no node, so no transform "
            f"outcome is established for the warehouse state this run would compare",
        )
    document["nodes"]["total"] = len(results)
    for index, entry in enumerate(results):
        if not isinstance(entry, Mapping):
            document["nodes"]["refused"] += 1
            _freshness_refused(
                document,
                f"result {index} of the dbt run artifact at {shown} is not an "
                f"object but a {type(entry).__name__}",
            )
            continue
        name = _recorded(entry.get("unique_id")) or f"result {index}"
        message = _recorded(entry.get("message"))
        raw_status = entry.get("status")
        status = _recorded(raw_status)
        if status is None:
            document["nodes"]["refused"] += 1
            document["refused_nodes"].append(
                {"unique_id": name, "status": None, "message": message}
            )
            _freshness_refused(
                document,
                f"the node {name} of the dbt run artifact at {shown} records no "
                f"status",
            )
            continue
        folded = status.lower()
        if folded in DBT_STATUSES_ACCEPTED:
            document["nodes"]["accepted"] += 1
            continue
        if folded in DBT_STATUSES_WARNED:
            document["nodes"]["warned"] += 1
            document["warned_nodes"].append(
                {"unique_id": name, "status": status, "message": message}
            )
            continue
        document["nodes"]["refused"] += 1
        document["refused_nodes"].append(
            {"unique_id": name, "status": status, "message": message}
        )
        recognised = "" if folded in DBT_STATUSES_REFUSED else " unrecognised"
        _freshness_refused(
            document,
            f"the node {name} of the dbt run artifact at {shown} recorded the"
            f"{recognised} status {_shown(status)}"
            + (f": {message}" if message else ""),
        )
    document["note"] = _freshness_note(document)
    return document


def _freshness_note(document: Mapping[str, Any]) -> str:
    """Return the one-line summary of a freshness document, for the report tables."""
    counts = document.get("nodes", {})
    invocation = document.get("invocation", {})
    refusals = list(document.get("refusals", ()))
    if refusals:
        head = refusals[0]
        remainder = (
            "" if len(refusals) == 1 else f" (and {len(refusals) - 1} further refusal"
            f"{'' if len(refusals) == 2 else 's'})"
        )
        return f"{head}{remainder}"
    command = invocation.get("command") or "an unnamed subcommand"
    warned = counts.get("warned", 0)
    return (
        f"dbt {command} recorded {counts.get('total', 0)} node"
        f"{'' if counts.get('total', 0) == 1 else 's'}, "
        f"{counts.get('accepted', 0)} of them successful and {warned} warned"
        + (
            ""
            if not warned
            else ": "
            + ", ".join(
                str(node.get("unique_id")) for node in document.get("warned_nodes", ())
            )
        )
    )


def transform_is_fresh(document: Mapping[str, Any]) -> bool:
    """Return whether ``document`` establishes a successful transform."""
    return document.get("verdict") == FRESHNESS_FRESH


def freshness_diagnostic(document: Mapping[str, Any]) -> str:
    """Return the refusal one line, naming what the artifact recorded."""
    refusals = list(document.get("refusals", ()))
    named = "; ".join(refusals[:5])
    remainder = (
        "" if len(refusals) <= 5 else f"; and {len(refusals) - 5} further refusals"
    )
    return (
        "the transform that produced this warehouse state is not established as "
        f"successful, so no verdict is published: {named}{remainder}"
    )


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
  3  the warehouse content was refused: the transform freshness precondition
     refused the state, because the dbt run artifact is absent, unreadable or
     records a node dbt did not record as successful; or the warehouse answered a
     canonical relation or column set other than the declared one, or other than
     exactly one row for a natural key
  4  a connection, configuration or usage failure, an output path outside the
     accepted roots among them; nothing is written
  5  one case of --self-test did not hold; a comparison run never returns it
"""


def build_parser() -> _ArgumentParser:
    """Return the command-line parser of this tool."""
    parser = _ArgumentParser(
        prog=_PROGRAM,
        description=(
            "Compare the GnuCOBOL harness captures of a case with the two canonical "
            "warehouse rows for the same policy, column by column. Reads the harness "
            "output and the dbt run artifact alone: no driver is started, no program "
            "is compiled, no chain is executed and no model is run. A warehouse state "
            "whose last dbt invocation did not succeed is refused before any "
            "comparison is made. Flow context: "
            "Figure 5 — Validation Harness Control Flow "
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
        help=(
            f"Markdown report to write; it must canonicalise below {ARTIFACTS_DIR}, "
            f"below {DEFAULT_EXPECTED_DIR} or below the temporary directory this run "
            "resolves, and every other path is refused before anything is written. "
            f"Default: {DEFAULT_REPORT}."
        ),
    )
    parser.add_argument(
        "--json",
        dest="json_report",
        default=DEFAULT_JSON_REPORT,
        metavar="PATH",
        help=(
            f"JSON report to write; it is confined to the same roots as --report. "
            f"Default: {DEFAULT_JSON_REPORT}."
        ),
    )
    parser.add_argument(
        "--expected-dir",
        default=DEFAULT_EXPECTED_DIR,
        metavar="PATH",
        help=(
            "directory of the per-case capture snapshots, one "
            f"{SNAPSHOT_NAME} per case; the snapshot path of every selected case is "
            "confined to the same roots as --report and a directory outside them is "
            f"refused before anything is written. Default: {DEFAULT_EXPECTED_DIR}."
        ),
    )
    parser.add_argument(
        "--refresh-snapshot",
        action="store_true",
        help=(
            f"rewrite the {SNAPSHOT_NAME} of every compared case from this run "
            "instead of comparing it, and report each one as refreshed. Without it a "
            "snapshot already on disk is compared and a difference fails the run. It "
            "writes no path outside the per-case snapshot of the expected directory "
            "and is confined to the accepted output roots, as every output of "
            "this tool is."
        ),
    )
    parser.add_argument(
        "--dbt-run-results",
        default=DEFAULT_DBT_RUN_RESULTS,
        metavar="PATH",
        help=(
            "dbt run artifact naming the outcome of the transform that produced the "
            "warehouse state. A run whose artifact is absent, unreadable or carrying "
            "a node dbt did not record as successful publishes no verdict and returns "
            f"{FRESHNESS_REFUSED_STATUS}. Default: {DEFAULT_DBT_RUN_RESULTS}."
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run the built-in case matrix and exit. It opens no warehouse, reaches "
            "no endpoint, reads no harness output and no field map, and writes "
            "nothing outside one private temporary directory it creates and "
            "removes; a case that does not hold returns "
            f"{EXIT_SELF_TEST_FAILED}. Accepted with --quiet alone."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help=(
            "print the verdict line alone; with --self-test, print the failing case "
            "lines and the summary line alone."
        ),
    )
    return parser


# Option of every setting a comparison run reads, by the destination argparse
# stores it under. --self-test reads none of them and is refused alongside any
# of them whose value differs from the declared default. The case matrix asserts
# that this inventory names every destination a parsed command line carries.
_RUN_OPTIONS = (
    ("case", "--case"),
    ("cases", "--cases"),
    ("run_dir", "--run-dir"),
    ("captures", "--captures"),
    ("commarea_post", "--commarea-post"),
    ("sample_record", "--sample-record"),
    ("field_map", "--field-map"),
    ("target", "--target"),
    ("database", "--database"),
    ("source_system_key", "--source-system-key"),
    ("report", "--report"),
    ("json_report", "--json"),
    ("expected_dir", "--expected-dir"),
    ("refresh_snapshot", "--refresh-snapshot"),
    ("dbt_run_results", "--dbt-run-results"),
)


def _refuse_self_test_companions(
    parser: _ArgumentParser, arguments: argparse.Namespace
) -> None:
    """Refuse --self-test alongside an option a comparison run would have read.

    The case matrix reads no input, opens no warehouse and writes no report of
    the run. Every option of ``_RUN_OPTIONS`` is compared with the default the
    parser declares, and a value that differs is named in the diagnostic.
    """
    supplied = [
        option
        for dest, option in _RUN_OPTIONS
        if getattr(arguments, dest) != parser.get_default(dest)
    ]
    if supplied:
        raise ConfigurationError(
            "--self-test reads no input and opens no warehouse, so it accepts none "
            f"of {_quote_all(supplied)}"
        )


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
    refresh_snapshot: bool
    dbt_run_results: Path
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
    settings = Settings(
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
        refresh_snapshot=bool(arguments.refresh_snapshot),
        dbt_run_results=_resolved(arguments.dbt_run_results),
        quiet=bool(arguments.quiet),
    )
    _confirm_output_destinations(settings)
    return settings


def _confirm_output_destinations(settings: Settings) -> None:
    """Confine every path this run would write, before anything is read or opened.

    The three destinations a command line names are validated here: the Markdown
    report, the JSON report and, for every selected case, the capture snapshot inside
    the expected directory. Each one goes through ``_refuse_protected_path``, the same
    guard ``_write_output`` applies at the moment of the write, so a destination outside
    the accepted roots ends the run with ``EXIT_CONFIGURATION`` and one diagnostic
    before the field map is read, the warehouse is opened or a report is rendered -
    which is what the documented "nothing is written on this path" status means.

    Raises ``ConfigurationError`` naming the first destination that is refused.
    """
    for path in (
        settings.report,
        settings.json_report,
        *(snapshot_path_of(case, settings.expected_dir) for case in settings.cases),
    ):
        _refuse_protected_path(path)



# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------
def run(settings: Settings) -> RunReport:
    """Compare every selected case and return the report of the run.

    The field map is read and checked, the transform freshness precondition is
    evaluated, the warehouse is opened, the canonical inventory is asserted once,
    and each case is then read and compared. A failure of one case is recorded
    against that case and the remaining cases are still compared, so one run
    reports the whole selection.

    The precondition stands ahead of every comparison: where the dbt run artifact
    does not establish that the transform which produced the warehouse state
    succeeded, the refusal is recorded in the report, no case is read, no row is
    compared and the run carries FRESHNESS_REFUSED_STATUS.
    """
    field_map = load_field_map(settings.field_map)
    freshness = read_transform_freshness(settings.dbt_run_results)
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
        transform_freshness=freshness,
        gate_artifact=read_gate_artifact(_resolved(ARTIFACTS_DIR)),
        return_codes=dict(field_map.return_codes),
    )
    try:
        if not transform_is_fresh(freshness):
            report.errors.append(freshness_diagnostic(freshness))
            report.statuses.append(FRESHNESS_REFUSED_STATUS)
            return report
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
                        refresh_snapshot=settings.refresh_snapshot,
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
    refreshed = [
        case.case
        for case in report.cases
        if case.snapshot_state == SNAPSHOT_STATE_REFRESHED
    ]
    if refreshed:
        print(
            f"{_PROGRAM}: --refresh-snapshot rewrote the capture snapshot of "
            f"{', '.join(refreshed)} under {_path_shown(settings.expected_dir)}; the "
            f"snapshot of those cases was not compared"
        )
    print(f"{_PROGRAM}: markdown report {_path_shown(settings.report)}")
    print(f"{_PROGRAM}: json report {_path_shown(settings.json_report)}")
    print(verdict)
    if report.local_substitute:
        print(f"{_PROGRAM}: {AWS_OPEN_TEXT}")


# --------------------------------------------------------------------------
# Self-test: fixtures
# --------------------------------------------------------------------------
# Every case below drives the comparison functions of this module in this
# process over records it builds itself, so no case opens a warehouse, reads a
# harness artifact, reads the field map or reaches an endpoint. Each case states
# what it observed in its return value, and one failing case carries the run to
# EXIT_SELF_TEST_FAILED.
class _SelfTestFailure(Exception):
    """One self-test case did not hold; the message states what was observed."""


class _SelfTestOutcome(NamedTuple):
    """The outcome of one self-test case."""

    name: str
    passed: bool
    detail: str


# Prefix of the private temporary directory one self-test run works inside.
_SCRATCH_PREFIX = "diff-harness-selftest-"

# Case, relations, items and locators the built records carry. The case and the
# relations are the declared ones, and the item names and locators of each
# column are the ones the field map declares for the logical field entry that
# supplies it, so a built record reads as a record of a comparison run.
_SELF_TEST_CASE = SUPPORTED_CASES[0]
_SELF_TEST_ISSUED = RELATION_KEYS[0]
_SELF_TEST_RATING = RELATION_KEYS[1]
_SELF_TEST_POLICY_NUMBER = 1
_SELF_TEST_ITEMS = {
    "policy_number": ("CA-POLICY-NUM", "base/src/lgcmarea.cpy:35"),
    "request_id": ("CA-REQUEST-ID", "base/src/lgcmarea.cpy:10"),
    "issue_date": ("CA-ISSUE-DATE / DB2-ISSUEDATE", "base/src/lgcmarea.cpy:38"),
    "last_changed": ("CA-LASTCHANGED / DB2-LASTCHANGED", "base/src/lgcmarea.cpy:40"),
    "policy_type": ("DB2-POLICYTYPE", "base/src/lgpolicy.cpy:43"),
    "customer_number": ("CA-CUSTOMER-NUM", "base/src/lgcmarea.cpy:12"),
    "brokers_reference": (
        "CA-BROKERSREF / DB2-BROKERSREF",
        "base/src/lgcmarea.cpy:42",
    ),
    "payment_amount": ("CA-PAYMENT / DB2-PAYMENT", "base/src/lgcmarea.cpy:43"),
    "motor_premium_amount": (
        "CA-M-PREMIUM / DB2-M-PREMIUM",
        "base/src/lgcmarea.cpy:73",
    ),
}

# Text a built record carries where a comparison run carries a path it read.
_SELF_TEST_ORIGIN = "built by --self-test"

# Paths the output-confinement cases aim at to exercise a destination standing outside
# every accepted root: the system configuration directory, which no accepted root holds,
# and the password file inside it. The cases validate them and never open them: the
# confinement decision is reached before a directory is created or a byte is written, so
# a refused case creates nothing there and changes nothing there.
_SYSTEM_DIRECTORY = Path("/etc")
_SYSTEM_PASSWORD_FILE = _SYSTEM_DIRECTORY / "passwd"


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
            f"{what} does not carry {fragment!r}: {_shown(text, limit=240)}"
        )


def _assert_raises(
    what: str,
    expected: type[BaseException],
    fragment: str,
    body: Callable[[], Any],
) -> str:
    """Return the message of the ``expected`` diagnostic ``body`` raises.

    A body that returns, that raises another class, or that raises a message
    without ``fragment`` fails the case.
    """
    try:
        body()
    except expected as error:
        message = str(error)
        _assert_in(fragment, message, f"the diagnostic of {what}")
        return message
    except Exception as error:  # any other class is a failure of this case
        raise _SelfTestFailure(
            f"{what} raised {type(error).__name__}: {_first_line(error)}"
        ) from error
    raise _SelfTestFailure(f"{what} was accepted, expected {expected.__name__}")


class _Scratch:
    """One private directory a self-test run writes inside.

    The directory is created below the system temporary directory under
    ``_SCRATCH_PREFIX`` on first use, so two runs in parallel never share a
    name. ``absent`` names a path inside it without creating it, and ``remove``
    deletes it with everything in it and reports that it is gone.
    """

    def __init__(self) -> None:
        self._path: Path | None = None

    @property
    def path(self) -> Path:
        """Return this run's directory, creating it on first use."""
        if self._path is None:
            self._path = Path(tempfile.mkdtemp(prefix=_SCRATCH_PREFIX))
        return self._path

    @property
    def created(self) -> Path | None:
        """Return the directory this run created, or None when it created none."""
        return self._path

    def absent(self, name: str) -> Path:
        """Return the path of ``name`` inside this directory without creating it."""
        return self.path / name

    def remove(self) -> bool:
        """Delete this directory with everything in it and report that it is gone."""
        if self._path is None:
            return True
        shutil.rmtree(self._path, ignore_errors=True)
        return not self._path.exists()


def _captured(body: Callable[[], Any]) -> tuple[str, str]:
    """Return the stdout and the stderr text ``body`` printed."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        body()
    return out.getvalue(), err.getvalue()


def _commarea_witness(raw: str, item: str) -> Witness:
    """Return the returned-COMMAREA authority of ``item`` carrying ``raw``."""
    return Witness(
        source=f"returned COMMAREA ({item})",
        raw=raw,
        family="commarea",
        key=item,
    )


def _capture_authority(raw: str | None, key: str) -> Witness:
    """Return the policy-insert capture authority of ``key`` carrying ``raw``.

    ``raw`` None builds the shape ``_capture_witness`` builds for a capture file
    that omits the key: no value and the absence named.
    """
    return Witness(
        source=f"policy insert capture (capture key {key})",
        raw=raw,
        absent=None if raw is not None else f"the capture file carries no key {key}",
        key=key,
    )


# COMMAREA item each built column is read from, where the returned COMMAREA
# carries a window for it. policy_type has no window: a run derives it from the
# request id.
_SELF_TEST_WINDOWS = {
    "policy_number": "CA-POLICY-NUM",
    "request_id": "CA-REQUEST-ID",
    "issue_date": "CA-ISSUE-DATE",
    "last_changed": "CA-LASTCHANGED",
    "customer_number": "CA-CUSTOMER-NUM",
    "brokers_reference": "CA-BROKERSREF",
}


def _authority_for(column: str, raw: str) -> Witness:
    """Return the authority a comparison run reads ``column`` from, holding ``raw``."""
    if column == "policy_type":
        return Witness(
            source="request routing derivation from CA-REQUEST-ID",
            raw=raw,
            family="derived",
        )
    return _commarea_witness(raw, _SELF_TEST_WINDOWS[column])


def _record(
    kind: str,
    witnesses: tuple[Witness, ...],
    *,
    column: str,
    relation: str = _SELF_TEST_ISSUED,
    notes: tuple[str, ...] = (),
) -> Comparison:
    """Return one uncompared record for ``column``, carrying ``witnesses``."""
    item, locator = _SELF_TEST_ITEMS[column]
    return Comparison(
        relation=relation,
        column=column,
        kind=kind,
        cobol_item=item,
        locator=locator,
        witnesses=witnesses,
        notes=notes,
    )


def _compared(
    kind: str,
    witnesses: tuple[Witness, ...],
    warehouse_value: Any,
    *,
    column: str,
    relation: str = _SELF_TEST_ISSUED,
    nullable: bool = False,
) -> Comparison:
    """Return the record ``_compare_column`` produced for these built inputs."""
    return _compare_column(
        _record(kind, witnesses, column=column, relation=relation),
        warehouse_value,
        nullable=nullable,
    )


def _compared_amount(
    digits: str,
    warehouse: Any,
    *,
    column: str = "payment_amount",
    capture: str = SQL_CAPTURE_KEYS["payment"],
) -> Comparison:
    """Return the amount record compared for ``digits`` against ``warehouse``."""
    return _compared(
        KIND_AMOUNT,
        (_capture_authority(digits, capture),),
        warehouse,
        column=column,
        relation=_SELF_TEST_RATING,
    )


def _policy_number_record(warehouse: Any) -> Comparison:
    """Return the policy_number record compared against ``warehouse``."""
    return _compared(
        KIND_INTEGER,
        (_commarea_witness("0000000001", "CA-POLICY-NUM"),),
        warehouse,
        column="policy_number",
    )


def _missing_record() -> Comparison:
    """Return the customer_number record whose capture authority is absent."""
    return _compared(
        KIND_INTEGER,
        (_capture_authority(None, SQL_CAPTURE_KEYS["customer_number"]),),
        100,
        column="customer_number",
    )


def _built_case(
    comparisons: Sequence[Comparison] = (),
    assertions: Sequence[Assertion] = (),
    statuses: Sequence[int] = (),
) -> CaseResult:
    """Return one case result carrying the records a case built."""
    return CaseResult(
        case=_SELF_TEST_CASE,
        fixture=_SELF_TEST_CASE.lower(),
        policy_type=VERIFIED_ROUTING[_SELF_TEST_CASE],
        request_id=_SELF_TEST_CASE,
        policy_number=_SELF_TEST_POLICY_NUMBER,
        captures_path=_SELF_TEST_ORIGIN,
        commarea_path=_SELF_TEST_ORIGIN,
        sample_source=_SELF_TEST_ORIGIN,
        comparisons=list(comparisons),
        assertions=list(assertions),
        snapshot_path=_SELF_TEST_ORIGIN,
        snapshot_state=_SELF_TEST_ORIGIN,
        statuses=list(statuses),
    )


# Values the snapshot cases build one run's output from: the identity seed and
# the timestamp seed of the default harness run, a second identity seed and a
# second timestamp seed a caller may pass, and the customer number the VSAM key
# of the built case carries in front of the policy number.
_SELF_TEST_SEED_A = 1000001
_SELF_TEST_SEED_B = 999999989
_SELF_TEST_STAMP_A = "2026-08-19-12.00.00.000000"
_SELF_TEST_STAMP_B = "2027-01-02-03.04.05.678901"
_SELF_TEST_CUSTOMER = "0000001001"


def _self_test_field_map() -> FieldMap:
    """Return a field map holding the byte grid this module carries and nothing else.

    Only the layout windows and the record length are filled: the snapshot cases
    read the window of the policy number and of the timestamp and nothing else.
    """
    windows = {
        item: Window(
            item=item,
            pic=pic,
            offset=offset,
            length=length,
            kind="numeric_display" if pic.startswith("9") else "alphanumeric",
            copybook="base/src/lgcmarea.cpy",
            line=0,
        )
        for item, pic, offset, length in VERIFIED_WINDOWS
    }
    return FieldMap(
        path=Path(_SELF_TEST_ORIGIN),
        record_length=COMMAREA_RECORD_LENGTH,
        windows=windows,
        entries={},
        source_system_entry=FieldEntry(
            logical_entry="source_system_key",
            concept=_SELF_TEST_ORIGIN,
            runtime_status=_SELF_TEST_ORIGIN,
            populated_by=None,
            applicable_policy_types=(),
            commarea_item=None,
            commarea_locator=None,
            db2_item=None,
            db2_locator=None,
            evidence=(),
            targets=(),
        ),
        routing=dict(VERIFIED_ROUTING),
        routing_locator="base/src/lgapdb01.cbl:184-207",
        supported_request_ids=tuple(sorted(VERIFIED_ROUTING)),
        return_codes={code: _SELF_TEST_ORIGIN for code in VERIFIED_RETURN_CODES},
        relations={},
        amount_columns=(),
        populated_amounts={},
        null_amounts={},
        declared_tolerance=str(AMOUNT_TOLERANCE),
    )


def _built_run_output(
    field_map: FieldMap,
    policy_number: int,
    last_changed: str,
    *,
    customer_number: str = _SELF_TEST_CUSTOMER,
    capture_last_changed: str | None = None,
) -> tuple[CaseResult, HarnessCase]:
    """Return the result and the harness inputs of one run under these seeds.

    The record carries the policy number and the timestamp in their windows, the
    comparisons carry the authorities a run reads for those two columns and for
    the customer number no seed determines, and the captures carry the VSAM key
    the write of that policy composed. ``capture_last_changed`` gives the policy
    insert capture a timestamp of its own, which is how a capture that disagrees
    with the returned record reaches a snapshot.
    """
    policy_window = field_map.window(POLICY_NUMBER_ITEM)
    padded = str(policy_number).zfill(policy_window.length)
    captured_stamp = last_changed if capture_last_changed is None else (
        capture_last_changed
    )
    record = [" "] * COMMAREA_RECORD_LENGTH
    for item, value in (
        (POLICY_NUMBER_ITEM, padded),
        (LASTCHANGED_ITEM, last_changed),
        ("CA-CUSTOMER-NUM", customer_number),
        ("CA-REQUEST-ID", _SELF_TEST_CASE),
    ):
        window = field_map.window(item)
        record[window.offset - 1 : window.offset - 1 + window.length] = list(value)
    vsam_key = f"{VERIFIED_ROUTING[_SELF_TEST_CASE]}{customer_number}{padded}"
    captures = {
        CASE_KEY: _SELF_TEST_CASE,
        FIXTURE_KEY: _SELF_TEST_CASE.lower(),
        _capture_key_of(POLICY_NUMBER_ITEM): padded,
        _capture_key_of(LASTCHANGED_ITEM): last_changed,
        _capture_key_of("CA-CUSTOMER-NUM"): customer_number,
        VSAM_KEY_KEY: vsam_key,
        VSAM_POLICY_NUM_KEY: padded,
        VSAM_CUSTOMER_NUM_KEY: customer_number,
    }
    echoed = "returned COMMAREA capture"
    result = _built_case(
        comparisons=[
            _record(
                KIND_INTEGER,
                (
                    _commarea_witness(padded, POLICY_NUMBER_ITEM),
                    _capture_witness(
                        captures, _capture_key_of(POLICY_NUMBER_ITEM), echoed
                    ),
                    _capture_authority(
                        str(policy_number), SQL_CAPTURE_KEYS["policy_number"]
                    ),
                ),
                column="policy_number",
            ),
            _record(
                KIND_TIMESTAMP,
                (
                    _commarea_witness(last_changed, LASTCHANGED_ITEM),
                    _capture_witness(
                        captures, _capture_key_of(LASTCHANGED_ITEM), echoed
                    ),
                    _capture_authority(
                        captured_stamp, SQL_CAPTURE_KEYS["last_changed"]
                    ),
                ),
                column="last_changed",
            ),
            _record(
                KIND_INTEGER,
                (
                    _commarea_witness(customer_number, "CA-CUSTOMER-NUM"),
                    _capture_witness(
                        captures, _capture_key_of("CA-CUSTOMER-NUM"), echoed
                    ),
                    _capture_authority(
                        customer_number.lstrip("0"),
                        SQL_CAPTURE_KEYS["customer_number"],
                    ),
                ),
                column="customer_number",
            ),
        ],
        assertions=[
            Assertion(
                group=GROUP_VSAM,
                name=name,
                expected=captures[name],
                observed=captures[name],
                locator="base/src/lgapvs01.cbl:99-101",
            )
            for name in (VSAM_KEY_KEY, VSAM_POLICY_NUM_KEY, VSAM_CUSTOMER_NUM_KEY)
        ],
    )
    result.policy_number = policy_number
    harness = HarnessCase(
        case=_SELF_TEST_CASE,
        fixture=_SELF_TEST_CASE.lower(),
        captures=captures,
        captures_path=Path(_SELF_TEST_ORIGIN),
        commarea="".join(record),
        commarea_path=Path(_SELF_TEST_ORIGIN),
        sample=None,
        sample_path=None,
        sample_source=_SELF_TEST_ORIGIN,
    )
    return result, harness


def _built_report(
    cases: Sequence[CaseResult] = (),
    *,
    statuses: Sequence[int] = (),
    local_substitute: bool = True,
    freshness: Mapping[str, Any] | None = None,
) -> RunReport:
    """Return one run report carrying the cases a self-test case built.

    ``freshness`` replaces the built fresh precondition document, so a case can
    render and document the refusal as a comparison run would record it.
    """
    return RunReport(
        generated_at="1970-01-01T00:00:00Z",
        target=TARGET_DUCKDB if local_substitute else TARGET_REDSHIFT,
        adapter=_SELF_TEST_ORIGIN,
        adapter_version="0",
        python_version=".".join(str(number) for number in sys.version_info[:3]),
        connection=f"{_SELF_TEST_ORIGIN} (no connection opened)",
        source_system_key=DEFAULT_SOURCE_SYSTEM_KEY,
        field_map=_SELF_TEST_ORIGIN,
        run_dir=_SELF_TEST_ORIGIN,
        expected_dir=_SELF_TEST_ORIGIN,
        requested_cases=(_SELF_TEST_CASE,),
        local_substitute=local_substitute,
        inventory={
            "verdict": _SELF_TEST_ORIGIN,
            "columns": {
                ISSUED_POLICY_ALIAS: list(ISSUED_POLICY_COLUMNS),
                PREISSUED_RATING_ALIAS: list(PREISSUED_RATING_COLUMNS),
            },
        },
        transform_freshness=(
            dict(freshness) if freshness is not None else _built_freshness()
        ),
        return_codes={code: _SELF_TEST_ORIGIN for code in VERIFIED_RETURN_CODES},
        cases=list(cases),
        statuses=list(statuses),
    )


def _run_results_node(
    unique_id: str, status: Any, message: str | None = None
) -> dict[str, Any]:
    """Return one result entry of a dbt run artifact, as dbt-core writes it."""
    return {
        "unique_id": unique_id,
        "status": status,
        "message": message,
        "failures": None,
        "execution_time": 0.0,
        "adapter_response": {},
        "timing": [],
        "thread_id": "Thread-1",
    }


def _run_results_document(
    results: Sequence[Any], *, command: str = "run", target: str = "local_substitute"
) -> dict[str, Any]:
    """Return one dbt run artifact carrying ``results``, in the v6 artifact shape."""
    return {
        "metadata": {
            "dbt_schema_version": "https://schemas.getdbt.com/dbt/run-results/v6.json",
            "dbt_version": "1.12.2",
            "generated_at": "1970-01-01T00:00:00.000000Z",
            "invocation_id": "00000000-0000-4000-8000-000000000000",
            "env": {},
        },
        "results": list(results),
        "elapsed_time": 0.0,
        "args": {"which": command, "target": target},
    }


def _written_artifact(scratch: _Scratch, name: str, content: Any) -> Path:
    """Write ``content`` as ``name`` inside the private directory and return its path.

    A mapping or sequence is written as JSON and text is written as it stands, so
    one helper builds both a well-formed artifact and a malformed one. Nothing is
    written outside the private directory.
    """
    path = scratch.absent(name)
    text = (
        content
        if isinstance(content, str)
        else json.dumps(content, indent=2, sort_keys=True) + "\n"
    )
    path.write_text(text, encoding="utf-8")
    return path


def _built_freshness(
    scratch: _Scratch | None = None, *, refused: bool = False
) -> dict[str, Any]:
    """Return one freshness document, read from an artifact or built in memory.

    Without ``scratch`` the document is built directly, so a case that only renders
    a report writes no file. With ``scratch`` the artifact is written inside the
    private directory and read back through ``read_transform_freshness``, so the
    document is the one a comparison run would carry.
    """
    if scratch is not None:
        return read_transform_freshness(
            _written_artifact(
                scratch,
                "run_results_refused.json" if refused else "run_results_fresh.json",
                _run_results_document(
                    [
                        _run_results_node(
                            "model.genapp_rqi.int_policy_issue_decoded",
                            "error" if refused else "success",
                            (
                                'Conversion Error: Could not convert string "ABCDEF" '
                                "to DECIMAL(8,2)"
                                if refused
                                else None
                            ),
                        ),
                        _run_results_node(
                            "model.genapp_rqi.canonical_preissued_rating",
                            "skipped" if refused else "success",
                        ),
                    ]
                ),
            )
        )
    document: dict[str, Any] = {
        "path": _SELF_TEST_ORIGIN,
        "verdict": FRESHNESS_REFUSED if refused else FRESHNESS_FRESH,
        "refusals": (
            [f"the node built by --self-test recorded the status {_shown('error')}"]
            if refused
            else []
        ),
        "accepted_statuses": list(DBT_STATUSES_ACCEPTED),
        "warned_statuses": list(DBT_STATUSES_WARNED),
        "refused_statuses": list(DBT_STATUSES_REFUSED),
        "invocation": {
            "schema_version": _SELF_TEST_ORIGIN,
            "dbt_version": "1.12.2",
            "invocation_id": "00000000-0000-4000-8000-000000000000",
            "generated_at": "1970-01-01T00:00:00.000000Z",
            "command": "run",
            "dbt_target": "local_substitute",
            "elapsed_time": "0.0",
        },
        "nodes": {
            "total": 1,
            "accepted": 0 if refused else 1,
            "warned": 0,
            "refused": 1 if refused else 0,
        },
        "warned_nodes": [],
        "refused_nodes": (
            [
                {
                    "unique_id": "model.genapp_rqi.int_policy_issue_decoded",
                    "status": "error",
                    "message": None,
                }
            ]
            if refused
            else []
        ),
    }
    document["note"] = _freshness_note(document)
    return document


def _failed_assertion() -> Assertion:
    """Return one failed VSAM assertion, as a short write would produce it."""
    return Assertion(
        group=GROUP_VSAM,
        name="record length",
        expected=str(VSAM_RECORD_LENGTH),
        observed="63",
        locator="base/src/lgapvs01.cbl:135-141",
        status=STATUS_FAIL,
        notes=(f"the capture records 63 where the write states {VSAM_RECORD_LENGTH}",),
    )


def _mixed_report() -> RunReport:
    """Return a report of one case carrying every reportable outcome at once.

    The case holds one failed column, one non-zero in-tolerance amount delta, one
    warehouse amount of another scale and one failed assertion, so the report
    renders every section a failing run reaches.
    """
    return _built_report(
        [
            _built_case(
                [
                    _policy_number_record(2),
                    _compared_amount("000480", Decimal("480.01")),
                    _compared_amount(
                        "000360",
                        Decimal("360.000"),
                        column="motor_premium_amount",
                        capture=SQL_CAPTURE_KEYS["motor_premium"],
                    ),
                ],
                [_failed_assertion()],
            )
        ]
    )


def _self_test_settings(scratch: _Scratch, *, quiet: bool = False) -> Settings:
    """Return settings whose every path lies inside the private directory."""
    return Settings(
        cases=(_SELF_TEST_CASE,),
        run_dir=scratch.absent("run"),
        captures=None,
        commarea=None,
        sample=None,
        field_map=scratch.absent("copybook_field_map.yml"),
        target=TARGET_DUCKDB,
        database=scratch.absent("local.duckdb"),
        source_system_key=DEFAULT_SOURCE_SYSTEM_KEY,
        report=scratch.absent("diff-report.md"),
        json_report=scratch.absent("diff-report.json"),
        expected_dir=scratch.absent("expected"),
        refresh_snapshot=False,
        dbt_run_results=scratch.absent("run_results.json"),
        quiet=quiet,
    )


def _tracked_report_state() -> tuple[tuple[str, int, int] | None, ...]:
    """Return the size and modification time of the two reports of a real run.

    A path that is absent is recorded as None. The write cases read this before
    and after they write, so a write that reached a tracked report is observed.
    """
    states: list[tuple[str, int, int] | None] = []
    for default in (DEFAULT_REPORT, DEFAULT_JSON_REPORT):
        path = _resolved(default)
        try:
            status = path.stat()
        except OSError:
            states.append(None)
            continue
        states.append((str(path), status.st_size, status.st_mtime_ns))
    return tuple(states)


# --------------------------------------------------------------------------
# Self-test: cases
# --------------------------------------------------------------------------
def _case_mismatched_value_fails() -> str:
    """A non-amount value the warehouse carries differently fails its column."""
    failing = _compared(
        KIND_TEXT,
        (_commarea_witness("BRMOT001  ", "CA-BROKERSREF"),),
        "BRMOT002",
        column="brokers_reference",
    )
    _assert_equal(failing.status, STATUS_FAIL, "the status of a mismatched value")
    _assert_equal(failing.passed, False, "the passed flag of a mismatched value")
    _assert_equal(failing.harness_value, "BRMOT001", "the harness value compared")
    _assert_equal(failing.warehouse_value, "BRMOT002", "the warehouse value compared")
    _assert_equal(
        failing.normalisations,
        (NORM_TRAILING_TRIM,),
        "the normalisation named for a fixed-width text window",
    )
    _assert_in(
        "the warehouse carries",
        "; ".join(failing.notes),
        "the note of a mismatched value",
    )
    matching = _compared(
        KIND_TEXT,
        (_commarea_witness("BRMOT001  ", "CA-BROKERSREF"),),
        "BRMOT001",
        column="brokers_reference",
    )
    _assert_equal(
        matching.status, STATUS_PASS, "the status of the same window matching"
    )
    return (
        f"brokers_reference harness [{failing.harness_value}] against warehouse "
        f"[{failing.warehouse_value}] -> {failing.status}; against [BRMOT001] -> "
        f"{matching.status}"
    )


def _case_failed_column_fails_case_and_run() -> str:
    """One failed column carries the case and the run to EXIT_COMPARISON_FAILED."""
    failing = _policy_number_record(2)
    _assert_equal(
        failing.status, STATUS_FAIL, "the status of a policy number that differs"
    )
    case = _built_case([failing])
    _assert_equal(
        case.exit_status,
        EXIT_COMPARISON_FAILED,
        "the status of a case carrying a failed column",
    )
    _assert_equal(case.verdict, "FAIL", "the verdict of that case")
    _assert_equal(len(case.failed), 1, "the failed columns of that case")
    report = _built_report([case])
    _assert_equal(
        report.exit_status,
        EXIT_COMPARISON_FAILED,
        "the status of a run carrying that case",
    )
    _assert_equal(report.verdict, "FAIL", "the verdict of that run")
    _assert_equal(
        report.as_document()["summary"]["failed"],
        1,
        "the failed count of the JSON summary",
    )
    passing = _built_report([_built_case([_policy_number_record(1)])])
    _assert_equal(
        passing.exit_status, EXIT_OK, "the status of a run whose columns all passed"
    )
    _assert_equal(passing.verdict, "PASS", "the verdict of that run")
    return (
        f"harness policy number 1 against warehouse 2 -> {failing.status}, case "
        f"{case.verdict} exit {case.exit_status}, run {report.verdict} exit "
        f"{report.exit_status}; against warehouse 1 -> {passing.verdict} exit "
        f"{passing.exit_status}"
    )


def _case_amount_delta_zero_passes() -> str:
    """A zero amount delta passes and records no in-tolerance anomaly."""
    record = _compared_amount("000480", Decimal("480.00"))
    _assert_equal(record.status, STATUS_PASS, "the status of a zero delta")
    _assert_equal(
        record.in_tolerance_anomaly, False, "the in-tolerance flag of a zero delta"
    )
    _assert_equal(record.scale_anomaly, False, "the scale flag of a declared scale")
    _assert_equal(record.delta, "0.00", "the delta recorded for equal amounts")
    _assert_equal(Decimal(record.delta), Decimal(0), "that delta read as a decimal")
    _assert_equal(
        record.harness_value, "480", "the harness amount read from its DISPLAY digits"
    )
    _assert_equal(record.warehouse_value, "480.00", "the warehouse amount read")
    case = _built_case([record])
    _assert_equal(case.exit_status, EXIT_OK, "the status of a case of that record")
    _assert_equal(case.in_tolerance, [], "the in-tolerance list of that case")
    return (
        f"payment_amount harness {record.harness_value} against warehouse "
        f"{record.warehouse_value} -> {record.status}, delta {record.delta}, "
        f"in_tolerance_anomaly {record.in_tolerance_anomaly}, case exit "
        f"{case.exit_status}"
    )


def _case_amount_delta_at_tolerance_passes() -> str:
    """A delta of exactly AMOUNT_TOLERANCE passes, is called out and still exits 0."""
    record = _compared_amount("000480", Decimal("480.01"))
    _assert_equal(
        record.status,
        STATUS_PASS_IN_TOLERANCE,
        "the status of a delta at the tolerance",
    )
    _assert_equal(record.passed, True, "the passed flag of that record")
    _assert_equal(
        record.in_tolerance_anomaly, True, "the in-tolerance flag of that record"
    )
    _assert_equal(
        Decimal(record.delta or ""),
        AMOUNT_TOLERANCE,
        "the delta recorded against AMOUNT_TOLERANCE",
    )
    _assert_in(
        "is not zero and is within the tolerance",
        "; ".join(record.notes),
        "the note of a delta at the tolerance",
    )
    case = _built_case([record])
    report = _built_report([case])
    _assert_equal(
        case.exit_status, EXIT_OK, "the status of a case carrying that delta alone"
    )
    _assert_equal(report.exit_status, EXIT_OK, "the status of the run of that case")
    _assert_equal(report.verdict, "PASS", "the verdict of that run")
    _assert_equal(
        [carried.column for _, carried in report.in_tolerance],
        ["payment_amount"],
        "the columns the run reports as unexpected in tolerance",
    )
    _assert_equal(
        report.as_document()["summary"]["unexpected_in_tolerance"],
        [
            {
                "case": _SELF_TEST_CASE,
                "column": "payment_amount",
                "delta": format(AMOUNT_TOLERANCE, "f"),
            }
        ],
        "the unexpected_in_tolerance summary of that run",
    )
    return (
        f"payment_amount 480 against 480.01 -> {record.status}, delta "
        f"{record.delta} = AMOUNT_TOLERANCE, anomaly recorded, run "
        f"{report.verdict} exit {report.exit_status}"
    )


def _case_amount_delta_above_tolerance_fails() -> str:
    """A delta above AMOUNT_TOLERANCE fails the column and the case."""
    record = _compared_amount("000480", Decimal("480.02"))
    _assert_equal(
        record.status, STATUS_FAIL, "the status of a delta above the tolerance"
    )
    _assert_equal(record.delta, "0.02", "the delta recorded")
    _assert_equal(
        record.in_tolerance_anomaly,
        False,
        "the in-tolerance flag of a delta above the tolerance",
    )
    _assert_in(
        f"is above the tolerance {AMOUNT_TOLERANCE}",
        "; ".join(record.notes),
        "the note of a delta above the tolerance",
    )
    case = _built_case([record])
    _assert_equal(
        case.exit_status,
        EXIT_COMPARISON_FAILED,
        "the status of a case carrying that delta",
    )
    _assert_equal(case.verdict, "FAIL", "the verdict of that case")
    return (
        f"payment_amount 480 against 480.02 -> {record.status}, delta "
        f"{record.delta} above {AMOUNT_TOLERANCE}, case {case.verdict} exit "
        f"{case.exit_status}"
    )


def _case_amount_tolerance_boundary_sweep() -> str:
    """The classification of a delta follows AMOUNT_TOLERANCE on both sides of it."""
    expected = (
        ("480.00", STATUS_PASS, False),
        ("480.005", STATUS_PASS_IN_TOLERANCE, True),
        ("479.995", STATUS_PASS_IN_TOLERANCE, True),
        ("480.01", STATUS_PASS_IN_TOLERANCE, True),
        ("479.99", STATUS_PASS_IN_TOLERANCE, True),
        ("480.0101", STATUS_FAIL, False),
        ("479.9899", STATUS_FAIL, False),
        ("480.02", STATUS_FAIL, False),
        ("4800.00", STATUS_FAIL, False),
    )
    observed: list[str] = []
    for warehouse, status, anomaly in expected:
        record = _compared_amount("000480", Decimal(warehouse))
        _assert_equal(record.status, status, f"the status of warehouse {warehouse}")
        _assert_equal(
            record.in_tolerance_anomaly,
            anomaly,
            f"the in-tolerance flag of warehouse {warehouse}",
        )
        observed.append(f"{warehouse} delta {record.delta} -> {record.status}")
    return f"harness 480 against {len(expected)} warehouse values: " + "; ".join(
        observed
    )


def _case_amount_scale_anomaly_recorded() -> str:
    """A warehouse amount of another scale is recorded as an anomaly and passes."""
    fractional = _compared_amount("000480", Decimal("480.000"))
    _assert_equal(fractional.scale_anomaly, True, "the scale flag of scale 3")
    _assert_equal(
        fractional.status, STATUS_PASS, "the status of a zero delta at scale 3"
    )
    _assert_in(
        f"carries scale 3 where the canonical type declares {AMOUNT_SCALE}",
        "; ".join(fractional.notes),
        "the note of an amount at scale 3",
    )
    integral = _compared_amount("000480", Decimal("480"))
    _assert_equal(integral.scale_anomaly, True, "the scale flag of scale 0")
    _assert_in(
        "carries scale 0", "; ".join(integral.notes), "the note of an amount at scale 0"
    )
    declared = _compared_amount("000480", Decimal("480.00"))
    _assert_equal(
        declared.scale_anomaly, False, f"the scale flag of scale {AMOUNT_SCALE}"
    )
    _assert_in(
        f"warehouse scale {AMOUNT_SCALE}",
        "; ".join(declared.notes),
        "the scale note of an amount at the declared scale",
    )
    report = _built_report([_built_case([fractional])])
    _assert_equal(
        [carried.column for _, carried in report.scale_anomalies],
        ["payment_amount"],
        "the columns the run reports as scale anomalies",
    )
    _assert_equal(
        report.as_document()["summary"]["scale_anomalies"],
        [{"case": _SELF_TEST_CASE, "column": "payment_amount"}],
        "the scale_anomalies summary of that run",
    )
    _assert_equal(
        report.exit_status,
        EXIT_OK,
        "the status of a run whose only anomaly is a scale",
    )
    return (
        f"scale 3 -> anomaly {fractional.scale_anomaly} status {fractional.status}; "
        f"scale 0 -> anomaly {integral.scale_anomaly}; scale {AMOUNT_SCALE} -> "
        f"anomaly {declared.scale_anomaly}; run exit {report.exit_status}"
    )


def _case_absent_authority_reports_missing() -> str:
    """An absent harness authority reports MISSING, which is not a pass."""
    absent = _missing_record()
    _assert_equal(absent.status, STATUS_MISSING, "the status of an absent authority")
    _assert_equal(absent.missing, True, "the missing flag of that record")
    _assert_equal(absent.passed, False, "the passed flag of a MISSING record")
    _assert_in(
        "the capture file carries no key",
        "; ".join(absent.notes),
        "the note of an absent capture key",
    )
    without = _compared(KIND_INTEGER, (), 100, column="customer_number")
    _assert_equal(
        without.status, STATUS_MISSING, "the status of a column with no authority"
    )
    _assert_equal(without.authority, "none", "the authority of that column")
    _assert_in(
        "no harness authority carries this column",
        "; ".join(without.notes),
        "the note of a column with no authority",
    )
    case = _built_case([absent])
    _assert_equal(
        case.exit_status,
        EXIT_HARNESS_INPUT,
        "the status of a case carrying a MISSING column",
    )
    _assert_equal(case.verdict, "FAIL", "the verdict of that case")
    report = _built_report([case])
    _assert_equal(
        report.as_document()["summary"]["missing"],
        1,
        "the missing count of the JSON summary",
    )
    _assert_equal(
        report.exit_status, EXIT_HARNESS_INPUT, "the status of the run of that case"
    )
    return (
        f"absent capture key -> {absent.status} (passed {absent.passed}), no "
        f"authority -> {without.status}, case {case.verdict} exit "
        f"{case.exit_status}, run exit {report.exit_status}"
    )


def _case_null_expectation_both_branches() -> str:
    """A NULL expectation passes on NULL and fails on any value standing in it."""
    kept = _compare_null_expected(
        _record(
            KIND_NULL_EXPECTED, (), column="motor_premium_amount",
            relation=_SELF_TEST_RATING,
        ),
        None,
    )
    _assert_equal(kept.status, STATUS_PASS, "the status of NULL where NULL is expected")
    _assert_equal(kept.harness_value, None, "the harness value of that record")
    _assert_equal(kept.warehouse_value, "NULL", "the warehouse value of that record")
    zero = _compare_null_expected(
        _record(
            KIND_NULL_EXPECTED, (), column="motor_premium_amount",
            relation=_SELF_TEST_RATING,
        ),
        Decimal("0.00"),
    )
    _assert_equal(zero.status, STATUS_FAIL, "the status of a zero standing for NULL")
    _assert_in(
        "zero instead of NULL",
        "; ".join(zero.notes),
        "the note of a zero standing for NULL",
    )
    valued = _compare_null_expected(
        _record(
            KIND_NULL_EXPECTED, (), column="motor_premium_amount",
            relation=_SELF_TEST_RATING,
        ),
        Decimal("125.00"),
    )
    _assert_equal(valued.status, STATUS_FAIL, "the status of a value standing for NULL")
    _assert_in(
        "125.00", "; ".join(valued.notes), "the value named in that diagnostic"
    )
    routed_null = _compared(
        KIND_NULL_EXPECTED, (), None, column="motor_premium_amount",
        relation=_SELF_TEST_RATING,
    )
    routed_value = _compared(
        KIND_NULL_EXPECTED, (), Decimal("125.00"), column="motor_premium_amount",
        relation=_SELF_TEST_RATING,
    )
    _assert_equal(
        routed_null.status,
        STATUS_PASS,
        "the status _compare_column returns for a NULL expectation carrying NULL",
    )
    _assert_equal(
        routed_value.status,
        STATUS_FAIL,
        "the status _compare_column returns for a NULL expectation carrying a value",
    )
    return (
        f"motor_premium_amount NULL -> {kept.status}, 0.00 -> {zero.status} (zero "
        f"instead of NULL), 125.00 -> {valued.status}; routed through "
        f"_compare_column -> {routed_null.status} and {routed_value.status}"
    )


def _case_nullable_blank_window_both_branches() -> str:
    """A blank COMMAREA window lands NULL in a nullable column and nothing else."""
    blank = (_commarea_witness(" " * 10, "CA-BROKERSREF"),)
    landed = _compared(
        KIND_TEXT, blank, None, column="brokers_reference", nullable=True
    )
    _assert_equal(
        landed.status, STATUS_PASS, "the status of a blank window against NULL"
    )
    _assert_equal(landed.harness_value, None, "the harness value of that record")
    _assert_in(
        "blank window lands null",
        ", ".join(landed.normalisations),
        "the normalisations of that record",
    )
    filled = _compared(
        KIND_TEXT, blank, "BRMOT001", column="brokers_reference", nullable=True
    )
    _assert_equal(
        filled.status, STATUS_FAIL, "the status of a blank window against a value"
    )
    _assert_in(
        "holds spaces alone and the warehouse carries",
        "; ".join(filled.notes),
        "the note of a blank window against a value",
    )
    strict = _compared(
        KIND_TEXT, blank, None, column="brokers_reference", nullable=False
    )
    _assert_equal(
        strict.status,
        STATUS_FAIL,
        "the status of NULL against a blank window of a column that is not nullable",
    )
    return (
        f"blank CA-BROKERSREF against NULL -> {landed.status}, against [BRMOT001] "
        f"-> {filled.status}, against NULL in a column that is not nullable -> "
        f"{strict.status}"
    )


def _case_authorities_that_disagree_fail() -> str:
    """Two harness authorities that disagree fail the column and are both named."""
    disagreeing = _compared(
        KIND_INTEGER,
        (
            _commarea_witness("0000000001", "CA-POLICY-NUM"),
            _capture_authority("2", SQL_CAPTURE_KEYS["policy_number"]),
        ),
        1,
        column="policy_number",
    )
    _assert_equal(
        disagreeing.status, STATUS_FAIL, "the status of authorities that disagree"
    )
    _assert_in(
        "the harness authorities disagree",
        "; ".join(disagreeing.notes),
        "the note of authorities that disagree",
    )
    _assert_in(
        "returned COMMAREA",
        disagreeing.harness_value or "",
        "the authorities named in the harness value",
    )
    _assert_in(
        SQL_CAPTURE_KEYS["policy_number"],
        disagreeing.harness_value or "",
        "the capture key named in the harness value",
    )
    agreeing = _compared(
        KIND_INTEGER,
        (
            _commarea_witness("0000000001", "CA-POLICY-NUM"),
            _capture_authority("1", SQL_CAPTURE_KEYS["policy_number"]),
        ),
        1,
        column="policy_number",
    )
    _assert_equal(
        agreeing.status, STATUS_PASS, "the status of authorities that agree"
    )
    _assert_in(
        "; ", agreeing.authority, "the authorities the passing record was read from"
    )
    return (
        f"COMMAREA 1 against capture 2 -> {disagreeing.status} with both values "
        f"named; COMMAREA 1 against capture 1 -> {agreeing.status} over "
        f"{len(agreeing.witnesses)} authorities"
    )


def _case_warehouse_null_fails() -> str:
    """A warehouse NULL fails a column whose harness authority carries a value."""
    strict = _policy_number_record(None)
    _assert_equal(strict.status, STATUS_FAIL, "the status of a NULL policy number")
    _assert_equal(strict.warehouse_value, "NULL", "the warehouse value recorded")
    _assert_in(
        "the warehouse carries NULL where the harness carries",
        "; ".join(strict.notes),
        "the note of a warehouse NULL",
    )
    nullable = _compared(
        KIND_INTEGER,
        (_commarea_witness("0000000001", "CA-POLICY-NUM"),),
        None,
        column="policy_number",
        nullable=True,
    )
    _assert_equal(
        nullable.status,
        STATUS_FAIL,
        "the status of a NULL against digits in a nullable column",
    )
    return (
        f"harness policy number 1 against warehouse NULL -> {strict.status}, and "
        f"-> {nullable.status} with the column declared nullable"
    )


def _case_unreadable_harness_value_fails() -> str:
    """A harness value the normalisation of its kind cannot read fails the column."""
    digits = _compared(
        KIND_INTEGER,
        (_commarea_witness("00000000A1", "CA-POLICY-NUM"),),
        1,
        column="policy_number",
    )
    _assert_equal(digits.status, STATUS_FAIL, "the status of a non-numeric window")
    _assert_in(
        "does not hold decimal digits alone",
        "; ".join(digits.notes),
        "the note of a non-numeric window",
    )
    date = _compared(
        KIND_DATE,
        (_commarea_witness("2026-13-01", "CA-ISSUE-DATE"),),
        datetime.date(2026, 1, 1),
        column="issue_date",
    )
    _assert_equal(date.status, STATUS_FAIL, "the status of a month outside 1..12")
    _assert_in(
        "is not a calendar date",
        "; ".join(date.notes),
        "the note of a month outside 1..12",
    )
    moment = _compared(
        KIND_TIMESTAMP,
        (_commarea_witness("2026-08-19 11:22", "CA-LASTCHANGED"),),
        datetime.datetime(2026, 8, 19, 11, 22, 0),  # noqa: DTZ001
        column="last_changed",
    )
    _assert_equal(moment.status, STATUS_FAIL, "the status of a truncated timestamp")
    _assert_in(
        "matches none of the accepted timestamp forms",
        "; ".join(moment.notes),
        "the note of a truncated timestamp",
    )
    return (
        f"[00000000A1] -> {digits.status}, [2026-13-01] -> {date.status}, "
        f"[2026-08-19 11:22] -> {moment.status}"
    )


def _case_unreadable_warehouse_value_fails() -> str:
    """A warehouse value the comparable form of its kind cannot read fails."""
    text = _policy_number_record("1x")
    _assert_equal(text.status, STATUS_FAIL, "the status of a non-numeric warehouse id")
    _assert_in(
        "the warehouse value is not comparable",
        "; ".join(text.notes),
        "the note of a non-numeric warehouse id",
    )
    fractional = _policy_number_record(Decimal("1.5"))
    _assert_equal(
        fractional.status, STATUS_FAIL, "the status of a fractional warehouse id"
    )
    _assert_in(
        "is not a whole number",
        "; ".join(fractional.notes),
        "the note of a fractional warehouse id",
    )
    amount = _compared_amount("000480", "four hundred and eighty")
    _assert_equal(amount.status, STATUS_FAIL, "the status of a non-numeric amount")
    _assert_in(
        "the warehouse value is not comparable",
        "; ".join(amount.notes),
        "the note of a non-numeric amount",
    )
    return (
        f"warehouse [1x] -> {text.status}, warehouse 1.5 -> {fractional.status}, "
        f"warehouse [four hundred and eighty] -> {amount.status}"
    )


def _case_normalisations_compare_equal() -> str:
    """Every declared normalisation compares equal values equal and nothing else."""
    checks = (
        (KIND_TEXT, "request_id", "01AMOT    ", "01AMOT", NORM_TRAILING_TRIM),
        (KIND_CHAR, "policy_type", " M ", "M", NORM_TRAILING_TRIM),
        (KIND_INTEGER, "policy_number", "0000000001", 1, NORM_INTEGER),
        (
            KIND_DATE,
            "issue_date",
            "2026-08-19",
            datetime.date(2026, 8, 19),
            NORM_ISO_DATE,
        ),
        (
            KIND_TIMESTAMP,
            "last_changed",
            "2026-08-19-11.22.33.123456",
            datetime.datetime(2026, 8, 19, 11, 22, 33, 123456),  # noqa: DTZ001
            NORM_TIMESTAMP,
        ),
        (
            KIND_TIMESTAMP,
            "last_changed",
            "2026-08-19T11:22:33.123456",
            datetime.datetime(2026, 8, 19, 11, 22, 33, 123456),  # noqa: DTZ001
            NORM_TIMESTAMP,
        ),
        (
            KIND_TIMESTAMP,
            "last_changed",
            "2026-08-19 11:22:33.123456",
            datetime.datetime(2026, 8, 19, 11, 22, 33, 123456),  # noqa: DTZ001
            NORM_TIMESTAMP,
        ),
    )
    observed: list[str] = []
    for kind, column, raw, warehouse, normalisation in checks:
        record = _compared(
            kind, (_authority_for(column, raw),), warehouse, column=column,
        )
        _assert_equal(record.status, STATUS_PASS, f"the status of {kind} {raw!r}")
        _assert_in(
            normalisation,
            ", ".join(record.normalisations),
            f"the normalisation named for {kind}",
        )
        observed.append(f"{kind} {raw.strip()} -> {record.status}")
    apart = _compared(
        KIND_TIMESTAMP,
        (_commarea_witness("2026-08-19-11.22.33.123456", "CA-LASTCHANGED"),),
        datetime.datetime(2026, 8, 19, 11, 22, 33, 123457),  # noqa: DTZ001
        column="last_changed",
    )
    _assert_equal(
        apart.status,
        STATUS_FAIL,
        "the status of two moments one microsecond apart",
    )
    return (
        f"{len(checks)} equal values compared: " + "; ".join(observed) +
        f"; one microsecond apart -> {apart.status}"
    )


def _case_failed_assertion_fails_case() -> str:
    """An assertion outside the columns carries the case to its own status."""
    passing_column = _policy_number_record(1)
    failed = _built_case([passing_column], [_failed_assertion()])
    _assert_equal(
        failed.exit_status,
        EXIT_COMPARISON_FAILED,
        "the status of a case whose columns passed and whose assertion failed",
    )
    _assert_equal(failed.verdict, "FAIL", "the verdict of that case")
    _assert_equal(len(failed.failed_assertions), 1, "the failed assertions counted")
    missing_assertion = Assertion(
        group=GROUP_CHAIN,
        name="policy insert capture",
        expected="present",
        observed="absent",
        locator="base/src/lgapdb01.cbl:261-321",
        status=STATUS_MISSING,
        notes=(f"the capture file carries no key {POLICY_PRESENT_KEY}",),
    )
    absent = _built_case([passing_column], [missing_assertion])
    _assert_equal(
        absent.exit_status,
        EXIT_HARNESS_INPUT,
        "the status of a case carrying a MISSING assertion",
    )
    passing_assertion = Assertion(
        group=GROUP_IDENTITY,
        name="policy_number across both relations",
        expected="equal",
        observed="equal",
        locator="base/src/lgapdb01.cbl:307-321",
    )
    clean = _built_case([passing_column], [passing_assertion])
    _assert_equal(
        clean.exit_status, EXIT_OK, "the status of a case whose assertions passed"
    )
    return (
        f"failed assertion -> case exit {failed.exit_status}, MISSING assertion -> "
        f"case exit {absent.exit_status}, passing assertion -> case exit "
        f"{clean.exit_status}"
    )


def _case_case_status_precedence() -> str:
    """A case reports the status standing first in the declared precedence."""
    both = _built_case([_missing_record(), _policy_number_record(2)])
    _assert_equal(
        both.exit_status,
        EXIT_HARNESS_INPUT,
        "the status of a case carrying a MISSING and a failed column",
    )
    refused = _built_case(
        [_policy_number_record(2)], statuses=[EXIT_WAREHOUSE_REFUSED]
    )
    _assert_equal(
        refused.exit_status,
        EXIT_WAREHOUSE_REFUSED,
        "the status of a case whose warehouse content was refused",
    )
    configured = _built_case(
        [], statuses=[EXIT_COMPARISON_FAILED, EXIT_CONFIGURATION]
    )
    _assert_equal(
        configured.exit_status,
        EXIT_CONFIGURATION,
        "the status of a case carrying a configuration failure",
    )
    empty = _built_case([])
    _assert_equal(
        empty.exit_status, EXIT_OK, "the status of a case carrying no record at all"
    )
    return (
        f"MISSING with FAIL -> {both.exit_status}, refused warehouse -> "
        f"{refused.exit_status}, configuration -> {configured.exit_status}, no "
        f"record -> {empty.exit_status}"
    )


def _case_run_report_statuses() -> str:
    """The run reports the status of its cases and of the failures it recorded."""
    empty = _built_report([])
    _assert_equal(
        empty.exit_status,
        EXIT_HARNESS_INPUT,
        "the status of a run that compared no case",
    )
    _assert_equal(empty.verdict, "FAIL", "the verdict of that run")
    refused = _built_report([_built_case([])], statuses=[EXIT_WAREHOUSE_REFUSED])
    _assert_equal(
        refused.exit_status,
        EXIT_WAREHOUSE_REFUSED,
        "the status of a run whose warehouse content was refused",
    )
    mixed = _built_report(
        [_built_case([_policy_number_record(2)]), _built_case([_missing_record()])]
    )
    _assert_equal(
        mixed.exit_status,
        EXIT_HARNESS_INPUT,
        "the status of a run carrying a failed case and a missing input",
    )
    _assert_equal(mixed.verdict, "FAIL", "the verdict of that run")
    passing = _built_report([_built_case([_policy_number_record(1)])])
    _assert_equal(
        passing.exit_status, EXIT_OK, "the status of a run whose cases all passed"
    )
    _assert_equal(
        passing.status_label,
        STATUS_LABEL_TEXT,
        "the disposition of a local-substitute run",
    )
    return (
        f"no case -> {empty.exit_status}, refused warehouse -> "
        f"{refused.exit_status}, failed and missing -> {mixed.exit_status}, all "
        f"passing -> {passing.exit_status} carrying the disposition "
        f"[{passing.status_label}]"
    )


def _case_exit_precedence_ordering() -> str:
    """_worst_status returns the status standing first in _EXIT_PRECEDENCE."""
    pairs = 0
    for index, first in enumerate(_EXIT_PRECEDENCE):
        for second in _EXIT_PRECEDENCE[index + 1:]:
            _assert_equal(
                _worst_status([first, second]),
                first,
                f"the worst status of {first} then {second}",
            )
            _assert_equal(
                _worst_status([second, first]),
                first,
                f"the worst status of {second} then {first}",
            )
            pairs += 1
    _assert_equal(
        _worst_status(_EXIT_PRECEDENCE),
        _EXIT_PRECEDENCE[0],
        "the worst status of every declared status",
    )
    _assert_equal(_worst_status([]), EXIT_OK, "the worst status of no status at all")
    _assert_equal(
        _worst_status([EXIT_OK]), EXIT_OK, "the worst status of a passing run alone"
    )
    _assert_equal(
        sorted(_EXIT_PRECEDENCE),
        [
            EXIT_OK,
            EXIT_COMPARISON_FAILED,
            EXIT_HARNESS_INPUT,
            EXIT_WAREHOUSE_REFUSED,
            EXIT_CONFIGURATION,
        ],
        "the statuses _EXIT_PRECEDENCE orders",
    )
    return (
        f"{pairs} ordered pairs in both argument orders each resolve to the status "
        f"standing first, the whole set resolves to {_EXIT_PRECEDENCE[0]}, and no "
        f"status at all resolves to {EXIT_OK}"
    )


def _case_markdown_reports_failure() -> str:
    """The Markdown report of a failing run states FAIL and keeps its disposition."""
    text = render_markdown(_mixed_report())
    _assert_in(
        f"**Overall verdict: FAIL** (exit status {EXIT_COMPARISON_FAILED})",
        text,
        "the verdict line of the Markdown report",
    )
    _assert_in(f"| {_SELF_TEST_CASE} | FAIL |", text, "the verdict row of the case")
    _assert_in(STATUS_LABEL_TEXT, text, "the disposition of the Markdown report")
    _assert_in(AWS_OPEN_TEXT, text, "the AWS statement of the Markdown report")
    _assert_in(STATUS_FAIL, text, "the status of the failed column")
    _assert_in(
        "## Amount deltas inside the tolerance",
        text,
        "the in-tolerance section of the report",
    )
    _assert_in(
        "carries scale 3", text, "the scale anomaly recorded in the report"
    )
    passing = render_markdown(_built_report([_built_case([_policy_number_record(1)])]))
    _assert_in(
        f"**Overall verdict: PASS** (exit status {EXIT_OK})",
        passing,
        "the verdict line of a passing report",
    )
    _assert_in(
        "unexpected_in_tolerance: none",
        passing,
        "the in-tolerance line of a passing report",
    )
    _assert_in(
        STATUS_LABEL_TEXT, passing, "the disposition of the passing report"
    )
    return (
        f"failing run renders [Overall verdict: FAIL] exit {EXIT_COMPARISON_FAILED} "
        f"with the case row FAIL, the in-tolerance and scale sections and the "
        f"disposition; passing run renders [Overall verdict: PASS] exit {EXIT_OK}"
    )


def _case_json_document_reports_failure() -> str:
    """The JSON document of a failing run carries FAIL and every counted outcome."""
    document = _mixed_report().as_document()
    _assert_equal(document["verdict"], "FAIL", "the verdict of the JSON document")
    _assert_equal(
        document["exit_status"],
        EXIT_COMPARISON_FAILED,
        "the exit status of the JSON document",
    )
    summary = document["summary"]
    _assert_equal(summary["failed"], 1, "the failed columns counted")
    _assert_equal(summary["failed_assertions"], 1, "the failed assertions counted")
    _assert_equal(summary["missing"], 0, "the missing columns counted")
    _assert_equal(
        summary["unexpected_in_tolerance"],
        [
            {
                "case": _SELF_TEST_CASE,
                "column": "payment_amount",
                "delta": format(AMOUNT_TOLERANCE, "f"),
            }
        ],
        "the unexpected_in_tolerance summary",
    )
    _assert_equal(
        summary["scale_anomalies"],
        [{"case": _SELF_TEST_CASE, "column": "motor_premium_amount"}],
        "the scale_anomalies summary",
    )
    _assert_equal(
        document["status_label"], STATUS_LABEL_TEXT, "the disposition recorded"
    )
    _assert_equal(
        document["aws_diff_requirement"], "OPEN", "the AWS disposition recorded"
    )
    serialised = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=True)
    _assert_in('"verdict": "FAIL"', serialised, "the serialised JSON document")
    return (
        f"failing run documents verdict FAIL exit {document['exit_status']}, "
        f"failed {summary['failed']}, failed_assertions "
        f"{summary['failed_assertions']}, one in-tolerance delta and one scale "
        f"anomaly, serialised in {len(serialised)} characters"
    )


def _case_summary_line_reports_failure(scratch: _Scratch) -> str:
    """The printed summary of a failing run states FAIL and names the column."""
    report = _mixed_report()
    out, err = _captured(
        lambda: print_summary(report, _self_test_settings(scratch))
    )
    _assert_in(f"{_PROGRAM}: FAIL", out, "the verdict line of a failing run")
    _assert_in("1 failed", out, "the failure count on the verdict line")
    _assert_in(STATUS_LABEL_TEXT, out, "the disposition on the verdict line")
    _assert_in(
        f"{STATUS_FAIL} {_SELF_TEST_ISSUED}.policy_number",
        err,
        "the failed column line on stderr",
    )
    _assert_in(
        f"{STATUS_FAIL} {GROUP_VSAM}",
        err,
        "the failed assertion line on stderr",
    )
    quiet_out, quiet_err = _captured(
        lambda: print_summary(report, _self_test_settings(scratch, quiet=True))
    )
    _assert_equal(
        len(quiet_out.strip().splitlines()),
        1,
        "the lines a quiet summary prints to stdout",
    )
    _assert_in(f"{_PROGRAM}: FAIL", quiet_out, "the verdict line of a quiet summary")
    _assert_equal(quiet_err, "", "the stderr of a quiet summary")
    return (
        f"failing run prints [{_PROGRAM}: FAIL ...] with the disposition, names "
        f"{_SELF_TEST_ISSUED}.policy_number and the {GROUP_VSAM} assertion on "
        f"stderr, and prints one line under --quiet"
    )


def _case_reports_written_inside_scratch(scratch: _Scratch) -> str:
    """Both reports of a failing run are written, and only inside the scratch."""
    before = _tracked_report_state()
    settings = _self_test_settings(scratch)
    write_reports(_mixed_report(), settings)
    markdown = settings.report.read_text(encoding="utf-8")
    document = json.loads(settings.json_report.read_text(encoding="utf-8"))
    _assert_in(
        "**Overall verdict: FAIL**", markdown, "the Markdown report written"
    )
    _assert_equal(
        document["exit_status"],
        EXIT_COMPARISON_FAILED,
        "the exit status of the JSON report written",
    )
    _assert_equal(
        settings.report.parent,
        scratch.path,
        "the directory the reports were written in",
    )
    _assert_equal(
        _tracked_report_state(),
        before,
        "the size and modification time of the two default report paths",
    )
    return (
        f"wrote {settings.report.name} ({len(markdown)} characters) and "
        f"{settings.json_report.name} inside the private directory; the two "
        f"default report paths are unchanged"
    )


def _case_protected_trees_refused(scratch: _Scratch) -> str:
    """An output path inside a protected tree is refused and nothing is written."""
    refused: list[str] = []
    for tree in PROTECTED_TREES:
        _assert_raises(
            f"an output path resolving inside {tree}/",
            ConfigurationError,
            "this tool never writes",
            lambda tree=tree: _refuse_protected_path(REPO_ROOT / tree),
        )
        target = REPO_ROOT / tree / "self-test-must-not-appear.txt"
        _assert_raises(
            f"a write inside {tree}/",
            ConfigurationError,
            "this tool never writes",
            lambda target=target: _write_output(target, _SELF_TEST_ORIGIN),
        )
        _assert(not target.exists(), f"the refused write created {target}")
        refused.append(tree)
    accepted = scratch.absent("accepted.txt")
    _write_output(accepted, f"{_SELF_TEST_ORIGIN}\n")
    _assert_equal(
        accepted.read_text(encoding="utf-8"),
        f"{_SELF_TEST_ORIGIN}\n",
        "the text written inside the private directory",
    )
    return (
        f"{len(refused)} protected trees refused as an output path and as a write "
        f"({', '.join(refused)}), each creating nothing; a path inside the private "
        f"directory is written"
    )


def _case_output_roots_accepted() -> str:
    """Every path a documented run writes is accepted, and validating creates nothing.

    The two default report paths and the default snapshot path of every supported case
    are the destinations the Makefile diff stage names, so this case holds the
    confinement policy to the pipeline it must not break. Each one is validated alone,
    which creates no directory and writes no byte, and the recorded state of the two
    default reports is compared either side of the validation.
    """
    before = _tracked_report_state()
    accepted: list[str] = []
    for default in (DEFAULT_REPORT, DEFAULT_JSON_REPORT):
        path = _resolved(default)
        _refuse_protected_path(path)
        accepted.append(default)
    expected_dir = _resolved(DEFAULT_EXPECTED_DIR)
    for case in SUPPORTED_CASES:
        snapshot = snapshot_path_of(case, expected_dir)
        _refuse_protected_path(snapshot)
        accepted.append(str(snapshot.relative_to(REPO_ROOT)))
    _assert_equal(
        _tracked_report_state(),
        before,
        "the size and modification time of the two default report paths",
    )
    return f"{len(accepted)} documented destinations accepted: {', '.join(accepted)}"


def _case_output_modes_private(scratch: _Scratch) -> str:
    """Every report, snapshot and directory this tool writes is private to its owner.

    The whole case runs under a zero umask, which is the setting under which a mode
    taken from the umask would leave the compared identifiers of a report or a snapshot
    world-readable. It measures the file this tool creates, the file it rewrites over a
    wider mode, the directories it creates on the way and a directory that already
    stood, all through ``_write_output`` - the one funnel both reports and every
    capture snapshot pass through.
    """
    nested = scratch.absent("mode-check") / "expected" / "01amot"
    document = nested / "captures.normalized.json"
    previous = os.umask(0o000)
    try:
        _write_output(document, _SELF_TEST_ORIGIN + "\n")
        created_file = stat.S_IMODE(os.stat(document).st_mode)
        created_directories = tuple(
            stat.S_IMODE(os.stat(directory).st_mode)
            for directory in (nested.parent.parent, nested.parent, nested)
        )
        os.chmod(document, 0o644)
        _write_output(document, _SELF_TEST_ORIGIN + " again\n")
        rewritten_file = stat.S_IMODE(os.stat(document).st_mode)
        os.chmod(nested, 0o755)
        beside = nested / "diff-report.md"
        _write_output(beside, _SELF_TEST_ORIGIN + "\n")
        kept_directory = stat.S_IMODE(os.stat(nested).st_mode)
        beside_file = stat.S_IMODE(os.stat(beside).st_mode)
        # A snapshot reaches its mode by the route the comparison takes: written on
        # the first run, and brought to that mode again on a run that confirms the
        # stored document equals its own output. A comparison that fails leaves the
        # snapshot exactly as it stands, mode included.
        field_map = _self_test_field_map()
        snapshot = scratch.absent("mode-check-snapshot") / _SELF_TEST_CASE.lower()
        snapshot = snapshot / SNAPSHOT_NAME
        stored = build_snapshot(
            *_built_run_output(field_map, _SELF_TEST_SEED_A, _SELF_TEST_STAMP_A),
            field_map,
        )
        apply_snapshot(snapshot, stored)
        written_snapshot = stat.S_IMODE(os.stat(snapshot).st_mode)
        os.chmod(snapshot, 0o644)
        matched_state = apply_snapshot(snapshot, stored)
        matched_snapshot = stat.S_IMODE(os.stat(snapshot).st_mode)
        drifted = build_snapshot(
            *_built_run_output(
                field_map,
                _SELF_TEST_SEED_A,
                _SELF_TEST_STAMP_A,
                customer_number="0000009009",
            ),
            field_map,
        )
        os.chmod(snapshot, 0o644)
        try:
            apply_snapshot(snapshot, drifted)
        except HarnessInputError:
            refused_snapshot = stat.S_IMODE(os.stat(snapshot).st_mode)
        else:  # pragma: no cover - the drift is built to differ
            refused_snapshot = -1
    finally:
        os.umask(previous)
    _assert_equal(
        f"{created_file:04o}", f"{FILE_MODE:04o}", "the mode of a created report"
    )
    for index, observed in enumerate(created_directories):
        _assert_equal(
            f"{observed:04o}",
            f"{DIRECTORY_MODE:04o}",
            f"the mode of created output directory {index + 1} of "
            f"{len(created_directories)}",
        )
    _assert_equal(
        f"{rewritten_file:04o}",
        f"{FILE_MODE:04o}",
        "the mode of a report rewritten over a wider mode",
    )
    _assert_equal(
        f"{kept_directory:04o}",
        "0755",
        "the mode of an output directory that already stood",
    )
    _assert_equal(
        f"{beside_file:04o}",
        f"{FILE_MODE:04o}",
        "the mode of a report written into a directory that already stood",
    )
    _assert_equal(
        document.read_text(encoding="utf-8"),
        _SELF_TEST_ORIGIN + " again\n",
        "the text the rewritten report holds",
    )
    _assert_equal(
        f"{written_snapshot:04o}",
        f"{FILE_MODE:04o}",
        "the mode of a written capture snapshot",
    )
    _assert_equal(
        matched_state, SNAPSHOT_STATE_MATCHED, "the state of the matched comparison"
    )
    _assert_equal(
        f"{matched_snapshot:04o}",
        f"{FILE_MODE:04o}",
        "the mode of a matched capture snapshot that stood at a wider mode",
    )
    _assert_equal(
        f"{refused_snapshot:04o}",
        "0644",
        "the mode of a capture snapshot a refused comparison left behind",
    )
    return (
        f"report {created_file:04o} on creation and {rewritten_file:04o} over a "
        f"wider mode, {len(created_directories)} created directories at "
        f"{DIRECTORY_MODE:04o} and an existing one at {kept_directory:04o}, "
        f"snapshot {written_snapshot:04o} when written and {matched_snapshot:04o} "
        f"when matched over a wider mode with {refused_snapshot:04o} left by a "
        f"refused comparison, all under a zero umask"
    )


def _case_output_outside_both_roots_refused(scratch: _Scratch) -> str:
    """An output path outside the repository and the temporary root is refused.

    The path stands in the system configuration directory, which neither accepted root
    holds, and carries a name that does not exist there. It is refused as an output
    path, as a write and through the command line as --json and as --expected-dir; each
    refusal returns EXIT_CONFIGURATION, creates nothing there and leaves the two default
    reports as they stood.
    """
    before = _tracked_report_state()
    name = f"diff-harness-selftest-{os.getpid()}.json"
    target = _SYSTEM_DIRECTORY / name
    _assert_raises(
        "an output path outside the repository and the temporary directory",
        ConfigurationError,
        "outside the temporary directory",
        lambda: _refuse_protected_path(target),
    )
    _assert_raises(
        "a write outside the repository and the temporary directory",
        ConfigurationError,
        "outside the temporary directory",
        lambda: _write_output(target, _SELF_TEST_ORIGIN),
    )
    _assert_raises(
        "the system password file as an output path",
        ConfigurationError,
        "outside the temporary directory",
        lambda: _refuse_protected_path(_SYSTEM_PASSWORD_FILE),
    )
    statuses: list[int] = []
    common = [
        "--target",
        TARGET_DUCKDB,
        "--database",
        str(scratch.absent("unused.duckdb")),
        "--case",
        _SELF_TEST_CASE,
    ]
    out, err = _captured(
        lambda: statuses.append(main([*common, "--json", str(target)]))
    )
    _assert_equal(statuses[-1], EXIT_CONFIGURATION, "the status of --json into /etc")
    _assert_in("outside the temporary directory", err, "the diagnostic of --json")
    _assert_equal(out, "", "the stdout of the refused --json run")
    out, err = _captured(
        lambda: statuses.append(
            main([*common, "--expected-dir", str(_SYSTEM_DIRECTORY)])
        )
    )
    _assert_equal(
        statuses[-1], EXIT_CONFIGURATION, "the status of --expected-dir /etc"
    )
    _assert_in(
        "outside the temporary directory", err, "the diagnostic of --expected-dir"
    )
    _assert_equal(out, "", "the stdout of the refused --expected-dir run")
    _assert(not target.exists(), f"the refused run created {target}")
    snapshot = snapshot_path_of(_SELF_TEST_CASE, _SYSTEM_DIRECTORY)
    _assert(not snapshot.parent.exists(), f"the refused run created {snapshot.parent}")
    _assert_equal(
        _tracked_report_state(),
        before,
        "the size and modification time of the two default report paths",
    )
    return (
        f"an output path, a write, --json and --expected-dir into "
        f"{_SYSTEM_DIRECTORY} each refused with {EXIT_CONFIGURATION}, creating "
        f"nothing there"
    )


def _case_output_inside_the_repository_refused(scratch: _Scratch) -> str:
    """An in-repository output path outside the two output roots is refused.

    Four in-tree paths stand in for the trees this tool does not write: the repository
    root itself, an authored file, the generated harness build tree and the dbt project
    directory. Each is refused for standing outside the output roots and none of them is
    opened. The command line is exercised too, with --report inside base/src, which the
    protected-tree rule refuses by that tree's name.
    """
    refused: list[str] = []
    for relative in (
        ".",
        "modernization/README.md",
        "modernization/harness/build/diff-report.md",
        "modernization/dbt/genapp_rqi/diff-report.json",
    ):
        candidate = _resolved(relative)
        _assert_raises(
            f"an output path at {relative}",
            ConfigurationError,
            "outside every output root",
            lambda candidate=candidate: _refuse_protected_path(candidate),
        )
        refused.append(relative)
    statuses: list[int] = []
    protected = _resolved(f"{PROTECTED_TREES[0]}/src/diff-report.md")
    out, err = _captured(
        lambda: statuses.append(
            main(
                [
                    "--target",
                    TARGET_DUCKDB,
                    "--database",
                    str(scratch.absent("unused.duckdb")),
                    "--case",
                    _SELF_TEST_CASE,
                    "--report",
                    str(protected),
                ]
            )
        )
    )
    _assert_equal(
        statuses[-1], EXIT_CONFIGURATION, f"the status of --report inside {protected}"
    )
    _assert_in(
        f"resolves inside {PROTECTED_TREES[0]}/",
        err,
        "the diagnostic of --report inside the read-only source tree",
    )
    _assert_equal(out, "", "the stdout of that refusal")
    _assert(not protected.exists(), f"the refused run created {protected}")
    return (
        f"{len(refused)} in-repository paths refused ({', '.join(refused)}) and "
        f"--report inside {PROTECTED_TREES[0]}/src refused with "
        f"{EXIT_CONFIGURATION}"
    )


def _case_output_symbolic_links_refused(scratch: _Scratch) -> str:
    """A symbolic-link parent and a symbolic-link output path are both refused.

    The first link stands in the private directory and names the system configuration
    directory, so the path spelled through it canonicalises outside every accepted root
    and is refused by the path it names rather than accepted by the path it spells. The
    second link stands at the output path itself, inside the private directory, and
    names a file there; it is refused as well, and that file keeps the bytes it held.
    """
    parent_link = scratch.absent("link_system")
    parent_link.symlink_to(_SYSTEM_DIRECTORY)
    name = f"diff-harness-selftest-{os.getpid()}.md"
    through_link = parent_link / name
    _assert_raises(
        "an output path spelled through a symbolic-link parent directory",
        ConfigurationError,
        "outside the temporary directory",
        lambda: _write_output(through_link, _SELF_TEST_ORIGIN),
    )
    named = _SYSTEM_DIRECTORY / name
    _assert(not named.exists(), f"the refused write created {named}")
    victim = scratch.absent("victim.md")
    victim.write_text(_SELF_TEST_ORIGIN, encoding="utf-8")
    final_link = scratch.absent("final_link.md")
    final_link.symlink_to(victim)
    _assert_raises(
        "an output path that is itself a symbolic link",
        ConfigurationError,
        "is a symbolic link",
        lambda: _write_output(final_link, "must not be written"),
    )
    _assert_equal(
        victim.read_text(encoding="utf-8"),
        _SELF_TEST_ORIGIN,
        "the text the file a link named still holds",
    )
    return (
        f"a symbolic-link parent naming {_SYSTEM_DIRECTORY} and a symbolic-link "
        f"output path both refused, each writing nothing"
    )


def _case_field_map_loader_refusals(scratch: _Scratch) -> str:
    """The field map loader refuses an alias, the merge key, a repeat and deep nesting.

    Each document is written inside the private directory and loaded through
    ``load_field_map``, so the refusal is the one a command line would return:
    ``ConfigurationError`` carrying EXIT_CONFIGURATION. A document carrying none of the
    four is composed by the same loader to confirm the loader still reads an ordinary
    mapping.
    """
    nesting = (
        "qa_deep: "
        + "{a: " * (MAX_DOCUMENT_DEPTH + 8)
        + "1"
        + "}" * (MAX_DOCUMENT_DEPTH + 8)
        + "\n"
    )
    documents = (
        (
            "alias_of_an_anchor.yml",
            "record:\n  length: 32500\nqa_anchor: &qa {a: 1}\nqa_alias: *qa\n",
            "refers to anchor '*qa'",
        ),
        (
            "merge_key.yml",
            "record:\n  length: 32500\nqa_merged:\n  <<: {a: 1}\n",
            "uses the merge key '<<'",
        ),
        (
            "duplicate_key.yml",
            "record:\n  length: 32500\nrecord:\n  length: 32500\n",
            "is not a YAML document this tool can read",
        ),
        (
            "deep_nesting.yml",
            nesting,
            f"nests deeper than the accepted {MAX_DOCUMENT_DEPTH} levels",
        ),
    )
    refused: list[str] = []
    for name, text, fragment in documents:
        path = scratch.absent(name)
        path.write_text(text, encoding="utf-8")
        _assert_raises(
            f"the field map {name}",
            ConfigurationError,
            fragment,
            lambda path=path: load_field_map(path),
        )
        refused.append(name)
    _assert_raises(
        "the repeated mapping key the loader itself refuses",
        yaml.constructor.ConstructorError,
        "duplicate key",
        lambda: yaml.load(
            "record:\n  length: 32500\nrecord:\n  length: 32500\n",
            Loader=_FieldMapLoader,
        ),
    )
    loaded = yaml.load(
        "record:\n  length: 32500\nlayout:\n  header:\n    items: []\n",
        Loader=_FieldMapLoader,
    )
    _assert_equal(
        loaded,
        {"record": {"length": 32500}, "layout": {"header": {"items": []}}},
        "the document the loader composes when none of the four is present",
    )
    return (
        f"{len(refused)} field map documents refused with {EXIT_CONFIGURATION} "
        f"({', '.join(refused)}); an ordinary mapping is still composed"
    )


def _case_snapshot_symbolises_the_run_seeds() -> str:
    """Every seeded position of a snapshot carries its symbol, and no other does."""
    field_map = _self_test_field_map()
    result, harness = _built_run_output(
        field_map, _SELF_TEST_SEED_A, _SELF_TEST_STAMP_A
    )
    document = build_snapshot(result, harness, field_map)
    padded_symbol = SNAPSHOT_POLICY_NUMBER_PADDED_SYMBOL.format(
        width=field_map.window(POLICY_NUMBER_ITEM).length
    )
    for family, key, expected in (
        ("captures", _capture_key_of(POLICY_NUMBER_ITEM), padded_symbol),
        ("captures", VSAM_POLICY_NUM_KEY, padded_symbol),
        (
            "captures",
            SQL_CAPTURE_KEYS["policy_number"],
            SNAPSHOT_POLICY_NUMBER_SYMBOL,
        ),
        (
            "captures",
            VSAM_KEY_KEY,
            f"{VERIFIED_ROUTING[_SELF_TEST_CASE]}{_SELF_TEST_CUSTOMER}"
            f"{padded_symbol}",
        ),
        (
            "captures",
            SQL_CAPTURE_KEYS["last_changed"],
            SNAPSHOT_LASTCHANGED_SYMBOL,
        ),
        (
            "captures",
            _capture_key_of(LASTCHANGED_ITEM),
            SNAPSHOT_LASTCHANGED_SYMBOL,
        ),
        ("commarea_windows", POLICY_NUMBER_ITEM, padded_symbol),
        ("commarea_windows", LASTCHANGED_ITEM, SNAPSHOT_LASTCHANGED_SYMBOL),
        ("commarea_windows", "CA-CUSTOMER-NUM", _SELF_TEST_CUSTOMER),
        (
            "captures",
            SQL_CAPTURE_KEYS["customer_number"],
            _SELF_TEST_CUSTOMER.lstrip("0"),
        ),
        ("captures", VSAM_CUSTOMER_NUM_KEY, _SELF_TEST_CUSTOMER),
    ):
        _assert_equal(
            document[family].get(key), expected, f"{family}.{key} of the snapshot"
        )
    rendered = json.dumps(document, sort_keys=True)
    for digits in (str(_SELF_TEST_SEED_A), _SELF_TEST_STAMP_A):
        _assert(
            digits not in rendered,
            f"the snapshot still carries the seeded value {digits}",
        )
    return (
        f"5 identity positions and 3 timestamp positions carry their symbol, the "
        f"customer number stands in 3 positions as it was captured, and neither "
        f"seed appears in the {len(rendered)}-character document"
    )


def _case_snapshot_is_seed_independent() -> str:
    """Two runs under different seeds write one document; a drift still differs."""
    field_map = _self_test_field_map()
    first = build_snapshot(
        *_built_run_output(field_map, _SELF_TEST_SEED_A, _SELF_TEST_STAMP_A),
        field_map,
    )
    second = build_snapshot(
        *_built_run_output(field_map, _SELF_TEST_SEED_B, _SELF_TEST_STAMP_B),
        field_map,
    )
    _assert_equal(
        _snapshot_differences(first, second),
        [],
        "the differences between the snapshots of two seeds",
    )
    moved_customer = build_snapshot(
        *_built_run_output(
            field_map,
            _SELF_TEST_SEED_B,
            _SELF_TEST_STAMP_B,
            customer_number="0000009009",
        ),
        field_map,
    )
    differences = _snapshot_differences(first, moved_customer)
    _assert(
        any("CA-CUSTOMER-NUM" in line for line in differences),
        f"a changed customer number was not reported: {differences}",
    )
    _assert(
        any(VSAM_KEY_KEY in line for line in differences),
        f"the VSAM key of a changed customer number was not reported: {differences}",
    )
    offset_capture = build_snapshot(
        *_built_run_output(
            field_map,
            _SELF_TEST_SEED_A,
            _SELF_TEST_STAMP_A,
            capture_last_changed="2026-08-19-12.00.00.000001",
        ),
        field_map,
    )
    timestamp_differences = _snapshot_differences(first, offset_capture)
    _assert(
        any(
            SQL_CAPTURE_KEYS["last_changed"] in line
            for line in timestamp_differences
        ),
        f"a capture timestamp one microsecond off the assigned one was not "
        f"reported: {timestamp_differences}",
    )
    return (
        f"seeds {_SELF_TEST_SEED_A} and {_SELF_TEST_SEED_B} with two timestamps "
        f"write one document; a moved customer number is reported in "
        f"{len(differences)} places and a capture timestamp one microsecond off "
        f"the assigned one in {len(timestamp_differences)}"
    )


def _case_snapshot_compared_written_and_refreshed(scratch: _Scratch) -> str:
    """A snapshot is written once, compared after that, and refreshed on request."""
    field_map = _self_test_field_map()
    path = scratch.absent("expected") / _SELF_TEST_CASE.lower() / SNAPSHOT_NAME
    first = build_snapshot(
        *_built_run_output(field_map, _SELF_TEST_SEED_A, _SELF_TEST_STAMP_A),
        field_map,
    )
    _assert_equal(
        apply_snapshot(path, first), SNAPSHOT_STATE_WRITTEN, "the state of a first run"
    )
    _assert_equal(
        apply_snapshot(path, first),
        SNAPSHOT_STATE_MATCHED,
        "the state of a run over the snapshot it wrote",
    )
    drifted = build_snapshot(
        *_built_run_output(
            field_map,
            _SELF_TEST_SEED_A,
            _SELF_TEST_STAMP_A,
            customer_number="0000009009",
        ),
        field_map,
    )
    _assert_raises(
        "a snapshot the harness output differs from",
        HarnessInputError,
        "differs from the capture snapshot",
        lambda: apply_snapshot(path, drifted),
    )
    _assert_equal(
        json.loads(path.read_text(encoding="utf-8")),
        first,
        "the snapshot a refused comparison left on disk",
    )
    _assert_equal(
        apply_snapshot(path, drifted, refresh=True),
        SNAPSHOT_STATE_REFRESHED,
        "the state of a run given --refresh-snapshot",
    )
    _assert_equal(
        json.loads(path.read_text(encoding="utf-8")),
        drifted,
        "the snapshot a refresh left on disk",
    )
    _assert_equal(
        apply_snapshot(path, drifted),
        SNAPSHOT_STATE_MATCHED,
        "the state of the comparison after that refresh",
    )
    protected = REPO_ROOT / PROTECTED_TREES[0] / _SELF_TEST_CASE.lower() / SNAPSHOT_NAME
    _assert_raises(
        "a refresh of a snapshot inside a protected tree",
        ConfigurationError,
        "this tool never writes",
        lambda: apply_snapshot(protected, drifted, refresh=True),
    )
    _assert(not protected.exists(), f"the refused refresh created {protected}")
    return (
        f"written, matched, a drift refused with the snapshot left as it stood, "
        f"refreshed on request, matched again, and a refresh into "
        f"{PROTECTED_TREES[0]}/ refused"
    )


def _case_self_test_status_reachable() -> str:
    """A failing case returns EXIT_SELF_TEST_FAILED, which no comparison returns."""
    _assert_equal(
        _self_test_status([_SelfTestOutcome("built", True, "observed")]),
        EXIT_OK,
        "the status of a matrix whose cases all passed",
    )
    _assert_equal(
        _self_test_status(
            [
                _SelfTestOutcome("built", True, "observed"),
                _SelfTestOutcome("built", False, "observed"),
            ]
        ),
        EXIT_SELF_TEST_FAILED,
        "the status of a matrix carrying a failing case",
    )
    declared = (
        EXIT_OK,
        EXIT_COMPARISON_FAILED,
        EXIT_HARNESS_INPUT,
        EXIT_WAREHOUSE_REFUSED,
        EXIT_CONFIGURATION,
        EXIT_SELF_TEST_FAILED,
    )
    _assert_equal(len(set(declared)), len(declared), "the distinct statuses declared")
    _assert(
        EXIT_SELF_TEST_FAILED not in _EXIT_PRECEDENCE,
        "EXIT_SELF_TEST_FAILED stands inside _EXIT_PRECEDENCE",
    )
    return (
        f"a passing matrix returns {EXIT_OK} and a matrix carrying one failing "
        f"case returns {EXIT_SELF_TEST_FAILED}, which stands outside the "
        f"{len(_EXIT_PRECEDENCE)} comparison statuses"
    )


def _case_command_line_refusals() -> str:
    """--self-test is refused alongside a run option, and its inventory is complete."""
    namespace = vars(build_parser().parse_args([]))
    _assert_equal(
        sorted(namespace),
        sorted([dest for dest, _ in _RUN_OPTIONS] + ["self_test", "quiet"]),
        "the destinations a parsed command line carries",
    )
    statuses: list[int] = []
    out, err = _captured(
        lambda: statuses.append(main(["--self-test", "--target", TARGET_REDSHIFT]))
    )
    _assert_equal(
        statuses[-1],
        EXIT_CONFIGURATION,
        "the status of --self-test alongside --target",
    )
    _assert_in("--target", err, "the diagnostic of --self-test alongside --target")
    _assert_equal(out, "", "the stdout of that refusal")
    out, err = _captured(lambda: statuses.append(main(["--not-an-option"])))
    _assert_equal(
        statuses[-1], EXIT_CONFIGURATION, "the status of an option this tool has not"
    )
    _assert_in(
        "the command line was refused",
        err,
        "the diagnostic of an option this tool has not",
    )
    _assert_equal(out, "", "the stdout of that refusal")
    return (
        f"--self-test with --target -> {EXIT_CONFIGURATION} naming --target, an "
        f"unknown option -> {EXIT_CONFIGURATION}, and _RUN_OPTIONS names every "
        f"one of the {len(namespace)} destinations a command line carries"
    )


def _case_transform_freshness_accepts_success(scratch: _Scratch) -> str:
    """A dbt run artifact of successful nodes passes the precondition."""
    built = read_transform_freshness(
        _written_artifact(
            scratch,
            "run_results_models.json",
            _run_results_document(
                [
                    _run_results_node(f"model.genapp_rqi.{name}", "success")
                    for name in (
                        "stg_genapp__policy_issue",
                        "int_policy_issue_decoded",
                        "canonical_issued_policy",
                        "canonical_preissued_rating",
                    )
                ]
            ),
        )
    )
    _assert_equal(built["verdict"], FRESHNESS_FRESH, "the verdict of a successful run")
    _assert_equal(built["refusals"], [], "the refusals of a successful run")
    _assert_equal(
        built["nodes"],
        {"total": 4, "accepted": 4, "warned": 0, "refused": 0},
        "the node counts of a successful run",
    )
    _assert(transform_is_fresh(built), "a successful run did not read as fresh")
    _assert_equal(
        built["invocation"]["dbt_version"], "1.12.2", "the dbt version recorded"
    )
    _assert_equal(built["invocation"]["command"], "run", "the subcommand recorded")
    tested = read_transform_freshness(
        _written_artifact(
            scratch,
            "run_results_tests.json",
            _run_results_document(
                [
                    _run_results_node("test.genapp_rqi.not_null_policy_number", "pass"),
                    _run_results_node("test.genapp_rqi.unique_natural_key", "pass"),
                ],
                command="test",
            ),
        )
    )
    _assert_equal(
        tested["verdict"], FRESHNESS_FRESH, "the verdict of a passing test invocation"
    )
    _assert_equal(
        tested["nodes"]["accepted"], 2, "the accepted nodes of a test invocation"
    )
    warned = read_transform_freshness(
        _written_artifact(
            scratch,
            "run_results_warned.json",
            _run_results_document(
                [
                    _run_results_node("model.genapp_rqi.int_policy_issue_decoded",
                                      "success"),
                    _run_results_node(
                        "test.genapp_rqi.warn_severity_check", "warn", "1 row warned"
                    ),
                ],
                command="build",
            ),
        )
    )
    _assert_equal(
        warned["verdict"], FRESHNESS_FRESH, "the verdict of a run carrying a warn"
    )
    _assert_equal(warned["nodes"]["warned"], 1, "the warned nodes counted")
    _assert_equal(
        [node["unique_id"] for node in warned["warned_nodes"]],
        ["test.genapp_rqi.warn_severity_check"],
        "the warned nodes named",
    )
    _assert_in(
        "test.genapp_rqi.warn_severity_check",
        warned["note"],
        "the note of a run carrying a warn",
    )
    _assert(transform_is_fresh(warned), "a warned node refused the precondition")
    markdown = render_markdown(_built_report(freshness=warned))
    _assert_in(
        "Nodes dbt recorded as warned", markdown, "the report of a warned run"
    )
    return (
        f"4 successful models -> {FRESHNESS_FRESH}, 2 passing tests -> "
        f"{FRESHNESS_FRESH}, one warn -> {FRESHNESS_FRESH} named in the note, in "
        f"warned_nodes and in the Markdown report"
    )


def _case_transform_freshness_refuses_failed_transform(scratch: _Scratch) -> str:
    """A dbt run artifact carrying a node that did not succeed refuses the state."""
    failed = read_transform_freshness(
        _written_artifact(
            scratch,
            "run_results_failed_run.json",
            _run_results_document(
                [
                    _run_results_node("model.genapp_rqi.stg_genapp__policy_issue",
                                      "success"),
                    _run_results_node(
                        "model.genapp_rqi.int_policy_issue_decoded",
                        "error",
                        'Conversion Error: Could not convert string "ABCDEF" to '
                        "DECIMAL(8,2)",
                    ),
                    _run_results_node("model.genapp_rqi.canonical_issued_policy",
                                      "skipped"),
                    _run_results_node("model.genapp_rqi.canonical_preissued_rating",
                                      "skipped"),
                ]
            ),
        )
    )
    _assert_equal(failed["verdict"], FRESHNESS_REFUSED, "the verdict of a failed run")
    _assert_equal(
        failed["nodes"],
        {"total": 4, "accepted": 1, "warned": 0, "refused": 3},
        "the node counts of a failed run",
    )
    _assert(not transform_is_fresh(failed), "a failed run read as fresh")
    diagnostic = freshness_diagnostic(failed)
    for fragment in (
        "not established as successful",
        "model.genapp_rqi.int_policy_issue_decoded",
        "error",
        "model.genapp_rqi.canonical_preissued_rating",
        "skipped",
        "ABCDEF",
    ):
        _assert_in(fragment, diagnostic, "the refusal diagnostic of a failed run")
    _assert_equal(
        FRESHNESS_REFUSED_STATUS,
        EXIT_WAREHOUSE_REFUSED,
        "the status a refused precondition returns",
    )
    _assert(
        FRESHNESS_REFUSED_STATUS in _EXIT_PRECEDENCE,
        "the refusal status stands outside _EXIT_PRECEDENCE",
    )
    observed: list[tuple[str, str]] = []
    for status in ("fail", "runtime error", "indeterminate"):
        document = read_transform_freshness(
            _written_artifact(
                scratch,
                f"run_results_{status.replace(' ', '_')}.json",
                _run_results_document(
                    [_run_results_node("test.genapp_rqi.assert_unique_key", status)],
                    command="test",
                ),
            )
        )
        _assert_equal(
            document["verdict"], FRESHNESS_REFUSED, f"the verdict of status {status}"
        )
        _assert_in(
            "test.genapp_rqi.assert_unique_key",
            freshness_diagnostic(document),
            f"the refusal diagnostic of status {status}",
        )
        observed.append((status, document["verdict"]))
    _assert_in(
        "unrecognised",
        freshness_diagnostic(
            read_transform_freshness(scratch.absent("run_results_indeterminate.json"))
        ),
        "the refusal diagnostic of an unrecognised status",
    )
    return (
        f"a failed model with its 2 skipped consumers -> {FRESHNESS_REFUSED} naming "
        f"the node, the status and the message; "
        + ", ".join(f"{status} -> {verdict}" for status, verdict in observed)
        + f"; the refusal returns {FRESHNESS_REFUSED_STATUS}"
    )


def _case_transform_freshness_refuses_unusable_artifact(scratch: _Scratch) -> str:
    """Every unusable dbt run artifact refuses the state and names why."""
    absent = scratch.absent("run_results_absent.json")
    _assert_in(
        "no dbt run artifact stands at",
        read_transform_freshness(absent)["note"],
        "the note of an absent artifact",
    )
    directory = scratch.absent("run_results_directory.json")
    directory.mkdir(exist_ok=True)
    _assert_equal(
        read_transform_freshness(directory)["verdict"],
        FRESHNESS_REFUSED,
        "the verdict of an artifact that is a directory",
    )
    cases: tuple[tuple[str, Any, str], ...] = (
        ("not_json", "this is not JSON at all\n", "is not JSON"),
        ("not_object", [1, 2, 3], "is not a JSON object"),
        ("no_results", {"metadata": {"dbt_version": "1.12.2"}}, "carries no results"),
        (
            "results_not_list",
            {"results": {"unique_id": "model.one", "status": "success"}},
            "is not a list",
        ),
        ("results_empty", {"results": []}, "records no node"),
        ("result_not_object", {"results": ["model.one"]}, "is not an object"),
        (
            "result_without_status",
            {"results": [{"unique_id": "model.genapp_rqi.one"}]},
            "records no status",
        ),
    )
    observed: list[str] = []
    for name, content, fragment in cases:
        document = read_transform_freshness(
            _written_artifact(scratch, f"run_results_{name}.json", content)
        )
        _assert_equal(document["verdict"], FRESHNESS_REFUSED, f"the verdict of {name}")
        _assert_in(fragment, document["note"], f"the note of {name}")
        _assert(
            not transform_is_fresh(document), f"{name} read as a fresh transform"
        )
        observed.append(name)
    return (
        f"an absent artifact, a directory and {len(observed)} malformed artifacts "
        f"({', '.join(observed)}) each refuse the state and name the cause"
    )


def _case_freshness_refusal_reported_in_both_reports(scratch: _Scratch) -> str:
    """A refused precondition reaches both reports, the verdict and the status."""
    before = _tracked_report_state()
    refused = _built_freshness(scratch, refused=True)
    report = _built_report(statuses=[FRESHNESS_REFUSED_STATUS], freshness=refused)
    _assert_equal(
        report.exit_status,
        EXIT_WAREHOUSE_REFUSED,
        "the status of a run whose precondition refused",
    )
    _assert_equal(report.verdict, "FAIL", "the verdict of a refused run")
    settings = _self_test_settings(scratch)
    write_reports(report, settings)
    markdown = settings.report.read_text(encoding="utf-8")
    document = json.loads(settings.json_report.read_text(encoding="utf-8"))
    for fragment in (
        "## Transform freshness precondition",
        "The precondition refused this warehouse state",
        FRESHNESS_REFUSED,
        "model.genapp_rqi.int_policy_issue_decoded",
        STATUS_LABEL_TEXT,
        AWS_OPEN_TEXT,
        "**Overall verdict: FAIL**",
    ):
        _assert_in(fragment, markdown, "the Markdown report of a refused run")
    _assert_equal(
        document["transform_freshness"]["verdict"],
        FRESHNESS_REFUSED,
        "the verdict the JSON report records",
    )
    _assert_equal(
        document["exit_status"],
        EXIT_WAREHOUSE_REFUSED,
        "the status the JSON report records",
    )
    _assert_equal(
        document["aws_diff_requirement"],
        "OPEN",
        "the AWS diff disposition the JSON report records",
    )
    _assert_equal(
        [
            (node["unique_id"], node["status"])
            for node in document["transform_freshness"]["refused_nodes"]
        ],
        [
            ("model.genapp_rqi.int_policy_issue_decoded", "error"),
            ("model.genapp_rqi.canonical_preissued_rating", "skipped"),
        ],
        "the refused nodes the JSON report records",
    )
    _assert_equal(
        _tracked_report_state(),
        before,
        "the size and modification time of the two default report paths",
    )
    unevaluated = render_markdown(_built_report(freshness={}))
    _assert_in(
        "The precondition was not evaluated on this run",
        unevaluated,
        "the section of a report carrying no precondition document",
    )
    return (
        f"a refused precondition renders the section, the refusal, the disposition "
        f"and the OPEN statement, records verdict {FRESHNESS_REFUSED} and status "
        f"{EXIT_WAREHOUSE_REFUSED} in the JSON report, and leaves the two default "
        f"report paths unchanged; an empty document renders as not evaluated"
    )


def _case_scratch_removed(scratch: _Scratch) -> str:
    """The private directory this run worked inside is removed with everything in it."""
    created = scratch.created
    _assert(scratch.remove(), f"the private directory remains: {created}")
    if created is None:
        return "no private directory was created by this run"
    _assert(not created.exists(), f"the private directory remains: {created}")
    return f"removed {created}"


# --------------------------------------------------------------------------
# Self-test: matrix
# --------------------------------------------------------------------------
def _run_case(
    results: list[_SelfTestOutcome],
    stream: Any,
    quiet: bool,
    name: str,
    body: Callable[[], str],
) -> None:
    """Run one case, record its outcome and print its line.

    A case that raises records a failure and the matrix continues with the next
    case. ``_SelfTestFailure`` carries the observation the case made; a
    ``DiffError`` or any of the listed defect classes is reported by class and
    message.
    """
    try:
        detail = body()
    except _SelfTestFailure as failure:
        result = _SelfTestOutcome(name=name, passed=False, detail=str(failure))
    except DiffError as error:
        result = _SelfTestOutcome(
            name=name, passed=False, detail=f"{type(error).__name__}: {error}"
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
    ) as error:
        result = _SelfTestOutcome(
            name=name,
            passed=False,
            detail=f"unexpected {type(error).__name__}: {error}",
        )
    else:
        result = _SelfTestOutcome(name=name, passed=True, detail=detail)
    results.append(result)
    if result.passed and quiet:
        return
    verdict = "PASS" if result.passed else "FAIL"
    print(
        f"self-test {verdict} {result.name} -- "
        f"{_printable(' '.join(result.detail.split()))}",
        file=stream,
    )


def _self_test_status(results: Sequence[_SelfTestOutcome]) -> int:
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
    Every comparison a case makes is made in this process over records the case
    built, so the matrix opens no warehouse, reads no harness output, reads no
    field map and reaches no endpoint. The three documents a case writes are
    written inside one private temporary directory the matrix creates and the
    last case removes, so no path of this repository is written and the reports
    of the last comparison run stand untouched.
    """
    out = sys.stdout if stream is None else stream
    results: list[_SelfTestOutcome] = []
    scratch = _Scratch()
    try:
        _run_case(
            results, out, quiet, "mismatched_value_fails", _case_mismatched_value_fails
        )
        _run_case(
            results, out, quiet, "failed_column_fails_case_and_run",
            _case_failed_column_fails_case_and_run,
        )
        _run_case(
            results, out, quiet, "amount_delta_zero_passes",
            _case_amount_delta_zero_passes,
        )
        _run_case(
            results, out, quiet, "amount_delta_at_tolerance_passes",
            _case_amount_delta_at_tolerance_passes,
        )
        _run_case(
            results, out, quiet, "amount_delta_above_tolerance_fails",
            _case_amount_delta_above_tolerance_fails,
        )
        _run_case(
            results, out, quiet, "amount_tolerance_boundary_sweep",
            _case_amount_tolerance_boundary_sweep,
        )
        _run_case(
            results, out, quiet, "amount_scale_anomaly_recorded",
            _case_amount_scale_anomaly_recorded,
        )
        _run_case(
            results, out, quiet, "absent_authority_reports_missing",
            _case_absent_authority_reports_missing,
        )
        _run_case(
            results, out, quiet, "null_expectation_both_branches",
            _case_null_expectation_both_branches,
        )
        _run_case(
            results, out, quiet, "nullable_blank_window_both_branches",
            _case_nullable_blank_window_both_branches,
        )
        _run_case(
            results, out, quiet, "authorities_that_disagree_fail",
            _case_authorities_that_disagree_fail,
        )
        _run_case(
            results, out, quiet, "warehouse_null_fails", _case_warehouse_null_fails
        )
        _run_case(
            results, out, quiet, "unreadable_harness_value_fails",
            _case_unreadable_harness_value_fails,
        )
        _run_case(
            results, out, quiet, "unreadable_warehouse_value_fails",
            _case_unreadable_warehouse_value_fails,
        )
        _run_case(
            results, out, quiet, "normalisations_compare_equal",
            _case_normalisations_compare_equal,
        )
        _run_case(
            results, out, quiet, "failed_assertion_fails_case",
            _case_failed_assertion_fails_case,
        )
        _run_case(
            results, out, quiet, "case_status_precedence", _case_case_status_precedence
        )
        _run_case(results, out, quiet, "run_report_statuses", _case_run_report_statuses)
        _run_case(
            results, out, quiet, "exit_precedence_ordering",
            _case_exit_precedence_ordering,
        )
        _run_case(
            results, out, quiet, "markdown_reports_failure",
            _case_markdown_reports_failure,
        )
        _run_case(
            results, out, quiet, "json_document_reports_failure",
            _case_json_document_reports_failure,
        )
        _run_case(
            results, out, quiet, "summary_line_reports_failure",
            lambda: _case_summary_line_reports_failure(scratch),
        )
        _run_case(
            results, out, quiet, "reports_written_inside_scratch",
            lambda: _case_reports_written_inside_scratch(scratch),
        )
        _run_case(
            results, out, quiet, "protected_trees_refused",
            lambda: _case_protected_trees_refused(scratch),
        )
        _run_case(
            results, out, quiet, "output_roots_accepted",
            _case_output_roots_accepted,
        )
        _run_case(
            results, out, quiet, "output_modes_private",
            lambda: _case_output_modes_private(scratch),
        )
        _run_case(
            results, out, quiet, "output_outside_both_roots_refused",
            lambda: _case_output_outside_both_roots_refused(scratch),
        )
        _run_case(
            results, out, quiet, "output_inside_the_repository_refused",
            lambda: _case_output_inside_the_repository_refused(scratch),
        )
        _run_case(
            results, out, quiet, "output_symbolic_links_refused",
            lambda: _case_output_symbolic_links_refused(scratch),
        )
        _run_case(
            results, out, quiet, "field_map_loader_refusals",
            lambda: _case_field_map_loader_refusals(scratch),
        )
        _run_case(
            results, out, quiet, "snapshot_symbolises_the_run_seeds",
            _case_snapshot_symbolises_the_run_seeds,
        )
        _run_case(
            results, out, quiet, "snapshot_is_seed_independent",
            _case_snapshot_is_seed_independent,
        )
        _run_case(
            results, out, quiet, "snapshot_compared_written_and_refreshed",
            lambda: _case_snapshot_compared_written_and_refreshed(scratch),
        )
        _run_case(
            results, out, quiet, "transform_freshness_accepts_success",
            lambda: _case_transform_freshness_accepts_success(scratch),
        )
        _run_case(
            results, out, quiet, "transform_freshness_refuses_failed_transform",
            lambda: _case_transform_freshness_refuses_failed_transform(scratch),
        )
        _run_case(
            results, out, quiet, "transform_freshness_refuses_unusable_artifact",
            lambda: _case_transform_freshness_refuses_unusable_artifact(scratch),
        )
        _run_case(
            results, out, quiet, "freshness_refusal_reported_in_both_reports",
            lambda: _case_freshness_refusal_reported_in_both_reports(scratch),
        )
        _run_case(
            results, out, quiet, "self_test_status_reachable",
            _case_self_test_status_reachable,
        )
        _run_case(
            results, out, quiet, "command_line_refusals", _case_command_line_refusals
        )
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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the comparison gate and return the status of the run.

    ``--self-test`` runs the built-in case matrix instead of a comparison and
    returns its own status, opening no warehouse and reading no harness output.
    """
    parser = build_parser()
    try:
        arguments = parser.parse_args(list(argv) if argv is not None else None)
        if arguments.self_test:
            _refuse_self_test_companions(parser, arguments)
            return run_self_test(quiet=bool(arguments.quiet))
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

