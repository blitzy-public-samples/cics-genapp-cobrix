# Makefile - the executable order of the GenApp Policy-Issue cloud-warehouse bridge.
#
# Working directory: the directory holding this file, modernization/. Every recipe path
# is written relative to it and every path a recipe writes stays inside it, which this
# file enforces: each generated path variable below is resolved before any recipe runs
# and a value resolving outside this directory, or an empty value, ends the invocation
# naming the variable. The only paths outside it that a recipe reaches are the five
# authorized source artifacts base/src/lgapol01.cbl, base/src/lgapdb01.cbl,
# base/src/lgapvs01.cbl, base/src/lgcmarea.cpy and base/src/lgpolicy.cpy, all
# read-only, and the repository-root git queries validation/verify_readonly.sh runs.
#
# Targets:
#   verify-env       Measures python3.12, cobc, git, the virtual environment, pip and
#                    every pin of requirements.txt, and writes
#                    validation/artifacts/verify-env.txt. A missing tool, an
#                    interpreter or compiler outside the accepted series, and any
#                    package version other than its pin, each end the run at the first
#                    such finding with the pinned and the measured value named. A tool
#                    version inside the accepted series that differs from its pin is
#                    recorded as a deviation, and HARNESS_STRICT_TOOL_VERSIONS makes a
#                    deviation end the run as well. It installs nothing.
#   gate             Runs the two real-target probes of landing/land_to_s3.py, selects
#                    redshift when both pass and local_substitute otherwise, and writes
#                    the selection and the probe results to
#                    validation/artifacts/gate-selection.json, which land, load, dbt
#                    and diff read. It provisions no bucket, cluster, workgroup,
#                    network or IAM object, starts no local endpoint, and ends the run
#                    only when DBT_TARGET names redshift and a probe did not pass.
#   translate        Writes the two 32,500-character sample records and translates
#                    read-only copies of the three programs, with the two verbatim
#                    copybooks, into harness/build.
#   compile          Compiles the three translated programs and the twelve stubs as
#                    callable modules and harness/driver.cbl as an executable, keeps
#                    the compiler output including warnings in
#                    validation/artifacts/compile-modules.log, and requires every
#                    expected module and the driver.
#   execute          Runs harness/run_harness.sh for the cases CASES_MODE selects:
#                    every row of that script's case table with the default
#                    CASES_MODE=all, and the two success cases 01AMOT and 01ACOM alone
#                    with CASES_MODE=success-only. It then requires the case selection
#                    the harness
#                    reports to be the one asked for, one executed case per label the
#                    harness lists, the executed-case count to match that list, and of
#                    each success case CA_RETURN_CODE 00, the policy and product SQL
#                    captures, an assigned policy number and timestamp in the returned
#                    COMMAREA, a 64-byte VSAM record whose key is the request-type
#                    letter followed by the customer number and the policy number, and
#                    no abend.
#   extract          Decodes the post-chain COMMAREA of each case into one landing
#                    record under harness/build/landing.
#   land             Writes the landing record of the case named by CASE as one S3
#                    object under the landing prefix, at the part number this file
#                    records for that case, through the endpoint the selected run mode
#                    requires.
#   load             Loads the landed object of the case named by CASE, at that same
#                    part number, into raw.genapp_policy_issue:
#                    landing/load_local.py on the local_substitute branch, and the two
#                    warehouse DDL files followed by the rendered statements of
#                    landing/load_redshift.sql on the redshift branch. It is the only
#                    target-specific stage, and it edits no dbt model file.
#   dbt              Cleans the dbt project, then runs and tests it against the
#                    selected target, keeping the output under validation/artifacts.
#   diff             Compares the harness captures of both cases with the two canonical
#                    rows and writes validation/artifacts/diff-report.md and
#                    diff-report.json.
#   verify-readonly  Runs validation/verify_readonly.sh for the stage named by STAGE:
#                    the five source hashes, an empty "git status --porcelain -- base/"
#                    and no tracked modification outside the generated evidence the
#                    script exempts.
#   all              Runs every stage above in the order this file records and stops at
#                    the first failure.
#   local-endpoint   Optional, and outside the order all runs: brings up the
#                    local_substitute S3 API surface land and load address. It accepts
#                    only a loopback http endpoint from S3_ENDPOINT_URL, starts the moto
#                    server of this virtual environment when nothing answers there,
#                    keeping its output in harness/build/logs/moto-<port>.log, and
#                    creates the bucket S3_BUCKET names at that endpoint only when the
#                    endpoint does not already hold it. It addresses no AWS endpoint and
#                    provisions nothing on AWS, and it refuses to run when DBT_TARGET
#                    names redshift.
#
# Variables a caller may override: CASE, CASES, CASES_MODE, SOURCE_SYSTEM_KEY,
# EXTRACT_DATE, STAGE, COBC, DBT_TARGET, DBT_PROFILES_DIR,
# HARNESS_STRICT_TOOL_VERSIONS. DBT_TARGET carries local_substitute, redshift or an
# empty value, and any other value ends the invocation naming it before a recipe runs.
# Connection settings - AWS credentials, AWS_REGION, S3_BUCKET, S3_ENDPOINT_URL, the
# REDSHIFT_* settings and REDSHIFT_IAM_ROLE - are read from the environment alone. No
# credential, bucket, host, role or password value is written into this file, and no
# recipe prints a credential, an endpoint URL, a host, a role or a password. The land
# and load stages do print the bucket name and the region they address on the console.
#
# Every recipe is non-interactive: it reads no input, opens no pager, installs no
# package and provisions no AWS resource.
# Flow context: Figure 5 — Validation Harness Control Flow in docs/architecture.md.
# Rationale for every choice in this file: docs/decision-log.md.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.NOTPARALLEL:
.SUFFIXES:
.DEFAULT_GOAL := all

# Location of this file, the project directory every relative recipe path is written
# against, and the repository root holding the read-only source directory.
# PROJECT_REL is the project directory in the repository-relative form a published
# report names it by.
MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
PROJECT_DIR := $(patsubst %/,%,$(dir $(MAKEFILE_PATH)))
REPO_ROOT := $(patsubst %/,%,$(dir $(PROJECT_DIR)))
PROJECT_REL := $(notdir $(PROJECT_DIR))

ifneq ($(CURDIR),$(PROJECT_DIR))
$(error this Makefile runs with $(PROJECT_DIR) as the working directory; invoke it as "make -C $(PROJECT_DIR) <target>")
endif

# Options every recursive invocation of this file carries.
MAKE_SELF := --no-print-directory -f $(MAKEFILE_PATH)

# Tools. Every Python and dbt invocation goes through the virtual environment of this
# project by explicit path; no recipe names a system interpreter.
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
DBT := $(VENV)/bin/dbt
ABS_PY := $(PROJECT_DIR)/$(PY)
COBC := cobc
COBFLAGS := -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy

# Pinned runtime and package versions verify-env measures against.
PYTHON_PIN := 3.12.3
PYTHON_SERIES := 3.12
COBC_PIN := 3.1.2.0
COBC_SERIES := 3
COBC_MINIMUM := 3.1.2
GIT_PIN := 2.43.0
GIT_SERIES := 2
PIP_PIN := 25.3
APT_PIN_PYTHON := 3.12.3-1ubuntu0.15
APT_PIN_PYTHON_VENV := 3.12.3-1ubuntu0.15
APT_PIN_GNUCOBOL := 3.1.2-5.1ubuntu1
APT_PIN_GIT := 1:2.43.0-1ubuntu7.3

# Remediation lines verify-env prints beside a finding it cannot clear itself.
APT_REMEDIATION := DEBIAN_FRONTEND=noninteractive apt-get update, then DEBIAN_FRONTEND=noninteractive apt-get install --reinstall -y python3.12=$(APT_PIN_PYTHON) python3.12-venv=$(APT_PIN_PYTHON_VENV) gnucobol3=$(APT_PIN_GNUCOBOL) git=$(APT_PIN_GIT); README.md records the whole procedure
VENV_REMEDIATION := python3.12 -m venv --clear $(VENV), then $(PY) -m pip install --upgrade pip==$(PIP_PIN), then $(PY) -m pip install -r requirements.txt; README.md records the whole procedure

# Generated directories, in the relative form the recipes are written in and in the
# absolute form the tools receive as arguments.
BUILD := harness/build
ARTIFACTS := validation/artifacts
EXPECTED := validation/expected
COMPILE_DIR := $(BUILD)/compile
ABS_BUILD := $(PROJECT_DIR)/$(BUILD)
ABS_ARTIFACTS := $(PROJECT_DIR)/$(ARTIFACTS)
ABS_EXPECTED := $(PROJECT_DIR)/$(EXPECTED)

# Containment of one generated path. $(1) names the variable and the value is read
# through that name, so a value carrying a comma is measured whole. The value is
# resolved with $(abspath ...), which resolves a relative value against this working
# directory - $(CURDIR) equals $(PROJECT_DIR) above - and folds away every . and ..
# element. Every resolved word must be $(PROJECT_DIR) itself or stand beneath it; a word
# resolving elsewhere and an empty value each end the invocation before a recipe runs,
# naming the variable, the supplied value, the resolved path and the boundary. These
# variables are internal to this file and carry no documented override.
check_generated_path = $(if $(strip $($(1))),\
    $(if $(filter-out $(PROJECT_DIR) $(PROJECT_DIR)/%,$(abspath $($(1)))),\
        $(error $(1) is set to "$($(1))", which resolves to $(abspath $($(1))) \
outside the project directory $(PROJECT_DIR); every path a recipe of this file \
writes stays inside that directory)),\
    $(error $(1) is set to an empty value, and it names a generated path inside the \
project directory $(PROJECT_DIR)))

# The generated directories, measured now so no recipe can write outside the project.
$(foreach generated_path,BUILD ARTIFACTS EXPECTED COMPILE_DIR ABS_BUILD ABS_ARTIFACTS ABS_EXPECTED,$(call check_generated_path,$(generated_path)))

# Authored inputs the recipes name.
FIELD_MAP := $(PROJECT_DIR)/extraction/copybook_field_map.yml
SAMPLE_INPUT := $(PROJECT_DIR)/extraction/sample_input
STATEMENT_MAP := $(PROJECT_DIR)/harness/statement_map.yml
COPYBOOK_DIR := $(PROJECT_DIR)/harness/copybooks
SOURCE_DIR := $(REPO_ROOT)/base/src
LANDER := $(PROJECT_DIR)/landing/land_to_s3.py
REDSHIFT_TEMPLATE := $(PROJECT_DIR)/landing/load_redshift.sql
DDL_SCHEMAS := $(PROJECT_DIR)/warehouse/ddl/01_schemas.sql
DDL_RAW := $(PROJECT_DIR)/warehouse/ddl/02_raw_genapp_policy_issue.sql
DBT_PROJECT := dbt/genapp_rqi

# Generated files the recipes write and read.
VERSION_REPORT := $(ARTIFACTS)/verify-env.txt
GATE_SELECTION := $(ARTIFACTS)/gate-selection.json
GATE_LOG_S3 := $(ARTIFACTS)/gate-probe-s3.log
GATE_LOG_REDSHIFT := $(ARTIFACTS)/gate-probe-redshift.log
COMPILE_LOG := $(ARTIFACTS)/compile-modules.log
EXECUTE_LOG := $(ARTIFACTS)/execute-harness.log
DBT_CLEAN_LOG := $(ARTIFACTS)/dbt-clean.log
DBT_RUN_LOG := $(ARTIFACTS)/dbt-run.log
DBT_TEST_LOG := $(ARTIFACTS)/dbt-test.log
DIFF_REPORT := $(ABS_ARTIFACTS)/diff-report.md
DIFF_JSON := $(ABS_ARTIFACTS)/diff-report.json
LOCAL_DUCKDB := $(PROJECT_DIR)/validation/local.duckdb

# The generated files and the dbt project directory dbt clean, run and test write under,
# measured by the same containment check as the generated directories above.
$(foreach generated_path,VERSION_REPORT GATE_SELECTION GATE_LOG_S3 GATE_LOG_REDSHIFT COMPILE_LOG EXECUTE_LOG DBT_CLEAN_LOG DBT_RUN_LOG DBT_TEST_LOG DIFF_REPORT DIFF_JSON LOCAL_DUCKDB DBT_PROJECT,$(call check_generated_path,$(generated_path)))

# Run identity. The landing prefix and both canonical relations carry the source-system
# key. The extract date is fixed once per invocation and reaches the landing writer and
# the raw loader alike, which address one object key.
SOURCE_SYSTEM_KEY ?= GENAPP_CLASS_EXEMPLAR
ENTITY := policy_issue
EXTRACT_DATE ?= $(shell date -u +%F)
LOCAL_DUCKDB_PATH := $(LOCAL_DUCKDB)
export SOURCE_SYSTEM_KEY EXTRACT_DATE LOCAL_DUCKDB_PATH

# Cases. CASES is the set translate, execute, extract and diff cover; CASE names the one
# case land and load address. CASES_MODE selects what the execute stage hands
# harness/run_harness.sh: all, every row of that script's case table, or success-only,
# the two success cases alone.
CASES := 01amot 01acom
CASE ?= 01amot
CASES_MODE ?= all
DIFF_CASES := 01AMOT,01ACOM

# Part element of the landed object name, one value per case. One landing key carries
# one object per source system, entity, extract date and part, so each case of a run
# lands as its own object beside the others and the landing prefix can be replayed to
# rebuild every raw row of that extract date. CASE_PART is the part of the case CASE
# names; a CASE with no line here resolves to nothing and land and load end the run
# rather than address another case's object.
CASE_PART_01amot := 0000
CASE_PART_01acom := 0001
CASE_PART := $(CASE_PART_$(CASE))
CASE_PARTS := $(foreach case,$(CASES),$(case)=$(CASE_PART_$(case)))

# Stage label verify-readonly records.
STAGE ?= unspecified

# Compilation inputs: the three translated programs of the build tree and the twelve
# authored stubs.
TRANSLATED_SOURCES := $(BUILD)/src/lgapol01.cbl $(BUILD)/src/lgapdb01.cbl $(BUILD)/src/lgapvs01.cbl
STUB_SOURCES := harness/stubs/cics_abend.cbl harness/stubs/cics_write.cbl \
    harness/stubs/cics_asktime.cbl harness/stubs/cics_formattime.cbl \
    harness/stubs/cics_diag_link.cbl harness/stubs/sql_insert_policy.cbl \
    harness/stubs/sql_insert_motor.cbl harness/stubs/sql_insert_commercial.cbl \
    harness/stubs/sql_insert_endowment.cbl harness/stubs/sql_insert_house.cbl \
    harness/stubs/sql_set_identity.cbl harness/stubs/sql_select_lastchanged.cbl
MODULE_SOURCES := $(TRANSLATED_SOURCES) $(STUB_SOURCES)
MODULE_COUNT := $(words $(MODULE_SOURCES))
COPIED_SOURCES := lgapol01.cbl lgapdb01.cbl lgapvs01.cbl lgcmarea.cpy lgpolicy.cpy

# dbt options taken from the environment. A profiles directory is passed only when the
# caller names one; with none named, dbt reads its own default location. DBT_TARGET
# carries the target the caller asks for by name; the gate records the target the stages
# address.
DBT_PROFILES_DIR ?=
DBT_TARGET ?=
DBT_PROFILES_FLAG := $(if $(strip $(DBT_PROFILES_DIR)),--profiles-dir $(strip $(DBT_PROFILES_DIR)),)

# The target names a caller may ask for, measured before any recipe runs so a value this
# file does not carry ends the invocation of every target rather than resolving to a
# branch nobody asked for. DBT_TARGET_REFUSED collects every word outside the accepted
# set and the word count of a value naming more than one target.
DBT_TARGET_ACCEPTED := local_substitute redshift
DBT_TARGET_NAMED := $(strip $(DBT_TARGET))
DBT_TARGET_REFUSED := $(strip $(filter-out $(DBT_TARGET_ACCEPTED),$(DBT_TARGET_NAMED)) $(filter-out 0 1,$(words $(DBT_TARGET_NAMED))))
ifneq ($(DBT_TARGET_REFUSED),)
$(error DBT_TARGET is set to "$(DBT_TARGET)", and this file accepts one of local_substitute or redshift, or an empty value; the gate records the target every stage addresses, in $(GATE_SELECTION))
endif

# Whether the caller asked for the real target by name, which makes a probe that does
# not pass a gate failure.
REAL_TARGET_REQUESTED := $(if $(filter redshift,$(DBT_TARGET_NAMED)),yes,no)

.PHONY: all verify-env gate translate compile execute extract land load dbt diff verify-readonly local-endpoint

# Reads the target name out of the selection the gate wrote, given the selection path and
# the stage reading it. A file that cannot be read, does not hold JSON, does not hold a
# JSON object, carries no selected_target or carries one that is not a non-empty text
# value each end this program with one line on stderr naming the stage, the path, the
# element that was refused and the remediation. The reason is stripped of control
# characters, so the diagnostic is one line whatever the file holds, and a successful
# read prints the target name alone on stdout.
define SELECTION_READER_PROGRAM
import json
import re
import sys

selection_path, stage_name = sys.argv[1], sys.argv[2]
CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f-\x9f]")


def refuse(reason):
    sys.stderr.write(
        '%s: %s is not a readable target selection: %s; run "make gate" first\n'
        % (stage_name, selection_path, CONTROL_CHARACTERS.sub(" ", reason).strip())
    )
    raise SystemExit(1)


try:
    with open(selection_path, encoding="utf-8") as handle:
        selection = json.load(handle)
except OSError as failure:
    refuse("it cannot be read: %s" % (failure.strerror or type(failure).__name__))
except UnicodeDecodeError:
    refuse("it does not hold UTF-8 text")
except ValueError as failure:
    refuse("it does not hold valid JSON: %s" % failure)
if not isinstance(selection, dict):
    refuse("it does not hold a JSON object")
if "selected_target" not in selection:
    refuse('it carries no "selected_target" key')
selected = selection["selected_target"]
if not isinstance(selected, str):
    refuse('it records a "selected_target" that is not a text value')
if not selected.strip():
    refuse('it records an empty "selected_target"')
if CONTROL_CHARACTERS.search(selected):
    refuse('it records a "selected_target" carrying a control character')
sys.stdout.write("%s\n" % selected)
endef
export SELECTION_READER_PROGRAM

# Reads the target the gate selected. Every caller sets stage_name first, and receives
# the selection in the shell variable "selected".
define read_selection
if [ ! -f '$(GATE_SELECTION)' ]; then
  printf '%s: no target selection at %s; run "make gate" first\n' "$$stage_name" '$(GATE_SELECTION)' >&2
  exit 1
fi
selected="$$($(PY) -c "$$SELECTION_READER_PROGRAM" '$(GATE_SELECTION)' "$$stage_name")"
case "$$selected" in
  local_substitute | redshift) ;;
  *)
    printf '%s: %s records the unsupported target "%s"\n' "$$stage_name" '$(GATE_SELECTION)' "$$selected" >&2
    exit 1
    ;;
esac
printf '%s: target %s, from %s\n' "$$stage_name" "$$selected" '$(GATE_SELECTION)'
endef

# Confirms one exact "key=value" line stands in one capture file.
define require_capture_line
require_capture_line() {
  if ! grep -q -x -F -e "$$2" "$$1"; then
    printf 'execute: %s does not carry %s\n' "$$1" "$$2" >&2
    exit 1
  fi
}
endef

# Confirms every pin of requirements.txt is installed at that exact version in the
# interpreter running this program, and prints one report line per distribution. The
# interpreter is named relative to the repository root of the fourth argument while it
# stands inside that root, and by its absolute path otherwise, so a report of an
# in-checkout interpreter carries the same text in every checkout.
define PIN_CHECK_PROGRAM
import os
import re
import sys
from importlib import metadata

requirements_path, pip_pin, pip_measured = sys.argv[1], sys.argv[2], sys.argv[3]
repository_root = os.path.join(os.path.abspath(sys.argv[4]), "")
interpreter = os.path.abspath(sys.executable)
if interpreter.startswith(repository_root):
    interpreter = os.path.relpath(interpreter, repository_root)
pin_pattern = re.compile(r"([A-Za-z0-9._-]+)(\[[^\]]*\])?==([^\s#]+)")
pins = []
with open(requirements_path, encoding="utf-8") as handle:
    for line in handle:
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        match = pin_pattern.fullmatch(entry)
        if match is None:
            sys.stderr.write(
                "verify-env: FATAL %s carries the entry %r, which is not an exact pin\n"
                % (requirements_path, entry)
            )
            raise SystemExit(1)
        pins.append((match.group(1), match.group(3)))
if not pins:
    sys.stderr.write("verify-env: FATAL %s declares no pin\n" % requirements_path)
    raise SystemExit(1)
lines = [
    "interpreter: %s" % interpreter,
    "interpreter version: %s" % sys.version.split()[0],
    "pip: pinned %s measured %s" % (pip_pin, pip_measured),
]
for name, pinned in pins:
    try:
        measured = metadata.version(name)
    except metadata.PackageNotFoundError:
        sys.stderr.write(
            "verify-env: FATAL %s: pinned %s, not installed in %s\n"
            % (name, pinned, interpreter)
        )
        raise SystemExit(1)
    if measured != pinned:
        sys.stderr.write(
            "verify-env: FATAL %s: pinned %s, measured %s in %s\n"
            % (name, pinned, measured, interpreter)
        )
        raise SystemExit(1)
    lines.append("%s: pinned %s measured %s" % (name, pinned, measured))
lines.append("pins measured: %d" % len(pins))
sys.stdout.write("\n".join(lines) + "\n")
endef
export PIN_CHECK_PROGRAM

# Records the target the precondition gate selected, with the status and the last
# reported line of each probe. It reaches no endpoint of its own.
define GATE_SELECTION_PROGRAM
import json
import os
import sys
from datetime import datetime, timezone

destination, selected = sys.argv[1], sys.argv[2]
probes = {}
for name, status, log in (
    ("s3", sys.argv[3], sys.argv[4]),
    ("redshift", sys.argv[5], sys.argv[6]),
):
    try:
        with open(log, encoding="utf-8", errors="replace") as handle:
            reported = [line.strip() for line in handle if line.strip()]
        last_line = reported[-1] if reported else ""
    except OSError as failure:
        last_line = "probe log unreadable: %s" % (failure.strerror or "unknown error")
    probes[name] = {
        "exit_status": int(status),
        "log": log,
        "last_reported_line": last_line,
        "passed": int(status) == 0,
    }
selection = {
    "selected_target": selected,
    "recorded_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "source_system_key": os.environ.get("SOURCE_SYSTEM_KEY", ""),
    "extract_date": os.environ.get("EXTRACT_DATE", ""),
    "probes": probes,
    "formal_aws_diff": "OPEN",
    "provisioned": [],
}
if selected != "redshift":
    selection["status_label"] = "validated against local substitute, not AWS"
with open(destination, "w", encoding="utf-8") as handle:
    json.dump(selection, handle, indent=2, sort_keys=True)
    handle.write("\n")
sys.stdout.write("%s\n" % destination)
endef
export GATE_SELECTION_PROGRAM

# Loads one landed object into raw.genapp_policy_issue on the real Amazon Redshift
# target: applies the two warehouse DDL files, renders landing/load_redshift.sql through
# the only supported renderer, confirms the authored eleven-statement sequence, and
# sends the statements in that order with the two markers bound from the landed record.
# Any failure sends ROLLBACK and names the statement that did not complete. It prints no
# host, port, user, database, schema, role or password value.
define REDSHIFT_LOAD_PROGRAM
import json
import os
import subprocess
import sys

(
    record_path,
    schemas_ddl,
    raw_ddl,
    interpreter,
    lander,
    template,
    source_system_key,
    entity,
    extract_date,
    part,
) = sys.argv[1:11]

AUTHORED_SEQUENCE = [
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
]
REQUIRED_SETTINGS = (
    "REDSHIFT_HOST",
    "REDSHIFT_USER",
    "REDSHIFT_PASSWORD",
    "REDSHIFT_DATABASE",
    "REDSHIFT_SCHEMA",
)


def refuse(reason):
    sys.stderr.write("load: %s\n" % reason)
    raise SystemExit(4)


def setting(name, default=None):
    value = os.environ.get(name, "")
    if not value.strip():
        if default is None:
            refuse(
                "no %s is set: the redshift branch reads it from the environment, as "
                "the redshift output of %s/profiles.example.yml does" % (name, "dbt/genapp_rqi")
            )
        return default
    return value


def render(document):
    completed = subprocess.run(
        [
            interpreter,
            lander,
            "--render-redshift-load",
            document,
            "--record",
            record_path,
            "--template",
            template,
            "--source-system-key",
            source_system_key,
            "--entity",
            entity,
            "--extract-date",
            extract_date,
            "--part",
            part,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
        refuse(
            "rendering the %s document of %s ended with status %d"
            % (document, template, completed.returncode)
        )
    return completed.stdout


def statements_of(text):
    """Return the statements of one SQL document, whole-line comments removed."""
    body = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("--")
    )
    return [fragment.strip() for fragment in body.split(";") if fragment.strip()]


def keyword(statement):
    """Return the leading keyword of one statement, upper case."""
    return statement.split(None, 1)[0].upper()


def statements_of_file(path):
    with open(path, encoding="utf-8") as handle:
        return statements_of(handle.read())


with open(record_path, encoding="utf-8") as handle:
    record = json.load(handle)
for key in ("source_system_key", "policy_number"):
    if not record.get(key):
        refuse("the landed record %s carries no %s" % (record_path, key))
parameters = {
    "source_system_key": record["source_system_key"],
    "policy_number": record["policy_number"],
}

statements = statements_of(render("sql"))
if len(statements) != len(AUTHORED_SEQUENCE):
    refuse(
        "the rendered load carries %d statements, and the authored sequence carries %d"
        % (len(statements), len(AUTHORED_SEQUENCE))
    )
measured_sequence = [keyword(statement) for statement in statements]
if measured_sequence != AUTHORED_SEQUENCE:
    refuse(
        "the rendered load carries the sequence %s, and the authored sequence is %s"
        % (", ".join(measured_sequence), ", ".join(AUTHORED_SEQUENCE))
    )

settings = {name: setting(name) for name in REQUIRED_SETTINGS}
port_text = setting("REDSHIFT_PORT", "5439")
timeout_text = setting("REDSHIFT_CONNECT_TIMEOUT", "30")
for name, value in (("REDSHIFT_PORT", port_text), ("REDSHIFT_CONNECT_TIMEOUT", timeout_text)):
    if not value.isdigit() or int(value) <= 0:
        refuse("%s must be decimal digits above zero" % name)

import redshift_connector

redshift_connector.paramstyle = "pyformat"
connection = None
cursor = None
sent = 0
try:
    connection = redshift_connector.connect(
        host=settings["REDSHIFT_HOST"],
        database=settings["REDSHIFT_DATABASE"],
        user=settings["REDSHIFT_USER"],
        password=settings["REDSHIFT_PASSWORD"],
        port=int(port_text),
        timeout=int(timeout_text),
    )
    connection.autocommit = True
    cursor = connection.cursor()
    for path in (schemas_ddl, raw_ddl):
        for statement in statements_of_file(path):
            cursor.execute(statement)
        sys.stdout.write("load: applied %s\n" % path)
    for index, statement in enumerate(statements, start=1):
        if "%(" in statement:
            cursor.execute(statement, parameters)
        else:
            cursor.execute(statement)
        sent = index
    sys.stdout.write(
        "load: %d statements sent, raw.genapp_policy_issue carries the landed record\n"
        % sent
    )
except Exception as failure:
    if cursor is not None:
        try:
            cursor.execute("ROLLBACK")
            sys.stderr.write("load: the transaction was rolled back\n")
        except Exception as rollback_failure:
            sys.stderr.write(
                "load: the rollback did not complete: %s\n" % type(rollback_failure).__name__
            )
    sys.stderr.write(
        "load: statement %d of %d did not complete: %s\n"
        % (sent + 1, len(statements), type(failure).__name__)
    )
    raise SystemExit(4)
finally:
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()
endef
export REDSHIFT_LOAD_PROGRAM

# Brings up the local_substitute S3 API surface land and load address, given the
# interpreter the server runs under, the endpoint, the bucket and the directory the
# server log stands in. The endpoint is confirmed to be http on a loopback host with an
# explicit port of 1024 or above before anything is started, and every request this
# program makes carries that endpoint, so no AWS endpoint is addressed and nothing is
# created on AWS. The server is started only when nothing answers there, in a session of
# its own so it outlives this run, and the bucket is created only when the endpoint does
# not already hold it: a second invocation reports both as standing and ends with status
# 0. Credentials come from the environment and the region from AWS_REGION or
# AWS_DEFAULT_REGION; an unresolved one is named, and no credential, secret or token
# value is read beyond confirming one is present or ever printed.
define LOCAL_ENDPOINT_PROGRAM
import os
import re
import socket
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone

interpreter, endpoint, bucket, log_directory = sys.argv[1:5]

ACCEPTED_SCHEME = "http"
ACCEPTED_HOSTS = ("127.0.0.1", "::1", "localhost")
PORT_FLOOR = 1024
MAX_ENDPOINT_CHARACTERS = 256
MIN_BUCKET_CHARACTERS = 3
MAX_BUCKET_CHARACTERS = 63
BUCKET_SHAPE = re.compile(r"\A[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9]\Z")
BUCKET_IPV4_SHAPE = re.compile(r"\A[0-9]{1,3}(\.[0-9]{1,3}){3}\Z")
BUCKET_ADJACENT_DOTS = ".."
BUCKET_RESERVED_PREFIXES = ("xn--", "sthree-", "amzn-s3-demo-")
BUCKET_RESERVED_SUFFIXES = ("-s3alias", "--ol-s3", ".mrap", "--x-s3", "--table-s3")
READY_TIMEOUT_SECONDS = 30.0
READY_POLL_SECONDS = 0.25
CONNECT_TIMEOUT_SECONDS = 1.0
STOP_TIMEOUT_SECONDS = 5.0
REQUEST_CONNECT_TIMEOUT_SECONDS = 5
REQUEST_READ_TIMEOUT_SECONDS = 15
REGION_VARIABLES = ("AWS_REGION", "AWS_DEFAULT_REGION")
CREDENTIAL_VARIABLES = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
LOCAL_CREDENTIAL_METHODS = ("env", "explicit")
GLOBAL_REGION = "us-east-1"
BUCKET_ABSENT_CODES = ("404", "NoSuchBucket", "NotFound")
BUCKET_PRESENT_CODES = ("BucketAlreadyOwnedByYou", "BucketAlreadyExists")
CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f-\x9f]")
ENDPOINT_POLICY = (
    "a local endpoint is %s on a loopback host (%s) with an explicit port of %d or "
    "above, no embedded credentials, no path, no query and no fragment"
    % (ACCEPTED_SCHEME, ", ".join(ACCEPTED_HOSTS), PORT_FLOOR)
)


def report(message):
    """Write one progress line naming what stands, and flush it in order."""
    sys.stdout.write("local-endpoint: %s\n" % message)
    sys.stdout.flush()


def refuse(reason, status=1):
    """Write one control-free line naming what was refused, and end this program."""
    sys.stderr.write(
        "local-endpoint: %s\n" % CONTROL_CHARACTERS.sub(" ", reason).strip()
    )
    raise SystemExit(status)


def refuse_endpoint(fault):
    """Refuse the endpoint naming the element that failed, never the value."""
    refuse(
        "the endpoint from S3_ENDPOINT_URL is not accepted: %s; %s. The value is not "
        "echoed" % (fault, ENDPOINT_POLICY)
    )


def endpoint_address(value):
    """Return the (host, port) an accepted local endpoint names.

    Every element is measured before a server, a client or a credential exists, so a
    value that is not a loopback endpoint reaches nothing at all.
    """
    if len(value) > MAX_ENDPOINT_CHARACTERS:
        refuse_endpoint(
            "it holds %d characters, and at most %d are accepted"
            % (len(value), MAX_ENDPOINT_CHARACTERS)
        )
    if any(character.isspace() for character in value) or CONTROL_CHARACTERS.search(
        value
    ):
        refuse_endpoint("it carries whitespace or a control character")
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        refuse_endpoint("it cannot be parsed as a URL")
    if parsed.scheme != ACCEPTED_SCHEME:
        refuse_endpoint("its scheme is not %s" % ACCEPTED_SCHEME)
    if "@" in parsed.netloc:
        refuse_endpoint("it carries embedded credentials before the host")
    if parsed.path not in ("", "/"):
        refuse_endpoint("it carries a path")
    if parsed.query:
        refuse_endpoint("it carries a query")
    if parsed.fragment:
        refuse_endpoint("it carries a fragment")
    try:
        host, port = parsed.hostname, parsed.port
    except ValueError:
        refuse_endpoint("its port is not a number")
    if not host:
        refuse_endpoint("it names no host")
    if host.casefold() not in ACCEPTED_HOSTS:
        refuse_endpoint("its host is not one of %s" % ", ".join(ACCEPTED_HOSTS))
    if port is None:
        refuse_endpoint("it names no port")
    if port < PORT_FLOOR:
        refuse_endpoint("its port is below %d" % PORT_FLOOR)
    return host, port


def confirm_bucket_name(value):
    """Refuse a bucket name the landing writer and the raw loader could not address.

    The general-purpose bucket naming rules hold whichever endpoint serves the name, so
    a name refused here is a name land and load would refuse as well, and it is refused
    before a server is started or a request is sent.
    """
    if not (MIN_BUCKET_CHARACTERS <= len(value) <= MAX_BUCKET_CHARACTERS):
        refuse(
            "the bucket name from S3_BUCKET holds %d characters: '%s'; between %d and "
            "%d are accepted"
            % (len(value), value, MIN_BUCKET_CHARACTERS, MAX_BUCKET_CHARACTERS)
        )
    if not BUCKET_SHAPE.fullmatch(value):
        refuse(
            "the bucket name from S3_BUCKET is not a general-purpose bucket name: "
            "'%s'; it carries lowercase letters, digits, dot and hyphen only, and "
            "begins and ends with a letter or a digit" % value
        )
    if BUCKET_ADJACENT_DOTS in value:
        refuse(
            "the bucket name from S3_BUCKET carries two adjacent dots: '%s'; a "
            "general-purpose bucket name does not" % value
        )
    if BUCKET_IPV4_SHAPE.fullmatch(value):
        refuse(
            "the bucket name from S3_BUCKET is written as an IPv4 address: '%s'; a "
            "general-purpose bucket name is not" % value
        )
    for prefix in BUCKET_RESERVED_PREFIXES:
        if value.startswith(prefix):
            refuse(
                "the bucket name from S3_BUCKET begins with the reserved prefix '%s': "
                "'%s'" % (prefix, value)
            )
    for suffix in BUCKET_RESERVED_SUFFIXES:
        if value.endswith(suffix):
            refuse(
                "the bucket name from S3_BUCKET ends with the reserved suffix '%s': "
                "'%s'" % (suffix, value)
            )


def answers(host, port):
    """Return whether something accepts a connection on that loopback address."""
    try:
        with socket.create_connection((host, port), CONNECT_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False


def stop(process):
    """End a started server that never answered, and wait for it to go."""
    process.terminate()
    try:
        process.wait(STOP_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(STOP_TIMEOUT_SECONDS)


def start_server(host, port, log_path):
    """Start the moto server of this virtual environment and wait for it to answer.

    The server is started in a session of its own with its input closed and both output
    streams appended to log_path, so it survives the make invocation that started it and
    every diagnostic it writes is kept. A server that ends, or that never answers within
    READY_TIMEOUT_SECONDS, ends this program naming the log.
    """
    command = [interpreter, "-m", "moto.server", "-H", host, "-p", str(port)]
    try:
        os.makedirs(log_directory, exist_ok=True)
        log = open(log_path, "a", encoding="utf-8")
    except OSError as failure:
        refuse(
            "the server log %s cannot be opened: %s"
            % (log_path, failure.strerror or type(failure).__name__)
        )
    try:
        log.write(
            "=== %s starting %s\n"
            % (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), " ".join(command))
        )
        log.flush()
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
            close_fds=True,
        )
    except OSError as failure:
        log.close()
        refuse(
            "the local substitute server cannot be started: %s"
            % (failure.strerror or type(failure).__name__)
        )
    log.close()
    started = time.monotonic()
    deadline = started + READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            refuse(
                "the local substitute server ended with status %d before it answered on "
                "%s:%d; its output stands in %s"
                % (process.returncode, host, port, log_path),
                4,
            )
        if answers(host, port):
            report(
                "the local substitute answers at %s:%d after %.1f seconds, process %d, "
                "output in %s" % (host, port, time.monotonic() - started, process.pid, log_path)
            )
            return
        time.sleep(READY_POLL_SECONDS)
    stop(process)
    refuse(
        "the local substitute server did not answer on %s:%d within %.0f seconds and was "
        "ended; its output stands in %s"
        % (host, port, READY_TIMEOUT_SECONDS, log_path),
        4,
    )


def resolved_region():
    """Return the region the bucket is created in, from the environment alone."""
    for name in REGION_VARIABLES:
        value = os.environ.get(name, "")
        if value.strip():
            if any(character.isspace() for character in value) or CONTROL_CHARACTERS.search(value):
                refuse(
                    "the region from %s carries whitespace or a control character" % name
                )
            return value
    refuse(
        "no region is resolved: set %s in the environment, which names the region the "
        "local endpoint holds the bucket in" % " or ".join(REGION_VARIABLES)
    )


def resolved_credentials(session):
    """Confirm one set of environment credentials the loopback endpoint is signed with.

    The session's own providers do the resolving, so a variable whose name merely begins
    with AWS is never taken for a credential, and the provenance they record is then
    confirmed: only credentials that came from the environment or were passed to the
    session directly are signed against a loopback port, because a credential resolved
    from a profile, single sign-on, an assumed role, container metadata or instance
    metadata belongs to a real account. No value is read beyond confirming one is
    present, and none is printed here or anywhere else.
    """
    try:
        credentials = session.get_credentials()
    except botocore.exceptions.PartialCredentialsError:
        refuse(
            "the resolved credentials are incomplete: set %s together in the "
            "environment; no value is printed" % " and ".join(CREDENTIAL_VARIABLES)
        )
    except botocore.exceptions.NoCredentialsError:
        refuse(
            "no credentials are resolved: set %s in the environment, which the local "
            "substitute accepts as throwaway values; no value is printed"
            % " and ".join(CREDENTIAL_VARIABLES)
        )
    except botocore.exceptions.BotoCoreError as failure:
        refuse("credentials cannot be resolved: %s" % type(failure).__name__)
    if credentials is None or not credentials.access_key:
        refuse(
            "no credentials are resolved: set %s in the environment, which the local "
            "substitute accepts as throwaway values; no value is printed"
            % " and ".join(CREDENTIAL_VARIABLES)
        )
    method = getattr(credentials, "method", "") or "an unnamed provider"
    if method not in LOCAL_CREDENTIAL_METHODS:
        refuse(
            "the resolved credentials came from %s, and only credentials from the "
            "environment are signed against a loopback endpoint: set %s in the "
            "environment; no value is printed"
            % (method, " and ".join(CREDENTIAL_VARIABLES))
        )
    return credentials


def error_code(failure):
    """Return the error code an S3 client failure reports, or an empty string."""
    response = getattr(failure, "response", None) or {}
    code = str(response.get("Error", {}).get("Code", ""))
    if not code:
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        code = str(status) if status else ""
    return code


def bucket_present(client, host, port, log_path):
    """Return whether the local endpoint already holds the bucket."""
    try:
        client.head_bucket(Bucket=bucket)
        return True
    except botocore.exceptions.EndpointConnectionError:
        refuse(
            "the local endpoint at %s:%d refused the connection while the bucket was "
            "measured; a server log stands in %s when this target started one"
            % (host, port, log_path),
            4,
        )
    except botocore.exceptions.ClientError as failure:
        code = error_code(failure)
        if code in BUCKET_ABSENT_CODES:
            return False
        refuse(
            "the local endpoint refused a head-bucket request for bucket '%s': %s"
            % (bucket, code or "no error code"),
            4,
        )
    except botocore.exceptions.BotoCoreError as failure:
        refuse(
            "the bucket cannot be measured at the local endpoint: %s"
            % type(failure).__name__,
            4,
        )


def create_bucket(client, region):
    """Create the bucket at the local endpoint, reporting one already standing."""
    request = {"Bucket": bucket}
    if region != GLOBAL_REGION:
        request["CreateBucketConfiguration"] = {"LocationConstraint": region}
    try:
        client.create_bucket(**request)
    except botocore.exceptions.ClientError as failure:
        code = error_code(failure)
        if code in BUCKET_PRESENT_CODES:
            report("bucket '%s' is already present at the local endpoint" % bucket)
            return
        refuse(
            "the local endpoint refused to create bucket '%s': %s"
            % (bucket, code or "no error code"),
            4,
        )
    except botocore.exceptions.BotoCoreError as failure:
        refuse(
            "bucket '%s' cannot be created at the local endpoint: %s"
            % (bucket, type(failure).__name__),
            4,
        )
    report(
        "bucket '%s' created at the local endpoint in region %s" % (bucket, region)
    )


host, port = endpoint_address(endpoint)
confirm_bucket_name(bucket)
log_path = os.path.join(log_directory, "moto-%d.log" % port)

import boto3
import botocore.config
import botocore.exceptions

if answers(host, port):
    report(
        "the local substitute already answers at %s:%d, so no server was started"
        % (host, port)
    )
else:
    report(
        "nothing answers at %s:%d; starting the moto server of this virtual environment"
        % (host, port)
    )
    start_server(host, port, log_path)

region = resolved_region()
session = boto3.session.Session()
resolved_credentials(session)
client = session.client(
    "s3",
    endpoint_url=endpoint,
    region_name=region,
    config=botocore.config.Config(
        connect_timeout=REQUEST_CONNECT_TIMEOUT_SECONDS,
        read_timeout=REQUEST_READ_TIMEOUT_SECONDS,
        retries={"max_attempts": 1},
    ),
)
if bucket_present(client, host, port, log_path):
    report("bucket '%s' is already present at the local endpoint" % bucket)
else:
    create_bucket(client, region)
report(
    "the local substitute stands at %s:%d with bucket '%s'; this target addresses that "
    "loopback endpoint alone and provisions nothing on AWS" % (host, port, bucket)
)
endef
export LOCAL_ENDPOINT_PROGRAM

# ---------------------------------------------------------------------------------
# Stage 1. Runtime and dependency measurement.
# ---------------------------------------------------------------------------------
verify-env:
	@mkdir -p '$(ARTIFACTS)'
	report='$(VERSION_REPORT)'
	: > "$$report"
	deviations=0
	strict='no'
	case "$$(printf '%s' "$${HARNESS_STRICT_TOOL_VERSIONS:-}" | tr 'A-Z' 'a-z')" in
	  1 | y | yes | t | true | on) strict='yes' ;;
	esac
	say() {
	  printf '%s\n' "$$1"
	  printf '%s\n' "$$1" >> "$$report"
	}
	fail() {
	  say "verify-env: FATAL $$1"
	  say "verify-env: remediation: $$2"
	  exit 1
	}
	deviation() {
	  say "verify-env: DEVIATION $$1"
	  deviations=$$((deviations + 1))
	}
	say "verify-env report of $(PROJECT_REL) in this checkout"
	say "strict tool versions: $$strict, from HARNESS_STRICT_TOOL_VERSIONS"
	command -v python3.12 > /dev/null 2>&1 || fail 'python3.12 is not on PATH' '$(APT_REMEDIATION)'
	measured_python="$$(python3.12 --version 2>&1 | awk '{print $$2}')"
	say "python3.12: pinned $(PYTHON_PIN) measured $$measured_python"
	case "$$measured_python" in
	  $(PYTHON_SERIES).*) ;;
	  *) fail "python3.12 measures $$measured_python, outside the accepted $(PYTHON_SERIES) series" '$(APT_REMEDIATION)' ;;
	esac
	if [ "$$measured_python" != '$(PYTHON_PIN)' ]; then
	  deviation "python3.12: pinned $(PYTHON_PIN), measured $$measured_python"
	fi
	command -v '$(COBC)' > /dev/null 2>&1 || fail '$(COBC) is not on PATH, so no program of the chain can be compiled' '$(APT_REMEDIATION)'
	measured_cobc="$$($(COBC) --version 2>&1 | head -n 1 | awk '{print $$3}')"
	say "cobc: pinned $(COBC_PIN) measured $$measured_cobc"
	[ "$${measured_cobc%%.*}" = '$(COBC_SERIES)' ] || fail "cobc measures $$measured_cobc, outside the accepted $(COBC_SERIES) series" '$(APT_REMEDIATION)'
	lowest="$$(printf '%s\n%s\n' '$(COBC_MINIMUM)' "$$measured_cobc" | sort -V | head -n 1)"
	[ "$$lowest" = '$(COBC_MINIMUM)' ] || fail "cobc measures $$measured_cobc, below the accepted minimum $(COBC_MINIMUM)" '$(APT_REMEDIATION)'
	if [ "$$measured_cobc" != '$(COBC_PIN)' ]; then
	  deviation "cobc: pinned $(COBC_PIN), measured $$measured_cobc"
	fi
	command -v git > /dev/null 2>&1 || fail 'git is not on PATH, so the read-only gate cannot run' '$(APT_REMEDIATION)'
	measured_git="$$(git --version 2>&1 | awk '{print $$3}')"
	say "git: pinned $(GIT_PIN) measured $$measured_git"
	[ "$${measured_git%%.*}" = '$(GIT_SERIES)' ] || fail "git measures $$measured_git, outside the accepted $(GIT_SERIES) series" '$(APT_REMEDIATION)'
	if [ "$$measured_git" != '$(GIT_PIN)' ]; then
	  deviation "git: pinned $(GIT_PIN), measured $$measured_git"
	fi
	if command -v dpkg-query > /dev/null 2>&1; then
	  for entry in 'python3.12=$(APT_PIN_PYTHON)' 'python3.12-venv=$(APT_PIN_PYTHON_VENV)' 'gnucobol3=$(APT_PIN_GNUCOBOL)' 'git=$(APT_PIN_GIT)'; do
	    package="$${entry%%=*}"
	    pinned="$${entry#*=}"
	    query_status=0
	    measured_package="$$(dpkg-query --showformat='$${Version}' --show "$$package" 2> /dev/null)" || query_status=$$?
	    if [ "$$query_status" -ne 0 ] || [ -z "$$measured_package" ]; then
	      deviation "apt package $$package: pinned $$pinned, not installed through apt"
	    elif [ "$$measured_package" != "$$pinned" ]; then
	      deviation "apt package $$package: pinned $$pinned, measured $$measured_package"
	    else
	      say "apt package $$package: pinned $$pinned measured $$measured_package"
	    fi
	  done
	else
	  deviation 'dpkg-query is not on PATH, so no apt package version was measured'
	fi
	[ -x '$(PY)' ] || fail 'no virtual environment interpreter at $(PROJECT_DIR)/$(PY)' '$(VENV_REMEDIATION)'
	measured_venv_python="$$($(PY) --version 2>&1 | awk '{print $$2}')"
	say "virtual environment interpreter $(PY): measured $$measured_venv_python"
	case "$$measured_venv_python" in
	  $(PYTHON_SERIES).*) ;;
	  *) fail "$(PY) measures $$measured_venv_python, outside the accepted $(PYTHON_SERIES) series" '$(VENV_REMEDIATION)' ;;
	esac
	[ -x '$(PIP)' ] || fail 'no pip at $(PROJECT_DIR)/$(PIP)' '$(VENV_REMEDIATION)'
	measured_pip="$$($(PIP) --version 2>&1 | awk '{print $$2}')"
	[ "$$measured_pip" = '$(PIP_PIN)' ] || fail "pip: pinned $(PIP_PIN), measured $$measured_pip" '$(VENV_REMEDIATION)'
	[ -x '$(DBT)' ] || fail 'no dbt at $(PROJECT_DIR)/$(DBT)' '$(VENV_REMEDIATION)'
	$(PY) -c "$$PIN_CHECK_PROGRAM" requirements.txt '$(PIP_PIN)' "$$measured_pip" '$(REPO_ROOT)' 2>&1 | tee -a "$$report"
	if [ "$$deviations" -gt 0 ] && [ "$$strict" = 'yes' ]; then
	  fail "$$deviations version deviation(s) recorded while HARNESS_STRICT_TOOL_VERSIONS is set" 'install the pinned versions, or leave HARNESS_STRICT_TOOL_VERSIONS unset to accept a reported deviation'
	fi
	say "verify-env: PASS with $$deviations deviation(s), report $(VERSION_REPORT)"

# ---------------------------------------------------------------------------------
# Stage 2. Precondition gate. Probes only, and nothing is provisioned.
# ---------------------------------------------------------------------------------
gate:
	@mkdir -p '$(ARTIFACTS)'
	printf 'gate: probing the real S3 target through landing/land_to_s3.py --probe\n'
	s3_status=0
	$(PY) landing/land_to_s3.py --probe --run-mode redshift > '$(GATE_LOG_S3)' 2>&1 || s3_status=$$?
	printf 'gate: S3 probe status %s, log %s\n' "$$s3_status" '$(GATE_LOG_S3)'
	printf 'gate: probing the real Redshift target through landing/land_to_s3.py --probe-redshift\n'
	redshift_status=0
	$(PY) landing/land_to_s3.py --probe-redshift --run-mode redshift > '$(GATE_LOG_REDSHIFT)' 2>&1 || redshift_status=$$?
	printf 'gate: Redshift probe status %s, log %s\n' "$$redshift_status" '$(GATE_LOG_REDSHIFT)'
	if [ "$$s3_status" -eq 0 ] && [ "$$redshift_status" -eq 0 ]; then
	  selected='redshift'
	else
	  selected='local_substitute'
	fi
	if [ "$$selected" != 'redshift' ] && [ '$(REAL_TARGET_REQUESTED)' = 'yes' ]; then
	  printf 'gate: DBT_TARGET names redshift and a probe did not pass; the probe reports stand in %s and %s\n' '$(GATE_LOG_S3)' '$(GATE_LOG_REDSHIFT)' >&2
	  exit 1
	fi
	$(PY) -c "$$GATE_SELECTION_PROGRAM" '$(GATE_SELECTION)' "$$selected" "$$s3_status" '$(GATE_LOG_S3)' "$$redshift_status" '$(GATE_LOG_REDSHIFT)' > /dev/null
	printf 'gate: selected target %s, recorded in %s\n' "$$selected" '$(GATE_SELECTION)'
	if [ "$$selected" != 'redshift' ]; then
	  printf 'gate: validated against local substitute, not AWS; the formal AWS diff stays OPEN\n'
	fi

# ---------------------------------------------------------------------------------
# Stage 3. Sample records and translated copies. Nothing is written outside
# $(BUILD), and no source file is preprocessed in place.
# ---------------------------------------------------------------------------------
translate:
	@mkdir -p '$(BUILD)/samples'
	for case in $(CASES); do
	  $(PY) extraction/build_sample_commarea.py --sample "$(SAMPLE_INPUT)/commarea_$$case.json" --field-map '$(FIELD_MAP)' --output "$(ABS_BUILD)/samples/commarea_$$case.dat"
	  bytes="$$(wc -c < "$(ABS_BUILD)/samples/commarea_$$case.dat")"
	  if [ "$$bytes" -ne 32500 ] && [ "$$bytes" -ne 32501 ]; then
	    printf 'translate: the record of case %s holds %s bytes, and the COMMAREA record is 32500 characters\n' "$$case" "$$bytes" >&2
	    exit 1
	  fi
	done
	$(PY) harness/translate.py --source-dir '$(SOURCE_DIR)' --build-dir '$(ABS_BUILD)' --statement-map '$(STATEMENT_MAP)' --copybook-dir '$(COPYBOOK_DIR)'
	for name in $(COPIED_SOURCES); do
	  if [ ! -f "$(BUILD)/src/$$name" ]; then
	    printf 'translate: %s is missing from %s\n' "$$name" '$(BUILD)/src' >&2
	    exit 1
	  fi
	done
	printf 'translate: %s sample records and the translated tree stand under %s\n' '$(words $(CASES))' '$(BUILD)'

# ---------------------------------------------------------------------------------
# Stage 4. Compilation of the translated programs, the twelve stubs and the driver.
# ---------------------------------------------------------------------------------
compile:
	@mkdir -p '$(COMPILE_DIR)' '$(ARTIFACTS)'
	log='$(COMPILE_LOG)'
	: > "$$log"
	printf 'compile: %s %s\n' '$(COBC)' '$(COBFLAGS)' | tee -a "$$log"
	$(COBC) --version 2>&1 | head -n 1 | tee -a "$$log"
	built=0
	for source in $(MODULE_SOURCES); do
	  if [ ! -f "$$source" ]; then
	    printf 'compile: %s is missing; run "make translate" first\n' "$$source" >&2
	    exit 1
	  fi
	  module="$(COMPILE_DIR)/$$(basename "$$source" .cbl).so"
	  printf '=== module %s from %s\n' "$$module" "$$source" >> "$$log"
	  $(COBC) $(COBFLAGS) -m -I '$(BUILD)/src' -o "$$module" "$$source" >> "$$log" 2>&1
	  if [ ! -f "$$module" ]; then
	    printf 'compile: no module at %s\n' "$$module" >&2
	    exit 1
	  fi
	  built=$$((built + 1))
	done
	if [ "$$built" -ne $(MODULE_COUNT) ]; then
	  printf 'compile: %s modules were built, and %s are expected\n' "$$built" '$(MODULE_COUNT)' >&2
	  exit 1
	fi
	printf '=== driver %s from harness/driver.cbl\n' '$(COMPILE_DIR)/driver' >> "$$log"
	$(COBC) $(COBFLAGS) -x -I '$(BUILD)/src' -o '$(COMPILE_DIR)/driver' harness/driver.cbl >> "$$log" 2>&1
	if [ ! -x '$(COMPILE_DIR)/driver' ]; then
	  printf 'compile: no driver executable at %s\n' '$(COMPILE_DIR)/driver' >&2
	  exit 1
	fi
	printf 'compile: %s modules and one driver, compiler output in %s\n' "$$built" '$(COMPILE_LOG)'

# ---------------------------------------------------------------------------------
# Stage 5. Execution of the cases CASES_MODE selects through the harness, which builds
# the modules it runs, sets COB_LIBRARY_PATH for them and publishes the evidence set.
# The whole case table runs by default; CASES_MODE=success-only runs the two success
# cases alone. Whichever selection runs, the two success cases are executed, so the
# stages below this one read the same evidence in either mode.
# ---------------------------------------------------------------------------------
execute:
	@mkdir -p '$(ARTIFACTS)'
	case '$(strip $(CASES_MODE))' in
	  all) selection='all' ;;
	  success-only) selection='--success-only' ;;
	  *)
	    printf 'execute: CASES_MODE is "%s"; it names all, for every case of harness/run_harness.sh, or success-only, for the two success cases 01AMOT and 01ACOM\n' '$(strip $(CASES_MODE))' >&2
	    exit 1
	    ;;
	esac
	PY='$(ABS_PY)' COBC='$(COBC)' bash harness/run_harness.sh "$$selection" 2>&1 | tee '$(EXECUTE_LOG)'
	reported_selection="$$(sed -n 's/^[[:space:]]*case selection:[[:space:]]*//p' '$(EXECUTE_LOG)' | tail -n 1)"
	if [ "$$reported_selection" != '$(strip $(CASES_MODE))' ]; then
	  printf 'execute: CASES_MODE names %s and the harness reports the case selection "%s"\n' '$(strip $(CASES_MODE))' "$$reported_selection" >&2
	  exit 1
	fi
	reported_labels="$$(sed -n 's/^[[:space:]]*cases:[[:space:]]*//p' '$(EXECUTE_LOG)' | tail -n 1 | tr ',' ' ')"
	if [ -z "$$reported_labels" ]; then
	  printf 'execute: %s names no executed case\n' '$(EXECUTE_LOG)' >&2
	  exit 1
	fi
	selected=0
	for label in $$reported_labels; do
	  if ! grep -q -E "^[[:space:]]+case $$label: return code " '$(EXECUTE_LOG)'; then
	    printf 'execute: the harness selected case %s and reported no execution of it in %s\n' "$$label" '$(EXECUTE_LOG)' >&2
	    exit 1
	  fi
	  selected=$$((selected + 1))
	done
	executed="$$(sed -n 's/^run_harness.sh:[[:space:]]*cases executed: \([0-9][0-9]*\);.*/\1/p' '$(EXECUTE_LOG)' | tail -n 1)"
	assertions="$$(sed -n 's/^run_harness.sh:[[:space:]]*cases executed: [0-9][0-9]*; assertions passed: \([0-9][0-9]*\).*/\1/p' '$(EXECUTE_LOG)' | tail -n 1)"
	if [ "$$executed" != "$$selected" ]; then
	  printf 'execute: the harness selected %s case(s) and reports "%s" executed\n' "$$selected" "$$executed" >&2
	  exit 1
	fi
	printf 'execute: CASES_MODE %s, %s case(s) executed with %s assertion(s) passed, harness output in %s\n' '$(strip $(CASES_MODE))' "$$executed" "$$assertions" '$(EXECUTE_LOG)'
	$(require_capture_line)
	for case in $(CASES); do
	  captures="$(BUILD)/run/$$case/captures.txt"
	  post="$(BUILD)/run/$$case/commarea_post.dat"
	  for artefact in "$$captures" "$$post"; do
	    if [ ! -s "$$artefact" ]; then
	      printf 'execute: case %s left nothing at %s\n' "$$case" "$$artefact" >&2
	      exit 1
	    fi
	  done
	  case "$$case" in
	    01amot) product_key='SQL_MOTOR_PRESENT' ;;
	    01acom) product_key='SQL_COMMERCIAL_PRESENT' ;;
	    *)
	      printf 'execute: case %s names no product capture group\n' "$$case" >&2
	      exit 1
	      ;;
	  esac
	  require_capture_line "$$captures" 'CA_RETURN_CODE=00'
	  require_capture_line "$$captures" 'SQL_POLICY_PRESENT=Y'
	  require_capture_line "$$captures" "$$product_key=Y"
	  require_capture_line "$$captures" 'VSAM_PRESENT=Y'
	  require_capture_line "$$captures" 'VSAM_LENGTH=0064'
	  require_capture_line "$$captures" 'ABEND_PRESENT=N'
	  policy_number="$$(sed -n 's/^CA_POLICY_NUM=//p' "$$captures")"
	  case "$$policy_number" in
	    '' | *[!0-9]* | 0000000000)
	      printf 'execute: case %s returned the policy number "%s", and the chain assigns ten digits above zero\n' "$$case" "$$policy_number" >&2
	      exit 1
	      ;;
	  esac
	  last_changed="$$(sed -n 's/^CA_LASTCHANGED=//p' "$$captures")"
	  if [ "$${#last_changed}" -ne 26 ]; then
	    printf 'execute: case %s returned the timestamp "%s", and CA-LASTCHANGED holds 26 characters\n' "$$case" "$$last_changed" >&2
	    exit 1
	  fi
	  vsam_key="$$(sed -n 's/^VSAM_KEY=//p' "$$captures")"
	  vsam_request_id="$$(sed -n 's/^VSAM_REQUEST_ID=//p' "$$captures")"
	  vsam_customer="$$(sed -n 's/^VSAM_CUSTOMER_NUM=//p' "$$captures")"
	  vsam_policy="$$(sed -n 's/^VSAM_POLICY_NUM=//p' "$$captures")"
	  if [ "$$vsam_key" != "$$vsam_request_id$$vsam_customer$$vsam_policy" ]; then
	    printf 'execute: case %s wrote the VSAM key "%s", and the request-type letter, the customer number and the policy number compose "%s"\n' "$$case" "$$vsam_key" "$$vsam_request_id$$vsam_customer$$vsam_policy" >&2
	    exit 1
	  fi
	  post_bytes="$$(wc -c < "$$post")"
	  if [ "$$post_bytes" -ne 32500 ] && [ "$$post_bytes" -ne 32501 ]; then
	    printf 'execute: case %s returned %s bytes of COMMAREA, and the record is 32500 characters\n' "$$case" "$$post_bytes" >&2
	    exit 1
	  fi
	  printf 'execute: case %s returned 00 with the policy, product and VSAM captures present\n' "$$case"
	done

# ---------------------------------------------------------------------------------
# Stage 6. Extraction of one landing record per case from the returned COMMAREA.
# ---------------------------------------------------------------------------------
extract:
	@mkdir -p '$(BUILD)/landing'
	for case in $(CASES); do
	  post="$(BUILD)/run/$$case/commarea_post.dat"
	  if [ ! -s "$$post" ]; then
	    printf 'extract: no returned COMMAREA at %s; run "make execute" first\n' "$$post" >&2
	    exit 1
	  fi
	  $(PY) extraction/extract_commarea.py --commarea "$(ABS_BUILD)/run/$$case/commarea_post.dat" --field-map '$(FIELD_MAP)' --output "$(ABS_BUILD)/landing/landing_$$case.json" --overwrite --source-system-key '$(SOURCE_SYSTEM_KEY)'
	done

# ---------------------------------------------------------------------------------
# Stage 7. Landing of one record as one S3 object, for the case named by CASE.
# ---------------------------------------------------------------------------------
land:
	@stage_name='land'
	$(read_selection)
	record="$(BUILD)/landing/landing_$(CASE).json"
	if [ ! -s "$$record" ]; then
	  printf 'land: no landing record at %s; run "make extract" first\n' "$$record" >&2
	  exit 1
	fi
	if [ -z "$${S3_BUCKET:-}" ]; then
	  printf 'land: no destination bucket is set: set S3_BUCKET to an existing bucket, which this bridge never creates; on the local_substitute branch "make local-endpoint" creates it at the loopback endpoint; README.md records the setup\n' >&2
	  exit 1
	fi
	if [ "$$selected" = 'local_substitute' ] && [ -z "$${S3_ENDPOINT_URL:-}" ]; then
	  printf 'land: run mode local_substitute addresses a loopback endpoint: set S3_ENDPOINT_URL to the local S3-compatible endpoint, which "make local-endpoint" brings up; README.md records the setup\n' >&2
	  exit 1
	fi
	part='$(CASE_PART)'
	if [ -z "$$part" ]; then
	  printf 'land: CASE=%s names no landing part: this file records one part per case (%s), and landing a case with no part of its own would address another case object; add a CASE_PART_%s line or name a recorded case\n' '$(CASE)' '$(CASE_PARTS)' '$(CASE)' >&2
	  exit 1
	fi
	$(PY) landing/land_to_s3.py --record "$(PROJECT_DIR)/$$record" --run-mode "$$selected" --source-system-key '$(SOURCE_SYSTEM_KEY)' --entity '$(ENTITY)' --extract-date '$(EXTRACT_DATE)' --part "$$part"

# ---------------------------------------------------------------------------------
# Stage 8. Raw load of the object standing at the landing prefix, one object per source
# system, entity and extract date; CASE names the landing record this stage requires to
# be present. The only stage whose commands differ by target, and it touches no dbt
# model file.
# ---------------------------------------------------------------------------------
load:
	@stage_name='load'
	$(read_selection)
	record="$(BUILD)/landing/landing_$(CASE).json"
	if [ ! -s "$$record" ]; then
	  printf 'load: no landing record at %s; run "make extract" and "make land" first\n' "$$record" >&2
	  exit 1
	fi
	if [ -z "$${S3_BUCKET:-}" ]; then
	  printf 'load: no source bucket is set: set S3_BUCKET to the bucket holding the landed object; on the local_substitute branch "make local-endpoint" brings up the endpoint holding it; README.md records the setup\n' >&2
	  exit 1
	fi
	part='$(CASE_PART)'
	if [ -z "$$part" ]; then
	  printf 'load: CASE=%s names no landing part: this file records one part per case (%s), and loading a case with no part of its own would read another case object; add a CASE_PART_%s line or name a recorded case\n' '$(CASE)' '$(CASE_PARTS)' '$(CASE)' >&2
	  exit 1
	fi
	if [ "$$selected" = 'local_substitute' ]; then
	  if [ -z "$${S3_ENDPOINT_URL:-}" ]; then
	    printf 'load: run mode local_substitute addresses a loopback endpoint: set S3_ENDPOINT_URL to the local S3-compatible endpoint, which "make local-endpoint" brings up; README.md records the setup\n' >&2
	    exit 1
	  fi
	  $(PY) landing/load_local.py --run-mode local_substitute --database '$(LOCAL_DUCKDB)' --source-system-key '$(SOURCE_SYSTEM_KEY)' --entity '$(ENTITY)' --extract-date '$(EXTRACT_DATE)' --part "$$part"
	else
	  $(PY) -c "$$REDSHIFT_LOAD_PROGRAM" "$(PROJECT_DIR)/$$record" '$(DDL_SCHEMAS)' '$(DDL_RAW)' '$(ABS_PY)' '$(LANDER)' '$(REDSHIFT_TEMPLATE)' '$(SOURCE_SYSTEM_KEY)' '$(ENTITY)' '$(EXTRACT_DATE)' "$$part"
	fi

# ---------------------------------------------------------------------------------
# Stage 9. dbt. The same model files serve both targets; only the target name changes.
# ---------------------------------------------------------------------------------
dbt:
	@stage_name='dbt'
	$(read_selection)
	mkdir -p '$(ARTIFACTS)'
	$(DBT) clean --project-dir '$(DBT_PROJECT)' $(DBT_PROFILES_FLAG) 2>&1 | tee '$(DBT_CLEAN_LOG)'
	$(DBT) run --project-dir '$(DBT_PROJECT)' --target "$$selected" $(DBT_PROFILES_FLAG) 2>&1 | tee '$(DBT_RUN_LOG)'
	$(DBT) test --project-dir '$(DBT_PROJECT)' --target "$$selected" $(DBT_PROFILES_FLAG) 2>&1 | tee '$(DBT_TEST_LOG)'
	printf 'dbt: run and test passed against target %s, output in %s and %s\n' "$$selected" '$(DBT_RUN_LOG)' '$(DBT_TEST_LOG)'

# ---------------------------------------------------------------------------------
# Stage 10. Field-by-field comparison of the harness captures with the two canonical
# rows of the same policy.
# ---------------------------------------------------------------------------------
diff:
	@stage_name='diff'
	$(read_selection)
	mkdir -p '$(ARTIFACTS)'
	if [ "$$selected" = 'redshift' ]; then
	  warehouse='redshift'
	else
	  warehouse='duckdb'
	fi
	$(PY) validation/diff_harness_vs_warehouse.py --cases '$(DIFF_CASES)' --run-dir '$(ABS_BUILD)/run' --field-map '$(FIELD_MAP)' --target "$$warehouse" --database '$(LOCAL_DUCKDB)' --source-system-key '$(SOURCE_SYSTEM_KEY)' --report '$(DIFF_REPORT)' --json '$(DIFF_JSON)' --expected-dir '$(ABS_EXPECTED)'

# ---------------------------------------------------------------------------------
# Source guard. Run after each generating stage and as the final gate.
# ---------------------------------------------------------------------------------
verify-readonly:
	@mkdir -p '$(BUILD)/logs'
	bash validation/verify_readonly.sh --stage '$(STAGE)'

# ---------------------------------------------------------------------------------
# The local substitute land and load address. Optional, and outside the order all
# runs: it addresses the loopback endpoint S3_ENDPOINT_URL names and nothing on AWS.
# ---------------------------------------------------------------------------------
local-endpoint:
	@if [ '$(REAL_TARGET_REQUESTED)' = 'yes' ]; then
	  printf 'local-endpoint: DBT_TARGET names redshift, and this target serves the local_substitute branch alone: it brings up a loopback endpoint and provisions nothing on AWS; README.md records the real-target setup\n' >&2
	  exit 1
	fi
	if [ -z "$${S3_ENDPOINT_URL:-}" ]; then
	  printf 'local-endpoint: no local endpoint is set: set S3_ENDPOINT_URL to the loopback endpoint the local substitute answers on; README.md records the setup\n' >&2
	  exit 1
	fi
	if [ -z "$${S3_BUCKET:-}" ]; then
	  printf 'local-endpoint: no bucket is named: set S3_BUCKET to the bucket this target creates at the local endpoint when the endpoint does not already hold it; README.md records the setup\n' >&2
	  exit 1
	fi
	mkdir -p '$(BUILD)/logs'
	$(PY) -c "$$LOCAL_ENDPOINT_PROGRAM" '$(ABS_PY)' "$$S3_ENDPOINT_URL" "$$S3_BUCKET" '$(ABS_BUILD)/logs'

# ---------------------------------------------------------------------------------
# The whole order, in one invocation, stopping at the first failure. land and load run
# once per case, in the order land, load, land, load.
# ---------------------------------------------------------------------------------
all:
	@$(MAKE) $(MAKE_SELF) verify-env
	$(MAKE) $(MAKE_SELF) gate
	$(MAKE) $(MAKE_SELF) verify-readonly STAGE=baseline
	$(MAKE) $(MAKE_SELF) translate
	$(MAKE) $(MAKE_SELF) verify-readonly STAGE=translate
	$(MAKE) $(MAKE_SELF) compile
	$(MAKE) $(MAKE_SELF) verify-readonly STAGE=compile
	$(MAKE) $(MAKE_SELF) execute
	$(MAKE) $(MAKE_SELF) verify-readonly STAGE=execute
	$(MAKE) $(MAKE_SELF) extract
	$(MAKE) $(MAKE_SELF) land CASE=01amot
	$(MAKE) $(MAKE_SELF) load CASE=01amot
	$(MAKE) $(MAKE_SELF) land CASE=01acom
	$(MAKE) $(MAKE_SELF) load CASE=01acom
	$(MAKE) $(MAKE_SELF) verify-readonly STAGE=load
	$(MAKE) $(MAKE_SELF) dbt
	$(MAKE) $(MAKE_SELF) verify-readonly STAGE=dbt
	$(MAKE) $(MAKE_SELF) diff
	$(MAKE) $(MAKE_SELF) verify-readonly STAGE=final
	printf 'all: every stage of %s completed\n' '$(MAKEFILE_PATH)'

