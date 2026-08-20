#!/usr/bin/env bash
#
# verify_readonly.sh - read-only scope gate for the modernization bridge.
#
# Checks that the five authorized GenApp source artifacts are byte-identical to
# the baseline embedded in this script, and that no pre-existing tracked
# repository file has been modified.
#
# Milestone status: this script runs standalone at this milestone. The
# modernization/Makefile that will invoke it and the decision log referenced
# below are planned deliverables, not present at this milestone.
#
# Stages, in execution order:
#   preflight  "git", "sha256sum", "wc", "date", "mkdir" and "stat" are on
#              PATH, a descriptor this shell holds can be inspected through
#              "/dev/fd/<number>", and the working directory resolves to a git
#              work tree.
#   gate A     For each of the five baseline entries: neither the path nor any
#              of its parent components is a symbolic link, the path exists and
#              reports a regular file without being followed, the path still
#              reports a regular file when it is re-read with shell builtins
#              immediately before the open, the file is opened once onto a
#              descriptor held for that entry, the path reports a regular file
#              once more after that open, that descriptor reports a regular
#              file with the same inode and device as the path, the SHA-256 and
#              the line count are both read through that descriptor, the path
#              still reports that inode and device after both measurements, and
#              each measurement equals the embedded baseline value.
#   gate B     "git status --porcelain -- base/" produces no output.
#   gate C     "git diff --name-only HEAD", after paths under the new-work
#              prefix "modernization/" are filtered out, lists no remaining
#              path.
#
# Evidence log location rules, all applied before anything is written:
#   - a supplied path is not empty, and an empty --log value never falls back to
#     the default;
#   - the path resolves inside the repository root, and that root is resolved
#     physically;
#   - its directory is exactly modernization/validation/artifacts, with no
#     sub-directory, no trailing "/" and no ".." component;
#   - its basename ends in ".log" and holds only letters, digits, ".", "_"
#     and "-";
#   - no component of that directory chain and no existing log is a symbolic
#     link, and an existing log is a regular file;
#   - missing directory components of that chain are created one level at a
#     time, and the directory's physical path is confirmed before the log is
#     opened;
#   - the path is re-read with shell builtins immediately before the open, with
#     no other command in between, and a path that is a symbolic link or that
#     exists as anything other than a regular file at that moment is rejected
#     without being opened;
#   - the log is opened once, for appending, onto a descriptor that stays open
#     for the whole run, and before any line is written the path reports a
#     regular file with exactly one hard link and that descriptor reports a
#     regular file with the same inode and device as the path;
#   - every line of the run is written through that descriptor, never through
#     the path a second time, and the descriptor is closed when the run block
#     ends.
# A rejected location exits 4, names the offending path and the rule it broke,
# and writes nothing. An append through the held descriptor that fails is
# reported on stderr only, names the log, and exits 4 without a further write
# attempt and without a further evidence line.
#
# Substitution of a path between its check and its open, for the evidence log
# and for every gate A entry:
#   - a path that is a symbolic link, that exists as something other than a
#     regular file, or that is reached through a symbolic link component is
#     rejected before any open, and no file is created;
#   - the last check before every open reads the path with shell builtins only,
#     so no other command runs between that check and the open; a substitution
#     seen by that check stops the run before the open as "replaced by a <type>
#     before it was opened", or as "removed before it was opened" when the path
#     is gone, with exit 4 for the log and exit 1 on the entry's gate A FAIL
#     line;
#   - a substitution that lands between the open and the next status read is
#     reported after the open as "became a <type> after it was validated", with
#     exit 4 for the log, which writes no line, and exit 1 for a gate A entry,
#     which is not measured;
#   - a substitution that leaves a regular file at the name is reported by the
#     comparison of the descriptor with the name, and a substitution that lands
#     while a gate A entry is measured is reported by the status of the path
#     read after both measurements;
#   - an append open that follows a symbolic link planted inside that window
#     creates an empty file at the link target and no line is ever written to
#     it; a read open that follows one reads the link target and no measurement
#     is taken from it;
#   - a directory component of the evidence log that becomes a symbolic link, or
#     that stops resolving to its place under the repository root, is reported
#     after the open as "directory component became a symbolic link" or
#     "directory resolves to <path>", with exit 4 and no line written, and a
#     parent component of a gate A entry that becomes a symbolic link is
#     reported as "parent became a symbolic link (<component>) after it was
#     validated", with exit 1 and no measurement taken;
#   - a path substituted for a FIFO inside that window blocks that open: the run
#     stops there and reports nothing further.
# Decisions taken about the open sequence are recorded in
# modernization/docs/decision-log.md.
#
# Externally supplied text - the --stage label, the requested and resolved log
# paths, the repository root and every git output line - is emitted with
# control bytes, non-ASCII bytes and backslashes replaced by "\xNN" escapes, so
# one supplied value occupies exactly one output line.
#
# Exit codes:
#   0  every gate passed
#   1  SHA-256 or line-count mismatch, or a missing, irregular or symlinked
#      source file, or a source whose type changed between its checks and its
#      open, or a source whose inode changed while it was measured
#   2  the base/ working tree is not clean
#   3  a pre-existing tracked file outside modernization/ has been modified
#   4  environment or usage error, including a rejected evidence log location, a
#      log whose type changed between its checks and its open, and a failed
#      append to the evidence log
#   5  --self-test recorded at least one failing case
#
# Any non-zero code will stop the planned fail-fast modernization/Makefile once
# that Makefile invokes this script.
#
# Accepted argument values:
#   --stage  one to 64 characters, starting with a letter or a digit and
#            continuing with letters, digits, ".", "_" or "-". Any other value,
#            including an empty value or one carrying whitespace, a control
#            character or a shell metacharacter, is a usage error and exits 4.
#   --log    a path that names a file directly inside
#            modernization/validation/artifacts/: that directory, then one name
#            starting with a letter or a digit and continuing with letters,
#            digits, ".", "_" or "-". No path below a subdirectory of that
#            directory is accepted, so the only directory this script ever
#            creates is modernization/validation/artifacts/ itself. An absolute
#            path is accepted when it lies under the repository root; a relative
#            path resolves from the repository root. A path carrying a control
#            character, a ".." component, a trailing "/", a character outside
#            "A-Z a-z 0-9 . _ - /", a resolved location outside that directory,
#            a name below a subdirectory of it, a symbolic link, or an existing
#            non-regular file is rejected before any directory is created or any
#            file is opened, and exits 4. The evidence directory is then entered
#            from the resolved repository root one component at a time: a
#            component that is a symbolic link is refused, a missing component
#            is created by a single-component "mkdir" that does not traverse a
#            symbolic link holding that name, a name that appears while that
#            creation runs is accepted once it is re-read with shell builtins
#            and reports a directory that is not a symbolic link, a name that
#            reads as a symbolic link at that moment is refused, a name that
#            reads as anything else exits 4, that tool's own stderr never
#            reaches the caller, and the directory the process holds after each
#            step must equal the accumulated absolute path. The log is opened
#            once for appending on one descriptor, addressed by its name alone
#            inside that entered directory, and the object that descriptor holds
#            must be a regular file, must carry exactly one link, must still
#            resolve inside modernization/validation/artifacts/, and must not be
#            the file any baseline source path names. That object must also be
#            the exact entry the run resolved: the path the descriptor reports
#            equals the resolved requested path character for character, and the
#            device and inode of the requested entry, read without following a
#            symbolic link, equal the device and inode of the object the
#            descriptor holds. That descriptor is inspected through
#            "/dev/fd/<number>" alone, and a shell that cannot resolve that name
#            is reported by the preflight as an environment error rather than as
#            a finding. Every component from the resolved repository root down
#            to and including the log entry must, in every run, also be a
#            directory entry that is not a symbolic link. A descriptor that
#            fails one of those checks is closed and no entry is ever removed:
#            an entry a rejected open created is left exactly as it stands, so
#            no run of this script can delete a file it did not prove it owns.
#            Nothing is appended, and the run exits 4.
#
# Generated-output policy: one policy governs every path this bridge writes. A
# generated record or translated copy resolves inside
# modernization/harness/build/ and a generated evidence log resolves inside
# modernization/validation/artifacts/. Every destination is canonicalised
# through its symbolic links before anything is created, a symbolic link and an
# existing non-regular target are refused, no authored or source path is
# reachable, and every value carried into a diagnostic or an evidence record is
# escaped to one control-free line. An evidence log names one file directly
# inside modernization/validation/artifacts/, that directory is created and
# entered one component at a time so each creation and the open address a single
# name in the directory the process holds rather than a multi-component
# pathname, and the log is additionally validated after it is opened: the opened
# object is a single-link regular file inside
# modernization/validation/artifacts/, it is the exact entry the run resolved as
# proven by the descriptor's own reported path and by the device and inode of
# that entry read without following a symbolic link, and every later record is
# written through that one descriptor rather than through the pathname again. A
# rejected evidence log is never removed: the descriptor is closed, nothing is
# appended and the entry is left exactly as it stands, so this script deletes no
# file outside its own throwaway self-test tree.
# This script enforces the policy for evidence logs;
# modernization/extraction/build_sample_commarea.py enforces it for generated
# records.
#
# Output: the same content is written to stdout and appended to the evidence
# log; --quiet suppresses stdout only. Each record reaches the log before it
# reaches stdout, and a stdout that can no longer be written is reported once on
# stderr and then silenced, leaving the evidence log complete and the exit status
# reporting the gate outcome. Every emitted record passes through one sanitizer
# that replaces control characters with "?", so one record is always one line.
# Failures also emit a one-line summary on stderr. The evidence log is
# the only file this script writes, every append reaches it through the one
# descriptor opened for it and closed when the run finishes; it performs no
# network access and runs no git command that alters repository state.
#
# --self-test builds a throwaway git work tree under a temporary directory,
# copies the five source artifacts and this script into it, commits them, and
# then asserts one case at a time: rejected log locations, a symlinked log
# target, a symlinked log directory, a hard-linked log target, a FIFO log
# target, a log whose open cannot succeed, a log directory whose mode is
# reduced, a log replaced between its open and its status read, a log whose name
# becomes a symbolic link and a log whose name becomes a FIFO between its open
# and its status read, a log whose append does not complete, the inode of a log
# across two runs, an evidence directory that appears while this run creates it,
# an evidence directory a symbolic link takes over while this run creates it, a
# committed symlinked source, a committed symlinked source directory, a FIFO and
# a directory in place of sources, a committed source content change, a removed
# source, a source whose line count and digest both moved, a source replaced
# between its status read and its open, a source replaced by a symbolic link and
# a source replaced by a FIFO between its status read and its open, a source
# whose name becomes a symbolic link and a source whose name becomes a FIFO
# between its open and the status read that follows it, a source replaced while
# it is measured through its descriptor, an unclean base/ working tree, a
# modified tracked file outside modernization/, one missing required tool per
# case, a failing status read of a held descriptor, an injected --stage label,
# clean positive runs, and the declared case count. The substitution cases and
# the descriptor-status case drive their fault through a "stat" shim placed
# ahead of PATH that otherwise forwards every call to the real tool. The two
# evidence-directory cases drive theirs through a "mkdir" shim placed ahead of
# PATH that places one name, writes its own stderr line and reports a failure
# for the single-component creation it selects, and that otherwise forwards
# every call to the real tool. The incomplete append is driven by a file-size
# limit with SIGXFSZ ignored. No case drives a substitution into the window that
# holds no command, between a builtin check and the open that follows it.
# It prints one PASS or FAIL line per case plus a count summary, checks after
# every case that nothing was written outside the throwaway tree, removes that
# tree on exit, and writes no path in the repository it is started from. It runs
# alone: no other option may accompany it.
#
# Options and per-option behavior are listed by --help.
#
# The harness topology this script belongs to is drawn in
# Figure 5 — Validation Harness Control Flow in modernization/docs/architecture.md.
# Decisions taken for this script will be recorded in
# modernization/docs/decision-log.md (planned deliverable; not present at this milestone).

set -euo pipefail
IFS=$'\n\t'

# One byte is one character for the escaper, and every external tool reports in
# the unlocalized C form.
export LC_ALL=C

# Turns a closed stdout reader into a write error for the writing command
# instead of a signal that ends the script, so stdout_write reports it and the
# evidence log still receives the whole run block.
trap '' PIPE

# Baseline entries, formatted as "path|expected_line_count|expected_sha256".
readonly BASELINE=(
  "base/src/lgapol01.cbl|169|4dddd29539dd96aaec9f6885d3d62d19d40a1c6c888636623164bc5f5b232f6f"
  "base/src/lgapdb01.cbl|595|3d21ad353a03c63d05defc511372e14477613fa4c51068a51a84d3c840c29815"
  "base/src/lgapvs01.cbl|188|e0bca62eed2d6390852befdbaddd684833040c8be183d23f4fca368834709215"
  "base/src/lgcmarea.cpy|103|4ecc9ed8dbf0936a8b0738cbb03a947e937206100b0e34f749fbb9e0b03f701d"
  "base/src/lgpolicy.cpy|107|717c8f5c50738a2ef4d432e4b397e21bdc0423a9fc789246eb3360aa3f99eaa5"
)

# Repository-relative prefix holding this work. Gate C ignores paths under it.
readonly NEW_WORK_PREFIX="modernization/"

# The only directory an evidence log may live in, relative to the repository
# root. No sub-directory of it is accepted.
readonly LOG_DIR_REL="modernization/validation/artifacts"

# Evidence log used when --log is not supplied, relative to the repository root.
readonly DEFAULT_LOG_REL="${LOG_DIR_REL}/readonly-check.log"

# External tools every verification run invokes, in first-use order. A missing
# entry is an environment error, reported before the evidence log is opened.
readonly REQUIRED_TOOLS=(git sha256sum wc date mkdir stat)

# External tools --self-test invokes in addition to REQUIRED_TOOLS.
readonly SELF_TEST_TOOLS=(mktemp cp ln rm mv mkfifo chmod)

# Accepted --stage value: one to 64 characters, leading alphanumeric, then
# alphanumerics, ".", "_" or "-".
readonly STAGE_PATTERN='^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$'

# Accepted --log characters: an optional leading "/", a leading alphanumeric,
# then alphanumerics, ".", "_", "-" or "/".
readonly LOG_PATH_PATTERN='^/?[A-Za-z0-9][A-Za-z0-9._/-]*$'

# Accepted evidence log name: the one path component that follows
# modernization/validation/artifacts/, a leading alphanumeric then
# alphanumerics, ".", "_" or "-". No "/" is accepted, so no path below a
# subdirectory of the evidence directory can be named.
readonly LOG_NAME_PATTERN='^[A-Za-z0-9][A-Za-z0-9._-]*$'

# Longest accepted --stage value, in characters.
readonly STAGE_MAX_LENGTH=64

readonly EXIT_OK=0
readonly EXIT_SOURCE=1
readonly EXIT_BASE_DIRTY=2
readonly EXIT_TRACKED=3
readonly EXIT_ENV=4
readonly EXIT_SELF_TEST=5

readonly PROG="${0##*/}"

# Physical path of this script, resolved before any directory change so that
# --self-test can copy the running file.
SCRIPT_PATH=""

# Runtime state.
STAGE="unspecified"
STAGE_SET=0
LOG_REQUESTED=""
LOG_SET=0
LOG_PATH=""

# Descriptor the evidence log is held open on for the whole run, or -1 while no
# log is open. Every evidence line is written through it.
LOG_FD=-1

# Descriptor one gate A baseline entry is held open on while it is measured, or
# -1 between entries.
SOURCE_FD=-1

# 0 while stdout can be written, 1 once a write to it has failed. A lost stdout
# reader silences later stdout output and changes no gate outcome.
STDOUT_FAILED=0

BASELINE_ONLY=0
QUIET=0
SELF_TEST=0
REPO_ROOT=""
SANITIZED=""

# Prints the option and exit-code summary. Uses shell builtins only, so it
# stays available when no external tool is on PATH.
usage() {
  local line=""
  while IFS= read -r line; do
    printf '%s\n' "$line"
  done <<'USAGE_TEXT'
Usage: verify_readonly.sh [options]

Checks that the five authorized GenApp source artifacts match the baseline
embedded in this script and that no pre-existing tracked repository file has
been modified.

Options:
  --stage NAME      Label recorded with this run, such as translate, compile,
                    execute, load, dbt, diff or final. Control bytes, non-ASCII
                    bytes and backslashes in the label are emitted as "\xNN"
                    escapes. Default: unspecified.
  --log PATH        Evidence log to append to. Must resolve to a ".log" file
                    directly inside modernization/validation/artifacts within
                    this repository, reached without a symbolic link, and must
                    be a regular file with exactly one hard link; any other
                    location is rejected with exit 4 and nothing is written.
                    The log is opened once onto a descriptor held for the whole
                    run, every line is written through that descriptor, and an
                    append that fails is reported on stderr only and exits 4. A
                    path that stops being a regular file between its checks and
                    its open, or between that open and the status read that
                    follows it, is reported with exit 4 and no line is written.
                    Default:
                    modernization/validation/artifacts/readonly-check.log
  --baseline-only   Print the embedded baseline and exit 0. Runs no gate,
                    invokes no external tool and writes no log.
  --quiet           Suppress stdout. The evidence log is still written.
  --self-test       Run the built-in negative and positive cases in a throwaway
                    git work tree, print one PASS or FAIL line per case with a
                    count summary, and write nothing in this repository. Exits
                    0 when every case passes and 5 when any case fails. Runs
                    alone: no other option may accompany it.
  -h, --help        Print this message and exit 0.

Stages, in execution order:
  preflight  "git", "sha256sum", "wc", "date", "mkdir" and "stat" are on PATH,
             a descriptor this shell holds can be inspected through
             "/dev/fd/<number>", and the working directory resolves to a git
             work tree.
  gate A     For each of the five baseline entries: neither the path nor any of
             its parent components is a symbolic link, the path exists and
             reports a regular file without being followed, it still reports a
             regular file when it is re-read immediately before the open and
             once more after it, the file is opened once onto a held descriptor
             that reports the same inode and device as the path, the SHA-256 and
             the line count are read through that descriptor, the path still
             reports that inode and device afterwards, and each measurement
             equals the embedded baseline value.
  gate B     "git status --porcelain -- base/" produces no output.
  gate C     "git diff --name-only HEAD", after paths under modernization/ are
             filtered out, lists no remaining path.

Substitution of a path between its check and its open:
  A path that is a symbolic link, that exists as something other than a regular
  file, or that is reached through a symbolic link component is rejected before
  any open, and no file is created. The last check before every open reads the
  path with shell builtins only, so no other command runs between that check and
  the open; a substitution seen by that check stops the run before the open as
  "replaced by a <type> before it was opened", or as "removed before it was
  opened" when the path is gone. A substitution that lands between the open and
  the status read that follows it is reported afterwards as "became a <type>
  after it was validated": the evidence log exits 4 without writing a line, and
  a gate A entry exits 1 without being measured. An append open that follows a
  symbolic link planted inside that window creates an empty file at the link
  target and writes no line to it. A directory component of the evidence log
  that becomes a symbolic link, or that stops resolving to its place under the
  repository root, is reported after the open and no line is written. A path
  substituted for a FIFO inside that window blocks that open and the run stops
  there.

Exit codes:
  0  every gate passed
  1  SHA-256 or line-count mismatch, or a missing, irregular or symlinked
     source file, or a source whose type changed between its checks and its
     open, or a source whose inode changed while it was measured
  2  the base/ working tree is not clean
  3  a pre-existing tracked file outside modernization/ has been modified
  4  environment or usage error, including a rejected evidence log location, a
     log whose type changed between its checks and its open, and a failed
     append to the evidence log
  5  --self-test recorded at least one failing case
USAGE_TEXT
}

# Prints the supplied value as one printable single-byte line: bytes 0x20 to
# 0x7E other than "\" are kept, and every other byte - carriage return, line
# feed, tab, any other control byte, DEL and any non-ASCII byte - plus "\"
# itself becomes "\xNN" with NN the upper-case hexadecimal byte value. Uses
# shell builtins only.
sanitize() {
  local input="$1" out="" ch="" hex="" code=0 i=0

  for ((i = 0; i < ${#input}; i++)); do
    ch="${input:i:1}"
    printf -v code '%d' "'${ch}"
    code=$((code & 255))
    if ((code >= 32 && code <= 126 && code != 92)); then
      out+="$ch"
    else
      printf -v hex '%02X' "$code"
      out+="\\x${hex}"
    fi
  done

  printf '%s' "$out"
}

# Replaces every control character in "$1" with "?" and stores the result in
# SANITIZED. Every record written to stdout, to the evidence log or to stderr
# passes through this function in addition to the per-value escaping applied by
# its caller, so no record can carry a control character or span more than one
# line. The substitution leaves every printable byte, including the backslash of
# an escape already produced by sanitize, exactly as it found it.
sanitize_line() {
  SANITIZED="${1//[[:cntrl:]]/?}"
}

# Succeeds when the supplied "stat -c %F" value names a regular file. "stat"
# reports a zero-length regular file as "regular empty file", and both forms
# are accepted.
is_regular_kind() {
  case "$1" in
    "regular file" | "regular empty file") return 0 ;;
    *) return 1 ;;
  esac
}

# Prints the reason a path is rejected by the check made immediately before it
# is opened, naming the type the path reports at that moment in the vocabulary
# "stat -c %F" uses. Reads the type without following a symbolic link and with
# shell builtins only, and is called on the rejection path alone, after the open
# has been skipped.
preopen_change_reason() {
  local path="$1"

  if [[ -L "$path" ]]; then
    printf '%s' "replaced by a symbolic link before it was opened"
  elif [[ ! -e "$path" ]]; then
    printf '%s' "removed before it was opened"
  elif [[ -d "$path" ]]; then
    printf '%s' "replaced by a directory before it was opened"
  elif [[ -p "$path" ]]; then
    printf '%s' "replaced by a fifo before it was opened"
  elif [[ -S "$path" ]]; then
    printf '%s' "replaced by a socket before it was opened"
  elif [[ -b "$path" ]]; then
    printf '%s' "replaced by a block special file before it was opened"
  elif [[ -c "$path" ]]; then
    printf '%s' "replaced by a character special file before it was opened"
  else
    printf '%s' "replaced before it was opened"
  fi
}

# Closes the held evidence-log descriptor. Writes nothing and is a no-op when
# no log is open.
close_log() {
  if ((LOG_FD >= 0)); then
    exec {LOG_FD}>&-
    LOG_FD=-1
  fi
}

# Closes the held gate A descriptor. Writes nothing and is a no-op when no
# baseline entry is open.
close_source() {
  if ((SOURCE_FD >= 0)); then
    exec {SOURCE_FD}<&-
    SOURCE_FD=-1
  fi
}

# Reports a failed append to the evidence log on stderr and exits 4. Makes no
# further attempt on the log and emits no further evidence line.
fail_log_write() {
  LOG_FD=-1
  printf '%s: error: evidence log append did not complete: %s\n' \
    "$PROG" "$(sanitize "$LOG_PATH")" >&2
  exit "$EXIT_ENV"
}

# Writes one line to stdout alone. Nothing is written while --quiet is in
# effect or after a stdout write has already failed; a failed write is reported
# once on stderr, latched in STDOUT_FAILED and silences later stdout output. The
# evidence log, the gate outcome and the exit status are unaffected, so a reader
# that closes early cannot change the verdict this run reports.
stdout_write() {
  if ((QUIET == 1)) || ((STDOUT_FAILED == 1)); then
    return 0
  fi
  if ! printf '%s\n' "$1" 2>/dev/null; then
    STDOUT_FAILED=1
    printf '%s: error: stdout could not be written; the run continues, the evidence log is unaffected and the exit code still reports the gate outcome\n' \
      "$PROG" >&2
  fi
}

# Appends one line to the evidence log, when one is open, and then writes the
# same line to stdout. The log receives the line first, so a record that reaches
# stdout is already recorded. An append that does not complete ends the run with
# exit 4; a stdout write that does not complete is reported once and the run
# continues.
emit() {
  sanitize_line "$1"
  local line="$SANITIZED"
  if ((LOG_FD >= 0)); then
    printf '%s\n' "$line" >&"$LOG_FD" || fail_log_write
  fi
  stdout_write "$line"
}

# Closes the run block, releases the evidence log and exits with the supplied
# code.
finish() {
  local code="$1"
  local verdict="$2"
  local -a block=("verdict: ${verdict}" "exit_code: ${code}" "END readonly-check" "")
  local -a records=()
  local line=""

  for line in "${block[@]}"; do
    sanitize_line "$line"
    records+=("$SANITIZED")
  done
  if ((LOG_FD >= 0)); then
    for line in "${records[@]}"; do
      printf '%s\n' "$line" >&"$LOG_FD" || fail_log_write
    done
  fi
  for line in "${records[@]}"; do
    stdout_write "$line"
  done
  close_log
  exit "$code"
}

# Reports a usage error on stderr with the option list and exits 4.
fail_usage() {
  sanitize_line "$1"
  printf '%s: error: %s\n' "$PROG" "$SANITIZED" >&2
  usage >&2
  exit "$EXIT_ENV"
}

# Reports an environment error on stderr, records it in the evidence log when
# the log is already open, and exits 4.
fail_env() {
  sanitize_line "$1"
  local message="$SANITIZED"
  printf '%s: error: %s\n' "$PROG" "$message" >&2
  if ((LOG_FD >= 0)); then
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
        STAGE_SET=1
        shift 2
        ;;
      --stage=*)
        STAGE="${1#*=}"
        STAGE_SET=1
        shift
        ;;
      --log)
        (($# >= 2)) || fail_usage "--log requires a value"
        LOG_REQUESTED="$2"
        LOG_SET=1
        shift 2
        ;;
      --log=*)
        LOG_REQUESTED="${1#*=}"
        LOG_SET=1
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
      --self-test)
        SELF_TEST=1
        shift
        ;;
      -h | --help)
        usage
        exit "$EXIT_OK"
        ;;
      *)
        fail_usage "unknown option: $(sanitize "$1")"
        ;;
    esac
  done
  [[ -n "$STAGE" ]] || fail_usage "--stage requires a non-empty value"
  if [[ ! "$STAGE" =~ $STAGE_PATTERN ]] || ((${#STAGE} > STAGE_MAX_LENGTH)); then
    local stage_rule=""
    printf -v stage_rule \
      '%s accepts one to %d characters, starting with a letter or a digit and continuing with letters, digits, %s, %s or %s' \
      '--stage' "$STAGE_MAX_LENGTH" "'.'" "'_'" "'-'"
    fail_usage "${stage_rule}, received: $(sanitize "$STAGE")"
  fi
  [[ -z "$LOG_REQUESTED" || "$LOG_REQUESTED" != -* ]] ||
    fail_usage "--log requires a path value, received: $(sanitize "$LOG_REQUESTED")"
  if ((SELF_TEST == 1)); then
    if ((STAGE_SET == 1 || BASELINE_ONLY == 1 || QUIET == 1 || LOG_SET == 1)); then
      fail_usage "--self-test accepts no other option"
    fi
  fi
}

require_tool() {
  local tool="$1"
  if ! command -v "$tool" >/dev/null 2>&1; then
    fail_env "required tool not found on PATH: ${tool}"
  fi
}

# Checks every external tool a verification run invokes. Runs before the
# repository root is resolved and before the evidence log is opened, so a tool
# that is absent is reported as an environment error and never as a source or
# working-tree finding.
preflight_tools() {
  local tool=""
  for tool in "${REQUIRED_TOOLS[@]}"; do
    require_tool "$tool"
  done
}

# Checks that a descriptor this shell holds can be inspected through
# "/dev/fd/<number>", which both the evidence log and gate A rely on. Runs
# before the repository root is resolved and before the evidence log is opened,
# so a shell or system that cannot resolve that path is reported as an
# environment error and never as a source finding.
preflight_descriptor_view() {
  local probe=-1 status=""

  if ! { exec {probe}</dev/null; } 2>/dev/null; then
    fail_env "unable to open a probe descriptor on /dev/null"
  fi
  if ! status="$(stat -L -c '%F' -- "/dev/fd/${probe}" 2>/dev/null)" ||
    [[ -z "$status" ]]; then
    exec {probe}<&-
    fail_env "unable to read the status of a held descriptor through /dev/fd"
  fi
  exec {probe}<&-
}

# Records the physical path of the running script. Called before any directory
# change.
resolve_script_path() {
  local source="${BASH_SOURCE[0]}" dir="" base=""

  base="${source##*/}"
  dir="${source%/*}"
  if [[ "$dir" == "$source" ]]; then
    dir="."
  fi
  if ! dir="$(cd -P -- "$dir" 2>/dev/null && printf '%s' "$PWD")" || [[ -z "$dir" ]]; then
    fail_env "unable to resolve the directory of this script: $(sanitize "$source")"
  fi
  SCRIPT_PATH="${dir}/${base}"
  if [[ ! -f "$SCRIPT_PATH" ]]; then
    fail_env "unable to resolve this script as a regular file: $(sanitize "$SCRIPT_PATH")"
  fi
}

# Moves to the repository root and records its physical path. Every later path
# resolves from there, independently of the caller's working directory and of
# any symbolic link on the way to it.
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
    fail_env "the resolved repository root is not a directory: $(sanitize "$root")"
  fi
  if ! cd -P -- "$root"; then
    fail_env "unable to change directory to the repository root: $(sanitize "$root")"
  fi
  REPO_ROOT="$PWD"
}

# Creates the directory chain of the evidence log one component at a time,
# rejecting a component that is a symbolic link or that exists as something
# other than a directory. Each missing component is created by a
# single-component "mkdir" whose own stderr is discarded, so the only record of
# a creation that does not complete is this script's one-line summary. A
# creation that does not complete is followed by a re-read of that one name with
# shell builtins alone: a name that reads as a symbolic link is rejected with
# exit 4, a name that reads as a directory is accepted and the descent
# continues, and any other name exits 4. Creates nothing outside that chain.
prepare_log_dir() {
  local walked="" component=""
  local -a components=()

  IFS='/' read -r -a components <<<"$LOG_DIR_REL"
  for component in "${components[@]}"; do
    walked="${walked:+${walked}/}${component}"
    if [[ -L "$walked" ]]; then
      fail_env "evidence log rejected: directory component is a symbolic link: $(sanitize "$walked")"
    fi
    if [[ -e "$walked" ]]; then
      if [[ ! -d "$walked" ]]; then
        fail_env "evidence log rejected: directory component is not a directory: $(sanitize "$walked")"
      fi
      continue
    fi
    if ! mkdir -- "$walked" 2>/dev/null; then
      if [[ -L "$walked" ]]; then
        fail_env "evidence log rejected: directory component is a symbolic link: $(sanitize "$walked")"
      fi
      if [[ ! -d "$walked" ]]; then
        fail_env "unable to create the evidence log directory component: $(sanitize "$walked")"
      fi
    fi
  done
}

# Validates the requested log location against every rule in the header block,
# creates the missing components of its directory chain, opens the log for
# appending onto one descriptor and confirms that the descriptor and the path
# name the same regular file with a single hard link. Every rejection closes the
# descriptor and exits 4 before anything is written. The recorded path stays
# repository-relative and is used for the evidence line only; all writing goes
# through the descriptor.
open_log() {
  local requested="$DEFAULT_LOG_REL"
  local rel="" dir="" base="" physical="" root_display=""
  local fd=-1 name_status="" fd_status=""
  local name_type="" name_links="" name_inode="" name_device=""
  local fd_type="" fd_inode="" fd_device=""
  local diverted="" after=""

  if ((LOG_SET == 1)); then
    requested="$LOG_REQUESTED"
  fi
  root_display="$(sanitize "$REPO_ROOT")"

  if [[ -z "$requested" ]]; then
    fail_env "evidence log rejected: empty path"
  fi

  if [[ "$requested" == /* ]]; then
    case "$requested" in
      "${REPO_ROOT}/"*) rel="${requested#"${REPO_ROOT}/"}" ;;
      *) fail_env "evidence log rejected: path lies outside the repository root ${root_display}: $(sanitize "$requested")" ;;
    esac
  else
    rel="$requested"
  fi

  if [[ ! "$rel" =~ $LOG_PATH_PATTERN ]]; then
    fail_env "evidence log rejected: path holds a character outside 'A-Z a-z 0-9 . _ - /' or does not start with a letter or a digit: $(sanitize "$requested")"
  fi
  if [[ "$rel" == */ ]]; then
    fail_env "evidence log rejected: path names a directory, not a file: $(sanitize "$requested")"
  fi
  if [[ "/${rel}/" == */../* ]]; then
    fail_env "evidence log rejected: path contains a '..' component: $(sanitize "$requested")"
  fi

  dir="${rel%/*}"
  base="${rel##*/}"
  if [[ "$dir" != "$LOG_DIR_REL" ]]; then
    fail_env "evidence log rejected: directory must be exactly ${LOG_DIR_REL}: $(sanitize "$requested")"
  fi
  if [[ "$base" != *?.log ]]; then
    fail_env "evidence log rejected: file name must end in '.log': $(sanitize "$requested")"
  fi
  if [[ ! "$base" =~ $LOG_NAME_PATTERN ]]; then
    fail_env "evidence log rejected: file name must begin with a letter or a digit and continue with letters, digits, '.', '_' or '-': $(sanitize "$requested")"
  fi
  if [[ "$base" == *[!A-Za-z0-9._-]* ]]; then
    fail_env "evidence log rejected: file name may hold only letters, digits, '.', '_' and '-': $(sanitize "$requested")"
  fi

  prepare_log_dir

  if [[ -L "$rel" ]]; then
    fail_env "evidence log rejected: path is a symbolic link: $(sanitize "$rel")"
  fi
  if [[ -e "$rel" && ! -f "$rel" ]]; then
    fail_env "evidence log rejected: path exists and is not a regular file: $(sanitize "$rel")"
  fi

  if ! physical="$(cd -P -- "$LOG_DIR_REL" 2>/dev/null && printf '%s' "$PWD")" ||
    [[ -z "$physical" ]]; then
    fail_env "unable to resolve the physical path of ${LOG_DIR_REL}"
  fi
  if [[ "$physical" != "${REPO_ROOT}/${LOG_DIR_REL}" ]]; then
    fail_env "evidence log rejected: directory resolves to $(sanitize "$physical") instead of ${root_display}/${LOG_DIR_REL}"
  fi

  # Last check before the open. Both tests are shell builtins, so no other
  # command runs between them and the open that follows.
  if [[ -L "$rel" ]] || { [[ -e "$rel" ]] && [[ ! -f "$rel" ]]; }; then
    fail_env "evidence log rejected: path $(preopen_change_reason "$rel"): $(sanitize "$rel")"
  fi
  if ! { exec {fd}>>"$rel"; } 2>/dev/null; then
    fail_env "unable to append to the evidence log: $(sanitize "$rel")"
  fi

  if ! name_status="$(stat -c '%F|%h|%i|%d' -- "$rel" 2>/dev/null)"; then
    exec {fd}>&-
    fail_env "evidence log rejected: file status unavailable: $(sanitize "$rel")"
  fi
  IFS='|' read -r name_type name_links name_inode name_device <<<"$name_status"
  # The checks above accepted this path as a regular file that is not a symbolic
  # link, so a symbolic link or any other non-regular type here is a
  # substitution that landed between them and the open.
  if ! is_regular_kind "$name_type"; then
    exec {fd}>&-
    fail_env "evidence log rejected: path became a ${name_type} after it was validated: $(sanitize "$rel")"
  fi
  if [[ "$name_links" != "1" ]]; then
    exec {fd}>&-
    fail_env "evidence log rejected: path has ${name_links} hard links, expected exactly 1: $(sanitize "$rel")"
  fi

  if ! fd_status="$(stat -L -c '%F|%h|%i|%d' -- "/dev/fd/${fd}" 2>/dev/null)"; then
    exec {fd}>&-
    fail_env "evidence log rejected: status of the opened file unavailable: $(sanitize "$rel")"
  fi
  IFS='|' read -r fd_type _ fd_inode fd_device <<<"$fd_status"
  if ! is_regular_kind "$fd_type"; then
    exec {fd}>&-
    fail_env "evidence log rejected: opened file is not a regular file (${fd_type}): $(sanitize "$rel")"
  fi
  if [[ "$fd_inode" != "$name_inode" || "$fd_device" != "$name_device" ]]; then
    exec {fd}>&-
    fail_env "evidence log rejected: opened file ${fd_device}:${fd_inode} is not the named path ${name_device}:${name_inode}: $(sanitize "$rel")"
  fi

  # Read after the open: a directory component replaced by a symbolic link
  # resolves the final component elsewhere, and the checks above then describe
  # that other file rather than the intended one.
  diverted="$(symlinked_parent "$rel")"
  if [[ -n "$diverted" ]]; then
    exec {fd}>&-
    fail_env "evidence log rejected: directory component became a symbolic link (${diverted}) after it was validated: $(sanitize "$rel")"
  fi
  if ! after="$(cd -P -- "$LOG_DIR_REL" 2>/dev/null && printf '%s' "$PWD")" ||
    [[ -z "$after" ]]; then
    exec {fd}>&-
    fail_env "evidence log rejected: physical path of ${LOG_DIR_REL} unavailable after the open"
  fi
  if [[ "$after" != "${REPO_ROOT}/${LOG_DIR_REL}" ]]; then
    exec {fd}>&-
    fail_env "evidence log rejected: directory resolves to $(sanitize "$after") instead of ${root_display}/${LOG_DIR_REL} after the open"
  fi

  LOG_PATH="$rel"
  LOG_FD="$fd"
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

# Prints the first parent component of the supplied repository-relative path
# that is a symbolic link, and nothing when no parent component is one.
symlinked_parent() {
  local path="$1" walked="" component=""
  local -a components=()

  if [[ "$path" != */* ]]; then
    return 0
  fi

  IFS='/' read -r -a components <<<"${path%/*}"
  for component in "${components[@]}"; do
    walked="${walked:+${walked}/}${component}"
    if [[ -L "$walked" ]]; then
      printf '%s' "$walked"
      return 0
    fi
  done
  return 0
}

# Emits one gate A FAIL line. A non-empty reason is placed between the path and
# the measurements; an empty reason keeps the line shape used when the file was
# read and its measurements differ from the baseline.
gate_a_fail() {
  local path="$1" reason="$2" expected_lines="$3" actual_lines="$4"
  local expected_sha="$5" actual_sha="$6" line=""

  if [[ -n "$reason" ]]; then
    printf -v line \
      '  FAIL %s %s expected_lines=%s actual_lines=%s expected_sha256=%s actual_sha256=%s' \
      "$path" "$reason" "$expected_lines" "$actual_lines" "$expected_sha" "$actual_sha"
  else
    printf -v line \
      '  FAIL %s expected_lines=%s actual_lines=%s expected_sha256=%s actual_sha256=%s' \
      "$path" "$expected_lines" "$actual_lines" "$expected_sha" "$actual_sha"
  fi
  emit "$line"
}

# Gate A: per-file link rejection and presence, file type read from the path
# without following it, that type re-read with shell builtins immediately before
# the open and read again from the path after it, then SHA-256 and line count
# read through one descriptor held open on that entry, with the inode and device
# of the path confirmed against the descriptor and re-read after both
# measurements. Each rejection carries its own reason and counts as a gate A
# failure.
gate_a() {
  local row="" path="" expected_lines="" expected_sha=""
  local actual_lines="" actual_sha="" digest="" raw="" line="" parent=""
  local before="" after="" fd_status="" name_type=""
  local before_type="" before_inode="" before_device=""
  local fd_type="" fd_inode="" fd_device=""
  local failures=0

  emit "gate A source integrity:"
  for row in "${BASELINE[@]}"; do
    IFS='|' read -r path expected_lines expected_sha <<<"$row"

    if [[ -L "$path" ]]; then
      gate_a_fail "$path" "not a regular file (symbolic link)" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    parent="$(symlinked_parent "$path")"
    if [[ -n "$parent" ]]; then
      gate_a_fail "$path" "parent is a symbolic link (${parent})" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    if [[ ! -e "$path" ]]; then
      gate_a_fail "$path" "missing" \
        "$expected_lines" "(absent)" "$expected_sha" "(absent)"
      failures=$((failures + 1))
      continue
    fi
    if ! before="$(stat -c '%F|%i|%d' -- "$path" 2>/dev/null)"; then
      gate_a_fail "$path" "file status unavailable" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    IFS='|' read -r before_type before_inode before_device <<<"$before"
    if ! is_regular_kind "$before_type"; then
      gate_a_fail "$path" "not a regular file (${before_type})" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    # Last check before the open. Both tests are shell builtins, so no other
    # command runs between them and the open that follows.
    if [[ -L "$path" ]] || [[ ! -f "$path" ]]; then
      gate_a_fail "$path" "$(preopen_change_reason "$path")" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    if ! { exec {SOURCE_FD}<"$path"; } 2>/dev/null; then
      SOURCE_FD=-1
      gate_a_fail "$path" "unreadable" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    if ! name_type="$(stat -c '%F' -- "$path" 2>/dev/null)"; then
      close_source
      gate_a_fail "$path" "file status unavailable after it was opened" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    # The checks above accepted this path as a regular file that is not a
    # symbolic link, so a symbolic link or any other non-regular type here is a
    # substitution that landed between them and the open.
    if ! is_regular_kind "$name_type"; then
      close_source
      gate_a_fail "$path" "became a ${name_type} after it was validated" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    if ! fd_status="$(stat -L -c '%F|%i|%d' -- "/dev/fd/${SOURCE_FD}" 2>/dev/null)"; then
      close_source
      gate_a_fail "$path" "status of the opened file unavailable" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    IFS='|' read -r fd_type fd_inode fd_device <<<"$fd_status"
    if ! is_regular_kind "$fd_type"; then
      close_source
      gate_a_fail "$path" "opened file is not a regular file (${fd_type})" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    if [[ "$fd_inode" != "$before_inode" || "$fd_device" != "$before_device" ]]; then
      close_source
      gate_a_fail "$path" \
        "opened file ${fd_device}:${fd_inode} is not the named path ${before_device}:${before_inode}" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    # Read after the open: a directory component replaced by a symbolic link
    # resolves the entry elsewhere, and the status reads above then describe that
    # other file rather than the baseline entry.
    parent="$(symlinked_parent "$path")"
    if [[ -n "$parent" ]]; then
      close_source
      gate_a_fail "$path" \
        "parent became a symbolic link (${parent}) after it was validated" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    if ! digest="$(sha256sum -- "/dev/fd/${SOURCE_FD}" 2>/dev/null)"; then
      close_source
      gate_a_fail "$path" "unreadable" \
        "$expected_lines" "(not read)" "$expected_sha" "(not read)"
      failures=$((failures + 1))
      continue
    fi
    actual_sha="${digest%% *}"
    if ! raw="$(wc -l <"/dev/fd/${SOURCE_FD}" 2>/dev/null)"; then
      close_source
      gate_a_fail "$path" "unreadable" \
        "$expected_lines" "(not read)" "$expected_sha" "$actual_sha"
      failures=$((failures + 1))
      continue
    fi
    actual_lines="${raw//[[:space:]]/}"
    if ! after="$(stat -c '%i|%d' -- "$path" 2>/dev/null)"; then
      close_source
      gate_a_fail "$path" "file status unavailable after measurement" \
        "$expected_lines" "$actual_lines" "$expected_sha" "$actual_sha"
      failures=$((failures + 1))
      continue
    fi
    close_source
    if [[ "$after" != "${before_inode}|${before_device}" ]]; then
      gate_a_fail "$path" "replaced while it was measured" \
        "$expected_lines" "$actual_lines" "$expected_sha" "$actual_sha"
      failures=$((failures + 1))
      continue
    fi

    if [[ "$actual_sha" == "$expected_sha" && "$actual_lines" == "$expected_lines" ]]; then
      printf -v line '  PASS %s expected_lines=%s actual_lines=%s sha256=%s' \
        "$path" "$expected_lines" "$actual_lines" "$actual_sha"
      emit "$line"
    else
      gate_a_fail "$path" "" \
        "$expected_lines" "$actual_lines" "$expected_sha" "$actual_sha"
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
    fail_env "git status --porcelain -- base/ did not complete: $(sanitize "$output")"
  fi

  if [[ -z "$output" ]]; then
    emit "  git status --porcelain -- base/ produced no output"
    emit "gate B result: PASS"
    return 0
  fi

  emit "  git status --porcelain -- base/ reported:"
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    emit "    $(sanitize "$line")"
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
    fail_env "git diff --name-only HEAD did not complete: $(sanitize "$output")"
  fi

  emit "  git diff --name-only HEAD raw output:"
  if [[ -z "$output" ]]; then
    emit "    (no tracked modification)"
  else
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      emit "    $(sanitize "$line")"
      case "$line" in
        "${NEW_WORK_PREFIX}"*) : ;;
        *) remaining+=("$(sanitize "$line")") ;;
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

# --self-test support.
#
# Each case runs in its own throwaway git work tree: "repo" holds the five
# baseline sources, a copy of this script, a stub dependency manifest and the
# modernization/validation directory, all committed; "outside" holds one canary
# file and is the target every escape attempt is pointed at. A case asserts the
# exit code, the message content, which paths were and were not created, and
# that nothing outside the throwaway tree changed.

# Location of this script inside the repository, used to find the baseline
# sources to copy and to place the copy under test.
readonly SELF_TEST_SCRIPT_REL="modernization/validation/verify_readonly.sh"

# Tool names --self-test scrubs from PATH one case at a time, stated
# independently of REQUIRED_TOOLS and compared against it by the tool-list
# case.
readonly SELF_TEST_EXPECTED_TOOLS=(git sha256sum wc date mkdir stat)

# Number of case lines --self-test reports, including the case that checks this
# number. A case that is added or removed changes it.
readonly SELF_TEST_CASE_COUNT=45

# Content written to the escape canary and to the stub dependency manifest of
# each case work tree.
readonly SELF_TEST_CANARY="self-test canary"
readonly SELF_TEST_MANIFEST_REL="modernization/requirements.txt"
readonly SELF_TEST_MANIFEST_BODY="PyYAML==6.0.3"

# --self-test state.
SELF_TEST_ORIGIN=""
SELF_TEST_ROOT=""
SELF_TEST_PASS=0
SELF_TEST_FAIL=0
ST_CASE=""
ST_CASE_DIR=""
ST_REPO=""
ST_OUTSIDE=""
ST_SCRIPT=""
ST_EXIT=0
ST_OUTPUT=""
ST_OK=1
ST_DETAIL=""

# Removes the throwaway tree. Registered on EXIT while --self-test runs.
self_test_cleanup() {
  if [[ -n "$SELF_TEST_ROOT" && -d "$SELF_TEST_ROOT" ]]; then
    rm -rf -- "$SELF_TEST_ROOT"
  fi
}

# Prints one case line and counts its outcome.
st_report() {
  local outcome="$1" detail="$2" line=""
  printf -v line '%-4s %-22s %s' "$outcome" "$ST_CASE" "$detail"
  printf '%s\n' "$line"
  if [[ "$outcome" == "PASS" ]]; then
    SELF_TEST_PASS=$((SELF_TEST_PASS + 1))
  else
    SELF_TEST_FAIL=$((SELF_TEST_FAIL + 1))
  fi
}

# Records one unmet expectation for the running case.
st_note() {
  ST_OK=0
  ST_DETAIL="${ST_DETAIL}${ST_DETAIL:+; }$1"
}

# Creates the work tree for one case and resets its expectation state.
st_begin() {
  local row="" path="" out=""

  ST_CASE="$1"
  ST_OK=1
  ST_DETAIL=""
  ST_CASE_DIR="${SELF_TEST_ROOT}/${ST_CASE}"
  ST_REPO="${ST_CASE_DIR}/repo"
  ST_OUTSIDE="${ST_CASE_DIR}/outside"
  ST_SCRIPT="${ST_REPO}/${SELF_TEST_SCRIPT_REL}"

  if ! mkdir -p -- "${ST_REPO}/base/src" "${ST_REPO}/modernization/validation" "$ST_OUTSIDE"; then
    fail_env "--self-test could not create the case directories for ${ST_CASE}"
  fi
  printf '%s\n' "$SELF_TEST_CANARY" >"${ST_OUTSIDE}/canary.txt"
  printf '%s\n' "$SELF_TEST_MANIFEST_BODY" >"${ST_REPO}/${SELF_TEST_MANIFEST_REL}"
  for row in "${BASELINE[@]}"; do
    IFS='|' read -r path _ _ <<<"$row"
    if ! cp -p -- "${SELF_TEST_ORIGIN}/${path}" "${ST_REPO}/${path}"; then
      fail_env "--self-test could not copy the baseline source ${path}"
    fi
  done
  if ! cp -p -- "$SCRIPT_PATH" "$ST_SCRIPT"; then
    fail_env "--self-test could not copy this script into the case work tree"
  fi
  if ! out="$(cd "$ST_REPO" && git init -q . && git add -A &&
    git commit -q -m "self-test baseline" 2>&1)"; then
    fail_env "--self-test could not commit the case work tree: $(sanitize "$out")"
  fi
}

# Commits the current state of the case work tree.
st_commit() {
  local out=""
  if ! out="$(cd "$ST_REPO" && git add -A && git commit -q -m "$1" 2>&1)"; then
    fail_env "--self-test could not commit ${ST_CASE}: $(sanitize "$out")"
  fi
}

# Runs the copy under test inside the case work tree, capturing merged output.
st_run() {
  ST_OUTPUT=""
  ST_EXIT=0
  ST_OUTPUT="$(cd "$ST_REPO" && "$ST_SCRIPT" "$@" 2>&1)" || ST_EXIT=$?
}

# Runs the copy under test with a "stat" shim ahead of PATH, so that one file
# replacement lands inside a chosen window of the run. The shim forwards every
# call to the real "stat" with its arguments and exit status unchanged, and
# renames a prepared file over one path exactly once, either before or after the
# single call it selects, so the replaced path carries a different inode.
#
# Positional parameters:
#   1  when the replacement happens relative to the selected call: before, after
#   2  pattern the last argument of the selected call must match
#   3  whether the selected call carries -L: yes, no
#   4  format the selected call must pass to -c
#   5  file the replacement is renamed from
#   6  path the replacement is renamed over
#   7  path the replaced file is renamed to first, or empty to drop its name
#   8+ options handed to the copy under test
st_run_with_stat_shim() {
  local when="$1" trigger="$2" follow="$3" format="$4"
  local swap_from="$5" swap_to="$6" aside="$7"
  local bin="" real="" line=""
  shift 7

  bin="${ST_CASE_DIR}/bin-stat-shim"
  if ! mkdir -p -- "$bin"; then
    fail_env "--self-test could not create the shim PATH directory for ${ST_CASE}"
  fi
  if ! real="$(command -v stat)" || [[ -z "$real" ]]; then
    fail_env "--self-test could not resolve the real stat for ${ST_CASE}"
  fi
  {
    printf '%s\n' '#!/usr/bin/env bash'
    printf '%s\n' '# Forwards every call to the real stat and performs one prepared replacement.'
    printf '%s\n' 'set -u'
    printf 'readonly REAL=%q\n' "$real"
    printf 'readonly WHEN=%q\n' "$when"
    printf 'readonly TRIGGER=%q\n' "$trigger"
    printf 'readonly FOLLOW=%q\n' "$follow"
    printf 'readonly FORMAT=%q\n' "$format"
    printf 'readonly SWAP_FROM=%q\n' "$swap_from"
    printf 'readonly SWAP_TO=%q\n' "$swap_to"
    printf 'readonly ASIDE=%q\n' "$aside"
    printf 'readonly MARKER=%q\n' "${bin}/replacement-done"
    while IFS= read -r line; do
      printf '%s\n' "$line"
    done <<'SHIM_BODY'
args=("$@")
follow="no"
seen_format=""
index=0
for index in "${!args[@]}"; do
  if [[ "${args[index]}" == "-L" ]]; then
    follow="yes"
  fi
  if [[ "${args[index]}" == "-c" ]]; then
    seen_format="${args[index + 1]-}"
  fi
done
target="${args[${#args[@]} - 1]}"
selected="no"
# TRIGGER is matched as a pattern; /dev/fd/* names a held descriptor whatever
# its number.
if [[ "$target" == $TRIGGER && "$follow" == "$FOLLOW" &&
  "$seen_format" == "$FORMAT" && ! -e "$MARKER" ]]; then
  selected="yes"
fi
replace_once() {
  if ! : >"$MARKER"; then
    printf 'stat shim: could not record %s\n' "$MARKER" >&2
    exit 1
  fi
  if [[ -n "$ASIDE" ]] && ! mv -f -- "$SWAP_TO" "$ASIDE"; then
    printf 'stat shim: could not rename %s aside\n' "$SWAP_TO" >&2
    exit 1
  fi
  if ! mv -f -- "$SWAP_FROM" "$SWAP_TO"; then
    printf 'stat shim: could not rename %s into place\n' "$SWAP_FROM" >&2
    exit 1
  fi
}
if [[ "$selected" == "yes" && "$WHEN" == "before" ]]; then
  replace_once
fi
"$REAL" "${args[@]}"
status=$?
if [[ "$selected" == "yes" && "$WHEN" == "after" ]]; then
  replace_once
fi
exit "$status"
SHIM_BODY
  } >"${bin}/stat"
  if ! chmod 0755 -- "${bin}/stat"; then
    fail_env "--self-test could not make the stat shim executable for ${ST_CASE}"
  fi

  ST_OUTPUT=""
  ST_EXIT=0
  ST_OUTPUT="$(cd "$ST_REPO" && PATH="${bin}:${PATH}" "$BASH" "$ST_SCRIPT" "$@" 2>&1)" ||
    ST_EXIT=$?
}

# Runs the copy under test under a file-size limit of the supplied number of
# blocks, with SIGXFSZ ignored so that a write past the limit returns a failure
# to the running shell instead of ending it. Its stdout is captured through a
# pipe, which the limit does not apply to.
#
# Positional parameters:
#   1  file-size limit handed to "ulimit -f"
#   2+ options handed to the copy under test
st_run_with_file_size_limit() {
  local blocks="$1"
  shift

  ST_OUTPUT=""
  ST_EXIT=0
  ST_OUTPUT="$(cd "$ST_REPO" && trap '' XFSZ && ulimit -f "$blocks" &&
    "$ST_SCRIPT" "$@" 2>&1)" || ST_EXIT=$?
}

# Runs the copy under test with a "stat" shim ahead of PATH that reports a
# failure for every call whose last argument matches the supplied pattern and
# forwards every other call to the real "stat".
#
# Positional parameters:
#   1  pattern the last argument of a failing call must match
#   2+ options handed to the copy under test
st_run_with_failing_stat() {
  local trigger="$1" bin="" real="" line=""
  shift

  bin="${ST_CASE_DIR}/bin-stat-failing"
  if ! mkdir -p -- "$bin"; then
    fail_env "--self-test could not create the failing-shim PATH directory for ${ST_CASE}"
  fi
  if ! real="$(command -v stat)" || [[ -z "$real" ]]; then
    fail_env "--self-test could not resolve the real stat for ${ST_CASE}"
  fi
  {
    printf '%s\n' '#!/usr/bin/env bash'
    printf '%s\n' '# Forwards every call to the real stat except the ones it is asked to fail.'
    printf '%s\n' 'set -u'
    printf 'readonly REAL=%q\n' "$real"
    printf 'readonly TRIGGER=%q\n' "$trigger"
    while IFS= read -r line; do
      printf '%s\n' "$line"
    done <<'FAILING_SHIM_BODY'
args=("$@")
target="${args[${#args[@]} - 1]}"
# TRIGGER is matched as a pattern, so a held descriptor can be named by
# /dev/fd/* without knowing its number.
if [[ "$target" == $TRIGGER ]]; then
  printf 'stat: cannot read the status of %s\n' "$target" >&2
  exit 1
fi
exec "$REAL" "${args[@]}"
FAILING_SHIM_BODY
  } >"${bin}/stat"
  if ! chmod 0755 -- "${bin}/stat"; then
    fail_env "--self-test could not make the failing stat shim executable for ${ST_CASE}"
  fi

  ST_OUTPUT=""
  ST_EXIT=0
  ST_OUTPUT="$(cd "$ST_REPO" && PATH="${bin}:${PATH}" "$BASH" "$ST_SCRIPT" "$@" 2>&1)" ||
    ST_EXIT=$?
}

# Runs the copy under test with a "mkdir" shim ahead of PATH, so that one
# single-component creation finds the name already taken. For the first call
# whose last argument matches the supplied pattern the shim places the requested
# kind of entry at that name, writes one line of its own on stderr in the form
# the real tool uses and exits non-zero; every other call, and every later call
# on that name, is forwarded to the real "mkdir" with its arguments and exit
# status unchanged.
#
# Positional parameters:
#   1  pattern the last argument of the selected call must match
#   2  entry the shim places at that name: directory, symlink
#   3  path a placed symbolic link points at, empty for a placed directory
#   4+ options handed to the copy under test
st_run_with_mkdir_shim() {
  local trigger="$1" kind="$2" link_target="$3"
  local bin="" real="" line=""
  shift 3

  bin="${ST_CASE_DIR}/bin-mkdir-shim"
  if ! mkdir -p -- "$bin"; then
    fail_env "--self-test could not create the mkdir-shim PATH directory for ${ST_CASE}"
  fi
  if ! real="$(command -v mkdir)" || [[ -z "$real" ]]; then
    fail_env "--self-test could not resolve the real mkdir for ${ST_CASE}"
  fi
  {
    printf '%s\n' '#!/usr/bin/env bash'
    printf '%s\n' '# Forwards every call to the real mkdir except the one creation it takes over.'
    printf '%s\n' 'set -u'
    printf 'readonly REAL=%q\n' "$real"
    printf 'readonly TRIGGER=%q\n' "$trigger"
    printf 'readonly KIND=%q\n' "$kind"
    printf 'readonly LINK_TARGET=%q\n' "$link_target"
    printf 'readonly MARKER=%q\n' "${bin}/creation-taken-over"
    while IFS= read -r line; do
      printf '%s\n' "$line"
    done <<'MKDIR_SHIM_BODY'
args=("$@")
target="${args[${#args[@]} - 1]}"
# TRIGGER is matched as a pattern, so a component of the evidence directory can
# be named by a pattern as well as by an exact string.
if [[ "$target" == $TRIGGER && ! -e "$MARKER" ]]; then
  if ! : >"$MARKER"; then
    printf 'mkdir shim: could not record %s\n' "$MARKER" >&2
    exit 1
  fi
  case "$KIND" in
    directory)
      if ! "$REAL" -- "$target"; then
        printf 'mkdir shim: could not create %s\n' "$target" >&2
        exit 1
      fi
      ;;
    symlink)
      if ! ln -s -- "$LINK_TARGET" "$target"; then
        printf 'mkdir shim: could not link %s\n' "$target" >&2
        exit 1
      fi
      ;;
    *)
      printf 'mkdir shim: unknown entry kind %s\n' "$KIND" >&2
      exit 1
      ;;
  esac
  printf 'mkdir: %s: File exists\n' "$target" >&2
  exit 1
fi
exec "$REAL" "${args[@]}"
MKDIR_SHIM_BODY
  } >"${bin}/mkdir"
  if ! chmod 0755 -- "${bin}/mkdir"; then
    fail_env "--self-test could not make the mkdir shim executable for ${ST_CASE}"
  fi

  ST_OUTPUT=""
  ST_EXIT=0
  ST_OUTPUT="$(cd "$ST_REPO" && PATH="${bin}:${PATH}" "$BASH" "$ST_SCRIPT" "$@" 2>&1)" ||
    ST_EXIT=$?
}

# Runs the copy under test with a PATH that holds every expected tool except
# the named one.
st_run_without_tool() {
  local missing="$1" bin="" tool="" resolved=""
  shift

  bin="${ST_CASE_DIR}/bin-without-${missing}"
  if ! mkdir -p -- "$bin"; then
    fail_env "--self-test could not create the scrubbed PATH directory for ${missing}"
  fi
  for tool in "${SELF_TEST_EXPECTED_TOOLS[@]}"; do
    if [[ "$tool" == "$missing" ]]; then
      continue
    fi
    resolved="$(command -v "$tool")"
    if ! ln -s -- "$resolved" "${bin}/${tool}"; then
      fail_env "--self-test could not link ${tool} into the scrubbed PATH"
    fi
  done

  ST_OUTPUT=""
  ST_EXIT=0
  ST_OUTPUT="$(cd "$ST_REPO" && PATH="$bin" "$BASH" "$ST_SCRIPT" "$@" 2>&1)" || ST_EXIT=$?
}

st_expect_exit() {
  ((ST_EXIT == $1)) || st_note "exit ${ST_EXIT}, expected $1"
}

st_expect_output() {
  [[ "$ST_OUTPUT" == *"$1"* ]] || st_note "output lacks '$1'"
}

st_expect_no_output() {
  [[ "$ST_OUTPUT" != *"$1"* ]] || st_note "output unexpectedly holds '$1'"
}

st_expect_absent() {
  [[ ! -e "$1" && ! -L "$1" ]] || st_note "created ${1#"${SELF_TEST_ROOT}/"}"
}

st_expect_body() {
  local path="$1" want="$2"
  if [[ ! -f "$path" ]]; then
    st_note "missing or irregular ${path#"${SELF_TEST_ROOT}/"}"
    return 0
  fi
  [[ "$(<"$path")" == "$want" ]] || st_note "content changed: ${path#"${SELF_TEST_ROOT}/"}"
}

# Counts the lines of a file that equal a literal string.
st_expect_exact_count() {
  local path="$1" wanted_line="$2" want="$3" line="" count=0
  if [[ ! -f "$path" ]]; then
    st_note "missing log ${path#"${SELF_TEST_ROOT}/"}"
    return 0
  fi
  while IFS= read -r line; do
    if [[ "$line" == "$wanted_line" ]]; then
      count=$((count + 1))
    fi
  done <"$path"
  ((count == want)) || st_note "${count} line(s) equal to '${wanted_line}', expected ${want}"
}

# Counts the lines of a file that start with a literal prefix.
st_expect_prefix_count() {
  local path="$1" prefix="$2" want="$3" line="" count=0
  if [[ ! -f "$path" ]]; then
    st_note "missing log ${path#"${SELF_TEST_ROOT}/"}"
    return 0
  fi
  while IFS= read -r line; do
    if [[ "$line" == "$prefix"* ]]; then
      count=$((count + 1))
    fi
  done <"$path"
  ((count == want)) || st_note "${count} line(s) starting '${prefix}', expected ${want}"
}

# Counts the lines of a file that hold a literal substring.
st_expect_substring_count() {
  local path="$1" needle="$2" want="$3" line="" count=0
  if [[ ! -f "$path" ]]; then
    st_note "missing log ${path#"${SELF_TEST_ROOT}/"}"
    return 0
  fi
  while IFS= read -r line; do
    if [[ "$line" == *"$needle"* ]]; then
      count=$((count + 1))
    fi
  done <"$path"
  ((count == want)) || st_note "${count} line(s) holding '${needle}', expected ${want}"
}

# Confirms the case wrote nothing outside its throwaway tree: the escape
# directory still holds only its unchanged canary, the five protected sources of
# the repository this run started from still match the embedded baseline, and no
# case log name appeared beside that repository root.
st_expect_no_write_outside() {
  local -a entries=()
  local row="" path="" expected_sha="" digest=""

  shopt -s nullglob dotglob
  entries=("${ST_OUTSIDE}"/*)
  shopt -u nullglob dotglob
  if ((${#entries[@]} != 1)) || [[ "${entries[0]}" != "${ST_OUTSIDE}/canary.txt" ]]; then
    st_note "the escape directory holds ${#entries[@]} entry/entries"
  else
    st_expect_body "${ST_OUTSIDE}/canary.txt" "$SELF_TEST_CANARY"
  fi

  for row in "${BASELINE[@]}"; do
    IFS='|' read -r path _ expected_sha <<<"$row"
    digest="unreadable"
    digest="$(sha256sum -- "${SELF_TEST_ORIGIN}/${path}" 2>/dev/null)" || digest="unreadable"
    if [[ "${digest%% *}" != "$expected_sha" ]]; then
      st_note "starting repository source changed: ${path}"
    fi
  done

  if [[ -e "${SELF_TEST_ORIGIN}/escape.log" ]]; then
    st_note "escape.log appeared beside the starting repository root"
  fi
}

# Closes the running case: adds the outside-the-tree check, then reports.
st_end() {
  st_expect_no_write_outside
  if ((ST_OK == 1)); then
    st_report "PASS" "$1"
  else
    st_report "FAIL" "$ST_DETAIL"
  fi
}

st_case_log_traversal() {
  st_begin "log-traversal"
  st_run --stage self-test --log "modernization/../escape.log"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "'..' component"
  st_expect_absent "${ST_REPO}/escape.log"
  st_expect_absent "${ST_CASE_DIR}/escape.log"
  st_expect_absent "${ST_REPO}/${LOG_DIR_REL}"
  st_end "exit 4, '..' rule named, no log and no escape file"
}

st_case_log_empty() {
  st_begin "log-empty"
  st_run --stage self-test --log ""
  st_expect_exit "$EXIT_ENV"
  st_expect_output "empty path"
  st_expect_absent "${ST_REPO}/${LOG_DIR_REL}"
  st_end "exit 4, empty-path rule named, no fallback to the default log"
}

st_case_log_authored_file() {
  st_begin "log-authored-file"
  st_run --stage self-test --log "$SELF_TEST_MANIFEST_REL"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "directory must be exactly ${LOG_DIR_REL}"
  st_expect_body "${ST_REPO}/${SELF_TEST_MANIFEST_REL}" "$SELF_TEST_MANIFEST_BODY"
  st_expect_absent "${ST_REPO}/${LOG_DIR_REL}"
  st_end "exit 4, directory rule named, authored manifest untouched"
}

st_case_log_absolute_outside() {
  st_begin "log-absolute-outside"
  st_run --stage self-test --log "${ST_OUTSIDE}/abs-escape.log"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "outside the repository root"
  st_expect_absent "${ST_OUTSIDE}/abs-escape.log"
  st_expect_absent "${ST_REPO}/${LOG_DIR_REL}"
  st_end "exit 4, repository-root rule named, nothing written outside"
}

st_case_log_absolute_inside() {
  st_begin "log-absolute-inside"
  st_run --stage self-test --log "${ST_REPO}/${LOG_DIR_REL}/absolute.log"
  st_expect_exit "$EXIT_OK"
  st_expect_output "verdict: PASS"
  st_expect_exact_count "${ST_REPO}/${LOG_DIR_REL}/absolute.log" "BEGIN readonly-check" 1
  st_expect_prefix_count "${ST_REPO}/${LOG_DIR_REL}/absolute.log" "verdict: " 1
  st_end "exit 0, accepted absolute path, one evidence block"
}

st_case_log_basename() {
  st_begin "log-basename"
  st_run --stage self-test --log "${LOG_DIR_REL}/notes.txt"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "must end in '.log'"
  st_expect_absent "${ST_REPO}/${LOG_DIR_REL}"
  st_end "exit 4, '.log' rule named, no file created"
}

st_case_log_symlinked_target() {
  st_begin "log-symlinked-target"
  if ! mkdir -p -- "${ST_REPO}/${LOG_DIR_REL}" ||
    ! ln -s -- "${ST_OUTSIDE}/link-target.log" "${ST_REPO}/${LOG_DIR_REL}/link.log"; then
    fail_env "--self-test could not create the symlinked log target"
  fi
  st_run --stage self-test --log "${LOG_DIR_REL}/link.log"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "path is a symbolic link"
  st_expect_absent "${ST_OUTSIDE}/link-target.log"
  st_end "exit 4, symbolic-link rule named, target never created"
}

st_case_log_symlinked_parent() {
  st_begin "log-symlinked-parent"
  if ! mkdir -p -- "${ST_CASE_DIR}/diverted" ||
    ! ln -s -- "${ST_CASE_DIR}/diverted" "${ST_REPO}/${LOG_DIR_REL}"; then
    fail_env "--self-test could not create the symlinked log directory"
  fi
  st_run --stage self-test
  st_expect_exit "$EXIT_ENV"
  st_expect_output "directory component is a symbolic link"
  st_expect_absent "${ST_CASE_DIR}/diverted/readonly-check.log"
  st_end "exit 4, directory-component rule named, nothing diverted"
}

st_case_log_hard_link() {
  local log_rel="${LOG_DIR_REL}/hard.log" log_abs=""
  st_begin "log-hard-link"
  log_abs="${ST_REPO}/${log_rel}"
  if ! mkdir -p -- "${ST_REPO}/${LOG_DIR_REL}" ||
    ! ln -- "${ST_REPO}/${SELF_TEST_MANIFEST_REL}" "$log_abs"; then
    fail_env "--self-test could not create the hard-linked log target"
  fi
  st_run --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "hard links, expected exactly 1"
  st_expect_body "${ST_REPO}/${SELF_TEST_MANIFEST_REL}" "$SELF_TEST_MANIFEST_BODY"
  st_expect_body "$log_abs" "$SELF_TEST_MANIFEST_BODY"
  st_expect_substring_count "$log_abs" "BEGIN readonly-check" 0
  st_end "exit 4, hard-link rule named, the other name of the inode unchanged"
}

st_case_log_fifo() {
  local log_rel="${LOG_DIR_REL}/pipe.log" log_abs=""
  st_begin "log-fifo"
  log_abs="${ST_REPO}/${log_rel}"
  if ! mkdir -p -- "${ST_REPO}/${LOG_DIR_REL}" || ! mkfifo -- "$log_abs"; then
    fail_env "--self-test could not create the FIFO log target"
  fi
  st_run --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "exists and is not a regular file"
  [[ -p "$log_abs" ]] || st_note "the FIFO log target no longer exists as a FIFO"
  st_expect_absent "${ST_REPO}/${DEFAULT_LOG_REL}"
  st_end "exit 4, non-regular rule named, the FIFO left in place and no fallback"
}

st_case_log_open_failure() {
  local name="" i=0 log_rel="" log_abs=""
  st_begin "log-open-failure"
  for ((i = 0; i < 65; i++)); do
    name+="aaaa"
  done
  log_rel="${LOG_DIR_REL}/${name}.log"
  log_abs="${ST_REPO}/${log_rel}"
  st_run --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "unable to append to the evidence log"
  st_expect_no_output "BEGIN readonly-check"
  st_expect_absent "$log_abs"
  st_expect_absent "${ST_REPO}/${DEFAULT_LOG_REL}"
  st_end "exit 4, refused open reported, no log created and no fallback"
}

# Asserts the outcome that matches this process's measured ability to create a
# file inside a mode-0500 evidence-log directory.
st_case_log_unwritable_dir() {
  local log_rel="${LOG_DIR_REL}/unwritable.log" log_abs="" dir="" detail=""
  local writable=0
  st_begin "log-unwritable-dir"
  dir="${ST_REPO}/${LOG_DIR_REL}"
  log_abs="${ST_REPO}/${log_rel}"
  if ! mkdir -p -- "$dir" || ! chmod 0500 -- "$dir"; then
    fail_env "--self-test could not reduce the mode of the log directory"
  fi
  if { : >"${dir}/write-probe.tmp"; } 2>/dev/null; then
    writable=1
    if ! rm -f -- "${dir}/write-probe.tmp"; then
      fail_env "--self-test could not remove its log-directory write probe"
    fi
  fi
  st_run --stage self-test --log "$log_rel"
  if ((writable == 0)); then
    st_expect_exit "$EXIT_ENV"
    st_expect_output "unable to append to the evidence log"
    st_expect_absent "$log_abs"
    detail="exit 4, refused open reported, no log created in the mode-0500 directory"
  else
    st_expect_exit "$EXIT_OK"
    st_expect_output "verdict: PASS"
    st_expect_exact_count "$log_abs" "BEGIN readonly-check" 1
    st_expect_exact_count "$log_abs" "verdict: PASS" 1
    detail="mode 0500 does not block this process, one complete block written"
  fi
  if ! chmod 0755 -- "$dir"; then
    fail_env "--self-test could not restore the mode of the log directory"
  fi
  st_end "$detail"
}

# Replaces the log with a different inode after it has been opened and before
# its status is read. The descriptor and the path then name different files.
st_case_log_swapped_open() {
  local log_rel="${LOG_DIR_REL}/swapped.log" log_abs="" replacement=""
  local body="self-test replacement log"
  st_begin "log-swapped-open"
  log_abs="${ST_REPO}/${log_rel}"
  replacement="${ST_CASE_DIR}/replacement.log"
  printf '%s\n' "$body" >"$replacement"
  st_run_with_stat_shim "before" "$log_rel" "no" '%F|%h|%i|%d' \
    "$replacement" "$log_abs" "" --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "is not the named path"
  st_expect_no_output "verdict: PASS"
  st_expect_body "$log_abs" "$body"
  st_expect_substring_count "$log_abs" "BEGIN readonly-check" 0
  st_expect_absent "${ST_REPO}/${DEFAULT_LOG_REL}"
  st_end "exit 4 when the opened log and the named path stop being one file"
}

# Puts a symbolic link at the log name after the log has been opened and before
# its status is read. The link points outside the work tree, and the run reports
# the type the name carries without writing a line or creating the link target.
# It covers the report made after the open. No command runs in the window
# between the builtin check and the open, and no case acts inside it.
st_case_log_became_symlink() {
  local log_rel="${LOG_DIR_REL}/late-link.log" log_abs="" link="" target=""
  st_begin "log-became-symlink"
  log_abs="${ST_REPO}/${log_rel}"
  link="${ST_CASE_DIR}/late-link.log"
  target="${ST_OUTSIDE}/late-link-target.log"
  if ! ln -s -- "$target" "$link"; then
    fail_env "--self-test could not create the replacement symbolic link"
  fi
  st_run_with_stat_shim "before" "$log_rel" "no" '%F|%h|%i|%d' \
    "$link" "$log_abs" "" --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "path became a symbolic link after it was validated"
  st_expect_no_output "BEGIN readonly-check"
  st_expect_absent "$target"
  st_expect_absent "${ST_REPO}/${DEFAULT_LOG_REL}"
  [[ -L "$log_abs" ]] || st_note "the log name is not the replacement symbolic link"
  st_end "exit 4 when the log name becomes a symbolic link after it was validated, link target never created"
}

# Puts a FIFO at the log name after the log has been opened and before its
# status is read. The run reports the type the name carries and writes no line.
# It covers the report made after the open. No command runs in the window
# between the builtin check and the open, and no case acts inside it.
st_case_log_became_fifo() {
  local log_rel="${LOG_DIR_REL}/late-pipe.log" log_abs="" fifo=""
  st_begin "log-became-fifo"
  log_abs="${ST_REPO}/${log_rel}"
  fifo="${ST_CASE_DIR}/late-pipe.log"
  if ! mkfifo -- "$fifo"; then
    fail_env "--self-test could not create the replacement FIFO log target"
  fi
  st_run_with_stat_shim "before" "$log_rel" "no" '%F|%h|%i|%d' \
    "$fifo" "$log_abs" "" --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "path became a fifo after it was validated"
  st_expect_no_output "BEGIN readonly-check"
  st_expect_absent "${ST_REPO}/${DEFAULT_LOG_REL}"
  [[ -p "$log_abs" ]] || st_note "the log name is not the replacement FIFO"
  st_end "exit 4 when the log name becomes a FIFO after it was validated, nothing written"
}

# Renames the accepted log aside and puts a different file at its name part way
# through the run. Asserts which of the two files the remaining lines reached.
st_case_log_name_swapped() {
  local log_rel="${LOG_DIR_REL}/held.log" log_abs="" replacement="" aside=""
  local trigger="" body="self-test replacement at the log name"
  st_begin "log-name-swapped"
  log_abs="${ST_REPO}/${log_rel}"
  replacement="${ST_CASE_DIR}/name-replacement.log"
  aside="${ST_CASE_DIR}/held-inode.log"
  printf '%s\n' "$body" >"$replacement"
  IFS='|' read -r trigger _ _ <<<"${BASELINE[0]}"
  st_run_with_stat_shim "before" "$trigger" "no" '%F|%i|%d' \
    "$replacement" "$log_abs" "$aside" --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_OK"
  st_expect_output "verdict: PASS"
  st_expect_exact_count "$aside" "BEGIN readonly-check" 1
  st_expect_exact_count "$aside" "END readonly-check" 1
  st_expect_prefix_count "$aside" "evidence_log: ${log_rel}" 1
  st_expect_prefix_count "$aside" "gate A result: PASS" 1
  st_expect_exact_count "$aside" "gate B result: PASS" 1
  st_expect_exact_count "$aside" "gate C result: PASS" 1
  st_expect_exact_count "$aside" "verdict: PASS" 1
  st_expect_exact_count "$aside" "exit_code: 0" 1
  st_expect_body "$log_abs" "$body"
  st_expect_substring_count "$log_abs" "readonly-check" 0
  st_end "exit 0 with the whole block in the opened inode and nothing at the replaced name"
}

# Lets the log open succeed and makes a later append fail. Asserts the exit
# code, the diagnostic and the state of the unfinished block.
st_case_log_write_failure() {
  local log_abs=""
  st_begin "log-write-failure"
  log_abs="${ST_REPO}/${DEFAULT_LOG_REL}"
  st_run_with_file_size_limit 1 --stage self-test
  st_expect_exit "$EXIT_ENV"
  st_expect_output "evidence log append did not complete"
  st_expect_no_output "verdict: PASS"
  st_expect_exact_count "$log_abs" "BEGIN readonly-check" 1
  st_expect_exact_count "$log_abs" "END readonly-check" 0
  st_expect_prefix_count "$log_abs" "verdict: " 0
  st_end "exit 4 when an append does not complete, with the block left unfinished"
}

st_case_log_inode_stability() {
  local log_abs="" before="" after="" links=""
  st_begin "log-inode-stability"
  log_abs="${ST_REPO}/${DEFAULT_LOG_REL}"
  st_run --stage first-run
  st_expect_exit "$EXIT_OK"
  before="$(stat -c '%i|%d' -- "$log_abs" 2>/dev/null)" ||
    st_note "the evidence log has no status after the first run"
  st_run --stage second-run
  st_expect_exit "$EXIT_OK"
  after="$(stat -c '%i|%d' -- "$log_abs" 2>/dev/null)" ||
    st_note "the evidence log has no status after the second run"
  [[ -n "$before" && "$after" == "$before" ]] ||
    st_note "the evidence log inode or device changed between runs"
  links="$(stat -c '%h' -- "$log_abs" 2>/dev/null)" || links=""
  [[ "$links" == "1" ]] ||
    st_note "the evidence log reports ${links:-no} hard link(s), expected 1"
  st_expect_exact_count "$log_abs" "BEGIN readonly-check" 2
  st_expect_prefix_count "$log_abs" "stage: first-run" 1
  st_expect_prefix_count "$log_abs" "stage: second-run" 1
  st_expect_prefix_count "$log_abs" "timestamp_utc: " 2
  st_expect_prefix_count "$log_abs" "repository_root: " 2
  st_expect_prefix_count "$log_abs" "evidence_log: ${DEFAULT_LOG_REL}" 2
  st_expect_exact_count "$log_abs" "preflight result: PASS" 2
  st_expect_prefix_count "$log_abs" "gate A result: PASS" 2
  st_expect_exact_count "$log_abs" "gate B result: PASS" 2
  st_expect_exact_count "$log_abs" "gate C result: PASS" 2
  st_expect_exact_count "$log_abs" "verdict: PASS" 2
  st_expect_exact_count "$log_abs" "exit_code: 0" 2
  st_expect_exact_count "$log_abs" "END readonly-check" 2
  st_end "two complete evidence blocks in one unchanged single-link inode"
}

# The evidence directory is a real directory by the time this run's creation of
# it reports a failure, and the creating tool writes a line of its own.
st_case_log_dir_appeared() {
  local log_abs=""
  st_begin "log-dir-appeared"
  log_abs="${ST_REPO}/${DEFAULT_LOG_REL}"
  st_run_with_mkdir_shim "$LOG_DIR_REL" "directory" "" --stage self-test
  st_expect_exit "$EXIT_OK"
  st_expect_output "gate A result: PASS (5 of 5 baseline entries matched)"
  st_expect_output "gate B result: PASS"
  st_expect_output "gate C result: PASS"
  st_expect_output "verdict: PASS"
  st_expect_no_output "unable to create the evidence log directory component"
  st_expect_no_output "mkdir:"
  st_expect_exact_count "$log_abs" "BEGIN readonly-check" 1
  st_expect_exact_count "$log_abs" "END readonly-check" 1
  st_expect_exact_count "$log_abs" "verdict: PASS" 1
  st_end "exit 0 with one complete block when the evidence directory appears under this run, no tool stderr"
}

# A symbolic link holds the evidence directory's name by the time this run's
# creation of it reports a failure.
st_case_log_dir_link_appeared() {
  st_begin "log-dir-link-appeared"
  if ! mkdir -p -- "${ST_CASE_DIR}/diverted"; then
    fail_env "--self-test could not create the diverted directory for ${ST_CASE}"
  fi
  st_run_with_mkdir_shim "$LOG_DIR_REL" "symlink" "${ST_CASE_DIR}/diverted" \
    --stage self-test
  st_expect_exit "$EXIT_ENV"
  st_expect_output "directory component is a symbolic link"
  st_expect_output "$LOG_DIR_REL"
  st_expect_no_output "verdict: PASS"
  st_expect_no_output "mkdir:"
  st_expect_absent "${ST_CASE_DIR}/diverted/readonly-check.log"
  st_end "exit 4 when a symbolic link takes that name under this run, nothing diverted, no tool stderr"
}

st_case_source_symlink() {
  local path="" base=""
  st_begin "source-symlink"
  IFS='|' read -r path _ _ <<<"${BASELINE[0]}"
  base="${path##*/}"
  if ! mkdir -p -- "${ST_REPO}/vendor" ||
    ! cp -p -- "${ST_REPO}/${path}" "${ST_REPO}/vendor/${base}" ||
    ! rm -- "${ST_REPO}/${path}" ||
    ! ln -s -- "${ST_REPO}/vendor/${base}" "${ST_REPO}/${path}"; then
    fail_env "--self-test could not replace ${path} with a symbolic link"
  fi
  st_commit "self-test source symlink"
  st_run --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} not a regular file (symbolic link)"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  st_end "exit 1 at gate A on committed identical-content symlink"
}

st_case_source_parent_symlink() {
  local row="" path="" base=""
  st_begin "source-parent-symlink"
  if ! mkdir -p -- "${ST_REPO}/vendor/src"; then
    fail_env "--self-test could not create the diverted source directory"
  fi
  for row in "${BASELINE[@]}"; do
    IFS='|' read -r path _ _ <<<"$row"
    base="${path##*/}"
    if ! cp -p -- "${ST_REPO}/${path}" "${ST_REPO}/vendor/src/${base}"; then
      fail_env "--self-test could not divert ${path}"
    fi
  done
  if ! rm -rf -- "${ST_REPO}/base/src" ||
    ! ln -s -- "${ST_REPO}/vendor/src" "${ST_REPO}/base/src"; then
    fail_env "--self-test could not replace base/src with a symbolic link"
  fi
  st_commit "self-test source directory symlink"
  st_run --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "parent is a symbolic link (base/src)"
  st_expect_output "gate A result: FAIL (5 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_end "exit 1 at gate A on committed symlinked source directory"
}

# Prints the SHA-256 of the supplied file, and nothing when it cannot be read.
st_digest_of() {
  local digest=""
  digest="$(sha256sum -- "$1" 2>/dev/null)" || return 0
  printf '%s' "${digest%% *}"
}

# Prints the line count of the supplied file without surrounding blanks, and
# nothing when it cannot be read.
st_lines_of() {
  local raw=""
  raw="$(wc -l <"$1" 2>/dev/null)" || return 0
  printf '%s' "${raw//[[:space:]]/}"
}

# Rewrites the supplied file with one extra character on its first line, so its
# content changes and its line count does not.
st_change_first_line() {
  local file="$1" line=""
  local -a body=()

  while IFS= read -r line; do
    body+=("$line")
  done <"$file"
  if ((${#body[@]} == 0)); then
    fail_env "--self-test read no line from $(sanitize "$file")"
  fi
  body[0]="${body[0]}Z"
  {
    for line in "${body[@]}"; do
      printf '%s\n' "$line"
    done
  } >"$file"
}

st_case_source_content_mismatch() {
  local path="" lines="" sha="" file="" measured="" mutated=""
  st_begin "source-content-mismatch"
  IFS='|' read -r path lines sha <<<"${BASELINE[0]}"
  file="${ST_REPO}/${path}"
  st_change_first_line "$file"
  measured="$(st_lines_of "$file")"
  mutated="$(st_digest_of "$file")"
  [[ "$measured" == "$lines" ]] ||
    st_note "the content change moved the line count to ${measured:-(unreadable)}"
  [[ -n "$mutated" && "$mutated" != "$sha" ]] ||
    st_note "the content change did not move the digest"
  st_commit "self-test source content change"
  st_run --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} expected_lines=${lines} actual_lines=${lines} expected_sha256=${sha} actual_sha256=${mutated}"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  st_end "exit 1 at gate A on a committed content change, both digests on one FAIL line"
}

st_case_source_missing() {
  local path="" lines="" sha=""
  st_begin "source-missing"
  IFS='|' read -r path lines sha <<<"${BASELINE[1]}"
  if ! rm -- "${ST_REPO}/${path}"; then
    fail_env "--self-test could not remove ${path}"
  fi
  st_commit "self-test source removal"
  st_run --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} missing expected_lines=${lines} actual_lines=(absent) expected_sha256=${sha} actual_sha256=(absent)"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  st_end "exit 1 at gate A on a committed removal, absent markers on the FAIL line"
}

st_case_source_line_count() {
  local path="" lines="" sha="" file="" measured="" mutated=""
  st_begin "source-line-count"
  IFS='|' read -r path lines sha <<<"${BASELINE[2]}"
  file="${ST_REPO}/${path}"
  printf '      *SELF-TEST APPENDED LINE\n' >>"$file"
  measured="$(st_lines_of "$file")"
  mutated="$(st_digest_of "$file")"
  [[ "$measured" == "$((lines + 1))" ]] ||
    st_note "the appended line moved the line count to ${measured:-(unreadable)}"
  [[ -n "$mutated" && "$mutated" != "$sha" ]] ||
    st_note "the appended line did not move the digest"
  st_commit "self-test source line addition"
  st_run --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} expected_lines=${lines} actual_lines=$((lines + 1)) expected_sha256=${sha} actual_sha256=${mutated}"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  st_end "exit 1 at gate A with both line counts and both digests on one FAIL line"
}

st_case_source_non_regular() {
  local fifo_path="" fifo_lines="" fifo_sha=""
  local dir_path="" dir_lines="" dir_sha=""
  st_begin "source-non-regular"
  IFS='|' read -r fifo_path fifo_lines fifo_sha <<<"${BASELINE[0]}"
  IFS='|' read -r dir_path dir_lines dir_sha <<<"${BASELINE[3]}"
  if ! rm -- "${ST_REPO}/${fifo_path}" || ! mkfifo -- "${ST_REPO}/${fifo_path}"; then
    fail_env "--self-test could not put a FIFO in place of ${fifo_path}"
  fi
  if ! rm -- "${ST_REPO}/${dir_path}" || ! mkdir -- "${ST_REPO}/${dir_path}"; then
    fail_env "--self-test could not put a directory in place of ${dir_path}"
  fi
  st_run --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${fifo_path} not a regular file (fifo) expected_lines=${fifo_lines} actual_lines=(not read) expected_sha256=${fifo_sha} actual_sha256=(not read)"
  st_expect_output "FAIL ${dir_path} not a regular file (directory) expected_lines=${dir_lines} actual_lines=(not read) expected_sha256=${dir_sha} actual_sha256=(not read)"
  st_expect_output "gate A result: FAIL (2 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  st_end "exit 1 at gate A on a FIFO and a directory in place of sources, neither opened"
}

# Replaces a baseline entry with an identical-content inode after its status has
# been read and before it is opened. The measurements still match the baseline,
# and the descriptor comparison is the check that reports the substitution.
st_case_source_swapped_open() {
  local path="" lines="" sha="" copy=""
  st_begin "source-swapped-open"
  IFS='|' read -r path lines sha <<<"${BASELINE[0]}"
  copy="${ST_CASE_DIR}/identical-copy"
  if ! cp -p -- "${ST_REPO}/${path}" "$copy"; then
    fail_env "--self-test could not copy ${path} for the substitution case"
  fi
  st_run_with_stat_shim "after" "$path" "no" '%F|%i|%d' \
    "$copy" "${ST_REPO}/${path}" "" --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} opened file "
  st_expect_output "is not the named path"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  st_end "exit 1 at gate A when an entry is substituted between its status read and its open"
}

# Puts a symbolic link to identical content at a baseline entry after its status
# has been read and before it is opened. The content behind the link matches the
# baseline, so the type read by the builtin check made immediately before the
# open is the only thing that reports it, and the entry is never opened.
st_case_source_swap_symlink() {
  local path="" lines="" sha="" copy="" link=""
  st_begin "source-swap-symlink"
  IFS='|' read -r path lines sha <<<"${BASELINE[0]}"
  copy="${ST_CASE_DIR}/identical-target"
  link="${ST_CASE_DIR}/replacement-link"
  if ! cp -p -- "${ST_REPO}/${path}" "$copy" || ! ln -s -- "$copy" "$link"; then
    fail_env "--self-test could not create the replacement symbolic link for ${path}"
  fi
  st_run_with_stat_shim "after" "$path" "no" '%F|%i|%d' \
    "$link" "${ST_REPO}/${path}" "" --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} replaced by a symbolic link before it was opened expected_lines=${lines} actual_lines=(not read) expected_sha256=${sha} actual_sha256=(not read)"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  [[ -L "${ST_REPO}/${path}" ]] || st_note "the entry is not the replacement symbolic link"
  st_end "exit 1 when an entry is replaced by a symbolic link to identical content before its open"
}

# Puts a FIFO at a baseline entry after its status has been read and before it
# is opened. The builtin check made immediately before the open reports the type
# and the entry is never opened, so the run completes instead of blocking on
# that open.
st_case_source_swap_fifo() {
  local path="" lines="" sha="" fifo=""
  st_begin "source-swap-fifo"
  IFS='|' read -r path lines sha <<<"${BASELINE[0]}"
  fifo="${ST_CASE_DIR}/replacement-fifo"
  if ! mkfifo -- "$fifo"; then
    fail_env "--self-test could not create the replacement FIFO for ${path}"
  fi
  st_run_with_stat_shim "after" "$path" "no" '%F|%i|%d' \
    "$fifo" "${ST_REPO}/${path}" "" --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} replaced by a fifo before it was opened expected_lines=${lines} actual_lines=(not read) expected_sha256=${sha} actual_sha256=(not read)"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  [[ -p "${ST_REPO}/${path}" ]] || st_note "the entry is not the replacement FIFO"
  st_end "exit 1 when an entry is replaced by a FIFO before its open, which is not attempted"
}

# Puts a symbolic link to identical content at a baseline entry after it has
# been opened and before the type of its name is read again. The entry is
# reported and neither measurement is taken. It covers the report made after the
# open. No command runs in the window between the builtin check and the open,
# and no case acts inside it.
st_case_source_became_symlink() {
  local path="" lines="" sha="" copy="" link=""
  st_begin "source-became-symlink"
  IFS='|' read -r path lines sha <<<"${BASELINE[0]}"
  copy="${ST_CASE_DIR}/late-identical-target"
  link="${ST_CASE_DIR}/late-link"
  if ! cp -p -- "${ST_REPO}/${path}" "$copy" || ! ln -s -- "$copy" "$link"; then
    fail_env "--self-test could not create the late symbolic link for ${path}"
  fi
  st_run_with_stat_shim "before" "$path" "no" '%F' \
    "$link" "${ST_REPO}/${path}" "" --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} became a symbolic link after it was validated expected_lines=${lines} actual_lines=(not read) expected_sha256=${sha} actual_sha256=(not read)"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  [[ -L "${ST_REPO}/${path}" ]] || st_note "the entry is not the late symbolic link"
  st_end "exit 1 when an entry name becomes a symbolic link after it was validated, entry not measured"
}

# Puts a FIFO at a baseline entry after it has been opened and before the type
# of its name is read again. The entry is reported by the type its name carries
# and neither measurement is taken. It covers the report made after the open. No
# command runs in the window between the builtin check and the open, and no case
# acts inside it.
st_case_source_became_fifo() {
  local path="" lines="" sha="" fifo=""
  st_begin "source-became-fifo"
  IFS='|' read -r path lines sha <<<"${BASELINE[0]}"
  fifo="${ST_CASE_DIR}/late-fifo"
  if ! mkfifo -- "$fifo"; then
    fail_env "--self-test could not create the late FIFO for ${path}"
  fi
  st_run_with_stat_shim "before" "$path" "no" '%F' \
    "$fifo" "${ST_REPO}/${path}" "" --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} became a fifo after it was validated expected_lines=${lines} actual_lines=(not read) expected_sha256=${sha} actual_sha256=(not read)"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  [[ -p "${ST_REPO}/${path}" ]] || st_note "the entry is not the late FIFO"
  st_end "exit 1 when an entry name becomes a FIFO after it was validated, entry not measured"
}

# Replaces a baseline entry with a different-content inode after the descriptor
# comparison and before the measurements. The digest and the line count come
# from the held inode, and the closing comparison reports the substitution.
st_case_source_swapped_measure() {
  local path="" lines="" sha="" copy=""
  st_begin "source-swapped-measure"
  IFS='|' read -r path lines sha <<<"${BASELINE[0]}"
  copy="${ST_CASE_DIR}/changed-copy"
  if ! cp -p -- "${ST_REPO}/${path}" "$copy"; then
    fail_env "--self-test could not copy ${path} for the measurement case"
  fi
  st_change_first_line "$copy"
  st_run_with_stat_shim "after" '/dev/fd/*' "yes" '%F|%i|%d' \
    "$copy" "${ST_REPO}/${path}" "" --stage self-test
  st_expect_exit "$EXIT_SOURCE"
  st_expect_output "FAIL ${path} replaced while it was measured expected_lines=${lines} actual_lines=${lines} expected_sha256=${sha} actual_sha256=${sha}"
  st_expect_output "gate A result: FAIL (1 of 5 baseline entries did not match)"
  st_expect_output "verdict: FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate B"
  st_end "exit 1 at gate A when an entry is substituted while it is measured through its descriptor"
}

st_case_base_dirty() {
  st_begin "base-dirty"
  printf '      *SELF-TEST TRACKED BASE FILE\n' >"${ST_REPO}/base/src/other.cbl"
  st_commit "self-test extra tracked base file"
  printf '      *SELF-TEST WORKING TREE CHANGE\n' >>"${ST_REPO}/base/src/other.cbl"
  printf 'self-test untracked\n' >"${ST_REPO}/base/src/scratch.txt"
  st_run --stage self-test
  st_expect_exit "$EXIT_BASE_DIRTY"
  st_expect_output "gate A result: PASS (5 of 5 baseline entries matched)"
  st_expect_output "M base/src/other.cbl"
  st_expect_output "?? base/src/scratch.txt"
  st_expect_output "gate B result: FAIL"
  st_expect_output "verdict: FAIL-BASE-WORKTREE-DIRTY"
  st_expect_no_output "gate C"
  st_end "exit 2 at gate B on a modified tracked and an untracked base/ path, gate C not reached"
}

st_case_tracked_outside() {
  local outside_rel="NOTES.txt"
  st_begin "tracked-outside"
  printf 'self-test tracked note\n' >"${ST_REPO}/${outside_rel}"
  st_commit "self-test tracked file outside the new-work prefix"
  printf 'self-test tracked note, modified\n' >"${ST_REPO}/${outside_rel}"
  printf '%s\njsonschema==4.26.0\n' "$SELF_TEST_MANIFEST_BODY" \
    >"${ST_REPO}/${SELF_TEST_MANIFEST_REL}"
  st_run --stage self-test
  st_expect_exit "$EXIT_TRACKED"
  st_expect_output "gate A result: PASS (5 of 5 baseline entries matched)"
  st_expect_output "gate B result: PASS"
  st_expect_output "    ${SELF_TEST_MANIFEST_REL}"
  st_expect_output "    ${outside_rel}"
  st_expect_output "  tracked paths outside ${NEW_WORK_PREFIX}: 1"
  st_expect_output "gate C result: FAIL"
  st_expect_output "verdict: FAIL-PREEXISTING-TRACKED-MODIFICATION"
  st_end "exit 3 at gate C on one tracked path outside ${NEW_WORK_PREFIX}, the prefix change filtered"
}

st_case_tool_list() {
  local declared="" expected="" tool=""
  st_begin "tool-list"
  for tool in "${REQUIRED_TOOLS[@]}"; do
    declared+="${declared:+ }${tool}"
  done
  for tool in "${SELF_TEST_EXPECTED_TOOLS[@]}"; do
    expected+="${expected:+ }${tool}"
  done
  if [[ "$declared" != "$expected" ]]; then
    st_note "preflight covers '${declared}', expected '${expected}'"
  fi
  st_end "preflight covers exactly ${expected}"
}

st_case_missing_tool() {
  local tool="$1"
  st_begin "tool-${tool}"
  st_run_without_tool "$tool" --stage self-test
  st_expect_exit "$EXIT_ENV"
  st_expect_output "required tool not found on PATH: ${tool}"
  st_expect_no_output "FAIL-SOURCE-INTEGRITY"
  st_expect_absent "${ST_REPO}/${LOG_DIR_REL}"
  st_end "exit 4, missing tool named, no source verdict, no log"
}

# Fails every status read of a held descriptor. The run then cannot inspect the
# descriptors the evidence log and gate A depend on.
st_case_descriptor_view() {
  st_begin "descriptor-view"
  st_run_with_failing_stat '/dev/fd/*' --stage self-test
  st_expect_exit "$EXIT_ENV"
  st_expect_output "status of a held descriptor through /dev/fd"
  st_expect_no_output "FAIL-SOURCE-INTEGRITY"
  st_expect_no_output "gate A"
  st_expect_absent "${ST_REPO}/${LOG_DIR_REL}"
  st_end "exit 4 when a held descriptor cannot be inspected, no source verdict and no log"
}

st_case_stage_injection() {
  local log_rel="${LOG_DIR_REL}/injection.log"
  st_begin "stage-injection"
  st_run --log "$log_rel" \
    --stage $'compile\nverdict: PASS\nexit_code: 0\nEND readonly-check\n\nBEGIN readonly-check\nstage: forged'
  st_expect_exit "$EXIT_ENV"
  st_expect_output "--stage accepts one to 64 characters"
  st_expect_output "received: compile\x0Averdict: PASS\x0Aexit_code: 0\x0AEND readonly-check\x0A\x0ABEGIN readonly-check\x0Astage: forged"
  st_expect_absent "${ST_REPO}/${LOG_DIR_REL}"
  st_end "exit 4, grammar named, label reported as one line of \\xNN escapes, nothing created"
}

# Runs last and needs no work tree: it compares the number of cases that have
# reported, plus itself, against the declared count.
st_case_case_count() {
  local reported=$((SELF_TEST_PASS + SELF_TEST_FAIL + 1))

  ST_CASE="case-count"
  ST_OK=1
  ST_DETAIL=""
  if ((reported != SELF_TEST_CASE_COUNT)); then
    st_note "${reported} case(s) reported, expected ${SELF_TEST_CASE_COUNT}"
  fi
  if ((ST_OK == 1)); then
    st_report "PASS" "${SELF_TEST_CASE_COUNT} declared cases all reported"
  else
    st_report "FAIL" "$ST_DETAIL"
  fi
}

st_case_positive_control() {
  local log_abs="" row="" path="" lines="" sha=""
  st_begin "positive-control"
  log_abs="${ST_REPO}/${DEFAULT_LOG_REL}"
  st_run --stage self-test
  st_expect_exit "$EXIT_OK"
  for row in "${BASELINE[@]}"; do
    IFS='|' read -r path lines sha <<<"$row"
    st_expect_output "PASS ${path} expected_lines=${lines} actual_lines=${lines} sha256=${sha}"
  done
  st_expect_output "gate A result: PASS (5 of 5 baseline entries matched)"
  st_expect_output "gate B result: PASS"
  st_expect_output "gate C result: PASS"
  st_expect_output "verdict: PASS"
  st_expect_exact_count "$log_abs" "BEGIN readonly-check" 1
  st_run --stage self-test-rerun --quiet
  st_expect_exit "$EXIT_OK"
  [[ -z "$ST_OUTPUT" ]] || st_note "--quiet wrote to stdout"
  st_expect_exact_count "$log_abs" "BEGIN readonly-check" 2
  st_expect_exact_count "$log_abs" "END readonly-check" 2
  st_expect_exact_count "$log_abs" "verdict: PASS" 2
  st_end "two clean runs, five PASS lines, appended blocks, quiet run silent"
}

# Runs every case in a throwaway tree and reports the counts. Returns 0 when
# every case passed and 5 otherwise.
run_self_test() {
  local tool="" row="" path="" created=""

  resolve_script_path
  preflight_tools
  preflight_descriptor_view
  for tool in "${SELF_TEST_TOOLS[@]}"; do
    require_tool "$tool"
  done

  if [[ "$SCRIPT_PATH" != */"${SELF_TEST_SCRIPT_REL}" ]]; then
    fail_env "--self-test expects this script at ${SELF_TEST_SCRIPT_REL}: $(sanitize "$SCRIPT_PATH")"
  fi
  if [[ ! -x "$SCRIPT_PATH" ]]; then
    fail_env "--self-test requires this script to be executable: $(sanitize "$SCRIPT_PATH")"
  fi
  SELF_TEST_ORIGIN="${SCRIPT_PATH%/"${SELF_TEST_SCRIPT_REL}"}"
  for row in "${BASELINE[@]}"; do
    IFS='|' read -r path _ _ <<<"$row"
    if [[ ! -f "${SELF_TEST_ORIGIN}/${path}" ]]; then
      fail_env "--self-test cannot read the baseline source $(sanitize "${SELF_TEST_ORIGIN}/${path}")"
    fi
  done

  if ! created="$(mktemp -d 2>/dev/null)" || [[ -z "$created" ]]; then
    fail_env "--self-test could not create a temporary directory"
  fi
  if ! SELF_TEST_ROOT="$(cd -P -- "$created" && printf '%s' "$PWD")" ||
    [[ -z "$SELF_TEST_ROOT" ]]; then
    fail_env "--self-test could not resolve its temporary directory: $(sanitize "$created")"
  fi
  trap self_test_cleanup EXIT

  printf 'self-test tree: %s\n' "$(sanitize "$SELF_TEST_ROOT")"
  printf 'self-test source repository: %s\n' "$(sanitize "$SELF_TEST_ORIGIN")"

  st_case_log_traversal
  st_case_log_empty
  st_case_log_authored_file
  st_case_log_absolute_outside
  st_case_log_absolute_inside
  st_case_log_basename
  st_case_log_symlinked_target
  st_case_log_symlinked_parent
  st_case_log_hard_link
  st_case_log_fifo
  st_case_log_open_failure
  st_case_log_unwritable_dir
  st_case_log_swapped_open
  st_case_log_became_symlink
  st_case_log_became_fifo
  st_case_log_name_swapped
  st_case_log_write_failure
  st_case_log_inode_stability
  st_case_log_dir_appeared
  st_case_log_dir_link_appeared
  st_case_source_symlink
  st_case_source_parent_symlink
  st_case_source_content_mismatch
  st_case_source_missing
  st_case_source_line_count
  st_case_source_non_regular
  st_case_source_swapped_open
  st_case_source_swap_symlink
  st_case_source_swap_fifo
  st_case_source_became_symlink
  st_case_source_became_fifo
  st_case_source_swapped_measure
  st_case_base_dirty
  st_case_tracked_outside
  st_case_tool_list
  for tool in "${SELF_TEST_EXPECTED_TOOLS[@]}"; do
    st_case_missing_tool "$tool"
  done
  st_case_descriptor_view
  st_case_stage_injection
  st_case_positive_control
  st_case_case_count

  self_test_cleanup
  printf 'self-test cases: %d passed, %d failed\n' "$SELF_TEST_PASS" "$SELF_TEST_FAIL"
  if ((SELF_TEST_FAIL > 0)); then
    printf '%s: error: --self-test recorded %d failing case(s)\n' \
      "$PROG" "$SELF_TEST_FAIL" >&2
    return "$EXIT_SELF_TEST"
  fi
  return "$EXIT_OK"
}

main() {
  local timestamp=""

  parse_args "$@"

  if ((SELF_TEST == 1)); then
    local self_test_code=0
    run_self_test || self_test_code=$?
    exit "$self_test_code"
  fi

  if ((BASELINE_ONLY == 1)); then
    print_baseline
    exit "$EXIT_OK"
  fi

  preflight_tools
  preflight_descriptor_view
  resolve_repo_root

  if ! timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; then
    fail_env "unable to read the current UTC time"
  fi

  open_log

  emit "BEGIN readonly-check"
  emit "stage: $(sanitize "$STAGE")"
  emit "timestamp_utc: ${timestamp}"
  emit "repository_root: $(sanitize "$REPO_ROOT")"
  emit "evidence_log: $(sanitize "$LOG_PATH")"
  print_baseline

  emit "preflight result: PASS"

  gate_a || finish "$EXIT_SOURCE" "FAIL-SOURCE-INTEGRITY"
  gate_b || finish "$EXIT_BASE_DIRTY" "FAIL-BASE-WORKTREE-DIRTY"
  gate_c || finish "$EXIT_TRACKED" "FAIL-PREEXISTING-TRACKED-MODIFICATION"

  finish "$EXIT_OK" "PASS"
}

main "$@"
