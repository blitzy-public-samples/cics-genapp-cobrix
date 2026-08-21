      ******************************************************************
      *                                                                *
      *                     SQL-INSERT-POLICY                          *
      *                                                                *
      *   Harness stand-in for the INSERT INTO POLICY statement of     *
      *   the translated LGAPDB01                                      *
      *                                                                *
      ******************************************************************
      *
      * Emulates the SQL block at [base/src/lgapdb01.cbl:268-288] in
      * paragraph INSERT-POLICY. The translated LGAPDB01 calls this
      * module in place of that block and passes the seven host
      * variables of the block BY REFERENCE in source order, as
      * recorded by the dml entry insert_policy of
      * modernization/harness/statement_map.yml.
      *
      * Two of the nine POLICY columns take no host variable: the
      * source supplies POLICYNUMBER with DEFAULT at
      * [base/src/lgapdb01.cbl:279] and LASTCHANGED with CURRENT
      * TIMESTAMP at [base/src/lgapdb01.cbl:284]. The arity of the
      * block is seven. This module supplies both of those values from
      * shared harness state.
      *
      * Parameters, each with the POLICY column it is paired with and
      * the capture item that witnesses it:
      *   1  DB2-CUSTOMERNUM-INT  CUSTOMERNUMBER    HC-POL-CUSTOMERNUM
      *   2  CA-ISSUE-DATE        ISSUEDATE         HC-POL-ISSUE-DATE
      *   3  CA-EXPIRY-DATE       EXPIRYDATE        HC-POL-EXPIRY-DATE
      *   4  DB2-POLICYTYPE       POLICYTYPE        HC-POL-POLICYTYPE
      *   5  DB2-BROKERID-INT     BROKERID          HC-POL-BROKERID
      *   6  CA-BROKERSREF        BROKERSREFERENCE  HC-POL-BROKERSREF
      *   7  DB2-PAYMENT-INT      PAYMENT           HC-POL-PAYMENT
      * Each value is recorded as received, without trimming or
      * reformatting. No value is derived from any parameter.
      *
      * Capture control, following the contract stated by
      * modernization/harness/copybooks/hcapture.cpy: HC-POL-PRESENT
      * becomes 'Y', HC-POL-COUNT counts the executions of the block,
      * HC-EVENT-SEQ is advanced and its new value is stamped into
      * HC-POL-SEQ, and HC-ORDER-LAST-STMT receives this statement's
      * key insert_policy. HC-ORDER-VIOLATION and
      * HC-ORDER-VIOLATION-STMT are not written here. insert_policy is
      * the predecessor of the one ordering constraint declared by the
      * execution_order block of
      * modernization/harness/statement_map.yml and has no
      * prerequisite ordinal of its own.
      *
      * SQLCODE of the shared SQLCA reports HC-INJECT-POL-SQLCODE on
      * every call. The translated LGAPDB01 evaluates it at
      * [base/src/lgapdb01.cbl:290-305]: zero takes the When 0 branch
      * at [base/src/lgapdb01.cbl:292] and moves '00' to
      * CA-RETURN-CODE, -530 takes the When -530 branch at
      * [base/src/lgapdb01.cbl:295-298] and moves '70' before
      * returning, and any other value takes the When Other branch at
      * [base/src/lgapdb01.cbl:300-303] and moves '90' before
      * returning. The seven host values, the capture control items and
      * both seeds are recorded before the code is reported, on every
      * path: the block executed whatever it then reported.
      *
      * Chain witness: HC-CHAIN-DB2-PRESENT becomes 'Y' and
      * HC-CHAIN-DB2-CALEN receives EIBCALEN as observed inside the
      * translated LGAPDB01. This block is the first emulated service
      * that program calls after the routing at
      * [base/src/lgapdb01.cbl:218-223], and the translated LGAPOL01
      * links that program with LENGTH(32500) at
      * [base/src/lgapol01.cbl:121-124].
      *
      * HC-SEED-POLICYNUM and HC-SEED-LASTCHANGED are resolved in this
      * order and are left holding the resolved pair:
      *   1  the value already present in the seed item, when
      *      HC-SEED-POLICYNUM is above zero or HC-SEED-LASTCHANGED is
      *      not blank and names a real timestamp;
      *   2  environment variable HARNESS_POLICY_NUMBER, taken when it
      *      holds one run of 1 to 9 digits with no other character
      *      and no embedded blank, and parses above zero, and
      *      HARNESS_LASTCHANGED, taken when it holds exactly 26
      *      non-blank characters naming a real Gregorian date and time
      *      in the form YYYY-MM-DD-HH.MM.SS.NNNNNN;
      *   3  the documented defaults 1000001 and
      *      2026-08-19-12.00.00.000000.
      * Every timestamp this module leaves in HC-SEED-LASTCHANGED has
      * passed that calendar validation, the seeded value included: a
      * timestamp naming an impossible date or time is named in the log
      * and replaced by the documented default, so no impossible
      * timestamp reaches the read-back of
      * [base/src/lgapdb01.cbl:316-321] or the captures of the case.
      * No clock is read. modernization/harness/stubs/
      * sql_set_identity.cbl returns the seeded identity for
      * [base/src/lgapdb01.cbl:308-310] and
      * modernization/harness/stubs/sql_select_lastchanged.cbl returns
      * the seeded timestamp for [base/src/lgapdb01.cbl:316-321]. The
      * pair left here is the pair that reaches CA-POLICY-NUM at
      * [base/src/lgapdb01.cbl:311] and CA-LASTCHANGED at
      * [base/src/lgapdb01.cbl:318]. Both seeds are resolved on every
      * call, under no condition. INSERT-COMMERCIAL consumes
      * CA-LASTCHANGED as its RequestDate at
      * [base/src/lgapdb01.cbl:525].
      *
      * No item of the caller's COMMAREA is addressed here, and no
      * capture item outside HC-SQL-POLICY, HC-EVENT-CONTROL,
      * HC-SEED, HC-CHAIN-DB2-PRESENT, HC-CHAIN-DB2-CALEN and
      * HC-ORDER-LAST-STMT is written. HC-INJECT-POL-SQLCODE is read
      * here and never written, and so is EIBCALEN of
      * modernization/harness/copybooks/dfheiblk.cpy.
      *
      * Rationale for the deterministic seeding of the identity and
      * timestamp, for the reported SQLCODE, for the chain witness and
      * for the arity of seven belongs to
      * modernization/docs/decision-log.md (planned deliverable; not
      * present at this milestone), rows: deterministic failure
      * injection through shared harness state; chain traversal
      * witnessed through the emulated services.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SQL-INSERT-POLICY.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      * Shared capture state. This module writes the POLICY group, the
      * shared event sequence, the seed pair, the LGAPDB01 chain
      * witness and the last-statement name, and reads the injected
      * SQLCODE.
       COPY HCAPTURE.
      *
      * Shared SQL communications area read by the translated LGAPDB01.
       COPY HSQLCA.
      *
      * Shared EXEC Interface Block surrogate. EIBCALEN is read as the
      * COMMAREA length in force inside the translated LGAPDB01.
       COPY DFHEIBLK.
      *
      *----------------------------------------------------------------*
      * Local items used to resolve the seeded identity and timestamp  *
      *----------------------------------------------------------------*
      * Text received from the environment. Positions 27 to 32 are
      * examined to detect a value longer than the 26-character
      * timestamp.
       01  WS-ENV-TEXT             PIC X(32).
      *
      * Character under inspection and its position within WS-ENV-TEXT.
       01  WS-SCAN-CHAR            PIC X.
       01  WS-SCAN-IX              PIC S9(4) COMP.
      *
      * Outcome of the character scan of WS-ENV-TEXT. Each item holds
      * 'Y' once the scan has seen that class of character and 'N'
      * otherwise. WS-HAS-EMBEDDED-BLANK reports a blank standing
      * before a later non-blank, which makes the text two values
      * rather than one.
       01  WS-SCAN-FLAGS.
           03 WS-HAS-DIGIT         PIC X.
           03 WS-HAS-NON-DIGIT     PIC X.
           03 WS-HAS-BLANK         PIC X.
           03 WS-HAS-EMBEDDED-BLANK
                                   PIC X.
      *
      * Number of digits the scan counted in WS-ENV-TEXT.
       01  WS-DIGIT-COUNT          PIC S9(4) COMP.
      *
      * Policy number parsed from WS-ENV-TEXT. Zero when the text held
      * no acceptable value.
       01  WS-PARSED-POLICYNUM     PIC S9(9) COMP.
      *
      * Documented fallbacks. Shapes follow HC-SEED-POLICYNUM and
      * HC-SEED-LASTCHANGED.
       01  WS-DEFAULT-POLICYNUM    PIC S9(9) COMP VALUE +1000001.
       01  WS-DEFAULT-LASTCHANGED  PIC X(26)
                                   VALUE '2026-08-19-12.00.00.000000'.
      *
      *----------------------------------------------------------------*
      * Local items used to validate a candidate timestamp             *
      *----------------------------------------------------------------*
      * The candidate, laid out as the Db2 external form
      * YYYY-MM-DD-HH.MM.SS.NNNNNN. The character view carries the
      * class tests; the redefinition below reads the same characters
      * as the numbers they spell, and is addressed only after every
      * one of them has been found numeric.
       01  WS-STAMP.
           03 WS-STAMP-YEAR       PIC X(4).
           03 WS-STAMP-SEP1       PIC X.
           03 WS-STAMP-MONTH      PIC X(2).
           03 WS-STAMP-SEP2       PIC X.
           03 WS-STAMP-DAY        PIC X(2).
           03 WS-STAMP-SEP3       PIC X.
           03 WS-STAMP-HOUR       PIC X(2).
           03 WS-STAMP-SEP4       PIC X.
           03 WS-STAMP-MINUTE     PIC X(2).
           03 WS-STAMP-SEP5       PIC X.
           03 WS-STAMP-SECOND     PIC X(2).
           03 WS-STAMP-SEP6       PIC X.
           03 WS-STAMP-MICROS     PIC X(6).
      *
       01  WS-STAMP-NUM REDEFINES WS-STAMP.
           03 WS-NUM-YEAR         PIC 9(4).
           03 FILLER              PIC X.
           03 WS-NUM-MONTH        PIC 9(2).
           03 FILLER              PIC X.
           03 WS-NUM-DAY          PIC 9(2).
           03 FILLER              PIC X.
           03 WS-NUM-HOUR         PIC 9(2).
           03 FILLER              PIC X.
           03 WS-NUM-MINUTE       PIC 9(2).
           03 FILLER              PIC X.
           03 WS-NUM-SECOND       PIC 9(2).
           03 FILLER              PIC X.
           03 WS-NUM-MICROS       PIC 9(6).
      *
      * Outcome of the validation, the element that failed it, the
      * highest day the month and year allow, and 'Y' while that year
      * is a leap year under the Gregorian rule.
       01  WS-STAMP-OK             PIC X.
       01  WS-STAMP-REASON         PIC X(48).
       01  WS-STAMP-MAX-DAY        PIC 9(2).
       01  WS-STAMP-LEAP           PIC X.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
      * The seven host variables of [base/src/lgapdb01.cbl:268-288], in
      * the source order of the block. Shapes follow the declarations
      * cited against each item.
       LINKAGE SECTION.
      *
      * Slot 1, column CUSTOMERNUMBER. DB2-CUSTOMERNUM-INT
      * [base/src/lgapdb01.cbl:90], loaded from CA-CUSTOMER-NUM by the
      * MOVE at [base/src/lgapdb01.cbl:176].
       01  DB2-CUSTOMERNUM-INT     PIC S9(9) COMP.
      *
      * Slot 2, column ISSUEDATE. CA-ISSUE-DATE
      * [base/src/lgcmarea.cpy:38].
       01  CA-ISSUE-DATE           PIC X(10).
      *
      * Slot 3, column EXPIRYDATE. CA-EXPIRY-DATE
      * [base/src/lgcmarea.cpy:39].
       01  CA-EXPIRY-DATE          PIC X(10).
      *
      * Slot 4, column POLICYTYPE. DB2-POLICYTYPE
      * [base/src/lgpolicy.cpy:43], set to 'E', 'H', 'M' or 'C' by the
      * request routing at [base/src/lgapdb01.cbl:184-207].
       01  DB2-POLICYTYPE          PIC X.
      *
      * Slot 5, column BROKERID. DB2-BROKERID-INT
      * [base/src/lgapdb01.cbl:91], loaded from CA-BROKERID by the MOVE
      * at [base/src/lgapdb01.cbl:264].
       01  DB2-BROKERID-INT        PIC S9(9) COMP.
      *
      * Slot 6, column BROKERSREFERENCE. CA-BROKERSREF
      * [base/src/lgcmarea.cpy:42].
       01  CA-BROKERSREF           PIC X(10).
      *
      * Slot 7, column PAYMENT. DB2-PAYMENT-INT
      * [base/src/lgapdb01.cbl:92], loaded from CA-PAYMENT PIC 9(6)
      * [base/src/lgcmarea.cpy:43] by the MOVE at
      * [base/src/lgapdb01.cbl:265].
       01  DB2-PAYMENT-INT         PIC S9(9) COMP.
      *
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION USING DB2-CUSTOMERNUM-INT
                                CA-ISSUE-DATE
                                CA-EXPIRY-DATE
                                DB2-POLICYTYPE
                                DB2-BROKERID-INT
                                CA-BROKERSREF
                                DB2-PAYMENT-INT.
      *
      *----------------------------------------------------------------*
      * Records the block, stamps its capture control items, records   *
      * the chain witness, resolves both seeds and reports the         *
      * SQLCODE this run selected.                                     *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM CAPTURE-POLICY-VALUES
           PERFORM STAMP-CAPTURE-CONTROL
           PERFORM RECORD-CHAIN-WITNESS
           PERFORM RESOLVE-SEED-POLICYNUM
           PERFORM RESOLVE-SEED-LASTCHANGED
           MOVE HC-INJECT-POL-SQLCODE TO SQLCODE
           GOBACK.
      *
      *----------------------------------------------------------------*
      * Moves the seven host values into their capture slots.          *
      *----------------------------------------------------------------*
       CAPTURE-POLICY-VALUES.
           MOVE DB2-CUSTOMERNUM-INT TO HC-POL-CUSTOMERNUM
           MOVE CA-ISSUE-DATE       TO HC-POL-ISSUE-DATE
           MOVE CA-EXPIRY-DATE      TO HC-POL-EXPIRY-DATE
           MOVE DB2-POLICYTYPE      TO HC-POL-POLICYTYPE
           MOVE DB2-BROKERID-INT    TO HC-POL-BROKERID
           MOVE CA-BROKERSREF       TO HC-POL-BROKERSREF
           MOVE DB2-PAYMENT-INT     TO HC-POL-PAYMENT.
      *
      *----------------------------------------------------------------*
      * Marks the block captured, counts the execution, stamps the     *
      * ordinal from the shared event sequence and names the           *
      * statement. The order-guard items are not written here.         *
      *----------------------------------------------------------------*
       STAMP-CAPTURE-CONTROL.
           MOVE 'Y' TO HC-POL-PRESENT
           ADD 1 TO HC-POL-COUNT END-ADD
           ADD 1 TO HC-EVENT-SEQ END-ADD
           MOVE HC-EVENT-SEQ TO HC-POL-SEQ
           MOVE 'insert_policy' TO HC-ORDER-LAST-STMT.
      *
      *----------------------------------------------------------------*
      * Reports that the translated LGAPDB01 was entered and records   *
      * the COMMAREA length in force there, set from LENGTH(32500) at  *
      * [base/src/lgapol01.cbl:121-124].                               *
      *----------------------------------------------------------------*
       RECORD-CHAIN-WITNESS.
           SET HC-CHAIN-DB2-ENTERED TO TRUE
           MOVE EIBCALEN TO HC-CHAIN-DB2-CALEN.
      *
      *----------------------------------------------------------------*
      * Leaves HC-SEED-POLICYNUM holding the identity for this case:   *
      * the value already seeded, else HARNESS_POLICY_NUMBER, else     *
      * the default.                                                   *
      *----------------------------------------------------------------*
       RESOLVE-SEED-POLICYNUM.
           IF HC-SEED-POLICYNUM IS NOT GREATER THAN ZERO
               MOVE SPACES TO WS-ENV-TEXT
               ACCEPT WS-ENV-TEXT FROM ENVIRONMENT
                      'HARNESS_POLICY_NUMBER'
               END-ACCEPT
               PERFORM SCAN-ENV-TEXT
               MOVE ZERO TO WS-PARSED-POLICYNUM
               IF WS-HAS-DIGIT = 'Y' AND WS-HAS-NON-DIGIT = 'N'
                   AND WS-HAS-EMBEDDED-BLANK = 'N'
                   AND WS-DIGIT-COUNT IS GREATER THAN ZERO
                   AND WS-DIGIT-COUNT IS NOT GREATER THAN 9
                   MOVE FUNCTION NUMVAL(WS-ENV-TEXT)
                     TO WS-PARSED-POLICYNUM
               END-IF
               IF WS-PARSED-POLICYNUM IS GREATER THAN ZERO
                   MOVE WS-PARSED-POLICYNUM TO HC-SEED-POLICYNUM
               ELSE
                   MOVE WS-DEFAULT-POLICYNUM TO HC-SEED-POLICYNUM
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Leaves HC-SEED-LASTCHANGED holding the 26-character timestamp  *
      * for this case: the value already seeded when it names a real   *
      * date and time, else HARNESS_LASTCHANGED when it holds exactly  *
      * 26 non-blank characters naming one, else the default. A value  *
      * that does not is named in the log and replaced.                *
      *----------------------------------------------------------------*
       RESOLVE-SEED-LASTCHANGED.
           IF HC-SEED-LASTCHANGED = SPACES
               PERFORM RESOLVE-LASTCHANGED-FROM-ENV
           ELSE
               MOVE HC-SEED-LASTCHANGED TO WS-STAMP
               PERFORM VALIDATE-TIMESTAMP-SEED
               IF WS-STAMP-OK NOT = 'Y'
                   DISPLAY 'SQL-INSERT-POLICY: the seeded timestamp '
                           'was rejected: '
                           FUNCTION TRIM(WS-STAMP-REASON)
                   END-DISPLAY
                   PERFORM APPLY-DEFAULT-LASTCHANGED
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Takes the timestamp from HARNESS_LASTCHANGED. An unset item    *
      * and a value that is not 26 non-blank characters naming a real  *
      * date and time both leave the documented default, and each      *
      * outcome is named in the log.                                   *
      *----------------------------------------------------------------*
       RESOLVE-LASTCHANGED-FROM-ENV.
           MOVE SPACES TO WS-ENV-TEXT
           ACCEPT WS-ENV-TEXT FROM ENVIRONMENT 'HARNESS_LASTCHANGED'
           END-ACCEPT
           IF WS-ENV-TEXT = SPACES
               DISPLAY 'SQL-INSERT-POLICY: HARNESS_LASTCHANGED is not '
                       'set'
               END-DISPLAY
               PERFORM APPLY-DEFAULT-LASTCHANGED
           ELSE
               MOVE 'N' TO WS-HAS-BLANK
               PERFORM VARYING WS-SCAN-IX FROM 1 BY 1
                       UNTIL WS-SCAN-IX IS GREATER THAN 26
                   IF WS-ENV-TEXT(WS-SCAN-IX:1) = SPACE
                       MOVE 'Y' TO WS-HAS-BLANK
                   END-IF
               END-PERFORM
               IF WS-HAS-BLANK = 'N' AND WS-ENV-TEXT(27:6) = SPACES
                   MOVE WS-ENV-TEXT(1:26) TO WS-STAMP
                   PERFORM VALIDATE-TIMESTAMP-SEED
               ELSE
                   MOVE 'N' TO WS-STAMP-OK
                   MOVE 'not 26 characters free of blanks'
                       TO WS-STAMP-REASON
               END-IF
               IF WS-STAMP-OK = 'Y'
                   MOVE WS-STAMP TO HC-SEED-LASTCHANGED
               ELSE
                   DISPLAY 'SQL-INSERT-POLICY: HARNESS_LASTCHANGED '
                           'rejected: '
                           FUNCTION TRIM(WS-STAMP-REASON)
                   END-DISPLAY
                   PERFORM APPLY-DEFAULT-LASTCHANGED
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Leaves the documented default in the shared seed item and      *
      * names it in the log.                                           *
      *----------------------------------------------------------------*
       APPLY-DEFAULT-LASTCHANGED.
           MOVE WS-DEFAULT-LASTCHANGED TO HC-SEED-LASTCHANGED
           DISPLAY 'SQL-INSERT-POLICY: the seed of this case is the '
                   'documented default ' WS-DEFAULT-LASTCHANGED
           END-DISPLAY.
      *
      *----------------------------------------------------------------*
      * Judges the 26 characters of WS-STAMP as a Db2 external         *
      * timestamp: the six separators in their fixed positions, every  *
      * other position a digit, a year of 0001 through 9999, a month   *
      * of 01 through 12, a day the month and year allow under the     *
      * Gregorian leap rule, an hour of 00 through 23, a minute and a  *
      * second of 00 through 59, and six fractional digits.            *
      *----------------------------------------------------------------*
       VALIDATE-TIMESTAMP-SEED.
           MOVE 'Y' TO WS-STAMP-OK
           MOVE SPACES TO WS-STAMP-REASON
           PERFORM CHECK-TIMESTAMP-LAYOUT
           IF WS-STAMP-OK = 'Y'
               PERFORM CHECK-TIMESTAMP-RANGES
           END-IF
           IF WS-STAMP-OK = 'Y'
               PERFORM CHECK-TIMESTAMP-DAY
           END-IF.
      *
      *----------------------------------------------------------------*
      * Confirms the separators and that every remaining position      *
      * holds a digit. The numeric redefinition of WS-STAMP is read    *
      * only after this paragraph has passed.                          *
      *----------------------------------------------------------------*
       CHECK-TIMESTAMP-LAYOUT.
           EVALUATE TRUE
             WHEN WS-STAMP-SEP1 NOT = '-'
               MOVE 'character 5 is not a hyphen' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-SEP2 NOT = '-'
               MOVE 'character 8 is not a hyphen' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-SEP3 NOT = '-'
               MOVE 'character 11 is not a hyphen' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-SEP4 NOT = '.'
               MOVE 'character 14 is not a point' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-SEP5 NOT = '.'
               MOVE 'character 17 is not a point' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-SEP6 NOT = '.'
               MOVE 'character 20 is not a point' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-YEAR NOT NUMERIC
               MOVE 'the year is not four digits' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-MONTH NOT NUMERIC
               MOVE 'the month is not two digits' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-DAY NOT NUMERIC
               MOVE 'the day is not two digits' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-HOUR NOT NUMERIC
               MOVE 'the hour is not two digits' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-MINUTE NOT NUMERIC
               MOVE 'the minute is not two digits'
                   TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-SECOND NOT NUMERIC
               MOVE 'the second is not two digits'
                   TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-STAMP-MICROS NOT NUMERIC
               MOVE 'the fraction is not six digits'
                   TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
           END-EVALUATE.
      *
      *----------------------------------------------------------------*
      * Confirms the range of every element except the day, which the  *
      * month and the year decide.                                    *
      *----------------------------------------------------------------*
       CHECK-TIMESTAMP-RANGES.
           EVALUATE TRUE
             WHEN WS-NUM-YEAR < 1
               MOVE 'the year is 0000' TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-NUM-MONTH < 1 OR WS-NUM-MONTH > 12
               MOVE 'the month is outside 01 through 12'
                   TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-NUM-HOUR > 23
               MOVE 'the hour is outside 00 through 23'
                   TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-NUM-MINUTE > 59
               MOVE 'the minute is outside 00 through 59'
                   TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
             WHEN WS-NUM-SECOND > 59
               MOVE 'the second is outside 00 through 59'
                   TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
           END-EVALUATE.
      *
      *----------------------------------------------------------------*
      * Confirms the day against the length of the month, taking       *
      * February from the Gregorian leap rule: a year divisible by     *
      * four is a leap year unless it is divisible by 100 without      *
      * being divisible by 400.                                       *
      *----------------------------------------------------------------*
       CHECK-TIMESTAMP-DAY.
           MOVE 'N' TO WS-STAMP-LEAP
           IF FUNCTION MOD(WS-NUM-YEAR 4) = ZERO
               IF FUNCTION MOD(WS-NUM-YEAR 100) NOT = ZERO
                   MOVE 'Y' TO WS-STAMP-LEAP
               ELSE
                   IF FUNCTION MOD(WS-NUM-YEAR 400) = ZERO
                       MOVE 'Y' TO WS-STAMP-LEAP
                   END-IF
               END-IF
           END-IF
           EVALUATE WS-NUM-MONTH
             WHEN 2
               IF WS-STAMP-LEAP = 'Y'
                   MOVE 29 TO WS-STAMP-MAX-DAY
               ELSE
                   MOVE 28 TO WS-STAMP-MAX-DAY
               END-IF
             WHEN 4
             WHEN 6
             WHEN 9
             WHEN 11
               MOVE 30 TO WS-STAMP-MAX-DAY
             WHEN OTHER
               MOVE 31 TO WS-STAMP-MAX-DAY
           END-EVALUATE
           IF WS-NUM-DAY < 1 OR WS-NUM-DAY > WS-STAMP-MAX-DAY
               MOVE 'the day is outside the length of the month'
                   TO WS-STAMP-REASON
               MOVE 'N' TO WS-STAMP-OK
           END-IF.
      *
      *----------------------------------------------------------------*
      * Classifies every character of WS-ENV-TEXT as a digit, a blank  *
      * or neither, reports each class it found in WS-SCAN-FLAGS,      *
      * counts the digits in WS-DIGIT-COUNT and reports a blank        *
      * standing before a later non-blank as an embedded blank.        *
      *----------------------------------------------------------------*
       SCAN-ENV-TEXT.
           MOVE 'N' TO WS-HAS-DIGIT
           MOVE 'N' TO WS-HAS-NON-DIGIT
           MOVE 'N' TO WS-HAS-BLANK
           MOVE 'N' TO WS-HAS-EMBEDDED-BLANK
           MOVE ZERO TO WS-DIGIT-COUNT
           PERFORM VARYING WS-SCAN-IX FROM 1 BY 1
                   UNTIL WS-SCAN-IX IS GREATER THAN 32
               MOVE WS-ENV-TEXT(WS-SCAN-IX:1) TO WS-SCAN-CHAR
               IF WS-SCAN-CHAR = SPACE
                   MOVE 'Y' TO WS-HAS-BLANK
               ELSE
                   IF WS-HAS-BLANK = 'Y'
                       MOVE 'Y' TO WS-HAS-EMBEDDED-BLANK
                   END-IF
                   IF WS-SCAN-CHAR IS NUMERIC
                       MOVE 'Y' TO WS-HAS-DIGIT
                       ADD 1 TO WS-DIGIT-COUNT
                       END-ADD
                   ELSE
                       MOVE 'Y' TO WS-HAS-NON-DIGIT
                   END-IF
               END-IF
           END-PERFORM.
