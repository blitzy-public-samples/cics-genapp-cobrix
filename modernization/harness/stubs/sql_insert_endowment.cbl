      ******************************************************************
      *                                                                *
      *                      SQL-INSERT-ENDOWMENT                      *
      *                                                                *
      *   Harness stand-in for both INSERT INTO ENDOWMENT              *
      *   statements of the translated LGAPDB01                        *
      *                                                                *
      ******************************************************************
      *
      * Emulates both SQL blocks of paragraph INSERT-ENDOW
      * [base/src/lgapdb01.cbl:327], the paragraph performed for
      * request id '01AEND' at [base/src/lgapdb01.cbl:225-226]:
      *
      *   [base/src/lgapdb01.cbl:346-366] inserts nine columns and
      *   supplies PADDINGDATA from :WS-VARY-FIELD.
      *   [base/src/lgapdb01.cbl:368-386] inserts the same first
      *   eight columns and omits PADDINGDATA.
      *
      * The guard IF WS-VARY-LEN IS GREATER THAN ZERO
      * [base/src/lgapdb01.cbl:342] selects between the two blocks,
      * over the length that the SUBTRACT at
      * [base/src/lgapdb01.cbl:339-340] computes from EIBCALEN and
      * WS-REQUIRED-CA-LEN. The translated LGAPDB01 calls this one
      * module from both arms and passes the nine-item superset BY
      * REFERENCE, as the dml entries insert_endowment_varchar and
      * insert_endowment_novarchar of
      * modernization/harness/statement_map.yml record. Both entries
      * give the call arity 9, and checks.using_counts of that file
      * records insert_endowment 9.
      *
      * Parameters, with the caller host each one receives, the Db2
      * column that host supplies and the capture item that
      * witnesses it:
      *   1  DB2-POLICYNUM-INT     POLICYNUMBER  HC-END-POLICYNUM
      *   2  CA-E-WITH-PROFITS     WITHPROFITS   HC-END-WITH-PROFITS
      *   3  CA-E-EQUITIES         EQUITIES      HC-END-EQUITIES
      *   4  CA-E-MANAGED-FUND     MANAGEDFUND   HC-END-MANAGED-FUND
      *   5  CA-E-FUND-NAME        FUNDNAME      HC-END-FUND-NAME
      *   6  DB2-E-TERM-SINT       TERM          HC-END-TERM
      *   7  DB2-E-SUMASSURED-INT  SUMASSURED    HC-END-SUMASSURED
      *   8  CA-E-LIFE-ASSURED     LIFEASSURED   HC-END-LIFE-ASSURED
      *   9  WS-VARY-FIELD         PADDINGDATA   HC-END-VARY-FIELD
      * Every value is moved verbatim: no trim, no re-format and no
      * normalisation. The parameters are read here and never
      * written here.
      *
      * The ninth parameter is the varchar host structure declared at
      * [base/src/lgapdb01.cbl:70-72]. Its two level-49 parts are the
      * length WS-VARY-LEN and the 3900-character body WS-VARY-CHAR,
      * and the passed length alone decides what is recorded:
      *   1 through 3900  the length reaches HC-END-VARY-LEN and
      *                   exactly that many leading characters reach
      *                   HC-END-VARY-CHAR.
      *   zero or below   the state that selects the
      *                   [base/src/lgapdb01.cbl:368-386] block. Only
      *                   the length reaches HC-END-VARY-LEN; the
      *                   character body is not read.
      *   above 3900      only the length reaches HC-END-VARY-LEN,
      *                   the character body is not read, and the run
      *                   log receives a report.
      * The captured length records which of the two blocks ran. No
      * length is recomputed here and no item of the source program
      * is addressed here.
      *
      * Capture control, following the contract stated by
      * modernization/harness/copybooks/hcapture.cpy: HC-END-PRESENT
      * becomes 'Y', HC-END-COUNT counts the executions, HC-EVENT-SEQ
      * is advanced and its new value is stamped into HC-END-SEQ, and
      * HC-ORDER-LAST-STMT receives this statement's key
      * insert_endowment.
      *
      * Order guard. The predecessor of both blocks is the INSERT INTO
      * POLICY block at [base/src/lgapdb01.cbl:268-288]: the source
      * performs INSERT-POLICY at [base/src/lgapdb01.cbl:219] ahead of
      * the product routing that reaches INSERT-ENDOW at
      * [base/src/lgapdb01.cbl:225-226], and the identity that
      * paragraph recovers is slot 1 here. HC-POL-SEQ carries that
      * predecessor. This module reads it after stamping its own
      * ordinal: a HC-POL-SEQ still at zero reports the predecessor
      * unrun in HC-ORDER-VIOLATION and HC-ORDER-VIOLATION-STMT, and a
      * non-zero HC-POL-SEQ leaves both items as
      * modernization/harness/driver.cbl set them. Both blocks are
      * tested alike: the guard reads the same ordinal whichever arm
      * of [base/src/lgapdb01.cbl:342] called this module. The
      * execution_order block of
      * modernization/harness/statement_map.yml declares one
      * constraint, policy_before_commercial, and neither endowment
      * block is a member of it; the constraint tested here is the one
      * the source routing states.
      *
      * SQLCODE of the shared SQLCA reports HC-INJECT-SUB-SQLCODE on
      * every call. The translated LGAPDB01 tests it at
      * [base/src/lgapdb01.cbl:389]; zero keeps the run clear of the
      * '90' return code at [base/src/lgapdb01.cbl:390] and of the
      * ABEND ABCODE('LGSQ') at [base/src/lgapdb01.cbl:393], and any
      * other value takes both. The eight fixed hosts, the padding host
      * and the capture control items are recorded before the code is
      * reported, on both paths: the block executed whatever it then
      * reported.
      *
      * Request ids '01AMOT' and '01ACOM' do not reach paragraph
      * INSERT-ENDOW: on those cases this module is compiled and
      * loadable, no capture is recorded, and HC-END-PRESENT holds
      * the 'N' that modernization/harness/driver.cbl set.
      *
      * No item of the caller's COMMAREA is addressed here. Of the
      * shared capture state, only HC-SQL-ENDOWMENT, HC-EVENT-SEQ,
      * HC-ORDER-LAST-STMT and the two order-guard items named above
      * are written, and HC-INJECT-SUB-SQLCODE and HC-POL-SEQ are
      * read and never written. That state carries no VALUE clause and
      * is never initialised here.
      *
      * Rationale for the single-superset signature standing for both
      * source blocks, for the reported SQLCODE, for the order guard
      * and for the length-keyed padding rule belongs to
      * modernization/docs/decision-log.md (planned deliverable; not
      * present at this milestone), rows: deterministic failure
      * injection through shared harness state; uniform stub-side
      * capture-order guard.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SQL-INSERT-ENDOWMENT.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      * Shared capture state. This module writes the ENDOWMENT group,
      * the shared event sequence and the last-statement name, and
      * reads the injected SQLCODE.
       COPY HCAPTURE.
      *
      * Shared SQL communications area read by the translated LGAPDB01.
       COPY HSQLCA.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
      * The nine host variables of the two blocks, in the order the dml
      * entries insert_endowment_varchar and insert_endowment_novarchar
      * of modernization/harness/statement_map.yml list them. Each shape
      * follows the declaration cited against it, and each is received
      * BY REFERENCE from the CALL the translated LGAPDB01 issues.
       LINKAGE SECTION.
      *
      * Slot 1, column POLICYNUMBER. Receives the caller's
      * DB2-POLICYNUM-INT PIC S9(9) COMP
      * [base/src/lgapdb01.cbl:117].
       01  LK-POLICYNUM-INT        PIC S9(9) COMP.
      *
      * Slot 2, column WITHPROFITS. Receives the caller's
      * CA-E-WITH-PROFITS PIC X
      * [base/src/lgcmarea.cpy:47].
       01  LK-WITH-PROFITS         PIC X.
      *
      * Slot 3, column EQUITIES. Receives the caller's
      * CA-E-EQUITIES PIC X
      * [base/src/lgcmarea.cpy:48].
       01  LK-EQUITIES             PIC X.
      *
      * Slot 4, column MANAGEDFUND. Receives the caller's
      * CA-E-MANAGED-FUND PIC X
      * [base/src/lgcmarea.cpy:49].
       01  LK-MANAGED-FUND         PIC X.
      *
      * Slot 5, column FUNDNAME. Receives the caller's
      * CA-E-FUND-NAME PIC X(10)
      * [base/src/lgcmarea.cpy:50].
       01  LK-FUND-NAME            PIC X(10).
      *
      * Slot 6, column TERM. Receives the caller's
      * DB2-E-TERM-SINT PIC S9(4) COMP
      * [base/src/lgapdb01.cbl:93].
      * The caller loads it from CA-E-TERM PIC 99
      * [base/src/lgcmarea.cpy:51] at [base/src/lgapdb01.cbl:330].
       01  LK-TERM-SINT            PIC S9(4) COMP.
      *
      * Slot 7, column SUMASSURED. Receives the caller's
      * DB2-E-SUMASSURED-INT PIC S9(9) COMP
      * [base/src/lgapdb01.cbl:94].
      * The caller loads it from CA-E-SUM-ASSURED PIC 9(6)
      * [base/src/lgcmarea.cpy:52] at [base/src/lgapdb01.cbl:331].
       01  LK-SUMASSURED-INT       PIC S9(9) COMP.
      *
      * Slot 8, column LIFEASSURED. Receives the caller's
      * CA-E-LIFE-ASSURED PIC X(31)
      * [base/src/lgcmarea.cpy:53].
       01  LK-LIFE-ASSURED         PIC X(31).
      *
      * Slot 9, column PADDINGDATA. Receives the caller's varchar host
      * structure WS-VARY-FIELD [base/src/lgapdb01.cbl:70-72], whose
      * two parts keep the level numbers and the pictures of that
      * declaration. Length prefix first, then the character body.
       01  LK-VARY-FIELD.
      *
      * Length half. Witnesses WS-VARY-LEN
      * [base/src/lgapdb01.cbl:71], the receiver of the SUBTRACT at
      * [base/src/lgapdb01.cbl:339-340] and the subject of the guard
      * at [base/src/lgapdb01.cbl:342].
           49 LK-VARY-LEN          PIC S9(4) COMP.
      *
      * Character half. Witnesses WS-VARY-CHAR
      * [base/src/lgapdb01.cbl:72], which the caller fills from
      * CA-E-PADDING-DATA [base/src/lgcmarea.cpy:54] at
      * [base/src/lgapdb01.cbl:344-345]. Read here only under the
      * length guard below.
           49 LK-VARY-CHAR         PIC X(3900).
      *
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION USING LK-POLICYNUM-INT
                                LK-WITH-PROFITS
                                LK-EQUITIES
                                LK-MANAGED-FUND
                                LK-FUND-NAME
                                LK-TERM-SINT
                                LK-SUMASSURED-INT
                                LK-LIFE-ASSURED
                                LK-VARY-FIELD.
      *
      *----------------------------------------------------------------*
      * Records the eight fixed hosts, applies the length-keyed        *
      * padding rule, stamps the capture control items, tests the      *
      * predecessor ordinal and reports the SQLCODE this run selected  *
      * to the translated LGAPDB01.                                    *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM CAPTURE-FIXED-HOSTS
           PERFORM CAPTURE-PADDING-HOST
           PERFORM STAMP-CAPTURE-CONTROL
           PERFORM CHECK-CAPTURE-ORDER
           MOVE HC-INJECT-SUB-SQLCODE TO SQLCODE
           GOBACK.
      *
      *----------------------------------------------------------------*
      * Moves the eight hosts common to both blocks into their         *
      * capture slots. Each slot carries the picture of the host it    *
      * witnesses; every move is verbatim.                             *
      *----------------------------------------------------------------*
       CAPTURE-FIXED-HOSTS.
           MOVE LK-POLICYNUM-INT  TO HC-END-POLICYNUM
           MOVE LK-WITH-PROFITS   TO HC-END-WITH-PROFITS
           MOVE LK-EQUITIES       TO HC-END-EQUITIES
           MOVE LK-MANAGED-FUND   TO HC-END-MANAGED-FUND
           MOVE LK-FUND-NAME      TO HC-END-FUND-NAME
           MOVE LK-TERM-SINT      TO HC-END-TERM
           MOVE LK-SUMASSURED-INT TO HC-END-SUMASSURED
           MOVE LK-LIFE-ASSURED   TO HC-END-LIFE-ASSURED.
      *
      *----------------------------------------------------------------*
      * Records the varchar host. The character capture slot is set    *
      * to spaces on every call, ahead of the length guard, so a call  *
      * whose body is not read leaves no characters of an earlier      *
      * call behind. The length reaches its capture slot on every      *
      * call and decides whether the character body is read: a length  *
      * of 1 through 3900 is read, a length of zero or below and a     *
      * length above 3900 are not.                                    *
      *----------------------------------------------------------------*
       CAPTURE-PADDING-HOST.
           MOVE SPACES TO HC-END-VARY-CHAR
           MOVE LK-VARY-LEN TO HC-END-VARY-LEN
           IF LK-VARY-LEN IS GREATER THAN ZERO
               IF LK-VARY-LEN IS GREATER THAN 3900
                   PERFORM REPORT-OVERSIZED-PADDING
               ELSE
                   PERFORM RECORD-PADDING-CHARACTERS
               END-IF
           END-IF.
      *
      *----------------------------------------------------------------*
      * Records the leading characters of the varchar body for a       *
      * length of 1 through 3900. The capture slot was set to spaces   *
      * by the caller above and receives exactly the passed number of  *
      * characters here, holding the data of this call alone. Both     *
      * fields are 3900 characters wide and the guard above bounds     *
      * the length; neither reference modification reaches past its    *
      * own field.                                                    *
      *----------------------------------------------------------------*
       RECORD-PADDING-CHARACTERS.
           MOVE LK-VARY-CHAR(1:LK-VARY-LEN)
             TO HC-END-VARY-CHAR(1:LK-VARY-LEN).
      *
      *----------------------------------------------------------------*
      * Reports on the run log a passed length above the 3900          *
      * characters that the varchar body declares. The length          *
      * already in HC-END-VARY-LEN is left as passed, the              *
      * character body is not read and no substitute value is          *
      * supplied.                                                      *
      *----------------------------------------------------------------*
       REPORT-OVERSIZED-PADDING.
           DISPLAY 'SQL-INSERT-ENDOWMENT: PADDING LENGTH '
                   LK-VARY-LEN
                   ' EXCEEDS THE 3900 CHARACTER BODY'
                   ' - NO CHARACTERS RECORDED'
           END-DISPLAY.
      *
      *----------------------------------------------------------------*
      * Marks the statement captured, counts the execution, stamps     *
      * the ordinal from the shared event sequence and names the       *
      * statement with its statement_map.yml key. The order-guard      *
      * items are written by CHECK-CAPTURE-ORDER below and not here.   *
      *----------------------------------------------------------------*
       STAMP-CAPTURE-CONTROL.
           MOVE 'Y' TO HC-END-PRESENT
           ADD 1 TO HC-END-COUNT
           END-ADD
           ADD 1 TO HC-EVENT-SEQ
           END-ADD
           MOVE HC-EVENT-SEQ TO HC-END-SEQ
           MOVE 'insert_endowment' TO HC-ORDER-LAST-STMT.
      *
      *----------------------------------------------------------------*
      * Tests the predecessor ordinal of both blocks, read after this  *
      * call stamped its own. HC-POL-SEQ at zero reports that the      *
      * INSERT INTO POLICY block at [base/src/lgapdb01.cbl:268-288]    *
      * was not captured ahead of this insert, which leaves slot 1     *
      * short of the identity [base/src/lgapdb01.cbl:308-311]          *
      * recovers. A non-zero HC-POL-SEQ leaves both order items as     *
      * the driver set them.                                           *
      *----------------------------------------------------------------*
       CHECK-CAPTURE-ORDER.
           IF HC-POL-SEQ = ZERO
               MOVE 'Y' TO HC-ORDER-VIOLATION
               MOVE 'insert_endowment' TO HC-ORDER-VIOLATION-STMT
           END-IF.
