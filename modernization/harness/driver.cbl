      ******************************************************************
      *                                                                *
      *                            DRIVER                              *
      *                                                                *
      *   Harness driver for the GenApp Policy-Issue chain             *
      *                                                                *
      ******************************************************************
      *
      * Stands in for the CICS caller of LGAPOL01. Reads one generated
      * 32,500-character COMMAREA record, seeds the shared EXTERNAL
      * harness state, calls the translated LGAPOL01 once, then writes
      * the post-chain COMMAREA record and the capture file that the
      * extraction, landing and diff steps read.
      *
      * Files, each named by a literal assign name and located through
      * GnuCOBOL filename mapping:
      *   SAMPLEFILE  input   DD_SAMPLEFILE  generated sample record
      *   POSTFILE    output  DD_POSTFILE    commarea_post.dat
      *   CAPTFILE    output  DD_CAPTFILE    captures.txt
      * Each name is read from DD_<name> first and from <name> when
      * DD_<name> is unset.
      *
      * Environment items read:
      *   HARNESS_CASE           case label; CA-REQUEST-ID when unset
      *   HARNESS_POLICY_NUMBER  identity seed for HC-SEED-POLICYNUM
      *   HARNESS_LASTCHANGED    timestamp seed for HC-SEED-LASTCHANGED
      *   COB_LS_FIXED           must hold a true value; the 32,500-
      *                          character post-chain record is written
      *                          in full only while it does
      *
      * Exit status:
      *   0  every check passed
      *   1  the chain returned a code other than '00'
      *   2  an abend was captured
      *   3  a required capture is missing or inconsistent
      *   4  a file input-output operation failed
      *   5  a required environment item was not provided
      *
      * Harness topology: Figure 5 - Validation Harness Control Flow
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
      * Generated fixed-width sample record read into the COMMAREA.
           SELECT SAMPLE-FILE
               ASSIGN TO "SAMPLEFILE"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-SAMPLE-STATUS.
      *
      * Post-chain COMMAREA record, one line of 32,500 characters.
           SELECT POST-FILE
               ASSIGN TO "POSTFILE"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-POST-STATUS.
      *
      * Capture file, one NAME=VALUE line per captured value.
           SELECT CAPTURE-FILE
               ASSIGN TO "CAPTFILE"
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
      * File handling                                                  *
      *----------------------------------------------------------------*
       01  WS-FILE-STATUS.
           03 WS-SAMPLE-STATUS         PIC XX.
           03 WS-POST-STATUS           PIC XX.
           03 WS-CAPT-STATUS           PIC XX.
      *
      * Resolved path of each file, as displayed in the run header.
       01  WS-FILE-PATHS.
           03 WS-SAMPLE-PATH           PIC X(255).
           03 WS-POST-PATH             PIC X(255).
           03 WS-CAPT-PATH             PIC X(255).
      *
      * Set to 'Y' once the capture file is open for output.
       01  WS-CAPT-OPEN                PIC X.
      *
      *----------------------------------------------------------------*
      * Run control                                                    *
      *----------------------------------------------------------------*
      * Case label taken from HARNESS_CASE, or from CA-REQUEST-ID of
      * the loaded record when that item is unset.
       01  WS-CASE                     PIC X(6).
      *
      * Status returned to the caller; the values are listed in the
      * program header.
       01  WS-EXIT-CODE                PIC 9(2).
      *
      * Number of named verdict checks that failed.
       01  WS-FAILURES                 PIC 9(2).
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
       01  WS-ENV-TEXT                 PIC X(255).
       01  WS-ENV-FLAG                 PIC X(8).
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
      * Product table the request id routes to: 'M' motor,
      * 'C' commercial, 'E' endowment, 'H' house, '?' none.
       01  WS-PRODUCT-WANTED           PIC X.
      *
      * Presence flag of that product table, and 'Y' once a product
      * table the request id does not route to reports a capture.
       01  WS-PRODUCT-FOUND            PIC X.
       01  WS-EXTRA-PRODUCT            PIC X.
      *
      * Character view of the returned CA-RETURN-CODE.
       01  WS-RETURN-CODE-TEXT         PIC XX.
      *
      * Name of the check being reported by REPORT-FAILED-CHECK.
       01  WS-CHECK-NAME               PIC X(40).
      *
      *----------------------------------------------------------------*
      * Constants                                                      *
      *----------------------------------------------------------------*
      * File the KSDSPOLY write names.
       01  WS-VSAM-FILE-NAME           PIC X(8) VALUE 'KSDSPOLY'.
      *
      * Record and key length the KSDSPOLY write is expected to pass.
       01  WS-VSAM-LEN-EXPECTED        PIC 9(4) VALUE 64.
       01  WS-VSAM-KEYLEN-EXPECTED     PIC 9(4) VALUE 21.
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
           PERFORM RESOLVE-CASE-LABEL
           PERFORM DISPLAY-RUN-HEADER
           PERFORM EXECUTE-CHAIN
           PERFORM WRITE-POST-RECORD
           IF WS-EXIT-CODE NOT = ZERO
               PERFORM RETURN-TO-CALLER
               GOBACK
           END-IF
           PERFORM OPEN-CAPTURE-FILE
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
           PERFORM EMIT-VSAM-CAPTURES
           PERFORM EMIT-FAILURE-SURFACE
           PERFORM EVALUATE-VERDICT
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
           MOVE 'N' TO WS-CALL-FAILED
           MOVE 'N' TO WS-CAPT-OPEN
           MOVE 'N' TO WS-LS-FIXED
           MOVE ZERO TO WS-EIBCALEN-AT-CALL
           MOVE SPACES TO WS-KEY-NAME
           MOVE SPACES TO WS-VALUE
           MOVE SPACES TO WS-LINE
           MOVE 1 TO WS-LINE-LEN
           MOVE SPACES TO WS-CHECK-NAME
           MOVE '?' TO WS-PRODUCT-WANTED.
      *
      * Returns the status listed in the program header to the caller.
       RETURN-TO-CALLER.
           MOVE WS-EXIT-CODE TO RETURN-CODE
           DISPLAY 'DRIVER: exit status ' WS-EXIT-CODE.
      *
      *================================================================*
      * Environment                                                    *
      *================================================================*
      * Locates the three files, reads the case label and confirms the
      * setting the full-length post-chain record depends on.
       RESOLVE-ENVIRONMENT.
           PERFORM RESOLVE-SAMPLE-PATH
           PERFORM RESOLVE-POST-PATH
           PERFORM RESOLVE-CAPT-PATH
           PERFORM RESOLVE-LS-FIXED
           MOVE SPACES TO WS-CASE
           ACCEPT WS-CASE FROM ENVIRONMENT "HARNESS_CASE"
           IF WS-SAMPLE-PATH = SPACES
               DISPLAY 'DRIVER: no path for SAMPLEFILE; set '
                       'DD_SAMPLEFILE to the generated sample record'
               MOVE 05 TO WS-EXIT-CODE
           END-IF
           IF WS-POST-PATH = SPACES
               DISPLAY 'DRIVER: no path for POSTFILE; set DD_POSTFILE '
                       'to the post-chain record to be written'
               MOVE 05 TO WS-EXIT-CODE
           END-IF
           IF WS-CAPT-PATH = SPACES
               DISPLAY 'DRIVER: no path for CAPTFILE; set DD_CAPTFILE '
                       'to the capture file to be written'
               MOVE 05 TO WS-EXIT-CODE
           END-IF
           IF WS-LS-FIXED = 'N'
               DISPLAY 'DRIVER: COB_LS_FIXED does not hold a true '
                       'value, so the 32500-character post-chain '
                       'record would be written without its trailing '
                       'spaces'
               MOVE 05 TO WS-EXIT-CODE
           END-IF.
      *
      * Each path is taken from DD_<assign-name>, and from
      * <assign-name> when the DD_ item is unset.
       RESOLVE-SAMPLE-PATH.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "DD_SAMPLEFILE"
           IF WS-ENV-TEXT = SPACES
               ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "SAMPLEFILE"
           END-IF
           MOVE WS-ENV-TEXT TO WS-SAMPLE-PATH.
      *
       RESOLVE-POST-PATH.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "DD_POSTFILE"
           IF WS-ENV-TEXT = SPACES
               ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "POSTFILE"
           END-IF
           MOVE WS-ENV-TEXT TO WS-POST-PATH.
      *
       RESOLVE-CAPT-PATH.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "DD_CAPTFILE"
           IF WS-ENV-TEXT = SPACES
               ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "CAPTFILE"
           END-IF
           MOVE WS-ENV-TEXT TO WS-CAPT-PATH.
      *
      * Accepts the spellings the runtime reads as true for a boolean
      * configuration item.
       RESOLVE-LS-FIXED.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "COB_LS_FIXED"
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
      * The case label is HARNESS_CASE, or the request id of the loaded
      * record when that item is unset.
       RESOLVE-CASE-LABEL.
           IF WS-CASE = SPACES
               MOVE CA-REQUEST-ID TO WS-CASE
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
           MOVE 32500 TO EIBCALEN
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
      * that reports a statement not yet captured.
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
           MOVE 'N' TO HC-ABEND-PRESENT.
      *
      * HARNESS_POLICY_NUMBER reaches HC-SEED-POLICYNUM when it holds
      * at most nine digits and a value above zero. The item is left
      * at zero otherwise.
       SEED-IDENTITY-SEED.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "HARNESS_POLICY_NUMBER"
           MOVE ZERO TO WS-SEED-POLICYNUM
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN > ZERO AND WS-SEED-LEN NOT > 9
               PERFORM SCAN-SEED-DIGITS
               IF WS-HAS-DIGIT = 'Y' AND WS-HAS-NON-DIGIT = 'N'
                   COMPUTE WS-SEED-POLICYNUM =
                       FUNCTION NUMVAL(WS-ENV-TEXT(1:WS-SEED-LEN))
               END-IF
           END-IF
           IF WS-SEED-POLICYNUM > ZERO
               MOVE WS-SEED-POLICYNUM TO HC-SEED-POLICYNUM
           END-IF.
      *
      * HARNESS_LASTCHANGED reaches HC-SEED-LASTCHANGED when it holds
      * exactly 26 characters and none of them is a space. The item is
      * left at spaces otherwise.
       SEED-TIMESTAMP-SEED.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT "HARNESS_LASTCHANGED"
           PERFORM TRIM-ENV-TEXT
           IF WS-SEED-LEN = 26
               MOVE ZERO TO WS-SPACE-COUNT
               INSPECT WS-ENV-TEXT(1:26) TALLYING WS-SPACE-COUNT
                   FOR ALL SPACE
               IF WS-SPACE-COUNT = ZERO
                   MOVE WS-ENV-TEXT(1:26) TO HC-SEED-LASTCHANGED
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
      * Loads the one generated record of the sample file into the
      * COMMAREA. The record holds 32,500 characters.
       READ-SAMPLE-RECORD.
           OPEN INPUT SAMPLE-FILE
           IF WS-SAMPLE-STATUS NOT = '00'
               DISPLAY 'DRIVER: open input failed on SAMPLEFILE '
                       FUNCTION TRIM(WS-SAMPLE-PATH)
                       ', file status ' WS-SAMPLE-STATUS
               MOVE 04 TO WS-EXIT-CODE
           ELSE
               READ SAMPLE-FILE
                   AT END
                       CONTINUE
               END-READ
               IF WS-SAMPLE-STATUS = '00'
                   MOVE SAMPLE-REC TO WS-COMMAREA-CHARS
               ELSE
                   DISPLAY 'DRIVER: read failed on SAMPLEFILE '
                           FUNCTION TRIM(WS-SAMPLE-PATH)
                           ', file status ' WS-SAMPLE-STATUS
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
               CLOSE SAMPLE-FILE
               IF WS-SAMPLE-STATUS NOT = '00'
                   DISPLAY 'DRIVER: close failed on SAMPLEFILE '
                           FUNCTION TRIM(WS-SAMPLE-PATH)
                           ', file status ' WS-SAMPLE-STATUS
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      *================================================================*
      * Chain execution                                                *
      *================================================================*
      * Sets the COMMAREA length the chain reads, records that value,
      * and calls the first program of the chain once. LGAPDB01 and
      * LGAPVS01 are called by the chain itself.
       EXECUTE-CHAIN.
           MOVE 32500 TO EIBCALEN
           MOVE EIBCALEN TO WS-EIBCALEN-AT-CALL
           CALL "LGAPOL01" USING WS-COMMAREA
               ON EXCEPTION
                   MOVE 'Y' TO WS-CALL-FAILED
                   DISPLAY 'DRIVER: module LGAPOL01 could not be '
                           'called; set COB_LIBRARY_PATH to the '
                           'directory holding the compiled harness '
                           'modules'
           END-CALL.
      *
      *================================================================*
      * Post-chain record                                              *
      *================================================================*
      * Writes the returned COMMAREA as one line of 32,500 characters,
      * the length the extraction step decodes by absolute offset.
       WRITE-POST-RECORD.
           MOVE WS-COMMAREA-CHARS TO POST-REC
           OPEN OUTPUT POST-FILE
           IF WS-POST-STATUS NOT = '00'
               DISPLAY 'DRIVER: open output failed on POSTFILE '
                       FUNCTION TRIM(WS-POST-PATH)
                       ', file status ' WS-POST-STATUS
               MOVE 04 TO WS-EXIT-CODE
           ELSE
               WRITE POST-REC
               IF WS-POST-STATUS NOT = '00'
                   DISPLAY 'DRIVER: write failed on POSTFILE '
                           FUNCTION TRIM(WS-POST-PATH)
                           ', file status ' WS-POST-STATUS
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
               CLOSE POST-FILE
               IF WS-POST-STATUS NOT = '00'
                   DISPLAY 'DRIVER: close failed on POSTFILE '
                           FUNCTION TRIM(WS-POST-PATH)
                           ', file status ' WS-POST-STATUS
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      *================================================================*
      * Capture file                                                   *
      *================================================================*
       OPEN-CAPTURE-FILE.
           OPEN OUTPUT CAPTURE-FILE
           IF WS-CAPT-STATUS NOT = '00'
               DISPLAY 'DRIVER: open output failed on CAPTFILE '
                       FUNCTION TRIM(WS-CAPT-PATH)
                       ', file status ' WS-CAPT-STATUS
               MOVE 04 TO WS-EXIT-CODE
           ELSE
               MOVE 'Y' TO WS-CAPT-OPEN
           END-IF.
      *
       CLOSE-CAPTURE-FILE.
           IF WS-CAPT-OPEN = 'Y'
               CLOSE CAPTURE-FILE
               MOVE 'N' TO WS-CAPT-OPEN
               IF WS-CAPT-STATUS NOT = '00'
                   DISPLAY 'DRIVER: close failed on CAPTFILE '
                           FUNCTION TRIM(WS-CAPT-PATH)
                           ', file status ' WS-CAPT-STATUS
                   MOVE 04 TO WS-EXIT-CODE
               END-IF
           END-IF.
      *
      *================================================================*
      * Run header and COMMAREA extract                                *
      *================================================================*
       DISPLAY-RUN-HEADER.
           DISPLAY 'DRIVER: case ' WS-CASE
                   ' request id ' CA-REQUEST-ID
           DISPLAY 'DRIVER: SAMPLEFILE ' FUNCTION TRIM(WS-SAMPLE-PATH)
           DISPLAY 'DRIVER: POSTFILE   ' FUNCTION TRIM(WS-POST-PATH)
           DISPLAY 'DRIVER: CAPTFILE   ' FUNCTION TRIM(WS-CAPT-PATH).
      *
      * The 28-character header and the 72-character common section of
      * the returned record, then the amount fields of the overlay the
      * request id selects. The whole record is in the post file.
       DISPLAY-COMMAREA-EXTRACT.
           DISPLAY 'DRIVER: post-chain COMMAREA characters 1-100'
           DISPLAY WS-COMMAREA-CHARS(1:100)
           EVALUATE CA-REQUEST-ID
             WHEN '01AMOT'
               DISPLAY 'DRIVER: CA-M-PREMIUM ' CA-M-PREMIUM
             WHEN '01ACOM'
               DISPLAY 'DRIVER: CA-B-FirePremium '
                       CA-B-FirePremium
               DISPLAY 'DRIVER: CA-B-CrimePremium '
                       CA-B-CrimePremium
               DISPLAY 'DRIVER: CA-B-FloodPremium '
                       CA-B-FloodPremium
               DISPLAY 'DRIVER: CA-B-WeatherPremium '
                       CA-B-WeatherPremium
             WHEN OTHER
               DISPLAY 'DRIVER: request id ' CA-REQUEST-ID
                       ' selects no requested overlay amount'
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
           MOVE WS-LINE TO CAPTURE-REC
           WRITE CAPTURE-REC
           IF WS-CAPT-STATUS NOT = '00'
               DISPLAY 'DRIVER: write failed on CAPTFILE '
                       FUNCTION TRIM(WS-CAPT-PATH)
                       ', file status ' WS-CAPT-STATUS
               MOVE 04 TO WS-EXIT-CODE
           END-IF
           DISPLAY WS-LINE(1:WS-LINE-LEN)
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
           MOVE SPACES TO WS-VALUE
           MOVE WS-INT-EDIT(WS-INT-FIRST:WS-INT-LEN) TO WS-VALUE
           PERFORM EMIT-VALUE.
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
           MOVE 'EIBCALEN_AT_CALL' TO WS-KEY-NAME
           MOVE WS-EIBCALEN-AT-CALL TO WS-INT-VALUE
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
      * The presence of the two product inserts the executed samples do
      * not reach.
       EMIT-OTHER-PRODUCT-CAPTURES.
           MOVE 'SQL_ENDOWMENT_PRESENT' TO WS-KEY-NAME
           MOVE HC-END-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_HOUSE_PRESENT' TO WS-KEY-NAME
           MOVE HC-HOU-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE.
      *
      * How often the identity and timestamp read-backs executed, and
      * the result of the most recent SQL operation.
       EMIT-SQL-BOOKKEEPING.
           MOVE 'SQL_IDENTITY_CALLS' TO WS-KEY-NAME
           MOVE HC-IDENT-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQL_LASTCHANGED_CALLS' TO WS-KEY-NAME
           MOVE HC-LCHG-COUNT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'SQLCODE_LAST' TO WS-KEY-NAME
           MOVE SQLCODE TO WS-INT-VALUE
           PERFORM EMIT-INTEGER.
      *
      *================================================================*
      * VSAM write captures                                            *
      *================================================================*
      * The record image, the key, the two lengths and the response of
      * the KSDSPOLY write.
       EMIT-VSAM-CAPTURES.
           MOVE 'VSAM_PRESENT' TO WS-KEY-NAME
           MOVE HC-VSAM-PRESENT TO WS-VALUE
           PERFORM EMIT-VALUE
           MOVE 'VSAM_FILE' TO WS-KEY-NAME
           MOVE WS-VSAM-FILE-NAME TO WS-VALUE
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
           PERFORM EMIT-INTEGER.
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
      * that fails is named in the log and counted in WS-FAILURES.
       EVALUATE-VERDICT.
           PERFORM CHECK-CHAIN-CALLED
           PERFORM CHECK-RETURN-CODE
           PERFORM CHECK-ABEND-ABSENT
           PERFORM CHECK-POLICY-CAPTURE
           PERFORM CHECK-PRODUCT-CAPTURES
           PERFORM CHECK-VSAM-CAPTURE
           PERFORM CHECK-IDENTITY-AGREEMENT
           PERFORM SELECT-EXIT-CODE.
      *
      * The chain was entered.
       CHECK-CHAIN-CALLED.
           IF WS-CALL-FAILED = 'Y'
               MOVE 'CHAIN-MODULE-CALLED' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
           END-IF.
      *
      * The chain returned '00'.
       CHECK-RETURN-CODE.
           MOVE CA-RETURN-CODE TO WS-RETURN-CODE-TEXT
           IF WS-RETURN-CODE-TEXT NOT = '00'
               MOVE 'RETURN-CODE-IS-00' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: CA-RETURN-CODE holds '
                       WS-RETURN-CODE-TEXT
           END-IF.
      *
      * No abend site was reached.
       CHECK-ABEND-ABSENT.
           IF HC-ABEND-PRESENT NOT = 'N'
                   OR HC-ABEND-COUNT NOT = ZERO
               MOVE 'NO-ABEND-CAPTURED' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: abend code ' HC-ABEND-CODE
                       ' recorded ' HC-ABEND-COUNT ' time(s)'
           END-IF.
      *
      * The policy insert was captured, an identity above zero was
      * assigned and the timestamp read back is not spaces.
       CHECK-POLICY-CAPTURE.
           IF HC-POL-PRESENT NOT = 'Y'
               MOVE 'POLICY-CAPTURE-PRESENT' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
           END-IF
           IF HC-IDENT-POLICYNUM NOT > ZERO
               MOVE 'POLICY-ASSIGNED-NUMBER-NON-ZERO'
                   TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
           END-IF
           IF HC-LCHG-LASTCHANGED = SPACES
               MOVE 'POLICY-ASSIGNED-TIMESTAMP-PRESENT'
                   TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
           END-IF.
      *
      * The product insert the request id routes to was captured, and
      * the other three product inserts were not.
       CHECK-PRODUCT-CAPTURES.
           EVALUATE CA-REQUEST-ID
             WHEN '01AMOT'
               MOVE 'M' TO WS-PRODUCT-WANTED
             WHEN '01ACOM'
               MOVE 'C' TO WS-PRODUCT-WANTED
             WHEN '01AEND'
               MOVE 'E' TO WS-PRODUCT-WANTED
             WHEN '01AHOU'
               MOVE 'H' TO WS-PRODUCT-WANTED
             WHEN OTHER
               MOVE '?' TO WS-PRODUCT-WANTED
           END-EVALUATE
           IF WS-PRODUCT-WANTED = '?'
               MOVE 'PRODUCT-CAPTURE-PRESENT' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: request id ' CA-REQUEST-ID
                       ' routes to no product table'
           ELSE
               PERFORM CHECK-WANTED-PRODUCT
           END-IF
           PERFORM CHECK-OTHER-PRODUCTS.
      *
       CHECK-WANTED-PRODUCT.
           MOVE 'N' TO WS-PRODUCT-FOUND
           EVALUATE WS-PRODUCT-WANTED
             WHEN 'M'
               MOVE HC-MOT-PRESENT TO WS-PRODUCT-FOUND
             WHEN 'C'
               MOVE HC-COM-PRESENT TO WS-PRODUCT-FOUND
             WHEN 'E'
               MOVE HC-END-PRESENT TO WS-PRODUCT-FOUND
             WHEN 'H'
               MOVE HC-HOU-PRESENT TO WS-PRODUCT-FOUND
           END-EVALUATE
           IF WS-PRODUCT-FOUND NOT = 'Y'
               MOVE 'PRODUCT-CAPTURE-PRESENT' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: no capture for the product table '
                       'request id ' CA-REQUEST-ID ' routes to'
           END-IF.
      *
       CHECK-OTHER-PRODUCTS.
           MOVE 'N' TO WS-EXTRA-PRODUCT
           IF WS-PRODUCT-WANTED NOT = 'M' AND HC-MOT-PRESENT = 'Y'
               MOVE 'Y' TO WS-EXTRA-PRODUCT
               DISPLAY 'DRIVER: motor insert captured for request id '
                       CA-REQUEST-ID
           END-IF
           IF WS-PRODUCT-WANTED NOT = 'C' AND HC-COM-PRESENT = 'Y'
               MOVE 'Y' TO WS-EXTRA-PRODUCT
               DISPLAY 'DRIVER: commercial insert captured for '
                       'request id ' CA-REQUEST-ID
           END-IF
           IF WS-PRODUCT-WANTED NOT = 'E' AND HC-END-PRESENT = 'Y'
               MOVE 'Y' TO WS-EXTRA-PRODUCT
               DISPLAY 'DRIVER: endowment insert captured for '
                       'request id ' CA-REQUEST-ID
           END-IF
           IF WS-PRODUCT-WANTED NOT = 'H' AND HC-HOU-PRESENT = 'Y'
               MOVE 'Y' TO WS-EXTRA-PRODUCT
               DISPLAY 'DRIVER: house insert captured for request id '
                       CA-REQUEST-ID
           END-IF
           IF WS-EXTRA-PRODUCT = 'Y'
               MOVE 'OTHER-PRODUCT-CAPTURES-ABSENT' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
           END-IF.
      *
      * The KSDSPOLY write was captured with a 64-character record, a
      * 21-character key length, and a key holding the fourth
      * character of the request id, the customer number and the
      * policy number of the returned COMMAREA.
       CHECK-VSAM-CAPTURE.
           IF HC-VSAM-PRESENT NOT = 'Y'
               MOVE 'VSAM-CAPTURE-PRESENT' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
           END-IF
           IF HC-VSAM-RECORD-LEN NOT = WS-VSAM-LEN-EXPECTED
               MOVE 'VSAM-RECORD-LENGTH-64' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: KSDSPOLY record length '
                       HC-VSAM-RECORD-LEN
           END-IF
           IF HC-VSAM-KEY-LEN NOT = WS-VSAM-KEYLEN-EXPECTED
               MOVE 'VSAM-KEY-LENGTH-21' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: KSDSPOLY key length '
                       HC-VSAM-KEY-LEN
           END-IF
           MOVE CA-REQUEST-ID(4:1) TO WS-EXP-REQUEST-ID
           MOVE CA-CUSTOMER-NUM TO WS-EXP-CUSTOMER-NUM
           MOVE CA-POLICY-NUM TO WS-EXP-POLICY-NUM
           IF HC-VSAM-KEY NOT = WS-EXPECTED-KEY
               MOVE 'VSAM-KEY-MATCHES-COMMAREA' TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: KSDSPOLY key [' HC-VSAM-KEY
                       '] COMMAREA key [' WS-EXPECTED-KEY ']'
           END-IF.
      *
      * The returned policy number and timestamp are the ones the
      * chain was given.
       CHECK-IDENTITY-AGREEMENT.
           IF CA-POLICY-NUM NOT = HC-IDENT-POLICYNUM
               MOVE 'POLICY-NUMBER-MATCHES-IDENTITY'
                   TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: CA-POLICY-NUM ' CA-POLICY-NUM
                       ' assigned identity ' HC-IDENT-POLICYNUM
           END-IF
           IF CA-LASTCHANGED NOT = HC-LCHG-LASTCHANGED
               MOVE 'LASTCHANGED-MATCHES-TIMESTAMP'
                   TO WS-CHECK-NAME
               PERFORM REPORT-FAILED-CHECK
               DISPLAY 'DRIVER: CA-LASTCHANGED [' CA-LASTCHANGED
                       '] assigned [' HC-LCHG-LASTCHANGED ']'
           END-IF.
      *
      * Reports the most specific condition observed: a file or
      * environment failure already recorded, then a chain that could
      * not be called, then an abend, then a return code other than
      * '00', then a failed capture check.
       SELECT-EXIT-CODE.
           EVALUATE TRUE
             WHEN WS-EXIT-CODE NOT = ZERO
               CONTINUE
             WHEN WS-CALL-FAILED = 'Y'
               MOVE 05 TO WS-EXIT-CODE
             WHEN HC-ABEND-PRESENT = 'Y'
               MOVE 02 TO WS-EXIT-CODE
             WHEN WS-RETURN-CODE-TEXT NOT = '00'
               MOVE 01 TO WS-EXIT-CODE
             WHEN WS-FAILURES > ZERO
               MOVE 03 TO WS-EXIT-CODE
             WHEN OTHER
               CONTINUE
           END-EVALUATE
           IF WS-FAILURES > ZERO
               DISPLAY 'DRIVER: ' WS-FAILURES
                       ' named check(s) failed'
           END-IF.
      *
      * Names one failed check in the log and counts it.
       REPORT-FAILED-CHECK.
           IF WS-FAILURES < 99
               ADD 1 TO WS-FAILURES
           END-IF
           DISPLAY 'DRIVER: check failed '
                   FUNCTION TRIM(WS-CHECK-NAME)
           MOVE SPACES TO WS-CHECK-NAME.
      *----------------------------------------------------------------*

