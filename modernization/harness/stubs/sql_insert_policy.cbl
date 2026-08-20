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
      * SQLCODE of the shared SQLCA is set to zero on every call.
      * The translated LGAPDB01 evaluates it at
      * [base/src/lgapdb01.cbl:290-305], where the When 0 branch at
      * [base/src/lgapdb01.cbl:292] moves '00' to CA-RETURN-CODE.
      *
      * HC-SEED-POLICYNUM and HC-SEED-LASTCHANGED are resolved in this
      * order and are left holding the resolved pair:
      *   1  the value already present in the seed item, when
      *      HC-SEED-POLICYNUM is above zero or HC-SEED-LASTCHANGED is
      *      not blank;
      *   2  environment variable HARNESS_POLICY_NUMBER, taken when it
      *      holds digits and blanks only and parses above zero, and
      *      HARNESS_LASTCHANGED, taken when it holds exactly 26
      *      non-blank characters;
      *   3  the documented defaults 1000001 and
      *      2026-08-19-12.00.00.000000.
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
      * HC-SEED and HC-ORDER-LAST-STMT is written.
      *
      * Rationale for the deterministic seeding of the identity and
      * timestamp, for the always-zero SQLCODE and for the arity of
      * seven is recorded in modernization/docs/decision-log.md.
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
      * shared event sequence, the seed pair and the last-statement
      * name.
       COPY HCAPTURE.
      *
      * Shared SQL communications area read by the translated LGAPDB01.
       COPY HSQLCA.
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
      * otherwise.
       01  WS-SCAN-FLAGS.
           03 WS-HAS-DIGIT         PIC X.
           03 WS-HAS-NON-DIGIT     PIC X.
           03 WS-HAS-BLANK         PIC X.
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
      * Records the block, stamps its capture control items, resolves  *
      * both seeds and reports success to the caller.                  *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM CAPTURE-POLICY-VALUES
           PERFORM STAMP-CAPTURE-CONTROL
           PERFORM RESOLVE-SEED-POLICYNUM
           PERFORM RESOLVE-SEED-LASTCHANGED
           MOVE ZERO TO SQLCODE
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
           ADD 1 TO HC-POL-COUNT
           ADD 1 TO HC-EVENT-SEQ
           MOVE HC-EVENT-SEQ TO HC-POL-SEQ
           MOVE 'insert_policy' TO HC-ORDER-LAST-STMT.
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
               PERFORM SCAN-ENV-TEXT
               MOVE ZERO TO WS-PARSED-POLICYNUM
               IF WS-HAS-DIGIT = 'Y' AND WS-HAS-NON-DIGIT = 'N'
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
      * for this case: the value already seeded, else                  *
      * HARNESS_LASTCHANGED when it is exactly 26 non-blank            *
      * characters, else the default. No calendar check is applied.    *
      *----------------------------------------------------------------*
       RESOLVE-SEED-LASTCHANGED.
           IF HC-SEED-LASTCHANGED = SPACES
               MOVE SPACES TO WS-ENV-TEXT
               ACCEPT WS-ENV-TEXT FROM ENVIRONMENT
                      'HARNESS_LASTCHANGED'
               MOVE 'N' TO WS-HAS-BLANK
               PERFORM VARYING WS-SCAN-IX FROM 1 BY 1
                       UNTIL WS-SCAN-IX IS GREATER THAN 26
                   IF WS-ENV-TEXT(WS-SCAN-IX:1) = SPACE
                       MOVE 'Y' TO WS-HAS-BLANK
                   END-IF
               END-PERFORM
               IF WS-HAS-BLANK = 'N' AND WS-ENV-TEXT(27:6) = SPACES
                   MOVE WS-ENV-TEXT(1:26) TO HC-SEED-LASTCHANGED
               ELSE
                   MOVE WS-DEFAULT-LASTCHANGED TO HC-SEED-LASTCHANGED
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Classifies every character of WS-ENV-TEXT as a digit, a blank  *
      * or neither, and reports each class it found in WS-SCAN-FLAGS.  *
      *----------------------------------------------------------------*
       SCAN-ENV-TEXT.
           MOVE 'N' TO WS-HAS-DIGIT
           MOVE 'N' TO WS-HAS-NON-DIGIT
           MOVE 'N' TO WS-HAS-BLANK
           PERFORM VARYING WS-SCAN-IX FROM 1 BY 1
                   UNTIL WS-SCAN-IX IS GREATER THAN 32
               MOVE WS-ENV-TEXT(WS-SCAN-IX:1) TO WS-SCAN-CHAR
               IF WS-SCAN-CHAR = SPACE
                   MOVE 'Y' TO WS-HAS-BLANK
               ELSE
                   IF WS-SCAN-CHAR IS NUMERIC
                       MOVE 'Y' TO WS-HAS-DIGIT
                   ELSE
                       MOVE 'Y' TO WS-HAS-NON-DIGIT
                   END-IF
               END-IF
           END-PERFORM.
