#!/usr/bin/env bash
#
# run_harness.sh - build, compile and execute the GnuCOBOL validation harness
# for the GenApp Policy-Issue chain.
#
# Takes the harness from the untouched sources to two executed samples with
# retained evidence. Runs non-interactively, installs nothing, reaches no
# network and stops at the first failing step.
#
# Stages, in execution order:
#   1 preflight   Resolves the repository root from the location of this
#                 script, checks the Python interpreter, the COBOL compiler and
#                 every harness input, and creates the build directories.
#   2 samples     Generates one 32,500-character COMMAREA record per selected
#                 case and translates read-only copies of the three named
#                 programs into the build tree.
#   3 compile     Builds the twelve stubs and the three translated programs as
#                 callable modules and the driver as an executable.
#   4 execute     Runs the driver once per selected case and checks the
#                 post-chain record and the captures it wrote.
#   5 evidence    Copies the retained logs and captures into the validation
#                 artifacts directory and prints the run summary.
#
# Arguments:
#   [CASE]        01AMOT, 01ACOM or both. Default: both. Accepted in either
#                 letter case. Any other value is a usage error.
#   --help, -h    Print the usage block and exit 0.
#
# Environment items honoured:
#   PY            Python interpreter used for the record builder and the
#                 translator. A relative value resolves from the repository
#                 root. Default: modernization/.venv/bin/python
#   COBC          COBOL compiler command. Default: cobc
#   COBC_FLAGS    Compiler flags shared by every module and the driver.
#                 Default: -std=ibm -ffold-copy=LOWER -ext cpy
#   HARNESS_POLICY_NUMBER
#                 Identity seed of case 01AMOT, one to nine digits above zero.
#                 Case 01ACOM receives the next value, whichever cases are
#                 selected. Default: 1000001, so 01AMOT receives 1000001 and
#                 01ACOM receives 1000002.
#   HARNESS_LASTCHANGED
#                 Timestamp seed of every selected case, exactly twenty-six
#                 characters in YYYY-MM-DD-HH.MM.SS.NNNNNN form and free of
#                 spaces. Default: 2026-08-19-12.00.00.000000
#   HARNESS_STRICT_TOOL_VERSIONS
#                 A true value makes any compiler version other than the
#                 pinned one a preflight failure instead of a reported
#                 deviation. Default: unset.
#
# Environment items exported to the driver:
#   COB_LIBRARY_PATH  module directory of this run
#   COB_LS_FIXED      1, the setting the full-length post-chain record is
#                     written under
#   COB_PRE_LOAD      the fifteen module names of this run
#   HARNESS_CASE, DD_SAMPLEFILE, DD_POSTFILE, DD_CAPTFILE,
#   HARNESS_POLICY_NUMBER, HARNESS_LASTCHANGED
#
# Every generated file is written under modernization/harness/build. The one
# exception is the evidence copy of stage 5, which writes into
# modernization/validation/artifacts.
#
# Driver exit statuses, reported for the operator when a case fails:
#   0 every check passed
#   1 the chain returned a code other than '00'
#   2 an abend was captured
#   3 a required capture is missing or inconsistent
#   4 a file input-output operation failed
#   5 a required environment item was not provided
#
# Exit codes of this script:
#   0 every stage passed
#   1 usage error: an unrecognised argument, case or argument count
#   2 preflight failure: a missing tool, interpreter, input or directory, an
#     unusable compiler version or an invalid seed value
#   3 sample generation failure or a generated record of the wrong size
#   4 translation failure, a missing generated source, or a source whose
#     SHA-256 no longer matches the baseline the translator recorded
#   5 compilation failure or a missing module or driver
#   6 execution failure: a non-zero driver status or a failed capture check
#   7 evidence copy failure
# Any non-zero code stops the fail-fast modernization/Makefile that invokes
# this script.
#
# Install this file with the execute bit set (chmod +x
# modernization/harness/run_harness.sh); "bash modernization/harness/
# run_harness.sh" runs it without one.
#
# Harness topology: Figure 5 - Validation Harness Control Flow in
# modernization/docs/architecture.md. Decisions taken about the harness are
# recorded in modernization/docs/decision-log.md.

set -euo pipefail
IFS=$'\n\t'

# --------------------------------------------------------------------------
# Program identity and exit codes
# --------------------------------------------------------------------------
readonly PROGRAM="run_harness.sh"

readonly EXIT_OK=0
readonly EXIT_USAGE=1
readonly EXIT_PREFLIGHT=2
readonly EXIT_SAMPLE=3
readonly EXIT_TRANSLATE=4
readonly EXIT_COMPILE=5
readonly EXIT_EXECUTE=6
readonly EXIT_EVIDENCE=7

# --------------------------------------------------------------------------
# Fixed harness values
# --------------------------------------------------------------------------
# One generated COMMAREA record is 32,500 characters and one line feed.
readonly RECORD_BYTES=32501

# Length of the KSDSPOLY record the projection writes.
readonly VSAM_RECORD_LENGTH=64

# Compiler release the dependency inventory pins, and the lowest release of
# the same major series this script accepts.
readonly COBC_VERSION_PINNED="3.1.2.0"
readonly COBC_VERSION_FLOOR="3.1.2"
readonly COBC_MAJOR_REQUIRED=3

# Python release series the record builder and the translator run under.
readonly PYTHON_SERIES="3.12"

# Compiler flags shared by every module and the driver when COBC_FLAGS names
# no value of its own.
readonly COBC_FLAGS_DEFAULT="-std=ibm -ffold-copy=LOWER -ext cpy"

# Identity and timestamp seeds. HARNESS_POLICY_NUMBER names the seed of case
# 01AMOT; case 01ACOM receives the value after it.
readonly POLICY_NUMBER_DEFAULT=1000001
readonly LASTCHANGED_DEFAULT="2026-08-19-12.00.00.000000"
readonly LASTCHANGED_LENGTH=26
readonly POLICY_NUMBER_MAX=999999999

# Every case this script knows, in execution order.
readonly -a ALL_CASES=("01AMOT" "01ACOM")

# Sources compiled as callable modules, as "<path>|<PROGRAM-ID>". The output
# name of each module is its PROGRAM-ID, which is the name the dynamic CALL of
# a literal resolves. Paths under modernization/harness/build/src are filled in
# once the build tree is known.
readonly -a STUB_MODULES=(
  "modernization/harness/stubs/cics_abend.cbl|CICS-ABEND"
  "modernization/harness/stubs/cics_write.cbl|CICS-WRITE"
  "modernization/harness/stubs/cics_asktime.cbl|CICS-ASKTIME"
  "modernization/harness/stubs/cics_formattime.cbl|CICS-FORMATTIME"
  "modernization/harness/stubs/cics_diag_link.cbl|CICS-DIAG-LINK"
  "modernization/harness/stubs/sql_insert_policy.cbl|SQL-INSERT-POLICY"
  "modernization/harness/stubs/sql_insert_motor.cbl|SQL-INSERT-MOTOR"
  "modernization/harness/stubs/sql_insert_commercial.cbl|SQL-INSERT-COMMERCIAL"
  "modernization/harness/stubs/sql_insert_endowment.cbl|SQL-INSERT-ENDOWMENT"
  "modernization/harness/stubs/sql_insert_house.cbl|SQL-INSERT-HOUSE"
  "modernization/harness/stubs/sql_set_identity.cbl|SQL-SET-IDENTITY"
  "modernization/harness/stubs/sql_select_lastchanged.cbl|SQL-SELECT-LASTCHANGED"
)

# Translated programs compiled as callable modules, as "<file>|<PROGRAM-ID>".
# Each file name is relative to the generated source directory.
readonly -a PROGRAM_MODULES=(
  "lgapol01.cbl|LGAPOL01"
  "lgapdb01.cbl|LGAPDB01"
  "lgapvs01.cbl|LGAPVS01"
)

# Files the translator leaves in the generated source directory: the three
# translated programs, the two source copybooks copied verbatim and the four
# harness copybooks.
readonly -a GENERATED_SOURCES=(
  "lgapol01.cbl"
  "lgapdb01.cbl"
  "lgapvs01.cbl"
  "lgcmarea.cpy"
  "lgpolicy.cpy"
  "dfheiblk.cpy"
  "dfhresp.cpy"
  "hsqlca.cpy"
  "hcapture.cpy"
)

# Harness copybooks the translator reads.
readonly -a HARNESS_COPYBOOKS=(
  "modernization/harness/copybooks/dfheiblk.cpy"
  "modernization/harness/copybooks/dfhresp.cpy"
  "modernization/harness/copybooks/hsqlca.cpy"
  "modernization/harness/copybooks/hcapture.cpy"
)

# Repository-relative inputs every run reads.
readonly TRANSLATOR="modernization/harness/translate.py"
readonly STATEMENT_MAP="modernization/harness/statement_map.yml"
readonly COPYBOOK_DIR="modernization/harness/copybooks"
readonly DRIVER_SOURCE="modernization/harness/driver.cbl"
readonly RECORD_BUILDER="modernization/extraction/build_sample_commarea.py"
readonly FIELD_MAP="modernization/extraction/copybook_field_map.yml"
readonly SAMPLE_INPUT_DIR="modernization/extraction/sample_input"
readonly SOURCE_DIR="base/src"

# External tools every run invokes, beyond the compiler and the interpreter.
readonly -a REQUIRED_TOOLS=("mkdir" "rm" "cp" "tee" "wc" "grep" "sha256sum" "date")

# --------------------------------------------------------------------------
# Run state
# --------------------------------------------------------------------------
SCRIPT_PATH=""
HARNESS_DIR=""
REPO_ROOT=""
BUILD_DIR=""
SRC_DIR=""
BIN_DIR=""
SAMPLES_DIR=""
RUN_DIR=""
LOGS_DIR=""
ARTIFACTS_DIR=""

# Cases selected by the command line.
declare -a SELECTED_CASES=()

# Measured tool versions, filled in by the preflight.
COBC_VERSION=""
COBC_VERSION_VERDICT=""
PYTHON_VERSION=""

# Compiler flags of this run, as one string for the messages and as the
# argument list every compile passes to the compiler.
declare -a COBC_FLAG_LIST=()

# Resolved seeds.
POLICY_NUMBER_BASE=""
LASTCHANGED_SEED=""

# Colon-separated module names handed to the runtime as a resolution aid.
MODULE_PRELOAD=""

# Status of the most recent command run through run_and_tee.
RUN_STATUS=0

# Summary state, one entry per executed case and one per retained artifact.
declare -a SUMMARY_CASE_LINES=()
declare -a SUMMARY_ARTIFACTS=()

# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
# Prints the argument, the honoured environment items and the exit codes.
# Written with shell builtins only; it stays available before the preflight has
# checked anything.
usage() {
  local line=""
  while IFS= read -r line; do
    printf '%s\n' "$line"
  done <<'USAGE_TEXT'
Usage: run_harness.sh [CASE]
       run_harness.sh --help

Builds, compiles and executes the GnuCOBOL validation harness for the GenApp
Policy-Issue chain, then retains the logs and captures of the run.

Arguments:
  CASE        01AMOT, 01ACOM or both, in either letter case. Default: both.
  --help, -h  Print this block and exit 0.

Environment items honoured:
  PY                     Python interpreter for the record builder and the
                         translator; a relative value resolves from the
                         repository root.
                         Default: modernization/.venv/bin/python
  COBC                   COBOL compiler command. Default: cobc
  COBC_FLAGS             Compiler flags for every module and the driver.
                         Default: -std=ibm -ffold-copy=LOWER -ext cpy
  HARNESS_POLICY_NUMBER  Identity seed of case 01AMOT, one to nine digits
                         above zero; case 01ACOM receives the next value.
                         Default: 1000001
  HARNESS_LASTCHANGED    Timestamp seed of every selected case, exactly 26
                         characters in YYYY-MM-DD-HH.MM.SS.NNNNNN form.
                         Default: 2026-08-19-12.00.00.000000
  HARNESS_STRICT_TOOL_VERSIONS
                         A true value (1, y, yes, t, true or on) makes a
                         compiler version other than the pinned 3.1.2.0 a
                         preflight failure instead of a reported deviation.

Environment items exported to the driver:
  COB_LIBRARY_PATH, COB_LS_FIXED, COB_PRE_LOAD, HARNESS_CASE, DD_SAMPLEFILE,
  DD_POSTFILE, DD_CAPTFILE, HARNESS_POLICY_NUMBER, HARNESS_LASTCHANGED

Generated output:
  modernization/harness/build/samples/commarea_<case>.dat
  modernization/harness/build/src/            translated programs, copybooks
  modernization/harness/build/bin/            fifteen modules and the driver
  modernization/harness/build/logs/           translate.log, compile.log,
                                              translation-report.json,
                                              source-baseline.sha256
  modernization/harness/build/run/<case>/     commarea_post.dat, captures.txt,
                                              driver.log
Retained evidence:
  modernization/validation/artifacts/         the logs, the report, the
                                              baseline and one driver log and
                                              capture file per case

Exit codes:
  0 every stage passed
  1 usage error
  2 preflight failure
  3 sample generation failure or a record of the wrong size
  4 translation failure, a missing generated source or a baseline mismatch
  5 compilation failure or a missing module or driver
  6 execution failure or a failed capture check
  7 evidence copy failure

Installs nothing, reaches no network and never prompts.
USAGE_TEXT
}

# Prints one progress line for a stage.
emit_stage() {
  printf '%s: == stage %s of 5: %s ==\n' "$PROGRAM" "$1" "$2"
}

# Prints one progress line for a step inside a stage.
emit_step() {
  printf '%s:   %s\n' "$PROGRAM" "$1"
}

# Prints one line that reports a measured value differing from a pinned one.
# The line names both values and the run continues.
emit_deviation() {
  printf '%s:   DEVIATION %s\n' "$PROGRAM" "$1"
}

# Prints one line of the final summary block.
emit_summary() {
  printf '%s\n' "$1"
}

# Prints one diagnostic on standard error and ends the run with the supplied
# status. Every message names the offending value and the action that clears
# it.
die() {
  local status="$1"
  shift
  local line=""
  for line in "$@"; do
    printf '%s: error: %s\n' "$PROGRAM" "$line" >&2
  done
  exit "$status"
}

# Prints the usage block on standard error, preceded by one diagnostic, and
# ends the run as a usage error.
die_usage() {
  printf '%s: error: %s\n' "$PROGRAM" "$1" >&2
  usage >&2
  exit "$EXIT_USAGE"
}

# --------------------------------------------------------------------------
# Path resolution
# --------------------------------------------------------------------------
# Records the physical path of this script and the harness directory holding
# it, then the repository root two levels above that directory, and moves to
# that root. The result does not depend on the working directory of the caller.
resolve_paths() {
  local source="${BASH_SOURCE[0]}" dir="" base=""

  base="${source##*/}"
  dir="${source%/*}"
  if [[ "$dir" == "$source" ]]; then
    dir="."
  fi
  if ! dir="$(cd -P -- "$dir" 2>/dev/null && printf '%s' "$PWD")" ||
    [[ -z "$dir" ]]; then
    die "$EXIT_PREFLIGHT" \
      "unable to resolve the directory holding this script: ${source}"
  fi

  HARNESS_DIR="$dir"
  SCRIPT_PATH="${dir}/${base}"
  if [[ ! -f "$SCRIPT_PATH" ]]; then
    die "$EXIT_PREFLIGHT" \
      "unable to resolve this script as a regular file: ${SCRIPT_PATH}"
  fi

  if ! REPO_ROOT="$(cd -P -- "${HARNESS_DIR}/../.." 2>/dev/null && printf '%s' "$PWD")" ||
    [[ -z "$REPO_ROOT" ]]; then
    die "$EXIT_PREFLIGHT" \
      "unable to resolve the repository root above ${HARNESS_DIR}"
  fi

  BUILD_DIR="${HARNESS_DIR}/build"
  SRC_DIR="${BUILD_DIR}/src"
  BIN_DIR="${BUILD_DIR}/bin"
  SAMPLES_DIR="${BUILD_DIR}/samples"
  RUN_DIR="${BUILD_DIR}/run"
  LOGS_DIR="${BUILD_DIR}/logs"
  ARTIFACTS_DIR="${REPO_ROOT}/modernization/validation/artifacts"

  # Every repository-relative path below resolves from here, and the baseline
  # the translator writes lists its entries relative to this directory.
  if ! cd -P -- "$REPO_ROOT"; then
    die "$EXIT_PREFLIGHT" \
      "unable to change directory to the repository root: ${REPO_ROOT}"
  fi
}

# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------
# Fills SELECTED_CASES from the optional first argument. Accepts one argument
# at most and rejects any value other than a known case or "both".
parse_args() {
  local requested="both"

  if (($# > 1)); then
    die_usage "one argument at most is accepted; received $#"
  fi
  if (($# == 1)); then
    requested="$1"
  fi

  case "$requested" in
    --help | -h)
      usage
      exit "$EXIT_OK"
      ;;
    both | BOTH | Both)
      SELECTED_CASES=("${ALL_CASES[@]}")
      ;;
    01AMOT | 01amot)
      SELECTED_CASES=("01AMOT")
      ;;
    01ACOM | 01acom)
      SELECTED_CASES=("01ACOM")
      ;;
    *)
      die_usage "unrecognised argument: ${requested}"
      ;;
  esac
}

# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
# Prints the lower-case file-name form of a case label.
case_lower() {
  printf '%s' "${1,,}"
}

# Prints the remaining arguments joined by the first one. The join does not use
# the field separator this script runs under.
join_with() {
  local separator="$1"
  shift
  local out="" item=""

  for item in "$@"; do
    if [[ -n "$out" ]]; then
      out+="$separator"
    fi
    out+="$item"
  done
  printf '%s' "$out"
}

# Prints the identity seed of a case: the base value for 01AMOT and the value
# after it for 01ACOM, whichever cases the command line selected.
policy_number_for() {
  case "$1" in
    01AMOT) printf '%s' "$POLICY_NUMBER_BASE" ;;
    01ACOM) printf '%s' "$((POLICY_NUMBER_BASE + 1))" ;;
    *) die "$EXIT_PREFLIGHT" "no identity seed is defined for case ${1}" ;;
  esac
}

# Succeeds when the supplied value is one of the spellings this script reads
# as true.
is_true() {
  case "${1,,}" in
    1 | y | yes | t | true | on) return 0 ;;
    *) return 1 ;;
  esac
}

# Prints the size of the supplied file in bytes. Fails when the file cannot be
# read.
file_size() {
  local size=""

  if ! size="$(wc -c <"$1" 2>/dev/null)"; then
    return 1
  fi
  printf '%s' "${size//[[:space:]]/}"
}

# Appends one command line to the named log. Each compiler diagnostic in the
# log then follows the command line of the module it belongs to.
log_command() {
  local log="$1"
  shift

  if ! printf '+ %s\n' "$(join_with " " "$@")" >>"$log"; then
    die "$EXIT_COMPILE" "unable to append to the log: ${log}"
  fi
}

# Runs the supplied command with its output merged and appended to the log
# named by the first argument. The status of the command, not the status of
# "tee", is reported in RUN_STATUS; this function itself always succeeds, and
# the caller reads RUN_STATUS to decide what a non-zero status means.
run_and_tee() {
  local log="$1"
  shift

  RUN_STATUS=0
  set +e
  "$@" 2>&1 | tee -a "$log"
  RUN_STATUS="${PIPESTATUS[0]}"
  set -e
  return 0
}

# Succeeds when the first dotted version is at or above the second. A field
# missing from either value counts as zero, and a field that is not a decimal
# number fails the comparison.
version_at_least() {
  local -a left=() right=()
  local index=0 count=0 lhs="" rhs=""

  IFS='.' read -r -a left <<<"$1"
  IFS='.' read -r -a right <<<"$2"
  count="${#left[@]}"
  if ((${#right[@]} > count)); then
    count="${#right[@]}"
  fi

  for ((index = 0; index < count; index++)); do
    lhs="${left[index]:-0}"
    rhs="${right[index]:-0}"
    if [[ ! "$lhs" =~ ^[0-9]+$ ]] || [[ ! "$rhs" =~ ^[0-9]+$ ]]; then
      return 1
    fi
    if ((10#$lhs > 10#$rhs)); then
      return 0
    fi
    if ((10#$lhs < 10#$rhs)); then
      return 1
    fi
  done
  return 0
}

# --------------------------------------------------------------------------
# Stage 1: preflight
# --------------------------------------------------------------------------
# Checks that every external tool this run invokes is on PATH.
preflight_tools() {
  local tool=""
  for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      die "$EXIT_PREFLIGHT" \
        "required tool not found on PATH: ${tool}" \
        "install it, or add its directory to PATH, and run this script again"
    fi
  done
}

# Resolves the Python interpreter and checks its release series. A relative
# value resolves from the repository root, which is the working directory of
# every stage.
preflight_python() {
  local reported=""

  PY="${PY:-modernization/.venv/bin/python}"
  if [[ -z "$PY" ]]; then
    die "$EXIT_PREFLIGHT" \
      "PY is set to an empty value" \
      "unset PY to use modernization/.venv/bin/python, or set it to an interpreter"
  fi
  if [[ ! -x "$PY" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the Python interpreter is not an executable file: ${PY}" \
      "create the environment with: /usr/local/bin/python3.12 -m venv --clear modernization/.venv" \
      "then install the pinned dependencies with: ./modernization/.venv/bin/python -m pip install -r modernization/requirements.txt" \
      "or set PY to an interpreter of the ${PYTHON_SERIES} series"
  fi
  if ! reported="$("$PY" --version 2>&1)" || [[ -z "$reported" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the Python interpreter did not report a version: ${PY}" \
      "check it with: ${PY} --version"
  fi
  if [[ ! "$reported" =~ ^Python[[:space:]]+([0-9]+\.[0-9]+(\.[0-9]+)?) ]]; then
    die "$EXIT_PREFLIGHT" \
      "unable to read a version from: ${reported}" \
      "set PY to an interpreter whose --version reports a Python ${PYTHON_SERIES} release"
  fi
  PYTHON_VERSION="${BASH_REMATCH[1]}"
  if [[ "$PYTHON_VERSION" != "${PYTHON_SERIES}" &&
    "$PYTHON_VERSION" != "${PYTHON_SERIES}".* ]]; then
    die "$EXIT_PREFLIGHT" \
      "the interpreter reports Python ${PYTHON_VERSION}; the harness runs on the ${PYTHON_SERIES} series" \
      "point PY at an interpreter of that series, such as modernization/.venv/bin/python"
  fi
  emit_step "python ${PYTHON_VERSION} (${PY})"
}

# Resolves the COBOL compiler, reads its version and compares it with the
# pinned release. A missing compiler ends the run with the commands that
# install the pinned package; this script installs nothing itself. A version
# below the accepted floor, or outside the accepted major series, ends the run.
# Any other difference from the pinned release is reported as a deviation, and
# a true HARNESS_STRICT_TOOL_VERSIONS turns that report into a failure.
preflight_cobc() {
  local reported="" major=""

  COBC="${COBC:-cobc}"
  if [[ -z "$COBC" ]]; then
    die "$EXIT_PREFLIGHT" \
      "COBC is set to an empty value" \
      "unset COBC to use cobc, or set it to a GnuCOBOL compiler command"
  fi
  if ! command -v "$COBC" >/dev/null 2>&1; then
    die "$EXIT_PREFLIGHT" \
      "the COBOL compiler was not found on PATH: ${COBC}" \
      "the package index of this checkout is empty, so refresh it first with: apt-get update" \
      "then install the pinned compiler with: apt-get install --reinstall -y gnucobol3=${COBC_VERSION_PINNED%.*}-5.1ubuntu1" \
      "this script reports the requirement and installs nothing" \
      "set COBC to an installed compiler to use one already present"
  fi
  if ! reported="$("$COBC" --version 2>&1 | head -n 1)" || [[ -z "$reported" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the COBOL compiler did not report a version: ${COBC}" \
      "check it with: ${COBC} --version"
  fi
  if [[ ! "$reported" =~ GnuCOBOL\)?[[:space:]]+([0-9]+(\.[0-9]+)*) ]]; then
    die "$EXIT_PREFLIGHT" \
      "unable to read a GnuCOBOL version from: ${reported}" \
      "set COBC to a GnuCOBOL compiler whose --version names its release"
  fi
  COBC_VERSION="${BASH_REMATCH[1]}"
  major="${COBC_VERSION%%.*}"
  if [[ "$major" != "$COBC_MAJOR_REQUIRED" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the compiler reports GnuCOBOL ${COBC_VERSION}; the harness is compiled by the ${COBC_MAJOR_REQUIRED}.x series" \
      "install gnucobol3=${COBC_VERSION_PINNED%.*}-5.1ubuntu1 after apt-get update, or set COBC to a ${COBC_MAJOR_REQUIRED}.x compiler"
  fi
  if ! version_at_least "$COBC_VERSION" "$COBC_VERSION_FLOOR"; then
    die "$EXIT_PREFLIGHT" \
      "the compiler reports GnuCOBOL ${COBC_VERSION}, below the accepted ${COBC_VERSION_FLOOR}" \
      "install gnucobol3=${COBC_VERSION_PINNED%.*}-5.1ubuntu1 after apt-get update, or set COBC to a ${COBC_VERSION_FLOOR} or later compiler"
  fi

  if [[ "$COBC_VERSION" == "$COBC_VERSION_PINNED" ]]; then
    COBC_VERSION_VERDICT="MATCH"
    emit_step "cobc ${COBC_VERSION} (${COBC}) MATCH pinned ${COBC_VERSION_PINNED}"
    return 0
  fi
  # A version other than the pinned one is reported once and the run
  # continues, unless the caller asked for the pin to be enforced.

  COBC_VERSION_VERDICT="DEVIATION"
  if is_true "${HARNESS_STRICT_TOOL_VERSIONS:-}"; then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_STRICT_TOOL_VERSIONS is set and the compiler reports GnuCOBOL ${COBC_VERSION} rather than the pinned ${COBC_VERSION_PINNED}" \
      "install gnucobol3=${COBC_VERSION_PINNED%.*}-5.1ubuntu1 after apt-get update, or unset HARNESS_STRICT_TOOL_VERSIONS to accept ${COBC_VERSION}"
  fi
  emit_step "cobc ${COBC_VERSION} (${COBC})"
  emit_deviation "cobc pinned=${COBC_VERSION_PINNED} measured=${COBC_VERSION}"
}

# Resolves the compiler flags into the argument list every compile passes on.
# An unset or empty COBC_FLAGS takes the default flag set.
preflight_cobc_flags() {
  COBC_FLAGS="${COBC_FLAGS:-$COBC_FLAGS_DEFAULT}"
  IFS=$' \t\n' read -r -a COBC_FLAG_LIST <<<"$COBC_FLAGS"
  if ((${#COBC_FLAG_LIST[@]} == 0)); then
    die "$EXIT_PREFLIGHT" \
      "COBC_FLAGS carries no flag" \
      "unset COBC_FLAGS to use ${COBC_FLAGS_DEFAULT}, or set it to the flags every compile takes"
  fi
  emit_step "cobc flags: ${COBC_FLAGS}"
}

# Checks that every harness input this run reads is a readable regular file,
# and that the read-only source directory the translator reads is present.
preflight_inputs() {
  local path="" entry="" name=""
  local -a required=(
    "$TRANSLATOR"
    "$STATEMENT_MAP"
    "$DRIVER_SOURCE"
    "$RECORD_BUILDER"
    "$FIELD_MAP"
  )

  for entry in "${HARNESS_COPYBOOKS[@]}"; do
    required+=("$entry")
  done
  for entry in "${STUB_MODULES[@]}"; do
    required+=("${entry%%|*}")
  done
  for entry in "${ALL_CASES[@]}"; do
    name="$(case_lower "$entry")"
    required+=("${SAMPLE_INPUT_DIR}/commarea_${name}.json")
  done

  if [[ ! -d "$SOURCE_DIR" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the read-only source directory is missing: ${REPO_ROOT}/${SOURCE_DIR}" \
      "run this script from a checkout that carries the named GenApp sources"
  fi
  for path in "${required[@]}"; do
    if [[ ! -f "$path" ]]; then
      die "$EXIT_PREFLIGHT" \
        "required harness input is missing: ${REPO_ROOT}/${path}" \
        "restore it before running the harness"
    fi
    if [[ ! -r "$path" ]]; then
      die "$EXIT_PREFLIGHT" \
        "required harness input is not readable: ${REPO_ROOT}/${path}" \
        "grant read permission before running the harness"
    fi
  done
  emit_step "inputs present: ${#required[@]} files under modernization/ plus ${SOURCE_DIR}/"
}

# Resolves and checks the two deterministic seeds. A supplied identity seed
# holds one to nine digits above zero and leaves room for the value the second
# case receives; a supplied timestamp seed holds exactly twenty-six characters
# in the form the chain reads back.
preflight_seeds() {
  local supplied=""

  supplied="${HARNESS_POLICY_NUMBER:-$POLICY_NUMBER_DEFAULT}"
  if [[ ! "$supplied" =~ ^[0-9]{1,9}$ ]]; then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_POLICY_NUMBER holds ${supplied}; one to nine digits are accepted" \
      "unset it to use ${POLICY_NUMBER_DEFAULT}, or set it to a value in that range"
  fi
  if ((10#$supplied <= 0)); then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_POLICY_NUMBER holds ${supplied}; a value above zero is required" \
      "unset it to use ${POLICY_NUMBER_DEFAULT}, or set it to a value above zero"
  fi
  if ((10#$supplied >= POLICY_NUMBER_MAX)); then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_POLICY_NUMBER holds ${supplied}; the value after it must stay at or below ${POLICY_NUMBER_MAX}" \
      "unset it to use ${POLICY_NUMBER_DEFAULT}, or set it below ${POLICY_NUMBER_MAX}"
  fi
  POLICY_NUMBER_BASE="$((10#$supplied))"

  supplied="${HARNESS_LASTCHANGED:-$LASTCHANGED_DEFAULT}"
  if ((${#supplied} != LASTCHANGED_LENGTH)); then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_LASTCHANGED holds ${#supplied} characters; exactly ${LASTCHANGED_LENGTH} are required" \
      "unset it to use ${LASTCHANGED_DEFAULT}, or set it to a value of that width"
  fi
  if [[ ! "$supplied" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{6}$ ]]; then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_LASTCHANGED holds ${supplied}; the form YYYY-MM-DD-HH.MM.SS.NNNNNN is required" \
      "unset it to use ${LASTCHANGED_DEFAULT}, or set it to a value of that form"
  fi
  LASTCHANGED_SEED="$supplied"

  emit_step "seeds: 01AMOT policy $(policy_number_for 01AMOT), 01ACOM policy $(policy_number_for 01ACOM), lastchanged ${LASTCHANGED_SEED}"
}

# Creates the build directories of this run, the per-case run directories and
# the validation artifacts directory.
prepare_directories() {
  local entry="" name=""
  local -a wanted=("$BUILD_DIR" "$SRC_DIR" "$BIN_DIR" "$SAMPLES_DIR" "$RUN_DIR"
    "$LOGS_DIR" "$ARTIFACTS_DIR")

  for entry in "${ALL_CASES[@]}"; do
    name="$(case_lower "$entry")"
    wanted+=("${RUN_DIR}/${name}")
  done

  for entry in "${wanted[@]}"; do
    if [[ -e "$entry" && ! -d "$entry" ]]; then
      die "$EXIT_PREFLIGHT" \
        "a required directory exists as something other than a directory: ${entry}" \
        "remove that entry and run this script again"
    fi
    if ! mkdir -p -- "$entry"; then
      die "$EXIT_PREFLIGHT" "unable to create directory: ${entry}"
    fi
  done
  emit_step "directories ready under ${BUILD_DIR}"
  emit_step "evidence directory ready at ${ARTIFACTS_DIR}"
}

# Runs every preflight check and reports the selected cases.
stage_preflight() {
  emit_stage 1 "preflight"
  preflight_tools
  preflight_python
  preflight_cobc
  preflight_cobc_flags
  preflight_inputs
  preflight_seeds
  prepare_directories
  emit_step "cases selected: $(join_with ", " "${SELECTED_CASES[@]}")"
}

# --------------------------------------------------------------------------
# Stage 2: samples and translation
# --------------------------------------------------------------------------
# Generates the full-length COMMAREA record of every selected case and checks
# its size. The size check protects the offset decoding every later step
# applies to the record.
build_samples() {
  local label="" lower="" sample="" output="" size=""

  for label in "${SELECTED_CASES[@]}"; do
    lower="$(case_lower "$label")"
    sample="${SAMPLE_INPUT_DIR}/commarea_${lower}.json"
    output="${SAMPLES_DIR}/commarea_${lower}.dat"

    rm -f -- "$output"
    if ! "$PY" "$RECORD_BUILDER" \
      --sample "$sample" \
      --output "$output" \
      --field-map "$FIELD_MAP"; then
      die "$EXIT_SAMPLE" \
        "the record builder failed for case ${label} on ${sample}" \
        "reproduce it with: ${PY} ${RECORD_BUILDER} --sample ${sample} --output ${output} --field-map ${FIELD_MAP}"
    fi
    if [[ ! -f "$output" ]]; then
      die "$EXIT_SAMPLE" \
        "the record builder reported success for case ${label} but left no record at ${output}"
    fi
    if ! size="$(file_size "$output")"; then
      die "$EXIT_SAMPLE" \
        "unable to read the size of the generated record for case ${label}: ${output}"
    fi
    if [[ "$size" != "$RECORD_BYTES" ]]; then
      die "$EXIT_SAMPLE" \
        "the generated record for case ${label} holds ${size} bytes: ${output}" \
        "${RECORD_BYTES} bytes are required, being 32,500 characters and one line feed" \
        "check the field map and the sample definition, then run this script again"
    fi
    emit_step "sample ${label}: ${output} (${size} bytes)"
  done
}

# Writes the translated copies of the three named programs, the verbatim
# copybooks, the source baseline and the translation report into the build
# tree. The translator reads the named sources read-only; nothing here writes
# to base/src.
translate_sources() {
  local log="${LOGS_DIR}/translate.log"

  if ! : >"$log"; then
    die "$EXIT_TRANSLATE" "unable to write the translation log: ${log}"
  fi
  run_and_tee "$log" "$PY" "$TRANSLATOR" \
    --source-dir "$SOURCE_DIR" \
    --build-dir "$BUILD_DIR" \
    --statement-map "$STATEMENT_MAP" \
    --copybook-dir "$COPYBOOK_DIR"
  if ((RUN_STATUS != 0)); then
    die "$EXIT_TRANSLATE" \
      "the translator failed; its output is retained in ${log}" \
      "reproduce it with: ${PY} ${TRANSLATOR} --source-dir ${SOURCE_DIR} --build-dir ${BUILD_DIR} --statement-map ${STATEMENT_MAP} --copybook-dir ${COPYBOOK_DIR}" \
      "translated programs that still fail after the documented rules are applied are reported, not patched by hand"
  fi
  emit_step "translation log: ${log}"
}

# Checks that the generated source directory carries every file the compile
# stage reads: the three translated programs, the two source copybooks and the
# four harness copybooks.
assert_generated_sources() {
  local name="" path=""

  for name in "${GENERATED_SOURCES[@]}"; do
    path="${SRC_DIR}/${name}"
    if [[ ! -f "$path" ]]; then
      die "$EXIT_TRANSLATE" \
        "the translator left no ${name} in the generated source directory: ${path}" \
        "review ${LOGS_DIR}/translate.log for the step that did not complete"
    fi
    if [[ ! -s "$path" ]]; then
      die "$EXIT_TRANSLATE" \
        "the generated file is empty: ${path}" \
        "review ${LOGS_DIR}/translate.log for the step that did not complete"
    fi
  done
  emit_step "generated sources present: ${#GENERATED_SOURCES[@]} files in ${SRC_DIR}"
}

# Re-reads the SHA-256 baseline the translator recorded for the five named
# source artifacts. The baseline lists repository-relative paths and is checked
# from the repository root.
verify_source_baseline() {
  local baseline="${LOGS_DIR}/source-baseline.sha256"

  if [[ ! -f "$baseline" ]]; then
    die "$EXIT_TRANSLATE" \
      "the translator left no source baseline at ${baseline}" \
      "review ${LOGS_DIR}/translate.log for the step that did not complete"
  fi
  emit_step "source baseline: ${baseline}"
  if ! sha256sum -c --strict -- "$baseline"; then
    die "$EXIT_TRANSLATE" \
      "a named source artifact no longer matches the baseline in ${baseline}" \
      "restore the five named files under ${SOURCE_DIR} to their committed state and run this script again"
  fi
}

# Builds the records, translates the sources and checks both results.
stage_samples_and_translation() {
  emit_stage 2 "samples and translation"
  build_samples
  translate_sources
  assert_generated_sources
  verify_source_baseline
}

# --------------------------------------------------------------------------
# Stage 3: compile
# --------------------------------------------------------------------------
# Removes the modules and the driver of an earlier run, so an existence check
# after this stage can only pass on a module this run produced.
clear_binaries() {
  local entry="" program=""

  for entry in "${STUB_MODULES[@]}" "${PROGRAM_MODULES[@]}"; do
    program="${entry##*|}"
    rm -f -- "${BIN_DIR}/${program}.so"
  done
  rm -f -- "${BIN_DIR}/driver"
}

# Compiles the twelve stubs and the three translated programs as callable
# modules. Each module is named after its PROGRAM-ID, the name the dynamic
# CALL of a literal resolves through COB_LIBRARY_PATH. Compiler output,
# warnings included, is appended to the compile log and retained.
compile_modules() {
  local log="$1"
  local entry="" source="" program="" count=0

  for entry in "${STUB_MODULES[@]}"; do
    source="${entry%%|*}"
    program="${entry##*|}"
    log_command "$log" "$COBC" -m "${COBC_FLAG_LIST[@]}" \
      -I "$SRC_DIR" -o "${BIN_DIR}/${program}.so" "$source"
    run_and_tee "$log" "$COBC" -m "${COBC_FLAG_LIST[@]}" \
      -I "$SRC_DIR" -o "${BIN_DIR}/${program}.so" "$source"
    if ((RUN_STATUS != 0)); then
      die "$EXIT_COMPILE" \
        "compilation of module ${program} failed from ${source}" \
        "the compiler output is retained in ${log}" \
        "reproduce it with: ${COBC} -m ${COBC_FLAGS} -I ${SRC_DIR} -o ${BIN_DIR}/${program}.so ${source}"
    fi
    count=$((count + 1))
  done

  for entry in "${PROGRAM_MODULES[@]}"; do
    source="${SRC_DIR}/${entry%%|*}"
    program="${entry##*|}"
    log_command "$log" "$COBC" -m "${COBC_FLAG_LIST[@]}" \
      -I "$SRC_DIR" -o "${BIN_DIR}/${program}.so" "$source"
    run_and_tee "$log" "$COBC" -m "${COBC_FLAG_LIST[@]}" \
      -I "$SRC_DIR" -o "${BIN_DIR}/${program}.so" "$source"
    if ((RUN_STATUS != 0)); then
      die "$EXIT_COMPILE" \
        "compilation of translated program ${program} failed from ${source}" \
        "the compiler output is retained in ${log}" \
        "reproduce it with: ${COBC} -m ${COBC_FLAGS} -I ${SRC_DIR} -o ${BIN_DIR}/${program}.so ${source}" \
        "a translated program that still fails after the documented rules are applied is reported, not patched by hand"
    fi
    count=$((count + 1))
  done
  emit_step "modules compiled: ${count} into ${BIN_DIR}"
}

# Compiles the driver as an executable.
compile_driver() {
  local log="$1"

  log_command "$log" "$COBC" -x "${COBC_FLAG_LIST[@]}" \
    -I "$SRC_DIR" -o "${BIN_DIR}/driver" "$DRIVER_SOURCE"
  run_and_tee "$log" "$COBC" -x "${COBC_FLAG_LIST[@]}" \
    -I "$SRC_DIR" -o "${BIN_DIR}/driver" "$DRIVER_SOURCE"
  if ((RUN_STATUS != 0)); then
    die "$EXIT_COMPILE" \
      "compilation of the driver failed from ${DRIVER_SOURCE}" \
      "the compiler output is retained in ${log}" \
      "reproduce it with: ${COBC} -x ${COBC_FLAGS} -I ${SRC_DIR} -o ${BIN_DIR}/driver ${DRIVER_SOURCE}"
  fi
  emit_step "driver compiled: ${BIN_DIR}/driver"
}

# Checks that every module and the driver stand in the module directory, and
# records the module names the runtime is given as a resolution aid.
assert_binaries() {
  local entry="" program="" path="" count=0

  MODULE_PRELOAD=""
  for entry in "${STUB_MODULES[@]}" "${PROGRAM_MODULES[@]}"; do
    program="${entry##*|}"
    path="${BIN_DIR}/${program}.so"
    if [[ ! -f "$path" ]]; then
      die "$EXIT_COMPILE" \
        "the compiler reported success but left no module at ${path}" \
        "review ${LOGS_DIR}/compile.log for the module that did not complete"
    fi
    if [[ -n "$MODULE_PRELOAD" ]]; then
      MODULE_PRELOAD+=":"
    fi
    MODULE_PRELOAD+="$program"
    count=$((count + 1))
  done

  if [[ ! -x "${BIN_DIR}/driver" ]]; then
    die "$EXIT_COMPILE" \
      "the compiler reported success but left no executable driver at ${BIN_DIR}/driver" \
      "review ${LOGS_DIR}/compile.log for the step that did not complete"
  fi
  emit_step "modules present: ${count}; driver present"
}

# Compiles every module and the driver and checks the result.
stage_compile() {
  local log="${LOGS_DIR}/compile.log"

  emit_stage 3 "compile"
  if ! : >"$log"; then
    die "$EXIT_COMPILE" "unable to write the compile log: ${log}"
  fi
  emit_step "compile log: ${log}"
  clear_binaries
  compile_modules "$log"
  compile_driver "$log"
  assert_binaries
}

# --------------------------------------------------------------------------
# Stage 4: execute
# --------------------------------------------------------------------------
# Prints the meaning the driver attaches to an exit status.
driver_status_text() {
  case "$1" in
    0) printf '%s' "every check passed" ;;
    1) printf '%s' "the chain returned a code other than '00'" ;;
    2) printf '%s' "an abend was captured" ;;
    3) printf '%s' "a required capture is missing or inconsistent" ;;
    4) printf '%s' "a file input-output operation failed" ;;
    5) printf '%s' "a required environment item was not provided" ;;
    *) printf '%s' "a status the driver does not define" ;;
  esac
}

# Prints the value of one capture key, with trailing blanks and any carriage
# return removed. Fails when the key is absent from the file.
capture_value() {
  local file="$1" key="$2"
  local line="" value=""

  line="$(grep -m 1 -e "^${key}=" -- "$file" 2>/dev/null || true)"
  if [[ -z "$line" ]]; then
    return 1
  fi
  value="${line#"${key}="}"
  value="${value%$'\r'}"
  while [[ -n "$value" && "$value" == *[[:space:]] ]]; do
    value="${value%?}"
  done
  printf '%s' "$value"
}

# Checks that one capture key carries exactly the expected text.
assert_capture_text() {
  local label="$1" file="$2" key="$3" expected="$4"
  local actual=""

  if ! actual="$(capture_value "$file" "$key")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the capture file carries no ${key}" \
      "the capture file is ${file}" \
      "review the driver log beside it for the step that did not complete"
  fi
  if [[ "$actual" != "$expected" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${key} holds '${actual}' where '${expected}' is required" \
      "the capture file is ${file}" \
      "review the driver log beside it for the values the chain produced"
  fi
}

# Checks that one capture key carries the expected number. The comparison is
# numeric: a fixed-width value and an unpadded value of the same number both
# pass, and a value that is not a number fails.
assert_capture_number() {
  local label="$1" file="$2" key="$3" expected="$4"
  local actual=""

  if ! actual="$(capture_value "$file" "$key")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the capture file carries no ${key}" \
      "the capture file is ${file}" \
      "review the driver log beside it for the step that did not complete"
  fi
  if [[ ! "$actual" =~ ^[0-9]+$ ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${key} holds '${actual}', which is not a number" \
      "the capture file is ${file}"
  fi
  if ((10#$actual != expected)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${key} holds '${actual}' where ${expected} is required" \
      "the capture file is ${file}" \
      "review the driver log beside it for the values the chain produced"
  fi
}

# Exports the settings every case runs under: the module directory, the
# line-sequential setting the full-length post-chain record is written under,
# and the module names handed to the runtime as a resolution aid.
export_runtime_environment() {
  export COB_LIBRARY_PATH="$BIN_DIR"
  export COB_LS_FIXED=1
  export COB_PRE_LOAD="$MODULE_PRELOAD"
  emit_step "COB_LIBRARY_PATH=${COB_LIBRARY_PATH}"
  emit_step "COB_LS_FIXED=${COB_LS_FIXED}"
}

# Checks the post-chain record and the captures of one executed case: the
# record holds the full COMMAREA, the chain returned '00' without an abend,
# the driver passed every check of its own, the policy insert and the VSAM
# write were captured, and the product capture matches the product the case
# requests.
assert_case_results() {
  local label="$1" post="$2" capt="$3"
  local size="" motor="N" commercial="N"

  if [[ ! -f "$post" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the driver left no post-chain record at ${post}"
  fi
  if ! size="$(file_size "$post")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: unable to read the size of the post-chain record: ${post}"
  fi
  if [[ "$size" != "$RECORD_BYTES" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the post-chain record holds ${size} bytes: ${post}" \
      "${RECORD_BYTES} bytes are required, being 32,500 characters and one line feed" \
      "the offset decoding of the extraction step reads the record at that width"
  fi
  if [[ ! -s "$capt" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the driver left no capture content at ${capt}"
  fi

  case "$label" in
    01AMOT)
      motor="Y"
      commercial="N"
      ;;
    01ACOM)
      motor="N"
      commercial="Y"
      ;;
    *)
      die "$EXIT_EXECUTE" "no product expectation is defined for case ${label}"
      ;;
  esac

  assert_capture_text "$label" "$capt" "CA_RETURN_CODE" "00"
  assert_capture_text "$label" "$capt" "DRIVER_STATUS" "PASS"
  assert_capture_text "$label" "$capt" "ABEND_PRESENT" "N"
  assert_capture_text "$label" "$capt" "VSAM_PRESENT" "Y"
  assert_capture_number "$label" "$capt" "VSAM_LENGTH" "$VSAM_RECORD_LENGTH"
  assert_capture_text "$label" "$capt" "SQL_POLICY_PRESENT" "Y"
  assert_capture_text "$label" "$capt" "SQL_MOTOR_PRESENT" "$motor"
  assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_PRESENT" "$commercial"
  emit_step "case ${label}: post-chain record ${size} bytes, every capture check passed"
}

# Runs the driver once for one case and checks what it wrote. The identity and
# timestamp seeds are the deterministic values the preflight resolved.
execute_case() {
  local label="$1"
  local lower="" dir="" sample="" post="" capt="" log="" policy=""
  local status=0 assigned="" returned=""

  lower="$(case_lower "$label")"
  dir="${RUN_DIR}/${lower}"
  sample="${SAMPLES_DIR}/commarea_${lower}.dat"
  post="${dir}/commarea_post.dat"
  capt="${dir}/captures.txt"
  log="${dir}/driver.log"
  policy="$(policy_number_for "$label")"

  if [[ ! -f "$sample" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the generated sample record is missing: ${sample}" \
      "run this script without a case argument, or with ${label}, to generate it"
  fi

  rm -f -- "$post" "$capt"
  if ! : >"$log"; then
    die "$EXIT_EXECUTE" "case ${label}: unable to write the driver log: ${log}"
  fi

  export HARNESS_CASE="$label"
  export DD_SAMPLEFILE="$sample"
  export DD_POSTFILE="$post"
  export DD_CAPTFILE="$capt"
  export HARNESS_POLICY_NUMBER="$policy"
  export HARNESS_LASTCHANGED="$LASTCHANGED_SEED"

  emit_step "case ${label}: policy seed ${policy}, sample ${sample}"
  run_and_tee "$log" "${BIN_DIR}/driver"
  status="$RUN_STATUS"
  if ((status != 0)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: the driver exited ${status}: $(driver_status_text "$status")" \
      "the driver log is ${log}" \
      "the capture file, when the driver reached it, is ${capt}"
  fi

  assert_case_results "$label" "$post" "$capt"

  returned="$(capture_value "$capt" "CA_RETURN_CODE")"
  assigned="$(capture_value "$capt" "SQL_POLICY_ASSIGNED_NUMBER" || printf '%s' "unavailable")"
  SUMMARY_CASE_LINES+=(
    "  case ${label}: return code ${returned}, driver status ${status}, policy number ${assigned}"
    "    post-chain record: ${post}"
    "    captures:          ${capt}"
    "    driver log:        ${log}"
  )
}

# Executes every selected case under one exported runtime environment.
stage_execute() {
  local label=""

  emit_stage 4 "execute"
  export_runtime_environment
  for label in "${SELECTED_CASES[@]}"; do
    execute_case "$label"
  done
}

# --------------------------------------------------------------------------
# Stage 5: evidence and summary
# --------------------------------------------------------------------------
# Copies one retained file into the validation artifacts directory under the
# supplied name and records the copy for the summary.
retain_artifact() {
  local source="$1" name="$2"
  local target="${ARTIFACTS_DIR}/${name}"

  if [[ ! -f "$source" ]]; then
    die "$EXIT_EVIDENCE" \
      "the file to retain is missing: ${source}" \
      "review the stage logs under ${LOGS_DIR} for the step that did not complete"
  fi
  if ! cp -- "$source" "$target"; then
    die "$EXIT_EVIDENCE" "unable to copy ${source} to ${target}"
  fi
  SUMMARY_ARTIFACTS+=("$target")
}

# Copies the translation log, the compile log, the translation report, the
# source baseline and the driver log and capture file of every executed case
# into the validation artifacts directory. Case names keep the per-case files
# distinct.
stage_evidence() {
  local label="" lower=""

  emit_stage 5 "evidence"
  retain_artifact "${LOGS_DIR}/translate.log" "translate.log"
  retain_artifact "${LOGS_DIR}/compile.log" "compile.log"
  retain_artifact "${LOGS_DIR}/translation-report.json" "translation-report.json"
  retain_artifact "${LOGS_DIR}/source-baseline.sha256" "source-baseline.sha256"
  for label in "${SELECTED_CASES[@]}"; do
    lower="$(case_lower "$label")"
    retain_artifact "${RUN_DIR}/${lower}/driver.log" "driver_${lower}.log"
    retain_artifact "${RUN_DIR}/${lower}/captures.txt" "captures_${lower}.txt"
  done
  emit_step "artifacts retained: ${#SUMMARY_ARTIFACTS[@]} files in ${ARTIFACTS_DIR}"
}

# Prints the tool versions of the run, the selected cases with the code each
# returned, and the absolute path of every file the run produced.
print_summary() {
  local line="" stamp="" cobc_note=""

  stamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  cobc_note="pinned ${COBC_VERSION_PINNED}, ${COBC_VERSION_VERDICT}"

  emit_summary ""
  emit_summary "${PROGRAM}: == run summary =="
  emit_summary "  result:            PASS"
  emit_summary "  completed (UTC):   ${stamp}"
  emit_summary "  harness script:    ${SCRIPT_PATH}"
  emit_summary "  repository root:   ${REPO_ROOT}"
  emit_summary "  cobc:              ${COBC_VERSION} (${cobc_note}) at ${COBC}"
  emit_summary "  cobc flags:        ${COBC_FLAGS}"
  emit_summary "  python:            ${PYTHON_VERSION} at ${PY}"
  emit_summary "  cases:             $(join_with ", " "${SELECTED_CASES[@]}")"
  emit_summary "  timestamp seed:    ${LASTCHANGED_SEED}"
  for line in "${SUMMARY_CASE_LINES[@]}"; do
    emit_summary "$line"
  done
  emit_summary "  build outputs:"
  emit_summary "    generated sources: ${SRC_DIR}"
  emit_summary "    modules and driver: ${BIN_DIR}"
  emit_summary "    generated samples:  ${SAMPLES_DIR}"
  emit_summary "    stage logs:         ${LOGS_DIR}"
  emit_summary "  retained evidence:"
  for line in "${SUMMARY_ARTIFACTS[@]}"; do
    emit_summary "    ${line}"
  done
}

# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
main() {
  parse_args "$@"
  resolve_paths
  stage_preflight
  stage_samples_and_translation
  stage_compile
  stage_execute
  stage_evidence
  print_summary
  return "$EXIT_OK"
}

main "$@"

