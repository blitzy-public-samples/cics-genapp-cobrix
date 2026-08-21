      ******************************************************************
      *                                                                *
      *                            DRIVER                              *
      *                                                                *
      *   Harness driver for the GenApp Policy-Issue chain             *
      *                                                                *
      ******************************************************************
      *
      * Stands in for the CICS caller of LGAPOL01. Reads one generated
      * 32,500-character COMMAREA record from standard input, keeps
      * that record as the fixture image of the case, seeds the shared
      * EXTERNAL harness state, calls the translated LGAPOL01 once,
      * then writes the post-chain COMMAREA record and the capture file
      * that the extraction, landing and diff steps read.
      *
      * Every captured business value is compared with the value
      * decoded from the fixture image at the offsets
      * modernization/extraction/copybook_field_map.yml declares, read
      * before the chain ran; the assigned identity and timestamp are
      * compared with the seeds this program supplied and with the
      * values the returned COMMAREA carries.
      *
      * The file statements of this program open no path it composed and
      * no path any environment item supplied. Each of its three files
      * is one descriptor its caller opened before the run:
      *   SAMPLEFILE  input   standard input, through the KEYBOARD
      *                       device
      *   POSTFILE    output  descriptor 3, through /dev/fd/3
      *   CAPTFILE    output  descriptor 4, through /dev/fd/4
      * The record read is the first one standard input carries, the
      * post-chain COMMAREA record is written into descriptor 3, and
      * the capture lines are written into descriptor 4. A caller
      * therefore chooses which already-open files this program writes
      * into, and this program can neither name nor create nor remove a
      * file: it holds no name for one, and it assembles none.
      * DD_SAMPLEFILE, DD_POSTFILE, DD_CAPTFILE and their lower-case
      * and bare forms are not read. The chain is reached by module
      * name: the runtime resolves LGAPOL01 through COB_LIBRARY_PATH,
      * and this program composes no file name for it either.
      *
      * A /dev/fd entry stands for the open file the descriptor already
      * holds, so an output open composes no directory path and resolves
      * no name, and a link standing anywhere reaches nothing this
      * program opens. An open on a descriptor the caller did not open
      * returns file status 30; that status and every other status other
      * than '00' is reported naming the descriptor and the caller
      * redirection that supplies it, and ends the run with status 4.
      *
      * A stream that carries no record, and a record holding more than
      * 32,500 characters, are each reported and end the run with
      * status 4.
      *
      * Environment items read:
      *   HARNESS_CASE           case label. Required, 1 to 24
      *                          characters of 'A' through 'Z', '0'
      *                          through '9' and '-'. The value labels
      *                          the evidence of the run: it is shown
      *                          in the run header and emitted as the
      *                          CASE capture
      *   HARNESS_FIXTURE        fixture name of the case. Required, 1
      *                          to 16 characters of 'a' through 'z'
      *                          and '0' through '9'. The value labels
      *                          the evidence of the run: it is shown
      *                          in the run header and emitted as the
      *                          FIXTURE capture
      *   HARNESS_POLICY_NUMBER  identity seed for HC-SEED-POLICYNUM
      *   HARNESS_LASTCHANGED    timestamp seed for HC-SEED-LASTCHANGED
      *   COB_LS_FIXED           must hold a true value; the 32,500-
      *                          character post-chain record is written
      *                          in full only while it does
      *
      * A required item that is absent, an item longer than the width
      * stated above, and a character the stated set does not hold are
      * each reported, and the run ends with status 5 before any file
      * is opened. The two labels are read as text and are held to the
      * character sets above; no file-system property is inspected for
      * either one, and no path is assembled from either one.
      *
      * Case input items, each optional and each carrying the default
      * that reproduces the success path of the two selected samples:
      *   HARNESS_COMMAREA_LENGTH   0 to 32500, default 32500; the
      *                             value moved to EIBCALEN at the call
      *   HARNESS_REQUEST_ID        six characters; replaces
      *                             CA-REQUEST-ID after the sample is
      *                             read. Default: the fixture value
      *   HARNESS_INJECT_POLICY_SQLCODE   default 0; reaches
      *                             HC-INJECT-POL-SQLCODE
      *   HARNESS_INJECT_SUBTYPE_SQLCODE  default 0; reaches
      *                             HC-INJECT-SUB-SQLCODE
      *   HARNESS_INJECT_VSAM_RESP        default 0; reaches
      *                             HC-INJECT-VSAM-RESP
      *   HARNESS_INJECT_VSAM_RESP2       default 0; reaches
      *                             HC-INJECT-VSAM-RESP2
      *
      * Case expectation items, each optional:
      *   HARNESS_EXPECT_RETURN_CODE      two characters or 'NONE',
      *                             default '00'
      *   HARNESS_EXPECT_ABEND            'NONE', default, or a
      *                             four-character abend code
      *   HARNESS_EXPECT_PRODUCT          MOTOR, COMMERCIAL,
      *                             ENDOWMENT, HOUSE or NONE. Default:
      *                             MOTOR on request id '01AMOT',
      *                             COMMERCIAL on '01ACOM', NONE
      *                             otherwise
      *   HARNESS_EXPECT_POLICY_SQL       'Y', default, or 'N'
      *   HARNESS_EXPECT_VSAM             'Y', default, or 'N'
      *   HARNESS_EXPECT_VALUES           'Y', default, or 'N'; runs
      *                             the fixture-derived oracle over the
      *                             policy host values and over the
      *                             identity and timestamp round trip
      *   HARNESS_EXPECT_PRODUCT_VALUES   'Y', default, or 'N'; runs
      *                             that oracle over the product host
      *                             values
      *   HARNESS_EXPECT_DIAG_LINKS       'NONE', default, or 'SOME'
      *
      * A value that is not numeric where a number is required, is
      * outside the stated range, or is a keyword this program does not
      * define is reported and ends the run with status 5.
      *
      * Exit status:
      *   0  every check passed
      *   1  the chain's return code differs from the expected code
      *   2  the abend state differs from the expected abend state
      *   3  a required capture is missing or inconsistent
      *   4  a file input-output operation failed: standard input
      *      carried no record, or an open, write or close failed on
      *      one of the three descriptors
      *   5  a required environment item was not provided or was
      *      rejected
      *   6  a captured value differs from the fixture-derived expected
      *      value
      *   7  the translated chain could not be called
      *
      * Rationale belongs to modernization/docs/decision-log.md
      * (planned deliverable; not present at this milestone), rows:
      * fixture-derived expected values in the driver; deterministic
      * failure injection through shared harness state; driver sample
      * record on standard input; driver outputs written into
      * caller-opened descriptors; length-preserving VSAM record
      * evidence; driver exit-status contract; shared EXTERNAL harness
      * state.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. DRIVER.
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
      *
      * Every file below is one descriptor the caller opened. The two
      * output assignments are dynamic, and the item each one consults
      * at OPEN carries the fixed /dev/fd entry of its descriptor, so
      * no environment item is consulted and no path is composed.
      *
      * Generated fixed-width sample record read into the COMMAREA. The
      * assignment names the KEYBOARD device rather than a path, so the
      * record read is the one standard input carries and this program
      * holds no name for it.
           SELECT SAMPLE-FILE
               ASSIGN TO KEYBOARD
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-SAMPLE-STATUS.
      *
      * Post-chain COMMAREA record, one line of 32,500 characters,
      * written into descriptor 3.
           SELECT POST-FILE
               ASSIGN TO DYNAMIC WS-POST-PATH
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-POST-STATUS.
      *
      * Capture file, one NAME=VALUE line per captured value, written
      * into descriptor 4.
           SELECT CAPTURE-FILE
               ASSIGN TO DYNAMIC WS-CAPT-PATH
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-CAPT-STATUS.
      *
       DATA DIVISION.
       FILE SECTION.
      *
       FD  SAMPLE-FILE.
       01  SAMPLE-REC                  PIC X(32500).
      *
       FD  POST-FILE.
       01  POST-REC                    PIC X(32500).
      *
      * Each capture line is written at its assembled length, the
      * trimmed width the capture format states.
       FD  CAPTURE-FILE
           RECORD IS VARYING IN SIZE FROM 1 TO 300 CHARACTERS
               DEPENDING ON WS-LINE-LEN.
       01  CAPTURE-REC                 PIC X(300).
      *
       WORKING-STORAGE SECTION.
      *
      *----------------------------------------------------------------*
      * Shared harness state                                           *
      *----------------------------------------------------------------*
      * The three groups below are EXTERNAL and declare no VALUE
      * clause. This program seeds each one before the call.
       COPY DFHEIBLK.
       COPY HSQLCA.
       COPY HCAPTURE.
      *
      *----------------------------------------------------------------*
      * COMMAREA passed to and returned by the chain                   *
      *----------------------------------------------------------------*
      * LGCMAREA begins at level 03 and is copied beneath this level-01
      * group. The group is 32,500 characters: CA-REQUEST-ID X(6),
      * CA-RETURN-CODE 9(2), CA-CUSTOMER-NUM 9(10) and
      * CA-REQUEST-SPECIFIC X(32482).
       01  WS-COMMAREA.
           COPY LGCMAREA.
      *
      * Character view of the same storage, used to load the sample
      * record, to write the post-chain record and to display the
      * leading 100 characters.
       01  WS-COMMAREA-CHARS REDEFINES WS-COMMAREA PIC X(32500).
      *
      *----------------------------------------------------------------*
      * Fixture image of the case                                      *
      *----------------------------------------------------------------*
      * The sample record exactly as it was read, held apart from the
      * COMMAREA the chain writes into. Every expected value is decoded
      * from this item by absolute offset, so no expectation can be
      * taken from a value an emulated service produced.
       01  WS-FIXTURE-CHARS            PIC X(32500).
      *
      *----------------------------------------------------------------*
      * File handling                                                  *
      *----------------------------------------------------------------*
       01  WS-FILE-STATUS.
           03 WS-SAMPLE-STATUS         PIC XX.
           03 WS-POST-STATUS           PIC XX.
           03 WS-CAPT-STATUS           PIC XX.
      *
      * The /dev/fd entry of the descriptor each output record is
      * written into, opened through the dynamic ASSIGN of that file and
      * reported in the run header. Each item carries the entry from its
      * VALUE clause and no statement of this program writes to it, so
      * the descriptor opened is the one named here and no name is
      * assembled for either output.
       01  WS-POST-PATH                PIC X(9) VALUE '/dev/fd/3'.
       01  WS-CAPT-PATH                PIC X(9) VALUE '/dev/fd/4'.
      *
      * Set to 'Y' once the capture file is open for output.
       01  WS-CAPT-OPEN                PIC X.
      *
      *----------------------------------------------------------------*
      * Evidence labels                                                *
      *----------------------------------------------------------------*
      * Fixture name from HARNESS_FIXTURE, and the position of its last
      * character. Zero reports a value that was rejected.
       01  WS-FIXTURE                  PIC X(16).
       01  WS-FIXTURE-LEN              PIC S9(4) COMP.
      *
      * The environment item the value under test came from, as its
      * rejection reports it.
       01  WS-PATH-NAME                PIC X(20).
      *
      * Set to 'N' by the first rejected condition of the value under
      * test, so one value reports one reason.
       01  WS-PATH-OK                  PIC X.
      *
      * Position being examined by the character scan, and the character
      * held there.
       01  WS-PATH-IX                  PIC S9(4) COMP.
       01  WS-PATH-CHAR                PIC X.
      *
      * The characters a case label and a fixture name are allowed to
      * hold, the set being applied, its width, and 'Y' while the
      * character examined stands in it. WS-STRICT-MAX-LEN holds the
      * widest value the item being read is allowed to carry.
       01  WS-CASE-ALPHABET            PIC X(37) VALUE
           'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'.
       01  WS-FIXTURE-ALPHABET         PIC X(36) VALUE
           'abcdefghijklmnopqrstuvwxyz0123456789'.
       01  WS-ALPHABET                 PIC X(37).
       01  WS-ALPHABET-LEN             PIC S9(4) COMP.
       01  WS-ALPHA-IX                 PIC S9(4) COMP.
       01  WS-CHAR-OK                  PIC X.
       01  WS-STRICT-MAX-LEN           PIC S9(4) COMP.
      *
      *----------------------------------------------------------------*
      * Run control                                                    *
      *----------------------------------------------------------------*
      * Case label from HARNESS_CASE and the position of its last
      * character.
       01  WS-CASE                     PIC X(24).
       01  WS-CASE-LEN                 PIC S9(4) COMP.
      *
      * Status returned to the caller; the values are listed in the
      * program header.
       01  WS-EXIT-CODE                PIC 9(2).
      *
      * Number of named verdict checks that failed.
       01  WS-FAILURES                 PIC 9(2).
      *
      * The same checks counted by the status each one selects: an
      * abend state that differs, a return code that differs, a capture
      * that is missing or inconsistent, and a captured value that
      * differs from the fixture-derived expected value.
       01  WS-FAILURE-COUNTS.
           03 WS-ABEND-FAILURES        PIC 9(2).
           03 WS-RC-FAILURES           PIC 9(2).
           03 WS-CAPTURE-FAILURES      PIC 9(2).
           03 WS-VALUE-FAILURES        PIC 9(2).
      *
      * Set to 'Y' when the call to LGAPOL01 could not be made.
       01  WS-CALL-FAILED              PIC X.
      *
      * Set to 'Y' while COB_LS_FIXED holds a true value.
       01  WS-LS-FIXED                 PIC X.
      *
      * Value of EIBCALEN as it stood at the call to LGAPOL01.
       01  WS-EIBCALEN-AT-CALL         PIC S9(9) COMP.
      *
      *----------------------------------------------------------------*
      * Case inputs                                                    *
      *----------------------------------------------------------------*
      * Length moved to EIBCALEN before the call, from
      * HARNESS_COMMAREA_LENGTH. 32500 reaches the product inserts and
      * the write; 20 reaches the '98' branch at
      * [base/src/lgapol01.cbl:113-116]; zero reaches the abend site at
      * [base/src/lgapol01.cbl:98-102].
       01  WS-CALL-LENGTH              PIC S9(9) COMP.
      *
      * Request id from HARNESS_REQUEST_ID, spaces when the item is
      * unset, and the request id in force after it was applied. The
      * routing at [base/src/lgapdb01.cbl:184-207] reads the value in
      * the COMMAREA.
       01  WS-REQUEST-ID-INPUT         PIC X(6).
       01  WS-EFFECTIVE-REQUEST-ID     PIC X(6).
      *
      * Reports 'Y' while every character of the request id read from
      * HARNESS_REQUEST_ID stands above a space.
       01  WS-REQID-OK                 PIC X.
      *
      * The four failure selections handed to the emulated services
      * through the HC-INJECT group. Zero in each selects the success
      * behaviour of the service that reads it.
       01  WS-INJECT-VALUES.
           03 WS-INJ-POL-SQLCODE       PIC S9(9) COMP.
           03 WS-INJ-SUB-SQLCODE       PIC S9(9) COMP.
           03 WS-INJ-VSAM-RESP         PIC S9(8) COMP.
           03 WS-INJ-VSAM-RESP2        PIC S9(8) COMP.
      *
      *----------------------------------------------------------------*
      * Case expectations                                              *
      *----------------------------------------------------------------*
      * What the case requires of the run. The first eight are supplied
      * by the environment; the rest are derived from those values, from
      * the effective request id and from the seeds this program
      * supplied.
       01  WS-EXPECTATIONS.
      *
      * Two characters, or 'NONE' to compare no return code.
           03 WS-WANT-RETURN-CODE      PIC X(4).
      *
      * 'NONE', or the four-character code of the site the case
      * reaches.
           03 WS-WANT-ABEND            PIC X(4).
      *
      * MOTOR, COMMERCIAL, ENDOWMENT, HOUSE or NONE.
           03 WS-WANT-PRODUCT          PIC X(10).
      *
      * 'Y' when the POLICY insert is required to have been captured.
           03 WS-WANT-POLICY-SQL       PIC X.
      *
      * 'Y' when the KSDSPOLY write is required to have been captured.
           03 WS-WANT-VSAM             PIC X.
      *
      * 'Y' when the fixture-derived oracle runs over the policy host
      * values and over the identity and timestamp round trip.
           03 WS-WANT-VALUES           PIC X.
      *
      * 'Y' when that oracle runs over the product host values and over
      * the 43-character payload of the written record.
           03 WS-WANT-PRODUCT-VALUES   PIC X.
      *
      * 'NONE' or 'SOME'.
           03 WS-WANT-DIAG-LINKS       PIC X(4).
      *
      * 'Y' when the identity and the timestamp read-backs are required
      * to have been captured: the POLICY insert is expected and the
      * SQLCODE this run injects for it is zero, the condition
      * [base/src/lgapdb01.cbl:290-305] passes before
      * [base/src/lgapdb01.cbl:308-321] runs.
           03 WS-WANT-IDENTITY         PIC X.
      *
      * Letter the routing at [base/src/lgapdb01.cbl:184-207] moves to
      * DB2-POLICYTYPE for the effective request id, and '?' for a
      * request id it does not route.
           03 WS-WANT-POLICY-TYPE      PIC X.
      *
      * Identity and timestamp the case expects: the values this
      * program seeded, or the values the shared seed items hold when it
      * seeded neither.
           03 WS-WANT-POLICYNUM        PIC S9(9) COMP.
           03 WS-WANT-LASTCHANGED      PIC X(26).
      *
      * Result the most recent SQL operation of the case is expected to
      * report: the subtype selection when a product insert ran, the
      * policy selection when only the POLICY insert ran, zero when no
      * SQL block ran.
           03 WS-WANT-SQLCODE          PIC S9(9) COMP.
      *
      * Response the write is expected to have returned: the normal
      * response while nothing is injected, the injected value
      * otherwise.
           03 WS-WANT-VSAM-RESP        PIC S9(8) COMP.
      *
      * Number of events the case expects to have been stamped from
      * HC-EVENT-SEQ: one for each capture it requires. The second item
      * carries the same value in the four digits HC-EVENT-SEQ is
      * written as.
           03 WS-WANT-EVENTS           PIC S9(4) COMP.
           03 WS-WANT-EVENTS-EDIT      PIC 9(4).
      *
      * Identity this program seeded, and zero when it seeded none, and
      * the timestamp it seeded, and spaces when it seeded none.
       01  WS-SEED-SUPPLIED            PIC S9(9) COMP.
       01  WS-SEED-LCHG-SUPPLIED       PIC X(26).
      *
      *----------------------------------------------------------------*
      * Capture line assembly                                          *
      *----------------------------------------------------------------*
      * One assembled NAME=VALUE line and the length written from it.
       01  WS-LINE                     PIC X(300).
       01  WS-LINE-LEN                 PIC S9(4) COMP.
      *
      * Name and value of the line being assembled, with the trimmed
      * length of each.
       01  WS-KEY-NAME                 PIC X(40).
       01  WS-KEY-LEN                  PIC S9(4) COMP.
       01  WS-VALUE                    PIC X(255).
       01  WS-VALUE-LEN                PIC S9(4) COMP.
      *
      * Text of a diagnostic that quotes bytes this program received,
      * and the index and character the sanitising loop reads. A byte
      * outside the printable range is replaced by a full stop before
      * the text reaches the log, so a received byte cannot begin a
      * line of its own there. Every comparison of this program reads
      * the received value itself, never this copy of it.
       01  WS-LOG-TEXT                 PIC X(100).
       01  WS-LOG-IX                   PIC S9(4) COMP.
       01  WS-LOG-CHAR                 PIC X.
      *
      * Pointer used while the line is assembled, and the index used
      * by the trimming loops.
       01  WS-STRING-PTR               PIC S9(4) COMP.
       01  WS-TRIM-IX                  PIC S9(4) COMP.
      *
      * Binary values are formatted through this edited field, then
      * shifted left to remove the leading spaces of the edit.
       01  WS-INT-VALUE                PIC S9(10) COMP-5.
       01  WS-INT-EDIT                 PIC -(10)9.
       01  WS-INT-FIRST                PIC S9(4) COMP.
       01  WS-INT-LEN                  PIC S9(4) COMP.
      *
      *----------------------------------------------------------------*
      * Environment reading                                            *
      *----------------------------------------------------------------*
      * Name of the item being read, and the value as accepted. The
      * buffer is wider than the 255 characters this program accepts, so
      * a longer value is seen in the characters beyond that width
      * instead of being taken as a shorter value.
       01  WS-ENV-NAME                 PIC X(40).
       01  WS-ENV-BUFFER               PIC X(600).
       01  WS-ENV-TEXT                 PIC X(255).
       01  WS-ENV-FLAG                 PIC X(8).
      *
      * Set to 'Y' when the value read carried a character beyond the
      * 255th.
       01  WS-ENV-OVERLONG             PIC X.
      *
      * One parsed number, the widest number of digits accepted for the
      * item being parsed, and 'Y' while the value read is a number of
      * that width. The sign, when present, is the first character.
       01  WS-NUM-VALUE                PIC S9(9) COMP.
       01  WS-NUM-MAX-DIGITS           PIC S9(4) COMP.
       01  WS-NUM-DIGITS               PIC S9(4) COMP.
       01  WS-NUM-FIRST                PIC S9(4) COMP.
       01  WS-NUM-OK                   PIC X.
      *
      * Digit scan of HARNESS_POLICY_NUMBER.
       01  WS-SCAN-FLAGS.
           03 WS-HAS-DIGIT             PIC X.
           03 WS-HAS-NON-DIGIT         PIC X.
      *
      * Parsed identity seed; it reaches HC-SEED-POLICYNUM only when it
      * is greater than zero.
       01  WS-SEED-POLICYNUM           PIC S9(9) COMP.
      *
      * Position of the last character of WS-ENV-TEXT that is not a
      * space, and the count of spaces inside a scanned range.
       01  WS-SEED-LEN                 PIC S9(4) COMP.
       01  WS-SPACE-COUNT              PIC S9(4) COMP.
      *
      *----------------------------------------------------------------*
      * Verdict working items                                          *
      *----------------------------------------------------------------*
      * Key the VSAM capture is expected to hold: the fourth character
      * of CA-REQUEST-ID, then CA-CUSTOMER-NUM, then CA-POLICY-NUM.
       01  WS-EXPECTED-KEY.
           03 WS-EXP-REQUEST-ID        PIC X.
           03 WS-EXP-CUSTOMER-NUM      PIC X(10).
           03 WS-EXP-POLICY-NUM        PIC X(10).
      *
      * The 43-character payload the projection at
      * [base/src/lgapvs01.cbl:103-131] produces for the expected
      * product from the fixture, and 'Y' once it has been built. It is
      * left at 'N' when a value the projection moves cannot be decoded
      * from the fixture.
       01  WS-EXPECTED-PAYLOAD         PIC X(43).
       01  WS-PAYLOAD-DERIVED          PIC X.
      *
      * The complete 64-character record image the case expects: the
      * 21-character key, then that payload, the two halves the group
      * From(WF-Policy-Info) [base/src/lgapvs01.cbl:136] passes. Every
      * one of the 64 characters is compared, including a trailing
      * space the projection leaves.
       01  WS-EXPECTED-RECORD          PIC X(64).
      *
      *----------------------------------------------------------------*
      * Hexadecimal encoding                                           *
      *----------------------------------------------------------------*
      * The characters being encoded, their number, and the two
      * upper-case hexadecimal digits per character the encoding
      * produces. The widest value encoded is the 64-character record
      * image, which fills all 128 characters.
       01  WS-HEX-DIGITS               PIC X(16) VALUE
           '0123456789ABCDEF'.
       01  WS-HEX-SOURCE               PIC X(64).
       01  WS-HEX-SOURCE-LEN           PIC S9(4) COMP.
       01  WS-HEX-TEXT                 PIC X(128).
       01  WS-HEX-LEN                  PIC S9(4) COMP.
      *
      * Position being encoded, the character held there, its value in
      * the runtime character set, and the two four-bit halves of that
      * value.
       01  WS-HEX-IX                   PIC S9(4) COMP.
       01  WS-HEX-CHAR                 PIC X.
       01  WS-HEX-VALUE                PIC S9(4) COMP.
       01  WS-HEX-HIGH                 PIC S9(4) COMP.
       01  WS-HEX-LOW                  PIC S9(4) COMP.
      *
      * Identity formatted as the ten digits CA-POLICY-NUM holds, the
      * form the key carries through the move at
      * [base/src/lgapvs01.cbl:100].
       01  WS-POLICYNUM-EDIT           PIC 9(10).
      *
      * Product table the expected product names: 'M' motor,
      * 'C' commercial, 'E' endowment, 'H' house, '?' none.
       01  WS-PRODUCT-WANTED           PIC X.
      *
      * Character view of the returned CA-RETURN-CODE.
       01  WS-RETURN-CODE-TEXT         PIC XX.
      *
      * Name of the check being reported by REPORT-FAILED-CHECK.
       01  WS-CHECK-NAME               PIC X(40).
      *
      *----------------------------------------------------------------*
      * One capture under test                                         *
      *----------------------------------------------------------------*
      * The statement being examined by CHECK-STATEMENT-CAPTURE: its
      * name, its presence flag, its counter, its ordinal, and 'Y' when
      * the case requires exactly one execution or 'N' when it forbids
      * every execution.
       01  WS-STMT-LABEL               PIC X(24).
       01  WS-STMT-PRESENT             PIC X.
       01  WS-STMT-COUNT               PIC 9(4).
       01  WS-STMT-SEQ                 PIC 9(4).
       01  WS-STMT-EXPECTED            PIC X.
      *
      * COMMAREA length observed inside the program being examined by
      * CHECK-ONE-CHAIN-WITNESS.
       01  WS-CHAIN-CALEN              PIC 9(5).
      *
      *----------------------------------------------------------------*
      * Execution order under test                                     *
      *----------------------------------------------------------------*
      * The ordinals of the captures the case requires, appended in the
      * order [base/src/lgapdb01.cbl:219-246] executes them: the POLICY
      * insert, the identity read-back, the timestamp read-back, the
      * product insert, then the KSDSPOLY write. Five entries fill the
      * table; the sixth is spare.
       01  WS-ORDER-TABLE.
           03 WS-ORDER-ENTRY OCCURS 6 TIMES.
              05 WS-ORDER-NAME         PIC X(24).
              05 WS-ORDER-SEQ          PIC 9(4).
       01  WS-ORDER-COUNT              PIC S9(4) COMP.
       01  WS-ORDER-IX                 PIC S9(4) COMP.
       01  WS-ORDER-PREV               PIC 9(4).
      *
      *----------------------------------------------------------------*
      * Fixture decoding                                               *
      *----------------------------------------------------------------*
      * Position and width of the item being decoded from
      * WS-FIXTURE-CHARS, the characters found there, the value they
      * spell, and 'Y' while every one of them is a digit.
       01  WS-DEC-OFFSET               PIC S9(4) COMP.
       01  WS-DEC-LENGTH               PIC S9(4) COMP.
       01  WS-DEC-TEXT                 PIC X(255).
       01  WS-DEC-NUM                  PIC S9(10) COMP.
       01  WS-DEC-OK                   PIC X.
      *
      *----------------------------------------------------------------*
      * Value comparison                                              *
      *----------------------------------------------------------------*
      * The field being compared, the width compared, and the expected
      * and captured values in the form the comparison uses.
       01  WS-CMP-FIELD                PIC X(32).
       01  WS-CMP-LEN                  PIC S9(4) COMP.
       01  WS-CMP-EXPECT-TEXT          PIC X(255).
       01  WS-CMP-ACTUAL-TEXT          PIC X(255).
       01  WS-CMP-EXPECT-NUM           PIC S9(10) COMP.
       01  WS-CMP-ACTUAL-NUM           PIC S9(10) COMP.
      *
      * Position of the first character that differs, the width of the
      * text shown from there, and the edited form of each number
      * shown in the report line.
       01  WS-CMP-DIFF-POS             PIC S9(4) COMP.
       01  WS-CMP-WINDOW               PIC S9(4) COMP.
       01  WS-CMP-EXPECT-EDIT          PIC -(10)9.
       01  WS-CMP-ACTUAL-EDIT          PIC -(10)9.
      *
      * One count or position, edited for the report line that carries
      * it.
       01  WS-COUNT-EDIT               PIC Z(4)9.
      *
      *----------------------------------------------------------------*
      * Amount comparison                                              *
      *----------------------------------------------------------------*
      * Number of the six amount fields compared in this case, the
      * absolute difference of the comparison being reported, and the
      * widest difference any of them showed. The fields are unsigned
      * display integers moved without arithmetic
      * [base/src/lgcmarea.cpy:43,73,85,87,89,91], so every difference
      * is a whole number and exceeds the 0.01 the acceptance contract
      * allows.
       01  WS-AMOUNT-CHECKS            PIC 9(2).
       01  WS-AMOUNT-DELTA             PIC S9(10) COMP.
       01  WS-AMOUNT-MAX-DELTA         PIC S9(10) COMP.
      *
      *----------------------------------------------------------------*
      * Constants                                                      *
      *----------------------------------------------------------------*
      * File name, record length and key length the write at
      * [base/src/lgapvs01.cbl:135-139] states. Each is compared with
      * the operand the emulated command received, never with a value
      * this program supplied in its place.
       01  WS-VSAM-FILE-EXPECTED       PIC X(8) VALUE 'KSDSPOLY'.
       01  WS-VSAM-LEN-EXPECTED        PIC 9(4) VALUE 64.
       01  WS-VSAM-KEYLEN-EXPECTED     PIC 9(4) VALUE 21.
      *
      * Length the two links of the chain state, at
      * [base/src/lgapol01.cbl:121-124] and
      * [base/src/lgapdb01.cbl:243-246].
       01  WS-LINK-LEN-EXPECTED        PIC 9(5) VALUE 32500.
      *
      * Value of the CICS NORMAL response condition, as
      * modernization/harness/copybooks/dfhresp.cpy declares it and as
      * the write returns it while nothing is injected.
       01  WS-RESP-NORMAL              PIC S9(8) COMP VALUE +0.
      *----------------------------------------------------------------*

      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION.
      *
      *================================================================*
      * Control flow                                                   *
      *================================================================*
      * Each step below reports its own failure and leaves a non-zero
      * status in WS-EXIT-CODE. A step that cannot leave a usable
      * artifact behind ends the run at once.
       MAIN-CONTROL.
           PERFORM INITIALIZE-RUN-CONTROL
           PERFORM RESOLVE-ENVIRONMENT
           IF WS-EXIT-CODE NOT = ZERO
               PERFORM RETURN-TO-CALLER
               GOBACK
           END-IF
           PERFORM SEED-SHARED-STATE
           PERFORM READ-SAMPLE-RECORD
           IF WS-EXIT-CODE NOT = ZERO
               PERFORM RETURN-TO-CALLER
               GOBACK
           END-IF
           PERFORM APPLY-REQUEST-ID-INPUT
           PERFORM RESOLVE-EXPECTATIONS
           PERFORM DISPLAY-RUN-HEADER
           PERFORM EXECUTE-CHAIN
           PERFORM WRITE-POST-RECORD
           IF WS-EXIT-CODE NOT = ZERO
               PERFORM RETURN-TO-CALLER
               GOBACK
           END-IF
           PERFORM CREATE-CAPTURE-FILE
           IF WS-EXIT-CODE NOT = ZERO
               PERFORM RETURN-TO-CALLER
               GOBACK
           END-IF
           PERFORM DISPLAY-COMMAREA-EXTRACT
           PERFORM EMIT-RUN-CAPTURES
           PERFORM EMIT-COMMAREA-CAPTURES
           PERFORM EMIT-POLICY-CAPTURES
           PERFORM EMIT-MOTOR-CAPTURES
           PERFORM EMIT-COMMERCIAL-CAPTURES
           PERFORM EMIT-OTHER-PRODUCT-CAPTURES
           PERFORM EMIT-SQL-BOOKKEEPING
           PERFORM EMIT-ORDER-CAPTURES
           PERFORM EMIT-VSAM-CAPTURES
           PERFORM EMIT-FAILURE-SURFACE
           PERFORM EVALUATE-VERDICT
           PERFORM EMIT-AMOUNT-CAPTURES
           PERFORM EMIT-VERDICT-COUNTS
           PERFORM EMIT-DRIVER-STATUS
           PERFORM CLOSE-CAPTURE-FILE
           PERFORM RETURN-TO-CALLER
           GOBACK.
      *
      *================================================================*
      * Run control                                                    *
      *================================================================*
       INITIALIZE-RUN-CONTROL.
           MOVE ZERO TO WS-EXIT-CODE
           MOVE ZERO TO WS-FAILURES
           MOVE ZERO TO WS-ABEND-FAILURES
           MOVE ZERO TO WS-RC-FAILURES
           MOVE ZERO TO WS-CAPTURE-FAILURES
           MOVE ZERO TO WS-VALUE-FAILURES
           MOVE 'N' TO WS-CALL-FAILED
           MOVE 'Y' TO WS-REQID-OK
           MOVE 'N' TO WS-CAPT-OPEN
           MOVE 'N' TO WS-LS-FIXED
           MOVE ZERO TO WS-EIBCALEN-AT-CALL
           MOVE SPACES TO WS-KEY-NAME
           MOVE SPACES TO WS-VALUE
           MOVE SPACES TO WS-LINE
           MOVE 1 TO WS-LINE-LEN
           MOVE SPACES TO WS-CHECK-NAME
           MOVE '?' TO WS-PRODUCT-WANTED
           MOVE SPACES TO WS-FIXTURE-CHARS
           MOVE SPACES TO WS-FIXTURE
           MOVE ZERO TO WS-FIXTURE-LEN
           MOVE SPACES TO WS-CASE
           MOVE ZERO TO WS-CASE-LEN
           MOVE SPACES TO WS-PATH-NAME
           MOVE 'Y' TO WS-PATH-OK
           MOVE SPACES TO WS-ALPHABET
           MOVE ZERO TO WS-ALPHABET-LEN
           MOVE ZERO TO WS-STRICT-MAX-LEN
           MOVE 'N' TO WS-CHAR-OK
           MOVE 32500 TO WS-CALL-LENGTH
           MOVE SPACES TO WS-REQUEST-ID-INPUT
           MOVE SPACES TO WS-EFFECTIVE-REQUEST-ID
           MOVE ZERO TO WS-INJ-POL-SQLCODE
           MOVE ZERO TO WS-INJ-SUB-SQLCODE
           MOVE ZERO TO WS-INJ-VSAM-RESP
           MOVE ZERO TO WS-INJ-VSAM-RESP2
           MOVE '00' TO WS-WANT-RETURN-CODE
           MOVE 'NONE' TO WS-WANT-ABEND
           MOVE SPACES TO WS-WANT-PRODUCT
           MOVE 'Y' TO WS-WANT-POLICY-SQL
           MOVE 'Y' TO WS-WANT-VSAM
           MOVE 'Y' TO WS-WANT-VALUES
           MOVE 'Y' TO WS-WANT-PRODUCT-VALUES
           MOVE 'NONE' TO WS-WANT-DIAG-LINKS
           MOVE 'N' TO WS-WANT-IDENTITY
           MOVE '?' TO WS-WANT-POLICY-TYPE
           MOVE ZERO TO WS-WANT-POLICYNUM
           MOVE SPACES TO WS-WANT-LASTCHANGED
           MOVE ZERO TO WS-WANT-SQLCODE
           MOVE ZERO TO WS-WANT-VSAM-RESP
           MOVE ZERO TO WS-WANT-EVENTS
           MOVE ZERO TO WS-SEED-SUPPLIED
           MOVE SPACES TO WS-SEED-LCHG-SUPPLIED
           MOVE ZERO TO WS-AMOUNT-CHECKS
           MOVE ZERO TO WS-AMOUNT-DELTA
           MOVE ZERO TO WS-AMOUNT-MAX-DELTA
           MOVE 'N' TO WS-PAYLOAD-DERIVED
           MOVE SPACES TO WS-EXPECTED-PAYLOAD
           MOVE SPACES TO WS-EXPECTED-KEY
           MOVE SPACES TO WS-EXPECTED-RECORD
           MOVE SPACES TO WS-HEX-TEXT
           MOVE ZERO TO WS-HEX-LEN
           MOVE ZERO TO WS-ORDER-COUNT
           INITIALIZE WS-ORDER-TABLE.
      *
      * Returns the status listed in the program header to the caller.
       RETURN-TO-CALLER.
           MOVE WS-EXIT-CODE TO RETURN-CODE
           DISPLAY 'DRIVER: exit status ' WS-EXIT-CODE
           END-DISPLAY.
      *
      *================================================================*
      * Environment                                                    *
      *================================================================*
      * Reads the case label and the fixture name, the two labels the
      * evidence of the run carries, and confirms the setting the
      * full-length post-chain record depends on. No path is read or
      * assembled here. Every rejection leaves status 5 and MAIN-CONTROL
      * ends the run before any file is opened.
       RESOLVE-ENVIRONMENT.
           PERFORM RESOLVE-CASE-LABEL
           PERFORM RESOLVE-FIXTURE-NAME
           PERFORM RESOLVE-LS-FIXED
           PERFORM RESOLVE-CASE-INPUTS
           PERFORM RESOLVE-CASE-EXPECTATIONS
           IF WS-LS-FIXED = 'N'
               DISPLAY 'DRIVER: COB_LS_FIXED does not hold a true '
                       'value, so the 32500-character post-chain '
                       'record would be written without its trailing '
                       'spaces'
               END-DISPLAY
               MOVE 05 TO WS-EXIT-CODE
           END-IF.
      *
      *----------------------------------------------------------------*
      * Case label and fixture name                                    *
      *----------------------------------------------------------------*
      * Reads the case label. The value is required, is required to
      * hold at most 24 characters, and is required to hold only the
      * characters WS-CASE-ALPHABET names. The accepted label is shown
      * in the run header and emitted as the CASE capture.
       RESOLVE-CASE-LABEL.
           MOVE 'HARNESS_CASE' TO WS-ENV-NAME
           MOVE 'HARNESS_CASE' TO WS-PATH-NAME
           MOVE WS-CASE-ALPHABET TO WS-ALPHABET
           MOVE 37 TO WS-ALPHABET-LEN
           MOVE 24 TO WS-STRICT-MAX-LEN
           PERFORM CHECK-STRICT-VALUE
           IF WS-PATH-OK = 'Y'
               MOVE WS-ENV-TEXT(1:WS-SEED-LEN) TO WS-CASE
               MOVE WS-SEED-LEN TO WS-CASE-LEN
           ELSE
               MOVE SPACES TO WS-CASE
               MOVE ZERO TO WS-CASE-LEN
           END-IF.
      *
      * Reads the fixture name. The value is required, is required to
      * hold at most 16 characters, and is required to hold only the
      * characters WS-FIXTURE-ALPHABET names.
       RESOLVE-FIXTURE-NAME.
           MOVE 'HARNESS_FIXTURE' TO WS-ENV-NAME
           MOVE 'HARNESS_FIXTURE' TO WS-PATH-NAME
           MOVE SPACES TO WS-ALPHABET
           MOVE WS-FIXTURE-ALPHABET TO WS-ALPHABET(1:36)
           MOVE 36 TO WS-ALPHABET-LEN
           MOVE 16 TO WS-STRICT-MAX-LEN
           PERFORM CHECK-STRICT-VALUE
           IF WS-PATH-OK = 'Y'
               MOVE WS-ENV-TEXT(1:WS-SEED-LEN) TO WS-FIXTURE
               MOVE WS-SEED-LEN TO WS-FIXTURE-LEN
           ELSE
               MOVE SPACES TO WS-FIXTURE
               MOVE ZERO TO WS-FIXTURE-LEN
           END-IF.
      *
      * Reads the item named in WS-ENV-NAME and requires it to be
      * present, to hold at most the WS-STRICT-MAX-LEN characters the
      * caller of this paragraph set, and to hold only the characters
      * WS-ALPHABET(1:WS-ALPHABET-LEN) names. The accepted value is
      * left in WS-ENV-TEXT(1:WS-SEED-LEN).
       CHECK-STRICT-VALUE.
           MOVE 'Y' TO WS-PATH-OK
           PERFORM ACCEPT-ENV-VALUE
           IF WS-ENV-OVERLONG = 'Y'
               MOVE SPACES TO WS-ENV-TEXT
               PERFORM REPORT-VALUE-REJECTED-LENGTH
           END-IF
           IF WS-PATH-OK = 'Y'
               PERFORM TRIM-ENV-TEXT
               IF WS-SEED-LEN = ZERO
                   PERFORM REPORT-VALUE-REJECTED-MISSING
               END-IF
           END-IF
           IF WS-PATH-OK = 'Y' AND WS-SEED-LEN > WS-STRICT-MAX-LEN
               PERFORM REPORT-VALUE-REJECTED-LENGTH
           END-IF
           IF WS-PATH-OK = 'Y'
               PERFORM VARYING WS-PATH-IX FROM 1 BY 1
                       UNTIL WS-PATH-IX > WS-SEED-LEN
                          OR WS-PATH-OK = 'N'
                   MOVE WS-ENV-TEXT(WS-PATH-IX:1) TO WS-PATH-CHAR
                   PERFORM CHECK-STRICT-CHARACTER
                   IF WS-CHAR-OK = 'N'
                       MOVE WS-PATH-IX TO WS-COUNT-EDIT
                       PERFORM REPORT-VALUE-REJECTED-CHARACTER
                   END-IF
               END-PERFORM
           END-IF.
      *
      * Reports whether the character in WS-PATH-CHAR stands in
      * WS-ALPHABET(1:WS-ALPHABET-LEN).
       CHECK-STRICT-CHARACTER.
           MOVE 'N' TO WS-CHAR-OK
           PERFORM VARYING WS-ALPHA-IX FROM 1 BY 1
                   UNTIL WS-ALPHA-IX > WS-ALPHABET-LEN
                      OR WS-CHAR-OK = 'Y'
               IF WS-ALPHABET(WS-ALPHA-IX:1) = WS-PATH-CHAR
                   MOVE 'Y' TO WS-CHAR-OK
               END-IF
           END-PERFORM.
      *
      * The reasons one case label or fixture name is rejected. Each
      * names the item it read and the width or the character set that
      * item is held to.
       REPORT-VALUE-REJECTED-LENGTH.
           MOVE WS-STRICT-MAX-LEN TO WS-COUNT-EDIT
           DISPLAY 'DRIVER: ' FUNCTION TRIM(WS-PATH-NAME)
                   ' holds more than ' FUNCTION TRIM(WS-COUNT-EDIT)
                   ' characters and is rejected rather than shortened'
           END-DISPLAY
           PERFORM REPORT-PATH-REJECTED.
      *
       REPORT-VALUE-REJECTED-MISSING.
           DISPLAY 'DRIVER: ' FUNCTION TRIM(WS-PATH-NAME)
                   ' is not set; set it to a value holding only ['
                   WS-ALPHABET(1:WS-ALPHABET-LEN) ']'
           END-DISPLAY
           PERFORM REPORT-PATH-REJECTED.
      *
       REPORT-VALUE-REJECTED-CHARACTER.
           DISPLAY 'DRIVER: ' FUNCTION TRIM(WS-PATH-NAME)
                   ' holds a character outside ['
                   WS-ALPHABET(1:WS-ALPHABET-LEN)
                   '] at position ' FUNCTION TRIM(WS-COUNT-EDIT)
           END-DISPLAY
           DISPLAY 'DRIVER:   value ['
                   WS-ENV-TEXT(1:WS-SEED-LEN) ']'
           END-DISPLAY
           PERFORM REPORT-PATH-REJECTED.
      *
       REPORT-PATH-REJECTED.
           MOVE 'N' TO WS-PATH-OK
           MOVE 05 TO WS-EXIT-CODE.
      *
      * Reads one environment item into WS-ENV-TEXT. The value is
      * accepted into a buffer wider than the 255 characters this
      * program holds, and WS-ENV-OVERLONG reports a value that
      * reached beyond that width.
       ACCEPT-ENV-VALUE.
           MOVE SPACES TO WS-ENV-BUFFER
           ACCEPT WS-ENV-BUFFER FROM ENVIRONMENT WS-ENV-NAME
           END-ACCEPT
           MOVE 'N' TO WS-ENV-OVERLONG
           IF WS-ENV-BUFFER(256:345) NOT = SPACES
               MOVE 'Y' TO WS-ENV-OVERLONG
           END-IF
           MOVE WS-ENV-BUFFER(1:255) TO WS-ENV-TEXT.
      *
      * Reports the item named in WS-ENV-NAME as longer than this
      * program holds, clears the value so no shortened text is read as
      * the item and no default is taken in its place, and ends the run
      * with status 5.
       REPORT-ENV-OVERLONG.
           DISPLAY 'DRIVER: ' FUNCTION TRIM(WS-ENV-NAME)
                   ' holds more than 255 characters and is rejected '
                   'rather than shortened'
           END-DISPLAY
           MOVE SPACES TO WS-ENV-TEXT
           MOVE 05 TO WS-EXIT-CODE.
      *
      *----------------------------------------------------------------*
      * Case inputs                                                    *
      *----------------------------------------------------------------*
      * Reads the COMMAREA length, the request-id replacement and the
      * four failure selections. Each item is optional; each value that
      * is present is required to be well formed, and one that is not
      * ends the run with status 5 rather than falling back to the
      * default.
       RESOLVE-CASE-INPUTS.
           PERFORM RESOLVE-COMMAREA-LENGTH
           PERFORM RESOLVE-REQUEST-ID-INPUT
           MOVE 'HARNESS_INJECT_POLICY_SQLCODE' TO WS-ENV-NAME
           MOVE 9 TO WS-NUM-MAX-DIGITS
           PERFORM RESOLVE-SIGNED-NUMBER
           IF WS-NUM-OK = 'Y'
               MOVE WS-NUM-VALUE TO WS-INJ-POL-SQLCODE
           END-IF
           MOVE 'HARNESS_INJECT_SUBTYPE_SQLCODE' TO WS-ENV-NAME
           MOVE 9 TO WS-NUM-MAX-DIGITS
           PERFORM RESOLVE-SIGNED-NUMBER
           IF WS-NUM-OK = 'Y'
               MOVE WS-NUM-VALUE TO WS-INJ-SUB-SQLCODE
           END-IF
           MOVE 'HARNESS_INJECT_VSAM_RESP' TO WS-ENV-NAME
           MOVE 8 TO WS-NUM-MAX-DIGITS
           PERFORM RESOLVE-SIGNED-NUMBER
           IF WS-NUM-OK = 'Y'
               MOVE WS-NUM-VALUE TO WS-INJ-VSAM-RESP
           END-IF
           MOVE 'HARNESS_INJECT_VSAM_RESP2' TO WS-ENV-NAME
           MOVE 8 TO WS-NUM-MAX-DIGITS
           PERFORM RESOLVE-SIGNED-NUMBER
           IF WS-NUM-OK = 'Y'
               MOVE WS-NUM-VALUE TO WS-INJ-VSAM-RESP2
           END-IF.
      *
      * The length moved to EIBCALEN at the call. Accepted values are
      * zero through 32500, the length of the COMMAREA the chain is
      * called with [base/src/lgapol01.cbl:121-124].
       RESOLVE-COMMAREA-LENGTH.
           MOVE 'HARNESS_COMMAREA_LENGTH' TO WS-ENV-NAME
           MOVE 5 TO WS-NUM-MAX-DIGITS
           PERFORM RESOLVE-SIGNED-NUMBER
           IF WS-NUM-OK = 'Y'
               IF WS-NUM-VALUE < ZERO OR WS-NUM-VALUE > 32500
                   DISPLAY 'DRIVER: HARNESS_COMMAREA_LENGTH holds '
                           WS-NUM-VALUE
                           ' and 0 through 32500 are accepted'
                   END-DISPLAY
                   MOVE 05 TO WS-EXIT-CODE
               ELSE
                   MOVE WS-NUM-VALUE TO WS-CALL-LENGTH
               END-IF
           END-IF.
      *
      * The request id that replaces CA-REQUEST-ID after the sample is
      * read. Six characters are required, none of them a space, so the
      * routing at [base/src/lgapdb01.cbl:184-207] reads a complete
      * request id.
       RESOLVE-REQUEST-ID-INPUT.
           MOVE 'HARNESS_REQUEST_ID' TO WS-ENV-NAME
           PERFORM ACCEPT-ENV-VALUE
           IF WS-ENV-OVERLONG = 'Y'
               PERFORM REPORT-ENV-OVERLONG
           END-IF
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN > ZERO
               IF WS-SEED-LEN = 6
                   PERFORM CHECK-REQUEST-ID-CHARACTERS
               ELSE
                   MOVE WS-SEED-LEN TO WS-COUNT-EDIT
                   DISPLAY 'DRIVER: HARNESS_REQUEST_ID holds '
                           FUNCTION TRIM(WS-COUNT-EDIT)
                           ' characters and exactly 6 are required'
                   END-DISPLAY
                   MOVE 05 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      * Requires each of the six characters to stand above a space and
      * to differ from X'7F', so the value moved to CA-REQUEST-ID holds
      * a complete request id for the routing at
      * [base/src/lgapdb01.cbl:184-207] to read.
       CHECK-REQUEST-ID-CHARACTERS.
           MOVE 'Y' TO WS-REQID-OK
           PERFORM VARYING WS-TRIM-IX FROM 1 BY 1
                   UNTIL WS-TRIM-IX > 6
                      OR WS-REQID-OK = 'N'
               IF WS-ENV-TEXT(WS-TRIM-IX:1) NOT > SPACE
                       OR WS-ENV-TEXT(WS-TRIM-IX:1) = X'7F'
                   MOVE 'N' TO WS-REQID-OK
               END-IF
           END-PERFORM
           IF WS-REQID-OK = 'Y'
               MOVE WS-ENV-TEXT(1:6) TO WS-REQUEST-ID-INPUT
           ELSE
               DISPLAY 'DRIVER: HARNESS_REQUEST_ID holds ['
                       WS-ENV-TEXT(1:6)
                       '] and six characters above a space are '
                       'required'
               END-DISPLAY
               MOVE 05 TO WS-EXIT-CODE
           END-IF.
      *
      * Reads the item named in WS-ENV-NAME as an optional sign
      * followed by digits. WS-NUM-OK reports 'Y' when a value was
      * present and well formed, and 'N' when the item was unset. A
      * value that is not a number of at most WS-NUM-MAX-DIGITS digits
      * ends the run with status 5.
       RESOLVE-SIGNED-NUMBER.
           MOVE 'N' TO WS-NUM-OK
           MOVE ZERO TO WS-NUM-VALUE
           PERFORM ACCEPT-ENV-VALUE
           IF WS-ENV-OVERLONG = 'Y'
               DISPLAY 'DRIVER: ' FUNCTION TRIM(WS-ENV-NAME)
                       ' holds more than 255 characters'
               END-DISPLAY
               MOVE 05 TO WS-EXIT-CODE
           ELSE
               PERFORM TRIM-ENV-TEXT
               IF WS-SEED-LEN > ZERO
                   PERFORM PARSE-SIGNED-NUMBER
               END-IF
           END-IF.
      *
      * Parses WS-ENV-TEXT(1:WS-SEED-LEN) as an optional leading '+' or
      * '-' followed by one or more digits.
       PARSE-SIGNED-NUMBER.
           MOVE 1 TO WS-NUM-FIRST
           IF WS-ENV-TEXT(1:1) = '+' OR WS-ENV-TEXT(1:1) = '-'
               MOVE 2 TO WS-NUM-FIRST
           END-IF
           COMPUTE WS-NUM-DIGITS = WS-SEED-LEN - WS-NUM-FIRST + 1
           END-COMPUTE
           MOVE 'N' TO WS-HAS-DIGIT
           MOVE 'N' TO WS-HAS-NON-DIGIT
           IF WS-NUM-DIGITS > ZERO
               PERFORM VARYING WS-TRIM-IX FROM WS-NUM-FIRST BY 1
                       UNTIL WS-TRIM-IX > WS-SEED-LEN
                   IF WS-ENV-TEXT(WS-TRIM-IX:1) IS NUMERIC
                       MOVE 'Y' TO WS-HAS-DIGIT
                   ELSE
                       MOVE 'Y' TO WS-HAS-NON-DIGIT
                   END-IF
               END-PERFORM
           END-IF
           IF WS-HAS-DIGIT = 'Y' AND WS-HAS-NON-DIGIT = 'N'
                   AND WS-NUM-DIGITS NOT > WS-NUM-MAX-DIGITS
               COMPUTE WS-NUM-VALUE =
                   FUNCTION NUMVAL(WS-ENV-TEXT(1:WS-SEED-LEN))
               END-COMPUTE
               MOVE 'Y' TO WS-NUM-OK
           ELSE
               MOVE WS-NUM-MAX-DIGITS TO WS-COUNT-EDIT
               DISPLAY 'DRIVER: ' FUNCTION TRIM(WS-ENV-NAME)
                       ' holds [' WS-ENV-TEXT(1:WS-SEED-LEN)
                       '] and an optional sign followed by at most '
                       FUNCTION TRIM(WS-COUNT-EDIT)
                       ' digits is required'
               END-DISPLAY
               MOVE 05 TO WS-EXIT-CODE
           END-IF.
      *
      *----------------------------------------------------------------*
      * Case expectations                                              *
      *----------------------------------------------------------------*
      * Reads the eight expectation items. An unset item keeps the
      * default the program header states; a value this program does
      * not define ends the run with status 5.
       RESOLVE-CASE-EXPECTATIONS.
           PERFORM RESOLVE-EXPECT-RETURN-CODE
           PERFORM RESOLVE-EXPECT-ABEND
           PERFORM RESOLVE-EXPECT-PRODUCT
           MOVE 'HARNESS_EXPECT_POLICY_SQL' TO WS-ENV-NAME
           PERFORM RESOLVE-YES-NO
           IF WS-ENV-FLAG NOT = SPACES
               MOVE WS-ENV-FLAG(1:1) TO WS-WANT-POLICY-SQL
           END-IF
           MOVE 'HARNESS_EXPECT_VSAM' TO WS-ENV-NAME
           PERFORM RESOLVE-YES-NO
           IF WS-ENV-FLAG NOT = SPACES
               MOVE WS-ENV-FLAG(1:1) TO WS-WANT-VSAM
           END-IF
           MOVE 'HARNESS_EXPECT_VALUES' TO WS-ENV-NAME
           PERFORM RESOLVE-YES-NO
           IF WS-ENV-FLAG NOT = SPACES
               MOVE WS-ENV-FLAG(1:1) TO WS-WANT-VALUES
           END-IF
           MOVE 'HARNESS_EXPECT_PRODUCT_VALUES' TO WS-ENV-NAME
           PERFORM RESOLVE-YES-NO
           IF WS-ENV-FLAG NOT = SPACES
               MOVE WS-ENV-FLAG(1:1) TO WS-WANT-PRODUCT-VALUES
           END-IF
           PERFORM RESOLVE-EXPECT-DIAG-LINKS.
      *
      * Two characters, or 'NONE' to compare no return code.
       RESOLVE-EXPECT-RETURN-CODE.
           MOVE 'HARNESS_EXPECT_RETURN_CODE' TO WS-ENV-NAME
           PERFORM ACCEPT-ENV-VALUE
           IF WS-ENV-OVERLONG = 'Y'
               PERFORM REPORT-ENV-OVERLONG
           END-IF
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN > ZERO
               IF WS-SEED-LEN = 2
                   MOVE WS-ENV-TEXT(1:2) TO WS-WANT-RETURN-CODE(1:2)
                   MOVE SPACES TO WS-WANT-RETURN-CODE(3:2)
               ELSE
                   IF FUNCTION UPPER-CASE(WS-ENV-TEXT(1:4)) = 'NONE'
                           AND WS-SEED-LEN = 4
                       MOVE 'NONE' TO WS-WANT-RETURN-CODE
                   ELSE
                       DISPLAY 'DRIVER: HARNESS_EXPECT_RETURN_CODE '
                               'holds [' WS-ENV-TEXT(1:WS-SEED-LEN)
                               '] and two characters or NONE are '
                               'accepted'
                       END-DISPLAY
                       MOVE 05 TO WS-EXIT-CODE
                   END-IF
               END-IF
           END-IF.
      *
      * 'NONE', or the four-character code of the abend site the case
      * reaches: 'LGCA' at [base/src/lgapol01.cbl:101] and
      * [base/src/lgapdb01.cbl:168], 'LGSQ' at
      * [base/src/lgapdb01.cbl:393,431,477,551].
       RESOLVE-EXPECT-ABEND.
           MOVE 'HARNESS_EXPECT_ABEND' TO WS-ENV-NAME
           PERFORM ACCEPT-ENV-VALUE
           IF WS-ENV-OVERLONG = 'Y'
               PERFORM REPORT-ENV-OVERLONG
           END-IF
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN > ZERO
               IF WS-SEED-LEN = 4
                   MOVE WS-ENV-TEXT(1:4) TO WS-WANT-ABEND
               ELSE
                   DISPLAY 'DRIVER: HARNESS_EXPECT_ABEND holds ['
                           WS-ENV-TEXT(1:WS-SEED-LEN)
                           '] and NONE or four characters are accepted'
                   END-DISPLAY
                   MOVE 05 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      * The product table the case expects to have been inserted into.
      * Left at spaces here; RESOLVE-EXPECTATIONS supplies the default
      * the effective request id selects.
       RESOLVE-EXPECT-PRODUCT.
           MOVE 'HARNESS_EXPECT_PRODUCT' TO WS-ENV-NAME
           PERFORM ACCEPT-ENV-VALUE
           IF WS-ENV-OVERLONG = 'Y'
               PERFORM REPORT-ENV-OVERLONG
           END-IF
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN > ZERO
               MOVE FUNCTION UPPER-CASE(WS-ENV-TEXT(1:10))
                   TO WS-WANT-PRODUCT
               EVALUATE WS-WANT-PRODUCT
                 WHEN 'MOTOR'
                 WHEN 'COMMERCIAL'
                 WHEN 'ENDOWMENT'
                 WHEN 'HOUSE'
                 WHEN 'NONE'
                   CONTINUE
                 WHEN OTHER
                   DISPLAY 'DRIVER: HARNESS_EXPECT_PRODUCT holds ['
                           WS-ENV-TEXT(1:WS-SEED-LEN)
                           '] and MOTOR, COMMERCIAL, ENDOWMENT, HOUSE '
                           'or NONE are accepted'
                   END-DISPLAY
                   MOVE 05 TO WS-EXIT-CODE
                   MOVE SPACES TO WS-WANT-PRODUCT
               END-EVALUATE
           END-IF.
      *
      * 'NONE' to require no diagnostic link, 'SOME' to require at
      * least one. The nine sites sit inside the error paragraphs of the
      * three programs.
       RESOLVE-EXPECT-DIAG-LINKS.
           MOVE 'HARNESS_EXPECT_DIAG_LINKS' TO WS-ENV-NAME
           PERFORM ACCEPT-ENV-VALUE
           IF WS-ENV-OVERLONG = 'Y'
               PERFORM REPORT-ENV-OVERLONG
           END-IF
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN > ZERO
               EVALUATE FUNCTION UPPER-CASE(WS-ENV-TEXT(1:4))
                 WHEN 'NONE'
                   MOVE 'NONE' TO WS-WANT-DIAG-LINKS
                 WHEN 'SOME'
                   MOVE 'SOME' TO WS-WANT-DIAG-LINKS
                 WHEN OTHER
                   DISPLAY 'DRIVER: HARNESS_EXPECT_DIAG_LINKS holds ['
                           WS-ENV-TEXT(1:WS-SEED-LEN)
                           '] and NONE or SOME are accepted'
                   END-DISPLAY
                   MOVE 05 TO WS-EXIT-CODE
               END-EVALUATE
           END-IF.
      *
      * Reads the item named in WS-ENV-NAME as 'Y' or 'N'. WS-ENV-FLAG
      * holds the value read, and spaces when the item is unset.
       RESOLVE-YES-NO.
           MOVE SPACES TO WS-ENV-FLAG
           PERFORM ACCEPT-ENV-VALUE
           IF WS-ENV-OVERLONG = 'Y'
               PERFORM REPORT-ENV-OVERLONG
           END-IF
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN > ZERO
               EVALUATE FUNCTION UPPER-CASE(WS-ENV-TEXT(1:1))
                 WHEN 'Y'
                   MOVE 'Y' TO WS-ENV-FLAG
                 WHEN 'N'
                   MOVE 'N' TO WS-ENV-FLAG
                 WHEN OTHER
                   CONTINUE
               END-EVALUATE
               IF WS-ENV-FLAG = SPACES OR WS-SEED-LEN NOT = 1
                   MOVE SPACES TO WS-ENV-FLAG
                   DISPLAY 'DRIVER: ' FUNCTION TRIM(WS-ENV-NAME)
                           ' holds [' WS-ENV-TEXT(1:WS-SEED-LEN)
                           '] and Y or N are accepted'
                   END-DISPLAY
                   MOVE 05 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      * Accepts the spellings the runtime reads as true for a boolean
      * configuration item.
       RESOLVE-LS-FIXED.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "COB_LS_FIXED"
           END-ACCEPT
           MOVE FUNCTION UPPER-CASE(WS-ENV-TEXT(1:8)) TO WS-ENV-FLAG
           MOVE 'N' TO WS-LS-FIXED
           EVALUATE WS-ENV-FLAG
             WHEN '1'
             WHEN 'Y'
             WHEN 'T'
             WHEN 'ON'
             WHEN 'YES'
             WHEN 'TRUE'
               MOVE 'Y' TO WS-LS-FIXED
           END-EVALUATE.
      *
      * Replaces the request id of the loaded record when
      * HARNESS_REQUEST_ID supplied one, then holds the value the chain
      * will route on. The rest of the record is left as the fixture
      * wrote it.
       APPLY-REQUEST-ID-INPUT.
           IF WS-REQUEST-ID-INPUT NOT = SPACES
               MOVE WS-REQUEST-ID-INPUT TO CA-REQUEST-ID
               DISPLAY 'DRIVER: request id replaced by '
                       WS-REQUEST-ID-INPUT
               END-DISPLAY
           END-IF
           MOVE CA-REQUEST-ID TO WS-EFFECTIVE-REQUEST-ID.
      *
      *================================================================*
      * Derived expectations                                           *
      *================================================================*
      * Completes the expectations from the effective request id, from
      * the failure selections and from the seeds this program
      * supplied. Every value derived here is known before the chain
      * runs, so no expectation is taken from a capture.
       RESOLVE-EXPECTATIONS.
           PERFORM DERIVE-EXPECTED-PRODUCT
           PERFORM DERIVE-EXPECTED-POLICY-TYPE
           PERFORM DERIVE-EXPECTED-SEEDS
           PERFORM DERIVE-EXPECTED-SQLCODE
           PERFORM DERIVE-EXPECTED-EVENTS.
      *
      * The product table the case expects. An unset
      * HARNESS_EXPECT_PRODUCT selects MOTOR for request id '01AMOT'
      * and COMMERCIAL for '01ACOM', the two request ids the harness
      * generates a sample for, and NONE for every other value.
       DERIVE-EXPECTED-PRODUCT.
           IF WS-WANT-PRODUCT = SPACES
               EVALUATE WS-EFFECTIVE-REQUEST-ID
                 WHEN '01AMOT'
                   MOVE 'MOTOR' TO WS-WANT-PRODUCT
                 WHEN '01ACOM'
                   MOVE 'COMMERCIAL' TO WS-WANT-PRODUCT
                 WHEN OTHER
                   MOVE 'NONE' TO WS-WANT-PRODUCT
               END-EVALUATE
           END-IF
           EVALUATE WS-WANT-PRODUCT
             WHEN 'MOTOR'
               MOVE 'M' TO WS-PRODUCT-WANTED
             WHEN 'COMMERCIAL'
               MOVE 'C' TO WS-PRODUCT-WANTED
             WHEN 'ENDOWMENT'
               MOVE 'E' TO WS-PRODUCT-WANTED
             WHEN 'HOUSE'
               MOVE 'H' TO WS-PRODUCT-WANTED
             WHEN OTHER
               MOVE '?' TO WS-PRODUCT-WANTED
           END-EVALUATE.
      *
      * The letter the routing at [base/src/lgapdb01.cbl:184-207] moves
      * to DB2-POLICYTYPE, taken from the fourth character of the
      * effective request id for the four request ids it routes.
       DERIVE-EXPECTED-POLICY-TYPE.
           EVALUATE WS-EFFECTIVE-REQUEST-ID
             WHEN '01AEND'
             WHEN '01AHOU'
             WHEN '01AMOT'
             WHEN '01ACOM'
               MOVE WS-EFFECTIVE-REQUEST-ID(4:1)
                   TO WS-WANT-POLICY-TYPE
             WHEN OTHER
               MOVE '?' TO WS-WANT-POLICY-TYPE
           END-EVALUATE.
      *
      * The identity and timestamp the case expects. The values this
      * program seeded are used when it seeded them; otherwise the
      * values the shared seed items hold are used, which
      * sql_insert_policy.cbl resolves before the identity read-back
      * runs.
       DERIVE-EXPECTED-SEEDS.
           IF WS-SEED-SUPPLIED > ZERO
               MOVE WS-SEED-SUPPLIED TO WS-WANT-POLICYNUM
           ELSE
               MOVE HC-SEED-POLICYNUM TO WS-WANT-POLICYNUM
           END-IF
           IF WS-SEED-LCHG-SUPPLIED NOT = SPACES
               MOVE WS-SEED-LCHG-SUPPLIED TO WS-WANT-LASTCHANGED
           ELSE
               MOVE HC-SEED-LASTCHANGED TO WS-WANT-LASTCHANGED
           END-IF
           MOVE 'N' TO WS-WANT-IDENTITY
           IF WS-WANT-POLICY-SQL = 'Y' AND WS-INJ-POL-SQLCODE = ZERO
               MOVE 'Y' TO WS-WANT-IDENTITY
           END-IF.
      *
      * The result the most recent SQL operation of the case reports.
      * A product insert runs last and reports the subtype selection
      * [base/src/lgapdb01.cbl:449-471,499-545]; a POLICY insert that
      * reported a failure returns before any product insert
      * [base/src/lgapdb01.cbl:290-305]; a case that reaches no SQL
      * block leaves the value this program seeded.
       DERIVE-EXPECTED-SQLCODE.
           IF WS-WANT-POLICY-SQL NOT = 'Y'
               MOVE ZERO TO WS-WANT-SQLCODE
           ELSE
               IF WS-INJ-POL-SQLCODE NOT = ZERO
                   MOVE WS-INJ-POL-SQLCODE TO WS-WANT-SQLCODE
               ELSE
                   IF WS-PRODUCT-WANTED = '?'
                       MOVE ZERO TO WS-WANT-SQLCODE
                   ELSE
                       MOVE WS-INJ-SUB-SQLCODE TO WS-WANT-SQLCODE
                   END-IF
               END-IF
           END-IF
           IF WS-INJ-VSAM-RESP = ZERO
               MOVE WS-RESP-NORMAL TO WS-WANT-VSAM-RESP
           ELSE
               MOVE WS-INJ-VSAM-RESP TO WS-WANT-VSAM-RESP
           END-IF.
      *
      * The number of events the case expects to have been stamped from
      * HC-EVENT-SEQ: one for the POLICY insert, one for each read-back,
      * one for the product insert, one for the write and one for the
      * abend site.
       DERIVE-EXPECTED-EVENTS.
           MOVE ZERO TO WS-WANT-EVENTS
           IF WS-WANT-POLICY-SQL = 'Y'
               ADD 1 TO WS-WANT-EVENTS
               END-ADD
           END-IF
           IF WS-WANT-IDENTITY = 'Y'
               ADD 2 TO WS-WANT-EVENTS
               END-ADD
           END-IF
           IF WS-PRODUCT-WANTED NOT = '?'
               ADD 1 TO WS-WANT-EVENTS
               END-ADD
           END-IF
           IF WS-WANT-VSAM = 'Y'
               ADD 1 TO WS-WANT-EVENTS
               END-ADD
           END-IF
           IF WS-WANT-ABEND NOT = 'NONE'
               ADD 1 TO WS-WANT-EVENTS
               END-ADD
           END-IF.
      *
      *================================================================*
      * Shared state seeding                                           *
      *================================================================*
       SEED-SHARED-STATE.
           PERFORM SEED-EIB-FIELDS
           PERFORM SEED-SQLCA
           PERFORM SEED-CAPTURE-STATE
           PERFORM SEED-IDENTITY-SEED
           PERFORM SEED-TIMESTAMP-SEED.
      *
      * The five fields the chain reads without declaring. EIBCALEN
      * carries the length of the COMMAREA the chain is called with;
      * the other four reach debug and diagnostic fields only.
       SEED-EIB-FIELDS.
           INITIALIZE DFHEIBLK-SURROGATE
           MOVE 'HARN' TO EIBTRNID
           MOVE 'HTRM' TO EIBTRMID
           MOVE 1 TO EIBTASKN
           MOVE WS-CALL-LENGTH TO EIBCALEN
           MOVE ZERO TO EIBRESP2.
      *
      * The result of the most recent SQL operation, as the SQL stubs
      * of the harness report it.
       SEED-SQLCA.
           INITIALIZE SQLCA
           MOVE ZERO TO SQLCODE.
      *
      * INITIALIZE clears every captured value, counter, ordinal and
      * name of the shared capture group; the moves below set each
      * presence flag and the order-violation flag to 'N', the value
      * that reports a statement not yet captured, and set the two
      * chain-traversal flags to the same value. The four HC-INJECT
      * items are set from the case inputs, so a selection made for an
      * earlier run of this program cannot reach this one.
       SEED-CAPTURE-STATE.
           INITIALIZE HC-CAPTURE-STATE
           MOVE 'N' TO HC-ORDER-VIOLATION
           MOVE 'N' TO HC-POL-PRESENT
           MOVE 'N' TO HC-IDENT-PRESENT
           MOVE 'N' TO HC-LCHG-PRESENT
           MOVE 'N' TO HC-MOT-PRESENT
           MOVE 'N' TO HC-COM-PRESENT
           MOVE 'N' TO HC-END-PRESENT
           MOVE 'N' TO HC-HOU-PRESENT
           MOVE 'N' TO HC-VSAM-PRESENT
           MOVE 'N' TO HC-ABEND-PRESENT
           MOVE 'N' TO HC-CHAIN-DB2-PRESENT
           MOVE 'N' TO HC-CHAIN-VSAM-PRESENT
           MOVE ZERO TO HC-CHAIN-DB2-CALEN
           MOVE ZERO TO HC-CHAIN-VSAM-CALEN
           MOVE WS-INJ-POL-SQLCODE TO HC-INJECT-POL-SQLCODE
           MOVE WS-INJ-SUB-SQLCODE TO HC-INJECT-SUB-SQLCODE
           MOVE WS-INJ-VSAM-RESP TO HC-INJECT-VSAM-RESP
           MOVE WS-INJ-VSAM-RESP2 TO HC-INJECT-VSAM-RESP2.
      *
      * HARNESS_POLICY_NUMBER reaches HC-SEED-POLICYNUM when it holds
      * at most nine digits and a value above zero. The item is left
      * at zero otherwise.
       SEED-IDENTITY-SEED.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "HARNESS_POLICY_NUMBER"
           END-ACCEPT
           MOVE ZERO TO WS-SEED-POLICYNUM
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN > ZERO AND WS-SEED-LEN NOT > 9
               PERFORM SCAN-SEED-DIGITS
               IF WS-HAS-DIGIT = 'Y' AND WS-HAS-NON-DIGIT = 'N'
                   COMPUTE WS-SEED-POLICYNUM =
                       FUNCTION NUMVAL(WS-ENV-TEXT(1:WS-SEED-LEN))
                   END-COMPUTE
               END-IF
           END-IF
           IF WS-SEED-POLICYNUM > ZERO
               MOVE WS-SEED-POLICYNUM TO HC-SEED-POLICYNUM
               MOVE WS-SEED-POLICYNUM TO WS-SEED-SUPPLIED
           END-IF.
      *
      * HARNESS_LASTCHANGED reaches HC-SEED-LASTCHANGED when it holds
      * exactly 26 characters and none of them is a space. The item is
      * left at spaces otherwise.
       SEED-TIMESTAMP-SEED.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "HARNESS_LASTCHANGED"
           END-ACCEPT
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN = 26
               MOVE ZERO TO WS-SPACE-COUNT
               INSPECT WS-ENV-TEXT(1:26) TALLYING WS-SPACE-COUNT
                   FOR ALL SPACE
               IF WS-SPACE-COUNT = ZERO
                   MOVE WS-ENV-TEXT(1:26) TO HC-SEED-LASTCHANGED
                   MOVE WS-ENV-TEXT(1:26) TO WS-SEED-LCHG-SUPPLIED
               END-IF
           END-IF.
      *
      * Sets WS-SEED-LEN to the position of the last character of
      * WS-ENV-TEXT that is not a space, and to zero when every
      * character is one.
       TRIM-ENV-TEXT.
           MOVE ZERO TO WS-SEED-LEN
           PERFORM VARYING WS-TRIM-IX FROM 255 BY -1
                   UNTIL WS-TRIM-IX < 1 OR WS-SEED-LEN > ZERO
               IF WS-ENV-TEXT(WS-TRIM-IX:1) NOT = SPACE
                   MOVE WS-TRIM-IX TO WS-SEED-LEN
               END-IF
           END-PERFORM.
      *
      * Reports whether WS-ENV-TEXT(1:WS-SEED-LEN) holds digits only.
       SCAN-SEED-DIGITS.
           MOVE 'N' TO WS-HAS-DIGIT
           MOVE 'N' TO WS-HAS-NON-DIGIT
           PERFORM VARYING WS-TRIM-IX FROM 1 BY 1
                   UNTIL WS-TRIM-IX > WS-SEED-LEN
               IF WS-ENV-TEXT(WS-TRIM-IX:1) IS NUMERIC
                   MOVE 'Y' TO WS-HAS-DIGIT
               ELSE
                   MOVE 'Y' TO WS-HAS-NON-DIGIT
               END-IF
           END-PERFORM.

      *
      *================================================================*
      * Sample record                                                  *
      *================================================================*
      * Loads the first record standard input carries into the COMMAREA.
      * The record holds 32,500 characters. A stream that carries no
      * record leaves the read at end, file status '10', and a record
      * wider than the 32,500 characters read leaves file status '06';
      * each is reported and ends the run with status 4, so the chain is
      * never called with a blank or a truncated COMMAREA. A stream that
      * no reader can be opened on is reported the same way. None of
      * them waits for a record that is not coming: an empty stream, a
      * closed standard input and /dev/null each end the read at once.
       READ-SAMPLE-RECORD.
           OPEN INPUT SAMPLE-FILE
           IF WS-SAMPLE-STATUS NOT = '00'
               DISPLAY 'DRIVER: open input failed on SAMPLEFILE, '
                       'the record read from standard input, file '
                       'status ' WS-SAMPLE-STATUS
               END-DISPLAY
               MOVE 04 TO WS-EXIT-CODE
           ELSE
               READ SAMPLE-FILE
                   AT END
                       CONTINUE
               END-READ
               IF WS-SAMPLE-STATUS = '00'
                   MOVE SAMPLE-REC TO WS-COMMAREA-CHARS
                   MOVE SAMPLE-REC TO WS-FIXTURE-CHARS
               ELSE
                   DISPLAY 'DRIVER: read failed on SAMPLEFILE, the '
                           'record read from standard input, file '
                           'status ' WS-SAMPLE-STATUS
                   END-DISPLAY
                   IF WS-SAMPLE-STATUS = '10'
                       DISPLAY 'DRIVER:   standard input carried no '
                               'record; redirect standard input from '
                               'the generated 32500-character sample '
                               'record of the case'
                       END-DISPLAY
                   END-IF
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
               CLOSE SAMPLE-FILE
               IF WS-SAMPLE-STATUS NOT = '00'
                   DISPLAY 'DRIVER: close failed on SAMPLEFILE, the '
                           'record read from standard input, file '
                           'status ' WS-SAMPLE-STATUS
                   END-DISPLAY
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      *================================================================*
      * Chain execution                                                *
      *================================================================*
      * Sets the COMMAREA length the chain reads from the case input,
      * records that value, and calls the first program of the chain
      * once. LGAPDB01 and LGAPVS01 are called by the chain itself. A
      * call that could not be made leaves WS-CALL-FAILED at 'Y' and
      * the run ends with status 7, the status that reports a module
      * the runtime could not resolve.
       EXECUTE-CHAIN.
           MOVE WS-CALL-LENGTH TO EIBCALEN
           MOVE EIBCALEN TO WS-EIBCALEN-AT-CALL
           CALL "LGAPOL01" USING WS-COMMAREA
               ON EXCEPTION
                   MOVE 'Y' TO WS-CALL-FAILED
                   DISPLAY 'DRIVER: module LGAPOL01 could not be '
                           'called; set COB_LIBRARY_PATH to the '
                           'directory holding the compiled harness '
                           'modules'
                   END-DISPLAY
           END-CALL.
      *
      *================================================================*
      * Post-chain record                                              *
      *================================================================*
      * Writes the returned COMMAREA as one line of 32,500 characters,
      * the length the extraction step decodes by absolute offset, into
      * the descriptor WS-POST-PATH names.
       WRITE-POST-RECORD.
           MOVE WS-COMMAREA-CHARS TO POST-REC
           PERFORM CREATE-POST-FILE.
      *
      * Opens descriptor 3, writes the one record and closes it. The
      * open reaches the open file the caller placed on that descriptor,
      * composes no directory path and resolves no name. An open, write
      * or close that does not return '00' names the descriptor and ends
      * the run with status 4.
       CREATE-POST-FILE.
           OPEN OUTPUT POST-FILE
           IF WS-POST-STATUS NOT = '00'
               DISPLAY 'DRIVER: open output failed on POSTFILE, '
                       'descriptor 3 through ' WS-POST-PATH
                       ', file status ' WS-POST-STATUS
               END-DISPLAY
               PERFORM REPORT-POST-DESCRIPTOR
           ELSE
               WRITE POST-REC
               END-WRITE
               IF WS-POST-STATUS NOT = '00'
                   DISPLAY 'DRIVER: write failed on POSTFILE, '
                           'descriptor 3 through ' WS-POST-PATH
                           ', file status ' WS-POST-STATUS
                   END-DISPLAY
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
               CLOSE POST-FILE
               IF WS-POST-STATUS NOT = '00'
                   DISPLAY 'DRIVER: close failed on POSTFILE, '
                           'descriptor 3 through ' WS-POST-PATH
                           ', file status ' WS-POST-STATUS
                   END-DISPLAY
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      * Names the redirection descriptor 3 requires and ends the run
      * with status 4. File status 30 is the status the open returns for
      * a descriptor the caller did not open.
       REPORT-POST-DESCRIPTOR.
           DISPLAY 'DRIVER:   descriptor 3 carries the post-chain '
                   'record; open it on the file that record is '
                   'written into, as in 3>commarea_post.dat'
           END-DISPLAY
           MOVE 04 TO WS-EXIT-CODE.
      *
      *================================================================*
      * Capture file                                                   *
      *================================================================*
      * Opens descriptor 4, the descriptor WS-CAPT-PATH names, and
      * records that the emitted lines have somewhere to go. The open
      * reaches the open file the caller placed on that descriptor,
      * composes no directory path and resolves no name.
       CREATE-CAPTURE-FILE.
           OPEN OUTPUT CAPTURE-FILE
           IF WS-CAPT-STATUS NOT = '00'
               DISPLAY 'DRIVER: open output failed on CAPTFILE, '
                       'descriptor 4 through ' WS-CAPT-PATH
                       ', file status ' WS-CAPT-STATUS
               END-DISPLAY
               PERFORM REPORT-CAPT-DESCRIPTOR
           ELSE
               MOVE 'Y' TO WS-CAPT-OPEN
           END-IF.
      *
      * Names the redirection descriptor 4 requires and ends the run
      * with status 4. File status 30 is the status the open returns for
      * a descriptor the caller did not open.
       REPORT-CAPT-DESCRIPTOR.
           DISPLAY 'DRIVER:   descriptor 4 carries the capture lines; '
                   'open it on the file those lines are written into, '
                   'as in 4>captures.txt'
           END-DISPLAY
           MOVE 04 TO WS-EXIT-CODE.
      *
       CLOSE-CAPTURE-FILE.
           IF WS-CAPT-OPEN = 'Y'
               CLOSE CAPTURE-FILE
               MOVE 'N' TO WS-CAPT-OPEN
               IF WS-CAPT-STATUS NOT = '00'
                   DISPLAY 'DRIVER: close failed on CAPTFILE, '
                           'descriptor 4 through ' WS-CAPT-PATH
                           ', file status ' WS-CAPT-STATUS
                   END-DISPLAY
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      *================================================================*
      * Run header and COMMAREA extract                                *
      *================================================================*
       DISPLAY-RUN-HEADER.
           DISPLAY 'DRIVER: case ' FUNCTION TRIM(WS-CASE)
                   ' fixture ' FUNCTION TRIM(WS-FIXTURE)
                   ' request id ' CA-REQUEST-ID
           END-DISPLAY
           DISPLAY 'DRIVER: SAMPLEFILE read from standard input'
           END-DISPLAY
           DISPLAY 'DRIVER: POSTFILE   written into descriptor 3, '
                   'opened as ' WS-POST-PATH
           END-DISPLAY
           DISPLAY 'DRIVER: CAPTFILE   written into descriptor 4, '
                   'opened as ' WS-CAPT-PATH
           END-DISPLAY.
      *
      * Replaces every byte of WS-LOG-TEXT outside the printable
      * range with a full stop, leaving the printable bytes as they
      * stand.
       SANITIZE-LOG-TEXT.
           PERFORM VARYING WS-LOG-IX FROM 1 BY 1
                   UNTIL WS-LOG-IX IS GREATER THAN 100
               MOVE WS-LOG-TEXT(WS-LOG-IX:1) TO WS-LOG-CHAR
               IF WS-LOG-CHAR IS LESS THAN SPACE
                   OR WS-LOG-CHAR IS GREATER THAN '~'
                   MOVE '.' TO WS-LOG-TEXT(WS-LOG-IX:1)
               END-IF
           END-PERFORM.
      *
      * The 28-character header and the 72-character common section of
      * the returned record, then the amount fields of the overlay the
      * request id selects. The whole record is in the post file.
       DISPLAY-COMMAREA-EXTRACT.
           DISPLAY 'DRIVER: post-chain COMMAREA characters 1-100'
           END-DISPLAY
           MOVE WS-COMMAREA-CHARS(1:100) TO WS-LOG-TEXT
           PERFORM SANITIZE-LOG-TEXT
           DISPLAY WS-LOG-TEXT
           END-DISPLAY
           EVALUATE CA-REQUEST-ID
             WHEN '01AMOT'
               DISPLAY 'DRIVER: CA-M-PREMIUM ' CA-M-PREMIUM
               END-DISPLAY
             WHEN '01ACOM'
               DISPLAY 'DRIVER: CA-B-FirePremium '
                       CA-B-FirePremium
               END-DISPLAY
               DISPLAY 'DRIVER: CA-B-CrimePremium '
                       CA-B-CrimePremium
               END-DISPLAY
               DISPLAY 'DRIVER: CA-B-FloodPremium '
                       CA-B-FloodPremium
               END-DISPLAY
               DISPLAY 'DRIVER: CA-B-WeatherPremium '
                       CA-B-WeatherPremium
               END-DISPLAY
             WHEN OTHER
               MOVE SPACES TO WS-LOG-TEXT
               MOVE CA-REQUEST-ID TO WS-LOG-TEXT(1:6)
               PERFORM SANITIZE-LOG-TEXT
               DISPLAY 'DRIVER: request id ' WS-LOG-TEXT(1:6)
                       ' selects no requested overlay amount'
               END-DISPLAY
           END-EVALUATE.
      *
      *================================================================*
      * Capture line assembly                                          *
      *================================================================*
      * Writes WS-KEY-NAME=WS-VALUE as one line of the capture file and
      * the same text to the log. The name is written at its trimmed
      * length, then '=', then the value at its trimmed length, so a
      * value of all spaces leaves nothing after '='.
       EMIT-VALUE.
           PERFORM TRIM-KEY-NAME
           PERFORM TRIM-VALUE
           MOVE SPACES TO WS-LINE
           MOVE 1 TO WS-STRING-PTR
           IF WS-KEY-LEN > ZERO
               STRING WS-KEY-NAME(1:WS-KEY-LEN) DELIMITED BY SIZE
                   INTO WS-LINE WITH POINTER WS-STRING-PTR
               END-STRING
           END-IF
           STRING '=' DELIMITED BY SIZE
               INTO WS-LINE WITH POINTER WS-STRING-PTR
           END-STRING
           IF WS-VALUE-LEN > ZERO
               STRING WS-VALUE(1:WS-VALUE-LEN) DELIMITED BY SIZE
                   INTO WS-LINE WITH POINTER WS-STRING-PTR
               END-STRING
           END-IF
           COMPUTE WS-LINE-LEN = WS-STRING-PTR - 1
           END-COMPUTE
           MOVE WS-LINE TO CAPTURE-REC
           WRITE CAPTURE-REC
           END-WRITE
           IF WS-CAPT-STATUS NOT = '00'
               DISPLAY 'DRIVER: write failed on CAPTFILE, '
                       'descriptor 4 through ' WS-CAPT-PATH
                       ', file status ' WS-CAPT-STATUS
               END-DISPLAY
               MOVE 04 TO WS-EXIT-CODE
           END-IF
           DISPLAY WS-LINE(1:WS-LINE-LEN)
           END-DISPLAY
           MOVE SPACES TO WS-KEY-NAME
           MOVE SPACES TO WS-VALUE.
      *
      * Formats WS-INT-VALUE as a plain decimal integer carrying no
      * padding, and a leading minus only when the value is negative,
      * then emits the line.
       EMIT-INTEGER.
           MOVE WS-INT-VALUE TO WS-INT-EDIT
           MOVE ZERO TO WS-INT-FIRST
           PERFORM VARYING WS-TRIM-IX FROM 1 BY 1
                   UNTIL WS-TRIM-IX > 11 OR WS-INT-FIRST > ZERO
               IF WS-INT-EDIT(WS-TRIM-IX:1) NOT = SPACE
                   MOVE WS-TRIM-IX TO WS-INT-FIRST
               END-IF
           END-PERFORM
           IF WS-INT-FIRST = ZERO
               MOVE 11 TO WS-INT-FIRST
           END-IF
           COMPUTE WS-INT-LEN = 12 - WS-INT-FIRST
           END-COMPUTE
           MOVE SPACES TO WS-VALUE
           MOVE WS-INT-EDIT(WS-INT-FIRST:WS-INT-LEN) TO WS-VALUE
           PERFORM EMIT-VALUE.
      *
      * Emits WS-HEX-SOURCE(1:WS-HEX-SOURCE-LEN) as two upper-case
      * hexadecimal digits per character, so every character of the
      * value reaches the capture file: a space is written as '20' and
      * is neither removed nor merged with the characters beside it.
      * The emitted line therefore carries twice as many characters as
      * the value holds, and a value whose trailing characters are
      * spaces is as long as one whose trailing characters are not.
       EMIT-HEX-VALUE.
           PERFORM ENCODE-HEX
           MOVE SPACES TO WS-VALUE
           IF WS-HEX-LEN > ZERO
               MOVE WS-HEX-TEXT(1:WS-HEX-LEN) TO WS-VALUE
           END-IF
           PERFORM EMIT-VALUE.
      *
      * Writes the two hexadecimal digits of each character of
      * WS-HEX-SOURCE(1:WS-HEX-SOURCE-LEN) into WS-HEX-TEXT and leaves
      * the number of digits written in WS-HEX-LEN. FUNCTION ORD
      * returns the position of the character in the runtime character
      * set, counted from one, so the value of the character is one
      * less.
       ENCODE-HEX.
           MOVE SPACES TO WS-HEX-TEXT
           MOVE ZERO TO WS-HEX-LEN
           PERFORM VARYING WS-HEX-IX FROM 1 BY 1
                   UNTIL WS-HEX-IX > WS-HEX-SOURCE-LEN
               MOVE WS-HEX-SOURCE(WS-HEX-IX:1) TO WS-HEX-CHAR
               COMPUTE WS-HEX-VALUE = FUNCTION ORD(WS-HEX-CHAR) - 1
               END-COMPUTE
               DIVIDE WS-HEX-VALUE BY 16 GIVING WS-HEX-HIGH
                   REMAINDER WS-HEX-LOW
               END-DIVIDE
               ADD 1 TO WS-HEX-LEN
               END-ADD
               MOVE WS-HEX-DIGITS(WS-HEX-HIGH + 1:1)
                   TO WS-HEX-TEXT(WS-HEX-LEN:1)
               ADD 1 TO WS-HEX-LEN
               END-ADD
               MOVE WS-HEX-DIGITS(WS-HEX-LOW + 1:1)
                   TO WS-HEX-TEXT(WS-HEX-LEN:1)
           END-PERFORM.
      *
      * Sets WS-KEY-LEN to the position of the last character of
      * WS-KEY-NAME that is not a space.
       TRIM-KEY-NAME.
           MOVE ZERO TO WS-KEY-LEN
           PERFORM VARYING WS-TRIM-IX FROM 40 BY -1
                   UNTIL WS-TRIM-IX < 1 OR WS-KEY-LEN > ZERO
               IF WS-KEY-NAME(WS-TRIM-IX:1) NOT = SPACE
                   MOVE WS-TRIM-IX TO WS-KEY-LEN
               END-IF
           END-PERFORM.
      *
      * Sets WS-VALUE-LEN to the position of the last character of
      * WS-VALUE that is not a space, and to zero when every character
      * is one.
       TRIM-VALUE.
           MOVE ZERO TO WS-VALUE-LEN
           PERFORM VARYING WS-TRIM-IX FROM 255 BY -1
                   UNTIL WS-TRIM-IX < 1 OR WS-VALUE-LEN > ZERO
               IF WS-VALUE(WS-TRIM-IX:1) NOT = SPACE
                   MOVE WS-TRIM-IX TO WS-VALUE-LEN
               END-IF
           END-PERFORM.
      *
      *================================================================*
      * Run captures                                                   *
      *================================================================*
       EMIT-RUN-CAPTURES.
           MOVE 'CASE' TO WS-KEY-NAME
           MOVE WS-CASE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'FIXTURE' TO WS-KEY-NAME
           MOVE WS-FIXTURE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EIBCALEN_AT_CALL' TO WS-KEY-NAME
           MOVE WS-EIBCALEN-AT-CALL TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'CASE_REQUEST_ID_EFFECTIVE' TO WS-KEY-NAME
           MOVE WS-EFFECTIVE-REQUEST-ID TO WS-VALUE
           PERFORM EMIT-VALUE
           PERFORM EMIT-CASE-INPUTS
           PERFORM EMIT-CASE-EXPECTATIONS
           PERFORM EMIT-CHAIN-CAPTURES.
      *
      * The four failure selections handed to the emulated services.
       EMIT-CASE-INPUTS.
           MOVE 'INJECT_POLICY_SQLCODE' TO WS-KEY-NAME
           MOVE WS-INJ-POL-SQLCODE TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'INJECT_SUBTYPE_SQLCODE' TO WS-KEY-NAME
           MOVE WS-INJ-SUB-SQLCODE TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'INJECT_VSAM_RESP' TO WS-KEY-NAME
           MOVE WS-INJ-VSAM-RESP TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'INJECT_VSAM_RESP2' TO WS-KEY-NAME
           MOVE WS-INJ-VSAM-RESP2 TO WS-INT-VALUE
           PERFORM EMIT-INTEGER.
      *
      * What the case required of the run, as the checks below applied
      * it, including the values derived from the effective request id
      * and from the seeds this program supplied.
       EMIT-CASE-EXPECTATIONS.
           MOVE 'EXPECT_RETURN_CODE' TO WS-KEY-NAME
           MOVE WS-WANT-RETURN-CODE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_ABEND' TO WS-KEY-NAME
           MOVE WS-WANT-ABEND TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_PRODUCT' TO WS-KEY-NAME
           MOVE WS-WANT-PRODUCT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_POLICY_SQL' TO WS-KEY-NAME
           MOVE WS-WANT-POLICY-SQL TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_VSAM' TO WS-KEY-NAME
           MOVE WS-WANT-VSAM TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_VALUES' TO WS-KEY-NAME
           MOVE WS-WANT-VALUES TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_PRODUCT_VALUES' TO WS-KEY-NAME
           MOVE WS-WANT-PRODUCT-VALUES TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_DIAG_LINKS' TO WS-KEY-NAME
           MOVE WS-WANT-DIAG-LINKS TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_IDENTITY_READBACKS' TO WS-KEY-NAME
           MOVE WS-WANT-IDENTITY TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_POLICY_TYPE' TO WS-KEY-NAME
           MOVE WS-WANT-POLICY-TYPE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_POLICY_NUMBER' TO WS-KEY-NAME
           MOVE WS-WANT-POLICYNUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'EXPECT_LASTCHANGED' TO WS-KEY-NAME
           MOVE WS-WANT-LASTCHANGED TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EXPECT_SQLCODE' TO WS-KEY-NAME
           MOVE WS-WANT-SQLCODE TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'EXPECT_VSAM_RESP' TO WS-KEY-NAME
           MOVE WS-WANT-VSAM-RESP TO WS-INT-VALUE
           PERFORM EMIT-INTEGER.
      *
      * The chain-traversal witness of each program the chain reaches
      * beyond the first: whether the program was entered and the
      * COMMAREA length in force inside it, as the first emulated
      * service that program calls observed it. The two links state
      * LENGTH(32500) at [base/src/lgapol01.cbl:121-124] and
      * [base/src/lgapdb01.cbl:243-246].
       EMIT-CHAIN-CAPTURES.
           MOVE 'LINK_DB2_PRESENT' TO WS-KEY-NAME
           MOVE HC-CHAIN-DB2-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'LINK_DB2_CALEN' TO WS-KEY-NAME
           MOVE HC-CHAIN-DB2-CALEN TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'LINK_VSAM_PRESENT' TO WS-KEY-NAME
           MOVE HC-CHAIN-VSAM-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'LINK_VSAM_CALEN' TO WS-KEY-NAME
           MOVE HC-CHAIN-VSAM-CALEN TO WS-INT-VALUE
           PERFORM EMIT-INTEGER.
      *
      *================================================================*
      * Returned COMMAREA captures                                     *
      *================================================================*
      * The request header, the common policy section and the amount
      * fields of the overlay the request id selects, as the chain
      * returned them.
       EMIT-COMMAREA-CAPTURES.
           MOVE 'CA_REQUEST_ID' TO WS-KEY-NAME
           MOVE CA-REQUEST-ID TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_RETURN_CODE' TO WS-KEY-NAME
           MOVE CA-RETURN-CODE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_CUSTOMER_NUM' TO WS-KEY-NAME
           MOVE CA-CUSTOMER-NUM TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_POLICY_NUM' TO WS-KEY-NAME
           MOVE CA-POLICY-NUM TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_ISSUE_DATE' TO WS-KEY-NAME
           MOVE CA-ISSUE-DATE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_EXPIRY_DATE' TO WS-KEY-NAME
           MOVE CA-EXPIRY-DATE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_LASTCHANGED' TO WS-KEY-NAME
           MOVE CA-LASTCHANGED TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_BROKERID' TO WS-KEY-NAME
           MOVE CA-BROKERID TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_BROKERSREF' TO WS-KEY-NAME
           MOVE CA-BROKERSREF TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CA_PAYMENT' TO WS-KEY-NAME
           MOVE CA-PAYMENT TO WS-VALUE
           PERFORM EMIT-VALUE
           EVALUATE CA-REQUEST-ID
             WHEN '01AMOT'
               MOVE 'CA_M_PREMIUM' TO WS-KEY-NAME
               MOVE CA-M-PREMIUM TO WS-VALUE
               PERFORM EMIT-VALUE
             WHEN '01ACOM'
               MOVE 'CA_B_FIREPREMIUM' TO WS-KEY-NAME
               MOVE CA-B-FirePremium TO WS-VALUE
               PERFORM EMIT-VALUE
               MOVE 'CA_B_CRIMEPREMIUM' TO WS-KEY-NAME
               MOVE CA-B-CrimePremium TO WS-VALUE
               PERFORM EMIT-VALUE
               MOVE 'CA_B_FLOODPREMIUM' TO WS-KEY-NAME
               MOVE CA-B-FloodPremium TO WS-VALUE
               PERFORM EMIT-VALUE
               MOVE 'CA_B_WEATHERPREMIUM' TO WS-KEY-NAME
               MOVE CA-B-WeatherPremium TO WS-VALUE
               PERFORM EMIT-VALUE
           END-EVALUATE.

      *
      *================================================================*
      * Policy insert captures                                         *
      *================================================================*
      * The seven host values the INSERT INTO POLICY block passed, then
      * the identity and the timestamp the chain read back.
       EMIT-POLICY-CAPTURES.
           MOVE 'SQL_POLICY_PRESENT' TO WS-KEY-NAME
           MOVE HC-POL-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_POLICY_COUNT' TO WS-KEY-NAME
           MOVE HC-POL-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_POLICY_SEQ' TO WS-KEY-NAME
           MOVE HC-POL-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_POLICY_CUSTOMERNUM' TO WS-KEY-NAME
           MOVE HC-POL-CUSTOMERNUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_POLICY_ISSUEDATE' TO WS-KEY-NAME
           MOVE HC-POL-ISSUE-DATE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_POLICY_EXPIRYDATE' TO WS-KEY-NAME
           MOVE HC-POL-EXPIRY-DATE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_POLICY_POLICYTYPE' TO WS-KEY-NAME
           MOVE HC-POL-POLICYTYPE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_POLICY_BROKERID' TO WS-KEY-NAME
           MOVE HC-POL-BROKERID TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_POLICY_BROKERSREF' TO WS-KEY-NAME
           MOVE HC-POL-BROKERSREF TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_POLICY_PAYMENT' TO WS-KEY-NAME
           MOVE HC-POL-PAYMENT TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_POLICY_ASSIGNED_NUMBER' TO WS-KEY-NAME
           MOVE HC-IDENT-POLICYNUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_POLICY_ASSIGNED_LASTCHANGED' TO WS-KEY-NAME
           MOVE HC-LCHG-LASTCHANGED TO WS-VALUE
           PERFORM EMIT-VALUE.
      *
      *================================================================*
      * Motor insert captures                                          *
      *================================================================*
      * The ten host values the INSERT INTO MOTOR block passed.
       EMIT-MOTOR-CAPTURES.
           MOVE 'SQL_MOTOR_PRESENT' TO WS-KEY-NAME
           MOVE HC-MOT-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_MOTOR_COUNT' TO WS-KEY-NAME
           MOVE HC-MOT-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_MOTOR_SEQ' TO WS-KEY-NAME
           MOVE HC-MOT-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_MOTOR_POLICYNUM' TO WS-KEY-NAME
           MOVE HC-MOT-POLICYNUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_MOTOR_MAKE' TO WS-KEY-NAME
           MOVE HC-MOT-MAKE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_MOTOR_MODEL' TO WS-KEY-NAME
           MOVE HC-MOT-MODEL TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_MOTOR_VALUE' TO WS-KEY-NAME
           MOVE HC-MOT-VALUE TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_MOTOR_REGNUMBER' TO WS-KEY-NAME
           MOVE HC-MOT-REGNUMBER TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_MOTOR_COLOUR' TO WS-KEY-NAME
           MOVE HC-MOT-COLOUR TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_MOTOR_CC' TO WS-KEY-NAME
           MOVE HC-MOT-CC TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_MOTOR_MANUFACTURED' TO WS-KEY-NAME
           MOVE HC-MOT-MANUFACTURED TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_MOTOR_PREMIUM' TO WS-KEY-NAME
           MOVE HC-MOT-PREMIUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_MOTOR_ACCIDENTS' TO WS-KEY-NAME
           MOVE HC-MOT-ACCIDENTS TO WS-INT-VALUE
           PERFORM EMIT-INTEGER.
      *
      *================================================================*
      * Commercial insert captures                                     *
      *================================================================*
      * The twenty host values the INSERT INTO COMMERCIAL block passed,
      * in the order the columns are listed there.
       EMIT-COMMERCIAL-CAPTURES.
           MOVE 'SQL_COMMERCIAL_PRESENT' TO WS-KEY-NAME
           MOVE HC-COM-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_COUNT' TO WS-KEY-NAME
           MOVE HC-COM-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_SEQ' TO WS-KEY-NAME
           MOVE HC-COM-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_POLICYNUM' TO WS-KEY-NAME
           MOVE HC-COM-POLICYNUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_REQUESTDATE' TO WS-KEY-NAME
           MOVE HC-COM-LASTCHANGED TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_STARTDATE' TO WS-KEY-NAME
           MOVE HC-COM-ISSUE-DATE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_RENEWALDATE' TO WS-KEY-NAME
           MOVE HC-COM-EXPIRY-DATE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_ADDRESS' TO WS-KEY-NAME
           MOVE HC-COM-ADDRESS TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_ZIPCODE' TO WS-KEY-NAME
           MOVE HC-COM-POSTCODE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_LATITUDEN' TO WS-KEY-NAME
           MOVE HC-COM-LATITUDE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_LONGITUDEW' TO WS-KEY-NAME
           MOVE HC-COM-LONGITUDE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_CUSTOMER' TO WS-KEY-NAME
           MOVE HC-COM-CUSTOMER TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_PROPERTYTYPE' TO WS-KEY-NAME
           MOVE HC-COM-PROPTYPE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_COMMERCIAL_FIREPERIL' TO WS-KEY-NAME
           MOVE HC-COM-FIREPERIL TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_FIREPREMIUM' TO WS-KEY-NAME
           MOVE HC-COM-FIREPREMIUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_CRIMEPERIL' TO WS-KEY-NAME
           MOVE HC-COM-CRIMEPERIL TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_CRIMEPREMIUM' TO WS-KEY-NAME
           MOVE HC-COM-CRIMEPREMIUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_FLOODPERIL' TO WS-KEY-NAME
           MOVE HC-COM-FLOODPERIL TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_FLOODPREMIUM' TO WS-KEY-NAME
           MOVE HC-COM-FLOODPREMIUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_WEATHERPERIL' TO WS-KEY-NAME
           MOVE HC-COM-WEATHERPERIL TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_WEATHERPREMIUM' TO WS-KEY-NAME
           MOVE HC-COM-WEATHERPREMIUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_STATUS' TO WS-KEY-NAME
           MOVE HC-COM-STATUS TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_COMMERCIAL_REJECTIONREASON' TO WS-KEY-NAME
           MOVE HC-COM-REJECTREASON TO WS-VALUE
           PERFORM EMIT-VALUE.
      *
      *================================================================*
      * Remaining product captures and SQL bookkeeping                 *
      *================================================================*
      * The two product inserts the two generated samples do not reach,
      * each with its presence flag, counter, ordinal and host values.
      * A case that routes to neither leaves both groups at the state
      * SEED-CAPTURE-STATE set.
       EMIT-OTHER-PRODUCT-CAPTURES.
           MOVE 'SQL_ENDOWMENT_PRESENT' TO WS-KEY-NAME
           MOVE HC-END-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_ENDOWMENT_COUNT' TO WS-KEY-NAME
           MOVE HC-END-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_ENDOWMENT_SEQ' TO WS-KEY-NAME
           MOVE HC-END-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_ENDOWMENT_POLICYNUM' TO WS-KEY-NAME
           MOVE HC-END-POLICYNUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_ENDOWMENT_WITHPROFITS' TO WS-KEY-NAME
           MOVE HC-END-WITH-PROFITS TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_ENDOWMENT_EQUITIES' TO WS-KEY-NAME
           MOVE HC-END-EQUITIES TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_ENDOWMENT_MANAGEDFUND' TO WS-KEY-NAME
           MOVE HC-END-MANAGED-FUND TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_ENDOWMENT_FUNDNAME' TO WS-KEY-NAME
           MOVE HC-END-FUND-NAME TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_ENDOWMENT_TERM' TO WS-KEY-NAME
           MOVE HC-END-TERM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_ENDOWMENT_SUMASSURED' TO WS-KEY-NAME
           MOVE HC-END-SUMASSURED TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_ENDOWMENT_LIFEASSURED' TO WS-KEY-NAME
           MOVE HC-END-LIFE-ASSURED TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_ENDOWMENT_PADDINGLEN' TO WS-KEY-NAME
           MOVE HC-END-VARY-LEN TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_HOUSE_PRESENT' TO WS-KEY-NAME
           MOVE HC-HOU-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_HOUSE_COUNT' TO WS-KEY-NAME
           MOVE HC-HOU-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_HOUSE_SEQ' TO WS-KEY-NAME
           MOVE HC-HOU-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_HOUSE_POLICYNUM' TO WS-KEY-NAME
           MOVE HC-HOU-POLICYNUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_HOUSE_PROPERTYTYPE' TO WS-KEY-NAME
           MOVE HC-HOU-PROPERTY-TYPE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_HOUSE_BEDROOMS' TO WS-KEY-NAME
           MOVE HC-HOU-BEDROOMS TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_HOUSE_VALUE' TO WS-KEY-NAME
           MOVE HC-HOU-VALUE TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQL_HOUSE_HOUSENAME' TO WS-KEY-NAME
           MOVE HC-HOU-HOUSE-NAME TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_HOUSE_HOUSENUMBER' TO WS-KEY-NAME
           MOVE HC-HOU-HOUSE-NUMBER TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_HOUSE_POSTCODE' TO WS-KEY-NAME
           MOVE HC-HOU-POSTCODE TO WS-VALUE
           PERFORM EMIT-VALUE.
      *
      * How often the identity and timestamp read-backs executed, the
      * presence, ordinal and predicate host of each, and the result of
      * the most recent SQL operation.
       EMIT-SQL-BOOKKEEPING.
           MOVE 'SQL_IDENTITY_CALLS' TO WS-KEY-NAME
           MOVE HC-IDENT-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_LASTCHANGED_CALLS' TO WS-KEY-NAME
           MOVE HC-LCHG-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_IDENTITY_PRESENT' TO WS-KEY-NAME
           MOVE HC-IDENT-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_IDENTITY_SEQ' TO WS-KEY-NAME
           MOVE HC-IDENT-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_LASTCHANGED_PRESENT' TO WS-KEY-NAME
           MOVE HC-LCHG-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_LASTCHANGED_SEQ' TO WS-KEY-NAME
           MOVE HC-LCHG-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_LASTCHANGED_POLICYNUM' TO WS-KEY-NAME
           MOVE HC-LCHG-POLICYNUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'SQLCODE_LAST' TO WS-KEY-NAME
           MOVE SQLCODE TO WS-INT-VALUE
           PERFORM EMIT-INTEGER.
      *
      *================================================================*
      * Execution order captures                                       *
      *================================================================*
      * How many events the case stamped, how many it expected, and the
      * order guard the capturing stubs maintain.
       EMIT-ORDER-CAPTURES.
           MOVE 'EVENT_SEQ_TOTAL' TO WS-KEY-NAME
           MOVE HC-EVENT-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'EVENT_SEQ_EXPECTED' TO WS-KEY-NAME
           MOVE WS-WANT-EVENTS TO WS-WANT-EVENTS-EDIT
           MOVE WS-WANT-EVENTS-EDIT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'ORDER_VIOLATION' TO WS-KEY-NAME
           MOVE HC-ORDER-VIOLATION TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'ORDER_VIOLATION_STMT' TO WS-KEY-NAME
           MOVE HC-ORDER-VIOLATION-STMT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'ORDER_LAST_STMT' TO WS-KEY-NAME
           MOVE HC-ORDER-LAST-STMT TO WS-VALUE
           PERFORM EMIT-VALUE.
      *
      *================================================================*
      * VSAM write captures                                            *
      *================================================================*
      * The complete 64-character record image, the key half of that
      * image, the key operand the command passed separately, the file
      * name and the two lengths as the command passed them, and the
      * response it returned. Every value below is a capture: none is a
      * value this program supplied in place of an operand.
      *
      * The record image, the payload and the key operand are each
      * emitted twice: once as the characters they hold, which a reader
      * reads, and once as hexadecimal, which carries two characters
      * per byte and so keeps every trailing space of the value. The
      * record image built from the fixture is emitted in the same
      * hexadecimal form, so the two 64-byte images are comparable
      * character by character outside this program as well.
       EMIT-VSAM-CAPTURES.
           MOVE 'VSAM_PRESENT' TO WS-KEY-NAME
           MOVE HC-VSAM-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_COUNT' TO WS-KEY-NAME
           MOVE HC-VSAM-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_SEQ' TO WS-KEY-NAME
           MOVE HC-VSAM-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_FILE' TO WS-KEY-NAME
           MOVE HC-VSAM-FILE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_LENGTH' TO WS-KEY-NAME
           MOVE HC-VSAM-RECORD-LEN TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_KEYLENGTH' TO WS-KEY-NAME
           MOVE HC-VSAM-KEY-LEN TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_KEY' TO WS-KEY-NAME
           MOVE HC-VSAM-KEY TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_REQUEST_ID' TO WS-KEY-NAME
           MOVE HC-VSAM-REQUEST-ID TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_CUSTOMER_NUM' TO WS-KEY-NAME
           MOVE HC-VSAM-CUSTOMER-NUM TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_POLICY_NUM' TO WS-KEY-NAME
           MOVE HC-VSAM-POLICY-NUM TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_RESP' TO WS-KEY-NAME
           MOVE HC-VSAM-RESP TO WS-INT-VALUE
           PERFORM EMIT-INTEGER
           MOVE 'VSAM_RECORD' TO WS-KEY-NAME
           MOVE HC-VSAM-RECORD TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_RECORD_HEX' TO WS-KEY-NAME
           MOVE HC-VSAM-RECORD TO WS-HEX-SOURCE
           MOVE 64 TO WS-HEX-SOURCE-LEN
           PERFORM EMIT-HEX-VALUE
           MOVE 'VSAM_PAYLOAD' TO WS-KEY-NAME
           MOVE HC-VSAM-POLICY-DATA TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_PAYLOAD_HEX' TO WS-KEY-NAME
           MOVE SPACES TO WS-HEX-SOURCE
           MOVE HC-VSAM-POLICY-DATA TO WS-HEX-SOURCE(1:43)
           MOVE 43 TO WS-HEX-SOURCE-LEN
           PERFORM EMIT-HEX-VALUE
           MOVE 'VSAM_RID_KEY' TO WS-KEY-NAME
           MOVE HC-VSAM-RIDFLD TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_RID_KEY_HEX' TO WS-KEY-NAME
           MOVE SPACES TO WS-HEX-SOURCE
           MOVE HC-VSAM-RIDFLD TO WS-HEX-SOURCE(1:21)
           MOVE 21 TO WS-HEX-SOURCE-LEN
           PERFORM EMIT-HEX-VALUE
           MOVE 'VSAM_RID_REQUEST_ID' TO WS-KEY-NAME
           MOVE HC-RID-REQUEST-ID TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_RID_CUSTOMER_NUM' TO WS-KEY-NAME
           MOVE HC-RID-CUSTOMER-NUM TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_RID_POLICY_NUM' TO WS-KEY-NAME
           MOVE HC-RID-POLICY-NUM TO WS-VALUE
           PERFORM EMIT-VALUE
           PERFORM BUILD-EXPECTED-KEY
           MOVE 'VSAM_KEY_EXPECTED' TO WS-KEY-NAME
           MOVE WS-EXPECTED-KEY TO WS-VALUE
           PERFORM EMIT-VALUE
           PERFORM BUILD-EXPECTED-PAYLOAD
           MOVE 'VSAM_PAYLOAD_EXPECTED' TO WS-KEY-NAME
           IF WS-PAYLOAD-DERIVED = 'Y'
               MOVE WS-EXPECTED-PAYLOAD TO WS-VALUE
           ELSE
               MOVE SPACES TO WS-VALUE
           END-IF
           PERFORM EMIT-VALUE
           MOVE 'VSAM_PAYLOAD_DERIVED' TO WS-KEY-NAME
           MOVE WS-PAYLOAD-DERIVED TO WS-VALUE
           PERFORM EMIT-VALUE
           PERFORM BUILD-EXPECTED-RECORD
           MOVE 'VSAM_RECORD_EXPECTED_HEX' TO WS-KEY-NAME
           MOVE WS-EXPECTED-RECORD TO WS-HEX-SOURCE
           MOVE 64 TO WS-HEX-SOURCE-LEN
           PERFORM EMIT-HEX-VALUE.
      *
      *================================================================*
      * Failure surface                                                *
      *================================================================*
      * Whether an abend site was reached, its code, and how many
      * diagnostic links the error paragraphs issued.
       EMIT-FAILURE-SURFACE.
           MOVE 'ABEND_PRESENT' TO WS-KEY-NAME
           MOVE HC-ABEND-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'ABEND_CODE' TO WS-KEY-NAME
           MOVE HC-ABEND-CODE TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'DIAG_LINK_COUNT' TO WS-KEY-NAME
           MOVE HC-DIAG-LINK-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'ABEND_COUNT' TO WS-KEY-NAME
           MOVE HC-ABEND-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'ABEND_SEQ' TO WS-KEY-NAME
           MOVE HC-ABEND-SEQ TO WS-VALUE
           PERFORM EMIT-VALUE.
      *
      *================================================================*
      * Amount captures                                                *
      *================================================================*
      * The amount fields of the case, each as the fixture spells it and
      * as the insert passed it, the number compared and the widest
      * difference seen. The fields are
      * [base/src/lgcmarea.cpy:43,73,85,87,89,91].
       EMIT-AMOUNT-CAPTURES.
           MOVE 95 TO WS-DEC-OFFSET
           MOVE 6 TO WS-DEC-LENGTH
           MOVE 'AMOUNT_PAYMENT' TO WS-CMP-FIELD
           MOVE HC-POL-PAYMENT TO WS-CMP-ACTUAL-NUM
           PERFORM EMIT-ONE-AMOUNT
           EVALUATE WS-PRODUCT-WANTED
             WHEN 'M'
               MOVE 166 TO WS-DEC-OFFSET
               MOVE 6 TO WS-DEC-LENGTH
               MOVE 'AMOUNT_MOTOR_PREMIUM' TO WS-CMP-FIELD
               MOVE HC-MOT-PREMIUM TO WS-CMP-ACTUAL-NUM
               PERFORM EMIT-ONE-AMOUNT
             WHEN 'C'
               MOVE 900 TO WS-DEC-OFFSET
               MOVE 8 TO WS-DEC-LENGTH
               MOVE 'AMOUNT_FIRE_PREMIUM' TO WS-CMP-FIELD
               MOVE HC-COM-FIREPREMIUM TO WS-CMP-ACTUAL-NUM
               PERFORM EMIT-ONE-AMOUNT
               MOVE 912 TO WS-DEC-OFFSET
               MOVE 8 TO WS-DEC-LENGTH
               MOVE 'AMOUNT_CRIME_PREMIUM' TO WS-CMP-FIELD
               MOVE HC-COM-CRIMEPREMIUM TO WS-CMP-ACTUAL-NUM
               PERFORM EMIT-ONE-AMOUNT
               MOVE 924 TO WS-DEC-OFFSET
               MOVE 8 TO WS-DEC-LENGTH
               MOVE 'AMOUNT_FLOOD_PREMIUM' TO WS-CMP-FIELD
               MOVE HC-COM-FLOODPREMIUM TO WS-CMP-ACTUAL-NUM
               PERFORM EMIT-ONE-AMOUNT
               MOVE 936 TO WS-DEC-OFFSET
               MOVE 8 TO WS-DEC-LENGTH
               MOVE 'AMOUNT_WEATHER_PREMIUM' TO WS-CMP-FIELD
               MOVE HC-COM-WEATHERPREMIUM TO WS-CMP-ACTUAL-NUM
               PERFORM EMIT-ONE-AMOUNT
           END-EVALUATE
           MOVE 'AMOUNT_CHECKS' TO WS-KEY-NAME
           MOVE WS-AMOUNT-CHECKS TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'AMOUNT_MAX_DELTA' TO WS-KEY-NAME
           MOVE WS-AMOUNT-MAX-DELTA TO WS-INT-VALUE
           PERFORM EMIT-INTEGER.
      *
      * Writes the expected and the captured value of one amount. The
      * expected value is the digits the fixture holds; a fixture field
      * that does not spell a number is written as the characters found
      * there.
       EMIT-ONE-AMOUNT.
           PERFORM DECODE-FIXTURE-NUMBER
           MOVE SPACES TO WS-KEY-NAME
           STRING FUNCTION TRIM(WS-CMP-FIELD) DELIMITED BY SIZE
                  '_EXPECTED' DELIMITED BY SIZE
               INTO WS-KEY-NAME
           END-STRING
           IF WS-DEC-OK = 'Y'
               MOVE WS-DEC-NUM TO WS-INT-VALUE
               PERFORM EMIT-INTEGER
           ELSE
               MOVE WS-DEC-TEXT TO WS-VALUE
               PERFORM EMIT-VALUE
           END-IF
           MOVE SPACES TO WS-KEY-NAME
           STRING FUNCTION TRIM(WS-CMP-FIELD) DELIMITED BY SIZE
                  '_CAPTURED' DELIMITED BY SIZE
               INTO WS-KEY-NAME
           END-STRING
           MOVE WS-CMP-ACTUAL-NUM TO WS-INT-VALUE
           PERFORM EMIT-INTEGER.
      *
      *================================================================*
      * Verdict counters                                               *
      *================================================================*
      * How many named checks failed, how many of them were capture
      * checks and how many were value checks, and the status this run
      * returns.
       EMIT-VERDICT-COUNTS.
           MOVE 'CHECKS_FAILED' TO WS-KEY-NAME
           MOVE WS-FAILURES TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'CAPTURE_CHECKS_FAILED' TO WS-KEY-NAME
           MOVE WS-CAPTURE-FAILURES TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VALUE_CHECKS_FAILED' TO WS-KEY-NAME
           MOVE WS-VALUE-FAILURES TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'DRIVER_EXIT_STATUS' TO WS-KEY-NAME
           MOVE WS-EXIT-CODE TO WS-VALUE
           PERFORM EMIT-VALUE.
      *
      * The verdict of the run, written as the last line of the
      * capture file.
       EMIT-DRIVER-STATUS.
           MOVE 'DRIVER_STATUS' TO WS-KEY-NAME
           IF WS-EXIT-CODE = ZERO
               MOVE 'PASS' TO WS-VALUE
           ELSE
               MOVE 'FAIL' TO WS-VALUE
           END-IF
           PERFORM EMIT-VALUE.

      *
      *================================================================*
      * Verdict                                                        *
      *================================================================*
      * Every check below must hold for the run to pass. Each check
      * that fails is named in the log, counted in WS-FAILURES and
      * counted again against the status it selects.
       EVALUATE-VERDICT.
           PERFORM CHECK-CHAIN-CALLED
           PERFORM CHECK-RETURN-CODE
           PERFORM CHECK-ABEND-STATE
           PERFORM CHECK-STATEMENT-CAPTURES
           PERFORM CHECK-EXECUTION-ORDER
           PERFORM CHECK-SQL-BOOKKEEPING
           PERFORM CHECK-CHAIN-WITNESS
           PERFORM CHECK-DIAG-LINKS
           PERFORM CHECK-VSAM-CAPTURE
           PERFORM CHECK-POLICY-VALUES
           PERFORM CHECK-PRODUCT-VALUES
           PERFORM SELECT-EXIT-CODE.
      *
      * The chain was entered.
       CHECK-CHAIN-CALLED.
           IF WS-CALL-FAILED = 'Y'
               MOVE 'CHAIN-MODULE-CALLED' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
           END-IF.
      *
      * The chain returned the code the case expects. 'NONE' compares
      * no code, the setting a case uses when the chain abends before
      * [base/src/lgapol01.cbl:105] and leaves the fixture value in
      * place.
       CHECK-RETURN-CODE.
           MOVE CA-RETURN-CODE TO WS-RETURN-CODE-TEXT
           IF WS-WANT-RETURN-CODE NOT = 'NONE'
               IF WS-RETURN-CODE-TEXT NOT = WS-WANT-RETURN-CODE(1:2)
                   MOVE 'RETURN-CODE-AS-EXPECTED' TO WS-CHECK-NAME
                   PERFORM REPORT-RC-FAILURE
                   DISPLAY 'DRIVER:   field CA-RETURN-CODE expected ['
                           WS-WANT-RETURN-CODE(1:2) '] captured ['
                           WS-RETURN-CODE-TEXT ']'
                   END-DISPLAY
               END-IF
           END-IF.
      *
      * The abend state is the one the case expects: no site reached,
      * or exactly one site reached with the expected code and an
      * ordinal above zero.
       CHECK-ABEND-STATE.
           IF WS-WANT-ABEND = 'NONE'
               IF HC-ABEND-PRESENT NOT = 'N'
                       OR HC-ABEND-COUNT NOT = ZERO
                   MOVE 'NO-ABEND-CAPTURED' TO WS-CHECK-NAME
                   PERFORM REPORT-ABEND-FAILURE
                   DISPLAY 'DRIVER:   field ABEND_CODE expected [] '
                           'captured [' HC-ABEND-CODE '] '
                           HC-ABEND-COUNT ' time(s)'
                   END-DISPLAY
               END-IF
           ELSE
               IF HC-ABEND-PRESENT NOT = 'Y'
                   MOVE 'ABEND-CAPTURED' TO WS-CHECK-NAME
                   PERFORM REPORT-ABEND-FAILURE
                   DISPLAY 'DRIVER:   field ABEND_CODE expected ['
                           WS-WANT-ABEND '] captured no abend'
                   END-DISPLAY
               ELSE
                   IF HC-ABEND-CODE NOT = WS-WANT-ABEND
                       MOVE 'ABEND-CODE-AS-EXPECTED' TO WS-CHECK-NAME
                       PERFORM REPORT-ABEND-FAILURE
                       DISPLAY 'DRIVER:   field ABEND_CODE expected ['
                               WS-WANT-ABEND '] captured ['
                               HC-ABEND-CODE ']'
                       END-DISPLAY
                   END-IF
                   IF HC-ABEND-COUNT NOT = 1
                       MOVE 'ABEND-COUNT-IS-ONE' TO WS-CHECK-NAME
                       PERFORM REPORT-ABEND-FAILURE
                       DISPLAY 'DRIVER:   field ABEND_COUNT expected '
                               '0001 captured ' HC-ABEND-COUNT
                       END-DISPLAY
                   END-IF
                   IF HC-ABEND-SEQ = ZERO
                       MOVE 'ABEND-ORDINAL-STAMPED' TO WS-CHECK-NAME
                       PERFORM REPORT-ABEND-FAILURE
                       DISPLAY 'DRIVER:   field ABEND_SEQ expected an '
                               'ordinal above zero captured '
                               HC-ABEND-SEQ
                       END-DISPLAY
                   END-IF
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Statement cardinality                                          *
      *----------------------------------------------------------------*
      * Every statement the case requires was captured exactly once and
      * carries an ordinal; every statement it forbids was not captured
      * at all. The eight statements are the seven SQL blocks of
      * [base/src/lgapdb01.cbl:268-321,346-386,409-425,449-471,499-545]
      * and the write of [base/src/lgapvs01.cbl:135-141].
       CHECK-STATEMENT-CAPTURES.
           MOVE 'insert_policy' TO WS-STMT-LABEL
           MOVE HC-POL-PRESENT TO WS-STMT-PRESENT
           MOVE HC-POL-COUNT TO WS-STMT-COUNT
           MOVE HC-POL-SEQ TO WS-STMT-SEQ
           MOVE WS-WANT-POLICY-SQL TO WS-STMT-EXPECTED
           PERFORM CHECK-STATEMENT-CAPTURE
           MOVE 'set_identity' TO WS-STMT-LABEL
           MOVE HC-IDENT-PRESENT TO WS-STMT-PRESENT
           MOVE HC-IDENT-COUNT TO WS-STMT-COUNT
           MOVE HC-IDENT-SEQ TO WS-STMT-SEQ
           MOVE WS-WANT-IDENTITY TO WS-STMT-EXPECTED
           PERFORM CHECK-STATEMENT-CAPTURE
           MOVE 'select_lastchanged' TO WS-STMT-LABEL
           MOVE HC-LCHG-PRESENT TO WS-STMT-PRESENT
           MOVE HC-LCHG-COUNT TO WS-STMT-COUNT
           MOVE HC-LCHG-SEQ TO WS-STMT-SEQ
           MOVE WS-WANT-IDENTITY TO WS-STMT-EXPECTED
           PERFORM CHECK-STATEMENT-CAPTURE
           MOVE 'insert_motor' TO WS-STMT-LABEL
           MOVE HC-MOT-PRESENT TO WS-STMT-PRESENT
           MOVE HC-MOT-COUNT TO WS-STMT-COUNT
           MOVE HC-MOT-SEQ TO WS-STMT-SEQ
           MOVE 'N' TO WS-STMT-EXPECTED
           IF WS-PRODUCT-WANTED = 'M'
               MOVE 'Y' TO WS-STMT-EXPECTED
           END-IF
           PERFORM CHECK-STATEMENT-CAPTURE
           MOVE 'insert_commercial' TO WS-STMT-LABEL
           MOVE HC-COM-PRESENT TO WS-STMT-PRESENT
           MOVE HC-COM-COUNT TO WS-STMT-COUNT
           MOVE HC-COM-SEQ TO WS-STMT-SEQ
           MOVE 'N' TO WS-STMT-EXPECTED
           IF WS-PRODUCT-WANTED = 'C'
               MOVE 'Y' TO WS-STMT-EXPECTED
           END-IF
           PERFORM CHECK-STATEMENT-CAPTURE
           MOVE 'insert_endowment' TO WS-STMT-LABEL
           MOVE HC-END-PRESENT TO WS-STMT-PRESENT
           MOVE HC-END-COUNT TO WS-STMT-COUNT
           MOVE HC-END-SEQ TO WS-STMT-SEQ
           MOVE 'N' TO WS-STMT-EXPECTED
           IF WS-PRODUCT-WANTED = 'E'
               MOVE 'Y' TO WS-STMT-EXPECTED
           END-IF
           PERFORM CHECK-STATEMENT-CAPTURE
           MOVE 'insert_house' TO WS-STMT-LABEL
           MOVE HC-HOU-PRESENT TO WS-STMT-PRESENT
           MOVE HC-HOU-COUNT TO WS-STMT-COUNT
           MOVE HC-HOU-SEQ TO WS-STMT-SEQ
           MOVE 'N' TO WS-STMT-EXPECTED
           IF WS-PRODUCT-WANTED = 'H'
               MOVE 'Y' TO WS-STMT-EXPECTED
           END-IF
           PERFORM CHECK-STATEMENT-CAPTURE
           MOVE 'cics_write' TO WS-STMT-LABEL
           MOVE HC-VSAM-PRESENT TO WS-STMT-PRESENT
           MOVE HC-VSAM-COUNT TO WS-STMT-COUNT
           MOVE HC-VSAM-SEQ TO WS-STMT-SEQ
           MOVE WS-WANT-VSAM TO WS-STMT-EXPECTED
           PERFORM CHECK-STATEMENT-CAPTURE.
      *
      * Compares one statement's presence flag, counter and ordinal
      * with what the case requires of it. A counter above one reports
      * a repeated execution and fails the case.
       CHECK-STATEMENT-CAPTURE.
           MOVE SPACES TO WS-CHECK-NAME
           STRING FUNCTION TRIM(WS-STMT-LABEL) DELIMITED BY SIZE
                  '-CAPTURE' DELIMITED BY SIZE
               INTO WS-CHECK-NAME
           END-STRING
           IF WS-STMT-EXPECTED = 'Y'
               IF WS-STMT-PRESENT NOT = 'Y'
                       OR WS-STMT-COUNT NOT = 1
                       OR WS-STMT-SEQ = ZERO
                   PERFORM REPORT-CAPTURE-FAILURE
                   DISPLAY 'DRIVER:   statement '
                           FUNCTION TRIM(WS-STMT-LABEL)
                           ' expected present Y count 0001 and an '
                           'ordinal above zero'
                   END-DISPLAY
                   PERFORM DISPLAY-STATEMENT-CAPTURED
               END-IF
           ELSE
               IF WS-STMT-PRESENT NOT = 'N'
                       OR WS-STMT-COUNT NOT = ZERO
                       OR WS-STMT-SEQ NOT = ZERO
                   PERFORM REPORT-CAPTURE-FAILURE
                   DISPLAY 'DRIVER:   statement '
                           FUNCTION TRIM(WS-STMT-LABEL)
                           ' expected present N count 0000 ordinal 0000'
                   END-DISPLAY
                   PERFORM DISPLAY-STATEMENT-CAPTURED
               END-IF
           END-IF.
      *
       DISPLAY-STATEMENT-CAPTURED.
           DISPLAY 'DRIVER:   captured present ' WS-STMT-PRESENT
                   ' count ' WS-STMT-COUNT
                   ' ordinal ' WS-STMT-SEQ
           END-DISPLAY.
      *
      *----------------------------------------------------------------*
      * Execution order                                                *
      *----------------------------------------------------------------*
      * The captures of the case were stamped in the order
      * [base/src/lgapdb01.cbl:219-246] executes them, no capturing
      * stub reported a prerequisite that had not run, and the case
      * stamped exactly as many events as it requires.
       CHECK-EXECUTION-ORDER.
           IF HC-ORDER-VIOLATION NOT = 'N'
               MOVE 'ORDER-GUARD-INTACT' TO WS-CHECK-NAME
               PERFORM REPORT-CAPTURE-FAILURE
               DISPLAY 'DRIVER:   statement '
                       HC-ORDER-VIOLATION-STMT
                       ' ran with a prerequisite ordinal at zero'
               END-DISPLAY
           END-IF
           IF HC-EVENT-SEQ NOT = WS-WANT-EVENTS
               MOVE 'EVENT-COUNT-AS-EXPECTED' TO WS-CHECK-NAME
               PERFORM REPORT-CAPTURE-FAILURE
               MOVE WS-WANT-EVENTS TO WS-WANT-EVENTS-EDIT
               DISPLAY 'DRIVER:   field EVENT_SEQ_TOTAL expected '
                       WS-WANT-EVENTS-EDIT ' captured ' HC-EVENT-SEQ
               END-DISPLAY
           END-IF
           PERFORM BUILD-ORDER-TABLE
           MOVE ZERO TO WS-ORDER-PREV
           PERFORM VARYING WS-ORDER-IX FROM 1 BY 1
                   UNTIL WS-ORDER-IX > WS-ORDER-COUNT
               IF WS-ORDER-SEQ(WS-ORDER-IX) NOT > WS-ORDER-PREV
                   MOVE 'CAPTURE-ORDER-AS-EXECUTED' TO WS-CHECK-NAME
                   PERFORM REPORT-CAPTURE-FAILURE
                   DISPLAY 'DRIVER:   statement '
                           FUNCTION TRIM(WS-ORDER-NAME(WS-ORDER-IX))
                           ' ordinal ' WS-ORDER-SEQ(WS-ORDER-IX)
                           ' does not follow ordinal ' WS-ORDER-PREV
                   END-DISPLAY
               END-IF
               MOVE WS-ORDER-SEQ(WS-ORDER-IX) TO WS-ORDER-PREV
           END-PERFORM.
      *
      * Lists the ordinals the case requires, in the order the source
      * executes them: the POLICY insert at
      * [base/src/lgapdb01.cbl:219], its two read-backs at
      * [base/src/lgapdb01.cbl:308-321], the product insert at
      * [base/src/lgapdb01.cbl:223-241] and the write the link at
      * [base/src/lgapdb01.cbl:243-246] leads to.
       BUILD-ORDER-TABLE.
           MOVE ZERO TO WS-ORDER-COUNT
           INITIALIZE WS-ORDER-TABLE
           IF WS-WANT-POLICY-SQL = 'Y'
               ADD 1 TO WS-ORDER-COUNT
               END-ADD
               MOVE 'insert_policy' TO WS-ORDER-NAME(WS-ORDER-COUNT)
               MOVE HC-POL-SEQ TO WS-ORDER-SEQ(WS-ORDER-COUNT)
           END-IF
           IF WS-WANT-IDENTITY = 'Y'
               ADD 1 TO WS-ORDER-COUNT
               END-ADD
               MOVE 'set_identity' TO WS-ORDER-NAME(WS-ORDER-COUNT)
               MOVE HC-IDENT-SEQ TO WS-ORDER-SEQ(WS-ORDER-COUNT)
               ADD 1 TO WS-ORDER-COUNT
               END-ADD
               MOVE 'select_lastchanged'
                   TO WS-ORDER-NAME(WS-ORDER-COUNT)
               MOVE HC-LCHG-SEQ TO WS-ORDER-SEQ(WS-ORDER-COUNT)
           END-IF
           EVALUATE WS-PRODUCT-WANTED
             WHEN 'M'
               ADD 1 TO WS-ORDER-COUNT
               END-ADD
               MOVE 'insert_motor' TO WS-ORDER-NAME(WS-ORDER-COUNT)
               MOVE HC-MOT-SEQ TO WS-ORDER-SEQ(WS-ORDER-COUNT)
             WHEN 'C'
               ADD 1 TO WS-ORDER-COUNT
               END-ADD
               MOVE 'insert_commercial'
                   TO WS-ORDER-NAME(WS-ORDER-COUNT)
               MOVE HC-COM-SEQ TO WS-ORDER-SEQ(WS-ORDER-COUNT)
             WHEN 'E'
               ADD 1 TO WS-ORDER-COUNT
               END-ADD
               MOVE 'insert_endowment'
                   TO WS-ORDER-NAME(WS-ORDER-COUNT)
               MOVE HC-END-SEQ TO WS-ORDER-SEQ(WS-ORDER-COUNT)
             WHEN 'H'
               ADD 1 TO WS-ORDER-COUNT
               END-ADD
               MOVE 'insert_house' TO WS-ORDER-NAME(WS-ORDER-COUNT)
               MOVE HC-HOU-SEQ TO WS-ORDER-SEQ(WS-ORDER-COUNT)
             WHEN OTHER
               CONTINUE
           END-EVALUATE
           IF WS-WANT-VSAM = 'Y'
               ADD 1 TO WS-ORDER-COUNT
               END-ADD
               MOVE 'cics_write' TO WS-ORDER-NAME(WS-ORDER-COUNT)
               MOVE HC-VSAM-SEQ TO WS-ORDER-SEQ(WS-ORDER-COUNT)
           END-IF.
      *
      *----------------------------------------------------------------*
      * SQL bookkeeping                                                *
      *----------------------------------------------------------------*
      * The most recent SQL operation reported the result the case
      * injected, and the read-back at
      * [base/src/lgapdb01.cbl:316-321] selected on the identity the
      * block at [base/src/lgapdb01.cbl:308-310] returned.
       CHECK-SQL-BOOKKEEPING.
           IF SQLCODE NOT = WS-WANT-SQLCODE
               MOVE 'SQLCODE-AS-INJECTED' TO WS-CHECK-NAME
               PERFORM REPORT-CAPTURE-FAILURE
               MOVE WS-WANT-SQLCODE TO WS-CMP-EXPECT-EDIT
               MOVE SQLCODE TO WS-CMP-ACTUAL-EDIT
               DISPLAY 'DRIVER:   field SQLCODE_LAST expected '
                       WS-CMP-EXPECT-EDIT ' captured '
                       WS-CMP-ACTUAL-EDIT
               END-DISPLAY
           END-IF
           IF WS-WANT-IDENTITY = 'Y' AND HC-LCHG-PRESENT = 'Y'
               IF HC-LCHG-POLICYNUM NOT = HC-IDENT-POLICYNUM
                   MOVE 'LASTCHANGED-PREDICATE-IS-IDENTITY'
                       TO WS-CHECK-NAME
                   PERFORM REPORT-CAPTURE-FAILURE
                   MOVE HC-IDENT-POLICYNUM TO WS-CMP-EXPECT-EDIT
                   MOVE HC-LCHG-POLICYNUM TO WS-CMP-ACTUAL-EDIT
                   DISPLAY 'DRIVER:   field '
                           'SQL_LASTCHANGED_POLICYNUM expected '
                           WS-CMP-EXPECT-EDIT ' captured '
                           WS-CMP-ACTUAL-EDIT
                   END-DISPLAY
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Chain traversal                                                *
      *----------------------------------------------------------------*
      * Each program the chain reaches beyond the first was entered
      * where the case requires it and observed the COMMAREA length its
      * caller states. The POLICY insert witnesses LGAPDB01 and the
      * write witnesses LGAPVS01.
       CHECK-CHAIN-WITNESS.
           MOVE 'LGAPDB01' TO WS-STMT-LABEL
           MOVE HC-CHAIN-DB2-PRESENT TO WS-STMT-PRESENT
           MOVE HC-CHAIN-DB2-CALEN TO WS-CHAIN-CALEN
           MOVE WS-WANT-POLICY-SQL TO WS-STMT-EXPECTED
           PERFORM CHECK-ONE-CHAIN-WITNESS
           MOVE 'LGAPVS01' TO WS-STMT-LABEL
           MOVE HC-CHAIN-VSAM-PRESENT TO WS-STMT-PRESENT
           MOVE HC-CHAIN-VSAM-CALEN TO WS-CHAIN-CALEN
           MOVE WS-WANT-VSAM TO WS-STMT-EXPECTED
           PERFORM CHECK-ONE-CHAIN-WITNESS.
      *
       CHECK-ONE-CHAIN-WITNESS.
           MOVE SPACES TO WS-CHECK-NAME
           STRING FUNCTION TRIM(WS-STMT-LABEL) DELIMITED BY SIZE
                  '-LINK-WITNESS' DELIMITED BY SIZE
               INTO WS-CHECK-NAME
           END-STRING
           IF WS-STMT-EXPECTED = 'Y'
               IF WS-STMT-PRESENT NOT = 'Y'
                   PERFORM REPORT-CAPTURE-FAILURE
                   DISPLAY 'DRIVER:   program '
                           FUNCTION TRIM(WS-STMT-LABEL)
                           ' was not entered'
                   END-DISPLAY
               ELSE
                   IF WS-CHAIN-CALEN NOT = WS-LINK-LEN-EXPECTED
                       PERFORM REPORT-CAPTURE-FAILURE
                       DISPLAY 'DRIVER:   program '
                               FUNCTION TRIM(WS-STMT-LABEL)
                               ' observed COMMAREA length '
                               WS-CHAIN-CALEN ' expected '
                               WS-LINK-LEN-EXPECTED
                       END-DISPLAY
                   END-IF
               END-IF
           ELSE
               IF WS-STMT-PRESENT NOT = 'N'
                       OR WS-CHAIN-CALEN NOT = ZERO
                   PERFORM REPORT-CAPTURE-FAILURE
                   DISPLAY 'DRIVER:   program '
                           FUNCTION TRIM(WS-STMT-LABEL)
                           ' was entered with COMMAREA length '
                           WS-CHAIN-CALEN
                           ' and the case reaches no service there'
                   END-DISPLAY
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Diagnostic links                                               *
      *----------------------------------------------------------------*
      * The error paragraphs of the three programs issued a diagnostic
      * link where the case reaches one, and none where it does not.
       CHECK-DIAG-LINKS.
           IF WS-WANT-DIAG-LINKS = 'NONE'
               IF HC-DIAG-LINK-COUNT NOT = ZERO
                   MOVE 'NO-DIAGNOSTIC-LINK' TO WS-CHECK-NAME
                   PERFORM REPORT-CAPTURE-FAILURE
                   DISPLAY 'DRIVER:   field DIAG_LINK_COUNT expected '
                           '0000 captured ' HC-DIAG-LINK-COUNT
                   END-DISPLAY
               END-IF
           ELSE
               IF HC-DIAG-LINK-COUNT = ZERO
                   MOVE 'DIAGNOSTIC-LINK-ISSUED' TO WS-CHECK-NAME
                   PERFORM REPORT-CAPTURE-FAILURE
                   DISPLAY 'DRIVER:   field DIAG_LINK_COUNT expected '
                           'a count above zero captured '
                           HC-DIAG-LINK-COUNT
                   END-DISPLAY
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * VSAM write                                                     *
      *----------------------------------------------------------------*
      * The operands the write passed, the two readings of its key and
      * the payload it projected. The presence, counter and ordinal are
      * checked by CHECK-STATEMENT-CAPTURES above.
       CHECK-VSAM-CAPTURE.
           IF WS-WANT-VSAM = 'Y' AND HC-VSAM-PRESENT = 'Y'
               PERFORM CHECK-VSAM-OPERANDS
               PERFORM CHECK-VSAM-KEY
               PERFORM CHECK-VSAM-PAYLOAD
           END-IF.
      *
      * The file name, the record length, the key length and the
      * response the command carried, each compared with what
      * [base/src/lgapvs01.cbl:135-140] states and with the response
      * the case injected. Every value compared here was received by
      * the emulated command as an operand.
       CHECK-VSAM-OPERANDS.
           IF HC-VSAM-FILE NOT = WS-VSAM-FILE-EXPECTED
               MOVE 'VSAM-FILE-IS-KSDSPOLY' TO WS-CHECK-NAME
               PERFORM REPORT-CAPTURE-FAILURE
               DISPLAY 'DRIVER:   field VSAM_FILE expected ['
                       WS-VSAM-FILE-EXPECTED '] captured ['
                       HC-VSAM-FILE ']'
               END-DISPLAY
           END-IF
           IF HC-VSAM-RECORD-LEN NOT = WS-VSAM-LEN-EXPECTED
               MOVE 'VSAM-RECORD-LENGTH-64' TO WS-CHECK-NAME
               PERFORM REPORT-CAPTURE-FAILURE
               DISPLAY 'DRIVER:   field VSAM_LENGTH expected '
                       WS-VSAM-LEN-EXPECTED ' captured '
                       HC-VSAM-RECORD-LEN
               END-DISPLAY
           END-IF
           IF HC-VSAM-KEY-LEN NOT = WS-VSAM-KEYLEN-EXPECTED
               MOVE 'VSAM-KEY-LENGTH-21' TO WS-CHECK-NAME
               PERFORM REPORT-CAPTURE-FAILURE
               DISPLAY 'DRIVER:   field VSAM_KEYLENGTH expected '
                       WS-VSAM-KEYLEN-EXPECTED ' captured '
                       HC-VSAM-KEY-LEN
               END-DISPLAY
           END-IF
           IF HC-VSAM-RESP NOT = WS-WANT-VSAM-RESP
               MOVE 'VSAM-RESPONSE-AS-INJECTED' TO WS-CHECK-NAME
               PERFORM REPORT-CAPTURE-FAILURE
               MOVE WS-WANT-VSAM-RESP TO WS-CMP-EXPECT-EDIT
               MOVE HC-VSAM-RESP TO WS-CMP-ACTUAL-EDIT
               DISPLAY 'DRIVER:   field VSAM_RESP expected '
                       WS-CMP-EXPECT-EDIT ' captured '
                       WS-CMP-ACTUAL-EDIT
               END-DISPLAY
           END-IF.
      *
      * The key of the case, read three ways: the first 21 characters
      * of the record image passed as From, the 21 characters passed as
      * Ridfld, and the key this program builds from the fixture. The
      * first two are compared with each other, then each component of
      * the record key and the whole key operand are compared with the
      * built key. The order is the declaration order at
      * [base/src/lgapvs01.cbl:26-29]: request type, customer number,
      * policy number.
       CHECK-VSAM-KEY.
           IF HC-VSAM-KEY NOT = HC-VSAM-RIDFLD
               MOVE 'VSAM-KEY-MATCHES-RIDFLD' TO WS-CHECK-NAME
               PERFORM REPORT-CAPTURE-FAILURE
               MOVE SPACES TO WS-LOG-TEXT
               MOVE HC-VSAM-KEY TO WS-LOG-TEXT(1:21)
               MOVE HC-VSAM-RIDFLD TO WS-LOG-TEXT(31:21)
               PERFORM SANITIZE-LOG-TEXT
               DISPLAY 'DRIVER:   field VSAM_KEY ['
                       WS-LOG-TEXT(1:21)
                       '] VSAM_RID_KEY [' WS-LOG-TEXT(31:21) ']'
               END-DISPLAY
           END-IF
           PERFORM BUILD-EXPECTED-KEY
           MOVE 'VSAM_REQUEST_ID' TO WS-CMP-FIELD
           MOVE 1 TO WS-CMP-LEN
           MOVE WS-EXP-REQUEST-ID TO WS-CMP-EXPECT-TEXT
           MOVE HC-VSAM-REQUEST-ID TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE
           MOVE 'VSAM_CUSTOMER_NUM' TO WS-CMP-FIELD
           MOVE 10 TO WS-CMP-LEN
           MOVE WS-EXP-CUSTOMER-NUM TO WS-CMP-EXPECT-TEXT
           MOVE HC-VSAM-CUSTOMER-NUM TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE
           MOVE 'VSAM_POLICY_NUM' TO WS-CMP-FIELD
           MOVE 10 TO WS-CMP-LEN
           MOVE WS-EXP-POLICY-NUM TO WS-CMP-EXPECT-TEXT
           MOVE HC-VSAM-POLICY-NUM TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE
           MOVE 'VSAM_RID_KEY' TO WS-CMP-FIELD
           MOVE 21 TO WS-CMP-LEN
           MOVE WS-EXPECTED-KEY TO WS-CMP-EXPECT-TEXT
           MOVE HC-VSAM-RIDFLD TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE.
      *
      * The 43-character payload of the record image and then the whole
      * 64-character image, each compared with the projection
      * [base/src/lgapvs01.cbl:103-131] produces for the expected
      * product from the fixture. Both comparisons run over every
      * character of the compared width, so a difference in a trailing
      * space is reported. A payload the fixture cannot describe is
      * reported rather than skipped.
       CHECK-VSAM-PAYLOAD.
           IF WS-WANT-PRODUCT-VALUES = 'Y'
               PERFORM BUILD-EXPECTED-PAYLOAD
               IF WS-PAYLOAD-DERIVED = 'Y'
                   MOVE 'VSAM_PAYLOAD' TO WS-CMP-FIELD
                   MOVE 43 TO WS-CMP-LEN
                   MOVE WS-EXPECTED-PAYLOAD TO WS-CMP-EXPECT-TEXT
                   MOVE HC-VSAM-POLICY-DATA TO WS-CMP-ACTUAL-TEXT
                   PERFORM COMPARE-TEXT-VALUE
                   PERFORM CHECK-VSAM-RECORD-IMAGE
               ELSE
                   MOVE 'VALUE-VSAM_PAYLOAD' TO WS-CHECK-NAME
                   PERFORM REPORT-VALUE-FAILURE
                   DISPLAY 'DRIVER:   field VSAM_PAYLOAD cannot be '
                           'derived from the fixture for request type '
                           WS-PRODUCT-WANTED
                   END-DISPLAY
               END-IF
           END-IF.
      *
      * The 64 characters passed as From(WF-Policy-Info)
      * [base/src/lgapvs01.cbl:136], compared with the image built from
      * the fixture: the 21-character key, then the 43-character
      * projection. All 64 are compared, so a difference in the padding
      * a shorter projected value leaves is reported with the position
      * it stands at.
       CHECK-VSAM-RECORD-IMAGE.
           PERFORM BUILD-EXPECTED-RECORD
           MOVE 'VSAM_RECORD' TO WS-CMP-FIELD
           MOVE 64 TO WS-CMP-LEN
           MOVE WS-EXPECTED-RECORD TO WS-CMP-EXPECT-TEXT
           MOVE HC-VSAM-RECORD TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE.
      *
      *----------------------------------------------------------------*
      * Expected key and payload                                       *
      *----------------------------------------------------------------*
      * Builds the 21-character key of the case: the request-type
      * letter of the effective request id, the customer number the
      * fixture holds, and the identity this program seeded, formatted
      * as the ten digits CA-POLICY-NUM carries. The moves are at
      * [base/src/lgapvs01.cbl:99-101].
       BUILD-EXPECTED-KEY.
           MOVE WS-EFFECTIVE-REQUEST-ID(4:1) TO WS-EXP-REQUEST-ID
           MOVE WS-FIXTURE-CHARS(9:10) TO WS-EXP-CUSTOMER-NUM
           MOVE WS-WANT-POLICYNUM TO WS-POLICYNUM-EDIT
           MOVE WS-POLICYNUM-EDIT TO WS-EXP-POLICY-NUM.
      *
      * Builds the 64-character record image of the case from those two
      * halves, in the order the group WF-Policy-Info
      * [base/src/lgapvs01.cbl:25-30] declares them: the key at
      * characters 1 to 21, the payload at 22 to 64. The payload half
      * carries the characters BUILD-EXPECTED-PAYLOAD left, which are
      * spaces while WS-PAYLOAD-DERIVED reports 'N'.
       BUILD-EXPECTED-RECORD.
           PERFORM BUILD-EXPECTED-KEY
           PERFORM BUILD-EXPECTED-PAYLOAD
           MOVE SPACES TO WS-EXPECTED-RECORD
           MOVE WS-EXPECTED-KEY TO WS-EXPECTED-RECORD(1:21)
           MOVE WS-EXPECTED-PAYLOAD TO WS-EXPECTED-RECORD(22:43).
      *
      * Builds the 43-character payload of the case from the fixture,
      * following the overlay the request type selects at
      * [base/src/lgapvs01.cbl:103-131] and the item order of
      * [base/src/lgapvs01.cbl:32-51]. A numeric field the fixture does
      * not spell as digits leaves WS-PAYLOAD-DERIVED at 'N'.
       BUILD-EXPECTED-PAYLOAD.
           MOVE SPACES TO WS-EXPECTED-PAYLOAD
           MOVE 'N' TO WS-PAYLOAD-DERIVED
           EVALUATE WS-PRODUCT-WANTED
             WHEN 'M'
               PERFORM BUILD-MOTOR-PAYLOAD
             WHEN 'C'
               PERFORM BUILD-COMMERCIAL-PAYLOAD
             WHEN 'E'
               PERFORM BUILD-ENDOWMENT-PAYLOAD
             WHEN 'H'
               PERFORM BUILD-HOUSE-PAYLOAD
             WHEN OTHER
               MOVE 'Y' TO WS-PAYLOAD-DERIVED
           END-EVALUATE.
      *
      * Make, model, value and registration number, the four items of
      * [base/src/lgapvs01.cbl:48-51].
       BUILD-MOTOR-PAYLOAD.
           MOVE WS-FIXTURE-CHARS(101:15) TO WS-EXPECTED-PAYLOAD(1:15)
           MOVE WS-FIXTURE-CHARS(116:15) TO WS-EXPECTED-PAYLOAD(16:15)
           MOVE WS-FIXTURE-CHARS(137:7) TO WS-EXPECTED-PAYLOAD(37:7)
           MOVE 131 TO WS-DEC-OFFSET
           MOVE 6 TO WS-DEC-LENGTH
           PERFORM DECODE-FIXTURE-NUMBER
           IF WS-DEC-OK = 'Y'
               MOVE WS-FIXTURE-CHARS(131:6) TO WS-EXPECTED-PAYLOAD(31:6)
               MOVE 'Y' TO WS-PAYLOAD-DERIVED
           END-IF.
      *
      * Postcode, status and the first 31 characters of the customer
      * name, the three items of [base/src/lgapvs01.cbl:32-34].
       BUILD-COMMERCIAL-PAYLOAD.
           MOVE WS-FIXTURE-CHARS(356:8) TO WS-EXPECTED-PAYLOAD(1:8)
           MOVE WS-FIXTURE-CHARS(386:31) TO WS-EXPECTED-PAYLOAD(13:31)
           MOVE 944 TO WS-DEC-OFFSET
           MOVE 4 TO WS-DEC-LENGTH
           PERFORM DECODE-FIXTURE-NUMBER
           IF WS-DEC-OK = 'Y'
               MOVE WS-FIXTURE-CHARS(944:4) TO WS-EXPECTED-PAYLOAD(9:4)
               MOVE 'Y' TO WS-PAYLOAD-DERIVED
           END-IF.
      *
      * With-profits, equities, managed fund, fund name and the first
      * 30 characters of the life assured, the five items of
      * [base/src/lgapvs01.cbl:36-40].
       BUILD-ENDOWMENT-PAYLOAD.
           MOVE WS-FIXTURE-CHARS(101:1) TO WS-EXPECTED-PAYLOAD(1:1)
           MOVE WS-FIXTURE-CHARS(102:1) TO WS-EXPECTED-PAYLOAD(2:1)
           MOVE WS-FIXTURE-CHARS(103:1) TO WS-EXPECTED-PAYLOAD(3:1)
           MOVE WS-FIXTURE-CHARS(104:10) TO WS-EXPECTED-PAYLOAD(4:10)
           MOVE WS-FIXTURE-CHARS(122:30) TO WS-EXPECTED-PAYLOAD(14:30)
           MOVE 'Y' TO WS-PAYLOAD-DERIVED.
      *
      * Property type, bedrooms, value, postcode and the first nine
      * characters of the house name, the five items of
      * [base/src/lgapvs01.cbl:42-46].
       BUILD-HOUSE-PAYLOAD.
           MOVE WS-FIXTURE-CHARS(101:15) TO WS-EXPECTED-PAYLOAD(1:15)
           MOVE WS-FIXTURE-CHARS(151:8) TO WS-EXPECTED-PAYLOAD(27:8)
           MOVE WS-FIXTURE-CHARS(127:9) TO WS-EXPECTED-PAYLOAD(35:9)
           MOVE 116 TO WS-DEC-OFFSET
           MOVE 3 TO WS-DEC-LENGTH
           PERFORM DECODE-FIXTURE-NUMBER
           IF WS-DEC-OK = 'Y'
               MOVE WS-FIXTURE-CHARS(116:3) TO WS-EXPECTED-PAYLOAD(16:3)
               MOVE 119 TO WS-DEC-OFFSET
               MOVE 8 TO WS-DEC-LENGTH
               PERFORM DECODE-FIXTURE-NUMBER
               IF WS-DEC-OK = 'Y'
                   MOVE WS-FIXTURE-CHARS(119:8)
                       TO WS-EXPECTED-PAYLOAD(19:8)
                   MOVE 'Y' TO WS-PAYLOAD-DERIVED
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Policy values                                                  *
      *----------------------------------------------------------------*
      * The seven host values the POLICY insert passed, the identity it
      * was given and the timestamp it read back, each compared with the
      * value this program knew before the chain ran.
       CHECK-POLICY-VALUES.
           IF WS-WANT-VALUES = 'Y'
               IF WS-WANT-POLICY-SQL = 'Y' AND HC-POL-PRESENT = 'Y'
                   PERFORM CHECK-POLICY-HOST-VALUES
               END-IF
               IF WS-WANT-IDENTITY = 'Y'
                   IF HC-IDENT-PRESENT = 'Y'
                       PERFORM CHECK-IDENTITY-VALUES
                   END-IF
                   IF HC-LCHG-PRESENT = 'Y'
                       PERFORM CHECK-TIMESTAMP-VALUES
                   END-IF
               END-IF
           END-IF.
      *
      * Slot 1 CUSTOMERNUMBER, slot 2 ISSUEDATE, slot 3 EXPIRYDATE,
      * slot 4 POLICYTYPE, slot 5 BROKERID, slot 6 BROKERSREFERENCE and
      * slot 7 PAYMENT of the block at [base/src/lgapdb01.cbl:268-288].
      * The two ten-digit COMMAREA fields reach nine-digit host
      * variables through the moves at [base/src/lgapdb01.cbl:176,264],
      * so the nine low-order digits are the value compared.
       CHECK-POLICY-HOST-VALUES.
           MOVE 10 TO WS-DEC-OFFSET
           MOVE 9 TO WS-DEC-LENGTH
           MOVE 'SQL_POLICY_CUSTOMERNUM' TO WS-CMP-FIELD
           MOVE HC-POL-CUSTOMERNUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 29 TO WS-DEC-OFFSET
           MOVE 10 TO WS-DEC-LENGTH
           MOVE 'SQL_POLICY_ISSUEDATE' TO WS-CMP-FIELD
           MOVE HC-POL-ISSUE-DATE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 39 TO WS-DEC-OFFSET
           MOVE 10 TO WS-DEC-LENGTH
           MOVE 'SQL_POLICY_EXPIRYDATE' TO WS-CMP-FIELD
           MOVE HC-POL-EXPIRY-DATE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 'SQL_POLICY_POLICYTYPE' TO WS-CMP-FIELD
           MOVE 1 TO WS-CMP-LEN
           MOVE WS-WANT-POLICY-TYPE TO WS-CMP-EXPECT-TEXT
           MOVE HC-POL-POLICYTYPE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE
           MOVE 76 TO WS-DEC-OFFSET
           MOVE 9 TO WS-DEC-LENGTH
           MOVE 'SQL_POLICY_BROKERID' TO WS-CMP-FIELD
           MOVE HC-POL-BROKERID TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 85 TO WS-DEC-OFFSET
           MOVE 10 TO WS-DEC-LENGTH
           MOVE 'SQL_POLICY_BROKERSREF' TO WS-CMP-FIELD
           MOVE HC-POL-BROKERSREF TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 95 TO WS-DEC-OFFSET
           MOVE 6 TO WS-DEC-LENGTH
           MOVE 'AMOUNT_PAYMENT' TO WS-CMP-FIELD
           MOVE HC-POL-PAYMENT TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-AMOUNT.
      *
      * The identity the read-back returned is the one this program
      * seeded, and the returned COMMAREA carries it, the round trip
      * [base/src/lgapdb01.cbl:308-311] performs.
       CHECK-IDENTITY-VALUES.
           MOVE 'SQL_POLICY_ASSIGNED_NUMBER' TO WS-CMP-FIELD
           MOVE WS-WANT-POLICYNUM TO WS-CMP-EXPECT-NUM
           MOVE HC-IDENT-POLICYNUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-NUM-VALUE
           MOVE 'CA_POLICY_NUM' TO WS-CMP-FIELD
           MOVE WS-WANT-POLICYNUM TO WS-CMP-EXPECT-NUM
           MOVE CA-POLICY-NUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-NUM-VALUE.
      *
      * The timestamp the read-back returned is the one this program
      * seeded, and the returned COMMAREA carries it, the move at
      * [base/src/lgapdb01.cbl:318] performs.
       CHECK-TIMESTAMP-VALUES.
           MOVE 'SQL_POLICY_ASSIGNED_LASTCHANGED' TO WS-CMP-FIELD
           MOVE 26 TO WS-CMP-LEN
           MOVE WS-WANT-LASTCHANGED TO WS-CMP-EXPECT-TEXT
           MOVE HC-LCHG-LASTCHANGED TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE
           MOVE 'CA_LASTCHANGED' TO WS-CMP-FIELD
           MOVE 26 TO WS-CMP-LEN
           MOVE WS-WANT-LASTCHANGED TO WS-CMP-EXPECT-TEXT
           MOVE CA-LASTCHANGED TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE.
      *
      *----------------------------------------------------------------*
      * Product values                                                 *
      *----------------------------------------------------------------*
      * Every host value of the product insert the case expects,
      * compared with the fixture. The policy number of each product
      * block is the identity the POLICY insert was given.
       CHECK-PRODUCT-VALUES.
           IF WS-WANT-PRODUCT-VALUES = 'Y'
               EVALUATE WS-PRODUCT-WANTED
                 WHEN 'M'
                   IF HC-MOT-PRESENT = 'Y'
                       PERFORM CHECK-MOTOR-VALUES
                   END-IF
                 WHEN 'C'
                   IF HC-COM-PRESENT = 'Y'
                       PERFORM CHECK-COMMERCIAL-VALUES
                   END-IF
                 WHEN 'E'
                   IF HC-END-PRESENT = 'Y'
                       PERFORM CHECK-ENDOWMENT-VALUES
                   END-IF
                 WHEN 'H'
                   IF HC-HOU-PRESENT = 'Y'
                       PERFORM CHECK-HOUSE-VALUES
                   END-IF
                 WHEN OTHER
                   CONTINUE
               END-EVALUATE
           END-IF.
      *
      * The ten host values of the block at
      * [base/src/lgapdb01.cbl:449-471].
       CHECK-MOTOR-VALUES.
           MOVE 'SQL_MOTOR_POLICYNUM' TO WS-CMP-FIELD
           MOVE WS-WANT-POLICYNUM TO WS-CMP-EXPECT-NUM
           MOVE HC-MOT-POLICYNUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-NUM-VALUE
           MOVE 101 TO WS-DEC-OFFSET
           MOVE 15 TO WS-DEC-LENGTH
           MOVE 'SQL_MOTOR_MAKE' TO WS-CMP-FIELD
           MOVE HC-MOT-MAKE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 116 TO WS-DEC-OFFSET
           MOVE 15 TO WS-DEC-LENGTH
           MOVE 'SQL_MOTOR_MODEL' TO WS-CMP-FIELD
           MOVE HC-MOT-MODEL TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 131 TO WS-DEC-OFFSET
           MOVE 6 TO WS-DEC-LENGTH
           MOVE 'SQL_MOTOR_VALUE' TO WS-CMP-FIELD
           MOVE HC-MOT-VALUE TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 137 TO WS-DEC-OFFSET
           MOVE 7 TO WS-DEC-LENGTH
           MOVE 'SQL_MOTOR_REGNUMBER' TO WS-CMP-FIELD
           MOVE HC-MOT-REGNUMBER TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 144 TO WS-DEC-OFFSET
           MOVE 8 TO WS-DEC-LENGTH
           MOVE 'SQL_MOTOR_COLOUR' TO WS-CMP-FIELD
           MOVE HC-MOT-COLOUR TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 152 TO WS-DEC-OFFSET
           MOVE 4 TO WS-DEC-LENGTH
           MOVE 'SQL_MOTOR_CC' TO WS-CMP-FIELD
           MOVE HC-MOT-CC TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 156 TO WS-DEC-OFFSET
           MOVE 10 TO WS-DEC-LENGTH
           MOVE 'SQL_MOTOR_MANUFACTURED' TO WS-CMP-FIELD
           MOVE HC-MOT-MANUFACTURED TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 166 TO WS-DEC-OFFSET
           MOVE 6 TO WS-DEC-LENGTH
           MOVE 'AMOUNT_MOTOR_PREMIUM' TO WS-CMP-FIELD
           MOVE HC-MOT-PREMIUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-AMOUNT
           MOVE 172 TO WS-DEC-OFFSET
           MOVE 6 TO WS-DEC-LENGTH
           MOVE 'SQL_MOTOR_ACCIDENTS' TO WS-CMP-FIELD
           MOVE HC-MOT-ACCIDENTS TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER.
      *
      * The twenty host values of the block at
      * [base/src/lgapdb01.cbl:499-545]. Slot 2 witnesses
      * CA-LASTCHANGED, which only the read-back at
      * [base/src/lgapdb01.cbl:316-321] populates, so the timestamp
      * seeded for this case is the value compared. The four peril
      * codes are compared here and carry no canonical target.
       CHECK-COMMERCIAL-VALUES.
           MOVE 'SQL_COMMERCIAL_POLICYNUM' TO WS-CMP-FIELD
           MOVE WS-WANT-POLICYNUM TO WS-CMP-EXPECT-NUM
           MOVE HC-COM-POLICYNUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-NUM-VALUE
           MOVE 'SQL_COMMERCIAL_REQUESTDATE' TO WS-CMP-FIELD
           MOVE 26 TO WS-CMP-LEN
           MOVE WS-WANT-LASTCHANGED TO WS-CMP-EXPECT-TEXT
           MOVE HC-COM-LASTCHANGED TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-TEXT-VALUE
           MOVE 29 TO WS-DEC-OFFSET
           MOVE 10 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_STARTDATE' TO WS-CMP-FIELD
           MOVE HC-COM-ISSUE-DATE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 39 TO WS-DEC-OFFSET
           MOVE 10 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_RENEWALDATE' TO WS-CMP-FIELD
           MOVE HC-COM-EXPIRY-DATE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 101 TO WS-DEC-OFFSET
           MOVE 255 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_ADDRESS' TO WS-CMP-FIELD
           MOVE HC-COM-ADDRESS TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 356 TO WS-DEC-OFFSET
           MOVE 8 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_ZIPCODE' TO WS-CMP-FIELD
           MOVE HC-COM-POSTCODE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 364 TO WS-DEC-OFFSET
           MOVE 11 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_LATITUDEN' TO WS-CMP-FIELD
           MOVE HC-COM-LATITUDE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 375 TO WS-DEC-OFFSET
           MOVE 11 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_LONGITUDEW' TO WS-CMP-FIELD
           MOVE HC-COM-LONGITUDE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 386 TO WS-DEC-OFFSET
           MOVE 255 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_CUSTOMER' TO WS-CMP-FIELD
           MOVE HC-COM-CUSTOMER TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 641 TO WS-DEC-OFFSET
           MOVE 255 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_PROPERTYTYPE' TO WS-CMP-FIELD
           MOVE HC-COM-PROPTYPE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           PERFORM CHECK-COMMERCIAL-AMOUNTS
           MOVE 944 TO WS-DEC-OFFSET
           MOVE 4 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_STATUS' TO WS-CMP-FIELD
           MOVE HC-COM-STATUS TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 948 TO WS-DEC-OFFSET
           MOVE 255 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_REJECTIONREASON' TO WS-CMP-FIELD
           MOVE HC-COM-REJECTREASON TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT.
      *
      * The four peril codes and the four premiums of that block, in
      * the column order [base/src/lgapdb01.cbl:502-521] lists.
       CHECK-COMMERCIAL-AMOUNTS.
           MOVE 896 TO WS-DEC-OFFSET
           MOVE 4 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_FIREPERIL' TO WS-CMP-FIELD
           MOVE HC-COM-FIREPERIL TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 900 TO WS-DEC-OFFSET
           MOVE 8 TO WS-DEC-LENGTH
           MOVE 'AMOUNT_FIRE_PREMIUM' TO WS-CMP-FIELD
           MOVE HC-COM-FIREPREMIUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-AMOUNT
           MOVE 908 TO WS-DEC-OFFSET
           MOVE 4 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_CRIMEPERIL' TO WS-CMP-FIELD
           MOVE HC-COM-CRIMEPERIL TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 912 TO WS-DEC-OFFSET
           MOVE 8 TO WS-DEC-LENGTH
           MOVE 'AMOUNT_CRIME_PREMIUM' TO WS-CMP-FIELD
           MOVE HC-COM-CRIMEPREMIUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-AMOUNT
           MOVE 920 TO WS-DEC-OFFSET
           MOVE 4 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_FLOODPERIL' TO WS-CMP-FIELD
           MOVE HC-COM-FLOODPERIL TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 924 TO WS-DEC-OFFSET
           MOVE 8 TO WS-DEC-LENGTH
           MOVE 'AMOUNT_FLOOD_PREMIUM' TO WS-CMP-FIELD
           MOVE HC-COM-FLOODPREMIUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-AMOUNT
           MOVE 932 TO WS-DEC-OFFSET
           MOVE 4 TO WS-DEC-LENGTH
           MOVE 'SQL_COMMERCIAL_WEATHERPERIL' TO WS-CMP-FIELD
           MOVE HC-COM-WEATHERPERIL TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 936 TO WS-DEC-OFFSET
           MOVE 8 TO WS-DEC-LENGTH
           MOVE 'AMOUNT_WEATHER_PREMIUM' TO WS-CMP-FIELD
           MOVE HC-COM-WEATHERPREMIUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-AMOUNT.
      *
      * The nine host values of the blocks at
      * [base/src/lgapdb01.cbl:346-366] and
      * [base/src/lgapdb01.cbl:368-386]. Slot 9 is the varchar host
      * whose length the SUBTRACT at
      * [base/src/lgapdb01.cbl:339-340] computes from EIBCALEN and the
      * required length 28 + 124; its characters are compared only for
      * a length the declared 3900 characters of
      * [base/src/lgapdb01.cbl:72] hold.
       CHECK-ENDOWMENT-VALUES.
           MOVE 'SQL_ENDOWMENT_POLICYNUM' TO WS-CMP-FIELD
           MOVE WS-WANT-POLICYNUM TO WS-CMP-EXPECT-NUM
           MOVE HC-END-POLICYNUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-NUM-VALUE
           MOVE 101 TO WS-DEC-OFFSET
           MOVE 1 TO WS-DEC-LENGTH
           MOVE 'SQL_ENDOWMENT_WITHPROFITS' TO WS-CMP-FIELD
           MOVE HC-END-WITH-PROFITS TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 102 TO WS-DEC-OFFSET
           MOVE 1 TO WS-DEC-LENGTH
           MOVE 'SQL_ENDOWMENT_EQUITIES' TO WS-CMP-FIELD
           MOVE HC-END-EQUITIES TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 103 TO WS-DEC-OFFSET
           MOVE 1 TO WS-DEC-LENGTH
           MOVE 'SQL_ENDOWMENT_MANAGEDFUND' TO WS-CMP-FIELD
           MOVE HC-END-MANAGED-FUND TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 104 TO WS-DEC-OFFSET
           MOVE 10 TO WS-DEC-LENGTH
           MOVE 'SQL_ENDOWMENT_FUNDNAME' TO WS-CMP-FIELD
           MOVE HC-END-FUND-NAME TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 114 TO WS-DEC-OFFSET
           MOVE 2 TO WS-DEC-LENGTH
           MOVE 'SQL_ENDOWMENT_TERM' TO WS-CMP-FIELD
           MOVE HC-END-TERM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 116 TO WS-DEC-OFFSET
           MOVE 6 TO WS-DEC-LENGTH
           MOVE 'SQL_ENDOWMENT_SUMASSURED' TO WS-CMP-FIELD
           MOVE HC-END-SUMASSURED TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 122 TO WS-DEC-OFFSET
           MOVE 31 TO WS-DEC-LENGTH
           MOVE 'SQL_ENDOWMENT_LIFEASSURED' TO WS-CMP-FIELD
           MOVE HC-END-LIFE-ASSURED TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           PERFORM CHECK-ENDOWMENT-PADDING.
      *
      * The length of the varchar host is EIBCALEN less the 152
      * characters the endowment route requires, and its characters are
      * the leading characters of CA-E-PADDING-DATA
      * [base/src/lgcmarea.cpy:54] when that length is between 1 and
      * the 3900 the host declares.
       CHECK-ENDOWMENT-PADDING.
           COMPUTE WS-CMP-EXPECT-NUM = WS-EIBCALEN-AT-CALL - 152
           END-COMPUTE
           MOVE 'SQL_ENDOWMENT_PADDINGLEN' TO WS-CMP-FIELD
           MOVE HC-END-VARY-LEN TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-NUM-VALUE
           IF HC-END-VARY-LEN > ZERO AND HC-END-VARY-LEN NOT > 3900
               MOVE 153 TO WS-DEC-OFFSET
               MOVE HC-END-VARY-LEN TO WS-DEC-LENGTH
               IF WS-DEC-LENGTH > 255
                   MOVE 255 TO WS-DEC-LENGTH
               END-IF
               MOVE 'SQL_ENDOWMENT_PADDINGDATA' TO WS-CMP-FIELD
               MOVE HC-END-VARY-CHAR(1:WS-DEC-LENGTH)
                   TO WS-CMP-ACTUAL-TEXT
               PERFORM COMPARE-FIXTURE-TEXT
           END-IF.
      *
      * The seven host values of the block at
      * [base/src/lgapdb01.cbl:409-425].
       CHECK-HOUSE-VALUES.
           MOVE 'SQL_HOUSE_POLICYNUM' TO WS-CMP-FIELD
           MOVE WS-WANT-POLICYNUM TO WS-CMP-EXPECT-NUM
           MOVE HC-HOU-POLICYNUM TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-NUM-VALUE
           MOVE 101 TO WS-DEC-OFFSET
           MOVE 15 TO WS-DEC-LENGTH
           MOVE 'SQL_HOUSE_PROPERTYTYPE' TO WS-CMP-FIELD
           MOVE HC-HOU-PROPERTY-TYPE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 116 TO WS-DEC-OFFSET
           MOVE 3 TO WS-DEC-LENGTH
           MOVE 'SQL_HOUSE_BEDROOMS' TO WS-CMP-FIELD
           MOVE HC-HOU-BEDROOMS TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 119 TO WS-DEC-OFFSET
           MOVE 8 TO WS-DEC-LENGTH
           MOVE 'SQL_HOUSE_VALUE' TO WS-CMP-FIELD
           MOVE HC-HOU-VALUE TO WS-CMP-ACTUAL-NUM
           PERFORM COMPARE-FIXTURE-NUMBER
           MOVE 127 TO WS-DEC-OFFSET
           MOVE 20 TO WS-DEC-LENGTH
           MOVE 'SQL_HOUSE_HOUSENAME' TO WS-CMP-FIELD
           MOVE HC-HOU-HOUSE-NAME TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 147 TO WS-DEC-OFFSET
           MOVE 4 TO WS-DEC-LENGTH
           MOVE 'SQL_HOUSE_HOUSENUMBER' TO WS-CMP-FIELD
           MOVE HC-HOU-HOUSE-NUMBER TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT
           MOVE 151 TO WS-DEC-OFFSET
           MOVE 8 TO WS-DEC-LENGTH
           MOVE 'SQL_HOUSE_POSTCODE' TO WS-CMP-FIELD
           MOVE HC-HOU-POSTCODE TO WS-CMP-ACTUAL-TEXT
           PERFORM COMPARE-FIXTURE-TEXT.
      *
      *----------------------------------------------------------------*
      * Fixture decoding and comparison                                *
      *----------------------------------------------------------------*
      * Copies WS-DEC-LENGTH characters from WS-DEC-OFFSET of the
      * fixture image.
       DECODE-FIXTURE-TEXT.
           MOVE SPACES TO WS-DEC-TEXT
           MOVE WS-FIXTURE-CHARS(WS-DEC-OFFSET:WS-DEC-LENGTH)
               TO WS-DEC-TEXT.
      *
      * Copies the same characters and reports whether every one of
      * them is a digit. WS-DEC-NUM holds the value they spell, and
      * zero when one of them is not a digit.
       DECODE-FIXTURE-NUMBER.
           PERFORM DECODE-FIXTURE-TEXT
           MOVE ZERO TO WS-DEC-NUM
           MOVE 'N' TO WS-HAS-DIGIT
           MOVE 'N' TO WS-HAS-NON-DIGIT
           PERFORM VARYING WS-TRIM-IX FROM 1 BY 1
                   UNTIL WS-TRIM-IX > WS-DEC-LENGTH
               IF WS-DEC-TEXT(WS-TRIM-IX:1) IS NUMERIC
                   MOVE 'Y' TO WS-HAS-DIGIT
               ELSE
                   MOVE 'Y' TO WS-HAS-NON-DIGIT
               END-IF
           END-PERFORM
           IF WS-HAS-DIGIT = 'Y' AND WS-HAS-NON-DIGIT = 'N'
               MOVE 'Y' TO WS-DEC-OK
               COMPUTE WS-DEC-NUM =
                   FUNCTION NUMVAL(WS-DEC-TEXT(1:WS-DEC-LENGTH))
               END-COMPUTE
           ELSE
               MOVE 'N' TO WS-DEC-OK
           END-IF.
      *
      * Compares the captured text in WS-CMP-ACTUAL-TEXT with the
      * characters the fixture holds at WS-DEC-OFFSET.
       COMPARE-FIXTURE-TEXT.
           PERFORM DECODE-FIXTURE-TEXT
           MOVE WS-DEC-TEXT TO WS-CMP-EXPECT-TEXT
           MOVE WS-DEC-LENGTH TO WS-CMP-LEN
           PERFORM COMPARE-TEXT-VALUE.
      *
      * Compares the captured number in WS-CMP-ACTUAL-NUM with the
      * value the fixture spells at WS-DEC-OFFSET. A fixture field that
      * does not spell a number is reported as a failed value check.
       COMPARE-FIXTURE-NUMBER.
           PERFORM DECODE-FIXTURE-NUMBER
           IF WS-DEC-OK = 'Y'
               MOVE WS-DEC-NUM TO WS-CMP-EXPECT-NUM
               PERFORM COMPARE-NUM-VALUE
           ELSE
               PERFORM REPORT-FIXTURE-NOT-NUMERIC
           END-IF.
      *
      * Compares one of the six amount fields. The fields are unsigned
      * display integers moved without arithmetic, so an equal
      * comparison is the expected result and any difference is a whole
      * number, above the 0.01 the acceptance contract allows.
       COMPARE-FIXTURE-AMOUNT.
           PERFORM DECODE-FIXTURE-NUMBER
           IF WS-DEC-OK = 'Y'
               MOVE WS-DEC-NUM TO WS-CMP-EXPECT-NUM
               ADD 1 TO WS-AMOUNT-CHECKS
               END-ADD
               COMPUTE WS-AMOUNT-DELTA =
                   WS-CMP-ACTUAL-NUM - WS-CMP-EXPECT-NUM
               END-COMPUTE
               IF WS-AMOUNT-DELTA < ZERO
                   COMPUTE WS-AMOUNT-DELTA = 0 - WS-AMOUNT-DELTA
                   END-COMPUTE
               END-IF
               IF WS-AMOUNT-DELTA > WS-AMOUNT-MAX-DELTA
                   MOVE WS-AMOUNT-DELTA TO WS-AMOUNT-MAX-DELTA
               END-IF
               IF WS-AMOUNT-DELTA NOT = ZERO
                   PERFORM REPORT-AMOUNT-DIFFERENCE
               END-IF
           ELSE
               PERFORM REPORT-FIXTURE-NOT-NUMERIC
           END-IF.
      *
      * Compares WS-CMP-LEN characters of the expected and captured
      * text and names the first character that differs.
       COMPARE-TEXT-VALUE.
           IF WS-CMP-EXPECT-TEXT(1:WS-CMP-LEN) NOT =
                   WS-CMP-ACTUAL-TEXT(1:WS-CMP-LEN)
               PERFORM FIND-TEXT-DIFFERENCE
               PERFORM NAME-VALUE-CHECK
               PERFORM REPORT-VALUE-FAILURE
               MOVE WS-CMP-DIFF-POS TO WS-COUNT-EDIT
               DISPLAY 'DRIVER:   field '
                       FUNCTION TRIM(WS-CMP-FIELD)
                       ' differs at character '
                       FUNCTION TRIM(WS-COUNT-EDIT)
               END-DISPLAY
               DISPLAY 'DRIVER:   expected ['
                       WS-CMP-EXPECT-TEXT(WS-CMP-DIFF-POS:
                                          WS-CMP-WINDOW) ']'
               END-DISPLAY
               DISPLAY 'DRIVER:   captured ['
                       WS-CMP-ACTUAL-TEXT(WS-CMP-DIFF-POS:
                                          WS-CMP-WINDOW) ']'
               END-DISPLAY
           END-IF.
      *
      * Compares the expected and captured numbers.
       COMPARE-NUM-VALUE.
           IF WS-CMP-EXPECT-NUM NOT = WS-CMP-ACTUAL-NUM
               PERFORM NAME-VALUE-CHECK
               PERFORM REPORT-VALUE-FAILURE
               MOVE WS-CMP-EXPECT-NUM TO WS-CMP-EXPECT-EDIT
               MOVE WS-CMP-ACTUAL-NUM TO WS-CMP-ACTUAL-EDIT
               DISPLAY 'DRIVER:   field '
                       FUNCTION TRIM(WS-CMP-FIELD)
                       ' expected ' WS-CMP-EXPECT-EDIT
                       ' captured ' WS-CMP-ACTUAL-EDIT
               END-DISPLAY
           END-IF.
      *
      * Reports one amount that differs, with the difference the
      * comparison found.
       REPORT-AMOUNT-DIFFERENCE.
           PERFORM NAME-VALUE-CHECK
           PERFORM REPORT-VALUE-FAILURE
           MOVE WS-CMP-EXPECT-NUM TO WS-CMP-EXPECT-EDIT
           MOVE WS-CMP-ACTUAL-NUM TO WS-CMP-ACTUAL-EDIT
           DISPLAY 'DRIVER:   field ' FUNCTION TRIM(WS-CMP-FIELD)
                   ' expected ' WS-CMP-EXPECT-EDIT
                   ' captured ' WS-CMP-ACTUAL-EDIT
           END-DISPLAY
           MOVE WS-AMOUNT-DELTA TO WS-CMP-ACTUAL-EDIT
           DISPLAY 'DRIVER:   difference ' WS-CMP-ACTUAL-EDIT
                   ' exceeds the 0.01 the acceptance contract allows'
           END-DISPLAY.
      *
      * Reports a fixture field the expected value cannot be decoded
      * from because its characters are not all digits.
       REPORT-FIXTURE-NOT-NUMERIC.
           PERFORM NAME-VALUE-CHECK
           PERFORM REPORT-VALUE-FAILURE
           MOVE WS-DEC-OFFSET TO WS-COUNT-EDIT
           DISPLAY 'DRIVER:   field ' FUNCTION TRIM(WS-CMP-FIELD)
                   ' expects digits at fixture offset '
                   FUNCTION TRIM(WS-COUNT-EDIT)
                   ' and the fixture holds ['
                   WS-DEC-TEXT(1:WS-DEC-LENGTH) ']'
           END-DISPLAY.
      *
      * Names the value check being reported after the field it
      * compares.
       NAME-VALUE-CHECK.
           MOVE SPACES TO WS-CHECK-NAME
           STRING 'VALUE-' DELIMITED BY SIZE
                  FUNCTION TRIM(WS-CMP-FIELD) DELIMITED BY SIZE
               INTO WS-CHECK-NAME
           END-STRING.
      *
      * Finds the first character of the compared width that differs
      * and the width shown from there, at most 30 characters.
       FIND-TEXT-DIFFERENCE.
           MOVE ZERO TO WS-CMP-DIFF-POS
           PERFORM VARYING WS-TRIM-IX FROM 1 BY 1
                   UNTIL WS-TRIM-IX > WS-CMP-LEN
                      OR WS-CMP-DIFF-POS > ZERO
               IF WS-CMP-EXPECT-TEXT(WS-TRIM-IX:1) NOT =
                       WS-CMP-ACTUAL-TEXT(WS-TRIM-IX:1)
                   MOVE WS-TRIM-IX TO WS-CMP-DIFF-POS
               END-IF
           END-PERFORM
           IF WS-CMP-DIFF-POS = ZERO
               MOVE 1 TO WS-CMP-DIFF-POS
           END-IF
           COMPUTE WS-CMP-WINDOW = WS-CMP-LEN - WS-CMP-DIFF-POS + 1
           END-COMPUTE
           IF WS-CMP-WINDOW > 30
               MOVE 30 TO WS-CMP-WINDOW
           END-IF
           IF WS-CMP-WINDOW < 1
               MOVE 1 TO WS-CMP-WINDOW
           END-IF.
      *
      *----------------------------------------------------------------*
      * Status selection                                               *
      *----------------------------------------------------------------*
      * Reports the most specific condition observed: a file or
      * environment failure already recorded, then a chain that could
      * not be called, then an abend state that differs from the
      * expected one, then a return code that differs, then a capture
      * that is missing or inconsistent, then a captured value that
      * differs from the fixture-derived expected value.
       SELECT-EXIT-CODE.
           EVALUATE TRUE
             WHEN WS-EXIT-CODE NOT = ZERO
               CONTINUE
             WHEN WS-CALL-FAILED = 'Y'
               MOVE 07 TO WS-EXIT-CODE
             WHEN WS-ABEND-FAILURES > ZERO
               MOVE 02 TO WS-EXIT-CODE
             WHEN WS-RC-FAILURES > ZERO
               MOVE 01 TO WS-EXIT-CODE
             WHEN WS-CAPTURE-FAILURES > ZERO
               MOVE 03 TO WS-EXIT-CODE
             WHEN WS-VALUE-FAILURES > ZERO
               MOVE 06 TO WS-EXIT-CODE
             WHEN WS-FAILURES > ZERO
               MOVE 03 TO WS-EXIT-CODE
             WHEN OTHER
               CONTINUE
           END-EVALUATE
           IF WS-FAILURES > ZERO
               DISPLAY 'DRIVER: ' WS-FAILURES
                       ' named check(s) failed'
               END-DISPLAY
           END-IF.
      *
      * Names one failed check in the log and counts it.
       REPORT-FAILED-CHECK.
           IF WS-FAILURES < 99
               ADD 1 TO WS-FAILURES
               END-ADD
           END-IF
           DISPLAY 'DRIVER: check failed '
                   FUNCTION TRIM(WS-CHECK-NAME)
           END-DISPLAY
           MOVE SPACES TO WS-CHECK-NAME.
      *
      * Counts one failed check against the status it selects, then
      * names it.
       REPORT-ABEND-FAILURE.
           IF WS-ABEND-FAILURES < 99
               ADD 1 TO WS-ABEND-FAILURES
               END-ADD
           END-IF
           PERFORM REPORT-FAILED-CHECK.
      *
       REPORT-RC-FAILURE.
           IF WS-RC-FAILURES < 99
               ADD 1 TO WS-RC-FAILURES
               END-ADD
           END-IF
           PERFORM REPORT-FAILED-CHECK.
      *
       REPORT-CAPTURE-FAILURE.
           IF WS-CAPTURE-FAILURES < 99
               ADD 1 TO WS-CAPTURE-FAILURES
               END-ADD
           END-IF
           PERFORM REPORT-FAILED-CHECK.
      *
       REPORT-VALUE-FAILURE.
           IF WS-VALUE-FAILURES < 99
               ADD 1 TO WS-VALUE-FAILURES
               END-ADD
           END-IF
           PERFORM REPORT-FAILED-CHECK.
      *----------------------------------------------------------------*
