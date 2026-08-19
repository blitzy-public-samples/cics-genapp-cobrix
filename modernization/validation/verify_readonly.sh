#!/usr/bin/env bash
#
# verify_readonly.sh - read-only scope gate for the modernization bridge.
#
# Checks that the five authorized GenApp source artifacts are byte-identical to
# the baseline embedded in this script, and that no pre-existing tracked
# repository file has been modified.
#
# Stages, in execution order:
#   preflight  "git" and "sha256sum" are on PATH and the working directory
#              resolves to a git work tree.
#   gate A     For each of the five baseline entries: the path exists, is a
#              regular file, and its recomputed SHA-256 and line count equal
#              the embedded baseline values.
#   gate B     "git status --porcelain -- base/" produces no output.
#   gate C     "git diff --name-only HEAD", after paths under the new-work
#              prefix "modernization/" are filtered out, lists no remaining
#              path.
#
# Exit codes:
#   0  every gate passed
#   1  SHA-256 or line-count mismatch, or a missing or irregular source file
#   2  the base/ working tree is not clean
#   3  a pre-existing tracked file outside modernization/ has been modified
#   4  environment or usage error
#
# Any non-zero code stops the fail-fast Makefile that invokes this script.
#
# Output: the same content is written to stdout and appended to the evidence
# log; --quiet suppresses stdout only. Failures also emit a one-line summary on
# stderr. The evidence log is the only file this script writes; it performs no
# network access and runs no git command that alters repository state.
#
# Options and per-option behavior are listed by --help.
#
# The harness topology this script belongs to is drawn in Figure 5 "Validation
# Harness Control Flow" in modernization/docs/architecture.md.
# Decisions taken for this script are recorded in
# modernization/docs/decision-log.md.

set -euo pipefail
IFS=$'\n\t'

# Baseline entries, formatted as "path|expected_line_count|expected_sha256".
readonly BASELINE=(
  "base/src/lgapol01.cbl|169|4dddd29539dd96aaec9f6885d3d62d19d40a1c6c888636623164bc5f5b232f6f"
  "base/src/lgapdb01.cbl|595|3d21ad353a03c63d05defc511372e14477613fa4c51068a51a84d3c840c29815"
  "base/src/lgapvs01.cbl|188|e0bca62eed2d6390852befdbaddd684833040c8be183d23f4fca368834709215"
  "base/src/lgcmarea.cpy|103|4ecc9ed8dbf0936a8b0738cbb03a947e937206100b0e34f749fbb9e0b03f701d"
  "base/src/lgpolicy.cpy|107|717c8f5c50738a2ef4d432e4b397e21bdc0423a9fc789246eb3360aa3f99eaa5"
)

# Repository-relative prefix holding this work. Gate C ignores paths under it,
# and the evidence log must resolve under it.
readonly NEW_WORK_PREFIX="modernization/"

# Evidence log used when --log is not supplied, relative to the repository root.
readonly DEFAULT_LOG_REL="modernization/validation/artifacts/readonly-check.log"

readonly EXIT_OK=0
readonly EXIT_SOURCE=1
readonly EXIT_BASE_DIRTY=2
readonly EXIT_TRACKED=3
readonly EXIT_ENV=4

readonly PROG="${0##*/}"

# Runtime state.
STAGE="unspecified"
LOG_REQUESTED=""
LOG_PATH=""
BASELINE_ONLY=0
QUIET=0
REPO_ROOT=""

usage() {
  cat <<'USAGE_TEXT'
Usage: verify_readonly.sh [options]

Checks that the five authorized GenApp source artifacts match the baseline
embedded in this script and that no pre-existing tracked repository file has
been modified.

Options:
  --stage NAME      Label recorded with this run, such as translate, compile,
                    execute, load, dbt, diff or final. Default: unspecified.
  --log PATH        Evidence log to append to. Resolves under modernization/;
                    any other location is rejected. Default:
                    modernization/validation/artifacts/readonly-check.log
  --baseline-only   Print the embedded baseline and exit 0. Runs no gate,
                    invokes no git command and writes no log.
  --quiet           Suppress stdout. The evidence log is still written.
  -h, --help        Print this message and exit 0.

Stages, in execution order:
  preflight  "git" and "sha256sum" are on PATH and the working directory
             resolves to a git work tree.
  gate A     For each of the five baseline entries: the path exists, is a
             regular file, and its recomputed SHA-256 and line count equal the
             embedded baseline values.
  gate B     "git status --porcelain -- base/" produces no output.
  gate C     "git diff --name-only HEAD", after paths under modernization/ are
             filtered out, lists no remaining path.

Exit codes:
  0  every gate passed
  1  SHA-256 or line-count mismatch, or a missing or irregular source file
  2  the base/ working tree is not clean
  3  a pre-existing tracked file outside modernization/ has been modified
  4  environment or usage error
USAGE_TEXT
}

# Writes one line to stdout and to the evidence log once the log is open.
emit() {
  local line="$1"
  if ((QUIET == 0)); then
    printf '%s\n' "$line"
  fi
  if [[ -n "$LOG_PATH" ]]; then
    printf '%s\n' "$line" >>"$LOG_PATH"
  fi
}

# Closes the run block and exits with the supplied code.
finish() {
  local code="$1"
  local verdict="$2"
  emit "verdict: ${verdict}"
  emit "exit_code: ${code}"
  emit "END readonly-check"
  emit ""
  exit "$code"
}

# Reports a usage error on stderr with the option list and exits 4.
fail_usage() {
  printf '%s: error: %s\n' "$PROG" "$1" >&2
  usage >&2
  exit "$EXIT_ENV"
}

# Reports an environment error on stderr, records it in the evidence log when
# the log is already open, and exits 4.
fail_env() {
  local message="$1"
  printf '%s: error: %s\n' "$PROG" "$message" >&2
  if [[ -n "$LOG_PATH" ]]; then
    emit "preflight: FAIL ${message}"
    emit "preflight result: FAIL"
    finish "$EXIT_ENV" "FAIL-ENVIRONMENT"
  fi
  exit "$EXIT_ENV"
}

parse_args() {
  while (($# > 0)); do
    case "$1" in
      --stage)
        (($# >= 2)) || fail_usage "--stage requires a value"
        STAGE="$2"
        shift 2
        ;;
      --stage=*)
        STAGE="${1#*=}"
        shift
        ;;
      --log)
        (($# >= 2)) || fail_usage "--log requires a value"
        LOG_REQUESTED="$2"
        shift 2
        ;;
      --log=*)
        LOG_REQUESTED="${1#*=}"
        shift
        ;;
      --baseline-only)
        BASELINE_ONLY=1
        shift
        ;;
      --quiet)
        QUIET=1
        shift
        ;;
      -h | --help)
        usage
        exit "$EXIT_OK"
        ;;
      *)
        fail_usage "unknown option: $1"
        ;;
    esac
  done
  [[ -n "$STAGE" ]] || fail_usage "--stage requires a non-empty value"
  [[ -z "$LOG_REQUESTED" || "$LOG_REQUESTED" != -* ]] ||
    fail_usage "--log requires a path value, received: ${LOG_REQUESTED}"
}

require_tool() {
  local tool="$1"
  if ! command -v "$tool" >/dev/null 2>&1; then
    fail_env "required tool not found on PATH: ${tool}"
  fi
}

# Moves to the repository root. Every later path resolves from there,
# independently of the caller's working directory.
resolve_repo_root() {
  local inside="" root=""
  if ! inside="$(git rev-parse --is-inside-work-tree 2>/dev/null)" ||
    [[ "$inside" != "true" ]]; then
    fail_env "the working directory does not resolve to a git work tree"
  fi
  if ! root="$(git rev-parse --show-toplevel 2>/dev/null)" || [[ -z "$root" ]]; then
    fail_env "unable to resolve the repository root"
  fi
  if [[ ! -d "$root" ]]; then
    fail_env "the resolved repository root is not a directory: ${root}"
  fi
  if ! cd -- "$root"; then
    fail_env "unable to change directory to the repository root: ${root}"
  fi
  REPO_ROOT="$root"
}

# Validates the requested log location, creates its directory and opens the log
# for appending. Validation precedes directory creation.
open_log() {
  local requested="${LOG_REQUESTED:-$DEFAULT_LOG_REL}"
  local rel="" dir=""

  if [[ "$requested" == /* ]]; then
    case "$requested" in
      "${REPO_ROOT}/"*) rel="${requested#"${REPO_ROOT}/"}" ;;
      *) fail_env "--log path lies outside the repository: ${requested}" ;;
    esac
  else
    rel="$requested"
  fi

  if [[ "/${rel}/" == */../* ]]; then
    fail_env "--log path must not contain a '..' component: ${requested}"
  fi
  if [[ "$rel" == */ ]]; then
    fail_env "--log path must name a file, not a directory: ${requested}"
  fi
  case "$rel" in
    "${NEW_WORK_PREFIX}"*) : ;;
    *) fail_env "--log path must resolve under ${NEW_WORK_PREFIX}: ${requested}" ;;
  esac

  dir="${rel%/*}"
  if ! mkdir -p -- "$dir"; then
    fail_env "unable to create the evidence log directory: ${dir}"
  fi
  if ! : >>"$rel"; then
    fail_env "unable to append to the evidence log: ${rel}"
  fi
  LOG_PATH="$rel"
}

# Records the embedded baseline as one line per entry.
print_baseline() {
  local row="" path="" lines="" sha="" line=""
  emit "baseline (path, lines, sha256):"
  for row in "${BASELINE[@]}"; do
    IFS='|' read -r path lines sha <<<"$row"
    printf -v line '  %-22s %5s  %s' "$path" "$lines" "$sha"
    emit "$line"
  done
}

# Gate A: per-file presence, regularity, SHA-256 and line count.
gate_a() {
  local row="" path="" expected_lines="" expected_sha=""
  local actual_lines="" actual_sha="" digest="" raw="" line=""
  local failures=0

  emit "gate A source integrity:"
  for row in "${BASELINE[@]}"; do
    IFS='|' read -r path expected_lines expected_sha <<<"$row"

    if [[ ! -e "$path" ]]; then
      printf -v line \
        '  FAIL %s missing expected_lines=%s actual_lines=%s expected_sha256=%s actual_sha256=%s' \
        "$path" "$expected_lines" "(absent)" "$expected_sha" "(absent)"
      emit "$line"
      failures=$((failures + 1))
      continue
    fi
    if [[ ! -f "$path" ]]; then
      printf -v line \
        '  FAIL %s not a regular file expected_lines=%s actual_lines=%s expected_sha256=%s actual_sha256=%s' \
        "$path" "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      emit "$line"
      failures=$((failures + 1))
      continue
    fi
    if ! digest="$(sha256sum -- "$path" 2>/dev/null)"; then
      printf -v line \
        '  FAIL %s unreadable expected_lines=%s actual_lines=%s expected_sha256=%s actual_sha256=%s' \
        "$path" "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      emit "$line"
      failures=$((failures + 1))
      continue
    fi
    actual_sha="${digest%% *}"
    if ! raw="$(wc -l <"$path" 2>/dev/null)"; then
      printf -v line \
        '  FAIL %s unreadable expected_lines=%s actual_lines=%s expected_sha256=%s actual_sha256=%s' \
        "$path" "$expected_lines" "(not read)" "$expected_sha" "$actual_sha"
      emit "$line"
      failures=$((failures + 1))
      continue
    fi
    actual_lines="${raw//[[:space:]]/}"

    if [[ "$actual_sha" == "$expected_sha" && "$actual_lines" == "$expected_lines" ]]; then
      printf -v line '  PASS %s expected_lines=%s actual_lines=%s sha256=%s' \
        "$path" "$expected_lines" "$actual_lines" "$actual_sha"
      emit "$line"
    else
      printf -v line \
        '  FAIL %s expected_lines=%s actual_lines=%s expected_sha256=%s actual_sha256=%s' \
        "$path" "$expected_lines" "$actual_lines" "$expected_sha" "$actual_sha"
      emit "$line"
      failures=$((failures + 1))
    fi
  done

  if ((failures > 0)); then
    printf -v line 'gate A result: FAIL (%d of %d baseline entries did not match)' \
      "$failures" "${#BASELINE[@]}"
    emit "$line"
    printf '%s: error: gate A source integrity failed for %d of %d baseline entries\n' \
      "$PROG" "$failures" "${#BASELINE[@]}" >&2
    return 1
  fi
  printf -v line 'gate A result: PASS (%d of %d baseline entries matched)' \
    "${#BASELINE[@]}" "${#BASELINE[@]}"
  emit "$line"
  return 0
}

# Gate B: the base/ working tree carries no reported change.
gate_b() {
  local output="" line=""

  emit "gate B base working tree clean:"
  if ! output="$(git status --porcelain -- base/ 2>&1)"; then
    fail_env "git status --porcelain -- base/ did not complete: ${output}"
  fi

  if [[ -z "$output" ]]; then
    emit "  git status --porcelain -- base/ produced no output"
    emit "gate B result: PASS"
    return 0
  fi

  emit "  git status --porcelain -- base/ reported:"
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    emit "    ${line}"
  done <<<"$output"
  emit "gate B result: FAIL"
  printf '%s: error: gate B the base/ working tree is not clean\n' "$PROG" >&2
  return 1
}

# Gate C: no tracked path outside the new-work prefix differs from HEAD.
gate_c() {
  local output="" line="" entry="" count=0
  local remaining=()

  emit "gate C no pre-existing tracked modification:"
  if ! output="$(git diff --name-only HEAD 2>&1)"; then
    fail_env "git diff --name-only HEAD did not complete: ${output}"
  fi

  emit "  git diff --name-only HEAD raw output:"
  if [[ -z "$output" ]]; then
    emit "    (no tracked modification)"
  else
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      emit "    ${line}"
      case "$line" in
        "${NEW_WORK_PREFIX}"*) : ;;
        *) remaining+=("$line") ;;
      esac
    done <<<"$output"
  fi

  count="${#remaining[@]}"
  printf -v line '  tracked paths outside %s: %d' "$NEW_WORK_PREFIX" "$count"
  emit "$line"

  if ((count == 0)); then
    emit "gate C result: PASS"
    return 0
  fi

  for entry in "${remaining[@]}"; do
    emit "    ${entry}"
  done
  emit "gate C result: FAIL"
  printf '%s: error: gate C %d pre-existing tracked file(s) outside %s modified\n' \
    "$PROG" "$count" "$NEW_WORK_PREFIX" >&2
  return 1
}

main() {
  parse_args "$@"

  if ((BASELINE_ONLY == 1)); then
    print_baseline
    exit "$EXIT_OK"
  fi

  require_tool git
  resolve_repo_root
  open_log

  local timestamp=""
  if ! timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; then
    fail_env "unable to read the current UTC time"
  fi

  emit "BEGIN readonly-check"
  emit "stage: ${STAGE}"
  emit "timestamp_utc: ${timestamp}"
  emit "repository_root: ${REPO_ROOT}"
  emit "evidence_log: ${LOG_PATH}"
  print_baseline

  require_tool sha256sum
  emit "preflight result: PASS"

  gate_a || finish "$EXIT_SOURCE" "FAIL-SOURCE-INTEGRITY"
  gate_b || finish "$EXIT_BASE_DIRTY" "FAIL-BASE-WORKTREE-DIRTY"
  gate_c || finish "$EXIT_TRACKED" "FAIL-PREEXISTING-TRACKED-MODIFICATION"

  finish "$EXIT_OK" "PASS"
}

main "$@"
