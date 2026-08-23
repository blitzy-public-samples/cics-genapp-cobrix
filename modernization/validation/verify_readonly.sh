#!/usr/bin/env bash
#
# verify_readonly.sh - read-only scope gate for the modernization bridge.
#
# Checks that the five authorized GenApp source artifacts are byte-identical to
# the baseline embedded in this script, and that no tracked repository file
# other than the generated evidence files the exempt inventory names has been
# modified.
#
# Invocation: this script runs standalone, is invoked by
# modernization/harness/run_harness.sh at four points of a harness run, and is
# invoked by the verify-readonly target of modernization/Makefile, which
# "make all" runs after each generating stage and as its final gate. The
# decision log referenced below is modernization/docs/decision-log.md.
#
# Stages, in execution order:
#   preflight  "git", "sha256sum", "wc", "date", "mkdir", "stat" and "flock"
#              are on PATH, a descriptor this shell holds can be inspected
#              through "/dev/fd/<number>", and the working directory resolves to
#              a git work tree.
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
#   gate C     "git diff --name-only HEAD" reports no tracked path other than
#              the generated evidence files the exempt inventory names. Every
#              reported path is evaluated, wherever in the repository it lies. A
#              path that equals one entry of that inventory - twenty-three exact
#              paths under "modernization/validation/artifacts/", each one a
#              file modernization/harness/run_harness.sh, the diff stage or a
#              stage of modernization/Makefile republishes on every run of that
#              stage - is recorded as exempt and is not
#              counted; every other reported
#              path, an authored path under "modernization/" included, is named
#              in the block, counted and fails the gate. The block records the
#              exempt inventory in full, then the exempt paths this run found
#              modified, then the tracked modifications it counted, each list
#              holding one escaped line per path or one marker line when it is
#              empty. The bytes of the block follow the tracked state the run
#              read.
#   gate D     Every exempt path of that inventory other than
#              "modernization/validation/artifacts/evidence-manifest.sha256"
#              that stands in the checkout is stated by one digest line of that
#              manifest, and every digest that manifest states matches the file
#              standing at the name it states. Gate C cannot compare an exempt
#              path with HEAD, because the run of its stage rewrites it; those
#              files carry the decisions of a run - the comparison report, the
#              recorded gate selection with the disposition of the target, the
#              version report, the probe logs, the compiler and harness output,
#              the dbt logs and the twelve files a harness run publishes - so
#              this gate measures their content instead. A line of the manifest
#              that is no digest line, a name it states that the inventory does
#              not name, a name it states twice, a stated name that is absent or
#              is not a regular file, a digest that does not match, and an exempt
#              path standing with no entry at all are each a finding naming the
#              path, with exit 6. A manifest that is absent while no other exempt
#              path stands in the checkout passes: nothing has been published
#              yet. The manifest carries no digest of itself, so a rewrite of an
#              artifact together with its manifest entry is not detected here and
#              the git history of the manifest is what carries that case; the
#              decision log records that limit. modernization/Makefile refreshes
#              the entries of the artifacts each of its stages rewrites through
#              --record-evidence, so the manifest is never stale.
#
# Evidence log location rules, all applied before anything is written:
#   - a supplied path is not empty, and an empty --log value never falls back to
#     the default;
#   - the path resolves inside the repository root, and that root is resolved
#     physically;
#   - its directory is exactly modernization/harness/build/logs, the generated
#     log directory of the harness, with no sub-directory, no trailing "/" and
#     no ".." component;
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
#   - once every one of those checks has passed, an exclusive lock is taken on
#     that descriptor and held until it closes: the blocks of two runs that
#     share one log follow one another in it, and no line of one block falls
#     between the lines of another. The wait for that lock is bounded at 60
#     seconds, and a lock that is not taken within that wait names the evidence
#     log on stderr and exits 4 with nothing appended;
#   - every line of the run is written through that descriptor, never through
#     the path a second time, and the descriptor is closed when the run block
#     ends, which releases the lock.
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
# Every run block carries a "status_label:" record holding the disposition of
# the target the run was validated against, written between the records that
# identify the run and the baseline it measured. The text is fixed and is
# written in both modes, so a block read on its own states that disposition.
#
# One record of a run block carries a value that differs between two runs of
# one stage: "timestamp_utc:" holds the UTC time of the run. --reproducible
# writes fixed text in place of it, and fixed text of its own in place of
# "repository_root:", keeping both keys and the order of the block, so two runs
# of one stage over one unchanged tracked state append byte-identical blocks in
# any checkout. Neither mode records the absolute path of a checkout: the
# default block names the root relative to itself. Nothing else changes: the
# same gates run, the same records are written, and the same exit codes are
# returned. In either mode the gate C records name the tracked state the run
# read: two runs of one stage record the same gate C bytes while that state is
# unchanged, and a run whose checkout carries a tracked modification records
# that path.
#
# Exit codes:
#   0  every gate passed
#   1  SHA-256 or line-count mismatch, or a missing, irregular or symlinked
#      source file, or a source whose type changed between its checks and its
#      open, or a source whose inode changed while it was measured
#   2  the base/ working tree is not clean
#   3  a tracked file the exempt inventory does not name has been modified
#   4  environment or usage error, including a rejected evidence log location, a
#      log whose type changed between its checks and its open, an exclusive lock
#      on the evidence log that is not taken within the bounded wait, and a
#      failed append to the evidence log
#   5  --self-test recorded at least one failing case
#   6  a generated evidence file is not covered by the manifest of its set, or
#      does not match the digest that manifest states
#
# Any non-zero code stops the fail-fast modernization/Makefile, which invokes
# this script through its verify-readonly target.
#
# Accepted argument values:
#   --stage  one to 64 characters, starting with a letter or a digit and
#            continuing with letters, digits, ".", "_" or "-". Any other value,
#            including an empty value or one carrying whitespace, a control
#            character or a shell metacharacter, is a usage error and exits 4.
#   --log    a path that names a file directly inside
#            modernization/harness/build/logs/: that directory, then one name
#            starting with a letter or a digit and continuing with letters,
#            digits, ".", "_" or "-". No path below a subdirectory of that
#            directory is accepted, so the only directory this script ever
#            creates is modernization/harness/build/logs/ itself, which the
#            ignore rules of modernization/.gitignore cover. An absolute
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
#            resolve inside modernization/harness/build/logs/, and must not be
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
#            Nothing is appended, and the run exits 4. A descriptor that passes
#            every one of those checks then carries an exclusive lock, taken
#            before the first record and held until that descriptor closes: two
#            runs appending to one log write their blocks one after the other,
#            and no line of one block falls between the lines of another. The
#            wait for that lock is bounded at 60 seconds; a lock that is not
#            taken within that wait names the evidence log on stderr, appends
#            nothing and exits 4.
#   --reproducible
#            records the run block with fixed text in place of the two values
#            that would otherwise identify the run: "timestamp_utc:" reads
#            "not recorded (--reproducible)" and "repository_root:" reads
#            "this checkout (--reproducible)". The clock is not read at all in
#            this mode. Without it, the block records the UTC time of the run
#            and names the root relative to itself. It takes no value, and it
#            changes no gate, no other record and no exit code.
#
# Generated-output policy: one policy governs every path this bridge writes. A
# generated record, a translated copy and a generated evidence log all resolve
# inside modernization/harness/build/. Every destination is canonicalised
# through its symbolic links before anything is created, a symbolic link and an
# existing non-regular target are refused, no authored or source path is
# reachable, and every value carried into a diagnostic or an evidence record is
# escaped to one control-free line. An evidence log names one file directly
# inside modernization/harness/build/logs/, that directory is created and
# entered one component at a time so each creation and the open address a single
# name in the directory the process holds rather than a multi-component
# pathname, and the log is additionally validated after it is opened: the opened
# object is a single-link regular file inside
# modernization/harness/build/logs/, it is the exact entry the run resolved as
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
# the only file a verification run writes, every append reaches it through the
# one descriptor opened for it and closed when the run finishes; --record-evidence
# writes the manifest of the generated evidence set and nothing else, runs no
# gate and opens no evidence log. Neither mode performs network access or runs a
# git command that alters repository state. One run
# at a time appends to a given evidence log: a run holds an exclusive lock on
# that log for its whole duration, the blocks of concurrent runs land in the log
# one after another, and each block stays contiguous. The wait for that lock is
# bounded at 60 seconds, and a lock that is not taken within that wait exits 4
# without appending.
#
# --self-test builds a throwaway git work tree under a temporary directory,
# copies the five source artifacts and this script into it, commits them, and
# then asserts one case at a time: rejected log locations, a symlinked log
# target, a symlinked log directory, a hard-linked log target, a FIFO log
# target, a log whose open cannot succeed, a log directory whose mode is
# reduced, a log replaced between its open and its status read, a log whose
# name becomes a symbolic link and a log whose name becomes a FIFO between its
# open and its status read, a log whose append does not complete, the inode of
# a log across two runs, three --reproducible runs of one stage from two
# checkout paths beside one run without that option, four runs appending to one
# log at the same time, a log whose exclusive lock another descriptor already
# holds, an evidence directory that appears while this run creates it, an
# evidence directory a symbolic link takes over while this run creates it, a
# committed symlinked source, a committed symlinked source directory, a FIFO
# and a directory in place of sources, a committed source content change, a
# removed source, a source whose line count and digest both moved, a source
# replaced between its status read and its open, a source replaced by a
# symbolic link and a source replaced by a FIFO between its status read and its
# open, a source whose name becomes a symbolic link and a source whose name
# becomes a FIFO between its open and the status read that follows it, a source
# replaced while it is measured through its descriptor, an unclean base/
# working tree, a modified tracked file outside modernization/ beside a
# modified tracked authored file under it, a modified tracked authored file
# under modernization/ over two runs of one stage, every exempt generated
# evidence path modified at once, two modified tracked paths under the published
# evidence directory that the exempt inventory does not name, one missing
# required tool per case, a failing status read of a held descriptor, an
# injected --stage label, clean positive runs, and the declared case count. The
# case that modifies a tracked authored file under modernization/ compares the
# gate C records of its two runs line by line and reads its log back for two
# identical blocks, and the case that modifies every exempt generated evidence
# path reads its log back for two lines per exempt path: the inventory line and
# the line that records it as modified. The substitution cases and the
# descriptor-status case drive their fault through a "stat" shim placed ahead
# of PATH that otherwise forwards every call to the real tool. The two
# evidence-directory cases drive theirs through a "mkdir" shim placed ahead of
# PATH that places one name, writes its own stderr line and reports a failure
# for the single-component creation it selects, and that otherwise forwards
# every call to the real tool. The incomplete append is driven by a file-size
# limit with SIGXFSZ ignored. The concurrent case starts its four runs at once
# against one log and then reads that log back for balanced markers, one
# verdict per run and no BEGIN marker opened inside another block. The
# held-lock case holds an exclusive lock on the evidence log through a
# descriptor of its own, which the run it starts does not inherit and which is
# closed as soon as that run returns, and drives that run's wait through a
# "flock" shim placed ahead of PATH: the shim records the bounded wait each
# call asks for, hands the real tool a shorter one, supplies a bounded wait to
# a call that carries none, and forwards every other argument, the descriptor
# and the exit status unchanged. That case asserts the recorded wait, the exit
# code, the diagnostic and the digest of the log. No option and no environment
# value of a verification run changes the wait that run asks for. No case
# drives a substitution into the window that holds no command, between a
# builtin check and the open that follows it. It prints one PASS or FAIL line
# per case plus a count summary, checks after every case that nothing was
# written outside the throwaway tree, removes that tree on exit, and writes no
# path in the repository it is started from. It runs alone: no other option may
# accompany it.
#
# Options and per-option behavior are listed by --help.
#
# The harness topology this script belongs to is drawn in
# Figure 5 — Validation Harness Control Flow in modernization/docs/architecture.md.
# Decisions taken for this script will be recorded in
# modernization/docs/decision-log.md.

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

# Repository-relative paths gate C exempts, one exact path each, in three
# groups. The first twelve are the ones modernization/harness/run_harness.sh
# publishes, in the order it publishes them: its five stage files
# (PUBLISHED_STAGE_ARTIFACTS), the manifest of the run
# (EVIDENCE_MANIFEST_NAME), and the driver log, the capture file and the
# post-chain record of each of its two success cases (SUCCESS_CASES). Every run
# of that script replaces those twelve tracked files. The next two are the
# comparison reports modernization/validation/diff_harness_vs_warehouse.py
# rewrites on every run of the diff stage, each one carrying the time of the run
# it reports. The last nine are the stage records modernization/Makefile
# rewrites, in the order its "all" target produces them: the version report of
# verify-env, the recorded selection and the two probe logs of gate, the
# compiler output of compile, the harness output of execute, and the clean, run
# and test output of dbt. Each of those nine carries the time, the measured
# values or the tool output of the run that wrote it, so a re-run of the same
# stage over one unchanged tracked state replaces it. A reported path is exempt
# only when it equals one of these strings: no prefix, no directory and no
# pattern is exempt, so every other tracked path under
# modernization/validation/artifacts/ - runtime-versions.txt, which no harness
# run and no Makefile stage writes, included - is evaluated by gate C like any
# other tracked path.
readonly GENERATED_EVIDENCE_EXEMPT=(
  "modernization/validation/artifacts/translate.log"
  "modernization/validation/artifacts/compile.log"
  "modernization/validation/artifacts/translation-report.json"
  "modernization/validation/artifacts/source-baseline.sha256"
  "modernization/validation/artifacts/readonly-check.log"
  "modernization/validation/artifacts/evidence-manifest.sha256"
  "modernization/validation/artifacts/driver_01amot.log"
  "modernization/validation/artifacts/captures_01amot.txt"
  "modernization/validation/artifacts/commarea_post_01amot.dat"
  "modernization/validation/artifacts/driver_01acom.log"
  "modernization/validation/artifacts/captures_01acom.txt"
  "modernization/validation/artifacts/commarea_post_01acom.dat"
  "modernization/validation/artifacts/diff-report.md"
  "modernization/validation/artifacts/diff-report.json"
  "modernization/validation/artifacts/verify-env.txt"
  "modernization/validation/artifacts/gate-selection.json"
  "modernization/validation/artifacts/gate-probe-s3.log"
  "modernization/validation/artifacts/gate-probe-redshift.log"
  "modernization/validation/artifacts/compile-modules.log"
  "modernization/validation/artifacts/execute-harness.log"
  "modernization/validation/artifacts/dbt-clean.log"
  "modernization/validation/artifacts/dbt-run.log"
  "modernization/validation/artifacts/dbt-test.log"
)

# Directory every entry of that inventory stands in, and the manifest of the
# set, both relative to the repository root. Gate C cannot judge the content of
# an exempt path, because every one of them is rewritten by the run that
# produces it; the manifest carries the SHA-256 of each of the others, and gate D
# measures the set against it. The manifest is itself an exempt entry and carries
# no digest of its own: no file can hash itself.
# Decisions taken for this coverage are recorded in
# modernization/docs/decision-log.md.
readonly EVIDENCE_DIR_REL="modernization/validation/artifacts"
readonly EVIDENCE_MANIFEST_REL="${EVIDENCE_DIR_REL}/evidence-manifest.sha256"

# Accepted digest of a manifest line: 64 lower-case hexadecimal characters, the
# form "sha256sum" writes and "sha256sum --check" reads.
readonly EVIDENCE_DIGEST_PATTERN='^[0-9a-f]{64}$'

# External tools --record-evidence invokes in addition to REQUIRED_TOOLS: the
# refreshed manifest is written beside the manifest and renamed over it in one
# step, so a refresh that stops part way leaves the manifest exactly as it
# stands. A verification run invokes neither.
readonly RECORD_TOOLS=(mv rm chmod)

# Mode the refreshed manifest carries. It is set on the temporary entry before
# the rename, so the manifest a refresh leaves behind carries this mode whatever
# the ambient umask of the caller and whatever mode the name carried before, in
# step with every other generated artifact of this bridge.
# Decision rationale: modernization/docs/decision-log.md, row D-127.
readonly EVIDENCE_MANIFEST_MODE=600

# Header of a manifest this script creates, written when a stage refreshes an
# entry in a checkout that carries no manifest yet - the first stage of a run
# that reaches an exempt artifact before the harness has published a set. The
# text is fixed, so two refreshes over one state write the same header, and a
# harness run replaces the whole manifest with the set it publishes.
readonly -a EVIDENCE_MANIFEST_CREATED_HEADER=(
  "# verify_readonly.sh evidence manifest: the generated evidence set of this checkout"
  "# status label:        validated against local substitute, not AWS"
  "# provenance:          created by verify_readonly.sh --record-evidence; a harness"
  "#                      run replaces it with the set that run publishes, and each"
  "#                      later stage refreshes its own entries through the same option"
  "# coverage:            one digest line per generated evidence path the exempt"
  "#                      inventory of verify_readonly.sh names, this manifest excepted"
  "# outside this set:    runtime-versions.txt, the environment record of the checkout"
)

# The only directory an evidence log may live in, relative to the repository
# root. No sub-directory of it is accepted. It is a generated directory covered
# by the ignore rules of modernization/.gitignore, so a run of this script
# changes no tracked file. The harness publishes the log it collects under
# modernization/validation/artifacts/readonly-check.log, one entry of the
# evidence set it replaces in one step once every gate has passed.
# Decisions taken for this script are recorded in
# modernization/docs/decision-log.md.
readonly LOG_DIR_REL="modernization/harness/build/logs"

# Evidence log used when --log is not supplied, relative to the repository root.
readonly DEFAULT_LOG_REL="${LOG_DIR_REL}/readonly-check.log"

# Value the "repository_root" record of an evidence block carries. Every path a
# block names - the baseline entries, the evidence log and the paths git
# reports - is repository-relative, and this record names the "." those paths
# are relative to; no block records the absolute path of a checkout. A
# diagnostic that rejects a path names the root it resolved.
# Decisions taken for this script are recorded in
# modernization/docs/decision-log.md.
readonly REPO_ROOT_DISPLAY=". (every path of this block is relative to the repository root)"

# Longest a run waits for the exclusive lock on the evidence log, in seconds. A
# wait that reaches it ends the run with exit 4 and appends nothing.
readonly LOG_LOCK_WAIT_SECONDS=60

# Text --reproducible records in the two run-block lines that would otherwise
# identify the run: the UTC time of the run and the root the block's paths are
# relative to. Both keys keep their place in the block, the clock is not read in
# that mode, and neither text names a checkout path.
readonly REPRODUCIBLE_TIMESTAMP_TEXT="not recorded (--reproducible)"
readonly REPRODUCIBLE_ROOT_TEXT="this checkout (--reproducible)"

# Disposition of the target this run was validated against, recorded by the
# "status_label:" line of every run block in the "key: value" form the other
# header records of a block take. The text is fixed, so the record stands in
# both modes and a block read on its own states the disposition it was written
# under.
readonly STATUS_LABEL_TEXT="validated against local substitute, not AWS"

# External tools every verification run invokes, in first-use order. A missing
# entry is an environment error, reported before the evidence log is opened.
readonly REQUIRED_TOOLS=(git sha256sum wc date mkdir stat flock)

# External tools --self-test invokes in addition to REQUIRED_TOOLS.
readonly SELF_TEST_TOOLS=(mktemp cp ln rm mv mkfifo chmod)

# Accepted --stage value: one to 64 characters, leading alphanumeric, then
# alphanumerics, ".", "_" or "-".
readonly STAGE_PATTERN='^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$'

# Accepted --log characters: an optional leading "/", a leading alphanumeric,
# then alphanumerics, ".", "_", "-" or "/".
readonly LOG_PATH_PATTERN='^/?[A-Za-z0-9][A-Za-z0-9._/-]*$'

# Accepted evidence log name: the one path component that follows
# modernization/harness/build/logs/, a leading alphanumeric then
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
readonly EXIT_EVIDENCE=6

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

# 1 once --record-evidence has been accepted, with the repository-relative paths
# it named in RECORD_PATHS. That mode refreshes the manifest entries of those
# paths and runs no gate.
RECORD_MODE=0
RECORD_PATHS=()

# SHA-256 of the last file read by evidence_file_digest, or empty when that read
# reported a failure.
EVIDENCE_DIGEST=""

# 1 once --reproducible has been accepted: the run block then records fixed text
# in place of the UTC time of the run and the absolute repository root.
REPRODUCIBLE=0

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
embedded in this script and that no tracked repository file other than the
generated evidence files the exempt inventory names has been modified.

Options:
  --stage NAME      Label recorded with this run, such as translate, compile,
                    execute, load, dbt, diff or final. Control bytes, non-ASCII
                    bytes and backslashes in the label are emitted as "\xNN"
                    escapes. Default: unspecified.
  --log PATH        Evidence log to append to. Must resolve to a ".log" file
                    directly inside modernization/harness/build/logs within
                    this repository, reached without a symbolic link, and must
                    be a regular file with exactly one hard link; any other
                    location is rejected with exit 4 and nothing is written.
                    That directory is generated and ignored, so a run of this
                    script changes no tracked file; the harness publishes the
                    log it collects as part of its evidence set.
                    The log is opened once onto a descriptor held for the whole
                    run, every line is written through that descriptor, and an
                    append that fails is reported on stderr only and exits 4. A
                    path that stops being a regular file between its checks and
                    its open, or between that open and the status read that
                    follows it, is reported with exit 4 and no line is written.
                    The run then holds an exclusive lock on that descriptor until
                    it closes: runs that share one log append their blocks one
                    after another, and no line of one block falls between the
                    lines of another. That wait is bounded at 60 seconds, and a
                    lock that is not taken within it names the log on stderr,
                    appends nothing and exits 4.
                    Default:
                    modernization/harness/build/logs/readonly-check.log
  --reproducible    Record the run block with fixed text in place of the two
                    values that vary between runs and between checkouts:
                    "timestamp_utc:" reads "not recorded (--reproducible)" and
                    "repository_root:" reads "this checkout (--reproducible)".
                    The clock is not read in this mode. Two runs of one stage
                    over one unchanged tracked state then append byte-identical
                    blocks in any checkout. Every gate, every other record and
                    every exit code are unchanged. Without it, the block records
                    the UTC time of the run; the root is recorded relative to
                    itself in both modes, so neither carries the absolute path
                    of one checkout. In either mode the gate C records name the
                    tracked state the run read, so a run whose checkout carries
                    a tracked modification records that path.
  --baseline-only   Print the embedded baseline and exit 0. Runs no gate,
                    invokes no external tool and writes no log.
  --quiet           Suppress stdout. The evidence log is still written.
  --self-test       Run the built-in negative and positive cases in a throwaway
                    git work tree, print one PASS or FAIL line per case with a
                    count summary, and write nothing in this repository. Exits
                    0 when every case passes and 5 when any case fails. Runs
                    alone: no other option may accompany it.
  --record-evidence PATH...
                    Refresh the manifest entry of every named generated evidence
                    file and leave every other line of
                    modernization/validation/artifacts/evidence-manifest.sha256
                    byte-identical, so the manifest gate D measures follows the
                    artifacts a stage has just rewritten. Each PATH is a
                    repository-relative path of the exempt generated evidence
                    inventory other than the manifest itself, and must be a
                    regular file that is not a symbolic link; any other value is
                    a usage error with exit 4 and the manifest is left exactly as
                    it stands. The refreshed manifest is written beside it and
                    renamed over it in one step. A checkout that carries no
                    manifest receives one whose header states that provenance.
                    Runs no gate, opens no evidence log, and accepts no other
                    option.
  -h, --help        Print this message and exit 0.

Stages, in execution order:
  preflight  "git", "sha256sum", "wc", "date", "mkdir", "stat" and "flock" are
             on PATH, a descriptor this shell holds can be inspected through
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
  gate C     "git diff --name-only HEAD" reports no tracked path other than the
             generated evidence files the exempt inventory names. Every reported
             path is evaluated, wherever in the repository it lies. A path that
             equals one entry of that inventory - twenty-three exact paths under
             modernization/validation/artifacts/, each one a file
             modernization/harness/run_harness.sh, the diff stage or a stage of
             modernization/Makefile republishes on every run of that stage - is
             recorded as exempt and is not counted; every
             other reported path,
             an authored path under modernization/ included, is named in the
             block, counted and fails the gate. The block records the exempt
             inventory in full, then the exempt paths this run found modified,
             then the tracked modifications it counted, each list holding one
             escaped line per path or one marker line when it is empty. The
             bytes of the block follow the tracked state the run read.
  gate D     Every exempt path of that inventory other than the manifest that
             stands in the checkout is stated by one digest line of
             modernization/validation/artifacts/evidence-manifest.sha256, and
             every digest that manifest states matches the file standing at the
             name it states. Gate C cannot compare an exempt path with HEAD, so
             this gate measures the content of those files, which carry the
             decisions of a run. A malformed line, a name outside the inventory,
             a name stated twice, a stated name that is absent or irregular, a
             digest that does not match, and an exempt path standing with no
             entry are each a finding naming the path, with exit 6. An absent
             manifest passes only while no other exempt path stands in the
             checkout. The manifest carries no digest of itself, so a rewrite of
             an artifact together with its own entry is not detected here.

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
  3  a tracked file the exempt inventory does not name has been modified
  4  environment or usage error, including a rejected evidence log location, a
     log whose type changed between its checks and its open, an exclusive lock
     on the evidence log that is not taken within the bounded wait, and a failed
     append to the evidence log
  5  --self-test recorded at least one failing case
  6  a generated evidence file is not covered by the manifest of its set, or does
     not match the digest that manifest states
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

# Closes the held evidence-log descriptor, which releases the exclusive lock
# that descriptor carries. Writes nothing and is a no-op when no log is open.
# Process exit closes the descriptor and releases that lock as well.
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
      --reproducible)
        REPRODUCIBLE=1
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
      --record-evidence)
        RECORD_MODE=1
        shift
        ;;
      -h | --help)
        usage
        exit "$EXIT_OK"
        ;;
      *)
        # Every argument that follows --record-evidence and does not open with
        # "-" is one path of the refresh; any other bare argument is a usage
        # error, as it is for every other mode of this script.
        if ((RECORD_MODE == 1)) && [[ "$1" != -* ]]; then
          RECORD_PATHS+=("$1")
          shift
          continue
        fi
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
    if ((STAGE_SET == 1 || BASELINE_ONLY == 1 || QUIET == 1 || LOG_SET == 1 ||
      REPRODUCIBLE == 1 || RECORD_MODE == 1)); then
      fail_usage "--self-test accepts no other option"
    fi
  fi
  if ((RECORD_MODE == 1)); then
    if ((STAGE_SET == 1 || BASELINE_ONLY == 1 || QUIET == 1 || LOG_SET == 1 ||
      REPRODUCIBLE == 1)); then
      fail_usage "--record-evidence accepts no other option"
    fi
    ((${#RECORD_PATHS[@]} > 0)) ||
      fail_usage "--record-evidence requires at least one repository-relative generated evidence path"
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
# appending onto one descriptor, confirms that the descriptor and the path name
# the same regular file with a single hard link, and takes an exclusive lock on
# that descriptor once every one of those checks has passed. Every rejection
# closes the descriptor and exits 4 before anything is written. The recorded path
# stays repository-relative and is used for the evidence line only; all writing
# goes through the descriptor, which holds the lock until it closes.
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

  # Taken on the validated descriptor, held until that descriptor closes, and
  # waited for at most LOG_LOCK_WAIT_SECONDS. The tool's own stderr is
  # discarded, leaving this script's one-line summary as the only record.
  if ! flock -x -w "$LOG_LOCK_WAIT_SECONDS" "$fd" 2>/dev/null; then
    exec {fd}>&-
    fail_env "unable to take the exclusive lock on the evidence log within ${LOG_LOCK_WAIT_SECONDS} seconds: $(sanitize "$rel")"
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

# Reports whether the supplied path, exactly as "git diff --name-only HEAD"
# printed it, equals one entry of GENERATED_EVIDENCE_EXEMPT. The comparison is
# string equality over the whole path: no prefix, no directory and no pattern
# matches, and a path git printed in any other form than one of those strings
# does not match. Returns 0 for an exempt path and 1 for every other path.
evidence_exempt_path() {
  local candidate="$1" entry=""

  for entry in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    if [[ "$candidate" == "$entry" ]]; then
      return 0
    fi
  done
  return 1
}

# Gate C: no tracked path differs from HEAD except the generated evidence files
# GENERATED_EVIDENCE_EXEMPT names by exact path.
#
# Every path "git diff --name-only HEAD" reports is evaluated, wherever in the
# repository it lies: a tracked path whose content differs from HEAD, staged or
# not, and a removed tracked path alike. A reported path that equals an exempt
# entry is recorded as exempt and is not counted; every other reported path - an
# authored path under modernization/, a path outside it, and a path under
# modernization/validation/artifacts/ the inventory does not name alike - is
# recorded, counted and fails the gate. The block records the exempt inventory
# in full, then the exempt paths this run found modified, then the tracked
# modifications it counted, each list holding one sanitized line per path or one
# marker line when it is empty: a reported path the gate does not count is named
# in the exempt list of the block. The two count lines report the size of each
# list, and a non-zero count of tracked modifications emits the count on stderr
# and returns the gate as EXIT_TRACKED. The bytes of these records follow
# the tracked state the run read: two runs of one stage record the same records
# while that state is unchanged, and a run whose checkout carries a tracked
# modification records that path.
# Decisions taken for this gate are recorded in
# modernization/docs/decision-log.md.
gate_c() {
  local output="" line="" entry="" count=0 exempt_count=0
  local exempted=() named=()

  emit "gate C no tracked modification outside the generated evidence set:"
  if ! output="$(git diff --name-only HEAD 2>&1)"; then
    fail_env "git diff --name-only HEAD did not complete: $(sanitize "$output")"
  fi

  if [[ -n "$output" ]]; then
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      if evidence_exempt_path "$line"; then
        exempted+=("$(sanitize "$line")")
      else
        named+=("$(sanitize "$line")")
      fi
    done <<<"$output"
  fi
  exempt_count="${#exempted[@]}"
  count="${#named[@]}"

  printf -v line '  exempt generated evidence paths, matched by exact path (%d):' \
    "${#GENERATED_EVIDENCE_EXEMPT[@]}"
  emit "$line"
  for entry in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    emit "    ${entry}"
  done

  emit "  git diff --name-only HEAD, exempt paths modified:"
  if ((exempt_count == 0)); then
    emit "    (no exempt generated evidence path modified)"
  else
    for entry in "${exempted[@]}"; do
      emit "    ${entry}"
    done
  fi

  emit "  git diff --name-only HEAD, tracked modifications:"
  if ((count == 0)); then
    emit "    (no tracked modification)"
  else
    for entry in "${named[@]}"; do
      emit "    ${entry}"
    done
  fi

  printf -v line '  exempt generated evidence paths modified: %d' "$exempt_count"
  emit "$line"
  printf -v line '  tracked modifications: %d' "$count"
  emit "$line"

  if ((count == 0)); then
    emit "gate C result: PASS"
    return 0
  fi

  emit "gate C result: FAIL"
  printf '%s: error: gate C %d tracked file(s) modified outside the generated evidence set, named in the evidence block\n' \
    "$PROG" "$count" >&2
  return 1
}

# Prints what the supplied path is, in the vocabulary the diagnostics of gate D
# and of the manifest refresh use. Reads the path without following a symbolic
# link and with shell builtins only.
evidence_kind() {
  local path="$1"

  if [[ -L "$path" ]]; then
    printf '%s' "a symbolic link"
  elif [[ ! -e "$path" ]]; then
    printf '%s' "absent"
  elif [[ -d "$path" ]]; then
    printf '%s' "a directory"
  elif [[ -p "$path" ]]; then
    printf '%s' "a fifo"
  elif [[ ! -f "$path" ]]; then
    printf '%s' "not a regular file"
  else
    printf '%s' "a regular file"
  fi
}

# Prints the name one exempt inventory entry carries inside the evidence
# directory: the entry with that directory and its separator removed.
evidence_entry_name() {
  printf '%s' "${1#"${EVIDENCE_DIR_REL}/"}"
}

# Reports whether the supplied name, exactly as a manifest digest line carries
# it, is the name of one exempt inventory entry other than the manifest itself.
# The comparison is string equality over the whole repository-relative path the
# name would form, so a name carrying a "/" component, a ".." component or the
# name of a file outside the inventory matches nothing.
evidence_covered_name() {
  local candidate="$1" entry=""

  for entry in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    if [[ "$entry" == "$EVIDENCE_MANIFEST_REL" ]]; then
      continue
    fi
    if [[ "$entry" == "${EVIDENCE_DIR_REL}/${candidate}" ]]; then
      return 0
    fi
  done
  return 1
}

# Reports whether the supplied value equals one entry of the exempt inventory,
# by string equality over the whole path.
evidence_inventory_path() {
  local candidate="$1" entry=""

  for entry in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    if [[ "$entry" == "$candidate" ]]; then
      return 0
    fi
  done
  return 1
}

# Reads the SHA-256 of one generated evidence file into EVIDENCE_DIGEST. A
# symbolic link, an absent path, a path that is not a regular file and a file
# that cannot be read each leave EVIDENCE_DIGEST empty and return 1, so the
# caller reports the path rather than a digest of something else.
evidence_file_digest() {
  local path="$1" line=""

  EVIDENCE_DIGEST=""
  if [[ -L "$path" || ! -f "$path" ]]; then
    return 1
  fi
  if ! line="$(sha256sum -- "$path" 2>/dev/null)" || [[ -z "$line" ]]; then
    return 1
  fi
  if [[ ! "${line%% *}" =~ $EVIDENCE_DIGEST_PATTERN ]]; then
    return 1
  fi
  EVIDENCE_DIGEST="${line%% *}"
  return 0
}

# Records one gate D finding: the reason in the evidence block, the verdict line
# that closes the gate, and a one-line summary on stderr. The caller returns 1
# immediately afterwards, so the first difference the gate meets is the one it
# reports.
gate_d_fail() {
  emit "  finding: $1"
  emit "gate D result: FAIL"
  printf '%s: error: gate D %s\n' "$PROG" "$1" >&2
}

# Gate D: every generated evidence file the exempt inventory names is covered by
# the manifest of its set, and every digest that manifest states matches the file
# standing in the checkout.
#
# Gate C exempts twenty-three exact paths because every one of them is rewritten
# by the run of the stage that produces it, so its content cannot be compared
# with HEAD. That leaves their content unmeasured by git, and those files carry
# the decisions of a run: the comparison report of the diff stage, the recorded
# gate selection with the disposition of the target, the version report, the
# probe logs, the compiler and harness output, the dbt logs and the twelve files
# a harness run publishes. This gate measures them against
# modernization/validation/artifacts/evidence-manifest.sha256, which the harness
# writes for the set it publishes and which every later stage refreshes for the
# artifact it rewrites, through --record-evidence.
#
# The gate holds when, in inventory order:
#   - the manifest is a regular file that is not a symbolic link, or is absent
#     while no other exempt path stands in the checkout, which is a checkout
#     where no stage has published anything yet;
#   - every line of it is a comment, an empty line, or a digest line of 64
#     lower-case hexadecimal characters, two spaces and the name of an exempt
#     entry other than the manifest, stated once;
#   - every stated name is a regular file whose SHA-256 equals the stated digest;
#   - every exempt path other than the manifest that stands in the checkout is
#     stated by a line of the manifest.
# A difference of any of those is a finding: the path is named in the evidence
# block and on stderr, and the run exits EXIT_EVIDENCE. A file whose digest was
# rewritten together with its manifest entry is not detected by this gate - a
# manifest cannot cover itself - and the git history of the manifest is what
# carries that case; modernization/docs/decision-log.md, row D-121, records that
# limit.
gate_d() {
  local entry="" name="" line="" digest="" count=0 covered=0
  local -A stated=()
  local -a lines=() present=() uncovered=()

  emit "gate D generated evidence covered by the manifest of its set:"
  emit "  manifest: ${EVIDENCE_MANIFEST_REL}"

  for entry in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    if [[ "$entry" == "$EVIDENCE_MANIFEST_REL" ]]; then
      continue
    fi
    if [[ -e "$entry" || -L "$entry" ]]; then
      present+=("$entry")
    fi
  done
  printf -v line '  generated evidence paths standing in this checkout: %d of %d' \
    "${#present[@]}" "$((${#GENERATED_EVIDENCE_EXEMPT[@]} - 1))"
  emit "$line"

  if [[ ! -e "$EVIDENCE_MANIFEST_REL" && ! -L "$EVIDENCE_MANIFEST_REL" ]]; then
    if ((${#present[@]} == 0)); then
      emit "  digest lines: 0"
      emit "  covered by a matching digest: 0"
      emit "  standing without an entry:"
      emit "    (no generated evidence path stands in this checkout)"
      emit "  paths the manifest does not cover: 0"
      emit "gate D result: PASS"
      return 0
    fi
    emit "  standing without an entry:"
    for entry in "${present[@]}"; do
      emit "    ${entry}"
    done
    gate_d_fail "the manifest ${EVIDENCE_MANIFEST_REL} is absent while ${#present[@]} generated evidence path(s) stand in this checkout, each named in the evidence block"
    return 1
  fi
  if [[ -L "$EVIDENCE_MANIFEST_REL" || ! -f "$EVIDENCE_MANIFEST_REL" ]]; then
    gate_d_fail "the manifest ${EVIDENCE_MANIFEST_REL} is $(evidence_kind "$EVIDENCE_MANIFEST_REL")"
    return 1
  fi

  mapfile -t lines <"$EVIDENCE_MANIFEST_REL"
  for line in "${lines[@]}"; do
    case "$line" in
      '#'* | '')
        continue
        ;;
    esac
    if ((${#line} < 67)) || [[ "${line:64:2}" != "  " ]] ||
      [[ ! "${line:0:64}" =~ $EVIDENCE_DIGEST_PATTERN ]]; then
      gate_d_fail "the manifest carries a line that is no digest line: $(sanitize "$line")"
      return 1
    fi
    digest="${line:0:64}"
    name="${line:66}"
    if ! evidence_covered_name "$name"; then
      gate_d_fail "the manifest states $(sanitize "$name"), which the exempt inventory does not name as a covered generated evidence path"
      return 1
    fi
    if [[ -n "${stated[$name]+set}" ]]; then
      gate_d_fail "the manifest states $(sanitize "$name") more than once"
      return 1
    fi
    stated["$name"]="$digest"
    count=$((count + 1))
  done
  printf -v line '  digest lines: %d' "$count"
  emit "$line"

  for entry in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    if [[ "$entry" == "$EVIDENCE_MANIFEST_REL" ]]; then
      continue
    fi
    name="$(evidence_entry_name "$entry")"
    if [[ -z "${stated[$name]+set}" ]]; then
      if [[ -e "$entry" || -L "$entry" ]]; then
        uncovered+=("$entry")
      fi
      continue
    fi
    if ! evidence_file_digest "$entry"; then
      gate_d_fail "the manifest states ${entry}, which is $(evidence_kind "$entry")"
      return 1
    fi
    if [[ "$EVIDENCE_DIGEST" != "${stated[$name]}" ]]; then
      gate_d_fail "${entry} does not match the digest its manifest entry states"
      return 1
    fi
    covered=$((covered + 1))
  done
  printf -v line '  covered by a matching digest: %d' "$covered"
  emit "$line"

  emit "  standing without an entry:"
  if ((${#uncovered[@]} == 0)); then
    emit "    (every generated evidence path standing in this checkout is covered)"
  else
    for entry in "${uncovered[@]}"; do
      emit "    ${entry}"
    done
  fi
  printf -v line '  paths the manifest does not cover: %d' "${#uncovered[@]}"
  emit "$line"

  if ((${#uncovered[@]} == 0)); then
    emit "gate D result: PASS"
    return 0
  fi
  gate_d_fail "${#uncovered[@]} generated evidence path(s) stand with no entry in ${EVIDENCE_MANIFEST_REL}, each named in the evidence block"
  return 1
}

# Prints one line of the manifest refresh on stdout. The refresh writes no
# evidence log: it produces the very file gate D measures, and the stage log of
# the caller records what it reported.
record_write() {
  sanitize_line "$1"
  stdout_write "$SANITIZED"
}

# --record-evidence: refreshes the manifest entry of every generated evidence
# path named on the command line and leaves every other line of the manifest
# byte-identical.
#
# The stage that rewrites an exempt artifact names it here immediately
# afterwards, so the manifest gate D measures is never stale: the harness writes
# the manifest for the set it publishes, and verify-env, gate, compile, execute,
# dbt and diff each refresh the entries of the artifacts they rewrote. Nothing
# else of the manifest changes, so one stage cannot silence the coverage of
# another.
#
# Every named path is validated before anything is written: it equals one entry
# of the exempt inventory, it is not the manifest itself - which carries no
# digest of its own - and it is a regular file that is not a symbolic link. A
# path that fails one of those is a usage error, and the manifest is left exactly
# as it stands. A manifest that already carries a line that is no digest line is
# a finding of its own rather than a line this refresh rewrites, so a manifest
# gate D would reject is never silently repaired.
#
# The refreshed manifest is written to a name beside it and renamed over it in
# one step: a refresh that stops part way leaves the manifest unchanged and
# removes what it had written. A checkout that carries no manifest yet receives
# one whose header states that provenance.
record_evidence() {
  local path="" name="" line="" temp="" refreshed=0 added=0 kept=0
  local -A digests=() written=()
  local -a wanted=() lines=() out=()

  for path in "${RECORD_TOOLS[@]}"; do
    require_tool "$path"
  done
  if [[ -L "$EVIDENCE_DIR_REL" || ! -d "$EVIDENCE_DIR_REL" ]]; then
    fail_env "the generated evidence directory ${EVIDENCE_DIR_REL} is $(evidence_kind "$EVIDENCE_DIR_REL")"
  fi

  for path in "${RECORD_PATHS[@]}"; do
    if ! evidence_inventory_path "$path"; then
      fail_usage "--record-evidence accepts a repository-relative path of the exempt generated evidence inventory, which names ${#GENERATED_EVIDENCE_EXEMPT[@]} paths under ${EVIDENCE_DIR_REL}/, received: $(sanitize "$path")"
    fi
    if [[ "$path" == "$EVIDENCE_MANIFEST_REL" ]]; then
      fail_usage "--record-evidence cannot record ${EVIDENCE_MANIFEST_REL}: a manifest carries no digest of itself"
    fi
    if [[ -L "$path" || ! -f "$path" ]]; then
      fail_usage "--record-evidence names ${path}, which is $(evidence_kind "$path")"
    fi
  done

  for path in "${RECORD_PATHS[@]}"; do
    name="$(evidence_entry_name "$path")"
    if [[ -n "${digests[$name]+set}" ]]; then
      continue
    fi
    if ! evidence_file_digest "$path"; then
      fail_env "unable to read the SHA-256 of ${path}"
    fi
    digests["$name"]="$EVIDENCE_DIGEST"
    wanted+=("$name")
  done

  if [[ -e "$EVIDENCE_MANIFEST_REL" || -L "$EVIDENCE_MANIFEST_REL" ]]; then
    if [[ -L "$EVIDENCE_MANIFEST_REL" || ! -f "$EVIDENCE_MANIFEST_REL" ]]; then
      fail_env "the manifest ${EVIDENCE_MANIFEST_REL} is $(evidence_kind "$EVIDENCE_MANIFEST_REL")"
    fi
    mapfile -t lines <"$EVIDENCE_MANIFEST_REL"
    for line in "${lines[@]}"; do
      case "$line" in
        '#'* | '')
          out+=("$line")
          continue
          ;;
      esac
      if ((${#line} < 67)) || [[ "${line:64:2}" != "  " ]] ||
        [[ ! "${line:0:64}" =~ $EVIDENCE_DIGEST_PATTERN ]]; then
        fail_env "the manifest ${EVIDENCE_MANIFEST_REL} carries a line that is no digest line, so no entry of it is refreshed: $(sanitize "$line")"
      fi
      name="${line:66}"
      if [[ -n "${digests[$name]+set}" && -z "${written[$name]+set}" ]]; then
        out+=("${digests[$name]}  ${name}")
        written["$name"]=1
        refreshed=$((refreshed + 1))
        continue
      fi
      out+=("$line")
      kept=$((kept + 1))
    done
  else
    for line in "${EVIDENCE_MANIFEST_CREATED_HEADER[@]}"; do
      out+=("$line")
    done
  fi
  for name in "${wanted[@]}"; do
    if [[ -z "${written[$name]+set}" ]]; then
      out+=("${digests[$name]}  ${name}")
      written["$name"]=1
      added=$((added + 1))
    fi
  done

  temp="${EVIDENCE_MANIFEST_REL}.record-$$"
  if [[ -e "$temp" || -L "$temp" ]]; then
    fail_env "the manifest refresh cannot write ${temp}, which is $(evidence_kind "$temp")"
  fi
  if ! : >"$temp"; then
    fail_env "unable to create the refreshed manifest ${temp}"
  fi
  for line in "${out[@]}"; do
    if ! printf '%s\n' "$line" >>"$temp"; then
      rm -f -- "$temp" 2>/dev/null || true
      fail_env "unable to write the refreshed manifest ${temp}"
    fi
  done
  if ! chmod "$EVIDENCE_MANIFEST_MODE" -- "$temp"; then
    rm -f -- "$temp" 2>/dev/null || true
    fail_env "unable to set mode ${EVIDENCE_MANIFEST_MODE} on ${temp}"
  fi
  if ! mv -f -- "$temp" "$EVIDENCE_MANIFEST_REL"; then
    rm -f -- "$temp" 2>/dev/null || true
    fail_env "unable to replace ${EVIDENCE_MANIFEST_REL} with the refreshed manifest"
  fi

  record_write "${PROG}: evidence manifest ${EVIDENCE_MANIFEST_REL}"
  for name in "${wanted[@]}"; do
    record_write "${PROG}:   ${digests[$name]}  ${name}"
  done
  printf -v line \
    '%s: %d entry(ies) refreshed, %d added, %d entry(ies) of other stages left unchanged' \
    "$PROG" "$refreshed" "$added" "$kept"
  record_write "$line"
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
readonly SELF_TEST_EXPECTED_TOOLS=(git sha256sum wc date mkdir stat flock)

# Number of case lines --self-test reports, including the case that checks this
# number. A case that is added or removed changes it.
readonly SELF_TEST_CASE_COUNT=61

# Seconds the "flock" shim of the held-lock case hands the real tool in place of
# the bounded wait the run under test asks for. It applies to that one shim
# alone: a verification run always asks for LOG_LOCK_WAIT_SECONDS.
readonly SELF_TEST_LOCK_INJECTED_WAIT_SECONDS=0.2

# Seconds --self-test waits for the exclusive lock it takes itself on the
# evidence log of the held-lock case, before that case starts its run. Nothing
# else holds that log, so the lock is taken at once; a wait that reaches this
# value is an environment error.
readonly SELF_TEST_LOCK_HOLD_WAIT_SECONDS=10

# Value the "flock" shim records for a call that carries no bounded wait.
readonly SELF_TEST_LOCK_WAIT_UNBOUNDED="none"

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

# Exit status of every run the concurrent case started, one entry per run.
ST_CONCURRENT_STATUS=()

# Number of those runs that wrote a byte on stdout or on stderr.
ST_CONCURRENT_NOISE=0

# Bounded wait, in seconds, that each "flock" call of the run the held-lock case
# started asked for, one entry per call, in call order. An entry reads
# SELF_TEST_LOCK_WAIT_UNBOUNDED when that call carried no bounded wait.
ST_LOCK_WAIT_REQUESTED=()

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

# Starts several copies under test at the same time, each appending to one
# evidence log under its own --stage label and with its stdout and stderr sent to
# a file of its own. Waits for all of them, records one exit status per run in
# ST_CONCURRENT_STATUS and counts the runs that wrote a byte on either stream in
# ST_CONCURRENT_NOISE.
#
# Positional parameters:
#   1  number of runs started at the same time
#   2  evidence log every run appends to, relative to the repository root
st_run_concurrently() {
  local runs="$1" log_rel="$2" dir="" index=0 status=0
  local -a pids=()

  dir="${ST_CASE_DIR}/concurrent-runs"
  if ! mkdir -p -- "$dir"; then
    fail_env "--self-test could not create the concurrent-run directory for ${ST_CASE}"
  fi

  ST_CONCURRENT_STATUS=()
  ST_CONCURRENT_NOISE=0
  for ((index = 0; index < runs; index++)); do
    (cd "$ST_REPO" && "$ST_SCRIPT" --stage "concurrent-${index}" --log "$log_rel" --quiet) \
      >"${dir}/stdout-${index}" 2>"${dir}/stderr-${index}" &
    pids+=("$!")
  done
  for ((index = 0; index < runs; index++)); do
    status=0
    wait "${pids[index]}" || status=$?
    ST_CONCURRENT_STATUS+=("$status")
    if [[ -s "${dir}/stdout-${index}" || -s "${dir}/stderr-${index}" ]]; then
      ST_CONCURRENT_NOISE=$((ST_CONCURRENT_NOISE + 1))
    fi
  done
}

# Runs one copy under test against an evidence log whose exclusive lock this
# function already holds, so that the run's own acquisition of that lock cannot
# succeed. The lock is taken on a descriptor this function opens, before the run
# starts; the run is started with that descriptor closed, so it holds no lock of
# its own through it; and the descriptor is closed as soon as the run returns,
# on the run's failing path as well as on its succeeding one, which releases the
# lock.
#
# The run's wait for that lock reaches a "flock" shim placed ahead of PATH. The
# shim records the bounded wait of every call it receives in
# ST_LOCK_WAIT_REQUESTED, one entry per call and
# SELF_TEST_LOCK_WAIT_UNBOUNDED for a call that carries none, hands the real
# tool SELF_TEST_LOCK_INJECTED_WAIT_SECONDS in place of that wait, supplies that
# same value to a call that carries no wait, and forwards every other argument,
# the descriptor number and the real tool's exit status unchanged.
#
# Positional parameters:
#   1  evidence log the lock is held on, as an absolute path
#   2+ options handed to the copy under test
st_run_with_held_log_lock() {
  local log_abs="$1" bin="" real="" line="" record="" held=-1
  shift

  bin="${ST_CASE_DIR}/bin-flock-shim"
  if ! mkdir -p -- "$bin"; then
    fail_env "--self-test could not create the flock-shim PATH directory for ${ST_CASE}"
  fi
  if ! real="$(command -v flock)" || [[ -z "$real" ]]; then
    fail_env "--self-test could not resolve the real flock for ${ST_CASE}"
  fi
  record="${bin}/requested-wait"
  {
    printf '%s\n' '#!/usr/bin/env bash'
    printf '%s\n' '# Forwards every call to the real flock with a shortened bounded wait.'
    printf '%s\n' 'set -u'
    printf 'readonly REAL=%q\n' "$real"
    printf 'readonly WAIT=%q\n' "$SELF_TEST_LOCK_INJECTED_WAIT_SECONDS"
    printf 'readonly UNBOUNDED=%q\n' "$SELF_TEST_LOCK_WAIT_UNBOUNDED"
    printf 'readonly RECORD=%q\n' "$record"
    while IFS= read -r line; do
      printf '%s\n' "$line"
    done <<'FLOCK_SHIM_BODY'
args=("$@")
requested="$UNBOUNDED"
index=0
# The value that follows -w is the bounded wait the caller asked for. Every other
# argument, the descriptor number among them, is forwarded as it was received.
for index in "${!args[@]}"; do
  if [[ "${args[index]}" == "-w" ]] && ((index + 1 < ${#args[@]})); then
    requested="${args[index + 1]}"
    args[index + 1]="$WAIT"
  fi
done
# A call that asked for no bounded wait is given one, so it returns instead of
# waiting for a lock this run cannot take.
if [[ "$requested" == "$UNBOUNDED" ]]; then
  args=("-w" "$WAIT" "${args[@]}")
fi
if ! printf '%s\n' "$requested" >>"$RECORD"; then
  printf 'flock shim: could not record %s\n' "$RECORD" >&2
  exit 1
fi
exec "$REAL" "${args[@]}"
FLOCK_SHIM_BODY
  } >"${bin}/flock"
  if ! chmod 0755 -- "${bin}/flock"; then
    fail_env "--self-test could not make the flock shim executable for ${ST_CASE}"
  fi

  if ! { exec {held}>>"$log_abs"; } 2>/dev/null; then
    fail_env "--self-test could not open the evidence log of ${ST_CASE} to hold its lock"
  fi
  if ! flock -x -w "$SELF_TEST_LOCK_HOLD_WAIT_SECONDS" "$held" 2>/dev/null; then
    exec {held}>&-
    fail_env "--self-test could not take the exclusive lock it holds for ${ST_CASE} within ${SELF_TEST_LOCK_HOLD_WAIT_SECONDS} seconds"
  fi

  ST_OUTPUT=""
  ST_EXIT=0
  ST_OUTPUT="$(cd "$ST_REPO" && PATH="${bin}:${PATH}" "$BASH" "$ST_SCRIPT" "$@" 2>&1 {held}>&-)" ||
    ST_EXIT=$?
  exec {held}>&-

  ST_LOCK_WAIT_REQUESTED=()
  if [[ -f "$record" ]]; then
    while IFS= read -r line; do
      ST_LOCK_WAIT_REQUESTED+=("$line")
    done <"$record"
  fi
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

# Reads a log block by block and checks that the expected number of blocks is
# present, that each one closes before the next opens, that the last one is
# closed, and that the record after every BEGIN marker is that block's own stage
# line.
st_expect_contiguous_blocks() {
  local path="$1" want="$2" line=""
  local open=0 nested=0 begun=0 ended=0 after_begin=0 stray=0

  if [[ ! -f "$path" ]]; then
    st_note "missing log ${path#"${SELF_TEST_ROOT}/"}"
    return 0
  fi
  while IFS= read -r line; do
    if ((after_begin == 1)); then
      after_begin=0
      if [[ "$line" != "stage: "* ]]; then
        stray=$((stray + 1))
      fi
    fi
    case "$line" in
      "BEGIN readonly-check")
        if ((open == 1)); then
          nested=$((nested + 1))
        fi
        open=1
        after_begin=1
        begun=$((begun + 1))
        ;;
      "END readonly-check")
        open=0
        ended=$((ended + 1))
        ;;
    esac
  done <"$path"

  ((nested == 0)) || st_note "${nested} BEGIN marker(s) opened inside another block"
  ((stray == 0)) || st_note "${stray} BEGIN marker(s) not followed by a stage line"
  ((open == 0)) || st_note "the last block of the log was left open"
  ((begun == want && ended == want)) ||
    st_note "${begun} BEGIN and ${ended} END marker(s), expected ${want} of each"
}

# Reads a log block by block and checks that the expected number of complete
# blocks is present and that every one of them holds the same lines, in the same
# order, as the first. Every line from a BEGIN marker to the END marker that
# follows it belongs to the block being read; a line outside a block is ignored.
st_expect_identical_blocks() {
  local path="$1" want="$2" line="" index=0 differing=0 reading=0
  local -a first=() current=()

  if [[ ! -f "$path" ]]; then
    st_note "missing log ${path#"${SELF_TEST_ROOT}/"}"
    return 0
  fi
  while IFS= read -r line; do
    case "$line" in
      "BEGIN readonly-check")
        reading=1
        current=("$line")
        ;;
      "END readonly-check")
        if ((reading == 1)); then
          current+=("$line")
          index=$((index + 1))
          if ((index == 1)); then
            first=("${current[@]}")
          elif [[ "${current[*]}" != "${first[*]}" ]]; then
            differing=$((differing + 1))
          fi
          reading=0
          current=()
        fi
        ;;
      *)
        if ((reading == 1)); then
          current+=("$line")
        fi
        ;;
    esac
  done <"$path"

  ((index == want)) ||
    st_note "${index} complete block(s), expected ${want}"
  ((differing == 0)) ||
    st_note "${differing} block(s) differ from the first"
}

# Prints the gate C records of the run the case last made: every line from the
# gate C header line to the gate C result line that follows it, in order and
# unchanged. Reads the captured output of that run alone, so two runs of one
# stage can be compared record by record. Prints nothing when the run reported
# no gate C header, which the caller reports as a missing block.
st_gate_c_block() {
  local line="" reading=0

  while IFS= read -r line; do
    case "$line" in
      "gate C no tracked modification outside the generated evidence set:")
        reading=1
        printf '%s\n' "$line"
        ;;
      "gate C result: "*)
        if ((reading == 1)); then
          printf '%s\n' "$line"
          reading=0
        fi
        ;;
      *)
        if ((reading == 1)); then
          printf '%s\n' "$line"
        fi
        ;;
    esac
  done <<<"$ST_OUTPUT"
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
  # The components above the evidence directory are created first, so the link
  # stands at the name of that directory itself and the walk of the chain meets
  # it at its last component.
  if ! mkdir -p -- "${ST_CASE_DIR}/diverted" ||
    ! mkdir -p -- "${ST_REPO}/${LOG_DIR_REL%/*}" ||
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

# Three --reproducible runs of one stage over one unchanged tracked state: two
# from the path the case work tree is created at and one from the path that tree
# is renamed to. Every block of that log holds the same lines, none of them
# names either path, and one run of the same stage without the option records
# its own UTC time in a log of its own while still naming the root relative to
# itself rather than as a checkout path.
st_case_reproducible_block() {
  local log_rel="${LOG_DIR_REL}/reproducible.log"
  local dated_rel="${LOG_DIR_REL}/dated.log"
  local log_abs="" dated_abs="" moved="" moved_output=""
  local moved_exit=0
  st_begin "reproducible-block"
  dated_abs="${ST_REPO}/${dated_rel}"

  st_run --stage fixed-stage --log "$log_rel" --reproducible
  st_expect_exit "$EXIT_OK"
  st_expect_output "timestamp_utc: ${REPRODUCIBLE_TIMESTAMP_TEXT}"
  st_expect_output "repository_root: ${REPRODUCIBLE_ROOT_TEXT}"
  st_expect_no_output "$ST_REPO"
  st_run --stage fixed-stage --log "$log_rel" --reproducible
  st_expect_exit "$EXIT_OK"

  st_run --stage fixed-stage --log "$dated_rel"
  st_expect_exit "$EXIT_OK"
  st_expect_prefix_count "$dated_abs" "timestamp_utc: " 1
  st_expect_prefix_count "$dated_abs" \
    "timestamp_utc: ${REPRODUCIBLE_TIMESTAMP_TEXT}" 0
  st_expect_prefix_count "$dated_abs" \
    "repository_root: ${REPO_ROOT_DISPLAY}" 1
  st_expect_prefix_count "$dated_abs" "repository_root: ${ST_REPO}" 0
  st_expect_substring_count "$dated_abs" "$ST_CASE_DIR" 0

  moved="${ST_CASE_DIR}/repo-under-a-longer-second-path"
  if ! mv -- "$ST_REPO" "$moved"; then
    fail_env "--self-test could not rename the work tree of ${ST_CASE}"
  fi
  log_abs="${moved}/${log_rel}"
  moved_output="$(cd "$moved" &&
    "${moved}/${SELF_TEST_SCRIPT_REL}" --stage fixed-stage --log "$log_rel" \
      --reproducible 2>&1)" || moved_exit=$?
  ((moved_exit == EXIT_OK)) ||
    st_note "the run from the second path exited ${moved_exit}, expected ${EXIT_OK}"
  [[ "$moved_output" == *"verdict: PASS"* ]] ||
    st_note "the run from the second path reported no passing verdict"

  st_expect_prefix_count "$log_abs" \
    "timestamp_utc: ${REPRODUCIBLE_TIMESTAMP_TEXT}" 3
  st_expect_prefix_count "$log_abs" \
    "repository_root: ${REPRODUCIBLE_ROOT_TEXT}" 3
  st_expect_prefix_count "$log_abs" "stage: fixed-stage" 3
  st_expect_substring_count "$log_abs" "$ST_CASE_DIR" 0
  st_expect_exact_count "$log_abs" "verdict: PASS" 3
  st_expect_exact_count "$log_abs" "exit_code: 0" 3
  st_expect_identical_blocks "$log_abs" 3
  st_end "three identical blocks from two checkout paths, dated block unchanged without the option"
}

# Four runs append to one evidence log at the same time, from an evidence
# directory that does not exist when they start.
st_case_log_concurrent_blocks() {
  local log_rel="${LOG_DIR_REL}/concurrent.log" log_abs="" status=""
  local runs=4
  st_begin "log-concurrent-blocks"
  log_abs="${ST_REPO}/${log_rel}"
  st_run_concurrently "$runs" "$log_rel"
  for status in "${ST_CONCURRENT_STATUS[@]}"; do
    ((status == EXIT_OK)) || st_note "a concurrent run exited ${status}, expected ${EXIT_OK}"
  done
  ((${#ST_CONCURRENT_STATUS[@]} == runs)) ||
    st_note "${#ST_CONCURRENT_STATUS[@]} run(s) reported a status, expected ${runs}"
  ((ST_CONCURRENT_NOISE == 0)) ||
    st_note "${ST_CONCURRENT_NOISE} concurrent run(s) wrote on stdout or stderr"
  st_expect_exact_count "$log_abs" "BEGIN readonly-check" "$runs"
  st_expect_exact_count "$log_abs" "END readonly-check" "$runs"
  st_expect_exact_count "$log_abs" "verdict: PASS" "$runs"
  st_expect_exact_count "$log_abs" "exit_code: 0" "$runs"
  st_expect_prefix_count "$log_abs" "stage: concurrent-" "$runs"
  st_expect_contiguous_blocks "$log_abs" "$runs"
  st_end "${runs} runs at once leave ${runs} contiguous blocks in one log, silently and with exit 0"
}

# One run meets an evidence log whose exclusive lock a descriptor of this
# self-test holds for the whole of that run. The run asks for the bounded wait a
# verification run always asks for, reaches the end of the wait it is given,
# reports the log on stderr and appends nothing to it.
st_case_log_lock_timeout() {
  local log_rel="${LOG_DIR_REL}/locked.log" log_abs=""
  local body="self-test held evidence log" before="" after=""
  st_begin "log-lock-timeout"
  log_abs="${ST_REPO}/${log_rel}"
  if ! mkdir -p -- "${ST_REPO}/${LOG_DIR_REL}"; then
    fail_env "--self-test could not create the evidence directory for ${ST_CASE}"
  fi
  printf '%s\n' "$body" >"$log_abs"
  before="$(st_digest_of "$log_abs")"
  [[ -n "$before" ]] || st_note "the held evidence log has no digest before the run"
  st_run_with_held_log_lock "$log_abs" --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "unable to take the exclusive lock on the evidence log within ${LOG_LOCK_WAIT_SECONDS} seconds: ${log_rel}"
  st_expect_no_output "BEGIN readonly-check"
  st_expect_no_output "verdict: PASS"
  ((${#ST_LOCK_WAIT_REQUESTED[@]} == 1)) ||
    st_note "${#ST_LOCK_WAIT_REQUESTED[@]} lock acquisition(s) reached the tool, expected 1"
  [[ "${ST_LOCK_WAIT_REQUESTED[0]-}" == "$LOG_LOCK_WAIT_SECONDS" ]] ||
    st_note "the run asked for a wait of ${ST_LOCK_WAIT_REQUESTED[0]-(none recorded)} seconds, expected ${LOG_LOCK_WAIT_SECONDS}"
  st_expect_body "$log_abs" "$body"
  st_expect_substring_count "$log_abs" "readonly-check" 0
  after="$(st_digest_of "$log_abs")"
  [[ -n "$after" && "$after" == "$before" ]] ||
    st_note "the held evidence log changed while its lock was held elsewhere"
  st_expect_absent "${ST_REPO}/${DEFAULT_LOG_REL}"
  st_end "exit 4 when the exclusive lock is not taken within the bounded wait, log named and its bytes unchanged"
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

# Modifies one tracked path outside modernization/ and one tracked authored path
# under it, and nothing else. Gate C names and counts both, records no exempt
# path as modified, fails and exits EXIT_TRACKED.
st_case_tracked_outside() {
  local outside_rel="NOTES.txt"
  st_begin "tracked-outside"
  printf 'self-test tracked note\n' >"${ST_REPO}/${outside_rel}"
  st_commit "self-test tracked file outside modernization/"
  printf 'self-test tracked note, modified\n' >"${ST_REPO}/${outside_rel}"
  printf '%s\njsonschema==4.26.0\n' "$SELF_TEST_MANIFEST_BODY" \
    >"${ST_REPO}/${SELF_TEST_MANIFEST_REL}"
  st_run --stage self-test
  st_expect_exit "$EXIT_TRACKED"
  st_expect_output "gate A result: PASS (5 of 5 baseline entries matched)"
  st_expect_output "gate B result: PASS"
  st_expect_output "    ${outside_rel}"
  st_expect_output "    ${SELF_TEST_MANIFEST_REL}"
  st_expect_output "    (no exempt generated evidence path modified)"
  st_expect_output "  exempt generated evidence paths modified: 0"
  st_expect_output "  tracked modifications: 2"
  st_expect_output "gate C result: FAIL"
  st_expect_output "verdict: FAIL-TRACKED-MODIFICATION"
  st_end "exit 3 at gate C on one modified tracked path outside modernization/ and one authored path under it, both named"
}

# Modifies one tracked authored path under modernization/ and nothing else, then
# runs one stage twice over that state into one log with --reproducible. Each
# run names and counts that path, records no exempt path as modified, fails gate
# C and exits EXIT_TRACKED; the gate C records of the two runs hold the same
# lines in the same order, and the log holds two identical blocks.
st_case_tracked_authored() {
  local log_rel="${LOG_DIR_REL}/authored.log"
  local log_abs="" first_block="" second_block="" reported=""
  st_begin "tracked-authored"
  log_abs="${ST_REPO}/${log_rel}"

  printf '%s\njsonschema==4.26.0\n' "$SELF_TEST_MANIFEST_BODY" \
    >"${ST_REPO}/${SELF_TEST_MANIFEST_REL}"
  reported="$(cd "$ST_REPO" && git diff --name-only HEAD)"
  [[ "$reported" == "$SELF_TEST_MANIFEST_REL" ]] ||
    st_note "the work tree reports '${reported}' where only ${SELF_TEST_MANIFEST_REL} was modified"

  st_run --stage fixed-stage --log "$log_rel" --reproducible
  st_expect_exit "$EXIT_TRACKED"
  st_expect_output "gate A result: PASS (5 of 5 baseline entries matched)"
  st_expect_output "gate B result: PASS"
  st_expect_output "    ${SELF_TEST_MANIFEST_REL}"
  st_expect_output "    (no exempt generated evidence path modified)"
  st_expect_output "  exempt generated evidence paths modified: 0"
  st_expect_output "  tracked modifications: 1"
  st_expect_output "gate C result: FAIL"
  st_expect_output "verdict: FAIL-TRACKED-MODIFICATION"
  first_block="$(st_gate_c_block)"
  [[ -n "$first_block" ]] || st_note "the first run recorded no gate C block"

  st_run --stage fixed-stage --log "$log_rel" --reproducible
  st_expect_exit "$EXIT_TRACKED"
  st_expect_output "  tracked modifications: 1"
  second_block="$(st_gate_c_block)"
  [[ "$second_block" == "$first_block" ]] ||
    st_note "the two runs over one tracked state recorded different gate C records"

  st_expect_identical_blocks "$log_abs" 2
  st_expect_exact_count "$log_abs" "verdict: FAIL-TRACKED-MODIFICATION" 2
  st_expect_exact_count "$log_abs" "    ${SELF_TEST_MANIFEST_REL}" 2
  st_end "exit 3 at gate C on one modified tracked authored path, named and counted in two identical blocks"
}

# Creates every path of the exempt inventory in the case work tree, the manifest
# of the set carrying one comment line and every other entry the supplied line.
# Leaves the tree uncommitted.
st_evidence_set() {
  local body="$1" path=""

  for path in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    if ! mkdir -p -- "${ST_REPO}/${path%/*}"; then
      fail_env "--self-test could not create the directory of ${path} for ${ST_CASE}"
    fi
    if [[ "$path" == "$EVIDENCE_MANIFEST_REL" ]]; then
      printf '# self-test evidence manifest\n' >"${ST_REPO}/${path}"
      continue
    fi
    printf '%s\n' "$body" >"${ST_REPO}/${path}"
  done
}

# Prints every path of the exempt inventory except the manifest, one per line, in
# inventory order: the paths a refresh of the whole set names.
st_evidence_covered_paths() {
  local path=""

  for path in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    if [[ "$path" != "$EVIDENCE_MANIFEST_REL" ]]; then
      printf '%s\n' "$path"
    fi
  done
}

# Refreshes the manifest entry of every exempt path except the manifest through
# the copy under test, and notes a failure when that refresh does not complete.
st_record_all_evidence() {
  local -a paths=()

  mapfile -t paths < <(st_evidence_covered_paths)
  st_run --record-evidence "${paths[@]}"
  ((ST_EXIT == EXIT_OK)) ||
    st_note "the manifest refresh of the whole set exited ${ST_EXIT}: ${ST_OUTPUT}"
}

# Commits every path of the exempt inventory, modifies all of them and nothing
# else, refreshes the manifest over the twenty-two it covers, and runs the gate.
# Each path is recorded twice in the log - once in the inventory and once in the
# list of exempt paths this run found modified - the exempt count reads the size
# of the inventory, no tracked modification is counted, gate D reports every one
# of those twenty-two as covered, and the run passes.
st_case_evidence_exempt() {
  local log_rel="${LOG_DIR_REL}/exempt.log"
  local log_abs="" path="" reported="" covered=0
  st_begin "evidence-exempt"
  log_abs="${ST_REPO}/${log_rel}"
  covered=$((${#GENERATED_EVIDENCE_EXEMPT[@]} - 1))

  st_evidence_set 'self-test published evidence'
  st_commit "self-test published evidence set"
  while IFS= read -r path; do
    printf 'self-test republished evidence\n' >"${ST_REPO}/${path}"
  done < <(st_evidence_covered_paths)
  st_record_all_evidence
  st_expect_output "0 entry(ies) refreshed, ${covered} added"
  reported="$(cd "$ST_REPO" && git diff --name-only HEAD | wc -l)"
  ((reported == ${#GENERATED_EVIDENCE_EXEMPT[@]})) ||
    st_note "the work tree reports ${reported} modified path(s), expected ${#GENERATED_EVIDENCE_EXEMPT[@]}"

  st_run --stage self-test --log "$log_rel"
  st_expect_exit "$EXIT_OK"
  st_expect_output "gate A result: PASS (5 of 5 baseline entries matched)"
  st_expect_output "gate B result: PASS"
  st_expect_no_output "    (no exempt generated evidence path modified)"
  st_expect_output "    (no tracked modification)"
  st_expect_output "  exempt generated evidence paths modified: ${#GENERATED_EVIDENCE_EXEMPT[@]}"
  st_expect_output "  tracked modifications: 0"
  st_expect_output "gate C result: PASS"
  st_expect_output "  digest lines: ${covered}"
  st_expect_output "  covered by a matching digest: ${covered}"
  st_expect_output "  paths the manifest does not cover: 0"
  st_expect_output "gate D result: PASS"
  st_expect_output "verdict: PASS"
  for path in "${GENERATED_EVIDENCE_EXEMPT[@]}"; do
    st_expect_exact_count "$log_abs" "    ${path}" 2
  done
  st_end "exit 0 with all ${#GENERATED_EVIDENCE_EXEMPT[@]} exempt generated evidence paths modified, each recorded as exempt and none counted, and all ${covered} covered by the refreshed manifest"
}

# Commits two tracked paths in the published evidence directory that the exempt
# inventory does not name - the environment record no harness run writes, and a
# name below a subdirectory of that directory - modifies both and nothing else,
# and runs the gate. Both are named and counted, no exempt path is recorded as
# modified, and the run fails: the exemption holds for the exact paths of the
# inventory and for no other path of that directory.
st_case_evidence_not_exempt() {
  local versions_rel="modernization/validation/artifacts/runtime-versions.txt"
  local nested_rel="modernization/validation/artifacts/nested/compile.log"
  st_begin "evidence-not-exempt"

  if ! mkdir -p -- "${ST_REPO}/${nested_rel%/*}"; then
    fail_env "--self-test could not create the directory of ${nested_rel} for ${ST_CASE}"
  fi
  printf 'self-test environment record\n' >"${ST_REPO}/${versions_rel}"
  printf 'self-test nested evidence name\n' >"${ST_REPO}/${nested_rel}"
  st_commit "self-test evidence directory paths outside the exempt inventory"
  printf 'self-test environment record, modified\n' >"${ST_REPO}/${versions_rel}"
  printf 'self-test nested evidence name, modified\n' >"${ST_REPO}/${nested_rel}"

  st_run --stage self-test
  st_expect_exit "$EXIT_TRACKED"
  st_expect_output "gate A result: PASS (5 of 5 baseline entries matched)"
  st_expect_output "gate B result: PASS"
  st_expect_output "    ${versions_rel}"
  st_expect_output "    ${nested_rel}"
  st_expect_output "    (no exempt generated evidence path modified)"
  st_expect_output "  exempt generated evidence paths modified: 0"
  st_expect_output "  tracked modifications: 2"
  st_expect_output "gate C result: FAIL"
  st_expect_output "verdict: FAIL-TRACKED-MODIFICATION"
  st_end "exit 3 at gate C on runtime-versions.txt and one nested name in the evidence directory, both named"
}

# Publishes the whole evidence set, records it in the manifest, commits, and then
# appends one byte to the comparison report and to nothing else - the shape the
# QA report reproduced. Gate C records that path as exempt and passes, because
# the diff stage rewrites it on every run; gate D compares its content with the
# digest the manifest states and fails, naming the path, with exit 6.
st_case_evidence_tamper() {
  local target="${EVIDENCE_DIR_REL}/diff-report.md"
  st_begin "evidence-tamper"

  st_evidence_set 'self-test published evidence'
  st_record_all_evidence
  st_commit "self-test published evidence set with its manifest"
  printf 'appended by the tamper case\n' >>"${ST_REPO}/${target}"

  st_run --stage self-test
  st_expect_exit "$EXIT_EVIDENCE"
  st_expect_output "gate C result: PASS"
  st_expect_output "  exempt generated evidence paths modified: 1"
  st_expect_output "${target} does not match the digest its manifest entry states"
  st_expect_output "gate D result: FAIL"
  st_expect_output "verdict: FAIL-EVIDENCE-COVERAGE"
  st_end "exit 6 at gate D on one altered exempt artifact, named, with gate C still passing it as exempt"
}

# Publishes the whole evidence set but records every path except one, so that one
# stands with no entry at all. Gate D names it and fails: an artifact a stage
# rewrote without refreshing its entry is a finding rather than a gap.
st_case_evidence_uncovered() {
  local skipped="${EVIDENCE_DIR_REL}/gate-selection.json"
  local path="" covered=0
  local -a paths=()
  st_begin "evidence-uncovered"
  covered=$((${#GENERATED_EVIDENCE_EXEMPT[@]} - 2))

  st_evidence_set 'self-test published evidence'
  while IFS= read -r path; do
    if [[ "$path" != "$skipped" ]]; then
      paths+=("$path")
    fi
  done < <(st_evidence_covered_paths)
  st_run --record-evidence "${paths[@]}"
  st_expect_exit "$EXIT_OK"
  st_commit "self-test published evidence set with one path unrecorded"

  st_run --stage self-test
  st_expect_exit "$EXIT_EVIDENCE"
  st_expect_output "gate C result: PASS"
  st_expect_output "  digest lines: ${covered}"
  st_expect_output "  covered by a matching digest: ${covered}"
  st_expect_output "    ${skipped}"
  st_expect_output "  paths the manifest does not cover: 1"
  st_expect_output "1 generated evidence path(s) stand with no entry in ${EVIDENCE_MANIFEST_REL}"
  st_expect_output "verdict: FAIL-EVIDENCE-COVERAGE"
  st_end "exit 6 at gate D on one exempt artifact standing without a manifest entry, named"
}

# Publishes generated evidence with no manifest beside it. Gate D names every
# uncovered path and fails: a set with no manifest is a set nothing measures.
st_case_evidence_manifest_absent() {
  local path="" covered=0
  st_begin "evidence-manifest-absent"
  covered=$((${#GENERATED_EVIDENCE_EXEMPT[@]} - 1))

  st_evidence_set 'self-test published evidence'
  if ! rm -f -- "${ST_REPO}/${EVIDENCE_MANIFEST_REL}"; then
    fail_env "--self-test could not remove the manifest for ${ST_CASE}"
  fi
  st_commit "self-test published evidence set without a manifest"

  st_run --stage self-test
  st_expect_exit "$EXIT_EVIDENCE"
  st_expect_output "gate C result: PASS"
  st_expect_output "the manifest ${EVIDENCE_MANIFEST_REL} is absent while ${covered} generated evidence path(s) stand in this checkout"
  st_expect_output "    ${EVIDENCE_DIR_REL}/translate.log"
  st_expect_output "verdict: FAIL-EVIDENCE-COVERAGE"
  st_end "exit 6 at gate D when ${covered} generated evidence paths stand with no manifest, each named"
}

# Commits a clean checkout that carries no generated evidence and no manifest.
# Gate D passes: nothing has been published, so there is nothing to cover.
st_case_evidence_none_published() {
  st_begin "evidence-none-published"

  st_run --stage self-test
  st_expect_exit "$EXIT_OK"
  st_expect_output "  generated evidence paths standing in this checkout: 0 of $((${#GENERATED_EVIDENCE_EXEMPT[@]} - 1))"
  st_expect_output "    (no generated evidence path stands in this checkout)"
  st_expect_output "  paths the manifest does not cover: 0"
  st_expect_output "gate D result: PASS"
  st_expect_output "verdict: PASS"
  st_end "exit 0 with no manifest and no generated evidence: nothing published, nothing to cover"
}

# Commits a manifest that states a name the exempt inventory does not name as a
# covered path - the environment record no run of the bridge writes. Gate D
# rejects the entry rather than measuring a file outside the set.
st_case_evidence_manifest_foreign() {
  local foreign="runtime-versions.txt"
  st_begin "evidence-manifest-foreign"

  st_evidence_set 'self-test published evidence'
  st_record_all_evidence
  printf '%s\n' "$foreign" >"${ST_REPO}/${EVIDENCE_DIR_REL}/${foreign}"
  printf '%064d  %s\n' 0 "$foreign" >>"${ST_REPO}/${EVIDENCE_MANIFEST_REL}"
  st_commit "self-test manifest naming a path outside the covered inventory"

  st_run --stage self-test
  st_expect_exit "$EXIT_EVIDENCE"
  st_expect_output "the manifest states ${foreign}, which the exempt inventory does not name as a covered generated evidence path"
  st_expect_output "gate D result: FAIL"
  st_expect_output "verdict: FAIL-EVIDENCE-COVERAGE"
  st_end "exit 6 at gate D on a manifest entry outside the covered inventory, named"
}

# Commits a manifest carrying a line that is no digest line, and a manifest
# stating one name twice. Gate D reports each as a finding, and the refresh
# refuses to rewrite the malformed manifest so a stage cannot repair it in
# silence, leaving it byte-identical and no temporary file behind.
st_case_evidence_manifest_malformed() {
  local target="${EVIDENCE_DIR_REL}/translate.log"
  local manifest="" before="" leftover=""
  st_begin "evidence-manifest-malformed"
  manifest="${ST_REPO}/${EVIDENCE_MANIFEST_REL}"

  st_evidence_set 'self-test published evidence'
  st_record_all_evidence
  printf 'not-a-digest  translate.log\n' >>"$manifest"
  st_commit "self-test manifest carrying a line that is no digest line"
  before="$(<"$manifest")"

  st_run --stage self-test
  st_expect_exit "$EXIT_EVIDENCE"
  st_expect_output "the manifest carries a line that is no digest line: not-a-digest  translate.log"
  st_expect_output "verdict: FAIL-EVIDENCE-COVERAGE"

  st_run --record-evidence "$target"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "carries a line that is no digest line, so no entry of it is refreshed"
  [[ "$(<"$manifest")" == "$before" ]] ||
    st_note "the refused refresh changed ${EVIDENCE_MANIFEST_REL}"
  leftover="$(cd "${ST_REPO}/${EVIDENCE_DIR_REL}" && printf '%s' "$(echo evidence-manifest.sha256.record-*)")"
  [[ "$leftover" == 'evidence-manifest.sha256.record-*' ]] ||
    st_note "the refused refresh left ${leftover} behind"
  st_end "exit 6 at gate D on a malformed manifest line, and exit 4 from a refresh that leaves that manifest unchanged"
}

# Commits a manifest stating one covered name twice. Gate D reports the repeated
# name: a set is described by one entry per file.
st_case_evidence_manifest_duplicate() {
  local manifest="" first=""
  st_begin "evidence-manifest-duplicate"
  manifest="${ST_REPO}/${EVIDENCE_MANIFEST_REL}"

  st_evidence_set 'self-test published evidence'
  st_record_all_evidence
  first="$(cd "$ST_REPO" && grep -m 1 '  translate.log$' "${EVIDENCE_MANIFEST_REL}")" ||
    fail_env "--self-test could not read the translate.log entry for ${ST_CASE}"
  printf '%s\n' "$first" >>"$manifest"
  st_commit "self-test manifest stating one name twice"

  st_run --stage self-test
  st_expect_exit "$EXIT_EVIDENCE"
  st_expect_output "the manifest states translate.log more than once"
  st_expect_output "verdict: FAIL-EVIDENCE-COVERAGE"
  st_end "exit 6 at gate D on a manifest stating one covered name twice"
}

# Refreshes one entry of a recorded set after rewriting that one artifact: the
# entry carries the new digest, every other line of the manifest stays
# byte-identical, the counts the refresh reports name what it did, a second
# refresh over unchanged content rewrites the same bytes, and the gate that
# follows passes.
st_case_record_evidence() {
  local target="${EVIDENCE_DIR_REL}/dbt-run.log"
  local other="${EVIDENCE_DIR_REL}/translate.log"
  local manifest="" before="" after="" again="" digest="" line="" covered=0
  st_begin "record-evidence"
  manifest="${ST_REPO}/${EVIDENCE_MANIFEST_REL}"
  covered=$((${#GENERATED_EVIDENCE_EXEMPT[@]} - 1))

  st_evidence_set 'self-test published evidence'
  st_record_all_evidence
  st_expect_output "0 entry(ies) refreshed, ${covered} added"
  st_commit "self-test published evidence set with its manifest"
  before="$(grep -v '  dbt-run.log$' -- "$manifest")"

  printf 'self-test dbt run of a later stage\n' >"${ST_REPO}/${target}"
  digest="$(sha256sum -- "${ST_REPO}/${target}")" ||
    fail_env "--self-test could not hash ${target} for ${ST_CASE}"
  digest="${digest%% *}"

  st_run --record-evidence "$target"
  st_expect_exit "$EXIT_OK"
  st_expect_output "1 entry(ies) refreshed, 0 added, $((covered - 1)) entry(ies) of other stages left unchanged"
  st_expect_output "${digest}  dbt-run.log"
  after="$(grep -v '  dbt-run.log$' -- "$manifest")"
  [[ "$after" == "$before" ]] ||
    st_note "the refresh changed a line of another stage in ${EVIDENCE_MANIFEST_REL}"
  line="$(grep -c "^${digest}  dbt-run.log$" -- "$manifest")" || line=0
  ((line == 1)) || st_note "${line} refreshed entry line(s) for dbt-run.log, expected 1"

  st_run --record-evidence "$target" "$other"
  st_expect_exit "$EXIT_OK"
  st_expect_output "2 entry(ies) refreshed, 0 added"
  again="$(grep -v '  dbt-run.log$' -- "$manifest")"
  [[ "$again" == "$before" ]] ||
    st_note "a refresh over unchanged content rewrote another line of ${EVIDENCE_MANIFEST_REL}"

  st_run --stage self-test
  st_expect_exit "$EXIT_OK"
  st_expect_output "  covered by a matching digest: ${covered}"
  st_expect_output "gate D result: PASS"
  st_expect_output "verdict: PASS"
  st_end "one entry refreshed with the new digest, every other line byte-identical, and the gate passing afterwards"
}

# Points the refresh at values it must refuse: a tracked authored path outside
# the exempt inventory, the manifest itself, a path of the inventory that does
# not exist, a path of the inventory that is a symbolic link, and no path at all.
# Each is a usage error, the manifest stays byte-identical, and nothing is
# created.
st_case_record_evidence_refused() {
  local outside="$SELF_TEST_MANIFEST_REL"
  local absent="${EVIDENCE_DIR_REL}/dbt-test.log"
  local linked="${EVIDENCE_DIR_REL}/dbt-clean.log"
  local manifest="" before="" path=""
  local -a paths=()
  st_begin "record-evidence-refused"
  manifest="${ST_REPO}/${EVIDENCE_MANIFEST_REL}"

  st_evidence_set 'self-test published evidence'
  if ! rm -f -- "${ST_REPO}/${absent}"; then
    fail_env "--self-test could not remove ${absent} for ${ST_CASE}"
  fi
  if ! rm -f -- "${ST_REPO}/${linked}" ||
    ! ln -s -- "../../../${SELF_TEST_MANIFEST_REL}" "${ST_REPO}/${linked}"; then
    fail_env "--self-test could not place the symbolic link ${linked} for ${ST_CASE}"
  fi
  while IFS= read -r path; do
    if [[ "$path" != "$absent" && "$path" != "$linked" ]]; then
      paths+=("$path")
    fi
  done < <(st_evidence_covered_paths)
  st_run --record-evidence "${paths[@]}"
  ((ST_EXIT == EXIT_OK)) ||
    st_note "the refresh of the recordable paths exited ${ST_EXIT}: ${ST_OUTPUT}"
  st_commit "self-test evidence set with one absent and one symlinked entry"
  before="$(<"$manifest")"

  st_run --record-evidence "$outside"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "--record-evidence accepts a repository-relative path of the exempt generated evidence inventory"
  st_expect_output "received: ${outside}"

  st_run --record-evidence "$EVIDENCE_MANIFEST_REL"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "a manifest carries no digest of itself"

  st_run --record-evidence "$absent"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "--record-evidence names ${absent}, which is absent"

  st_run --record-evidence "$linked"
  st_expect_exit "$EXIT_ENV"
  st_expect_output "--record-evidence names ${linked}, which is a symbolic link"

  st_run --record-evidence
  st_expect_exit "$EXIT_ENV"
  st_expect_output "--record-evidence requires at least one repository-relative generated evidence path"

  st_run --record-evidence "${EVIDENCE_DIR_REL}/translate.log" --stage self-test
  st_expect_exit "$EXIT_ENV"
  st_expect_output "--record-evidence accepts no other option"

  [[ "$(<"$manifest")" == "$before" ]] ||
    st_note "a refused refresh changed ${EVIDENCE_MANIFEST_REL}"
  st_expect_body "${ST_REPO}/${SELF_TEST_MANIFEST_REL}" "$SELF_TEST_MANIFEST_BODY"
  st_end "six refused refreshes, each naming its rule, with the manifest and the link target unchanged"
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
  st_expect_output "    (no exempt generated evidence path modified)"
  st_expect_output "    (no tracked modification)"
  st_expect_output "  exempt generated evidence paths modified: 0"
  st_expect_output "  tracked modifications: 0"
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
  st_case_reproducible_block
  st_case_log_concurrent_blocks
  st_case_log_lock_timeout
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
  st_case_tracked_authored
  st_case_evidence_exempt
  st_case_evidence_not_exempt
  st_case_evidence_tamper
  st_case_evidence_uncovered
  st_case_evidence_manifest_absent
  st_case_evidence_none_published
  st_case_evidence_manifest_foreign
  st_case_evidence_manifest_malformed
  st_case_evidence_manifest_duplicate
  st_case_record_evidence
  st_case_record_evidence_refused
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
  local timestamp="" root_recorded=""

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

  # The manifest refresh runs no gate and opens no evidence log: it produces the
  # file gate D measures, so it resolves the repository root, records the entries
  # it was given and returns.
  if ((RECORD_MODE == 1)); then
    preflight_tools
    resolve_repo_root
    record_evidence
    exit "$EXIT_OK"
  fi

  preflight_tools
  preflight_descriptor_view
  resolve_repo_root

  # The record that differs between two runs of one stage. --reproducible
  # records fixed text and reads no clock; without it the run records its own
  # UTC time. The root record never carries the absolute path of a checkout:
  # the default block names it relative to itself, and --reproducible names the
  # mode instead, so a block reads the same from every checkout either way.
  if ((REPRODUCIBLE == 1)); then
    timestamp="$REPRODUCIBLE_TIMESTAMP_TEXT"
    root_recorded="$REPRODUCIBLE_ROOT_TEXT"
  else
    if ! timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; then
      fail_env "unable to read the current UTC time"
    fi
    root_recorded="$REPO_ROOT_DISPLAY"
  fi

  open_log

  emit "BEGIN readonly-check"
  emit "stage: $(sanitize "$STAGE")"
  emit "timestamp_utc: ${timestamp}"
  # The root itself, named as the block names every other path: relative to it.
  # A block therefore reads the same from every checkout of this repository, and
  # the checkout it was written in is the one the file stands in. --reproducible
  # substitutes its own fixed text for that record as well, so the mode a block
  # was written in is legible from the block.
  emit "repository_root: ${root_recorded}"
  emit "evidence_log: $(sanitize "$LOG_PATH")"
  # The disposition every block of this log carries, after the records that
  # identify the run and before the baseline it measured.
  emit "status_label: ${STATUS_LABEL_TEXT}"
  print_baseline

  emit "preflight result: PASS"

  gate_a || finish "$EXIT_SOURCE" "FAIL-SOURCE-INTEGRITY"
  gate_b || finish "$EXIT_BASE_DIRTY" "FAIL-BASE-WORKTREE-DIRTY"
  gate_c || finish "$EXIT_TRACKED" "FAIL-TRACKED-MODIFICATION"
  gate_d || finish "$EXIT_EVIDENCE" "FAIL-EVIDENCE-COVERAGE"

  finish "$EXIT_OK" "PASS"
}

main "$@"
