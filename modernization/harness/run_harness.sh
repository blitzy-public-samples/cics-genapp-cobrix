#!/usr/bin/env bash
#
# run_harness.sh - build, compile and execute the GnuCOBOL validation harness
# for the GenApp Policy-Issue chain.
#
# Takes the harness from the untouched sources to the executed cases of the
# case table below, with retained evidence. Runs non-interactively, installs
# nothing, reaches no network and stops at the first failing step.
#
# Stages, in execution order:
#   1 preflight   Resolves the repository root from the location of this
#                 script, takes the exclusive harness lock of the checkout
#                 before any shared build path is created or read, checks the
#                 Python interpreter, the COBOL compiler and every harness
#                 input, pins the compiler environment the compile and the
#                 execution stages run under, creates the build directories,
#                 empties the evidence log the source guard appends its blocks
#                 to so that log holds the gates of this run alone, and runs
#                 modernization/validation/verify_readonly.sh before any
#                 generated output is produced. Every gate of the run asks that
#                 script for its reproducible block, so the published log holds
#                 the same bytes after two runs of the same selection over one
#                 unchanged tracked state, in any checkout. The lock is held
#                 until the run ends, so two invocations of this script on one
#                 checkout run one after the other rather than over each other.
#   2 samples     Generates one 32,500-character COMMAREA record per selected
#                 fixture and translates read-only copies of the three named
#                 programs into the build tree.
#   3 compile     Records the compiler environment and the resolved dialect of
#                 the run at the head of the compile log, builds the twelve
#                 stubs and the three translated programs as callable modules
#                 and the driver as an executable, then runs the source guard
#                 again.
#   4 probes      Runs the driver once per infrastructure probe of the probe
#                 table below, each with one item of its environment, or one of
#                 the three handles this script opens for it, made deliberately
#                 wrong, and asserts the status the driver reports and the side
#                 effect the row of that probe names.
#   5 execute     Runs the driver once per selected case on the three handles
#                 this script opens and checks for it, asserts the row of the
#                 case table against values this script reads out of the
#                 generated sample record, and runs the source guard again.
#   6 evidence    Runs the source guard as the final gate, then collects the
#                 retained logs, the guard's own evidence log and the captures
#                 of the success cases the run executed, and writes the manifest
#                 of that set: the provenance of the run, and one SHA-256 line
#                 per collected file. It then runs the replacement over a
#                 directory of its own under the build tree, and replaces the
#                 published set in the validation artifacts directory - every
#                 name this script owns there is removed, the collected files
#                 are placed under the names the manifest carries and the
#                 manifest is placed last - before reading that set back against
#                 the manifest and printing the run summary. The published set
#                 is the five stage files, the manifest, and the driver log, the
#                 capture file and the post-chain record of each success case
#                 the run executed: twelve names for a run that executed both
#                 success cases, nine for one and six for none. The names of a
#                 success case the run did not execute are removed, so the set
#                 describes this run alone. runtime-versions.txt stands in that
#                 directory outside the replacement: it is the environment
#                 record of the checkout and no run of this script writes it.
#
# Case table, one row per executable case. Each row names the fixture it runs
# on, the COMMAREA length the driver calls with, the request id it overrides
# the fixture with, the failure it injects, and the outcome this script
# asserts. "policy SQL", "VSAM", "values" and "product values" say which
# capture groups the row asserts; "diag" says whether the row expects
# diagnostic links.
#   label          fixture calen req.id  injection      rc   abend product    policy VSAM values prod diag
#   01AMOT         motor   32500 -       -              00   -     MOTOR      Y      Y    Y      Y    none
#   01ACOM         comm    32500 -       -              00   -     COMMERCIAL Y      Y    Y      Y    none
#   01AMOT-RC70    motor   32500 -       policy   -530  70   -     -          Y      N    Y      N    some
#   01AMOT-RC90    motor   32500 -       policy   -911  90   -     -          Y      N    Y      N    some
#   01AMOT-LGSQ    motor   32500 -       subtype  -803  90   LGSQ  MOTOR      Y      N    Y      Y    some
#   01ACOM-LGSQ    comm    32500 -       subtype  -803  90   LGSQ  COMMERCIAL Y      N    Y      Y    some
#   01AMOT-RC80    motor   32500 -       VSAM resp 12   80   -     MOTOR      Y      Y    Y      Y    some
#   01AMOT-RC98    motor      20 -       -              98   -     -          N      N    N      N    none
#   01AMOT-LGCA    motor       0 -       -              -    LGCA  -          N      N    N      N    some
#   01AXXX-RC99    motor   32500 01AXXX  -              99   -     -          N      N    N      N    none
#   01AHOU-ROUTE   house   32500 -       -              00   -     HOUSE      Y      Y    Y      Y    none
#   01AHOU-LGSQ    house   32500 -       subtype  -803  90   LGSQ  HOUSE      Y      N    Y      Y    some
# Row 01AMOT-LGCA carries no expected return code: the chain abends at
# [base/src/lgapol01.cbl:96-102] before the MOVE '00' that follows it, so
# CA-RETURN-CODE keeps the value the generated record carries, and that is what
# this script asserts. That value is the chain_populated_items seed of
# modernization/extraction/copybook_field_map.yml, which stands outside the
# codes of RETURN_CODE_DOMAIN, so the value this row asserts is one no step of
# the chain writes and the code every other row asserts is one the chain wrote.
# Every executed case asserts both the seed it read and that the seed is outside
# that domain.
# The endowment route is not executed: no row of the table selects it and every
# row asserts the endowment capture group absent. Under the mandated
# "-fbinary-truncate" the length subtraction of
# [base/src/lgapdb01.cbl:339-340] stays inside its PIC S9(4) COMP item, and a
# direct call of the translated LGAPDB01 on request id 01AEND at
# EIBCALEN=32500 returns '00' and writes the VSAM record under an "E" key. See
# modernization/docs/decision-log.md (planned deliverable; not present at this
# milestone), row: endowment route not executed.
#
# Two runtime properties of the chain the case table exercises but does not
# assert by name:
#
#   One diagnostic link from LGAPOL01, two from the programs below it.
#   WRITE-ERROR-MESSAGE of LGAPOL01 links the diagnostic program once
#   unconditionally and a second time only under "IF EIBCALEN > 0"
#   [base/src/lgapol01.cbl:149-166], and the only PERFORM of that paragraph
#   stands inside "IF EIBCALEN = ZERO" [base/src/lgapol01.cbl:96-102], so the
#   second link is unreachable by construction and the zero-length case reports
#   DIAG_LINK_COUNT=0001 carrying "NO COMMAREA RECEIVED" alone. The error paths
#   of LGAPDB01 and LGAPVS01 reach the same shape of paragraph with a COMMAREA
#   in hand [base/src/lgapdb01.cbl:575-592; base/src/lgapvs01.cbl:169-185] and
#   report DIAG_LINK_COUNT=0002. Every row of the case table whose "diag" field
#   says SOME is asserted at one link or more, so both counts pass that row.
#
#   WS-REQUIRED-CA-LEN accumulates across calls in one process.
#   "WS-REQUIRED-CA-LEN PIC S9(4) VALUE +0" [base/src/lgapol01.cbl:60;
#   base/src/lgapdb01.cbl:66] is never re-initialised, and each program adds to
#   it before comparing it with EIBCALEN [base/src/lgapol01.cbl:109;
#   base/src/lgapdb01.cbl:182-199], so a second call in the same process
#   compares against twice the requirement: 28, 56, 84 in LGAPOL01 and 165,
#   330, 495 for the motor route of LGAPDB01. A request that returns '00' at
#   EIBCALEN=30 therefore returns '98' from the second call onward. This is the
#   behaviour of the frozen source. Each case of this script is one process
#   making one chain call, and five calls in one process at EIBCALEN=32500 all
#   return '00' because the accumulated requirement stays below the length. A
#   host that calls these modules more than once per process has to CANCEL them
#   between calls to reproduce the first result.
#
# Probe table, one row per infrastructure probe. Each row names the environment
# item or the driver handle it makes wrong, the driver status this script
# asserts, and the side effect it asserts beside that status. None of them is a
# row of the case table.
# PRB5A, PRB5B and PRB5C are rejected before the chain is called and are handed
# no output handle at all, so nothing can stand at either output name
# afterwards; PRB7 reaches the call with both handles open; PRB4 reaches the
# chain and fails on the capture handle this script leaves closed.
# Every probe is handed the generated record of the probe fixture on the
# driver's standard input, the same record a case is handed, so each probe
# reports the item its row makes wrong rather than a record it did not receive.
#   label   wrong item                       status side effect asserted
#   PRB7    COB_LIBRARY_PATH with no modules 7      capture records no chain
#                                                   effect at all, post-chain
#                                                   record equals the record
#                                                   the driver read
#   PRB5A   HARNESS_CASE not provided        5      no capture, no post record,
#                                                   nothing but the driver log
#                                                   in the probe directory
#   PRB5B   HARNESS_CASE naming a path above 5      no capture, no post record,
#           the run directory                       no escaped directory,
#                                                   nothing but the driver log
#                                                   in the probe directory
#   PRB5C   HARNESS_FIXTURE empty            5      no capture, no post record,
#                                                   nothing but the driver log
#                                                   in the probe directory
#   PRB4    capture descriptor not open      4      nothing written into the
#                                                   capture name, post-chain
#                                                   name is the file this
#                                                   script opened for it
#
# Arguments:
#   [CASE]        A case label from the table, "all" for every row, or "both"
#                 for the two success cases 01AMOT and 01ACOM. Accepted in
#                 either letter case. Default: every row. Any other value is a
#                 usage error.
#   --case LABEL  Run the single case LABEL from the table.
#   --success-only
#                 Run the two success cases 01AMOT and 01ACOM.
#   --help, -h    Print the usage block and exit 0.
#
# Environment items honoured:
#   PY            Python interpreter used for the record builder and the
#                 translator. A relative value resolves from the repository
#                 root. Default: modernization/.venv/bin/python
#   COBC          COBOL compiler command. Default: cobc
#   COBC_EXTRA_FLAGS
#                 Compiler options added after the mandated
#                 "-std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy",
#                 which every compile passes whatever this variable holds. Only
#                 the options of the allow-list below are accepted; an unknown
#                 option, an option that would restate the source format, the
#                 numeric store of the dialect, the copybook folding, the
#                 copybook extension or an output selector, and an option that
#                 leaves the compiler intermediates outside the build directory
#                 ("-g" and "-save-temps" in either spelling), is a preflight
#                 failure that names the option. Default: unset.
#   COBC_FLAGS    Read under the same allow-list as COBC_EXTRA_FLAGS, with the
#                 mandated options accepted as no-ops. It cannot replace a
#                 mandated option. Default: unset.
#   HARNESS_POLICY_NUMBER
#                 Identity seed of the first row of the case table, one to nine
#                 digits above zero. Each later row receives the next value,
#                 whichever rows are selected, so 01AMOT receives the seed and
#                 01ACOM the value after it. Every run reserves one identity for
#                 each of the twelve rows of the table, a run of one case
#                 included, so the seed is also required to leave room for
#                 twelve consecutive values at or below 999999999: the highest
#                 seed any invocation accepts is 999999988, and a higher one is
#                 a preflight failure naming the value the table would reach.
#                 Default: 1000001.
#   HARNESS_LASTCHANGED
#                 Timestamp seed of every selected case, exactly twenty-six
#                 characters in YYYY-MM-DD-HH.MM.SS.NNNNNN form and free of
#                 spaces. Default: 2026-08-19-12.00.00.000000
#   HARNESS_STRICT_TOOL_VERSIONS
#                 A true value makes any compiler version other than the
#                 pinned one a preflight failure instead of a reported
#                 deviation. Default: unset.
#   HARNESS_LOCK_WAIT_SECONDS
#                 Seconds this script waits for the exclusive harness lock of
#                 the checkout before it gives up, one to 3600. A wait that
#                 runs out ends the run with exit 9 and leaves every shared
#                 path untouched. Default: 300.
#
# The three handles the driver is started with. This script opens all three,
# checks each opened descriptor rather than the name it came from, hands them
# over across the exec and closes them again as soon as the driver returns, so
# the driver names no file of its own and an entry that appears at one of those
# names while the driver runs reaches nothing:
#   standard input    the generated record of the case,
#                     <build>/samples/commarea_<fixture>.dat, opened read-only
#   descriptor 3      the post-chain record,
#                     <build>/run/<case>/commarea_post.dat, created exclusively
#   descriptor 4      the capture file, <build>/run/<case>/captures.txt,
#                     created exclusively
#
# Environment items exported to the driver:
#   COB_LIBRARY_PATH  module directory of this run
#   COB_LS_FIXED      1, the setting the full-length post-chain record is
#                     written under
#   COB_PRE_LOAD      the fifteen module names of this run
#   HARNESS_FIXTURE   fixture stem of the case, such as 01amot
#   HARNESS_CASE, HARNESS_POLICY_NUMBER, HARNESS_LASTCHANGED
#   HARNESS_COMMAREA_LENGTH, HARNESS_REQUEST_ID
#   HARNESS_INJECT_POLICY_SQLCODE, HARNESS_INJECT_SUBTYPE_SQLCODE,
#   HARNESS_INJECT_VSAM_RESP, HARNESS_INJECT_VSAM_RESP2
#   HARNESS_EXPECT_RETURN_CODE, HARNESS_EXPECT_ABEND, HARNESS_EXPECT_PRODUCT,
#   HARNESS_EXPECT_POLICY_SQL, HARNESS_EXPECT_VSAM, HARNESS_EXPECT_VALUES,
#   HARNESS_EXPECT_PRODUCT_VALUES, HARNESS_EXPECT_DIAG_LINKS
#
# Compiler environment items the preflight pins for the compile stage and the
# execution stage alike. Each one is removed from the environment of the caller
# first, and an ambient value that was removed is reported as a deviation
# naming the value that was ignored, so no run compiles or executes under a
# dialect, a run-time configuration or a set of C options this script did not
# choose:
#   COB_CONFIG_DIR      the configuration directory the compiler reports as its
#                       own, read from "cobc --info" with no ambient value in
#                       force. The dialect the mandated "-std=ibm" resolves
#                       inside it - the files of the ibm.conf include chain
#                       with the SHA-256 of each, and the value that chain
#                       leaves for binary-size, binary-truncate,
#                       binary-byteorder, hostsign and defaultbyte - is
#                       recorded at the head of the compile log
#   COB_RUNTIME_CONFIG  removed, so a module loads the run-time configuration of
#                       that installation
#   COB_CFLAGS          the C options that installation reports, with the
#                       _FORTIFY_SOURCE definition its host toolchain states
#                       twice reduced to the one that takes effect. A COBOL
#                       diagnostic is unaffected: it is still written to the
#                       compile log and still counted as a deviation
#
# Every generated file is written under modernization/harness/build. The one
# exception is the evidence publication of stage 6, which writes into
# modernization/validation/artifacts. Both roots are canonicalised and required
# to resolve inside this repository, every path this script creates, truncates,
# compiles into, appends a log to, copies or opens for the driver is refused
# when any component of it is a symbolic link or when the entry carries more
# than one hard link, the three handles the driver runs with are opened here and
# checked on the descriptor, and every externally supplied value reaches the
# output as one line of "\xNN" escapes.
#
# Driver exit statuses, reported for the operator when a case fails:
#   0 every check passed
#   1 the chain's return code differs from the expected code
#   2 the abend state differs from the expected abend state
#   3 a required capture is missing or inconsistent
#   4 a file input-output operation failed, the record on standard input held
#     no line, or that line held other than 32,500 characters
#   5 a required environment item was not provided or was rejected
#   6 a captured value differs from the fixture-derived expected value
#   7 the translated chain could not be called
#
# Capture grammar of the driver: one "NAME=VALUE" line per captured value, the
# name and the value each written at its trimmed width. The keys of the run
# itself stand first, CASE naming the label this script exported, FIXTURE the
# record it redirected onto standard input, SAMPLE_RECORD_LENGTH the characters
# the driver measured in that record and EIBCALEN_AT_CALL the length it called
# the chain with. Every case asserts SAMPLE_RECORD_LENGTH against the 32,500
# characters one generated record holds, so a case runs on a complete record or
# fails, and the width every value of the capture file was decoded at is stated
# in the file itself.
#
# Exit codes of this script:
#   0 every stage passed
#   1 usage error: an unrecognised argument, case or argument count
#   2 preflight failure: a missing tool, interpreter, input or directory, an
#     unusable compiler version, a rejected compiler option, a rejected path or
#     an invalid seed value
#   3 sample generation failure or a generated record of the wrong size
#   4 translation failure, a missing generated source, or a source whose
#     SHA-256 no longer matches the baseline the translator recorded
#   5 compilation failure or a missing module or driver
#   6 execution failure: a non-zero driver status, a probe of the probe table
#     that did not report the status or the side effect it asserts, or a failed
#     assertion of this script
#   7 evidence publication failure: a missing file to retain, a publication
#     check that did not leave the set its manifest describes, or a published
#     set that does not match the manifest published with it
#   8 source guard failure: modernization/validation/verify_readonly.sh did not
#     pass at one of the four points this script runs it
#   9 the exclusive harness lock of this checkout was still held by another run
#     when the bounded wait ran out; nothing of this run was created
# 143 a termination, interrupt or hangup signal reached this script: a command
#     it was still waiting on was ended with its whole process group and
#     reaped, and the harness lock of the checkout was released. The status
#     reports what the run had published: nothing when the signal arrived
#     before the replacement of the published set, the complete set when it
#     arrived inside that replacement - which is deferred to the end of it -
#     and otherwise how far each of the two loops of that replacement came
# Any non-zero code stops the fail-fast modernization/Makefile that invokes
# this script.
#
# Install this file with the execute bit set (chmod +x
# modernization/harness/run_harness.sh); "bash modernization/harness/
# run_harness.sh" runs it without one.
#
# Harness topology: Figure 5 — Validation Harness Control Flow in
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
readonly EXIT_GUARD=8
readonly EXIT_LOCK=9

# Status a run ends with when a termination, interrupt or hangup signal reaches
# it: 128 plus the number of SIGTERM, reported for all three so one status names
# an interrupted run. The command the run was waiting on is ended first, and the
# diagnostic names what the replacement of the published evidence set had
# reached when the signal arrived.
readonly EXIT_SIGNAL=143

# --------------------------------------------------------------------------
# Fixed harness values
# --------------------------------------------------------------------------
# Stages this script runs, reported in every stage line.
readonly STAGE_COUNT=6

# One generated COMMAREA record is 32,500 characters and one line feed.
readonly RECORD_BYTES=32501

# Characters of that record, the width the driver measures the record it read
# at and reports in its SAMPLE_RECORD_LENGTH capture. The line feed of
# RECORD_BYTES ends the line and is not part of the record.
readonly RECORD_CHARACTERS=32500

# The COMMAREA length the chain links with, and the length the driver calls
# with unless the case row names a shorter one.
readonly COMMAREA_LENGTH=32500

# Length of the KSDSPOLY record the projection writes, the length of the key it
# writes it under, and the length of the product projection that follows the
# key inside the record [base/src/lgapvs01.cbl:25-51].
readonly VSAM_RECORD_LENGTH=64
readonly VSAM_KEY_LENGTH=21
readonly VSAM_PAYLOAD_LENGTH=43

# Length of the hexadecimal form of each of those three values: two characters
# per byte. The record, the key and the projection are compared in that form,
# so a byte that holds a blank is compared as "20" and a value that carries
# fewer bytes than the source writes fails on its length.
readonly VSAM_RECORD_HEX_LENGTH=128
readonly VSAM_KEY_HEX_LENGTH=42
readonly VSAM_PAYLOAD_HEX_LENGTH=86

# File the projection writes the record to.
readonly VSAM_FILE_NAME="KSDSPOLY"

# Seconds the driver of one case, and one source-guard run, are allowed. A
# command that has not returned by then ends the stage that started it.
readonly DRIVER_TIMEOUT_SECONDS=120
readonly GUARD_TIMEOUT_SECONDS=180

# The exclusive lock one run of this script holds on the build tree of its
# checkout, named below the build directory the run resolves and covered by the
# ignore rules of modernization/.gitignore. It is taken before any shared build
# path is created or read and released when the run ends, so a second
# invocation on the same checkout waits rather than regenerating a sample, a
# module or a published name under a run that is still using it. The file
# carries no content: it is opened for append and never written.
readonly HARNESS_LOCK_NAME="harness.lock"

# Seconds a run waits for that lock, and the range HARNESS_LOCK_WAIT_SECONDS is
# accepted in. The default is above the duration of a complete run, so two runs
# started together both finish; a wait that runs out ends the run with
# EXIT_LOCK and leaves every shared path untouched.
readonly HARNESS_LOCK_WAIT_DEFAULT=300
readonly HARNESS_LOCK_WAIT_MAX=3600

# Seconds an interrupted run leaves between the two signals it ends the command
# it was waiting on with: SIGTERM reaches the whole process group of that
# command, and SIGKILL reaches whatever still stands after this pause. The
# command and the process recording its output are both reaped before the run
# exits, so no child of this script outlives it and no descendant keeps the
# harness lock of the checkout open.
readonly TERMINATE_GRACE_SECONDS=0.1

# Compiler release the dependency inventory pins, and the lowest release of
# the same major series this script accepts.
readonly COBC_VERSION_PINNED="3.1.2.0"
readonly COBC_VERSION_FLOOR="3.1.2"
readonly COBC_MAJOR_REQUIRED=3

# Python release series the record builder and the translator run under.
readonly PYTHON_SERIES="3.12"

# Compiler options every module and the driver are compiled with, in this
# order, whatever the environment names.
#
# Under "-fbinary-truncate" a binary receiving item keeps only the digits its
# PICTURE declares; the dialect configuration that "-std=ibm" resolves to
# leaves that truncation off. Measured on the endowment route: the
# "SUBTRACT WS-REQUIRED-CA-LEN FROM EIBCALEN GIVING WS-VARY-LEN" of
# [base/src/lgapdb01.cbl:339-340] leaves 32348 in its PIC S9(4) COMP item at
# the chain's own COMMAREA length without the option and 2348 with it, and the
# reference-modified MOVE that follows [base/src/lgapdb01.cbl:341-345]
# addresses that many characters of a 3,900-character item. No value the case
# table asserts changes under the option: every count, length and amount of the
# two success cases is a display numeric, a PIC S9(4) COMP-5 item, or a value
# that already fits its picture.
# See planned decision-log row: IBM binary truncation pinned for the harness
# compile.
readonly -a COBC_FLAGS_MANDATED=("-std=ibm" "-fbinary-truncate"
  "-ffold-copy=LOWER" "-ext" "cpy")

# Compiler options COBC_EXTRA_FLAGS and COBC_FLAGS may add. Each adds
# diagnostics, run-time checking or optimisation, none of them restates a
# mandated option, and none of them writes a file: a compile carrying any one
# of them leaves only the module named by "-o".
readonly -a COBC_FLAGS_ALLOWED_EXTRA=("-debug" "-Wall" "-W" "-Wextra"
  "-ftrace" "-ftraceall" "-fstack-check" "-v" "--verbose"
  "-O" "-O2" "-Os")

# Options refused by name, as "<option>|<what it does>". Each keeps the
# compiler intermediates of every compile, and the compiler writes them beside
# the working directory of this script, which is the repository root, rather
# than under the build directory. The refusal names the option and the options
# that add the same checking without writing a file.
readonly -a COBC_FLAGS_REFUSED=(
  "-g|keeps the C intermediates of every compile in the working directory"
  "-save-temps|keeps the C intermediates of every compile in the working directory"
  "--save-temps|keeps the C intermediates of every compile in the working directory"
)

# Option prefixes an extra option may not carry, as "<prefix>|<what it names>".
# Each names a setting this script fixes itself, so an extra option carrying one
# of them is refused rather than passed on.
readonly -a COBC_FLAGS_CONFLICTING=(
  "-std|the COBOL dialect"
  "-fbinary-truncate|the numeric store of the dialect"
  "-fno-binary-truncate|the numeric store of the dialect"
  "-ffold-copy|the copybook name folding"
  "-ext|the copybook extension"
  "-free|the source format"
  "-fixed|the source format"
  "-I|the include directory"
  "-o|the output name"
  "-m|the output kind"
  "-x|the output kind"
  "-c|the output kind"
  "-b|the output kind"
)

# Compiler environment items this script pins before the first compile and
# holds pinned through the execution stage. The dialect a compile resolves, the
# run-time configuration a module loads and the C options the compiler hands
# its own back end come from these pinned values and not from the environment
# of the caller. An item the caller exported is reported as a deviation naming
# the value that was ignored, and the dialect the run resolved is recorded in
# the compile log.
#   COB_CONFIG_DIR      pinned to the configuration directory the compiler
#                       reports as its own, the directory the mandated
#                       "-std=ibm" resolves its files in
#   COB_RUNTIME_CONFIG  removed; a module loads the run-time configuration of
#                       that installation
#   COB_CFLAGS          pinned to the C options the compiler reports as its
#                       own, with the duplicated _FORTIFY_SOURCE definition of
#                       the host toolchain reduced to the one definition that
#                       takes effect. Every COBOL diagnostic is still reported
#                       and still counted
# See planned decision-log row: compiler environment pinned for the harness
# compile and execution.
readonly -a COBC_PINNED_ENVIRONMENT=("COB_CONFIG_DIR" "COB_RUNTIME_CONFIG"
  "COB_CFLAGS")

# The C preprocessor definition the host toolchain states twice, once through
# the options of the compiler and once through those of its distribution
# packaging. Both definitions reach one command line, the later one takes
# effect, and the host C compiler reports the redefinition once per compile.
readonly COBC_CFLAGS_DUPLICATED_DEFINE="-D_FORTIFY_SOURCE="

# The dialect file the mandated "-std=ibm" names inside the configuration
# directory of the compiler, the deepest include chain read from it, and the
# keys of that resolved chain the harness depends on:
#   binary-size       the storage one PIC S9(4) COMP item of the shared
#                     copybooks occupies
#   binary-truncate   whether a binary receiving item keeps only the digits its
#                     PICTURE declares; the mandated "-fbinary-truncate" pins
#                     this on whatever the chain resolves
#   binary-byteorder  the byte order of that storage, which every module of one
#                     run shares
#   hostsign          the sign representation of a signed display item
#   defaultbyte       the byte an item without a VALUE clause starts at, which
#                     the three EXTERNAL harness copybooks rely on
readonly COBC_DIALECT_ENTRY="ibm.conf"
readonly COBC_DIALECT_MAX_DEPTH=8
readonly -a COBC_DIALECT_KEYS=("binary-size" "binary-truncate"
  "binary-byteorder" "hostsign" "defaultbyte")

# Identity and timestamp seeds. HARNESS_POLICY_NUMBER names the seed of the
# first row of the case table; each later row receives the next value.
readonly POLICY_NUMBER_DEFAULT=1000001
readonly LASTCHANGED_DEFAULT="2026-08-19-12.00.00.000000"
readonly LASTCHANGED_LENGTH=26
readonly POLICY_NUMBER_MAX=999999999

# The case table, one row per case, in execution order. Fields, separated by
# "|":
#    1 label                  case label, also the run directory name and the
#                             value of HARNESS_CASE
#    2 fixture                generated record the case runs on
#    3 commarea length        value of HARNESS_COMMAREA_LENGTH
#    4 request id override    value of HARNESS_REQUEST_ID, empty for the
#                             request id the fixture carries
#    5 policy SQLCODE         value of HARNESS_INJECT_POLICY_SQLCODE
#    6 subtype SQLCODE        value of HARNESS_INJECT_SUBTYPE_SQLCODE
#    7 VSAM response          value of HARNESS_INJECT_VSAM_RESP
#    8 VSAM response 2        value of HARNESS_INJECT_VSAM_RESP2
#    9 expected return code   two characters, or NONE for the value the
#                             generated record carries
#   10 expected abend         NONE or a four-character code
#   11 expected product       MOTOR, COMMERCIAL, ENDOWMENT, HOUSE or NONE
#   12 policy SQL expected    Y or N
#   13 VSAM write expected    Y or N
#   14 values asserted        Y or N
#   15 product values         Y or N
#   16 diagnostic links       NONE or SOME
readonly -a HARNESS_CASES=(
  "01AMOT|01amot|32500||0|0|0|0|00|NONE|MOTOR|Y|Y|Y|Y|NONE"
  "01ACOM|01acom|32500||0|0|0|0|00|NONE|COMMERCIAL|Y|Y|Y|Y|NONE"
  "01AMOT-RC70|01amot|32500||-530|0|0|0|70|NONE|NONE|Y|N|Y|N|SOME"
  "01AMOT-RC90|01amot|32500||-911|0|0|0|90|NONE|NONE|Y|N|Y|N|SOME"
  "01AMOT-LGSQ|01amot|32500||0|-803|0|0|90|LGSQ|MOTOR|Y|N|Y|Y|SOME"
  "01ACOM-LGSQ|01acom|32500||0|-803|0|0|90|LGSQ|COMMERCIAL|Y|N|Y|Y|SOME"
  "01AMOT-RC80|01amot|32500||0|0|12|0|80|NONE|MOTOR|Y|Y|Y|Y|SOME"
  "01AMOT-RC98|01amot|20||0|0|0|0|98|NONE|NONE|N|N|N|N|NONE"
  "01AMOT-LGCA|01amot|0||0|0|0|0|NONE|LGCA|NONE|N|N|N|N|SOME"
  "01AXXX-RC99|01amot|32500|01AXXX|0|0|0|0|99|NONE|NONE|N|N|N|N|NONE"
  "01AHOU-ROUTE|01ahou|32500||0|0|0|0|00|NONE|HOUSE|Y|Y|Y|Y|NONE"
  "01AHOU-LGSQ|01ahou|32500||0|-803|0|0|90|LGSQ|HOUSE|Y|N|Y|Y|SOME"
)

# Every case label of the table, in execution order. The default selection.
readonly -a ALL_CASES=("01AMOT" "01ACOM" "01AMOT-RC70" "01AMOT-RC90"
  "01AMOT-LGSQ" "01ACOM-LGSQ" "01AMOT-RC80" "01AMOT-RC98" "01AMOT-LGCA"
  "01AXXX-RC99" "01AHOU-ROUTE" "01AHOU-LGSQ")

# The two cases that traverse the chain to a written VSAM record and return
# '00'. Selected by "both" and by --success-only, and the only cases whose
# driver log and capture file are published as evidence.
readonly -a SUCCESS_CASES=("01AMOT" "01ACOM")

# Fixtures the table runs on, in generation order. A built fixture names one
# sample definition under modernization/extraction/sample_input and one
# generated record; a derived fixture is written by this script from the record
# of the fixture it names, which the list carries before it.
readonly -a HARNESS_FIXTURES=("01amot" "01acom" "01ahou")

# Derived fixtures, as "<fixture>|<fixture its record is written from>".
readonly -a DERIVED_FIXTURES=("01ahou|01amot")

# The overlay the derived house record carries, as "<field>|<kind>|<value>".
# The field is an entry of FIXTURE_FIELDS below, so one offset and length locate
# it both when this script writes the record and when it reads the record back
# to build the values it asserts. A "text" value is written blank-padded to the
# width of its field, the width an alphanumeric item of the COMMAREA carries; a
# "number" value is required to fill its field with digits, the form a display
# numeric of the COMMAREA carries, so no house field this record hands the
# chain is invalid numeric data.
#
# The request id stands at characters 1 to 6 [base/src/lgcmarea.cpy:10] and
# routes the chain to the house branch [base/src/lgapdb01.cbl:190-192]. The six
# house fields stand at characters 101 to 158 [base/src/lgcmarea.cpy:56-62].
# Characters 159 on hold CA-H-FILLER [base/src/lgcmarea.cpy:63] and keep the
# characters the record this one is written from carries there: the house route
# reads the six house fields and nothing after them
# [base/src/lgapdb01.cbl:405-424; base/src/lgapvs01.cbl:117-122].
readonly HOUSE_FIXTURE="01ahou"
readonly -a HOUSE_FIXTURE_OVERLAY=(
  "request_id|text|01AHOU"
  "house_proptype|text|DETACHED"
  "house_bedrooms|number|004"
  "house_value|number|00275000"
  "house_name|text|LAUREL COTTAGE"
  "house_number|text|17"
  "house_postcode|text|PO16 7GZ"
)

# The probe table, one row per infrastructure probe, in execution order. A
# probe runs the driver with one item of its environment, or one of the three
# handles this script opens for it, made wrong, and asserts the status the
# driver reports and the side effect the header of this script records for that
# probe. No probe is a case of the case table, so the rule that any non-zero
# driver status fails a case still holds for every case.
# Fields, separated by "|":
#    1 label        probe label, also the run directory name of the probe and
#                   the value of HARNESS_CASE, which the driver reports whole in
#                   its CASE capture
#    2 wrong item   the environment item or driver handle this probe makes wrong
#    3 status       the driver status this probe asserts
#    4 description  what the probe does, reported in the summary
readonly -a HARNESS_PROBES=(
  "PRB7|COB_LIBRARY_PATH|7|module directory of the run holds no module"
  "PRB5A|HARNESS_CASE|5|case is not provided"
  "PRB5B|HARNESS_CASE|5|case names a path above the run directory"
  "PRB5C|HARNESS_FIXTURE|5|fixture is empty"
  "PRB4|capture descriptor|4|capture descriptor of the driver is not open"
)

# The fixture every probe runs on. Its record is generated by every run,
# whichever cases the command line selected.
readonly PROBE_FIXTURE="01amot"

# Value PRB5B hands the driver as HARNESS_CASE. A driver that accepts it writes
# into the parent of the run directory instead of a directory below it, so the
# probe asserts that neither spelling of the escaped name was created.
readonly PROBE_ESCAPING_CASE="../ESC"

# Directory below the build directory that holds no module, and the directory
# the probes below the build directory are created in.
readonly PROBE_DIR_NAME="probe"
readonly PROBE_EMPTY_MODULES_NAME="no-modules"

# Product capture groups, as "<product>|<capture key prefix>". Exactly one
# group is expected per case that reaches a product insert, and every other
# group is expected absent.
readonly -a PRODUCT_GROUPS=(
  "MOTOR|SQL_MOTOR"
  "COMMERCIAL|SQL_COMMERCIAL"
  "ENDOWMENT|SQL_ENDOWMENT"
  "HOUSE|SQL_HOUSE"
)

# Offset and length, in 1-based characters of the generated record, of every
# field this script reads out of it. The record is fixed-width, so one offset
# and length locate one field in every generated record.
#
# The ten header and common fields, the nine motor fields and the sixteen
# commercial fields carry the offset and length the layout of
# modernization/extraction/copybook_field_map.yml states for the request header,
# the common policy section and those two overlays. The six house fields are the
# declarations of the house overlay itself, which follows the 100 characters of
# the header and the common policy section: CA-H-PROPERTY-TYPE at 101 for 15,
# CA-H-BEDROOMS at 116 for 3, CA-H-VALUE at 119 for 8, CA-H-HOUSE-NAME at 127
# for 20, CA-H-HOUSE-NUMBER at 147 for 4 and CA-H-POSTCODE at 151 for 8
# [base/src/lgcmarea.cpy:56-62]. That same file records those six under
# derived_samples, as the overlay this script writes over the motor record to
# generate the house fixture; it does not carry them in its layout section,
# which records the house overlay by its start offset alone.
declare -rA FIXTURE_FIELDS=(
  [request_id]="1 6"
  [return_code]="7 2"
  [customer_num]="9 10"
  [policy_num]="19 10"
  [issue_date]="29 10"
  [expiry_date]="39 10"
  [lastchanged]="49 26"
  [brokerid]="75 10"
  [brokersref]="85 10"
  [payment]="95 6"
  [motor_make]="101 15"
  [motor_model]="116 15"
  [motor_value]="131 6"
  [motor_regnumber]="137 7"
  [motor_colour]="144 8"
  [motor_cc]="152 4"
  [motor_manufactured]="156 10"
  [motor_premium]="166 6"
  [motor_accidents]="172 6"
  [house_proptype]="101 15"
  [house_bedrooms]="116 3"
  [house_value]="119 8"
  [house_name]="127 20"
  [house_number]="147 4"
  [house_postcode]="151 8"
  [commercial_address]="101 255"
  [commercial_postcode]="356 8"
  [commercial_latitude]="364 11"
  [commercial_longitude]="375 11"
  [commercial_customer]="386 255"
  [commercial_proptype]="641 255"
  [commercial_fireperil]="896 4"
  [commercial_firepremium]="900 8"
  [commercial_crimeperil]="908 4"
  [commercial_crimepremium]="912 8"
  [commercial_floodperil]="920 4"
  [commercial_floodpremium]="924 8"
  [commercial_weatherperil]="932 4"
  [commercial_weatherpremium]="936 8"
  [commercial_status]="944 4"
  [commercial_rejectreason]="948 255"
)

# Capture keys of the driver this script reads by a name that may differ
# between driver revisions, as "<item>|<name> <name> ...". The first name the
# capture file carries is read; a case whose capture file carries none of the
# names of an item fails, so an item that stops being emitted cannot pass.
declare -rA CAPTURE_KEY_NAMES=(
  [policy_count]="SQL_POLICY_COUNT SQL_POLICY_CALLS"
  [identity_count]="SQL_IDENTITY_CALLS SQL_IDENTITY_COUNT"
  [lastchanged_count]="SQL_LASTCHANGED_CALLS SQL_LASTCHANGED_COUNT"
  [motor_count]="SQL_MOTOR_COUNT SQL_MOTOR_CALLS"
  [commercial_count]="SQL_COMMERCIAL_COUNT SQL_COMMERCIAL_CALLS"
  [endowment_count]="SQL_ENDOWMENT_COUNT SQL_ENDOWMENT_CALLS"
  [house_count]="SQL_HOUSE_COUNT SQL_HOUSE_CALLS"
  [vsam_count]="VSAM_COUNT VSAM_CALLS"
  [abend_count]="ABEND_COUNT ABEND_CALLS"
  [policy_seq]="SQL_POLICY_SEQ SQL_POLICY_ORDINAL"
  [identity_seq]="SQL_IDENTITY_SEQ SQL_IDENTITY_ORDINAL"
  [lastchanged_seq]="SQL_LASTCHANGED_SEQ SQL_LASTCHANGED_ORDINAL"
  [motor_seq]="SQL_MOTOR_SEQ SQL_MOTOR_ORDINAL"
  [commercial_seq]="SQL_COMMERCIAL_SEQ SQL_COMMERCIAL_ORDINAL"
  [endowment_seq]="SQL_ENDOWMENT_SEQ SQL_ENDOWMENT_ORDINAL"
  [house_seq]="SQL_HOUSE_SEQ SQL_HOUSE_ORDINAL"
  [vsam_seq]="VSAM_SEQ VSAM_ORDINAL"
  [order_violation]="ORDER_VIOLATION HC_ORDER_VIOLATION SQL_ORDER_VIOLATION"
  [link_db2_calen]="LINK_DB2_CALEN CHAIN_DB2_CALEN"
  [link_vsam_calen]="LINK_VSAM_CALEN CHAIN_VSAM_CALEN"
  [vsam_record]="VSAM_RECORD VSAM_RECORD_IMAGE"
)

# Capture keys every case is required to carry, whatever its row says.
# SAMPLE_RECORD_LENGTH carries the characters the driver measured in the record
# it read; a case is asserted against RECORD_CHARACTERS, so a record the sample
# step generated short, or one a broken stream truncated, fails the case instead
# of running the chain on a record the reader padded with spaces.
# FIXTURE_RETURN_CODE carries the two characters the record held in the
# CA-RETURN-CODE window before the chain ran, so a driver that stops publishing
# the value CA_RETURN_CODE is read against fails the case.
readonly -a CAPTURE_KEYS_BASE=("CASE" "FIXTURE" "SAMPLE_RECORD_LENGTH"
  "EIBCALEN_AT_CALL" "CA_REQUEST_ID" "FIXTURE_RETURN_CODE"
  "CA_RETURN_CODE" "CA_PAYMENT" "DRIVER_STATUS" "ABEND_PRESENT" "ABEND_CODE"
  "DIAG_LINK_COUNT" "SQL_POLICY_PRESENT" "SQL_IDENTITY_PRESENT"
  "SQL_LASTCHANGED_PRESENT" "SQL_MOTOR_PRESENT" "SQL_COMMERCIAL_PRESENT"
  "SQL_ENDOWMENT_PRESENT" "SQL_HOUSE_PRESENT" "SQLCODE_LAST" "VSAM_PRESENT")

# The codes the chain writes into CA-RETURN-CODE [base/src/lgapol01.cbl:105,114;
# base/src/lgapdb01.cbl:172,204,211,239,293,296,301,390,428,474,548;
# base/src/lgapvs01.cbl:144], which are also the codes
# modernization/extraction/copybook_field_map.yml records as the domain of its
# return_code logical entry. The generated record carries the
# chain_populated_items seed of that file in the CA-RETURN-CODE window, and
# every executed case asserts that the seed it read is none of these values, so
# a row that expects one of them cannot pass on a window the chain left
# untouched.
readonly -a RETURN_CODE_DOMAIN=("00" "70" "80" "90" "98" "99")

# Capture keys a case whose policy insert succeeded is required to carry: the
# identity read and the timestamp read of [base/src/lgapdb01.cbl:307-321] then
# run, and the timestamp read carries the identity as its predicate host.
readonly -a CAPTURE_KEYS_IDENTITY=("SQL_LASTCHANGED_POLICYNUM")

# Capture keys a case whose row asserts values is required to carry.
readonly -a CAPTURE_KEYS_VALUES=("CA_CUSTOMER_NUM" "CA_POLICY_NUM"
  "CA_ISSUE_DATE" "CA_EXPIRY_DATE" "CA_LASTCHANGED" "CA_BROKERID"
  "CA_BROKERSREF")

# COMMAREA amount keys of one request id, as "<request id>|<key> <key> ...".
# The chain moves these amounts into its host variables and writes none of them
# back [base/src/lgapdb01.cbl:261-287,440-470,486-545], so every case that calls
# with the request id carries them at the value its generated record holds.
readonly -a CAPTURE_KEYS_AMOUNTS=(
  "01AMOT|CA_M_PREMIUM"
  "01ACOM|CA_B_FIREPREMIUM CA_B_CRIMEPREMIUM CA_B_FLOODPREMIUM CA_B_WEATHERPREMIUM"
)

# Capture keys a case whose row expects the policy insert is required to carry.
readonly -a CAPTURE_KEYS_POLICY=("SQL_POLICY_CUSTOMERNUM"
  "SQL_POLICY_ISSUEDATE" "SQL_POLICY_EXPIRYDATE" "SQL_POLICY_POLICYTYPE"
  "SQL_POLICY_BROKERID" "SQL_POLICY_BROKERSREF" "SQL_POLICY_PAYMENT"
  "SQL_POLICY_ASSIGNED_NUMBER" "SQL_POLICY_ASSIGNED_LASTCHANGED")

# Capture keys a case whose row expects a written VSAM record is required to
# carry.
readonly -a CAPTURE_KEYS_VSAM=("VSAM_FILE" "VSAM_LENGTH" "VSAM_KEYLENGTH"
  "VSAM_KEY" "VSAM_RID_KEY" "VSAM_REQUEST_ID" "VSAM_CUSTOMER_NUM"
  "VSAM_POLICY_NUM" "VSAM_RESP" "VSAM_PAYLOAD" "VSAM_RID_REQUEST_ID"
  "VSAM_RID_CUSTOMER_NUM" "VSAM_RID_POLICY_NUM" "VSAM_KEY_EXPECTED"
  "VSAM_PAYLOAD_EXPECTED" "VSAM_PAYLOAD_DERIVED")

# Hexadecimal capture keys of the same write, as "<key>|<hex characters>". Each
# carries two characters per byte of the value it names: the whole 64-byte
# record the write was given, the record the driver derived from the record of
# the case, the 43-byte product projection and the 21-byte key of the RIDFLD
# operand. A blank byte is "20" in these values, so they are compared whole,
# with no character removed from either side, and a value that carries fewer
# characters than the source writes fails on its length.
readonly -a CAPTURE_KEYS_VSAM_HEX=(
  "VSAM_RECORD_HEX|${VSAM_RECORD_HEX_LENGTH}"
  "VSAM_RECORD_EXPECTED_HEX|${VSAM_RECORD_HEX_LENGTH}"
  "VSAM_PAYLOAD_HEX|${VSAM_PAYLOAD_HEX_LENGTH}"
  "VSAM_RID_KEY_HEX|${VSAM_KEY_HEX_LENGTH}"
)

# Capture keys a motor case whose row asserts product values is required to
# carry.
readonly -a CAPTURE_KEYS_MOTOR=("SQL_MOTOR_POLICYNUM" "SQL_MOTOR_MAKE"
  "SQL_MOTOR_MODEL" "SQL_MOTOR_VALUE" "SQL_MOTOR_REGNUMBER"
  "SQL_MOTOR_COLOUR" "SQL_MOTOR_CC" "SQL_MOTOR_MANUFACTURED"
  "SQL_MOTOR_PREMIUM" "SQL_MOTOR_ACCIDENTS")

# Capture keys a commercial case whose row asserts product values is required
# to carry.
readonly -a CAPTURE_KEYS_COMMERCIAL=("SQL_COMMERCIAL_POLICYNUM"
  "SQL_COMMERCIAL_REQUESTDATE" "SQL_COMMERCIAL_STARTDATE"
  "SQL_COMMERCIAL_RENEWALDATE"
  "SQL_COMMERCIAL_ADDRESS" "SQL_COMMERCIAL_ZIPCODE"
  "SQL_COMMERCIAL_LATITUDEN" "SQL_COMMERCIAL_LONGITUDEW"
  "SQL_COMMERCIAL_CUSTOMER" "SQL_COMMERCIAL_PROPERTYTYPE"
  "SQL_COMMERCIAL_FIREPERIL" "SQL_COMMERCIAL_FIREPREMIUM"
  "SQL_COMMERCIAL_CRIMEPERIL" "SQL_COMMERCIAL_CRIMEPREMIUM"
  "SQL_COMMERCIAL_FLOODPERIL" "SQL_COMMERCIAL_FLOODPREMIUM"
  "SQL_COMMERCIAL_WEATHERPERIL" "SQL_COMMERCIAL_WEATHERPREMIUM"
  "SQL_COMMERCIAL_STATUS" "SQL_COMMERCIAL_REJECTIONREASON")

# Capture keys a house case whose row asserts product values is required to
# carry: the seven host values of the block at
# [base/src/lgapdb01.cbl:409-425].
readonly -a CAPTURE_KEYS_HOUSE=("SQL_HOUSE_POLICYNUM"
  "SQL_HOUSE_PROPERTYTYPE" "SQL_HOUSE_BEDROOMS" "SQL_HOUSE_VALUE"
  "SQL_HOUSE_HOUSENAME" "SQL_HOUSE_HOUSENUMBER" "SQL_HOUSE_POSTCODE")

# The amount tolerance the comparison contract accepts, in hundredths. The six
# amount fields are whole-number display values, so a non-zero delta inside the
# tolerance is reported as unexpected and the case still passes.
readonly AMOUNT_TOLERANCE_HUNDREDTHS=1

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

# The read-only scope gate every stage boundary runs, and the evidence log it
# appends its block to, which the preflight of a run empties before the first
# gate. The gate holds the approved SHA-256 baseline of the five named source
# artifacts; this script runs it and reports its verdict.
#
# The log stands with the other stage logs of the run, under the generated build
# tree the ignore rules of modernization/.gitignore cover, so a gate run writes
# no tracked file. This script creates it empty at the start of every run
# and publishes it with the other evidence of that run, so the published copy
# carries the four blocks of one run rather than the accumulated blocks of
# every run of the checkout. Every gate asks the guard for its reproducible
# block, so those four blocks hold the same bytes in any checkout.
# See planned decision-log row: read-only gate log published with the evidence
# set.
readonly SOURCE_GUARD="modernization/validation/verify_readonly.sh"
readonly SOURCE_GUARD_LOG_NAME="readonly-check.log"
readonly SOURCE_GUARD_LOG="modernization/harness/build/logs/readonly-check.log"

# Directories this script writes into, relative to the repository root. Every
# path it creates resolves inside one of them.
readonly BUILD_DIR_RELATIVE="modernization/harness/build"
readonly ARTIFACTS_DIR_RELATIVE="modernization/validation/artifacts"

# Report the translator publishes, and the two link sites this script asserts
# in it, as "<program>|<target program>".
readonly TRANSLATION_REPORT_NAME="translation-report.json"
readonly -a CHAIN_LINK_SITES=(
  "lgapol01.cbl|LGAPDB01"
  "lgapdb01.cbl|LGAPVS01"
)

# Stage files this script publishes into the validation artifacts directory,
# all five collected from the stage logs of the run - the fifth being the
# evidence log of the source guard, emptied once in the preflight of a run and
# appended to by each gate of that run. Every run publishes these five, and with
# them the manifest of the run and the driver log, the capture file and the
# post-chain record of each success case it executed.
readonly -a PUBLISHED_STAGE_ARTIFACTS=("translate.log" "compile.log"
  "translation-report.json" "source-baseline.sha256"
  "$SOURCE_GUARD_LOG_NAME")

# Name of the manifest of one run, written beside the stage logs and published
# with the set it describes. It carries the provenance of the run as comment
# lines and one "sha256sum" line per other file of the set, and it is read back
# from the published directory after the set has been placed there.
readonly EVIDENCE_MANIFEST_NAME="evidence-manifest.sha256"

# Names this script owns in the validation artifacts directory: the five stage
# files above, the manifest, and three names per success case of the case table.
# A run publishes the subset its selection produced - six names for a run that
# executed no success case, nine for one and twelve for both - and removes every
# other owned name, so the published set is the set of one run and carries no
# artifact of a case that run did not execute. evidence_owned_names prints them.
#
# Name in that directory this script never writes: the environment record of the
# checkout. It stands outside the published set and outside the replacement, and
# the manifest of every set records it as standing outside. Any further name
# found beside a published set is reported in the run summary.
readonly RUNTIME_VERSIONS_NAME="runtime-versions.txt"

# Directory of the run's staging tree the publication check works in. It holds
# the simulated published directory and the staged set that replaces its
# content, both created and filled by that check alone.
readonly PUBLICATION_CHECK_NAME="publication-check"

# External tools every run invokes, beyond the compiler and the interpreter.
# "git" is invoked by the translator and by the source guard, "stat" reads the
# status of every name and of every descriptor this script opens, "flock" takes
# the exclusive harness lock of this run and is invoked again by the source
# guard, and "dd" reads the fields this script asserts out of the generated
# record and writes the overlay of the derived record.
readonly -a REQUIRED_TOOLS=("mkdir" "rm" "mv" "cat" "tee" "wc" "grep"
  "sha256sum" "date" "head" "git" "stat" "flock" "dd" "timeout")

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
STAGING_DIR=""

# The exclusive harness lock of this run: the file it is taken on, the
# descriptor it is held through until the run ends, and the seconds the run
# waited for it at most.
HARNESS_LOCK_PATH=""
HARNESS_LOCK_FD=""
HARNESS_LOCK_WAIT=""

# Identifier of this run, used for the staging directory name and reported in
# the summary.
RUN_ID=""

# Cases selected by the command line, and the fixtures they need.
declare -a SELECTED_CASES=()
declare -a SELECTED_FIXTURES=()

# The selection the command line asked for, as one word: "all", "both",
# "success-only" or the label of the single case. Recorded in the manifest of
# the run and in the run summary, so the published evidence states which
# invocation produced it.
CASE_SELECTION=""

# Measured tool versions, filled in by the preflight.
COBC_VERSION=""
COBC_VERSION_VERDICT=""
PYTHON_VERSION=""

# Compiler options of this run: the argument list every compile passes to the
# compiler, the same list as one string for the messages, and the extra
# options the environment added to the mandated ones.
declare -a COBC_FLAG_LIST=()
COBC_FLAGS_EFFECTIVE=""
COBC_FLAGS_EXTRA_ACCEPTED=""

# The compiler environment this run pinned: the "--info" output every pinned
# value is read from, the configuration directory and the C options the run
# pinned, and the ambient values the pin replaced, one
# "<item>=<value>" entry per item the caller had exported.
COBC_INFO_TEXT=""
COBC_CONFIG_DIR_PINNED=""
COBC_CFLAGS_PINNED=""
declare -a COBC_AMBIENT_IGNORED=()

# The dialect this run resolved out of the pinned configuration directory: one
# "<file>|<kind>|<sha256>" entry per file of the include chain in the order the
# compiler reads them, the resolved value of each key of COBC_DIALECT_KEYS, and
# the file whose last assignment of that key produced it.
declare -a COBC_DIALECT_FILES=()
declare -A COBC_DIALECT_VALUE=()
declare -A COBC_DIALECT_SOURCE=()
declare -A COBC_DIALECT_SEEN=()

# Resolved seeds.
POLICY_NUMBER_BASE=""
LASTCHANGED_SEED=""

# Colon-separated module names handed to the runtime as a resolution aid.
MODULE_PRELOAD=""

# Status of the most recent command run through run_and_tee, and the status of
# the "tee" that wrote its log.
RUN_STATUS=0
RUN_LOG_STATUS=0

# The command run_and_tee is waiting on, while one runs: the process group it
# and its own children stand in, the start time /proc reports for the leader of
# that group, the identifier of the "tee" recording its output, the start time
# /proc reports for that process, and the name the command was started under.
# Each identifier is set at the spawn of the process it names and the start time
# of that process next to it, and the pair is emptied as the process is reaped,
# the identifier first. terminate_run reads both halves and signals nothing whose
# /proc entry does not still report this shell as its parent, and that recorded
# start time when one is recorded, so an identifier this run has already reaped,
# and that another process could have received since, is never signalled.
RUN_CHILD_PGID=""
RUN_CHILD_START=""
RUN_LOG_PID=""
RUN_LOG_START=""
RUN_CHILD_NAME=""

# The three descriptors the driver of one case or one probe runs with, held by
# this script while that driver runs. open_driver_input opens the generated
# record of the case on a descriptor of its own and records it here, which
# run_and_tee duplicates onto the standard input of the command it runs;
# open_driver_output opens each output on the descriptor number the driver reads
# it as, 3 for the post-chain record and 4 for the capture file, and records
# that number here. close_driver_handles closes whichever of the three are open
# and empties these three items again, so a later command inherits none of them
# and a command whose caller opened no input reads /dev/null.
RUN_INPUT_FD=""
DRIVER_POST_FD=""
DRIVER_CAPT_FD=""

# Verdict of the most recent source-guard run and the number of runs that
# passed.
GUARD_VERDICT=""
GUARD_PASSES=0

# Assertions this run made, counted per case and in total, and the amount
# deltas inside the tolerance it reported.
CASE_ASSERTIONS=0
TOTAL_ASSERTIONS=0
declare -a SUMMARY_DEVIATIONS=()

# Summary state: one entry per executed case, one per executed probe, one per
# published artifact and one per staged file awaiting publication, the latter
# as "<staged>|<name>".
declare -a SUMMARY_CASE_LINES=()
declare -a SUMMARY_PROBE_LINES=()
declare -a SUMMARY_ARTIFACTS=()
declare -a STAGED_ARTIFACTS=()

# Evidence publication state: the names removed and the files placed by the most
# recent publication, the SHA-256 published_digest read last, the first
# difference verify_published_set found, and the names it found beside a
# published set that this script does not publish.
EVIDENCE_CLEARED=0
EVIDENCE_PLACED=0
EVIDENCE_DIGEST=""
EVIDENCE_DIFFERENCE=""
declare -a EVIDENCE_FOREIGN=()
# How far the replacement of the published evidence set has come, read by the
# diagnostic of an interrupted run:
#   none        no published name has been touched by this run
#   clearing    the published names this script owns are being cleared
#   publishing  the clearing has passed every owned name and the staged files
#               are being published under their names, so this state with a
#               zero published count is a set that holds nothing at all
#   published   every name of the set carries the file this run staged for it,
#               read back against the manifest standing beside it
# with the number of names this run publishes, the number of owned published
# names the clearing has passed, and the number of names published so far. The
# counts are the two loops' own progress, so a diagnostic printed between them
# names the state on disk. The publication check works in a directory of its
# own and leaves these four values as it found them.
PUBLICATION_STATE="none"
PUBLICATION_NAMES_TOTAL=0
PUBLICATION_NAMES_CLEARED=0
PUBLICATION_NAMES_PUBLISHED=0

# The first termination, interrupt or hangup signal deferred while that
# replacement was in progress, empty when none was deferred, and the lines
# publication_state_report leaves for the diagnostic of an interrupted run.
DEFERRED_SIGNAL=""
declare -a PUBLICATION_MESSAGES=()

# Value read by the most recent capture_value call, and the capture key that
# carried it. Set instead of a subshell so a value holding a control byte is
# never re-parsed by the shell.
CAPTURE_VALUE=""
CAPTURE_KEY=""

# The row of the case being executed, as load_case_row read it out of the case
# table, and the values that follow from it: the generated record of the case,
# the request id the chain reads, the routing letter of that request id, the
# identity the case is seeded with in both its forms, whether the identity and
# timestamp reads run, the SQLCODE the chain ends on, and the size of the
# post-chain record the driver wrote.
CASE_LABEL=""
CASE_FIXTURE=""
CASE_CALEN=""
CASE_REQUEST_OVERRIDE=""
CASE_INJECT_POLICY=""
CASE_INJECT_SUBTYPE=""
CASE_INJECT_VSAM_RESP=""
CASE_INJECT_VSAM_RESP2=""
CASE_EXPECT_RC=""
CASE_EXPECT_ABEND=""
CASE_EXPECT_PRODUCT=""
CASE_EXPECT_POLICY_SQL=""
CASE_EXPECT_VSAM=""
CASE_EXPECT_VALUES=""
CASE_EXPECT_PRODUCT_VALUES=""
CASE_EXPECT_DIAG=""
CASE_SAMPLE=""
CASE_REQUEST_ID=""
CASE_TYPE_LETTER=""
CASE_POLICY_NUMBER=""
CASE_POLICY_PADDED=""
CASE_EXPECT_IDENTITY=""
CASE_EXPECT_SQLCODE=""
CASE_POST_SIZE=""

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
       run_harness.sh --case LABEL
       run_harness.sh --success-only
       run_harness.sh --help

Builds, compiles and executes the GnuCOBOL validation harness for the GenApp
Policy-Issue chain, asserts every row of the case table it runs against the
generated record of that row, and publishes the evidence of the run.

Arguments:
  CASE             A case label, "all" for every case, or "both" for the two
                   success cases, in either letter case. Default: all.
  --case LABEL     Run the single case LABEL.
  --success-only   Run the two success cases 01AMOT and 01ACOM.
  --help, -h       Print this block and exit 0.

Cases, in execution order:
  01AMOT         motor fixture, returns 00, writes the VSAM record
  01ACOM         commercial fixture, returns 00, writes the VSAM record
  01AMOT-RC70    policy insert reports SQLCODE -530, returns 70
  01AMOT-RC90    policy insert reports SQLCODE -911, returns 90
  01AMOT-LGSQ    motor insert reports SQLCODE -803, returns 90, abends LGSQ
  01ACOM-LGSQ    commercial insert reports -803, returns 90, abends LGSQ
  01AMOT-RC80    the VSAM write responds 12, returns 80
  01AMOT-RC98    COMMAREA length 20, returns 98
  01AMOT-LGCA    COMMAREA length 0, abends LGCA
  01AXXX-RC99    request id 01AXXX, returns 99
  01AHOU-ROUTE   house fixture, routes to the house insert, returns 00
  01AHOU-LGSQ    house fixture, house insert reports -803, abends LGSQ
The endowment route is not executed: no case selects it and every case asserts
the endowment capture group absent. See modernization/docs/decision-log.md, row: endowment route not
executed. It is still survivable under the mandated -fbinary-truncate, which
keeps the length subtraction of that route inside its PIC S9(4) COMP item: a
direct call of the translated LGAPDB01 on request id 01AEND at EIBCALEN=32500
returns 00 and writes the VSAM record under an "E" key.

Infrastructure probes, run after the compile stage of every run and reported on
their own. Each hands the driver one wrong environment item, or one wrong
handle, and asserts the status it reports and the side effect named beside it:
  PRB7           the module directory holds no module, status 7, and the
                 capture of the probe records no chain effect
  PRB5A          the case is not provided, status 5, and the probe directory
                 holds nothing but the driver log
  PRB5B          the case names a path above the run directory, status 5
  PRB5C          the fixture is empty, status 5
  PRB4           the capture descriptor of the driver is not open, status 4,
                 and nothing stands at the capture name

Environment items honoured:
  PY                     Python interpreter for the record builder and the
                         translator; a relative value resolves from the
                         repository root.
                         Default: modernization/.venv/bin/python
  COBC                   COBOL compiler command. Default: cobc
  COBC_EXTRA_FLAGS       Compiler options added after the mandated
                         -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy,
                         which every compile passes whatever this variable
                         holds. Accepted options: -debug -Wall -W -Wextra
                         -ftrace -ftraceall -fstack-check -v --verbose -O -O2
                         -Os. Any other option is a preflight failure; -g and
                         -save-temps, in either spelling, are refused by name,
                         and -fno-binary-truncate is refused. Each refusal
                         names the option and the action that clears it.
  COBC_FLAGS             Read under the same allow-list, with a mandated
                         option accepted as a no-op. It cannot replace one.
  HARNESS_POLICY_NUMBER  Identity seed of the first case, one to nine digits
                         above zero; each later case receives the next value.
                         Every run reserves one identity for each of the twelve
                         cases of the table, a run of one case included, so the
                         seed must also leave room for twelve consecutive values
                         at or below 999999999: 999999988 is the highest seed
                         any invocation accepts, and a higher one is a preflight
                         failure naming the value the table would reach.
                         Default: 1000001
  HARNESS_LASTCHANGED    Timestamp seed of every selected case, exactly 26
                         characters in YYYY-MM-DD-HH.MM.SS.NNNNNN form.
                         Default: 2026-08-19-12.00.00.000000
  HARNESS_STRICT_TOOL_VERSIONS
                         A true value (1, y, yes, t, true or on) makes a
                         compiler version other than the pinned 3.1.2.0 a
                         preflight failure instead of a reported deviation.
  HARNESS_LOCK_WAIT_SECONDS
                         Seconds this run waits for the exclusive harness lock
                         of the checkout, one to 3600. A wait that runs out
                         ends the run with exit 9. Default: 300

Environment items exported to the driver:
  COB_LIBRARY_PATH, COB_LS_FIXED, COB_PRE_LOAD,
  HARNESS_CASE, HARNESS_FIXTURE,
  HARNESS_POLICY_NUMBER, HARNESS_LASTCHANGED, HARNESS_COMMAREA_LENGTH,
  HARNESS_REQUEST_ID, HARNESS_INJECT_POLICY_SQLCODE,
  HARNESS_INJECT_SUBTYPE_SQLCODE, HARNESS_INJECT_VSAM_RESP,
  HARNESS_INJECT_VSAM_RESP2, HARNESS_EXPECT_RETURN_CODE,
  HARNESS_EXPECT_ABEND, HARNESS_EXPECT_PRODUCT, HARNESS_EXPECT_POLICY_SQL,
  HARNESS_EXPECT_VSAM, HARNESS_EXPECT_VALUES, HARNESS_EXPECT_PRODUCT_VALUES,
  HARNESS_EXPECT_DIAG_LINKS

Compiler environment items the preflight pins, for the compile stage and the
execution stage alike. An ambient value is removed before the compiler is asked
what its own installation carries, and the removal is reported as a deviation
naming the value that was ignored:
  COB_CONFIG_DIR         the configuration directory cobc --info reports as its
                         own. The dialect the mandated -std=ibm resolves inside
                         it is recorded at the head of compile.log: the files
                         of the ibm.conf include chain with the SHA-256 of
                         each, and the resolved binary-size, binary-truncate,
                         binary-byteorder, hostsign and defaultbyte
  COB_RUNTIME_CONFIG     removed, so a module loads the run-time configuration
                         of that installation
  COB_CFLAGS             the C options that installation reports, with the
                         _FORTIFY_SOURCE definition its host toolchain states
                         twice reduced to the one that takes effect. A COBOL
                         diagnostic is still written to compile.log and still
                         counted as a deviation

Each case and each probe runs the driver with three handles this script opens
and checks on the descriptor: the generated record of its fixture on standard
input, the post-chain record on descriptor 3 and the capture file on descriptor
4. The driver names none of those files itself, and all three are closed as soon
as it returns.

The driver measures the record it reads and refuses any width other than the
32,500 characters one generated record holds, reporting the width it found and
ending with its file status 4 before the chain is called. The width it read is
emitted as the SAMPLE_RECORD_LENGTH capture and every case asserts it, so a
capture file states the width its case ran on and a short record fails the run
rather than passing on the leading fields it still carries.

Generated output:
  modernization/harness/build/harness.lock    lock this run holds, no content
  modernization/harness/build/samples/commarea_<fixture>.dat
  modernization/harness/build/src/            translated programs, copybooks
  modernization/harness/build/bin/            fifteen modules and the driver
  modernization/harness/build/logs/           translate.log, compile.log,
                                              translation-report.json,
                                              source-baseline.sha256,
                                              readonly-check.log,
                                              evidence-manifest.sha256
  modernization/harness/build/run/<case>/     commarea_post.dat, captures.txt,
                                              driver.log
  modernization/harness/build/run/<probe>/    driver.log of each probe
  modernization/harness/build/probe/          directories the probes need
  modernization/harness/build/evidence/       staged evidence of this run and
                                              the publication check it runs
Published evidence, replaced as one set only after every selected case, every
probe and the final source guard passed. The set is the five stage files, the
manifest of the run, and the driver log, the capture file and the post-chain
record of each success case this run executed - twelve names for a run that
executed both success cases, nine for one and six for none. Every other name
this script owns there is removed, the manifest is removed first and placed
last, each name is replaced in one step, and the set is then read back against
the manifest published with it: a published set therefore carries the evidence
of one run, states in its manifest which run that is, and holds no artifact of a
success case that run did not execute:
  modernization/validation/artifacts/         translate.log, compile.log,
                                              translation-report.json,
                                              source-baseline.sha256,
                                              readonly-check.log,
                                              evidence-manifest.sha256, and the
                                              driver log, capture file and
                                              post-chain record of each success
                                              case that ran
The manifest names the run identifier, the moment it was written, the selection
the run was invoked with and the cases it executed on "#" comment lines, then
carries one sha256 line per published file, so "sha256sum -c
evidence-manifest.sha256" in that directory checks the published set.
runtime-versions.txt stands in that directory outside this replacement: it is
the environment record of the checkout and no run of this script writes it.

The manifest carries the run identifier, the time it was written, the case
selection, the success cases whose captures the set covers, the identity and
timestamp seeds, the measured cobc and python versions, the source-guard
verdict, the number of files in the set and the name standing outside it, all as
comment lines, then one "sha256sum" line per other file of the set. The comment
lines carry a leading "#", so "sha256sum --check evidence-manifest.sha256" run
in that directory checks the set as the manifest stands. Before it publishes,
every run repeats the replacement over a directory of its own under
modernization/harness/build/evidence/, holding the twelve names of a full-table
run and the environment record, with a set covering one success case: that check
requires the names of the other success case to be gone, requires the
environment record to be untouched, and requires the read-back to reject a set
carrying a planted artifact of the case the simulated run did not execute.

The evidence log of the source guard,
modernization/harness/build/logs/readonly-check.log, is emptied in the
preflight of a run, once the harness lock is held and before the first gate,
and then carries one block per gate of that run. It is emptied through its own
name rather than removed, so it is never absent while a run is in progress; a
run that ends before the preflight reaches it leaves it as it stands. Every
gate is run with the guard's --reproducible option, which records fixed text in
place of the time of the gate and of the root the block's paths are relative to,
so two runs of one selection over one unchanged tracked state leave the same
bytes in that log whatever directory the checkout was taken into. The gate
verdicts, the baseline table and the four gates themselves are recorded in
full. The log is collected after the final gate and published with the rest of
the evidence set, so the published copy carries all four gates of the run.

Exit codes:
  0 every stage passed
  1 usage error
  2 preflight failure
  3 sample generation failure or a record of the wrong size
  4 translation failure, a missing generated source or a baseline mismatch
  5 compilation failure or a missing module or driver
  6 execution failure, a probe that did not report its status or side effect,
    or a failed assertion
  7 evidence publication failure: a missing file to retain, a publication check
    that did not leave the set its manifest describes, or a published set that
    does not match the manifest published with it
  8 source guard failure
  9 the exclusive harness lock of this checkout was still held when the
    bounded wait ran out
143 a termination, interrupt or hangup signal reached this run: a command it was
    still waiting on was ended with its whole process group and reaped, and the
    harness lock of the checkout was released. The status reports what the run
    had published: nothing, the complete set when the signal arrived inside the
    replacement of it, which is deferred to the end of that replacement, or how
    far each of its two loops came

Characterisation notes, stated in full in the header of this script: LGAPOL01
reports DIAG_LINK_COUNT=0001 where the programs below it report 0002, because
the second diagnostic link of its error paragraph is unreachable by
construction; and WS-REQUIRED-CA-LEN accumulates across calls in one process,
so a host that calls these modules more than once per process has to CANCEL
them between calls. Both are the behaviour of the frozen source and neither
affects a run of this script, which gives each case its own process.

Installs nothing, reaches no network and never prompts.
USAGE_TEXT
}

# Prints the supplied value as one printable single-byte line: bytes 0x20 to
# 0x7E other than "\" are kept, and every other byte - carriage return, line
# feed, tab, any other control byte, DEL and any non-ASCII byte - plus "\"
# itself becomes "\xNN" with NN the upper-case hexadecimal byte value. Uses
# shell builtins only. Every line this script prints passes through it, so an
# argument, an environment item or a captured value occupies exactly one line
# and can carry no terminal control sequence. The same escaping is applied by
# modernization/validation/verify_readonly.sh.
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

# Prints one progress line for a stage.
emit_stage() {
  printf '%s: == stage %s of %s: %s ==\n' "$PROGRAM" "$(sanitize "$1")" \
    "$STAGE_COUNT" "$(sanitize "$2")"
}

# Prints one progress line for a step inside a stage.
emit_step() {
  printf '%s:   %s\n' "$PROGRAM" "$(sanitize "$1")"
}

# Prints one line that reports a measured value differing from a pinned one.
# The line names both values and the run continues.
emit_deviation() {
  printf '%s:   DEVIATION %s\n' "$PROGRAM" "$(sanitize "$1")"
  SUMMARY_DEVIATIONS+=("$1")
}

# Prints one line of the final summary block.
emit_summary() {
  printf '%s\n' "$(sanitize "$1")"
}

# Prints one diagnostic on standard error and ends the run with the supplied
# status. Every message names the offending value and the action that clears
# it.
die() {
  local status="$1"
  shift
  local line=""
  for line in "$@"; do
    printf '%s: error: %s\n' "$PROGRAM" "$(sanitize "$line")" >&2
  done
  exit "$status"
}

# Prints the usage block on standard error, preceded by one diagnostic, and
# ends the run as a usage error.
die_usage() {
  printf '%s: error: %s\n' "$PROGRAM" "$(sanitize "$1")" >&2
  usage >&2
  exit "$EXIT_USAGE"
}

# --------------------------------------------------------------------------
# Path resolution
# --------------------------------------------------------------------------
# Records the physical path of this script and the harness directory holding
# it, then the repository root two levels above that directory, and moves to
# that root. The result does not depend on the working directory of the caller.
# Every directory this run writes into is then formed from that physical root
# and a fixed repository-relative path, so no symbolic link on the way to this
# script can move an output root outside this checkout.
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

  if [[ "$HARNESS_DIR" != "${REPO_ROOT}/modernization/harness" ]]; then
    die "$EXIT_PREFLIGHT" \
      "this script resolves to ${SCRIPT_PATH}, outside ${REPO_ROOT}/modernization/harness" \
      "run the copy that stands in the harness directory of the checkout"
  fi

  BUILD_DIR="${REPO_ROOT}/${BUILD_DIR_RELATIVE}"
  # Every generated path of the run, the harness lock included, is formed from
  # this directory and accepted only when it lies below it, so it is checked
  # here, before any directory is created under it.
  if [[ "$BUILD_DIR" != *"/${BUILD_DIR_RELATIVE}" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the build directory of this run is ${BUILD_DIR}, which does not end in ${BUILD_DIR_RELATIVE}" \
      "run the copy that stands in the harness directory of the checkout"
  fi
  SRC_DIR="${BUILD_DIR}/src"
  BIN_DIR="${BUILD_DIR}/bin"
  SAMPLES_DIR="${BUILD_DIR}/samples"
  RUN_DIR="${BUILD_DIR}/run"
  LOGS_DIR="${BUILD_DIR}/logs"
  ARTIFACTS_DIR="${REPO_ROOT}/${ARTIFACTS_DIR_RELATIVE}"

  # One identifier per run, from the start time and the process number, names
  # the staging directory the evidence of this run is collected in.
  if ! RUN_ID="$(date -u '+%Y%m%dT%H%M%SZ')-$$" || [[ -z "$RUN_ID" ]]; then
    die "$EXIT_PREFLIGHT" "unable to read the current time for the run identifier"
  fi
  STAGING_DIR="${BUILD_DIR}/evidence/${RUN_ID}"

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
# Prints the row of the case table whose label matches the supplied one, and
# fails when the table carries no such label. The comparison is exact; the
# caller upper-cases a supplied label first.
case_row() {
  local label="$1" row=""

  for row in "${HARNESS_CASES[@]}"; do
    if [[ "${row%%|*}" == "$label" ]]; then
      printf '%s' "$row"
      return 0
    fi
  done
  return 1
}

# Fills SELECTED_CASES from the command line, and CASE_SELECTION with the one
# word that names the selection for the manifest and the summary. Accepts one
# selection: a case label of the table, "all" for every row, "both" or
# --success-only for the two success cases, or --case with a label. Any other
# value is a usage error.
parse_args() {
  local requested="all" upper=""

  if (($# > 2)); then
    die_usage "two arguments at most are accepted; received $#"
  fi
  if (($# == 2)); then
    case "$1" in
      --case)
        requested="$2"
        ;;
      *)
        die_usage "unrecognised argument: ${1}"
        ;;
    esac
  elif (($# == 1)); then
    case "$1" in
      --case)
        die_usage "--case requires a case label; pass one of: $(join_with ", " "${ALL_CASES[@]}")"
        ;;
      *)
        requested="$1"
        ;;
    esac
  fi

  case "$requested" in
    --help | -h)
      usage
      exit "$EXIT_OK"
      ;;
    --success-only)
      CASE_SELECTION="success-only"
      SELECTED_CASES=("${SUCCESS_CASES[@]}")
      return 0
      ;;
  esac

  upper="${requested^^}"
  case "$upper" in
    ALL)
      CASE_SELECTION="all"
      SELECTED_CASES=("${ALL_CASES[@]}")
      ;;
    BOTH)
      CASE_SELECTION="both"
      SELECTED_CASES=("${SUCCESS_CASES[@]}")
      ;;
    *)
      if ! case_row "$upper" >/dev/null; then
        die_usage \
          "unrecognised argument: ${requested}; accepted values are all, both, --success-only or one of: $(join_with ", " "${ALL_CASES[@]}")"
      fi
      CASE_SELECTION="$upper"
      SELECTED_CASES=("$upper")
      ;;
  esac
}

# Prints the fixture the record of the supplied fixture is written from, and
# prints nothing when that fixture is built from a sample definition of its own.
fixture_base() {
  local fixture="$1" entry=""

  for entry in "${DERIVED_FIXTURES[@]}"; do
    if [[ "${entry%%|*}" == "$fixture" ]]; then
      printf '%s' "${entry##*|}"
      return 0
    fi
  done
  return 0
}

# Fills SELECTED_FIXTURES with the fixtures the run needs, each once, in the
# order the fixture list declares them: the fixture of every selected case, the
# fixture every derived one of those is written from, and the fixture the
# probes run on. Only those fixtures are generated.
resolve_selected_fixtures() {
  local fixture="" label="" row="" wanted="" base="" entry=""
  local -A needed=()

  SELECTED_FIXTURES=()
  for label in "${SELECTED_CASES[@]}"; do
    row="$(case_row "$label")"
    wanted="${row#*|}"
    wanted="${wanted%%|*}"
    needed["$wanted"]=1
  done
  needed["$PROBE_FIXTURE"]=1
  for entry in "${DERIVED_FIXTURES[@]}"; do
    fixture="${entry%%|*}"
    if [[ -n "${needed[$fixture]:-}" ]]; then
      needed["${entry##*|}"]=1
    fi
  done

  for fixture in "${HARNESS_FIXTURES[@]}"; do
    if [[ -z "${needed[$fixture]:-}" ]]; then
      continue
    fi
    base="$(fixture_base "$fixture")"
    if [[ -n "$base" && -z "${needed[$base]:-}" ]]; then
      die "$EXIT_PREFLIGHT" \
        "fixture ${fixture} is written from ${base}, which this run does not generate"
    fi
    SELECTED_FIXTURES+=("$fixture")
  done
  if ((${#SELECTED_FIXTURES[@]} == 0)); then
    die "$EXIT_PREFLIGHT" \
      "the selected cases name no fixture; the case table names ${#HARNESS_CASES[@]} rows"
  fi
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

# Prints the identity seed of a case: the base value for the first row of the
# case table and the next value for each row after it, whichever rows the
# command line selected. Two cases therefore never share an identity, and the
# seed of a case does not move when another case is left out of the run.
policy_number_for() {
  local label="$1" index=0

  for index in "${!HARNESS_CASES[@]}"; do
    if [[ "${HARNESS_CASES[index]%%|*}" == "$label" ]]; then
      printf '%s' "$((POLICY_NUMBER_BASE + index))"
      return 0
    fi
  done
  die "$EXIT_PREFLIGHT" "no identity seed is defined for case ${label}"
}

# Prints the ten-digit form of an identity seed, the width CA-POLICY-NUM
# [base/src/lgcmarea.cpy:35] holds it in.
policy_number_padded() {
  printf '%010d' "$1"
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

# Prints the supplied path with the repository root of this run removed, and
# prints any other value unchanged; the paths it prints resolve from the
# repository root, the working directory of every stage of this script. A root
# that is not resolved yet strips nothing, so no value can lose its leading
# separator before the preflight has resolved the checkout.
# See modernization/docs/decision-log.md, row: evidence paths recorded relative
# to the repository root.
repo_relative() {
  local value="$1"

  if [[ -n "$REPO_ROOT" && "$value" == "${REPO_ROOT}/"* ]]; then
    printf '%s' "${value#"${REPO_ROOT}/"}"
    return 0
  fi
  printf '%s' "$value"
}

# Appends one command line to the named log, with every argument that names a
# path inside this checkout written relative to the repository root. Each
# compiler diagnostic in the log then follows the command line of the module it
# belongs to, and the recorded line is the command as it reads from any
# checkout; the command itself runs on the absolute paths the caller assembled.
log_command() {
  local log="$1"
  shift
  local argument="" line=""
  local -a logged=()

  for argument in "$@"; do
    logged+=("$(repo_relative "$argument")")
  done
  line="$(join_with " " "${logged[@]}")"
  if ! printf '+ %s\n' "$line" >>"$log"; then
    die "$EXIT_COMPILE" "unable to append to the log: ${log}"
  fi
}

# Appends one line to the named log, escaped to one printable control-free line
# by the same rule every line this script prints follows. A value read from the
# environment of the caller, from the report of the compiler or from a
# configuration file therefore occupies exactly one line of the log and can
# neither end that line early nor forge a further record.
log_line() {
  local log="$1" text="$2"

  if ! printf '%s\n' "$(sanitize "$text")" >>"$log"; then
    die "$EXIT_COMPILE" "unable to append to the log: ${log}"
  fi
}

# Prints the parent identifier, the process group and the start time /proc
# reports for the supplied identifier, as "<ppid>|<pgid>|<start>", and fails
# when that identifier names no process or the status line cannot be read. The
# line is read with shell builtins alone. The name of the process, the one field
# that may itself carry a space or a bracket, is dropped with its brackets
# first, so every field after it is positional: the fields that remain are
# state, parent identifier, process group, session and onward, and the start
# time is the twentieth of them.
read_process_identity() {
  local pid="$1" line="" rest=""
  local -a fields=()

  if [[ ! "$pid" =~ ^[0-9]+$ ]]; then
    return 1
  fi
  if ! IFS= read -r line 2>/dev/null <"/proc/${pid}/stat" || [[ -z "$line" ]]; then
    return 1
  fi
  rest="${line##*')'}"
  if [[ "$rest" == "$line" ]]; then
    return 1
  fi
  IFS=' ' read -r -a fields <<<"$rest"
  if ((${#fields[@]} < 20)); then
    return 1
  fi
  printf '%s|%s|%s' "${fields[1]}" "${fields[2]}" "${fields[19]}"
}

# Prints the start time /proc reports for a process this script has just
# started, and fails when that identifier names no process or names one this
# shell did not start. Called immediately after the spawn, while the process is
# still unreaped and its identifier can therefore not have been given to another
# process, so the identifier and the start time recorded together here identify
# that one process for the rest of the step.
own_child_start_time() {
  local pid="$1"
  local identity="" ppid="" start=""

  if ! identity="$(read_process_identity "$pid")"; then
    return 1
  fi
  IFS='|' read -r ppid _ start <<<"$identity"
  if [[ "$ppid" != "$$" || ! "$start" =~ ^[0-9]+$ ]]; then
    return 1
  fi
  printf '%s' "$start"
}

# Succeeds when the supplied identifier still names a process this script
# started and has not reaped: /proc reports this shell as its parent and reports
# the start time recorded at the spawn. A third argument of "Y" also requires
# that process to lead its own process group, which is what a group signal is
# sent to. An identifier this run has reaped fails the test - its /proc entry is
# gone, or it names a process another parent started at another time - so
# nothing is signalled on the strength of a recorded identifier alone. An
# identifier this run has signalled but not yet reaped still passes: the process
# it names is held by this script until it is waited for, and its identifier
# cannot be reused before then.
#
# An empty start time is the state between the spawn of a process and the record
# of its start time, and run_and_tee empties the identifier before the start
# time when a process is reaped, so an identifier carrying no start time is one
# of a process this run has spawned and not waited for. The parent /proc reports,
# with the group leadership when it is required, decides that state; an
# identifier carrying a start time is decided on the start time as well.
process_is_own_child() {
  local pid="$1" start="$2" require_group_leader="$3"
  local identity="" ppid="" pgid="" observed=""

  if [[ ! "$pid" =~ ^[0-9]+$ ]] || ((pid <= 1)) || ((pid == $$)); then
    return 1
  fi
  if [[ -n "$start" && ! "$start" =~ ^[0-9]+$ ]]; then
    return 1
  fi
  if ! identity="$(read_process_identity "$pid")"; then
    return 1
  fi
  IFS='|' read -r ppid pgid observed <<<"$identity"
  if [[ "$ppid" != "$$" ]]; then
    return 1
  fi
  if [[ -n "$start" && "$observed" != "$start" ]]; then
    return 1
  fi
  if [[ "$require_group_leader" == "Y" && "$pgid" != "$pid" ]]; then
    return 1
  fi
  return 0
}

# Leaves in PUBLICATION_MESSAGES, one line per message, what the replacement of
# the published evidence set had reached when an interrupted run ended. State
# "none" is a run that ended before stage 6 touched a published name: its own
# evidence stands in the staging directory and every published name is the one
# the run before it left. State "published" is a run that ended after every name
# of the set had been replaced and re-read. Any state between the two - and any
# other value - is reported as a set that holds names of this run beside names
# of the run before it, with how far each of the two loops came, and with the
# command that replaces the whole set.
publication_state_report() {
  PUBLICATION_MESSAGES=()

  if [[ "$PUBLICATION_STATE" == "none" ]]; then
    PUBLICATION_MESSAGES+=(
      "nothing of this run was published; the harness lock of this checkout is released"
    )
    return 0
  fi
  if [[ "$PUBLICATION_STATE" == "published" ]]; then
    PUBLICATION_MESSAGES+=(
      "the complete evidence set of this run was published, ${PUBLICATION_NAMES_PUBLISHED} of ${PUBLICATION_NAMES_TOTAL} names in ${ARTIFACTS_DIR}"
      "the harness lock of this checkout is released"
    )
    return 0
  fi
  PUBLICATION_MESSAGES+=(
    "the published evidence set may be incomplete: of the ${PUBLICATION_NAMES_TOTAL} names this run publishes, ${PUBLICATION_NAMES_PUBLISHED} were published, and the clearing that runs first passed ${PUBLICATION_NAMES_CLEARED} published names of an earlier run, so ${ARTIFACTS_DIR} holds names of this run beside names of the run before it"
    "run this script again on the same cases to replace the whole set; the evidence this run staged stands in ${STAGING_DIR}"
    "the harness lock of this checkout is released"
  )
}

# Ends the run on a termination, interrupt or hangup signal. The command
# run_and_tee is waiting on, and the children that command started of its own,
# stand in one process group of their own. When the leader of that group is
# still a process this run started and has not reaped, the whole group is ended
# here: SIGTERM first, then SIGKILL for whatever still stands after
# TERMINATE_GRACE_SECONDS, with the identity checked again before that second
# signal. The group and the "tee" recording its output are both reaped before
# this returns. An identifier whose process this run has already reaped is
# reported as ended and is not signalled, so no signal of this handler can reach
# a process that received such an identifier afterwards. No sample, module, log
# or published name is written after this point, so an interrupted run publishes
# nothing, and the exclusive harness lock of the checkout is released by the exit
# that follows: the descriptor this script holds it through closes with the
# process, and the descriptor its children inherited closes with them. Ends the
# run with EXIT_SIGNAL whichever of the three signals arrived.
# The handler is removed before the group is ended, so a second signal reaching
# this script while the group is being ended takes its default action.
terminate_run() {
  local signal="$1"
  local pgid="$RUN_CHILD_PGID" child_start="$RUN_CHILD_START"
  local log_pid="$RUN_LOG_PID" log_start="$RUN_LOG_START"
  local name="$RUN_CHILD_NAME"
  local -a messages=()

  trap - TERM INT HUP
  RUN_CHILD_PGID=""
  RUN_CHILD_START=""
  RUN_LOG_PID=""
  RUN_LOG_START=""
  RUN_CHILD_NAME=""

  if [[ -z "$pgid" ]]; then
    messages+=("no external command was running")
  elif process_is_own_child "$pgid" "$child_start" "Y"; then
    kill -TERM "-${pgid}" 2>/dev/null || true
    sleep "$TERMINATE_GRACE_SECONDS" 2>/dev/null || true
    if process_is_own_child "$pgid" "$child_start" "Y"; then
      kill -KILL "-${pgid}" 2>/dev/null || true
    fi
    wait "$pgid" 2>/dev/null || true
    messages+=("the command it was waiting on, ${name}, was ended with its process group ${pgid} and reaped")
  else
    messages+=("the command it was waiting on, ${name}, had already ended; process group ${pgid} was not signalled")
  fi
  if [[ -n "$log_pid" ]]; then
    if process_is_own_child "$log_pid" "$log_start" "N"; then
      kill -TERM "$log_pid" 2>/dev/null || true
      wait "$log_pid" 2>/dev/null || true
      messages+=("the log of that command, written by process ${log_pid}, was ended with it and is left as it stands")
    else
      messages+=("the process that wrote the log of that command, ${log_pid}, had already ended; it was not signalled")
    fi
  fi
  publication_state_report
  messages+=("${PUBLICATION_MESSAGES[@]}")
  die "$EXIT_SIGNAL" "run ended by SIG${signal}" "${messages[@]}"
}

# Installs the handler that ends a run reached by a termination, interrupt or
# hangup signal. Runs as the first step of the run, so a signal that arrives
# before the first stage is handled the same way as one that arrives while a
# compile is in progress, and runs again as soon as the replacement of the
# published evidence set is over, which defer_signal_traps holds those three
# signals for.
install_signal_traps() {
  trap 'terminate_run TERM' TERM
  trap 'terminate_run INT' INT
  trap 'terminate_run HUP' HUP
}

# Records the first termination, interrupt or hangup signal that reaches this
# script while the published evidence set is being replaced.
# Bash runs a trap between two commands, so a signal that arrives inside the
# "rm", the "cat" or the "mv" of that replacement is handled once that command
# has returned, and the loop that command belongs to then continues to its end:
# the set is replaced in full and resume_deferred_signal ends the run
# afterwards. Returns 0: a handler that returns non-zero ends a run under
# "set -e" at the command the signal interrupted, and a handler that fails
# inside a pipeline ends it under "set -o pipefail". The first signal is the one
# recorded and the one reported; a second one of the three is held the same way
# and adds nothing.
# See planned decision-log row: the three signals deferred for the replacement
# of the published evidence set.
defer_signal() {
  local signal="$1"

  if [[ -z "$DEFERRED_SIGNAL" ]]; then
    DEFERRED_SIGNAL="$signal"
  fi
  return 0
}

# Installs the handler that defers the three signals in place of the one that
# ends the run on them. Held for the replacement of the published evidence set
# alone - clearing the names of this run, publishing the staged files under them
# and re-reading every published file against the manifest - so an interrupted
# run leaves that set complete rather than half replaced. The deferral covers
# the signals delivered to this script. A signal delivered to the whole process
# group also reaches the command the step running at the time started: a step
# that reads the status of an "rm", a "cat" or a "mv" then reports the name it
# could not write and ends the run with the evidence status, and a step that
# reads a digest through a command substitution ends the run with the status of
# the signal. Both leave the set replaced as far as that step came.
defer_signal_traps() {
  trap 'defer_signal TERM' TERM
  trap 'defer_signal INT' INT
  trap 'defer_signal HUP' HUP
}

# Ends the run through terminate_run when a signal was deferred while the
# published evidence set was being replaced, and returns 0 when none was. Runs
# once the terminating handlers are installed again, so a signal that arrives
# between the end of that replacement and their reinstallation is deferred and
# reported here rather than lost. The run ends with EXIT_SIGNAL, and the
# published evidence set terminate_run reports is the complete set of this run.
resume_deferred_signal() {
  local signal="$DEFERRED_SIGNAL"

  if [[ -z "$signal" ]]; then
    return 0
  fi
  DEFERRED_SIGNAL=""
  terminate_run "$signal"
}

# Runs the supplied command with its output merged and appended to the log named
# by the second argument. Its standard input is a duplicate of the descriptor
# open_driver_input opened, when the caller opened one, and /dev/null when the
# caller opened none; the descriptor itself is closed for the command, so the
# command receives the record and no handle on the record this script keeps.
# Descriptors 3 and 4, opened by open_driver_output, are inherited as they
# stand: a caller that opened neither runs a command that has neither, which is
# what the probe of the missing capture handle relies on. The status of the
# command is reported in RUN_STATUS and the status of the "tee" that wrote the
# log in RUN_LOG_STATUS. A "tee" that could not write ends the run with the
# status the first argument names, leaving the log of that command incomplete;
# the caller reads RUN_STATUS to decide what a non-zero command status means.
#
# The command and the "tee" recording it each run as a background process of
# their own, connected by a pipe, and this script waits on each of the two in
# turn for its status. The command, and every child it starts of its own, stand
# in one process group under job control. A termination, interrupt or hangup
# signal that arrives while one of those waits is in progress ends that wait at
# once, and terminate_run then ends that process group, ends the "tee" and reaps
# both. The command reads the same standard input, holds no handle of this
# script's own, inherits the same descriptors 3 and 4, and reports the same
# status as it does in a foreground pipeline.
#
# Each of the two is recorded for the handler as its identifier and the start
# time /proc reports for it, the identifier at the spawn and the start time
# next, and each pair is emptied as that process is reaped, the identifier again
# first. An identifier the handler finds carrying no start time is therefore an
# identifier of a process spawned and not yet waited for, the state in which the
# parent /proc reports identifies it on its own. An identifier whose identity
# this script cannot read is a host without a readable /proc: the process is
# ended here and the step fails.
run_and_tee() {
  local log_failure_status="$1" log="$2"
  shift 2
  local command_status=0 log_status=0 record_fd="" spawned="" start=""

  RUN_STATUS=0
  RUN_LOG_STATUS=0
  RUN_CHILD_NAME="$1"
  set +e
  # The "tee" of this step is started first, reading the merged output of the
  # command through a pipe this script holds the write end of on record_fd and
  # writing it to the log and to the standard output of this script.
  exec {record_fd}> >(tee -a "$log")
  RUN_LOG_PID="$!"
  if [[ ! "$record_fd" =~ ^[0-9]+$ ]] || [[ ! "$RUN_LOG_PID" =~ ^[0-9]+$ ]]; then
    set -e
    RUN_LOG_PID=""
    RUN_CHILD_NAME=""
    die "$log_failure_status" \
      "the process that records this step could not be started for the log: ${log}" \
      "grant write permission on that path, or free space on its file system, and run this script again"
  fi
  if ! start="$(own_child_start_time "$RUN_LOG_PID")"; then
    spawned="$RUN_LOG_PID"
    kill -TERM "$spawned" 2>/dev/null || true
    wait "$spawned" 2>/dev/null || true
    RUN_LOG_PID=""
    exec {record_fd}>&-
    set -e
    RUN_CHILD_NAME=""
    die "$log_failure_status" \
      "the identity of the process that records this step, ${spawned}, could not be read from /proc" \
      "run this script on a host that mounts /proc for the user it runs as"
  fi
  RUN_LOG_START="$start"
  # Job control gives the command, and every child it starts of its own, one
  # process group whose identifier is the identifier of the command itself.
  set -m
  if [[ -n "$RUN_INPUT_FD" ]]; then
    "$@" <&"$RUN_INPUT_FD" {RUN_INPUT_FD}<&- \
      >&"$record_fd" 2>&1 {record_fd}>&- &
  else
    "$@" </dev/null >&"$record_fd" 2>&1 {record_fd}>&- &
  fi
  RUN_CHILD_PGID="$!"
  set +m
  if ! start="$(own_child_start_time "$RUN_CHILD_PGID")"; then
    spawned="$RUN_CHILD_PGID"
    kill -TERM "-${spawned}" 2>/dev/null || true
    wait "$spawned" 2>/dev/null || true
    RUN_CHILD_PGID=""
    exec {record_fd}>&-
    kill -TERM "$RUN_LOG_PID" 2>/dev/null || true
    wait "$RUN_LOG_PID" 2>/dev/null || true
    RUN_LOG_PID=""
    RUN_LOG_START=""
    set -e
    RUN_CHILD_NAME=""
    die "$log_failure_status" \
      "the identity of the command of this step, ${spawned}, could not be read from /proc" \
      "run this script on a host that mounts /proc for the user it runs as"
  fi
  RUN_CHILD_START="$start"
  # Closed here, so the "tee" reads the end of its input as soon as the command
  # and its children have released the write end.
  exec {record_fd}>&-
  wait "$RUN_CHILD_PGID"
  command_status=$?
  RUN_CHILD_PGID=""
  RUN_CHILD_START=""
  wait "$RUN_LOG_PID"
  log_status=$?
  RUN_LOG_PID=""
  RUN_LOG_START=""
  set -e
  RUN_CHILD_NAME=""
  RUN_STATUS="$command_status"
  RUN_LOG_STATUS="$log_status"
  if ((RUN_LOG_STATUS != 0)); then
    die "$log_failure_status" \
      "the log of this step could not be written: ${log}" \
      "\"tee\" exited ${RUN_LOG_STATUS} while the command it recorded exited ${RUN_STATUS}" \
      "grant write permission on that path, or free space on its file system, and run this script again"
  fi
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
# Path handling
# --------------------------------------------------------------------------
# One rule governs every path this script writes: the path lies inside the
# build directory or the validation artifacts directory of this checkout, no
# component on the way to it is a symbolic link, and the entry itself is either
# absent or a regular file carrying exactly one hard link. A path that breaks
# the rule is refused before anything is created, truncated, compiled into,
# appended to or copied. The same rule governs the record handed to the driver
# on its standard input, which is refused before the driver is started.
# Decisions taken about this rule are recorded in
# modernization/docs/decision-log.md.

# Prints the name of the file type a path holds, without following a symbolic
# link, in the vocabulary the diagnostics of this script use.
path_kind() {
  local path="$1"

  if [[ -L "$path" ]]; then
    printf '%s' "a symbolic link"
  elif [[ ! -e "$path" ]]; then
    printf '%s' "absent"
  elif [[ -d "$path" ]]; then
    printf '%s' "a directory"
  elif [[ -p "$path" ]]; then
    printf '%s' "a fifo"
  elif [[ -S "$path" ]]; then
    printf '%s' "a socket"
  elif [[ -b "$path" ]]; then
    printf '%s' "a block special file"
  elif [[ -c "$path" ]]; then
    printf '%s' "a character special file"
  elif [[ -f "$path" ]]; then
    printf '%s' "a regular file"
  else
    printf '%s' "of an unknown type"
  fi
}

# Succeeds when the supplied absolute path lies inside one of the two roots
# this script writes into. The comparison is textual and both roots are
# physical paths, so it holds for every path built from them.
path_is_anchored() {
  local path="$1"

  case "$path" in
    "${BUILD_DIR}"/*) return 0 ;;
    "${ARTIFACTS_DIR}"/*) return 0 ;;
    *) return 1 ;;
  esac
}

# Ends the run when any component of the supplied absolute path, from the
# repository root down to and including the entry itself, is a symbolic link.
# The walk reads each component with shell builtins alone.
assert_no_symlink_components() {
  local path="$1" status="$2"
  local remainder="" walked="$REPO_ROOT" component=""

  if [[ "$path" != "${REPO_ROOT}/"* ]]; then
    die "$status" \
      "path outside the repository root: ${path}" \
      "the repository root of this run is ${REPO_ROOT}"
  fi
  remainder="${path#"${REPO_ROOT}/"}"
  while [[ -n "$remainder" ]]; do
    component="${remainder%%/*}"
    if [[ "$component" == "$remainder" ]]; then
      remainder=""
    else
      remainder="${remainder#*/}"
    fi
    if [[ -z "$component" || "$component" == "." || "$component" == ".." ]]; then
      die "$status" \
        "path carries a component this script does not accept: ${path}"
    fi
    walked="${walked}/${component}"
    if [[ -L "$walked" ]]; then
      die "$status" \
        "path component is a symbolic link: ${walked}" \
        "remove that link so ${path} names a file inside this checkout, then run this script again"
    fi
  done
}

# Ends the run unless the supplied absolute path is one this script may write:
# anchored under a build or artifacts root, reached without a symbolic link,
# and either absent or a single-link regular file. Called before every create,
# truncate, compile output, log append and copy destination.
assert_writable_path() {
  local path="$1" status="$2"
  local links=""

  if ! path_is_anchored "$path"; then
    die "$status" \
      "output path outside the directories this script writes: ${path}" \
      "generated output belongs under ${BUILD_DIR} and published evidence under ${ARTIFACTS_DIR}"
  fi
  assert_no_symlink_components "$path" "$status"
  if [[ -e "$path" && ! -f "$path" ]]; then
    die "$status" \
      "output path exists as $(path_kind "$path"): ${path}" \
      "remove that entry so this script can write a regular file there"
  fi
  if [[ -f "$path" ]]; then
    if ! links="$(stat -c '%h' -- "$path" 2>/dev/null)"; then
      die "$status" "unable to read the link count of: ${path}"
    fi
    if [[ ! "$links" =~ ^[0-9]+$ ]] || ((10#$links != 1)); then
      die "$status" \
        "output path carries ${links} hard links: ${path}" \
        "a file this script writes carries one name; remove the other links and run this script again"
    fi
  fi
}

# Ends the run unless the supplied absolute path is one this script may read as
# the source of a copy: reached without a symbolic link and a single-link
# regular file that this run produced.
assert_readable_path() {
  local path="$1" status="$2"
  local links=""

  assert_no_symlink_components "$path" "$status"
  if [[ ! -f "$path" ]]; then
    die "$status" \
      "the file to read is $(path_kind "$path"): ${path}" \
      "review the stage logs under ${LOGS_DIR} for the step that did not complete"
  fi
  if ! links="$(stat -c '%h' -- "$path" 2>/dev/null)"; then
    die "$status" "unable to read the link count of: ${path}"
  fi
  if [[ ! "$links" =~ ^[0-9]+$ ]] || ((10#$links != 1)); then
    die "$status" \
      "the file to read carries ${links} hard links: ${path}" \
      "a file this run produced carries one name; remove the other links and run this script again"
  fi
}

# Ends the run unless the descriptor named by the second argument holds the file
# the first argument names: a regular file carrying one hard link, the same
# inode on the same device as that name, and - when a fourth argument is given -
# exactly that many bytes. The status of the descriptor is read through
# /dev/fd/<n>, so what is checked is the open file itself rather than the name
# it was opened from: an entry that replaces the name after the open is visible
# here as a different inode, and one that replaces it after this check reaches
# nothing, because the descriptor stays open until the driver has returned.
assert_open_descriptor() {
  local path="$1" fd="$2" status="$3" expected_size="${4:-}"
  local name_status="" fd_status=""
  local name_type="" name_inode="" name_device=""
  local fd_type="" fd_links="" fd_inode="" fd_device="" fd_size=""

  if ! name_status="$(stat -c '%F|%h|%i|%d' -- "$path" 2>/dev/null)"; then
    die "$status" "unable to read the status of the file handed to the driver: ${path}"
  fi
  # The link count of the name was read by the path rule before the open; the
  # count that decides here is the one the opened file itself reports.
  IFS='|' read -r name_type _ name_inode name_device <<<"$name_status"
  if ! fd_status="$(stat -L -c '%F|%h|%i|%d|%s' -- "/dev/fd/${fd}" 2>/dev/null)"; then
    die "$status" \
      "unable to read the status of descriptor ${fd}, opened on: ${path}"
  fi
  IFS='|' read -r fd_type fd_links fd_inode fd_device fd_size <<<"$fd_status"
  case "$fd_type" in
    "regular file" | "regular empty file") ;;
    *)
      die "$status" \
        "descriptor ${fd} is open on ${fd_type} where a regular file is required: ${path}" \
        "remove the entry that stands at that name and run this script again"
      ;;
  esac
  if [[ "$fd_links" != "1" ]]; then
    die "$status" \
      "descriptor ${fd} is open on a file carrying ${fd_links} hard links: ${path}" \
      "a file this script hands the driver carries one name; remove the other links and run this script again"
  fi
  if [[ "$fd_inode" != "$name_inode" || "$fd_device" != "$name_device" ]]; then
    die "$status" \
      "descriptor ${fd} is open on ${fd_device}:${fd_inode}, which is no longer the file at ${path} (${name_device}:${name_inode})" \
      "an entry replaced that name between the check and the open; run this script again"
  fi
  if [[ "$name_type" != "$fd_type" ]]; then
    die "$status" \
      "the name ${path} reports ${name_type} where descriptor ${fd} is open on ${fd_type}"
  fi
  if [[ -n "$expected_size" && "$fd_size" != "$expected_size" ]]; then
    die "$status" \
      "descriptor ${fd} is open on a file of ${fd_size} bytes where ${expected_size} are required: ${path}" \
      "the generated records of a run hold ${RECORD_BYTES} bytes; run this script again to regenerate them"
  fi
}

# Opens the record the next driver run reads on its standard input and keeps it
# open until close_driver_handles closes it again. The path goes through the read
# rule first - anchored under a root this script writes, reached without a
# symbolic link, a single-link regular file and open to be read - then the file
# is opened read-only on a descriptor of its own, and the descriptor is checked
# against that name and against the size one generated record holds. The driver
# receives a duplicate of that descriptor and no name, so the record it reads is
# the file this check accepted, whatever appears at the name afterwards. A path
# the rule refuses, and a descriptor whose file differs from the name, end the
# run here, before the driver is started.
open_driver_input() {
  local path="$1" status="$2"
  local fd=""

  if ! path_is_anchored "$path"; then
    die "$status" \
      "the record to hand the driver lies outside the directories this script writes: ${path}" \
      "the generated records of a run stand under ${BUILD_DIR}"
  fi
  assert_readable_path "$path" "$status"
  if [[ ! -r "$path" ]]; then
    die "$status" \
      "the record to hand the driver cannot be read: ${path}" \
      "grant read permission on that record and run this script again"
  fi
  if ! { exec {fd}<"$path"; } 2>/dev/null; then
    die "$status" \
      "unable to open the record to hand the driver: ${path}" \
      "grant read permission on that record and run this script again"
  fi
  RUN_INPUT_FD="$fd"
  assert_open_descriptor "$path" "$fd" "$status" "$RECORD_BYTES"
}

# Opens one of the two files the next driver run writes and keeps it open until
# close_driver_handles closes it again. The slot names which of them it is and
# fixes the descriptor number the driver reads it as: "post" is descriptor 3 and
# "capture" is descriptor 4. The earlier entry at the name is removed through the
# path rule, then the file is created and opened with the shell's noclobber
# setting in force, which refuses an existing file, a symbolic link to an
# existing file and a dangling symbolic link alike rather than writing through
# it, and the descriptor is checked against the name it was created at. The
# setting is turned off again on both paths out, so it applies to this creation
# alone.
open_driver_output() {
  local slot="$1" path="$2" status="$3"
  local fd="" opened="N"

  remove_output_path "$path" "$status"
  case "$slot" in
    post)
      fd=3
      set -C
      if { exec 3>"$path"; } 2>/dev/null; then
        opened="Y"
      fi
      set +C
      ;;
    capture)
      fd=4
      set -C
      if { exec 4>"$path"; } 2>/dev/null; then
        opened="Y"
      fi
      set +C
      ;;
    *)
      die "$status" \
        "the driver has no output handle named ${slot}; \"post\" and \"capture\" are the two it runs with"
      ;;
  esac
  if [[ "$opened" != "Y" ]]; then
    die "$status" \
      "unable to create the file the driver writes on descriptor ${fd}: ${path}" \
      "an entry appeared at that name while this run was creating it, or its directory is not writable" \
      "remove that entry and run this script again"
  fi
  if [[ "$slot" == "post" ]]; then
    DRIVER_POST_FD="$fd"
  else
    DRIVER_CAPT_FD="$fd"
  fi
  assert_open_descriptor "$path" "$fd" "$status" 0
}

# Closes whichever of the three driver handles are open and records that none is
# open any more. Called as soon as the driver of a case or a probe has returned,
# so the two files it wrote are complete before this script reads them and no
# later command of the run inherits a handle on them.
close_driver_handles() {
  if [[ -n "$RUN_INPUT_FD" ]]; then
    exec {RUN_INPUT_FD}<&-
    RUN_INPUT_FD=""
  fi
  if [[ -n "$DRIVER_POST_FD" ]]; then
    exec 3>&-
    DRIVER_POST_FD=""
  fi
  if [[ -n "$DRIVER_CAPT_FD" ]]; then
    exec 4>&-
    DRIVER_CAPT_FD=""
  fi
}

# Removes an entry this script is about to write, after the path rule has
# accepted it. The removal takes the name itself and never follows a link.
remove_output_path() {
  local path="$1" status="$2"

  assert_writable_path "$path" "$status"
  if ! rm -f -- "$path"; then
    die "$status" "unable to remove the earlier output at: ${path}"
  fi
}

# Creates an empty file at the supplied path and leaves it owned by this run.
# The path rule accepts it, the earlier entry is removed by name, and the
# creation itself refuses to open an existing entry, so a name that appears
# between the two ends the run instead of being written through.
create_private_file() {
  local path="$1" status="$2"

  remove_output_path "$path" "$status"
  set -C
  if ! : >"$path"; then
    set +C
    die "$status" \
      "unable to create the file: ${path}" \
      "an entry appeared at that name while this run was creating it, or its directory is not writable"
  fi
  set +C
}

# Creates one directory below the repository root, one component at a time,
# refusing a component that is a symbolic link and confirming that the result
# is the directory the caller named. Nothing outside the two write roots is
# created.
ensure_directory() {
  local path="$1" status="$2"
  local remainder="" walked="$REPO_ROOT" component="" resolved=""

  if [[ "$path" != "$BUILD_DIR" && "$path" != "$ARTIFACTS_DIR" ]] &&
    ! path_is_anchored "$path"; then
    die "$status" \
      "directory outside the directories this script writes: ${path}" \
      "generated output belongs under ${BUILD_DIR} and published evidence under ${ARTIFACTS_DIR}"
  fi
  if [[ "$path" != "${REPO_ROOT}/"* ]]; then
    die "$status" "directory outside the repository root: ${path}"
  fi
  remainder="${path#"${REPO_ROOT}/"}"
  while [[ -n "$remainder" ]]; do
    component="${remainder%%/*}"
    if [[ "$component" == "$remainder" ]]; then
      remainder=""
    else
      remainder="${remainder#*/}"
    fi
    if [[ -z "$component" || "$component" == "." || "$component" == ".." ]]; then
      die "$status" "directory carries a component this script does not accept: ${path}"
    fi
    walked="${walked}/${component}"
    if [[ -L "$walked" ]]; then
      die "$status" \
        "directory component is a symbolic link: ${walked}" \
        "remove that link and run this script again"
    fi
    if [[ -e "$walked" && ! -d "$walked" ]]; then
      die "$status" \
        "directory component exists as $(path_kind "$walked"): ${walked}" \
        "remove that entry and run this script again"
    fi
    if [[ ! -d "$walked" ]] && ! mkdir -- "$walked" 2>/dev/null; then
      if [[ -L "$walked" ]]; then
        die "$status" \
          "directory component became a symbolic link while it was created: ${walked}"
      fi
      if [[ ! -d "$walked" ]]; then
        die "$status" "unable to create directory: ${walked}"
      fi
    fi
  done
  if ! resolved="$(cd -P -- "$path" 2>/dev/null && printf '%s' "$PWD")" ||
    [[ "$resolved" != "$path" ]]; then
    die "$status" \
      "directory ${path} resolves to ${resolved:-nothing}" \
      "remove the entry that redirects it and run this script again"
  fi
}

# Copies one file to a destination this script owns and replaces the
# destination in one step. Both paths pass the path rule first, the bytes are
# written into a file created beside the destination, and the rename that
# follows leaves either the previous content or the complete new content at the
# destination name, never a partial file.
publish_file() {
  local source="$1" target="$2" status="$3"
  local temporary="${target%/*}/.publish-${RUN_ID}-${target##*/}"

  assert_readable_path "$source" "$status"
  assert_writable_path "$target" "$status"
  create_private_file "$temporary" "$status"
  if ! cat -- "$source" >"$temporary"; then
    rm -f -- "$temporary"
    die "$status" "unable to write ${temporary} from ${source}"
  fi
  if ! mv -f -- "$temporary" "$target"; then
    rm -f -- "$temporary"
    die "$status" "unable to move ${temporary} onto ${target}"
  fi
}

# Prints the SHA-256 of one file outside this checkout, such as a file of the
# configuration directory of the compiler installation. The path rule above
# governs the paths this script writes and the record it hands the driver; a
# file read here is neither, so it is required to be a readable regular file and
# is read once, never written.
hash_external_file() {
  local path="$1" status="$2"
  local line=""

  if [[ ! -f "$path" || ! -r "$path" ]]; then
    die "$status" "not a readable regular file: ${path}"
  fi
  if ! line="$(sha256sum -- "$path")" || [[ -z "$line" ]]; then
    die "$status" "unable to read the SHA-256 of: ${path}"
  fi
  printf '%s' "${line%% *}"
}

# Prints the SHA-256 of one file, read through its name after the path rule has
# accepted it.
hash_file() {
  local path="$1" status="$2"
  local line=""

  assert_readable_path "$path" "$status"
  if ! line="$(sha256sum -- "$path")" || [[ -z "$line" ]]; then
    die "$status" "unable to read the SHA-256 of: ${path}"
  fi
  printf '%s' "${line%% *}"
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

# Takes the exclusive harness lock of this checkout and holds it for the rest of
# the run, publication included. The lock stands on one file below the build
# directory, which is created here as the first shared path of the run and is
# covered by the ignore rules of modernization/.gitignore; the file is opened
# for append and never written, so every run of this checkout locks the same
# inode. The wait is bounded by HARNESS_LOCK_WAIT_SECONDS, a value outside the
# accepted range ends the run as a preflight failure before anything is created,
# and a wait that runs out ends the run with EXIT_LOCK, naming the lock file and
# the seconds waited, with no sample, module, log or published name of this run
# created. Every path this script writes is reached only after this returns, so
# two invocations on one checkout cannot regenerate or publish over each other.
acquire_harness_lock() {
  local supplied="" path="" fd=""

  supplied="${HARNESS_LOCK_WAIT_SECONDS:-$HARNESS_LOCK_WAIT_DEFAULT}"
  if [[ ! "$supplied" =~ ^[0-9]{1,4}$ ]] || ((10#$supplied < 1)) ||
    ((10#$supplied > HARNESS_LOCK_WAIT_MAX)); then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_LOCK_WAIT_SECONDS holds ${supplied}; a whole number of seconds from 1 to ${HARNESS_LOCK_WAIT_MAX} is accepted" \
      "unset it to wait up to ${HARNESS_LOCK_WAIT_DEFAULT} seconds, or set it to a value in that range"
  fi
  HARNESS_LOCK_WAIT="$((10#$supplied))"

  ensure_directory "$BUILD_DIR" "$EXIT_PREFLIGHT"
  path="${BUILD_DIR}/${HARNESS_LOCK_NAME}"
  assert_writable_path "$path" "$EXIT_PREFLIGHT"
  if ! { exec {fd}>>"$path"; } 2>/dev/null; then
    die "$EXIT_PREFLIGHT" \
      "unable to open the harness lock file: ${path}" \
      "grant write permission on ${BUILD_DIR} and run this script again"
  fi
  HARNESS_LOCK_FD="$fd"
  HARNESS_LOCK_PATH="$path"
  assert_open_descriptor "$path" "$fd" "$EXIT_PREFLIGHT"

  # The lock is held through this descriptor, which stays open until the run
  # ends, and the wait is bounded, so a run never waits for a run that has
  # stopped and never waits without end. The tool's own diagnostic is discarded,
  # leaving the message below as the only record of a wait that ran out.
  if ! flock -x -w "$HARNESS_LOCK_WAIT" "$fd" 2>/dev/null; then
    die "$EXIT_LOCK" \
      "another run of this script still holds the harness lock ${path} after ${HARNESS_LOCK_WAIT} seconds" \
      "one run at a time uses the build tree of a checkout; wait for the run that holds it to finish and run this script again" \
      "raise HARNESS_LOCK_WAIT_SECONDS above ${HARNESS_LOCK_WAIT} to wait longer"
  fi
  emit_step \
    "harness lock held: ${path} (waited up to ${HARNESS_LOCK_WAIT} seconds)"
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
      "provision the ${PYTHON_SERIES} environment carrying the pins of modernization/requirements.txt through the project's controlled environment setup; this script installs nothing" \
      "or set PY to an installed interpreter of the ${PYTHON_SERIES} series, such as modernization/.venv/bin/python"
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
      "the pinned GnuCOBOL ${COBC_VERSION_PINNED} package is provisioned through the project's controlled environment setup; this script reports the requirement and installs nothing" \
      "set COBC to the path of a GnuCOBOL ${COBC_MAJOR_REQUIRED}.x compiler already installed, or add its directory to PATH"
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
      "set COBC to an installed GnuCOBOL ${COBC_MAJOR_REQUIRED}.x compiler; this script installs nothing"
  fi
  if ! version_at_least "$COBC_VERSION" "$COBC_VERSION_FLOOR"; then
    die "$EXIT_PREFLIGHT" \
      "the compiler reports GnuCOBOL ${COBC_VERSION}, below the accepted ${COBC_VERSION_FLOOR}" \
      "set COBC to an installed GnuCOBOL ${COBC_VERSION_FLOOR} or later compiler; this script installs nothing"
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
      "set COBC to an installed compiler whose --version reports ${COBC_VERSION_PINNED}, or unset HARNESS_STRICT_TOOL_VERSIONS to accept ${COBC_VERSION}; this script installs nothing"
  fi
  emit_step "cobc ${COBC_VERSION} (${COBC})"
  emit_deviation "cobc pinned=${COBC_VERSION_PINNED} measured=${COBC_VERSION}"
}

# Prints the supplied value without its leading and trailing spaces and tabs.
# Uses shell builtins only, so it reads a compiler report and a configuration
# line without invoking a tool.
trim_space() {
  local value="$1"

  while [[ "$value" == [[:space:]]* ]]; do
    value="${value#?}"
  done
  while [[ "$value" == *[[:space:]] ]]; do
    value="${value%?}"
  done
  printf '%s' "$value"
}

# Prints the value the compiler reports for one item of its own "--info"
# output, and prints nothing when that output carries no such item. The report
# names one item per line as "<item><spaces>: <value>", wraps a long value onto
# indented continuation lines, and repeats an item the environment overrides on
# its own "  env: <item> : <value>" line. The continuation lines of the item are
# joined to its value with one space between them, and the "env:" line is not
# read: this reports what the installation carries, whatever the caller
# exported.
cobc_info_value() {
  local want="$1"
  local line="" key="" value="" out="" inside=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    case "$line" in
      "  env: "*)
        inside=0
        continue
        ;;
    esac
    if [[ "$line" != [[:space:]]* && "$line" == *" : "* ]]; then
      key="$(trim_space "${line%%:*}")"
      value="$(trim_space "${line#*" : "}")"
      if [[ "$key" == "$want" ]]; then
        inside=1
        out="$value"
      else
        inside=0
      fi
      continue
    fi
    if ((inside == 1)) && [[ "$line" == [[:space:]]* ]]; then
      value="$(trim_space "$line")"
      if [[ -n "$value" ]]; then
        out+=" ${value}"
      fi
      continue
    fi
    inside=0
  done <<<"$COBC_INFO_TEXT"

  printf '%s' "$out"
}

# Reads one file of the dialect chain: records its SHA-256, follows every
# configuration file it includes at the point the include stands, records every
# word list it names, and keeps the value of each key of COBC_DIALECT_KEYS the
# file assigns. A key assigned again later in the chain keeps the later value,
# the order the compiler reads them in. A file already read is not read again,
# and a chain deeper than COBC_DIALECT_MAX_DEPTH ends the run.
read_dialect_file() {
  local name="$1" depth="$2" kind="$3"
  local path="${COBC_CONFIG_DIR_PINNED}/${name}"
  local line="" trimmed="" key="" value="" digest=""

  if ((depth > COBC_DIALECT_MAX_DEPTH)); then
    die "$EXIT_PREFLIGHT" \
      "the dialect chain of ${COBC_DIALECT_ENTRY} includes files more than ${COBC_DIALECT_MAX_DEPTH} levels deep at ${name}" \
      "the configuration directory of this run is ${COBC_CONFIG_DIR_PINNED}"
  fi
  if [[ -n "${COBC_DIALECT_SEEN[$name]:-}" ]]; then
    return 0
  fi
  if [[ "$name" == */* || "$name" == "." || "$name" == ".." ]]; then
    die "$EXIT_PREFLIGHT" \
      "the dialect chain of ${COBC_DIALECT_ENTRY} names ${name}, which is not a single file name" \
      "the configuration directory of this run is ${COBC_CONFIG_DIR_PINNED}"
  fi
  if [[ ! -f "$path" || ! -r "$path" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the dialect chain of ${COBC_DIALECT_ENTRY} names ${name}, which is not a readable file: ${path}" \
      "install the configuration directory of the compiler this run uses, or set COBC to a compiler that carries it"
  fi
  COBC_DIALECT_SEEN["$name"]=1
  digest="$(hash_external_file "$path" "$EXIT_PREFLIGHT")"
  COBC_DIALECT_FILES+=("${name}|${kind}|${digest}")

  if [[ "$kind" == "words" ]]; then
    return 0
  fi

  while IFS= read -r line || [[ -n "$line" ]]; do
    trimmed="$(trim_space "$line")"
    if [[ -z "$trimmed" || "$trimmed" == "#"* ]]; then
      continue
    fi
    if [[ "$trimmed" =~ ^include[[:space:]]+\"([^\"]+)\" ]]; then
      read_dialect_file "${BASH_REMATCH[1]}" "$((depth + 1))" "dialect"
      continue
    fi
    if [[ "$trimmed" =~ ^include:[[:space:]]*\"([^\"]+)\" ]]; then
      read_dialect_file "${BASH_REMATCH[1]}" "$((depth + 1))" "words"
      continue
    fi
    if [[ ! "$trimmed" =~ ^([A-Za-z0-9][A-Za-z0-9_-]*):[[:space:]]*(.*)$ ]]; then
      continue
    fi
    key="${BASH_REMATCH[1]}"
    if [[ -z "${COBC_DIALECT_VALUE[$key]+set}" ]]; then
      continue
    fi
    value="$(trim_space "${BASH_REMATCH[2]%%#*}")"
    COBC_DIALECT_VALUE["$key"]="$value"
    COBC_DIALECT_SOURCE["$key"]="$name"
  done <"$path"
}

# Resolves the dialect the mandated "-std=ibm" of this run compiles under: the
# files of its include chain with the SHA-256 of each, and the value the chain
# leaves for every key the harness depends on. A key the chain never assigns is
# reported as unresolved rather than assumed.
resolve_compiler_dialect() {
  local key="" entry=""

  COBC_DIALECT_FILES=()
  COBC_DIALECT_VALUE=()
  COBC_DIALECT_SOURCE=()
  COBC_DIALECT_SEEN=()
  for key in "${COBC_DIALECT_KEYS[@]}"; do
    COBC_DIALECT_VALUE["$key"]="unresolved"
    COBC_DIALECT_SOURCE["$key"]="none"
  done

  read_dialect_file "$COBC_DIALECT_ENTRY" 1 "dialect"

  emit_step \
    "dialect chain of ${COBC_DIALECT_ENTRY}: ${#COBC_DIALECT_FILES[@]} files under ${COBC_CONFIG_DIR_PINNED}"
  for key in "${COBC_DIALECT_KEYS[@]}"; do
    entry+="${entry:+, }${key}=${COBC_DIALECT_VALUE[$key]}"
  done
  emit_step "dialect keys resolved: ${entry}"
  emit_step \
    "binary truncation in force: yes, pinned by the mandated -fbinary-truncate whatever binary-truncate the chain resolves"
}

# Pins the compiler environment of this run before anything is compiled, and
# reports every ambient value it replaced. Each item of COBC_PINNED_ENVIRONMENT
# the caller exported is reported as a deviation and removed first, so the
# compiler then reports the values of its own installation rather than the ones
# a caller placed in the environment; the configuration directory and the C
# options of that installation are then exported for the rest of the run, the
# run-time configuration is left unset, and the dialect the compile resolves is
# read out of the pinned directory. The compile and the execution stages both
# run under what this sets.
pin_compiler_environment() {
  local name="" ambient="" reported="" defines=0 fortify="" token=""
  local -a tokens=() kept=()

  COBC_AMBIENT_IGNORED=()
  for name in "${COBC_PINNED_ENVIRONMENT[@]}"; do
    if [[ ! -v "$name" ]]; then
      continue
    fi
    ambient="${!name}"
    COBC_AMBIENT_IGNORED+=("${name}=${ambient}")
    unset -v "$name"
    emit_deviation \
      "ambient ${name}=${ambient} ignored; this run pins the compiler environment itself"
  done

  if ! COBC_INFO_TEXT="$("$COBC" --info 2>/dev/null)" ||
    [[ -z "$COBC_INFO_TEXT" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the COBOL compiler did not report its own configuration: ${COBC}" \
      "check it with: ${COBC} --info"
  fi

  reported="$(cobc_info_value "COB_CONFIG_DIR")"
  if [[ -z "$reported" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the COBOL compiler reported no configuration directory: ${COBC}" \
      "check it with: ${COBC} --info | grep COB_CONFIG_DIR"
  fi
  if [[ "$reported" != /* || ! -d "$reported" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the COBOL compiler reports the configuration directory ${reported}, which is not an absolute path to a directory" \
      "install the configuration directory of that compiler, or set COBC to a compiler that carries it"
  fi
  if [[ ! -f "${reported}/${COBC_DIALECT_ENTRY}" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the configuration directory ${reported} carries no ${COBC_DIALECT_ENTRY}, the dialect file the mandated options name" \
      "install the configuration directory of that compiler, or set COBC to a compiler that carries it"
  fi
  COBC_CONFIG_DIR_PINNED="$reported"
  export COB_CONFIG_DIR="$COBC_CONFIG_DIR_PINNED"
  emit_step "COB_CONFIG_DIR=${COB_CONFIG_DIR} (pinned to the compiler's own)"
  emit_step \
    "COB_RUNTIME_CONFIG left unset, so the run-time configuration of that installation is loaded"
  resolve_compiler_dialect

  # The C options of the compiler itself, with the duplicated definition
  # reduced to the one that takes effect. A report that carries no C options
  # leaves the variable unset, which is the compiler's own default, and says so.
  reported="$(cobc_info_value "COB_CFLAGS")"
  if [[ -z "$reported" ]]; then
    COBC_CFLAGS_PINNED="unset"
    emit_deviation \
      "the compiler reported no C options; COB_CFLAGS stays unset and a host toolchain diagnostic may be reported per compile"
    emit_step "COB_CFLAGS left unset (the compiler reported no C options)"
    return 0
  fi
  IFS=$' \t\n' read -r -a tokens <<<"$reported"
  for token in "${tokens[@]}"; do
    if [[ "$token" == "${COBC_CFLAGS_DUPLICATED_DEFINE}"* ]]; then
      defines=$((defines + 1))
      fortify="$token"
      continue
    fi
    kept+=("$token")
  done
  if ((defines > 1)); then
    kept+=("$fortify")
    COBC_CFLAGS_PINNED="$(join_with " " "${kept[@]}")"
  else
    COBC_CFLAGS_PINNED="$reported"
  fi
  export COB_CFLAGS="$COBC_CFLAGS_PINNED"
  emit_step "COB_CFLAGS=${COB_CFLAGS}"
  if ((defines > 1)); then
    emit_step \
      "C options pinned: ${defines} ${COBC_CFLAGS_DUPLICATED_DEFINE} definitions of the host toolchain reduced to the one that takes effect, ${fortify}"
  fi
}

# Succeeds when the supplied option is one of the extra options the allow-list
# names.
cobc_flag_allowed() {
  local candidate="$1" allowed=""

  for allowed in "${COBC_FLAGS_ALLOWED_EXTRA[@]}"; do
    if [[ "$candidate" == "$allowed" ]]; then
      return 0
    fi
  done
  return 1
}

# Succeeds when the supplied option is one of the mandated options, which every
# compile passes whether or not the environment restates it.
cobc_flag_mandated() {
  local candidate="$1" mandated=""

  for mandated in "${COBC_FLAGS_MANDATED[@]}"; do
    if [[ "$candidate" == "$mandated" ]]; then
      return 0
    fi
  done
  return 1
}

# Prints the setting the supplied option would change, as "<prefix>|<setting>",
# and prints nothing when it would change none. An option matches a prefix when
# it is that prefix or begins with that prefix followed by "=".
cobc_flag_conflict() {
  local candidate="$1" entry="" prefix=""

  for entry in "${COBC_FLAGS_CONFLICTING[@]}"; do
    prefix="${entry%%|*}"
    if [[ "$candidate" == "$prefix" || "$candidate" == "${prefix}="* ]]; then
      printf '%s' "$entry"
      return 0
    fi
  done
  return 0
}

# Prints the entry of the refused list the supplied option matches, as
# "<option>|<what it does>", and prints nothing when it matches none. An option
# matches an entry when it is that option or begins with that option followed
# by "=", so the directory form of a refused option is refused too.
cobc_flag_refused() {
  local candidate="$1" entry="" option=""

  for entry in "${COBC_FLAGS_REFUSED[@]}"; do
    option="${entry%%|*}"
    if [[ "$candidate" == "$option" || "$candidate" == "${option}="* ]]; then
      printf '%s' "$entry"
      return 0
    fi
  done
  return 0
}

# Adds one externally supplied compiler option to the argument list of this
# run. A mandated option is accepted and dropped: the list already carries it.
# An option of the allow-list is appended once. An option that
# names the source format, the copybook folding, the copybook extension, an
# include directory or an output selector is refused as conflicting, an option
# of the refused list is refused by name, and any other option is refused as
# unknown.
accept_cobc_extra_flag() {
  local candidate="$1" origin="$2" conflict="" refused="" present=""

  if cobc_flag_mandated "$candidate"; then
    return 0
  fi
  conflict="$(cobc_flag_conflict "$candidate")"
  if [[ -n "$conflict" ]]; then
    die "$EXIT_PREFLIGHT" \
      "${origin} names ${candidate}, which names ${conflict##*|} this script sets itself" \
      "every compile of this run passes $(join_with " " "${COBC_FLAGS_MANDATED[@]}") and that cannot be replaced" \
      "remove ${candidate} from ${origin} and run this script again"
  fi
  refused="$(cobc_flag_refused "$candidate")"
  if [[ -n "$refused" ]]; then
    die "$EXIT_PREFLIGHT" \
      "${origin} names ${candidate}, and ${refused%%|*} ${refused##*|}" \
      "the compiler writes those files beside the working directory of this script, which is ${REPO_ROOT}, and every generated file of this run belongs under ${BUILD_DIR}" \
      "-debug adds the run-time checking and -fstack-check the stack check without writing a file" \
      "remove ${candidate} from ${origin} and run this script again"
  fi
  if ! cobc_flag_allowed "$candidate"; then
    die "$EXIT_PREFLIGHT" \
      "${origin} names ${candidate}, which is not an accepted extra compiler option" \
      "accepted extra options are: $(join_with " " "${COBC_FLAGS_ALLOWED_EXTRA[@]}")" \
      "remove ${candidate} from ${origin} and run this script again"
  fi
  for present in "${COBC_FLAG_LIST[@]}"; do
    if [[ "$present" == "$candidate" ]]; then
      return 0
    fi
  done
  COBC_FLAG_LIST+=("$candidate")
  if [[ -n "$COBC_FLAGS_EXTRA_ACCEPTED" ]]; then
    COBC_FLAGS_EXTRA_ACCEPTED+=" "
  fi
  COBC_FLAGS_EXTRA_ACCEPTED+="$candidate"
}

# Builds the argument list every compile of this run passes to the compiler.
# The mandated options come first and are not read from the environment, so no
# run can compile under a different source format, copybook folding or copybook
# extension. COBC_EXTRA_FLAGS and COBC_FLAGS may then add options of the
# allow-list; anything else ends the run here, before a module is built.
preflight_cobc_flags() {
  local -a tokens=()
  local token="" source_name=""

  COBC_FLAG_LIST=("${COBC_FLAGS_MANDATED[@]}")
  COBC_FLAGS_EXTRA_ACCEPTED=""

  for source_name in "COBC_EXTRA_FLAGS" "COBC_FLAGS"; do
    tokens=()
    case "$source_name" in
      COBC_EXTRA_FLAGS) IFS=$' \t\n' read -r -a tokens <<<"${COBC_EXTRA_FLAGS:-}" ;;
      COBC_FLAGS) IFS=$' \t\n' read -r -a tokens <<<"${COBC_FLAGS:-}" ;;
    esac
    for token in "${tokens[@]}"; do
      if [[ -z "$token" ]]; then
        continue
      fi
      accept_cobc_extra_flag "$token" "$source_name"
    done
  done

  COBC_FLAGS_EFFECTIVE="$(join_with " " "${COBC_FLAG_LIST[@]}")"
  emit_step "cobc flags: ${COBC_FLAGS_EFFECTIVE}"
  if [[ -n "$COBC_FLAGS_EXTRA_ACCEPTED" ]]; then
    emit_step "cobc extra flags accepted: ${COBC_FLAGS_EXTRA_ACCEPTED}"
  fi
}

# Checks that every harness input this run reads is a readable regular file,
# and that the read-only source directory the translator reads is present.
preflight_inputs() {
  local path="" entry=""
  local -a required=(
    "$TRANSLATOR"
    "$STATEMENT_MAP"
    "$DRIVER_SOURCE"
    "$RECORD_BUILDER"
    "$FIELD_MAP"
    "$SOURCE_GUARD"
  )

  for entry in "${HARNESS_COPYBOOKS[@]}"; do
    required+=("$entry")
  done
  for entry in "${STUB_MODULES[@]}"; do
    required+=("${entry%%|*}")
  done
  # A derived fixture has no sample definition of its own: this script writes
  # its record from the record of the fixture it names.
  for entry in "${HARNESS_FIXTURES[@]}"; do
    if [[ -n "$(fixture_base "$entry")" ]]; then
      continue
    fi
    required+=("${SAMPLE_INPUT_DIR}/commarea_${entry}.json")
  done

  if [[ ! -x "$SOURCE_GUARD" ]]; then
    die "$EXIT_PREFLIGHT" \
      "the read-only source guard is not an executable file: ${REPO_ROOT}/${SOURCE_GUARD}" \
      "restore it, or grant the execute bit, before running the harness"
  fi

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
# holds one to nine digits above zero and leaves room for the value every later
# row of the case table receives; a supplied timestamp seed holds exactly
# twenty-six characters in the form the chain reads back, and names a real
# Gregorian date and time.
#
# One rule governs the timestamp seed in the three places that read it: this
# preflight, modernization/harness/driver.cbl and
# modernization/harness/stubs/sql_insert_policy.cbl. The three accept the same
# values - the six separators in their fixed positions, digits everywhere else,
# a year of 0001 through 9999, a month of 01 through 12, a day inside the
# length of that month under the Gregorian leap rule, an hour of 00 through 23
# and a minute and a second of 00 through 59 - so a seed that reaches a case is
# the seed its captures report and its assertions compare. The driver and the
# stub replace a value they refuse with ${LASTCHANGED_DEFAULT}; this preflight
# refuses it before any case runs.
#
# Reads one two-digit component of a timestamp at its fixed offset and ends the
# run unless it lies between low and high. The digits and the separators of the
# value have already been matched by the caller.
assert_timestamp_component() {
  local value="$1" name="$2" offset="$3" low="$4" high="$5"
  local component=""

  component="${value:offset:2}"
  if ((10#$component < low || 10#$component > high)); then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_LASTCHANGED holds ${value}, whose ${name} is ${component}; $(printf '%02d' "$low") to ${high} is accepted" \
      "the driver and the policy stub refuse that ${name} and use ${LASTCHANGED_DEFAULT} instead" \
      "unset HARNESS_LASTCHANGED to use ${LASTCHANGED_DEFAULT}, or set the ${name} inside that range"
  fi
}

# Reads the four-digit year of a timestamp and ends the run when it is 0000,
# the one four-digit value no calendar carries.
assert_timestamp_year() {
  local value="$1"
  local year=""

  year="${value:0:4}"
  if ((10#$year < 1)); then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_LASTCHANGED holds ${value}, whose year is ${year}; 0001 to 9999 is accepted" \
      "the driver and the policy stub refuse that year and use ${LASTCHANGED_DEFAULT} instead" \
      "unset HARNESS_LASTCHANGED to use ${LASTCHANGED_DEFAULT}, or set the year inside that range"
  fi
}

# Prints the number of days the named month of the named year holds. February
# is taken from the Gregorian leap rule: a year divisible by four is a leap
# year unless it is divisible by 100 without being divisible by 400. Both
# arguments are decimal integers.
month_length() {
  local year="$1" month="$2"

  case "$month" in
    1 | 3 | 5 | 7 | 8 | 10 | 12) printf '31' ;;
    4 | 6 | 9 | 11) printf '30' ;;
    2)
      if ((year % 4 == 0 && (year % 100 != 0 || year % 400 == 0))); then
        printf '29'
      else
        printf '28'
      fi
      ;;
    *) return 1 ;;
  esac
}

# Reads the day of a timestamp and ends the run unless the month and the year
# it stands in hold that many days. The year and the month have already been
# checked by the caller, so the length is always resolved.
assert_timestamp_day() {
  local value="$1"
  local year="" month="" day="" length=""

  year="${value:0:4}"
  month="${value:5:2}"
  day="${value:8:2}"
  if ! length="$(month_length "$((10#$year))" "$((10#$month))")"; then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_LASTCHANGED holds ${value}, whose month ${month} names no calendar month" \
      "unset HARNESS_LASTCHANGED to use ${LASTCHANGED_DEFAULT}, or set a month of 01 through 12"
  fi
  if ((10#$day < 1 || 10#$day > length)); then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_LASTCHANGED holds ${value}, whose day is ${day}; month ${month} of year ${year} holds ${length} days" \
      "the driver and the policy stub refuse that day and use ${LASTCHANGED_DEFAULT} instead" \
      "unset HARNESS_LASTCHANGED to use ${LASTCHANGED_DEFAULT}, or set a day of 01 through ${length}"
  fi
}

preflight_seeds() {
  local supplied="" highest=0

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
  highest=$((10#$supplied + ${#HARNESS_CASES[@]} - 1))
  if ((highest > POLICY_NUMBER_MAX)); then
    die "$EXIT_PREFLIGHT" \
      "HARNESS_POLICY_NUMBER holds ${supplied}; the ${#HARNESS_CASES[@]} cases of the table would reach ${highest}, above ${POLICY_NUMBER_MAX}" \
      "unset it to use ${POLICY_NUMBER_DEFAULT}, or set it low enough for ${#HARNESS_CASES[@]} consecutive values"
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
  assert_timestamp_year "$supplied"
  assert_timestamp_component "$supplied" "month" 5 1 12
  assert_timestamp_component "$supplied" "hour" 11 0 23
  assert_timestamp_component "$supplied" "minute" 14 0 59
  assert_timestamp_component "$supplied" "second" 17 0 59
  assert_timestamp_day "$supplied"
  LASTCHANGED_SEED="$supplied"

  emit_step "seeds: first case policy ${POLICY_NUMBER_BASE}, last case policy $((POLICY_NUMBER_BASE + ${#HARNESS_CASES[@]} - 1)), lastchanged ${LASTCHANGED_SEED}"
}

# Creates the build directories of this run, the run directory of every
# selected case, the staging directory of this run and the validation
# artifacts directory. Each is created one component at a time under the
# physical repository root, and each is confirmed to resolve to the path it
# names, so no link can move an output tree.
prepare_directories() {
  local label="" name="" entry=""
  local -a wanted=("$BUILD_DIR" "$SRC_DIR" "$BIN_DIR" "$SAMPLES_DIR" "$RUN_DIR"
    "$LOGS_DIR" "$ARTIFACTS_DIR" "$STAGING_DIR")

  for label in "${SELECTED_CASES[@]}"; do
    name="$(case_lower "$label")"
    wanted+=("${RUN_DIR}/${name}")
  done

  for entry in "${wanted[@]}"; do
    ensure_directory "$entry" "$EXIT_PREFLIGHT"
  done
  emit_step "directories ready under ${BUILD_DIR}"
  emit_step "staging directory of this run: ${STAGING_DIR}"
  emit_step "evidence directory ready at ${ARTIFACTS_DIR}"
}

# Empties the evidence log the source guard appends its blocks to, so the log
# records the gates of this run and nothing that ran before it. The path rule
# accepts the name first, and the log is emptied through that name: it keeps the
# mode it carries, it is never absent while a run is in progress, and it is
# created empty when it is absent. Runs once per run, after the harness lock is
# held and before the first gate.
reset_source_guard_log() {
  local path="${REPO_ROOT}/${SOURCE_GUARD_LOG}"

  assert_writable_path "$path" "$EXIT_PREFLIGHT"
  if ! : >"$path"; then
    die "$EXIT_PREFLIGHT" \
      "unable to empty the evidence log of the source guard: ${path}" \
      "grant write permission on that path, or free space on its file system, and run this script again"
  fi
  emit_step "source guard evidence log emptied: ${SOURCE_GUARD_LOG}"
}

# Runs the read-only scope gate of the bridge and ends the run when it does not
# pass. The gate holds the approved SHA-256 baseline of the five named source
# artifacts, checks that no tracked file outside its exempt inventory of the
# generated evidence set has been modified, and appends its own block to the
# evidence log named here, which the preflight of this run emptied. It runs
# before any generated output is produced and again at every stage boundary, so
# a source that moves during a run is reported at the next boundary and the log
# holds one block per gate of this run. Each gate is asked for the guard's
# reproducible block, which carries fixed text in place of the time of the gate
# and of the root its paths are relative to, and every other record in full, so
# two runs over one tracked state record the same bytes whatever directory the
# checkout was taken into; the paths a block names are the tracked state the run
# read, and which of the exempt evidence paths differ from HEAD is part of that
# state.
run_source_guard() {
  local stage="$1"
  local status=0

  set +e
  timeout "$GUARD_TIMEOUT_SECONDS" "$SOURCE_GUARD" \
    --stage "$stage" --log "$SOURCE_GUARD_LOG" --reproducible --quiet </dev/null
  status=$?
  set -e
  if ((status == 124)); then
    GUARD_VERDICT="TIMEOUT"
    die "$EXIT_GUARD" \
      "the read-only source guard did not finish within ${GUARD_TIMEOUT_SECONDS} seconds at stage ${stage}" \
      "its evidence log is ${REPO_ROOT}/${SOURCE_GUARD_LOG}"
  fi
  if ((status != 0)); then
    GUARD_VERDICT="FAIL"
    die "$EXIT_GUARD" \
      "the read-only source guard failed at stage ${stage}, exit ${status}" \
      "its evidence log is ${REPO_ROOT}/${SOURCE_GUARD_LOG}" \
      "restore the five named files under ${SOURCE_DIR} and every tracked file the guard's exempt inventory does not name, then run this script again" \
      "reproduce it with: ./${SOURCE_GUARD} --stage ${stage} --log ${SOURCE_GUARD_LOG} --reproducible"
  fi
  GUARD_VERDICT="PASS"
  GUARD_PASSES=$((GUARD_PASSES + 1))
  emit_step "source guard ${stage}: PASS (${SOURCE_GUARD_LOG})"
}

# Runs every preflight check, pins the compiler environment the compile and the
# execution stages run under, reports the selected cases, empties the evidence
# log of the source guard and closes the stage with the first gate of the run,
# so no generated output exists before the approved source hashes have been
# confirmed.
stage_preflight() {
  emit_stage 1 "preflight"
  preflight_tools
  acquire_harness_lock
  preflight_python
  preflight_cobc
  pin_compiler_environment
  preflight_cobc_flags
  preflight_inputs
  preflight_seeds
  resolve_selected_fixtures
  prepare_directories
  emit_step "cases selected: $(join_with ", " "${SELECTED_CASES[@]}")"
  emit_step "fixtures selected: $(join_with ", " "${SELECTED_FIXTURES[@]}")"
  # The gate appends one block per run of it, so the log is emptied here, before
  # the first of the four runs. The published copy then carries the four blocks
  # of this run alone.
  reset_source_guard_log
  run_source_guard "harness-preflight"
}

# --------------------------------------------------------------------------
# Stage 2: samples and translation
# --------------------------------------------------------------------------
# Ends the run unless the record of the named fixture holds exactly the bytes
# one generated record holds. The size check protects the offset decoding this
# script and every later step apply to the record.
assert_sample_size() {
  local fixture="$1" output="$2"
  local size=""

  assert_readable_path "$output" "$EXIT_SAMPLE"
  if ! size="$(file_size "$output")"; then
    die "$EXIT_SAMPLE" \
      "unable to read the size of the generated record for fixture ${fixture}: ${output}"
  fi
  if [[ "$size" != "$RECORD_BYTES" ]]; then
    die "$EXIT_SAMPLE" \
      "the generated record for fixture ${fixture} holds ${size} bytes: ${output}" \
      "${RECORD_BYTES} bytes are required, being 32,500 characters and one line feed" \
      "check the field map and the sample definition, then run this script again"
  fi
  emit_step "sample ${fixture}: ${output} (${size} bytes)"
}

# Prints the overlay of one derived fixture, one "<field>|<kind>|<value>" entry
# per line. A fixture the list below does not name ends the run.
derived_overlay() {
  local fixture="$1" entry=""

  case "$fixture" in
    "$HOUSE_FIXTURE")
      for entry in "${HOUSE_FIXTURE_OVERLAY[@]}"; do
        printf '%s\n' "$entry"
      done
      ;;
    *)
      die "$EXIT_SAMPLE" \
        "no overlay is defined for the derived fixture ${fixture}"
      ;;
  esac
}

# Writes the record of one derived fixture: a copy of the record of the fixture
# it is written from, with every field of its overlay written over that copy at
# the offset and length the field table names, then read back field by field.
# The read-back uses the same reader the assertions of a case use, so a record
# whose overlay did not land where the field table says ends the run here rather
# than reaching a case.
derive_sample() {
  local fixture="$1" base="$2"
  local source="${SAMPLES_DIR}/commarea_${base}.dat"
  local output="${SAMPLES_DIR}/commarea_${fixture}.dat"
  local entry="" field="" kind="" value="" spec="" offset="" length=""
  local padded="" observed="" number=""
  local -a overlay=()

  mapfile -t overlay < <(derived_overlay "$fixture")
  if ((${#overlay[@]} == 0)); then
    die "$EXIT_SAMPLE" "the overlay of the derived fixture ${fixture} is empty"
  fi
  if [[ ! -f "$source" ]]; then
    die "$EXIT_SAMPLE" \
      "fixture ${fixture} is written from ${base}, whose record is missing: ${source}" \
      "the fixture list names ${base} before ${fixture} so that record exists first"
  fi
  assert_readable_path "$source" "$EXIT_SAMPLE"
  create_private_file "$output" "$EXIT_SAMPLE"
  if ! cat -- "$source" >"$output"; then
    die "$EXIT_SAMPLE" "unable to write ${output} from ${source}"
  fi

  for entry in "${overlay[@]}"; do
    field="${entry%%|*}"
    kind="${entry#*|}"
    kind="${kind%%|*}"
    value="${entry##*|}"
    spec="${FIXTURE_FIELDS[$field]:-}"
    if [[ -z "$spec" ]]; then
      die "$EXIT_SAMPLE" \
        "the overlay of fixture ${fixture} names the field ${field}, which the record offset table does not carry"
    fi
    offset="${spec%% *}"
    length="${spec##* }"
    case "$kind" in
      text)
        if ((${#value} > length)); then
          die "$EXIT_SAMPLE" \
            "the overlay value of ${field} holds ${#value} characters where the field holds ${length}: ${value}"
        fi
        printf -v padded '%-*s' "$length" "$value"
        ;;
      number)
        if [[ ! "$value" =~ ^[0-9]+$ ]] || ((${#value} != length)); then
          die "$EXIT_SAMPLE" \
            "the overlay value of ${field} is '${value}' where ${length} digits are required" \
            "the field is a display numeric of the COMMAREA and is read as one by the chain"
        fi
        padded="$value"
        ;;
      *)
        die "$EXIT_SAMPLE" \
          "the overlay of fixture ${fixture} names the kind ${kind} for ${field}, which is neither text nor number"
        ;;
    esac
    if ! printf '%s' "$padded" |
      dd of="$output" bs=1 seek="$((offset - 1))" conv=notrunc status=none; then
      die "$EXIT_SAMPLE" \
        "unable to write the ${field} of fixture ${fixture} at character ${offset} of ${output}"
    fi
  done

  for entry in "${overlay[@]}"; do
    field="${entry%%|*}"
    kind="${entry#*|}"
    kind="${kind%%|*}"
    value="${entry##*|}"
    spec="${FIXTURE_FIELDS[$field]}"
    length="${spec##* }"
    if [[ "$kind" == "number" ]]; then
      printf -v padded '%s' "$value"
    else
      printf -v padded '%-*s' "$length" "$value"
    fi
    observed="$(fixture_field_raw "$output" "$field")"
    if [[ "$observed" != "$padded" ]]; then
      die "$EXIT_SAMPLE" \
        "fixture ${fixture} holds '${observed}' at ${field} where '${padded}' was written: ${output}"
    fi
    if [[ "$kind" == "number" ]]; then
      if ! number="$(number_value "$observed")"; then
        die "$EXIT_SAMPLE" \
          "fixture ${fixture} holds '${observed}' at ${field}, which the chain reads as a number: ${output}"
      fi
      emit_step "fixture ${fixture}: ${field} = ${observed} (${number})"
    else
      emit_step "fixture ${fixture}: ${field} = '${observed}'"
    fi
  done
}

# Generates the full-length COMMAREA record of every fixture this run needs: a
# built fixture from its sample definition and a derived fixture from the record
# it is written from. The output name is refused before anything writes to it
# when it is a symbolic link, a multi-link file or anything other than a regular
# file.
build_samples() {
  local fixture="" sample="" output="" base=""

  for fixture in "${SELECTED_FIXTURES[@]}"; do
    output="${SAMPLES_DIR}/commarea_${fixture}.dat"
    base="$(fixture_base "$fixture")"
    if [[ -n "$base" ]]; then
      derive_sample "$fixture" "$base"
      assert_sample_size "$fixture" "$output"
      continue
    fi

    sample="${SAMPLE_INPUT_DIR}/commarea_${fixture}.json"
    remove_output_path "$output" "$EXIT_SAMPLE"
    if ! "$PY" "$RECORD_BUILDER" \
      --sample "$sample" \
      --output "$output" \
      --field-map "$FIELD_MAP" </dev/null; then
      die "$EXIT_SAMPLE" \
        "the record builder failed for fixture ${fixture} on ${sample}" \
        "reproduce it with: ${PY} ${RECORD_BUILDER} --sample ${sample} --output ${output} --field-map ${FIELD_MAP}"
    fi
    if [[ ! -f "$output" ]]; then
      die "$EXIT_SAMPLE" \
        "the record builder reported success for fixture ${fixture} but left no record at ${output}"
    fi
    assert_sample_size "$fixture" "$output"
  done
}

# Writes the translated copies of the three named programs, the verbatim
# copybooks, the source baseline and the translation report into the build
# tree. The translator reads the named sources read-only; nothing here writes
# to base/src.
translate_sources() {
  local log="${LOGS_DIR}/translate.log"

  create_private_file "$log" "$EXIT_TRANSLATE"
  run_and_tee "$EXIT_TRANSLATE" "$log" "$PY" "$TRANSLATOR" \
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
# source artifacts, so the generated copies of this run are tied to the bytes
# the translator read. The baseline lists repository-relative paths and is
# checked from the repository root. The approved hashes themselves are held by
# modernization/validation/verify_readonly.sh, which run_source_guard runs
# before this stage and at every stage boundary after it; this check reports the
# translator's own reading beside it.
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

# Asserts the chain link contract the translator publishes in its report: two
# link sites, each naming the program it links, the target the source names,
# DFHCOMMAREA as the COMMAREA operand and 32500 as the length. The report is
# read as JSON, so a site that loses its target, its operand or its length is
# reported by name.
assert_chain_link_contract() {
  local report="${LOGS_DIR}/${TRANSLATION_REPORT_NAME}"
  local output="" status=0

  if [[ ! -f "$report" ]]; then
    die "$EXIT_TRANSLATE" \
      "the translator left no report at ${report}" \
      "review ${LOGS_DIR}/translate.log for the step that did not complete"
  fi
  set +e
  output="$("$PY" - "$report" "$COMMAREA_LENGTH" "DFHCOMMAREA" \
    "${CHAIN_LINK_SITES[@]}" <<'PYTHON_CHAIN_LINK' 2>&1
"""Assert the chain link contract of the translation report.

Reads the report named by the first argument and requires its
chain_link_contract object to carry exactly the sites named by the remaining
arguments, each as "<program>|<target program>", with the COMMAREA operand and
the length named by the second and third arguments.
"""
import json
import sys

report_path = sys.argv[1]
expected_length = int(sys.argv[2])
expected_operand = sys.argv[3]
expected_sites = [item.split("|", 1) for item in sys.argv[4:]]

with open(report_path, encoding="utf-8") as handle:
    report = json.load(handle)

contract = report.get("chain_link_contract")
if not isinstance(contract, dict):
    print("the report carries no chain_link_contract object")
    raise SystemExit(1)

sites = contract.get("sites")
if not isinstance(sites, list):
    print("chain_link_contract carries no sites list")
    raise SystemExit(1)
if len(sites) != len(expected_sites):
    print(
        "chain_link_contract carries %d sites where %d are required"
        % (len(sites), len(expected_sites))
    )
    raise SystemExit(1)

by_program = {}
for site in sites:
    if not isinstance(site, dict):
        print("chain_link_contract carries a site that is not an object")
        raise SystemExit(1)
    by_program[str(site.get("program", ""))] = site

for program, target in expected_sites:
    site = by_program.get(program)
    if site is None:
        print("chain_link_contract carries no site for program %s" % program)
        raise SystemExit(1)
    if str(site.get("target_program", "")) != target:
        print(
            "site %s links %r where %s is required"
            % (program, site.get("target_program"), target)
        )
        raise SystemExit(1)
    if str(site.get("commarea_operand", "")) != expected_operand:
        print(
            "site %s passes %r where %s is required"
            % (program, site.get("commarea_operand"), expected_operand)
        )
        raise SystemExit(1)
    try:
        length = int(site.get("length"))
    except (TypeError, ValueError):
        print("site %s carries no numeric length" % program)
        raise SystemExit(1)
    if length != expected_length:
        print(
            "site %s links with length %d where %d is required"
            % (program, length, expected_length)
        )
        raise SystemExit(1)

print(
    "%d sites, %s, length %d"
    % (len(expected_sites), expected_operand, expected_length)
)
PYTHON_CHAIN_LINK
  )"
  status=$?
  set -e
  if ((status != 0)); then
    die "$EXIT_TRANSLATE" \
      "the chain link contract of ${report} does not hold: ${output}" \
      "the translator publishes that contract from the link sites of the named sources" \
      "review ${LOGS_DIR}/translate.log for the rewrite that produced it"
  fi
  emit_step "chain link contract: ${output}"
}

# Builds the records, translates the sources and checks every result: the
# generated files, the source baseline and the published link contract.
stage_samples_and_translation() {
  emit_stage 2 "samples and translation"
  build_samples
  translate_sources
  assert_generated_sources
  verify_source_baseline
  assert_chain_link_contract
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
    remove_output_path "${BIN_DIR}/${program}.so" "$EXIT_COMPILE"
  done
  remove_output_path "${BIN_DIR}/driver" "$EXIT_COMPILE"
}

# Compiles the twelve stubs and the three translated programs as callable
# modules. Each module is named after its PROGRAM-ID, the name the dynamic
# CALL of a literal resolves through COB_LIBRARY_PATH. Every compile passes the
# mandated options first, the output name is refused before the compiler runs
# when it is not a name this script owns, and compiler output, warnings
# included, is appended to the compile log and retained.
#
# The include directory, the output name and the source are handed to the
# compiler relative to the repository root, which is the working directory of
# every stage of this script, so a diagnostic the compiler writes about one of
# them names the same path from any checkout. The output name is still checked as
# the absolute path it resolves to before the compiler runs, and the command line
# recorded in the log is the command line that ran.
compile_modules() {
  local log="$1"
  local entry="" source="" program="" target="" count=0
  local include_relative="" source_relative="" target_relative=""

  include_relative="$(repo_relative "$SRC_DIR")"
  for entry in "${STUB_MODULES[@]}"; do
    source="${entry%%|*}"
    program="${entry##*|}"
    target="${BIN_DIR}/${program}.so"
    assert_writable_path "$target" "$EXIT_COMPILE"
    source_relative="$(repo_relative "$source")"
    target_relative="$(repo_relative "$target")"
    log_command "$log" "$COBC" -m "${COBC_FLAG_LIST[@]}" \
      -I "$include_relative" -o "$target_relative" "$source_relative"
    run_and_tee "$EXIT_COMPILE" "$log" "$COBC" -m "${COBC_FLAG_LIST[@]}" \
      -I "$include_relative" -o "$target_relative" "$source_relative"
    if ((RUN_STATUS != 0)); then
      die "$EXIT_COMPILE" \
        "compilation of module ${program} failed from ${source_relative}" \
        "the compiler output is retained in ${log}" \
        "reproduce it from the repository root with: ${COBC} -m ${COBC_FLAGS_EFFECTIVE} -I ${include_relative} -o ${target_relative} ${source_relative}"
    fi
    count=$((count + 1))
  done

  for entry in "${PROGRAM_MODULES[@]}"; do
    source="${SRC_DIR}/${entry%%|*}"
    program="${entry##*|}"
    target="${BIN_DIR}/${program}.so"
    assert_writable_path "$target" "$EXIT_COMPILE"
    source_relative="$(repo_relative "$source")"
    target_relative="$(repo_relative "$target")"
    log_command "$log" "$COBC" -m "${COBC_FLAG_LIST[@]}" \
      -I "$include_relative" -o "$target_relative" "$source_relative"
    run_and_tee "$EXIT_COMPILE" "$log" "$COBC" -m "${COBC_FLAG_LIST[@]}" \
      -I "$include_relative" -o "$target_relative" "$source_relative"
    if ((RUN_STATUS != 0)); then
      die "$EXIT_COMPILE" \
        "compilation of translated program ${program} failed from ${source_relative}" \
        "the compiler output is retained in ${log}" \
        "reproduce it from the repository root with: ${COBC} -m ${COBC_FLAGS_EFFECTIVE} -I ${include_relative} -o ${target_relative} ${source_relative}" \
        "a translated program that still fails after the documented rules are applied is reported, not patched by hand"
    fi
    count=$((count + 1))
  done
  emit_step "modules compiled: ${count} into ${BIN_DIR}"
}

# Compiles the driver as an executable, on the same repository-relative include
# directory, output name and source as every module compile of the stage.
compile_driver() {
  local log="$1"
  local target="${BIN_DIR}/driver"
  local include_relative="" source_relative="" target_relative=""

  assert_writable_path "$target" "$EXIT_COMPILE"
  include_relative="$(repo_relative "$SRC_DIR")"
  source_relative="$(repo_relative "$DRIVER_SOURCE")"
  target_relative="$(repo_relative "$target")"
  log_command "$log" "$COBC" -x "${COBC_FLAG_LIST[@]}" \
    -I "$include_relative" -o "$target_relative" "$source_relative"
  run_and_tee "$EXIT_COMPILE" "$log" "$COBC" -x "${COBC_FLAG_LIST[@]}" \
    -I "$include_relative" -o "$target_relative" "$source_relative"
  if ((RUN_STATUS != 0)); then
    die "$EXIT_COMPILE" \
      "compilation of the driver failed from ${source_relative}" \
      "the compiler output is retained in ${log}" \
      "reproduce it from the repository root with: ${COBC} -x ${COBC_FLAGS_EFFECTIVE} -I ${include_relative} -o ${target_relative} ${source_relative}"
  fi
  emit_step "driver compiled: ${target}"
}

# Records the compiler environment and the dialect of this run at the head of
# the compile log, above the command line of the first module: the options every
# compile passes, the pinned configuration directory and C options, every
# ambient value the pin replaced, the files of the dialect chain with the
# SHA-256 of each, and the value the chain leaves for every key the harness
# depends on. The block names the configuration directory of the compiler
# installation and no path of this checkout, so the published log reads the same
# from every checkout.
write_dialect_record() {
  local log="$1"
  local entry="" key="" name="" kind="" digest="" ignored=""
  local truncate_value=""

  truncate_value="${COBC_DIALECT_VALUE[binary-truncate]:-unresolved}"
  log_line "$log" "compiler: ${COBC_VERSION} (${COBC})"
  log_line "$log" "compiler options: ${COBC_FLAGS_EFFECTIVE}"
  log_line "$log" "COB_CONFIG_DIR: ${COBC_CONFIG_DIR_PINNED} (pinned)"
  log_line "$log" "COB_RUNTIME_CONFIG: unset (pinned)"
  log_line "$log" "COB_CFLAGS: ${COBC_CFLAGS_PINNED}"
  if ((${#COBC_AMBIENT_IGNORED[@]} == 0)); then
    log_line "$log" "ambient compiler environment ignored: none"
  else
    for ignored in "${COBC_AMBIENT_IGNORED[@]}"; do
      log_line "$log" "ambient compiler environment ignored: ${ignored}"
    done
  fi
  log_line "$log" "dialect chain of ${COBC_DIALECT_ENTRY} (file, kind, sha256):"
  for entry in "${COBC_DIALECT_FILES[@]}"; do
    name="${entry%%|*}"
    kind="${entry#*|}"
    digest="${kind#*|}"
    kind="${kind%%|*}"
    log_line "$log" "  ${name} ${kind} ${digest}"
  done
  log_line "$log" "dialect keys (key, resolved value, file that set it):"
  for key in "${COBC_DIALECT_KEYS[@]}"; do
    log_line "$log" \
      "  ${key} ${COBC_DIALECT_VALUE[$key]} ${COBC_DIALECT_SOURCE[$key]}"
  done
  log_line "$log" \
    "binary truncation in force: yes (-fbinary-truncate of the mandated options, over the chain value ${truncate_value})"
  emit_step "compiler dialect recorded in ${log}"
}

# Reports how many compiler diagnostics the compile log carries. Warnings are
# retained rather than treated as failures, and their count stands in the
# summary of the run beside the module count.
report_compile_diagnostics() {
  local log="$1"
  local warnings=0 notes=0

  warnings="$(grep -c -e 'warning:' -- "$log" || true)"
  notes="$(grep -c -e 'note:' -- "$log" || true)"
  emit_step "compiler diagnostics: ${warnings} warning lines, ${notes} note lines in ${log}"
  if ((10#$warnings > 0)); then
    emit_deviation "compiler warnings=${warnings} log=${log}"
  fi
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
    assert_readable_path "$path" "$EXIT_COMPILE"
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
  assert_readable_path "${BIN_DIR}/driver" "$EXIT_COMPILE"
  emit_step "modules present: ${count}; driver present"
}

# Compiles every module and the driver, checks the result and closes the stage
# with the source guard.
stage_compile() {
  local log="${LOGS_DIR}/compile.log"

  emit_stage 3 "compile"
  create_private_file "$log" "$EXIT_COMPILE"
  emit_step "compile log: ${log}"
  write_dialect_record "$log"
  clear_binaries
  compile_modules "$log"
  compile_driver "$log"
  assert_binaries
  report_compile_diagnostics "$log"
  run_source_guard "harness-compile"
}

# --------------------------------------------------------------------------
# Stages 4 and 5: probes and execution
# --------------------------------------------------------------------------
# Prints the meaning the driver attaches to an exit status.
driver_status_text() {
  case "$1" in
    0) printf '%s' "every check passed" ;;
    1) printf '%s' "the chain's return code differs from the expected code" ;;
    2) printf '%s' "the abend state differs from the expected abend state" ;;
    3) printf '%s' "a required capture is missing or inconsistent" ;;
    4) printf '%s' "a file input-output operation failed, or the record read held other than ${RECORD_CHARACTERS} characters" ;;
    5) printf '%s' "a required environment item was not provided or was rejected" ;;
    6) printf '%s' "a captured value differs from the fixture-derived expected value" ;;
    7) printf '%s' "the translated chain could not be called" ;;
    124) printf '%s' "the driver did not finish inside the time this script allows" ;;
    *) printf '%s' "a status the driver does not define" ;;
  esac
}

# --------------------------------------------------------------------------
# Stage 4: infrastructure probes
# --------------------------------------------------------------------------
# One probe hands the driver the environment of the first success case with one
# item of it made wrong, or one of the three handles this script opens withheld,
# and asserts both the status the driver reports and the side effect the probe
# table names. The three statuses asserted here - 7 for a chain that cannot be
# called, 5 for an environment item the driver rejects and 4 for a file
# operation that fails - are the statuses no case of the case table can reach,
# because a case that reports any non-zero status fails. Every path a probe
# creates lies below the build directory, and the empty module directory a probe
# points the runtime at is left in place, holding nothing, for the next run.
# The output names are asserted by what the probe handed over: a probe that was
# handed no output handle requires both names to be absent in every form and its
# run directory to hold nothing but the driver log, and PRB4, handed the
# post-chain handle alone, requires the capture name to be absent as well.

# Ends the run when one of the two output names of a probe exists in any form.
# Used by every probe that was handed no handle on that name: this script
# removed the name before the driver ran and opened nothing at it, so an entry
# standing there afterwards is one the driver made for itself and fails the
# probe whatever it holds. A dangling symbolic link is refused too, which "-e"
# alone does not see.
assert_probe_output_absent() {
  local label="$1" what="$2" path="$3"

  if [[ -e "$path" || -L "$path" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the ${what} name is $(path_kind "$path") where nothing is required: ${path}" \
      "this probe handed the driver no handle on that name, so nothing of the driver can stand there" \
      "remove that entry and run this script again"
  fi
  count_assertion
}

# Ends the run unless the capture file of a probe records that no part of the
# chain ran: every capture group absent, every count, link witness and
# diagnostic-link count zero, and the driver's own verdict a failure carrying
# the status the probe asserted. The driver writes its failure surface after a
# call it could not make, so this is what that surface is required to say.
assert_probe_no_chain_evidence() {
  local label="$1" expected_status="$2" capt="$3"
  local key=""
  local -a absent=("SQL_POLICY_PRESENT" "SQL_IDENTITY_PRESENT"
    "SQL_LASTCHANGED_PRESENT" "SQL_MOTOR_PRESENT" "SQL_COMMERCIAL_PRESENT"
    "SQL_ENDOWMENT_PRESENT" "SQL_HOUSE_PRESENT" "VSAM_PRESENT"
    "ABEND_PRESENT")
  local -a zero=("policy_count" "identity_count" "lastchanged_count"
    "motor_count" "commercial_count" "endowment_count" "house_count"
    "vsam_count" "abend_count" "DIAG_LINK_COUNT" "link_db2_calen"
    "link_vsam_calen")

  if [[ ! -s "$capt" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the driver reported status ${expected_status} and left no capture content at ${capt}" \
      "a status the driver reports after a call it could not make is written into its capture file"
  fi
  assert_readable_path "$capt" "$EXIT_EXECUTE"
  capture_require "$label" "$capt" "CASE"
  if [[ "$CAPTURE_VALUE" != "$label" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: CASE holds '${CAPTURE_VALUE}' where the whole label of this probe is required" \
      "the capture file is ${capt}"
  fi
  count_assertion
  for key in "${absent[@]}"; do
    assert_capture_text "$label" "$capt" "$key" "N"
  done
  for key in "${zero[@]}"; do
    assert_capture_number "$label" "$capt" "$key" 0
  done
  assert_capture_text "$label" "$capt" "DRIVER_STATUS" "FAIL"
  assert_capture_number "$label" "$capt" "DRIVER_EXIT_STATUS" "$expected_status"
  emit_step \
    "probe ${label}: capture records no chain effect, driver verdict FAIL at status ${expected_status}"
}

# Ends the run unless the post-chain record of a probe carries the bytes of the
# record the driver read. A chain that was never entered writes nothing into the
# COMMAREA, so the two files hold the same SHA-256.
assert_probe_record_unchanged() {
  local label="$1" post="$2" sample="$3"
  local post_digest="" sample_digest=""

  if [[ ! -f "$post" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the driver left no post-chain record at ${post}"
  fi
  post_digest="$(hash_file "$post" "$EXIT_EXECUTE")"
  sample_digest="$(hash_file "$sample" "$EXIT_EXECUTE")"
  if [[ "$post_digest" != "$sample_digest" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the post-chain record differs from the record the driver read" \
      "${post} holds ${post_digest}" \
      "${sample} holds ${sample_digest}" \
      "no program of the chain was entered, so the returned record carries the bytes it was given"
  fi
  count_assertion
  emit_step \
    "probe ${label}: post-chain record matches the record read, ${post_digest}"
}

# Ends the run when the supplied path exists in any form. Used for the name a
# probe hands the driver as an escape from the run directory.
assert_probe_path_absent() {
  local label="$1" what="$2" path="$3"

  if [[ -e "$path" || -L "$path" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: ${what} exists as $(path_kind "$path"): ${path}" \
      "the driver was handed a case naming a path above its run directory and created that path" \
      "remove that entry and run this script again"
  fi
  count_assertion
}

# Ends the run unless the run directory of a probe holds exactly the driver log
# this script created in it, hidden entries included. Used by every probe that
# was handed no output handle: the driver of such a probe reports its status
# through the log this script opened for it and creates nothing, so any second
# entry in that directory is a file the driver named itself.
assert_probe_directory_holds_log_only() {
  local label="$1" dir="$2"
  local -a entries=()
  local expected="${dir}/driver.log"

  if [[ -L "$dir" || ! -d "$dir" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the run directory is $(path_kind "$dir") where the directory this script created is required: ${dir}"
  fi
  shopt -s nullglob dotglob
  entries=("$dir"/*)
  shopt -u nullglob dotglob
  if ((${#entries[@]} != 1)) || [[ "${entries[0]}" != "$expected" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the run directory holds ${#entries[@]} entries where the driver log alone is required: ${dir}" \
      "entries found: $(join_with ", " "${entries[@]}")" \
      "this probe handed the driver no output handle, so it writes nothing but that log"
  fi
  count_assertion
}

# Ends the run unless the supplied path is the single-link regular file this
# script opened for the driver. Used for the one output name PRB4 does hand over:
# the file is required to be the one this script created, whatever the driver
# managed to write into it before the handle it lacks ended the run.
assert_probe_opened_file() {
  local label="$1" what="$2" path="$3"
  local links=""

  if [[ -L "$path" || ! -f "$path" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the ${what} is $(path_kind "$path") where the file this script opened for the driver is required: ${path}"
  fi
  if ! links="$(stat -c '%h' -- "$path" 2>/dev/null)"; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: unable to read the link count of the ${what}: ${path}"
  fi
  if [[ ! "$links" =~ ^[0-9]+$ ]] || ((10#$links != 1)); then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the ${what} carries ${links} hard links: ${path}" \
      "a file this script opens for the driver carries one name; remove the other links and run this script again"
  fi
  count_assertion
}

# Ends the run unless the supplied directory holds no compiled module, so the
# probe that points the runtime at it proves the chain cannot be resolved there.
assert_probe_no_modules() {
  local label="$1" path="$2"
  local -a modules=()

  shopt -s nullglob
  modules=("$path"/*.so)
  shopt -u nullglob
  if ((${#modules[@]} != 0)); then
    die "$EXIT_EXECUTE" \
      "probe ${label}: ${path} holds ${#modules[@]} modules where none is required" \
      "remove them so the probe points the runtime at a directory holding no module"
  fi
  count_assertion
}

# Prepares the run directory of one probe: the directory itself, the two names
# the driver writes through the handles of a case, removed so a name found
# afterwards belongs to this probe, and the driver log this probe retains. A
# probe that is handed a handle on one of those names opens it after this,
# through open_driver_output; a probe that is handed none leaves both names
# absent, which is what its assertions require.
prepare_probe_directory() {
  local lower="$1"
  local dir="${RUN_DIR}/${lower}"

  ensure_directory "$dir" "$EXIT_EXECUTE"
  remove_output_path "${dir}/commarea_post.dat" "$EXIT_EXECUTE"
  remove_output_path "${dir}/captures.txt" "$EXIT_EXECUTE"
  create_private_file "${dir}/driver.log" "$EXIT_EXECUTE"
}

# Exports the environment one probe starts from: the row of the first success
# case, the fixture the probes run on and the label of the probe as the case.
# The caller then makes one item of it wrong.
export_probe_environment() {
  local label="$1"

  load_case_row "${SUCCESS_CASES[0]}"
  CASE_LABEL="$label"
  CASE_FIXTURE="$PROBE_FIXTURE"
  CASE_SAMPLE="${SAMPLES_DIR}/commarea_${PROBE_FIXTURE}.dat"
  if [[ ! -f "$CASE_SAMPLE" ]]; then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the generated record of the probe fixture is missing: ${CASE_SAMPLE}"
  fi
  export_case_environment
}

# Runs the driver once for one probe and asserts the status it reports. The run
# is bounded in time and its output is retained in the driver log of the probe.
# Every probe reads the generated record of the probe fixture on its standard
# input, whichever item of its environment or handle the probe made wrong: a
# probe whose status is reported before that record is read reports the
# rejection of that item, and PRB7 and PRB4, which do read it, reach the call
# and the file operation their rows assert. The output handles the probe opened
# before this call, if any, are inherited as they stand and every handle is
# closed as soon as the driver returns, so the files the probe asserts are
# complete and no later step of the run holds one.
run_probe_driver() {
  local label="$1" expected="$2" log="$3"
  local status=0

  open_driver_input "$CASE_SAMPLE" "$EXIT_EXECUTE"
  run_and_tee "$EXIT_EXECUTE" "$log" timeout "$DRIVER_TIMEOUT_SECONDS" \
    "${BIN_DIR}/driver"
  status="$RUN_STATUS"
  close_driver_handles
  if ((status != expected)); then
    die "$EXIT_EXECUTE" \
      "probe ${label}: the driver exited ${status} where ${expected} is required" \
      "status ${status} is $(driver_status_text "$status")" \
      "status ${expected} is $(driver_status_text "$expected")" \
      "the driver log is ${log}"
  fi
  count_assertion
  emit_step \
    "probe ${label}: driver status ${status}, $(driver_status_text "$status")"
}

# Probe PRB7: the runtime is pointed at a directory below the build directory
# that holds no module, so the call of the first translated program cannot be
# resolved. The driver is handed both output handles, as a case is, so the
# evidence of a call that could not be made is written: the probe asserts the
# status, that the capture file records no chain effect at all, and that the
# post-chain record carries the bytes of the record the driver read.
probe_modules_absent() {
  local label="$1" expected="$2"
  local lower="" dir="" log="" empty=""
  local saved_library="" saved_preload=""

  lower="$(case_lower "$label")"
  dir="${RUN_DIR}/${lower}"
  log="${dir}/driver.log"
  empty="${BUILD_DIR}/${PROBE_DIR_NAME}/${PROBE_EMPTY_MODULES_NAME}"

  ensure_directory "$empty" "$EXIT_EXECUTE"
  assert_probe_no_modules "$label" "$empty"
  prepare_probe_directory "$lower"
  open_driver_output post "${dir}/commarea_post.dat" "$EXIT_EXECUTE"
  open_driver_output capture "${dir}/captures.txt" "$EXIT_EXECUTE"
  export_probe_environment "$label"

  saved_library="$COB_LIBRARY_PATH"
  saved_preload="$COB_PRE_LOAD"
  export COB_LIBRARY_PATH="$empty"
  export COB_PRE_LOAD=""
  run_probe_driver "$label" "$expected" "$log"
  export COB_LIBRARY_PATH="$saved_library"
  export COB_PRE_LOAD="$saved_preload"

  assert_probe_no_chain_evidence "$label" "$expected" "${dir}/captures.txt"
  assert_probe_record_unchanged "$label" "${dir}/commarea_post.dat" \
    "$CASE_SAMPLE"
}

# Probe PRB5A: the driver is handed no case at all, the item that names its run
# in every capture it writes. It is handed no output handle either, so a driver
# that reported this status after opening something would have opened a name of
# its own: the probe asserts the status, that neither output name exists
# afterwards, and that its run directory holds nothing but the driver log.
probe_missing_case() {
  local label="$1" expected="$2"
  local lower="" dir="" log=""

  lower="$(case_lower "$label")"
  dir="${RUN_DIR}/${lower}"
  log="${dir}/driver.log"

  prepare_probe_directory "$lower"
  export_probe_environment "$label"
  unset HARNESS_CASE
  run_probe_driver "$label" "$expected" "$log"

  assert_probe_output_absent "$label" "capture" "${dir}/captures.txt"
  assert_probe_output_absent "$label" "post-chain record" "${dir}/commarea_post.dat"
  assert_probe_directory_holds_log_only "$label" "$dir"
}

# Probe PRB5B: the driver is handed a case naming a path above the run
# directory, and no output handle. The probe asserts the status, that neither
# output name exists afterwards, that neither spelling of the escaped name was
# created beside the run directory, and that its run directory holds nothing but
# the driver log.
probe_escaping_case() {
  local label="$1" expected="$2"
  local lower="" dir="" log="" escaped=""

  lower="$(case_lower "$label")"
  dir="${RUN_DIR}/${lower}"
  log="${dir}/driver.log"
  escaped="${PROBE_ESCAPING_CASE##*/}"

  prepare_probe_directory "$lower"
  export_probe_environment "$label"
  export HARNESS_CASE="$PROBE_ESCAPING_CASE"
  run_probe_driver "$label" "$expected" "$log"

  assert_probe_output_absent "$label" "capture" "${dir}/captures.txt"
  assert_probe_output_absent "$label" "post-chain record" "${dir}/commarea_post.dat"
  assert_probe_path_absent "$label" "the escaped run directory" \
    "${BUILD_DIR}/${escaped}"
  assert_probe_path_absent "$label" "the escaped run directory" \
    "${BUILD_DIR}/$(case_lower "$escaped")"
  assert_probe_directory_holds_log_only "$label" "$dir"
}

# Probe PRB5C: the driver is handed an empty fixture, so it has no label for the
# record it is handed on its standard input, and no output handle. The probe
# asserts the status, that neither output name exists afterwards, and that its
# run directory holds nothing but the driver log.
probe_empty_fixture() {
  local label="$1" expected="$2"
  local lower="" dir="" log=""

  lower="$(case_lower "$label")"
  dir="${RUN_DIR}/${lower}"
  log="${dir}/driver.log"

  prepare_probe_directory "$lower"
  export_probe_environment "$label"
  export HARNESS_FIXTURE=""
  run_probe_driver "$label" "$expected" "$log"

  assert_probe_output_absent "$label" "capture" "${dir}/captures.txt"
  assert_probe_output_absent "$label" "post-chain record" "${dir}/commarea_post.dat"
  assert_probe_directory_holds_log_only "$label" "$dir"
}

# Probe PRB4: the driver is handed a valid environment and the post-chain handle
# on descriptor 3, and descriptor 4 is left closed, so the file operation that
# writes the capture evidence has no handle to write through and fails. The
# probe asserts the status, that nothing stands at the capture name, and that the
# post-chain name is still the file this script opened for it.
probe_capture_handle_absent() {
  local label="$1" expected="$2"
  local lower="" dir="" log="" post="" capt=""

  lower="$(case_lower "$label")"
  dir="${RUN_DIR}/${lower}"
  log="${dir}/driver.log"
  post="${dir}/commarea_post.dat"
  capt="${dir}/captures.txt"

  prepare_probe_directory "$lower"
  open_driver_output post "$post" "$EXIT_EXECUTE"
  export_probe_environment "$label"
  run_probe_driver "$label" "$expected" "$log"

  assert_probe_output_absent "$label" "capture" "$capt"
  assert_probe_opened_file "$label" "post-chain record" "$post"
}

# Runs every probe of the probe table in the order the table declares them, each
# in its own run directory, and records one summary line per probe. The probes
# run after the compile stage, so every module of the run exists, and before the
# cases, so no case inherits the environment a probe made wrong: each probe and
# each case exports its own environment before it starts.
stage_probes() {
  local row="" label="" item="" expected="" description=""

  emit_stage 4 "infrastructure probes"
  export_runtime_environment
  for row in "${HARNESS_PROBES[@]}"; do
    IFS='|' read -r label item expected description <<<"$row"
    emit_step "probe ${label}: ${item}, ${description}, expects status ${expected}"
    case "$label" in
      PRB7) probe_modules_absent "$label" "$expected" ;;
      PRB5A) probe_missing_case "$label" "$expected" ;;
      PRB5B) probe_escaping_case "$label" "$expected" ;;
      PRB5C) probe_empty_fixture "$label" "$expected" ;;
      PRB4) probe_capture_handle_absent "$label" "$expected" ;;
      *)
        die "$EXIT_EXECUTE" \
          "the probe table names ${label}, for which no probe is implemented"
        ;;
    esac
    SUMMARY_PROBE_LINES+=(
      "  probe ${label}: ${item}, ${description}, driver status ${expected} asserted"
      "    driver log:        ${RUN_DIR}/$(case_lower "$label")/driver.log"
    )
  done
  emit_step \
    "probes executed: ${#HARNESS_PROBES[@]}; assertions passed: ${TOTAL_ASSERTIONS}"
}

# --------------------------------------------------------------------------
# The oracle: expected values read out of the generated record
# --------------------------------------------------------------------------
# Every value this script asserts comes either from the generated record of the
# case, read here at the offset and length the field map documents, or from a
# seed this script exported. Nothing is read back from the expectations the
# driver was given, so a driver that agrees with itself still fails these
# checks when the chain moves the wrong bytes.

# Prints one field of a generated record, read at its documented offset and
# length, with the trailing blanks the record pads it with removed. A field the
# offset table does not carry, and a record the field cannot be read from, print
# a value no capture can match, so the assertion that reads it fails and names
# the field.
fixture_field() {
  local record="$1" name="$2"
  local value=""

  value="$(fixture_field_raw "$record" "$name")"
  value="${value%$'\r'}"
  while [[ -n "$value" && "$value" == *[[:space:]] ]]; do
    value="${value%?}"
  done
  printf '%s' "$value"
}

# Prints one field of a generated record without removing anything, so a
# fixed-width value keeps the blanks the record holds. The trailing marker
# printed by the reader keeps those blanks through the command substitution
# that returns them.
fixture_field_raw() {
  local record="$1" name="$2"
  local spec="" offset="" length="" value=""

  spec="${FIXTURE_FIELDS[$name]:-}"
  if [[ -z "$spec" ]]; then
    printf '%s' "<no record offset for ${name}>"
    return 0
  fi
  offset="${spec%% *}"
  length="${spec##* }"
  if ! value="$(
    dd if="$record" bs=1 skip="$((offset - 1))" count="$length" status=none 2>/dev/null
    printf 'x'
  )"; then
    printf '%s' "<unreadable ${name} in ${record}>"
    return 0
  fi
  printf '%s' "${value%x}"
}

# Prints one numeric field of a generated record as a number, with the leading
# zeros of its display form resolved. A field that is not numeric prints a value
# no capture can match.
fixture_number() {
  local record="$1" name="$2"
  local raw="" value=""

  raw="$(fixture_field "$record" "$name")"
  if ! value="$(number_value "$raw")"; then
    printf '%s' "<${name} is not numeric: ${raw}>"
    return 0
  fi
  printf '%s' "$value"
}

# Prints the value of a decimal string as a number, with leading zeros and an
# optional sign resolved. Fails when the value is not a decimal number.
number_value() {
  local raw="$1" digits="" sign=1

  if [[ ! "$raw" =~ ^([+-]?)([0-9]+)$ ]]; then
    return 1
  fi
  digits="${BASH_REMATCH[2]}"
  if [[ "${BASH_REMATCH[1]}" == "-" ]]; then
    sign=-1
  fi
  printf '%s' "$((sign * 10#$digits))"
}

# Prints the value of a decimal string in hundredths, accepting up to two
# decimal places. Fails when the value is not a decimal amount.
amount_hundredths() {
  local raw="$1" sign=1 whole="" fraction=""

  if [[ ! "$raw" =~ ^([+-]?)([0-9]+)(\.([0-9]{1,2}))?$ ]]; then
    return 1
  fi
  if [[ "${BASH_REMATCH[1]}" == "-" ]]; then
    sign=-1
  fi
  whole="${BASH_REMATCH[2]}"
  fraction="${BASH_REMATCH[4]:-0}"
  while ((${#fraction} < 2)); do
    fraction="${fraction}0"
  done
  printf '%s' "$((sign * (10#$whole * 100 + 10#$fraction)))"
}

# Prints the nine right-hand digits of one numeric field of a generated record.
# The chain narrows the ten-digit display fields of the COMMAREA into
# PIC S9(9) COMP host variables [base/src/lgapdb01.cbl:90-117], so a captured
# host value is compared against the significant digits of the record field
# rather than against its width. A field that is not numeric prints a value no
# capture can match.
fixture_number_narrowed() {
  local value=""

  value="$(fixture_number "$1" "$2")"
  if [[ ! "$value" =~ ^-?[0-9]+$ ]]; then
    printf '%s' "$value"
    return 0
  fi
  printf '%s' "$((value % 1000000000))"
}

# --------------------------------------------------------------------------
# Capture reading and assertions
# --------------------------------------------------------------------------
# Reads the value of one capture key into CAPTURE_VALUE, with trailing blanks
# and any carriage return removed, and records the key it read in CAPTURE_KEY.
# Fails when the key is absent from the file.
capture_value() {
  local file="$1" key="$2"
  local line=""

  CAPTURE_VALUE=""
  CAPTURE_KEY="$key"
  line="$(grep -m 1 -e "^${key}=" -- "$file" 2>/dev/null || true)"
  if [[ -z "$line" ]]; then
    return 1
  fi
  line="${line#"${key}="}"
  line="${line%$'\r'}"
  while [[ -n "$line" && "$line" == *[[:space:]] ]]; do
    line="${line%?}"
  done
  CAPTURE_VALUE="$line"
}

# Reads one capture entry into CAPTURE_VALUE and ends the run when the capture
# file carries none of its names. A name in upper case is the capture key
# itself; a name in lower case is an item of CAPTURE_KEY_NAMES and is read by
# the first of its names the file carries, so a case fails rather than passes
# when the driver stops emitting the item.
capture_require() {
  local label="$1" file="$2" name="$3"
  local -a candidates=()
  local candidate=""

  if [[ "$name" == *[[:lower:]]* ]]; then
    IFS=' ' read -r -a candidates <<<"${CAPTURE_KEY_NAMES[$name]:-}"
    if ((${#candidates[@]} == 0)); then
      die "$EXIT_EXECUTE" "no capture key is defined for the item ${name}"
    fi
  else
    candidates=("$name")
  fi
  for candidate in "${candidates[@]}"; do
    if capture_value "$file" "$candidate"; then
      return 0
    fi
  done
  die "$EXIT_EXECUTE" \
    "case ${label}: the capture file carries none of: $(join_with ", " "${candidates[@]}")" \
    "the capture file is ${file}" \
    "review the driver log beside it for the step that did not complete"
}

# Counts one assertion of the case being executed.
count_assertion() {
  CASE_ASSERTIONS=$((CASE_ASSERTIONS + 1))
  TOTAL_ASSERTIONS=$((TOTAL_ASSERTIONS + 1))
}

# Prints the hexadecimal form of the supplied text: two upper-case characters
# per byte, and nothing for an empty value. Written with shell builtins alone,
# so a value holding a blank or a control byte is never re-parsed by the shell.
# A blank becomes "20", which is how a padded field is compared whole.
text_to_hex() {
  local input="$1" out="" hex="" code=0 index=0

  for ((index = 0; index < ${#input}; index++)); do
    printf -v code '%d' "'${input:index:1}"
    code=$((code & 255))
    printf -v hex '%02X' "$code"
    out+="$hex"
  done
  printf '%s' "$out"
}

# Checks one hexadecimal capture entry against the value this script built out
# of the generated record: the entry carries exactly the required number of
# characters, every character is an upper-case hexadecimal digit, and the whole
# value matches. Nothing is removed from either side, so a byte the source pads
# with a blank is compared as "20", a value that carries fewer bytes than the
# source writes fails on its length, and the message names the first byte that
# differs.
assert_capture_hex() {
  local label="$1" file="$2" name="$3" expected="$4" length="$5"
  local index=0 byte=0

  if ((${#expected} != length)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: the expected ${name} holds ${#expected} characters where ${length} are required" \
      "the record of this case is ${CASE_SAMPLE}"
  fi
  capture_require "$label" "$file" "$name"
  if ((${#CAPTURE_VALUE} != length)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds ${#CAPTURE_VALUE} characters where ${length} are required" \
      "two characters carry one byte, so ${length} characters carry $((length / 2)) bytes" \
      "the capture file is ${file}"
  fi
  if [[ ! "$CAPTURE_VALUE" =~ ^[0-9A-F]+$ ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}', which is not an upper-case hexadecimal value" \
      "the capture file is ${file}"
  fi
  if [[ "$CAPTURE_VALUE" != "$expected" ]]; then
    for ((index = 0; index < length; index += 2)); do
      if [[ "${CAPTURE_VALUE:index:2}" != "${expected:index:2}" ]]; then
        byte=$((index / 2 + 1))
        break
      fi
    done
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} differs from the value the record carries at byte ${byte} of $((length / 2))" \
      "the capture holds ${CAPTURE_VALUE:index:2} there where ${expected:index:2} is required" \
      "captured: ${CAPTURE_VALUE}" \
      "required: ${expected}" \
      "the capture file is ${file} and the record is ${CASE_SAMPLE}"
  fi
  count_assertion
}

# Checks that one capture entry carries exactly the expected text.
assert_capture_text() {
  local label="$1" file="$2" name="$3" expected="$4"

  capture_require "$label" "$file" "$name"
  if [[ "$CAPTURE_VALUE" != "$expected" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}' where '${expected}' is required" \
      "the capture file is ${file}" \
      "review the driver log beside it for the values the chain produced"
  fi
  count_assertion
}

# Checks that one capture entry carries the expected number. The comparison is
# numeric, so a fixed-width value and an unpadded value of the same number both
# pass, a signed value is read with its sign, and a value that is not a number
# fails.
assert_capture_number() {
  local label="$1" file="$2" name="$3" expected_raw="$4"
  local actual="" expected=""

  if ! expected="$(number_value "$expected_raw")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the expected value of ${name} is '${expected_raw}', which is not a number" \
      "the record of this case is ${CASE_SAMPLE}"
  fi
  capture_require "$label" "$file" "$name"
  if ! actual="$(number_value "$CAPTURE_VALUE")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}', which is not a number" \
      "the capture file is ${file}"
  fi
  if ((actual != expected)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}' where ${expected} is required" \
      "the capture file is ${file}" \
      "review the driver log beside it for the values the chain produced"
  fi
  count_assertion
}

# Checks that one capture entry carries a number at or above the expected one.
assert_capture_at_least() {
  local label="$1" file="$2" name="$3" expected_raw="$4"
  local actual="" expected=""

  if ! expected="$(number_value "$expected_raw")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the expected floor of ${name} is '${expected_raw}', which is not a number"
  fi
  capture_require "$label" "$file" "$name"
  if ! actual="$(number_value "$CAPTURE_VALUE")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}', which is not a number" \
      "the capture file is ${file}"
  fi
  if ((actual < expected)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}' where ${expected} or more is required" \
      "the capture file is ${file}" \
      "review the driver log beside it for the values the chain produced"
  fi
  count_assertion
}

# Checks one amount capture against the value the generated record carries. The
# acceptance contract is an absolute delta of one hundredth or less; the six
# amount fields are whole-number display values, so a delta inside the
# tolerance still passes and is reported as unexpected.
assert_capture_amount() {
  local label="$1" file="$2" name="$3" expected_raw="$4"
  local expected=0 actual=0 delta=0

  if ! expected="$(amount_hundredths "$expected_raw")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the generated record holds '${expected_raw}' where an amount is required" \
      "the record is ${CASE_SAMPLE}"
  fi
  capture_require "$label" "$file" "$name"
  if ! actual="$(amount_hundredths "$CAPTURE_VALUE")"; then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}', which is not an amount" \
      "the capture file is ${file}"
  fi
  delta=$((actual - expected))
  if ((delta < 0)); then
    delta=$((-delta))
  fi
  if ((delta > AMOUNT_TOLERANCE_HUNDREDTHS)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}' where the record carries '${expected_raw}'" \
      "the delta of ${delta} hundredths is above the accepted ${AMOUNT_TOLERANCE_HUNDREDTHS}" \
      "the capture file is ${file} and the record is ${CASE_SAMPLE}"
  fi
  if ((delta != 0)); then
    emit_deviation \
      "case ${label}: ${CAPTURE_KEY} differs from the record by ${delta} hundredths, inside the accepted ${AMOUNT_TOLERANCE_HUNDREDTHS}"
  fi
  count_assertion
}

# Exports the settings every case and every probe runs under: the module
# directory, the line-sequential setting the full-length post-chain record is
# written under, and the module names handed to the runtime as a resolution aid.
# The case and the fixture are exported per case, by export_case_environment,
# which names no file: the three files a driver reads or writes reach it as the
# handles open_driver_input and open_driver_output opened.
export_runtime_environment() {
  export COB_LIBRARY_PATH="$BIN_DIR"
  export COB_LS_FIXED=1
  export COB_PRE_LOAD="$MODULE_PRELOAD"
  emit_step "COB_LIBRARY_PATH=${COB_LIBRARY_PATH}"
  emit_step "COB_LS_FIXED=${COB_LS_FIXED}"
}

# --------------------------------------------------------------------------
# One case of the case table
# --------------------------------------------------------------------------
# Loads the row of the case being executed into the CASE_ variables, then
# derives from it the values that follow from the source: the request id the
# chain reads, the routing letter it takes from that id
# [base/src/lgapdb01.cbl:184-207], the identity this case is seeded with, the
# SQLCODE the chain ends on, and whether the identity and timestamp reads of
# [base/src/lgapdb01.cbl:307-321] run at all, which they do only when the policy
# insert reports zero.
load_case_row() {
  local label="$1"
  local row=""

  if ! row="$(case_row "$label")"; then
    die "$EXIT_EXECUTE" "the case table carries no row for ${label}"
  fi
  IFS='|' read -r CASE_LABEL CASE_FIXTURE CASE_CALEN CASE_REQUEST_OVERRIDE \
    CASE_INJECT_POLICY CASE_INJECT_SUBTYPE CASE_INJECT_VSAM_RESP \
    CASE_INJECT_VSAM_RESP2 CASE_EXPECT_RC CASE_EXPECT_ABEND \
    CASE_EXPECT_PRODUCT CASE_EXPECT_POLICY_SQL CASE_EXPECT_VSAM \
    CASE_EXPECT_VALUES CASE_EXPECT_PRODUCT_VALUES CASE_EXPECT_DIAG \
    <<<"$row"

  CASE_SAMPLE="${SAMPLES_DIR}/commarea_${CASE_FIXTURE}.dat"
  if [[ ! -f "$CASE_SAMPLE" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${CASE_LABEL}: the generated sample record is missing: ${CASE_SAMPLE}" \
      "run this script without a case argument, or with ${CASE_LABEL}, to generate it"
  fi
  assert_readable_path "$CASE_SAMPLE" "$EXIT_EXECUTE"

  if [[ -n "$CASE_REQUEST_OVERRIDE" ]]; then
    CASE_REQUEST_ID="$CASE_REQUEST_OVERRIDE"
  else
    CASE_REQUEST_ID="$(fixture_field "$CASE_SAMPLE" request_id)"
  fi
  CASE_TYPE_LETTER="${CASE_REQUEST_ID:3:1}"
  CASE_POLICY_NUMBER="$(policy_number_for "$CASE_LABEL")"
  CASE_POLICY_PADDED="$(policy_number_padded "$CASE_POLICY_NUMBER")"

  if [[ "$CASE_EXPECT_POLICY_SQL" == "Y" && "$CASE_INJECT_POLICY" == "0" ]]; then
    CASE_EXPECT_IDENTITY="Y"
  else
    CASE_EXPECT_IDENTITY="N"
  fi

  if [[ "$CASE_EXPECT_PRODUCT" != "NONE" && "$CASE_INJECT_SUBTYPE" != "0" ]]; then
    CASE_EXPECT_SQLCODE="$CASE_INJECT_SUBTYPE"
  elif [[ "$CASE_EXPECT_POLICY_SQL" == "Y" && "$CASE_INJECT_POLICY" != "0" ]]; then
    CASE_EXPECT_SQLCODE="$CASE_INJECT_POLICY"
  else
    CASE_EXPECT_SQLCODE=0
  fi
}

# Exports the environment of one case: the case and the fixture the driver
# reports in its captures, the seeds it runs under, the COMMAREA length and
# request id it calls with, the failures it injects, and the outcome the driver
# is told to expect. Every item is set on every case, so no case inherits a
# value from the case before it. No item names a file: the record of the case,
# the post-chain record and the capture file reach the driver as the three
# handles this script opens, and a build root a caller happens to have exported
# is removed here so nothing of this run can be redirected through it.
export_case_environment() {
  unset HARNESS_BUILD_ROOT
  export HARNESS_CASE="$CASE_LABEL"
  export HARNESS_FIXTURE="$CASE_FIXTURE"
  export HARNESS_POLICY_NUMBER="$CASE_POLICY_NUMBER"
  export HARNESS_LASTCHANGED="$LASTCHANGED_SEED"
  export HARNESS_COMMAREA_LENGTH="$CASE_CALEN"
  export HARNESS_REQUEST_ID="$CASE_REQUEST_OVERRIDE"
  export HARNESS_INJECT_POLICY_SQLCODE="$CASE_INJECT_POLICY"
  export HARNESS_INJECT_SUBTYPE_SQLCODE="$CASE_INJECT_SUBTYPE"
  export HARNESS_INJECT_VSAM_RESP="$CASE_INJECT_VSAM_RESP"
  export HARNESS_INJECT_VSAM_RESP2="$CASE_INJECT_VSAM_RESP2"
  export HARNESS_EXPECT_RETURN_CODE="$CASE_EXPECT_RC"
  export HARNESS_EXPECT_ABEND="$CASE_EXPECT_ABEND"
  export HARNESS_EXPECT_PRODUCT="$CASE_EXPECT_PRODUCT"
  export HARNESS_EXPECT_POLICY_SQL="$CASE_EXPECT_POLICY_SQL"
  export HARNESS_EXPECT_VSAM="$CASE_EXPECT_VSAM"
  export HARNESS_EXPECT_VALUES="$CASE_EXPECT_VALUES"
  export HARNESS_EXPECT_PRODUCT_VALUES="$CASE_EXPECT_PRODUCT_VALUES"
  export HARNESS_EXPECT_DIAG_LINKS="$CASE_EXPECT_DIAG"
}

# Checks the post-chain record and the captures of one executed case: the
# record holds the full COMMAREA, the chain returned '00' without an abend,
# the driver passed every check of its own, the policy insert and the VSAM
# write were captured, and the product capture matches the product the case
# requests.
assert_post_record() {
  local label="$1" post="$2"
  local size=""

  CASE_POST_SIZE=""
  if [[ ! -f "$post" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the driver left no post-chain record at ${post}"
  fi
  assert_readable_path "$post" "$EXIT_EXECUTE"
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
  CASE_POST_SIZE="$size"
  count_assertion
}

# Checks that the capture file of the case carries every key the row requires,
# before any value is compared. A key the driver stops emitting therefore fails
# the case instead of removing an assertion from it.
assert_case_keys() {
  local label="$1" capt="$2"
  local key="" entry="" present_count=0
  local -a amount_keys=()

  if [[ ! -s "$capt" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: the driver left no capture content at ${capt}"
  fi
  assert_readable_path "$capt" "$EXIT_EXECUTE"

  local -a keys_wanted=("${CAPTURE_KEYS_BASE[@]}" "policy_count" "identity_count"
    "lastchanged_count" "motor_count" "commercial_count" "endowment_count"
    "house_count" "vsam_count" "abend_count" "policy_seq" "identity_seq"
    "lastchanged_seq" "motor_seq" "commercial_seq" "endowment_seq" "house_seq"
    "vsam_seq" "order_violation" "link_db2_calen" "link_vsam_calen")

  if [[ "$CASE_EXPECT_VALUES" == "Y" ]]; then
    keys_wanted+=("${CAPTURE_KEYS_VALUES[@]}")
  fi
  for entry in "${CAPTURE_KEYS_AMOUNTS[@]}"; do
    if [[ "${entry%%|*}" != "$CASE_REQUEST_ID" ]]; then
      continue
    fi
    IFS=' ' read -r -a amount_keys <<<"${entry##*|}"
    keys_wanted+=("${amount_keys[@]}")
  done
  if [[ "$CASE_EXPECT_POLICY_SQL" == "Y" ]]; then
    keys_wanted+=("${CAPTURE_KEYS_POLICY[@]}")
  fi
  if [[ "$CASE_EXPECT_IDENTITY" == "Y" ]]; then
    keys_wanted+=("${CAPTURE_KEYS_IDENTITY[@]}")
  fi
  if [[ "$CASE_EXPECT_VSAM" == "Y" ]]; then
    keys_wanted+=("${CAPTURE_KEYS_VSAM[@]}" "vsam_record")
    for entry in "${CAPTURE_KEYS_VSAM_HEX[@]}"; do
      keys_wanted+=("${entry%%|*}")
    done
  fi
  if [[ "$CASE_EXPECT_PRODUCT_VALUES" == "Y" ]]; then
    case "$CASE_EXPECT_PRODUCT" in
      MOTOR) keys_wanted+=("${CAPTURE_KEYS_MOTOR[@]}") ;;
      COMMERCIAL) keys_wanted+=("${CAPTURE_KEYS_COMMERCIAL[@]}") ;;
      HOUSE) keys_wanted+=("${CAPTURE_KEYS_HOUSE[@]}") ;;
      *)
        die "$EXIT_EXECUTE" \
          "case ${label}: the row asserts product values for product ${CASE_EXPECT_PRODUCT}, which carries no value list"
        ;;
    esac
  fi

  for key in "${keys_wanted[@]}"; do
    capture_require "$label" "$capt" "$key"
    present_count=$((present_count + 1))
  done
  count_assertion
  emit_step "case ${label}: capture keys present: ${present_count}"
}

# Ends the run when the CA-RETURN-CODE window of the generated record carries
# one of the codes the chain writes. The window holds the chain_populated_items
# seed of modernization/extraction/copybook_field_map.yml, which stands outside
# RETURN_CODE_DOMAIN, so the return-code assertion of a row that expects a code
# fails on a chain that did not write that window, and the row that expects no
# code asserts a surviving value no chain step produces.
assert_fixture_return_code_outside_domain() {
  local label="$1" record="$2"
  local observed="" code=""

  observed="$(fixture_field "$record" return_code)"
  for code in "${RETURN_CODE_DOMAIN[@]}"; do
    if [[ "$observed" == "$code" ]]; then
      die "$EXIT_EXECUTE" \
        "case ${label}: the generated record carries '${observed}' in the CA-RETURN-CODE window, which is a code the chain writes" \
        "the record is ${record}" \
        "the return-code assertion of this case cannot fail on a chain that leaves that window untouched" \
        "regenerate the record so the window holds the chain_populated_items seed of modernization/extraction/copybook_field_map.yml"
    fi
  done
  count_assertion
}

# Checks the outcome of the case: the length it called with, the request id the
# chain read, the return code, the abend state, the product the chain selected,
# the count and the ordinal of every captured statement, the order of those
# ordinals, the final SQLCODE, the diagnostic-link count and the two link
# witnesses. Counts and ordinals come from the row, so a duplicated, missing or
# reordered call fails the case.
assert_case_outcome() {
  local label="$1" capt="$2"
  local expected_rc="" entry="" product="" prefix="" count=0 flag="" selected=0

  # The label this script exported reaches the driver as HARNESS_CASE and comes
  # back whole in CASE, so the capture is compared with the label itself and a
  # value carrying part of it fails the case. The file is removed before the
  # driver runs, so its content belongs to this run of this case.
  capture_require "$label" "$capt" "CASE"
  if [[ "$CAPTURE_VALUE" != "$label" ]]; then
    die "$EXIT_EXECUTE" \
      "case ${label}: CASE holds '${CAPTURE_VALUE}' where the whole label of this case is required" \
      "the capture file is ${capt}"
  fi
  count_assertion

  # FIXTURE names the record the driver read. The record itself arrives on the
  # driver's standard input, so this label is what attributes the capture file to
  # the record this script redirected onto it.
  assert_capture_text "$label" "$capt" "FIXTURE" "$CASE_FIXTURE"

  # SAMPLE_RECORD_LENGTH is the width the driver measured in that record. The
  # driver refuses any other width before it calls the chain, and this
  # assertion states the width every later comparison of the case was decoded
  # at, whatever COMMAREA length the row calls with.
  assert_capture_number "$label" "$capt" "SAMPLE_RECORD_LENGTH" \
    "$RECORD_CHARACTERS"

  assert_capture_number "$label" "$capt" "EIBCALEN_AT_CALL" "$CASE_CALEN"
  assert_capture_text "$label" "$capt" "CA_REQUEST_ID" "$CASE_REQUEST_ID"
  assert_capture_text "$label" "$capt" "DRIVER_STATUS" "PASS"

  # FIXTURE_RETURN_CODE is the CA-RETURN-CODE window of the record the driver
  # read, published before the chain ran. It is asserted against the same window
  # read out of the generated record by this script, so the value the next
  # assertion is read against comes from the record and not from the driver
  # alone, and it is asserted to be none of the codes the chain writes, so a
  # window the chain left untouched cannot carry the code a row expects.
  assert_capture_text "$label" "$capt" "FIXTURE_RETURN_CODE" \
    "$(fixture_field "$CASE_SAMPLE" return_code)"
  assert_fixture_return_code_outside_domain "$label" "$CASE_SAMPLE"

  expected_rc="$CASE_EXPECT_RC"
  if [[ "$expected_rc" == "NONE" ]]; then
    expected_rc="$(fixture_field "$CASE_SAMPLE" return_code)"
  fi
  assert_capture_text "$label" "$capt" "CA_RETURN_CODE" "$expected_rc"

  if [[ "$CASE_EXPECT_ABEND" == "NONE" ]]; then
    assert_capture_text "$label" "$capt" "ABEND_PRESENT" "N"
    assert_capture_text "$label" "$capt" "ABEND_CODE" ""
    assert_capture_number "$label" "$capt" "abend_count" 0
  else
    assert_capture_text "$label" "$capt" "ABEND_PRESENT" "Y"
    assert_capture_text "$label" "$capt" "ABEND_CODE" "$CASE_EXPECT_ABEND"
    assert_capture_number "$label" "$capt" "abend_count" 1
  fi

  if [[ "$CASE_EXPECT_POLICY_SQL" == "Y" ]]; then
    assert_capture_text "$label" "$capt" "SQL_POLICY_PRESENT" "Y"
    assert_capture_number "$label" "$capt" "policy_count" 1
  else
    assert_capture_text "$label" "$capt" "SQL_POLICY_PRESENT" "N"
    assert_capture_number "$label" "$capt" "policy_count" 0
  fi
  if [[ "$CASE_EXPECT_IDENTITY" == "Y" ]]; then
    assert_capture_text "$label" "$capt" "SQL_IDENTITY_PRESENT" "Y"
    assert_capture_text "$label" "$capt" "SQL_LASTCHANGED_PRESENT" "Y"
    assert_capture_number "$label" "$capt" "identity_count" 1
    assert_capture_number "$label" "$capt" "lastchanged_count" 1
  else
    assert_capture_text "$label" "$capt" "SQL_IDENTITY_PRESENT" "N"
    assert_capture_text "$label" "$capt" "SQL_LASTCHANGED_PRESENT" "N"
    assert_capture_number "$label" "$capt" "identity_count" 0
    assert_capture_number "$label" "$capt" "lastchanged_count" 0
  fi

  # Exactly one product group is captured on a case that reaches a product
  # insert, and none on a case that does not.
  selected=0
  for entry in "${PRODUCT_GROUPS[@]}"; do
    product="${entry%%|*}"
    prefix="${entry##*|}"
    if [[ "$product" == "$CASE_EXPECT_PRODUCT" ]]; then
      count=1
      flag="Y"
      selected=$((selected + 1))
    else
      count=0
      flag="N"
    fi
    assert_capture_text "$label" "$capt" "${prefix}_PRESENT" "$flag"
    assert_capture_number "$label" "$capt" "$(case_lower "$product")_count" "$count"
  done
  if [[ "$CASE_EXPECT_PRODUCT" != "NONE" ]] && ((selected != 1)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: the row names product ${CASE_EXPECT_PRODUCT}, which the product group list does not carry"
  fi

  if [[ "$CASE_EXPECT_VSAM" == "Y" ]]; then
    assert_capture_text "$label" "$capt" "VSAM_PRESENT" "Y"
    assert_capture_number "$label" "$capt" "vsam_count" 1
  else
    assert_capture_text "$label" "$capt" "VSAM_PRESENT" "N"
    assert_capture_number "$label" "$capt" "vsam_count" 0
  fi

  assert_capture_number "$label" "$capt" "SQLCODE_LAST" "$CASE_EXPECT_SQLCODE"
  assert_capture_text "$label" "$capt" "order_violation" "N"

  if [[ "$CASE_EXPECT_DIAG" == "NONE" ]]; then
    assert_capture_number "$label" "$capt" "DIAG_LINK_COUNT" 0
  else
    assert_capture_at_least "$label" "$capt" "DIAG_LINK_COUNT" 1
  fi

  if [[ "$CASE_EXPECT_POLICY_SQL" == "Y" ]]; then
    assert_capture_number "$label" "$capt" "link_db2_calen" "$COMMAREA_LENGTH"
  else
    assert_capture_number "$label" "$capt" "link_db2_calen" 0
  fi
  if [[ "$CASE_EXPECT_VSAM" == "Y" ]]; then
    assert_capture_number "$label" "$capt" "link_vsam_calen" "$COMMAREA_LENGTH"
  else
    assert_capture_number "$label" "$capt" "link_vsam_calen" 0
  fi

  assert_case_ordinals "$label" "$capt"
}

# Checks the ordinals of the statements the case captured. The chain runs the
# policy insert, then the identity read, then the timestamp read, then the
# product insert, then the VSAM write [base/src/lgapdb01.cbl:218-250,261-321],
# so each captured ordinal stands above the one before it and every statement
# the row does not expect carries the ordinal zero.
assert_case_ordinals() {
  local label="$1" capt="$2"
  local item="" expected_present="" previous=0 ordinal=0 entry=""
  local -a chain=()

  chain=("policy_seq|$CASE_EXPECT_POLICY_SQL"
    "identity_seq|$CASE_EXPECT_IDENTITY"
    "lastchanged_seq|$CASE_EXPECT_IDENTITY")
  for entry in "${PRODUCT_GROUPS[@]}"; do
    if [[ "${entry%%|*}" == "$CASE_EXPECT_PRODUCT" ]]; then
      chain+=("$(case_lower "${entry%%|*}")_seq|Y")
    fi
  done
  chain+=("vsam_seq|$CASE_EXPECT_VSAM")

  for entry in "${chain[@]}"; do
    item="${entry%%|*}"
    expected_present="${entry##*|}"
    capture_require "$label" "$capt" "$item"
    if ! ordinal="$(number_value "$CAPTURE_VALUE")"; then
      die "$EXIT_EXECUTE" \
        "case ${label}: ${CAPTURE_KEY} holds '${CAPTURE_VALUE}', which is not an ordinal" \
        "the capture file is ${capt}"
    fi
    if [[ "$expected_present" == "Y" ]]; then
      if ((ordinal <= previous)); then
        die "$EXIT_EXECUTE" \
          "case ${label}: ${CAPTURE_KEY} holds ${ordinal}, not above the ${previous} of the statement before it" \
          "the chain runs policy, identity, timestamp, product, then the VSAM write" \
          "the capture file is ${capt}"
      fi
      previous="$ordinal"
    elif ((ordinal != 0)); then
      die "$EXIT_EXECUTE" \
        "case ${label}: ${CAPTURE_KEY} holds ${ordinal} where the row expects the statement not to run" \
        "the capture file is ${capt}"
    fi
    count_assertion
  done

  # Every product group the row does not select carries the ordinal zero.
  for entry in "${PRODUCT_GROUPS[@]}"; do
    if [[ "${entry%%|*}" == "$CASE_EXPECT_PRODUCT" ]]; then
      continue
    fi
    assert_capture_number "$label" "$capt" "$(case_lower "${entry%%|*}")_seq" 0
  done
}

# Checks the COMMAREA amounts of the case against the generated record it ran
# on: the payment of every case, and the product premiums of the request id the
# case calls with. The chain reads these amounts and writes none of them back,
# so every case carries them at the value its record holds, whatever the row
# expects of the rest of the run. Each is compared under the amount contract:
# an absolute delta of one hundredth or less passes and a non-zero delta is
# reported as unexpected.
assert_case_amounts() {
  local label="$1" capt="$2"
  local record="$CASE_SAMPLE"
  local entry="" key=""
  local -a amount_keys=()

  assert_capture_amount "$label" "$capt" "CA_PAYMENT" \
    "$(fixture_field "$record" payment)"

  for entry in "${CAPTURE_KEYS_AMOUNTS[@]}"; do
    if [[ "${entry%%|*}" != "$CASE_REQUEST_ID" ]]; then
      continue
    fi
    IFS=' ' read -r -a amount_keys <<<"${entry##*|}"
    for key in "${amount_keys[@]}"; do
      case "$key" in
        CA_M_PREMIUM)
          assert_capture_amount "$label" "$capt" "$key" \
            "$(fixture_field "$record" motor_premium)"
          ;;
        CA_B_FIREPREMIUM)
          assert_capture_amount "$label" "$capt" "$key" \
            "$(fixture_field "$record" commercial_firepremium)"
          ;;
        CA_B_CRIMEPREMIUM)
          assert_capture_amount "$label" "$capt" "$key" \
            "$(fixture_field "$record" commercial_crimepremium)"
          ;;
        CA_B_FLOODPREMIUM)
          assert_capture_amount "$label" "$capt" "$key" \
            "$(fixture_field "$record" commercial_floodpremium)"
          ;;
        CA_B_WEATHERPREMIUM)
          assert_capture_amount "$label" "$capt" "$key" \
            "$(fixture_field "$record" commercial_weatherpremium)"
          ;;
        *)
          die "$EXIT_EXECUTE" \
            "case ${label}: no record field is defined for the amount key ${key}"
          ;;
      esac
    done
  done
}

# Checks the values of the case against the generated record it ran on: the
# COMMAREA fields the chain leaves untouched, the values handed to the policy
# insert [base/src/lgapdb01.cbl:261-287], and the identity and timestamp the
# chain reads back [base/src/lgapdb01.cbl:307-321], which equal the two seeds
# this script exported.
assert_case_values() {
  local label="$1" capt="$2"
  local record="$CASE_SAMPLE"

  assert_capture_text "$label" "$capt" "CA_CUSTOMER_NUM" \
    "$(fixture_field "$record" customer_num)"
  assert_capture_text "$label" "$capt" "CA_ISSUE_DATE" \
    "$(fixture_field "$record" issue_date)"
  assert_capture_text "$label" "$capt" "CA_EXPIRY_DATE" \
    "$(fixture_field "$record" expiry_date)"
  assert_capture_text "$label" "$capt" "CA_BROKERID" \
    "$(fixture_field "$record" brokerid)"
  assert_capture_text "$label" "$capt" "CA_BROKERSREF" \
    "$(fixture_field "$record" brokersref)"

  if [[ "$CASE_EXPECT_IDENTITY" == "Y" ]]; then
    assert_capture_text "$label" "$capt" "CA_POLICY_NUM" "$CASE_POLICY_PADDED"
    assert_capture_text "$label" "$capt" "CA_LASTCHANGED" "$LASTCHANGED_SEED"
  else
    assert_capture_text "$label" "$capt" "CA_POLICY_NUM" \
      "$(fixture_field "$record" policy_num)"
    assert_capture_text "$label" "$capt" "CA_LASTCHANGED" \
      "$(fixture_field "$record" lastchanged)"
  fi

  if [[ "$CASE_EXPECT_POLICY_SQL" != "Y" ]]; then
    return 0
  fi

  assert_capture_number "$label" "$capt" "SQL_POLICY_CUSTOMERNUM" \
    "$(fixture_number_narrowed "$record" customer_num)"
  assert_capture_text "$label" "$capt" "SQL_POLICY_ISSUEDATE" \
    "$(fixture_field "$record" issue_date)"
  assert_capture_text "$label" "$capt" "SQL_POLICY_EXPIRYDATE" \
    "$(fixture_field "$record" expiry_date)"
  assert_capture_text "$label" "$capt" "SQL_POLICY_POLICYTYPE" "$CASE_TYPE_LETTER"
  assert_capture_number "$label" "$capt" "SQL_POLICY_BROKERID" \
    "$(fixture_number_narrowed "$record" brokerid)"
  assert_capture_text "$label" "$capt" "SQL_POLICY_BROKERSREF" \
    "$(fixture_field "$record" brokersref)"
  assert_capture_amount "$label" "$capt" "SQL_POLICY_PAYMENT" \
    "$(fixture_field "$record" payment)"

  if [[ "$CASE_EXPECT_IDENTITY" == "Y" ]]; then
    assert_capture_number "$label" "$capt" "SQL_POLICY_ASSIGNED_NUMBER" \
      "$CASE_POLICY_NUMBER"
    assert_capture_text "$label" "$capt" "SQL_POLICY_ASSIGNED_LASTCHANGED" \
      "$LASTCHANGED_SEED"
    # The timestamp read selects on the identity the read before it returned
    # [base/src/lgapdb01.cbl:315-321], so its predicate host carries that value.
    assert_capture_number "$label" "$capt" "SQL_LASTCHANGED_POLICYNUM" \
      "$CASE_POLICY_NUMBER"
  fi
}

# Checks the product values of the case against the generated record: the ten
# motor values [base/src/lgapdb01.cbl:440-481] or the commercial values
# [base/src/lgapdb01.cbl:486-555], with the premium of each product compared
# under the amount contract. Every value the row forbids is checked as absent by
# assert_case_outcome through the count of its group.
assert_case_product_values() {
  local label="$1" capt="$2"
  local record="$CASE_SAMPLE"

  case "$CASE_EXPECT_PRODUCT" in
    MOTOR)
      assert_capture_number "$label" "$capt" "SQL_MOTOR_POLICYNUM" \
        "$CASE_POLICY_NUMBER"
      assert_capture_text "$label" "$capt" "SQL_MOTOR_MAKE" \
        "$(fixture_field "$record" motor_make)"
      assert_capture_text "$label" "$capt" "SQL_MOTOR_MODEL" \
        "$(fixture_field "$record" motor_model)"
      assert_capture_number "$label" "$capt" "SQL_MOTOR_VALUE" \
        "$(fixture_number "$record" motor_value)"
      assert_capture_text "$label" "$capt" "SQL_MOTOR_REGNUMBER" \
        "$(fixture_field "$record" motor_regnumber)"
      assert_capture_text "$label" "$capt" "SQL_MOTOR_COLOUR" \
        "$(fixture_field "$record" motor_colour)"
      assert_capture_number "$label" "$capt" "SQL_MOTOR_CC" \
        "$(fixture_number "$record" motor_cc)"
      assert_capture_text "$label" "$capt" "SQL_MOTOR_MANUFACTURED" \
        "$(fixture_field "$record" motor_manufactured)"
      assert_capture_amount "$label" "$capt" "SQL_MOTOR_PREMIUM" \
        "$(fixture_field "$record" motor_premium)"
      assert_capture_number "$label" "$capt" "SQL_MOTOR_ACCIDENTS" \
        "$(fixture_number "$record" motor_accidents)"
      ;;
    COMMERCIAL)
      assert_capture_number "$label" "$capt" "SQL_COMMERCIAL_POLICYNUM" \
        "$CASE_POLICY_NUMBER"
      # RequestDate carries CA-LASTCHANGED, StartDate CA-ISSUE-DATE and
      # RenewalDate CA-EXPIRY-DATE [base/src/lgapdb01.cbl:522-525].
      if [[ "$CASE_EXPECT_IDENTITY" == "Y" ]]; then
        assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_REQUESTDATE" \
          "$LASTCHANGED_SEED"
      else
        assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_REQUESTDATE" \
          "$(fixture_field "$record" lastchanged)"
      fi
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_STARTDATE" \
        "$(fixture_field "$record" issue_date)"
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_RENEWALDATE" \
        "$(fixture_field "$record" expiry_date)"
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_ADDRESS" \
        "$(fixture_field "$record" commercial_address)"
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_ZIPCODE" \
        "$(fixture_field "$record" commercial_postcode)"
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_LATITUDEN" \
        "$(fixture_field "$record" commercial_latitude)"
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_LONGITUDEW" \
        "$(fixture_field "$record" commercial_longitude)"
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_CUSTOMER" \
        "$(fixture_field "$record" commercial_customer)"
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_PROPERTYTYPE" \
        "$(fixture_field "$record" commercial_proptype)"
      assert_capture_number "$label" "$capt" "SQL_COMMERCIAL_FIREPERIL" \
        "$(fixture_number "$record" commercial_fireperil)"
      assert_capture_amount "$label" "$capt" "SQL_COMMERCIAL_FIREPREMIUM" \
        "$(fixture_field "$record" commercial_firepremium)"
      assert_capture_number "$label" "$capt" "SQL_COMMERCIAL_CRIMEPERIL" \
        "$(fixture_number "$record" commercial_crimeperil)"
      assert_capture_amount "$label" "$capt" "SQL_COMMERCIAL_CRIMEPREMIUM" \
        "$(fixture_field "$record" commercial_crimepremium)"
      assert_capture_number "$label" "$capt" "SQL_COMMERCIAL_FLOODPERIL" \
        "$(fixture_number "$record" commercial_floodperil)"
      assert_capture_amount "$label" "$capt" "SQL_COMMERCIAL_FLOODPREMIUM" \
        "$(fixture_field "$record" commercial_floodpremium)"
      assert_capture_number "$label" "$capt" "SQL_COMMERCIAL_WEATHERPERIL" \
        "$(fixture_number "$record" commercial_weatherperil)"
      assert_capture_amount "$label" "$capt" "SQL_COMMERCIAL_WEATHERPREMIUM" \
        "$(fixture_field "$record" commercial_weatherpremium)"
      assert_capture_number "$label" "$capt" "SQL_COMMERCIAL_STATUS" \
        "$(fixture_number "$record" commercial_status)"
      assert_capture_text "$label" "$capt" "SQL_COMMERCIAL_REJECTIONREASON" \
        "$(fixture_field "$record" commercial_rejectreason)"
      ;;
    HOUSE)
      # The seven host values of the block at
      # [base/src/lgapdb01.cbl:409-425]. Bedrooms and value reach it through
      # the integer host variables of [base/src/lgapdb01.cbl:405-406], so both
      # are compared as numbers; the other four carry the characters of the
      # record.
      assert_capture_number "$label" "$capt" "SQL_HOUSE_POLICYNUM" \
        "$CASE_POLICY_NUMBER"
      assert_capture_text "$label" "$capt" "SQL_HOUSE_PROPERTYTYPE" \
        "$(fixture_field "$record" house_proptype)"
      assert_capture_number "$label" "$capt" "SQL_HOUSE_BEDROOMS" \
        "$(fixture_number "$record" house_bedrooms)"
      assert_capture_number "$label" "$capt" "SQL_HOUSE_VALUE" \
        "$(fixture_number "$record" house_value)"
      assert_capture_text "$label" "$capt" "SQL_HOUSE_HOUSENAME" \
        "$(fixture_field "$record" house_name)"
      assert_capture_text "$label" "$capt" "SQL_HOUSE_HOUSENUMBER" \
        "$(fixture_field "$record" house_number)"
      assert_capture_text "$label" "$capt" "SQL_HOUSE_POSTCODE" \
        "$(fixture_field "$record" house_postcode)"
      ;;
    *)
      die "$EXIT_EXECUTE" \
        "case ${label}: no product value list is defined for ${CASE_EXPECT_PRODUCT}"
      ;;
  esac
}

# Checks the VSAM write of the case: the file name, the record length, the key
# length, the response the write returned, the three key parts in the order the
# projection builds them [base/src/lgapvs01.cbl:99-101], the whole 21-byte key,
# and the whole 64-byte record image against the projection the source declares
# [base/src/lgapvs01.cbl:25-51,103-131].
#
# The image, its 43-byte product projection and its 21-byte key are compared in
# their hexadecimal form, byte for byte, against the image this script builds
# out of the generated record of the case. Every byte of all 64 takes part: the
# blanks the projection pads a shorter field with are compared as "20" rather
# than removed, so a record whose last bytes are wrong, and a captured value
# that carries fewer bytes than the source writes, both fail. The capture also
# carries the image the driver derived for itself, which is compared against the
# same expected value, so the two oracles are compared with each other as well.
assert_case_vsam() {
  local label="$1" capt="$2"
  local record="$CASE_SAMPLE"
  local customer="" key="" image="" payload="" name=""

  customer="$(fixture_field_raw "$record" customer_num)"
  key="${CASE_TYPE_LETTER}${customer}${CASE_POLICY_PADDED}"

  assert_capture_text "$label" "$capt" "VSAM_FILE" "$VSAM_FILE_NAME"
  assert_capture_number "$label" "$capt" "VSAM_LENGTH" "$VSAM_RECORD_LENGTH"
  assert_capture_number "$label" "$capt" "VSAM_KEYLENGTH" "$VSAM_KEY_LENGTH"
  assert_capture_number "$label" "$capt" "VSAM_RESP" "$CASE_INJECT_VSAM_RESP"
  assert_capture_text "$label" "$capt" "VSAM_REQUEST_ID" "$CASE_TYPE_LETTER"
  assert_capture_text "$label" "$capt" "VSAM_CUSTOMER_NUM" "$customer"
  assert_capture_text "$label" "$capt" "VSAM_POLICY_NUM" "$CASE_POLICY_PADDED"
  if ((${#key} != VSAM_KEY_LENGTH)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: the expected key holds ${#key} characters where ${VSAM_KEY_LENGTH} are required" \
      "the key is the request-type letter, the customer number and the policy number"
  fi
  assert_capture_text "$label" "$capt" "VSAM_KEY" "$key"
  assert_capture_text "$label" "$capt" "VSAM_RID_KEY" "$key"
  # The RIDFLD operand carries the same three parts in the same order as the
  # opening of the record [base/src/lgapvs01.cbl:26-29,99-101], and the
  # expected key the driver derived for itself carries them too.
  assert_capture_text "$label" "$capt" "VSAM_RID_REQUEST_ID" "$CASE_TYPE_LETTER"
  assert_capture_text "$label" "$capt" "VSAM_RID_CUSTOMER_NUM" "$customer"
  assert_capture_text "$label" "$capt" "VSAM_RID_POLICY_NUM" "$CASE_POLICY_PADDED"
  assert_capture_text "$label" "$capt" "VSAM_KEY_EXPECTED" "$key"

  # The 43-byte projection of the product the request id routes to. Each field
  # is copied at the width the projection declares for it, so a COMMAREA field
  # wider than its counterpart contributes only its opening characters
  # [base/src/lgapvs01.cbl:30-51].
  case "$CASE_EXPECT_PRODUCT" in
    MOTOR)
      payload="$(fixture_field_raw "$record" motor_make)"
      payload+="$(fixture_field_raw "$record" motor_model)"
      payload+="$(fixture_field_raw "$record" motor_value)"
      payload+="$(fixture_field_raw "$record" motor_regnumber)"
      ;;
    COMMERCIAL)
      payload="$(fixture_field_raw "$record" commercial_postcode)"
      payload+="$(fixture_field_raw "$record" commercial_status)"
      name="$(fixture_field_raw "$record" commercial_customer)"
      payload+="${name:0:31}"
      ;;
    HOUSE)
      payload="$(fixture_field_raw "$record" house_proptype)"
      payload+="$(fixture_field_raw "$record" house_bedrooms)"
      payload+="$(fixture_field_raw "$record" house_value)"
      payload+="$(fixture_field_raw "$record" house_postcode)"
      name="$(fixture_field_raw "$record" house_name)"
      payload+="${name:0:9}"
      ;;
    NONE)
      # A request id the projection does not recognise leaves the product area
      # blank [base/src/lgapvs01.cbl:130-131].
      printf -v payload '%-*s' "$VSAM_PAYLOAD_LENGTH" ""
      ;;
    *)
      die "$EXIT_EXECUTE" \
        "case ${label}: no record image is defined for product ${CASE_EXPECT_PRODUCT}"
      ;;
  esac
  if ((${#payload} != VSAM_PAYLOAD_LENGTH)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: the expected product projection holds ${#payload} characters where ${VSAM_PAYLOAD_LENGTH} are required" \
      "the projection of ${CASE_EXPECT_PRODUCT} fills the 43 bytes that follow the key"
  fi
  image="${key}${payload}"
  if ((${#image} != VSAM_RECORD_LENGTH)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: the expected record image holds ${#image} characters where ${VSAM_RECORD_LENGTH} are required" \
      "the image is the 21-byte key and the 43-byte product projection"
  fi

  assert_capture_hex "$label" "$capt" "VSAM_RECORD_HEX" \
    "$(text_to_hex "$image")" "$VSAM_RECORD_HEX_LENGTH"
  assert_capture_hex "$label" "$capt" "VSAM_RECORD_EXPECTED_HEX" \
    "$(text_to_hex "$image")" "$VSAM_RECORD_HEX_LENGTH"
  assert_capture_hex "$label" "$capt" "VSAM_PAYLOAD_HEX" \
    "$(text_to_hex "$payload")" "$VSAM_PAYLOAD_HEX_LENGTH"
  assert_capture_hex "$label" "$capt" "VSAM_RID_KEY_HEX" \
    "$(text_to_hex "$key")" "$VSAM_KEY_HEX_LENGTH"

  # The same image, its projection and the projection the driver derived, each
  # as text. The capture file carries a text value without its trailing blanks,
  # so these assertions stand beside the hexadecimal ones rather than in place
  # of them.
  while [[ -n "$image" && "$image" == *[[:space:]] ]]; do
    image="${image%?}"
  done
  while [[ -n "$payload" && "$payload" == *[[:space:]] ]]; do
    payload="${payload%?}"
  done
  assert_capture_text "$label" "$capt" "vsam_record" "$image"
  assert_capture_text "$label" "$capt" "VSAM_PAYLOAD" "$payload"
  assert_capture_text "$label" "$capt" "VSAM_PAYLOAD_EXPECTED" "$payload"
  assert_capture_text "$label" "$capt" "VSAM_PAYLOAD_DERIVED" "Y"
}

# Checks everything the row of the case asserts: the post-chain record, the
# required capture keys, the outcome and cardinality, the values, the product
# values and the VSAM write.
assert_case_results() {
  local label="$1" post="$2" capt="$3"

  CASE_ASSERTIONS=0
  assert_post_record "$label" "$post"
  assert_case_keys "$label" "$capt"
  assert_case_outcome "$label" "$capt"
  assert_case_amounts "$label" "$capt"
  if [[ "$CASE_EXPECT_VALUES" == "Y" ]]; then
    assert_case_values "$label" "$capt"
  fi
  if [[ "$CASE_EXPECT_PRODUCT_VALUES" == "Y" ]]; then
    assert_case_product_values "$label" "$capt"
  fi
  if [[ "$CASE_EXPECT_VSAM" == "Y" ]]; then
    assert_case_vsam "$label" "$capt"
  fi
  emit_step \
    "case ${label}: post-chain record ${CASE_POST_SIZE} bytes, ${CASE_ASSERTIONS} assertions passed"
}

# Runs the driver once for one case and asserts the row of the case table
# against the generated record it ran on. The identity and timestamp seeds are
# the deterministic values the preflight resolved, and the run is bounded in
# time. The record of the case, the post-chain record and the capture file are
# opened here, each after its path has been refused as a name this script does
# not own, each checked on the descriptor that was opened rather than on the
# name again, and all three are handed to the driver across the exec and closed
# as soon as it returns: the driver names none of the three, so an entry that
# appears at one of those names while it runs is written through by nothing.
# Every non-zero driver status fails the case; the statuses a wrong environment
# or a withheld handle produces are asserted by the probes of stage 4, which are
# not cases.
execute_case() {
  local label="$1"
  local lower="" dir="" post="" capt="" log=""
  local status=0 returned="" assigned=""

  load_case_row "$label"
  lower="$(case_lower "$label")"
  dir="${RUN_DIR}/${lower}"
  post="${dir}/commarea_post.dat"
  capt="${dir}/captures.txt"
  log="${dir}/driver.log"

  ensure_directory "$dir" "$EXIT_EXECUTE"
  create_private_file "$log" "$EXIT_EXECUTE"
  open_driver_output post "$post" "$EXIT_EXECUTE"
  open_driver_output capture "$capt" "$EXIT_EXECUTE"

  export_case_environment

  emit_step \
    "case ${label}: fixture ${CASE_FIXTURE}, request id ${CASE_REQUEST_ID}, commarea length ${CASE_CALEN}, policy seed ${CASE_POLICY_NUMBER}"
  emit_step \
    "case ${label}: injections policy ${CASE_INJECT_POLICY}, subtype ${CASE_INJECT_SUBTYPE}, vsam resp ${CASE_INJECT_VSAM_RESP}/${CASE_INJECT_VSAM_RESP2}"
  emit_step \
    "case ${label}: expects return ${CASE_EXPECT_RC}, abend ${CASE_EXPECT_ABEND}, product ${CASE_EXPECT_PRODUCT}, policy sql ${CASE_EXPECT_POLICY_SQL}, vsam ${CASE_EXPECT_VSAM}, diag ${CASE_EXPECT_DIAG}"
  open_driver_input "$CASE_SAMPLE" "$EXIT_EXECUTE"
  run_and_tee "$EXIT_EXECUTE" "$log" timeout "$DRIVER_TIMEOUT_SECONDS" \
    "${BIN_DIR}/driver"
  status="$RUN_STATUS"
  close_driver_handles
  if ((status != 0)); then
    die "$EXIT_EXECUTE" \
      "case ${label}: the driver exited ${status}: $(driver_status_text "$status")" \
      "the driver log is ${log}" \
      "the capture file, when the driver reached it, is ${capt}"
  fi

  assert_case_results "$label" "$post" "$capt"

  capture_value "$capt" "CA_RETURN_CODE" || true
  returned="$CAPTURE_VALUE"
  assigned="unavailable"
  if capture_value "$capt" "SQL_POLICY_ASSIGNED_NUMBER"; then
    assigned="$CAPTURE_VALUE"
  fi
  SUMMARY_CASE_LINES+=(
    "  case ${label}: return code ${returned}, driver status ${status}, policy number ${assigned}, assertions ${CASE_ASSERTIONS}"
    "    post-chain record: ${post}"
    "    captures:          ${capt}"
    "    driver log:        ${log}"
  )
}

# Executes every selected case under one exported runtime environment, then
# closes the stage with the source guard. Each case runs in its own process with
# its own run directory, so no case reads a file or an EXTERNAL value another
# case left behind.
stage_execute() {
  local label=""

  emit_stage 5 "execute"
  export_runtime_environment
  for label in "${SELECTED_CASES[@]}"; do
    execute_case "$label"
  done
  emit_step \
    "cases executed: ${#SELECTED_CASES[@]}; assertions passed: ${TOTAL_ASSERTIONS}"
  run_source_guard "harness-execute"
}

# --------------------------------------------------------------------------
# Stage 6: evidence and summary
# --------------------------------------------------------------------------
# Stage 6 runs the source guard as the final gate, collects the evidence of this
# run in the staging directory of the run, writes the manifest of what it
# collected, repeats the replacement over a directory of its own under the build
# tree, and only then replaces the published set in the validation artifacts
# directory: every name this script owns there is removed, the manifest first,
# the staged files are placed under the names the manifest carries, and the
# manifest is placed last. The set published is the five stage files, the
# manifest, and the driver log, the capture file and the post-chain record of
# each success case this run executed; the names of a success case it did not
# execute are removed with the rest. The set is then read back and required to
# match the manifest published with it, name for name and digest for digest.
# Nothing is published before every selected case, every probe and that final
# gate have passed, so a run that fails at any point leaves the published
# evidence exactly as it stands, and a run that succeeds leaves a set that
# describes itself alone.

# Copies one file of this run into the staging directory under the name it is to
# be published as, and records the pair for the publication step.
stage_artifact() {
  local source="$1" name="$2"
  local staged="${STAGING_DIR}/${name}"

  if [[ ! -f "$source" ]]; then
    die "$EXIT_EVIDENCE" \
      "the file to retain is missing: ${source}" \
      "review the stage logs under ${LOGS_DIR} for the step that did not complete"
  fi
  assert_readable_path "$source" "$EXIT_EVIDENCE"
  create_private_file "$staged" "$EXIT_EVIDENCE"
  if ! cat -- "$source" >"$staged"; then
    die "$EXIT_EVIDENCE" "unable to write ${staged} from ${source}"
  fi
  STAGED_ARTIFACTS+=("${staged}|${name}")
}

# Collects the evidence of this run: the translation log, the compile log, the
# translation report, the source baseline, the evidence log of the source guard,
# and the driver log, the capture file and the post-chain record of every success
# case that ran. The guard log is collected after the final gate has appended its
# block to it, so the copy published carries all four gate runs of this run. The
# staged pairs are the files of the published set, beside the manifest that
# describes them; every other name this script owns in the published directory is
# removed rather than published. The cases that are not success cases keep their
# log, capture file and post-chain record under the build tree, where the run
# directory of the case names them.
collect_evidence() {
  local name="" label="" lower="" candidate=""

  STAGED_ARTIFACTS=()
  for name in "${PUBLISHED_STAGE_ARTIFACTS[@]}"; do
    stage_artifact "${LOGS_DIR}/${name}" "$name"
  done
  for label in "${SUCCESS_CASES[@]}"; do
    for candidate in "${SELECTED_CASES[@]}"; do
      if [[ "$candidate" != "$label" ]]; then
        continue
      fi
      lower="$(case_lower "$label")"
      stage_artifact "${RUN_DIR}/${lower}/driver.log" "driver_${lower}.log"
      stage_artifact "${RUN_DIR}/${lower}/captures.txt" "captures_${lower}.txt"
      stage_artifact "${RUN_DIR}/${lower}/commarea_post.dat" \
        "commarea_post_${lower}.dat"
    done
  done
  emit_step "evidence staged: ${#STAGED_ARTIFACTS[@]} files in ${STAGING_DIR}"
}

# Prints every name this script publishes into, or removes from, the validation
# artifacts directory: the five stage files, the manifest, and the driver log,
# the capture file and the post-chain record of each success case of the case
# table. One name per line. A run publishes the subset its selection produced
# and removes the rest, so the published set holds no artifact of a success case
# that run did not execute.
evidence_owned_names() {
  local name="" label="" lower=""

  for name in "${PUBLISHED_STAGE_ARTIFACTS[@]}"; do
    printf '%s\n' "$name"
  done
  printf '%s\n' "$EVIDENCE_MANIFEST_NAME"
  for label in "${SUCCESS_CASES[@]}"; do
    lower="$(case_lower "$label")"
    printf '%s\n%s\n%s\n' "driver_${lower}.log" "captures_${lower}.txt" \
      "commarea_post_${lower}.dat"
  done
}

# Prints the success cases of this run's selection, comma separated, and prints
# nothing when the selection carries none. Those are the cases whose driver log,
# capture file and post-chain record the published set covers.
evidence_success_selection() {
  local label="" candidate=""
  local -a executed=()

  for label in "${SUCCESS_CASES[@]}"; do
    for candidate in "${SELECTED_CASES[@]}"; do
      if [[ "$candidate" == "$label" ]]; then
        executed+=("$label")
      fi
    done
  done
  if ((${#executed[@]} == 0)); then
    return 0
  fi
  join_with ", " "${executed[@]}"
}

# Prints the name of every entry standing in the supplied directory, one per
# line, hidden entries included. The globbing options it needs are set inside a
# subshell, so they do not outlive the call, and no external tool is invoked.
directory_entry_names() {
  local dir="$1"

  (
    shopt -s nullglob dotglob
    local path=""
    for path in "$dir"/*; do
      printf '%s\n' "${path##*/}"
    done
  )
}

# Reads the SHA-256 of one published file into EVIDENCE_DIGEST and reports a
# failure instead of ending the run: an absent name, a symbolic link, an entry
# that is not a regular file and an unreadable file each leave EVIDENCE_DIGEST
# empty and return 1. Used by the check that reads a published set back, which
# reports its verdict to its caller rather than ending the run itself.
published_digest() {
  local path="$1"
  local line=""

  EVIDENCE_DIGEST=""
  if [[ -L "$path" || ! -f "$path" ]]; then
    return 1
  fi
  if ! line="$(sha256sum -- "$path" 2>/dev/null)" || [[ -z "$line" ]]; then
    return 1
  fi
  EVIDENCE_DIGEST="${line%% *}"
  return 0
}

# Writes one evidence manifest: the provenance of this run as comment lines,
# then one "sha256sum" line per staged file under the name it is published as.
# The provenance names the run, the time the manifest was written, the case
# selection it describes, the success cases whose captures the set covers, the
# two seeds of the run, the measured tool versions, the source-guard verdict, the
# number of files in the set and the name that stands outside it. Every comment
# line carries a leading "#", which "sha256sum --check" skips, so the manifest
# checks the set as it stands. The manifest is published with the set and read
# back from the published directory afterwards.
#   1 path of the manifest
#   2 case selection this set describes
#   3 success cases the set covers, or "none"
#   4.. staged pairs "<staged path>|<published name>"
write_evidence_manifest() {
  local manifest="$1" selection="$2" covered="$3"
  shift 3
  local entry="" staged="" name="" digest="" stamp="" header=""

  if (($# == 0)); then
    die "$EXIT_EVIDENCE" "the evidence manifest ${manifest} would carry no file"
  fi
  if ! stamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')" || [[ -z "$stamp" ]]; then
    die "$EXIT_EVIDENCE" \
      "unable to read the current time for the evidence manifest: ${manifest}"
  fi

  header="# ${PROGRAM} evidence manifest: one run, one published set"$'\n'
  header+="# run identifier:      $(sanitize "$RUN_ID")"$'\n'
  header+="# written (UTC):       $(sanitize "$stamp")"$'\n'
  header+="# case selection:      $(sanitize "$selection")"$'\n'
  header+="# success captures:    $(sanitize "$covered")"$'\n'
  header+="# policy number seed:  $(sanitize "$POLICY_NUMBER_BASE")"$'\n'
  header+="# timestamp seed:      $(sanitize "$LASTCHANGED_SEED")"$'\n'
  header+="# cobc:                $(sanitize "$COBC_VERSION") (pinned ${COBC_VERSION_PINNED}, $(sanitize "$COBC_VERSION_VERDICT"))"$'\n'
  header+="# python:              $(sanitize "$PYTHON_VERSION")"$'\n'
  header+="# source guard:        $(sanitize "$GUARD_VERDICT") at ${GUARD_PASSES} of 4 points"$'\n'
  header+="# files in this set:   $(($# + 1)), this manifest included"$'\n'
  header+="# outside this set:    ${RUNTIME_VERSIONS_NAME}, the environment record of the checkout"$'\n'

  create_private_file "$manifest" "$EXIT_EVIDENCE"
  if ! printf '%s' "$header" >"$manifest"; then
    die "$EXIT_EVIDENCE" "unable to write the evidence manifest: ${manifest}"
  fi
  for entry in "$@"; do
    staged="${entry%%|*}"
    name="${entry##*|}"
    digest="$(hash_file "$staged" "$EXIT_EVIDENCE")"
    if ! printf '%s  %s\n' "$digest" "$name" >>"$manifest"; then
      die "$EXIT_EVIDENCE" "unable to append to the evidence manifest: ${manifest}"
    fi
  done
}

# Replaces the complete published set in the supplied directory. The manifest
# name is removed first, then every other name this script owns there, then the
# staged files are placed under the names the manifest carries and the manifest
# is placed last. A directory holding the manifest therefore holds the whole set
# that manifest describes, and a publication that stops part way leaves no
# manifest beside a partial set. publish_file replaces each name in one step. The
# leftover of an interrupted publication carries the name publish_file writes
# through and is removed with the set it belongs to. What was removed and what
# was placed is left in EVIDENCE_CLEARED and EVIDENCE_PLACED.
#   1 directory the set is published into
#   2 manifest of the set, already written
#   3.. staged pairs "<staged path>|<published name>"
publish_evidence_set() {
  local target_dir="$1" manifest="$2"
  shift 2
  local entry="" staged="" name="" path="" tracking="N"
  local -A set_names=()
  local -a owned=() present=()

  if (($# == 0)); then
    die "$EXIT_EVIDENCE" "the staged evidence list is empty"
  fi
  EVIDENCE_CLEARED=0
  EVIDENCE_PLACED=0
  if [[ "$target_dir" == "$ARTIFACTS_DIR" ]]; then
    tracking="Y"
    PUBLICATION_NAMES_TOTAL=$(($# + 1))
    PUBLICATION_NAMES_CLEARED=0
    PUBLICATION_NAMES_PUBLISHED=0
    PUBLICATION_STATE="clearing"
  fi
  for entry in "$@"; do
    set_names["${entry##*|}"]=1
  done

  mapfile -t present < <(directory_entry_names "$target_dir")
  for name in "${present[@]}"; do
    case "$name" in
      .publish-*)
        remove_output_path "${target_dir}/${name}" "$EXIT_EVIDENCE"
        EVIDENCE_CLEARED=$((EVIDENCE_CLEARED + 1))
        ;;
    esac
  done

  path="${target_dir}/${EVIDENCE_MANIFEST_NAME}"
  if [[ -e "$path" || -L "$path" ]]; then
    remove_output_path "$path" "$EXIT_EVIDENCE"
    EVIDENCE_CLEARED=$((EVIDENCE_CLEARED + 1))
  fi
  if [[ "$tracking" == "Y" ]]; then
    PUBLICATION_NAMES_CLEARED=$((PUBLICATION_NAMES_CLEARED + 1))
  fi
  mapfile -t owned < <(evidence_owned_names)
  for name in "${owned[@]}"; do
    if [[ -z "$name" || "$name" == "$EVIDENCE_MANIFEST_NAME" ]]; then
      continue
    fi
    path="${target_dir}/${name}"
    if [[ -e "$path" || -L "$path" ]]; then
      remove_output_path "$path" "$EXIT_EVIDENCE"
      EVIDENCE_CLEARED=$((EVIDENCE_CLEARED + 1))
    fi
    if [[ "$tracking" == "Y" ]]; then
      PUBLICATION_NAMES_CLEARED=$((PUBLICATION_NAMES_CLEARED + 1))
    fi
  done
  if [[ "$tracking" == "Y" ]]; then
    PUBLICATION_STATE="publishing"
  fi

  for entry in "$@"; do
    staged="${entry%%|*}"
    name="${entry##*|}"
    publish_file "$staged" "${target_dir}/${name}" "$EXIT_EVIDENCE"
    EVIDENCE_PLACED=$((EVIDENCE_PLACED + 1))
    if [[ "$tracking" == "Y" ]]; then
      PUBLICATION_NAMES_PUBLISHED=$((PUBLICATION_NAMES_PUBLISHED + 1))
    fi
  done
  publish_file "$manifest" "${target_dir}/${EVIDENCE_MANIFEST_NAME}" \
    "$EXIT_EVIDENCE"
  EVIDENCE_PLACED=$((EVIDENCE_PLACED + 1))
  if [[ "$tracking" == "Y" ]]; then
    PUBLICATION_NAMES_PUBLISHED=$((PUBLICATION_NAMES_PUBLISHED + 1))
  fi
}

# Reads one published set back and reports whether the directory holds exactly
# the set its manifest describes: the manifest is the one whose SHA-256 was
# supplied, it carries one digest line per staged name and no other, every
# published file matches its digest line, and no name this script owns stands
# there outside the manifest - so an artifact of a success case the run did not
# execute is a difference rather than part of the set. Names this script never
# writes, other than the environment record, are collected in EVIDENCE_FOREIGN
# for the caller to report. The verdict is returned rather than acted on: 0 when
# the set holds, 1 with the first difference in EVIDENCE_DIFFERENCE, so a caller
# can require either outcome.
#   1 directory the set was published into
#   2 SHA-256 of the manifest that describes the set
#   3.. staged pairs "<staged path>|<published name>"
verify_published_set() {
  local target_dir="$1" expected_manifest="$2"
  shift 2
  local expected_count=$#
  local manifest="${target_dir}/${EVIDENCE_MANIFEST_NAME}"
  local entry="" line="" name="" digest="" count=0
  local -A set_names=() stated=()
  local -a lines=() owned=() present=()

  EVIDENCE_DIFFERENCE=""
  EVIDENCE_FOREIGN=()
  for entry in "$@"; do
    set_names["${entry##*|}"]=1
  done

  if ! published_digest "$manifest"; then
    EVIDENCE_DIFFERENCE="the manifest of the set is $(path_kind "$manifest"): ${manifest}"
    return 1
  fi
  if [[ "$EVIDENCE_DIGEST" != "$expected_manifest" ]]; then
    EVIDENCE_DIFFERENCE="the manifest ${manifest} is not the one written for this set"
    return 1
  fi

  mapfile -t lines <"$manifest"
  for line in "${lines[@]}"; do
    case "$line" in
      '#'* | '')
        continue
        ;;
    esac
    if ((${#line} < 67)) || [[ "${line:64:2}" != "  " ]] ||
      [[ ! "${line:0:64}" =~ ^[0-9a-f]{64}$ ]]; then
      EVIDENCE_DIFFERENCE="the manifest ${manifest} carries a line that is no digest line: ${line}"
      return 1
    fi
    digest="${line:0:64}"
    name="${line:66}"
    if [[ -z "${set_names[$name]+set}" ]]; then
      EVIDENCE_DIFFERENCE="the manifest names ${name}, which this set does not carry"
      return 1
    fi
    if [[ -n "${stated[$name]+set}" ]]; then
      EVIDENCE_DIFFERENCE="the manifest names ${name} more than once"
      return 1
    fi
    stated["$name"]="$digest"
    count=$((count + 1))
  done
  if ((count != expected_count)); then
    EVIDENCE_DIFFERENCE="the manifest carries ${count} digest lines where ${expected_count} are required"
    return 1
  fi

  for name in "${!stated[@]}"; do
    if ! published_digest "${target_dir}/${name}"; then
      EVIDENCE_DIFFERENCE="the published file is $(path_kind "${target_dir}/${name}"): ${target_dir}/${name}"
      return 1
    fi
    if [[ "$EVIDENCE_DIGEST" != "${stated[$name]}" ]]; then
      EVIDENCE_DIFFERENCE="the published ${target_dir}/${name} does not match its manifest entry"
      return 1
    fi
  done

  mapfile -t owned < <(evidence_owned_names)
  for name in "${owned[@]}"; do
    if [[ -z "$name" || "$name" == "$EVIDENCE_MANIFEST_NAME" ||
      -n "${set_names[$name]+set}" ]]; then
      continue
    fi
    if [[ -e "${target_dir}/${name}" || -L "${target_dir}/${name}" ]]; then
      EVIDENCE_DIFFERENCE="${target_dir}/${name} stands beside the set, and the manifest does not name it"
      return 1
    fi
  done

  mapfile -t present < <(directory_entry_names "$target_dir")
  for name in "${present[@]}"; do
    if [[ -z "$name" || "$name" == "$EVIDENCE_MANIFEST_NAME" ||
      "$name" == "$RUNTIME_VERSIONS_NAME" || -n "${set_names[$name]+set}" ]]; then
      continue
    fi
    EVIDENCE_FOREIGN+=("$name")
  done
  return 0
}

# Creates one file of the publication check at the supplied path, holding the
# supplied line. The check compares content it wrote itself, so no file of the
# run is read or replaced by it.
write_check_file() {
  local path="$1" line="$2"

  create_private_file "$path" "$EXIT_EVIDENCE"
  if ! printf '%s\n' "$line" >"$path"; then
    die "$EXIT_EVIDENCE" "unable to write the publication check file: ${path}"
  fi
}

# Runs the publication contract of this script over a directory of its own under
# the staging tree of the run, so every run - whatever its command line selected
# - performs the replacement a run of one success case performs over the set of a
# full-table run. The simulated directory is filled with every name a full-table
# run publishes and with the environment record no run writes; a set covering the
# five stage files and the first success case alone is then published into it.
# The published set is required to match its manifest, the three names of the
# second success case are required to be gone, and the environment record is
# required to stand unchanged. A stale artifact of that second case is then
# planted and the read-back is required to reject the set, so a publication that
# left the evidence of an unexecuted success case standing fails this step
# instead of reaching the published directory.
check_publication_replacement() {
  local root="${STAGING_DIR}/${PUBLICATION_CHECK_NAME}"
  local published="${root}/published" staged="${root}/staged"
  local covered_case="" absent_case="" lower="" name="" manifest="" digest=""
  local record="" rejected=""
  local -a owned=() present=() pairs=() gone=()

  if ((${#SUCCESS_CASES[@]} < 2)); then
    die "$EXIT_EVIDENCE" \
      "the publication check requires two success cases; the case table names ${#SUCCESS_CASES[@]}"
  fi
  covered_case="${SUCCESS_CASES[0]}"
  absent_case="${SUCCESS_CASES[1]}"

  ensure_directory "$published" "$EXIT_EVIDENCE"
  ensure_directory "$staged" "$EXIT_EVIDENCE"
  mapfile -t present < <(directory_entry_names "$published")
  for name in "${present[@]}"; do
    if [[ -n "$name" ]]; then
      remove_output_path "${published}/${name}" "$EXIT_EVIDENCE"
    fi
  done

  mapfile -t owned < <(evidence_owned_names)
  for name in "${owned[@]}"; do
    if [[ -n "$name" ]]; then
      write_check_file "${published}/${name}" \
        "publication check: ${name} of an earlier run"
    fi
  done
  write_check_file "${published}/${RUNTIME_VERSIONS_NAME}" \
    "publication check: environment record of the checkout"
  record="$(hash_file "${published}/${RUNTIME_VERSIONS_NAME}" "$EXIT_EVIDENCE")"

  for name in "${PUBLISHED_STAGE_ARTIFACTS[@]}"; do
    write_check_file "${staged}/${name}" \
      "publication check: ${name} of run ${RUN_ID}"
    pairs+=("${staged}/${name}|${name}")
  done
  lower="$(case_lower "$covered_case")"
  for name in "driver_${lower}.log" "captures_${lower}.txt" \
    "commarea_post_${lower}.dat"; do
    write_check_file "${staged}/${name}" \
      "publication check: ${name} of run ${RUN_ID}"
    pairs+=("${staged}/${name}|${name}")
  done
  lower="$(case_lower "$absent_case")"
  gone=("driver_${lower}.log" "captures_${lower}.txt"
    "commarea_post_${lower}.dat")

  manifest="${staged}/${EVIDENCE_MANIFEST_NAME}"
  write_evidence_manifest "$manifest" \
    "publication check of a set covering ${covered_case}" "$covered_case" "${pairs[@]}"
  digest="$(hash_file "$manifest" "$EXIT_EVIDENCE")"
  publish_evidence_set "$published" "$manifest" "${pairs[@]}"

  if ! verify_published_set "$published" "$digest" "${pairs[@]}"; then
    die "$EXIT_EVIDENCE" \
      "the publication check did not leave the set its manifest describes" \
      "$EVIDENCE_DIFFERENCE" \
      "the directory it works in is ${published}"
  fi
  for name in "${gone[@]}"; do
    if [[ -e "${published}/${name}" || -L "${published}/${name}" ]]; then
      die "$EXIT_EVIDENCE" \
        "the publication check left ${name}, the evidence of ${absent_case}, which the set does not cover" \
        "the directory it works in is ${published}" \
        "a published set carries the evidence of the cases of its own run alone"
    fi
  done
  if [[ "$(hash_file "${published}/${RUNTIME_VERSIONS_NAME}" "$EXIT_EVIDENCE")" != "$record" ]]; then
    die "$EXIT_EVIDENCE" \
      "the publication check replaced ${RUNTIME_VERSIONS_NAME}, which stands outside every set" \
      "the directory it works in is ${published}"
  fi

  write_check_file "${published}/${gone[0]}" \
    "publication check: ${gone[0]} of an earlier run"
  if verify_published_set "$published" "$digest" "${pairs[@]}"; then
    die "$EXIT_EVIDENCE" \
      "the read-back accepted a set carrying ${gone[0]}, the evidence of ${absent_case}" \
      "the directory it works in is ${published}" \
      "a set carrying a name its manifest does not describe is not the set of one run"
  fi
  rejected="$EVIDENCE_DIFFERENCE"
  remove_output_path "${published}/${gone[0]}" "$EXIT_EVIDENCE"
  if ! verify_published_set "$published" "$digest" "${pairs[@]}"; then
    die "$EXIT_EVIDENCE" \
      "the publication check could not read the set back after the planted ${gone[0]} was removed" \
      "$EVIDENCE_DIFFERENCE" \
      "the directory it works in is ${published}"
  fi

  emit_step \
    "publication check: ${#pairs[@]} staged names and the manifest replaced the ${#owned[@]} of a full-table run in ${published}, the ${#gone[@]} names of ${absent_case} were removed, ${RUNTIME_VERSIONS_NAME} stood unchanged, and the read-back rejected a planted artifact: ${rejected}"
}

# Replaces the published set in the validation artifacts directory with the set
# this run staged and its manifest, then reads that set back against the
# manifest standing in it. A name this script owns there that this run did not
# publish is removed by the replacement, so nothing of an earlier run survives
# beside the set; a name this script never writes, other than the environment
# record of the checkout, is reported as a deviation naming it.
publish_evidence() {
  local manifest="${LOGS_DIR}/${EVIDENCE_MANIFEST_NAME}"
  local published="${ARTIFACTS_DIR}/${EVIDENCE_MANIFEST_NAME}"
  local digest="" entry="" name=""

  digest="$(hash_file "$manifest" "$EXIT_EVIDENCE")"
  publish_evidence_set "$ARTIFACTS_DIR" "$manifest" "${STAGED_ARTIFACTS[@]}"
  emit_step \
    "published names cleared: ${EVIDENCE_CLEARED}; files placed: ${EVIDENCE_PLACED}"
  if ! verify_published_set "$ARTIFACTS_DIR" "$digest" "${STAGED_ARTIFACTS[@]}"; then
    die "$EXIT_EVIDENCE" \
      "the published evidence in ${ARTIFACTS_DIR} is not the set this run produced" \
      "$EVIDENCE_DIFFERENCE" \
      "the manifest of this run is ${manifest}" \
      "publish the evidence again from ${STAGING_DIR}"
  fi

  PUBLICATION_STATE="published"

  SUMMARY_ARTIFACTS=()
  for entry in "${STAGED_ARTIFACTS[@]}"; do
    name="${entry##*|}"
    SUMMARY_ARTIFACTS+=("${ARTIFACTS_DIR}/${name}")
  done
  SUMMARY_ARTIFACTS+=("$published")
  for name in "${EVIDENCE_FOREIGN[@]}"; do
    emit_deviation \
      "${ARTIFACTS_DIR}/${name} stands beside the published set and no run of this script writes it"
  done
  emit_step \
    "artifacts published: ${#SUMMARY_ARTIFACTS[@]} files in ${ARTIFACTS_DIR}, each named by ${published}"
}

# Runs the source guard as the final gate of the run, then collects the evidence
# of the run in the staging directory, writes the manifest that describes it,
# runs the publication check, and replaces the published set. The gate runs first
# so the evidence log it appends its fourth block to is complete before that log
# is collected, and it still decides whether anything is published at all: a gate
# that does not pass ends the run here, with nothing collected, nothing removed
# and the published evidence of the previous run exactly as it stands.
stage_evidence() {
  local manifest="${LOGS_DIR}/${EVIDENCE_MANIFEST_NAME}"
  local selection="" covered=""

  emit_stage 6 "evidence"
  run_source_guard "harness-final"
  collect_evidence
  selection="$(join_with ", " "${SELECTED_CASES[@]}")"
  covered="$(evidence_success_selection)"
  write_evidence_manifest "$manifest" "$selection" "${covered:-none}" \
    "${STAGED_ARTIFACTS[@]}"
  emit_step "evidence manifest: ${manifest}"
  check_publication_replacement
  defer_signal_traps
  publish_evidence
  install_signal_traps
  resume_deferred_signal
}

# Prints the tool versions of the run, the compiler options every compile
# passed, the source-guard verdict, the probes with the driver status each
# asserted, the selection the run was invoked with, the selected cases with the
# code each returned and the assertions each passed, every deviation the run
# reported, and the absolute path of every file the run produced.
print_summary() {
  local line="" stamp="" cobc_note="" extra_note="none"

  stamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  cobc_note="pinned ${COBC_VERSION_PINNED}, ${COBC_VERSION_VERDICT}"
  if [[ -n "$COBC_FLAGS_EXTRA_ACCEPTED" ]]; then
    extra_note="$COBC_FLAGS_EXTRA_ACCEPTED"
  fi

  emit_summary ""
  emit_summary "${PROGRAM}: == run summary =="
  emit_summary "  result:            PASS"
  emit_summary "  completed (UTC):   ${stamp}"
  emit_summary "  run identifier:    ${RUN_ID}"
  emit_summary "  harness script:    ${SCRIPT_PATH}"
  emit_summary "  repository root:   ${REPO_ROOT}"
  emit_summary "  harness lock:      ${HARNESS_LOCK_PATH} held on descriptor ${HARNESS_LOCK_FD}, waited up to ${HARNESS_LOCK_WAIT} seconds"
  emit_summary "  cobc:              ${COBC_VERSION} (${cobc_note}) at ${COBC}"
  emit_summary "  cobc flags:        ${COBC_FLAGS_EFFECTIVE}"
  emit_summary "  cobc extra flags:  ${extra_note}"
  emit_summary "  python:            ${PYTHON_VERSION} at ${PY}"
  emit_summary "  source guard:      ${GUARD_VERDICT} at ${GUARD_PASSES} of 4 points, log ${SOURCE_GUARD_LOG}"
  emit_summary "  case selection:    ${CASE_SELECTION}"
  emit_summary "  cases:             $(join_with ", " "${SELECTED_CASES[@]}")"
  emit_summary "  fixtures:          $(join_with ", " "${SELECTED_FIXTURES[@]}")"
  emit_summary "  timestamp seed:    ${LASTCHANGED_SEED}"
  emit_summary "  assertions passed: ${TOTAL_ASSERTIONS}"
  emit_summary "  probes:            ${#HARNESS_PROBES[@]} of ${#HARNESS_PROBES[@]} asserted their driver status and side effect"
  for line in "${SUMMARY_PROBE_LINES[@]}"; do
    emit_summary "$line"
  done
  for line in "${SUMMARY_CASE_LINES[@]}"; do
    emit_summary "$line"
  done
  if ((${#SUMMARY_DEVIATIONS[@]} > 0)); then
    emit_summary "  deviations reported: ${#SUMMARY_DEVIATIONS[@]}"
    for line in "${SUMMARY_DEVIATIONS[@]}"; do
      emit_summary "    ${line}"
    done
  else
    emit_summary "  deviations reported: 0"
  fi
  emit_summary "  build outputs:"
  emit_summary "    generated sources: ${SRC_DIR}"
  emit_summary "    modules and driver: ${BIN_DIR}"
  emit_summary "    generated samples:  ${SAMPLES_DIR}"
  emit_summary "    stage logs:         ${LOGS_DIR}"
  emit_summary "    staged evidence:    ${STAGING_DIR}"
  emit_summary "    evidence manifest:  ${LOGS_DIR}/${EVIDENCE_MANIFEST_NAME}"
  emit_summary "  published evidence:"
  for line in "${SUMMARY_ARTIFACTS[@]}"; do
    emit_summary "    ${line}"
  done
}

# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
# Closes descriptors 3 and 4 for the rest of the run, whatever the caller left
# open on them. The two output handles of a driver are opened on those numbers
# by open_driver_output alone, so a case runs on the files this script opened and
# the probe that withholds the capture handle hands the driver nothing on
# descriptor 4. Closing a descriptor that is not open changes nothing.
release_inherited_driver_handles() {
  exec 3>&- 4>&-
}

# Runs the six stages in order and stops at the first failure, with the handler
# that ends an interrupted run installed before the first argument is read. The
# source guard closes stage 1, before any generated output exists, closes stages
# 3 and 5, and runs again in stage 6 before anything is published, so the run
# reports the state of the named sources at every boundary and publishes nothing
# when one of them has moved.
main() {
  install_signal_traps
  parse_args "$@"
  release_inherited_driver_handles
  resolve_paths
  stage_preflight
  stage_samples_and_translation
  stage_compile
  stage_probes
  stage_execute
  stage_evidence
  print_summary
  return "$EXIT_OK"
}

main "$@"
