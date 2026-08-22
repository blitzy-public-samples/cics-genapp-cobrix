      ******************************************************************
      *                                                                *
      *                     SQL-SELECT-LASTCHANGED                     *
      *                                                                *
      *   Harness stand-in for the SELECT LASTCHANGED read-back of     *
      *   the translated LGAPDB01                                      *
      *                                                                *
      ******************************************************************
      *
      * Emulates the SQL block at [base/src/lgapdb01.cbl:316-321] in
      * paragraph INSERT-POLICY. The translated LGAPDB01 calls this
      * module in place of that block and passes the two host variables
      * of the block BY REFERENCE in source order, as recorded by the
      * dml entry select_lastchanged of
      * modernization/harness/statement_map.yml.
      *
      * Parameters, each with the POLICY column it is paired with, its
      * direction and the capture item that witnesses it:
      *   1  CA-LASTCHANGED     LASTCHANGED   out  HC-LCHG-LASTCHANGED
      *   2  DB2-POLICYNUM-INT  POLICYNUMBER  in   HC-LCHG-POLICYNUM
      * Parameter 1 is the INTO target of [base/src/lgapdb01.cbl:318].
      * Parameter 2 is the host of the WHERE POLICYNUMBER predicate at
      * [base/src/lgapdb01.cbl:320]; it is recorded as received, and no
      * row selection, comparison or not-found condition is derived
      * from it. The block returns one row for the policy of the case.
      *
      * The value moved into parameter 1 is HC-SEED-LASTCHANGED, the
      * 26-character timestamp that
      * modernization/harness/stubs/sql_insert_policy.cbl leaves
      * resolved in the shared seed group on every call. The move fills
      * all 26 characters, in the Db2 external form
      * YYYY-MM-DD-HH.MM.SS.NNNNNN. No environment variable is read
      * here, no clock is read and the value is neither trimmed nor
      * reformatted.
      *
      * The seed is validated before it is returned: the six separators
      * in their fixed positions, a digit in every other position, a
      * year of 0001 through 9999, a month of 01 through 12, a day the
      * month and year allow under the Gregorian leap rule, an hour of
      * 00 through 23, a minute and a second of 00 through 59, and six
      * fractional digits. A seed that names an impossible date or time
      * is named in the log and replaced by the same documented default
      * the policy insert of the harness applies,
      * 2026-08-19-12.00.00.000000, in the shared seed item and in
      * parameter 1 alike, so this module returns a real timestamp on
      * every call.
      *
      * Parameter 1 addresses CA-LASTCHANGED [base/src/lgcmarea.cpy:40]
      * within the caller's DFHCOMMAREA. The move reaches the post-chain
      * record that modernization/harness/driver.cbl reports and the
      * value INSERT-COMMERCIAL supplies to the COMMERCIAL column
      * RequestDate at [base/src/lgapdb01.cbl:525]. HC-SEED-LASTCHANGED
      * is left holding the same value.
      *
      * Capture control, following the contract stated by
      * modernization/harness/copybooks/hcapture.cpy: HC-LCHG-PRESENT
      * becomes 'Y', HC-LCHG-COUNT counts the executions of the block,
      * HC-EVENT-SEQ is advanced and its new value is stamped into
      * HC-LCHG-SEQ, and HC-ORDER-LAST-STMT receives this statement's
      * key select_lastchanged.
      *
      * Order guard. The predecessor of this block is the SET
      * :DB2-POLICYNUM-INT = IDENTITY_VAL_LOCAL() block at
      * [base/src/lgapdb01.cbl:308-310]: it stands ahead of this one in
      * paragraph INSERT-POLICY and supplies the WHERE predicate host
      * of parameter 2. HC-IDENT-SEQ carries that predecessor. This
      * module reads it after stamping its own ordinal: a HC-IDENT-SEQ
      * still at zero reports the predecessor unrun in
      * HC-ORDER-VIOLATION and HC-ORDER-VIOLATION-STMT, and a non-zero
      * HC-IDENT-SEQ leaves both items as
      * modernization/harness/driver.cbl set them. The INSERT INTO
      * POLICY block ahead of both is the predecessor the SET block
      * tests for itself. This is the constraint the execution_order
      * entry identity_before_lastchanged of
      * modernization/harness/statement_map.yml declares, and this
      * block is in turn the predecessor its four product entries
      * declare, so HC-LCHG-SEQ carries the whole paragraph to them.
      * modernization/harness/translate.py reconciles this guard with
      * those entries on every run.
      *
      * The execution_order block of
      * modernization/harness/statement_map.yml declares eight ordering
      * constraints, and each names in its enforced_by field the one
      * stub that tests it at run time. This module is the enforced_by
      * module of identity_before_lastchanged, the constraint the guard
      * above tests: predecessor set_identity, successor
      * select_lastchanged, reason_kind data_dependency on
      * DB2-POLICYNUM-INT, witness ordinals HC-IDENT-SEQ and
      * HC-LCHG-SEQ.
      *
      * The HC-LCHG-SEQ stamped here is read by four further constraints
      * that this module does not enforce, one per product insert, each
      * declaring select_lastchanged as its predecessor and HC-LCHG-SEQ
      * as its predecessor ordinal: lastchanged_before_motor, enforced
      * by modernization/harness/stubs/sql_insert_motor.cbl;
      * lastchanged_before_house, enforced by
      * modernization/harness/stubs/sql_insert_house.cbl;
      * lastchanged_before_endowment, enforced by
      * modernization/harness/stubs/sql_insert_endowment.cbl; and
      * lastchanged_before_commercial, enforced by
      * modernization/harness/stubs/sql_insert_commercial.cbl. The
      * remaining three, policy_first_captured, policy_before_identity
      * and policy_and_product_before_vsam_write, name neither
      * select_lastchanged nor HC-LCHG-SEQ.
      *
      * SQLCODE of the shared SQLCA is set to zero on every call. The
      * translated LGAPDB01 issues no SQLCODE test after this block; the
      * value SQLCODE carries reaches EM-SQLRC at
      * [base/src/lgapdb01.cbl:564] on the diagnostic path.
      *
      * No item of the caller's COMMAREA other than parameter 1 is
      * addressed here, no capture item outside
      * HC-SQL-SELECT-LASTCHANGED, HC-EVENT-CONTROL,
      * HC-ORDER-LAST-STMT, the two order-guard items named above and
      * HC-SEED-LASTCHANGED is written, that
      * last one only to replace a seed the validation rejected, and
      * the shared group is never initialised here. HC-IDENT-SEQ is
      * read here and never written.
      *
      * Rationale for the deterministic seeding of the timestamp, for
      * the order guard and for the always-zero SQLCODE belongs to
      * modernization/docs/decision-log.md, row: uniform stub-side
      * capture-order guard.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SQL-SELECT-LASTCHANGED.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      * Shared harness capture state. The group carries the EXTERNAL
      * clause. This module addresses the same storage as the driver and
      * as every other capture stub of the run unit, and writes the
      * SELECT LASTCHANGED group, the shared event sequence and the
      * last-statement name.
       COPY HCAPTURE.
      *
      * Shared SQL communications area read by the translated LGAPDB01.
       COPY HSQLCA.
      *
      *----------------------------------------------------------------*
      * Local items used to validate the seeded timestamp              *
      *----------------------------------------------------------------*
      * The seed under validation, laid out as the Db2 external form
      * YYYY-MM-DD-HH.MM.SS.NNNNNN. The character view carries the
      * class tests; the redefinition below reads the same characters
      * as the numbers they spell, and is addressed only after every
      * one of them has been found numeric.
       01  WS-STAMP.
           03 WS-STAMP-YEAR        PIC X(4).
           03 WS-STAMP-SEP1        PIC X.
           03 WS-STAMP-MONTH       PIC X(2).
           03 WS-STAMP-SEP2        PIC X.
           03 WS-STAMP-DAY         PIC X(2).
           03 WS-STAMP-SEP3        PIC X.
           03 WS-STAMP-HOUR        PIC X(2).
           03 WS-STAMP-SEP4        PIC X.
           03 WS-STAMP-MINUTE      PIC X(2).
           03 WS-STAMP-SEP5        PIC X.
           03 WS-STAMP-SECOND      PIC X(2).
           03 WS-STAMP-SEP6        PIC X.
           03 WS-STAMP-MICROS      PIC X(6).
      *
       01  WS-STAMP-NUM REDEFINES WS-STAMP.
           03 WS-NUM-YEAR          PIC 9(4).
           03 FILLER               PIC X.
           03 WS-NUM-MONTH         PIC 9(2).
           03 FILLER               PIC X.
           03 WS-NUM-DAY           PIC 9(2).
           03 FILLER               PIC X.
           03 WS-NUM-HOUR          PIC 9(2).
           03 FILLER               PIC X.
           03 WS-NUM-MINUTE        PIC 9(2).
           03 FILLER               PIC X.
           03 WS-NUM-SECOND        PIC 9(2).
           03 FILLER               PIC X.
           03 WS-NUM-MICROS        PIC 9(6).
      *
      * Outcome of the validation, the element that failed it, the
      * highest day the month and year allow, and 'Y' while that year
      * is a leap year under the Gregorian rule.
       01  WS-STAMP-OK             PIC X.
       01  WS-STAMP-REASON         PIC X(48).
       01  WS-STAMP-MAX-DAY        PIC 9(2).
       01  WS-STAMP-LEAP           PIC X.
      *
      * The timestamp returned when the seed does not name a real date
      * and time. It is the default
      * modernization/harness/stubs/sql_insert_policy.cbl applies.
       01  WS-DEFAULT-LASTCHANGED  PIC X(26)
                                   VALUE '2026-08-19-12.00.00.000000'.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N                             *
      ******************************************************************
      * The two host variables of [base/src/lgapdb01.cbl:316-321], in
      * the source order of the block, which is the order the dml entry
      * select_lastchanged of modernization/harness/statement_map.yml
      * records. Shapes follow the declarations cited against each item.
       LINKAGE SECTION.
      *
      * Slot 1, column LASTCHANGED, direction out. CA-LASTCHANGED
      * [base/src/lgcmarea.cpy:40], the INTO target at
      * [base/src/lgapdb01.cbl:318]. Receives all 26 characters of the
      * timestamp on every call.
       01  CA-LASTCHANGED           PIC X(26).
      *
      * Slot 2, column POLICYNUMBER, direction in. DB2-POLICYNUM-INT
      * [base/src/lgapdb01.cbl:117], the WHERE predicate host at
      * [base/src/lgapdb01.cbl:320], holding the identity the
      * translated LGAPDB01 received for
      * [base/src/lgapdb01.cbl:308-310]. This module records it and
      * never assigns to it.
       01  DB2-POLICYNUM-INT        PIC S9(9) COMP.
      *
      ******************************************************************
      *    P R O C E D U R E S                                         *
      ******************************************************************
       PROCEDURE DIVISION USING CA-LASTCHANGED
                                DB2-POLICYNUM-INT.
      *
      *----------------------------------------------------------------*
      * Returns the seeded timestamp, records both host slots,         *
      * stamps the capture control items, tests the predecessor        *
      * ordinal and reports success to the caller.                     *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM RETURN-LASTCHANGED
           PERFORM CAPTURE-SELECT-VALUES
           PERFORM STAMP-CAPTURE-CONTROL
           PERFORM CHECK-CAPTURE-ORDER
           MOVE ZERO TO SQLCODE
           GOBACK.
      *
      *----------------------------------------------------------------*
      * Moves the seeded 26-character timestamp into the INTO          *
      * target. The field is copied in full. A seed that does not name *
      * a real date and time is named in the log and replaced by the   *
      * documented default in the shared seed item and in the INTO     *
      * target alike.                                                 *
      *----------------------------------------------------------------*
       RETURN-LASTCHANGED.
           MOVE HC-SEED-LASTCHANGED TO WS-STAMP
           PERFORM VALIDATE-TIMESTAMP-SEED
           IF WS-STAMP-OK NOT = 'Y'
               DISPLAY 'SQL-SELECT-LASTCHANGED: the seeded timestamp '
                       'was rejected: '
                       FUNCTION TRIM(WS-STAMP-REASON)
               END-DISPLAY
               DISPLAY 'SQL-SELECT-LASTCHANGED: the read-back returns '
                       'the documented default '
                       WS-DEFAULT-LASTCHANGED
               END-DISPLAY
               MOVE WS-DEFAULT-LASTCHANGED TO HC-SEED-LASTCHANGED
           END-IF
           MOVE HC-SEED-LASTCHANGED TO CA-LASTCHANGED.
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
      * month and the year decide.                                     *
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
      * Records the timestamp handed back and the predicate value      *
      * received, each as it stands.                                   *
      *----------------------------------------------------------------*
       CAPTURE-SELECT-VALUES.
           MOVE CA-LASTCHANGED      TO HC-LCHG-LASTCHANGED
           MOVE DB2-POLICYNUM-INT   TO HC-LCHG-POLICYNUM.
      *
      *----------------------------------------------------------------*
      * Marks the block captured, counts the execution, stamps the     *
      * ordinal from the shared event sequence and names the           *
      * statement. The order-guard items are written by                *
      * CHECK-CAPTURE-ORDER below and not here.                        *
      *----------------------------------------------------------------*
       STAMP-CAPTURE-CONTROL.
           SET  HC-LCHG-CAPTURED    TO TRUE
           ADD  1                   TO HC-LCHG-COUNT  END-ADD
           ADD  1                   TO HC-EVENT-SEQ   END-ADD
           MOVE HC-EVENT-SEQ        TO HC-LCHG-SEQ
           MOVE 'select_lastchanged' TO HC-ORDER-LAST-STMT.
      *
      *----------------------------------------------------------------*
      * Tests the predecessor ordinal of this block, read after it     *
      * stamped its own. HC-IDENT-SEQ at zero reports that the SET     *
      * block at [base/src/lgapdb01.cbl:308-310] was not captured      *
      * ahead of this read-back, which leaves the WHERE predicate host *
      * of parameter 2 unpopulated. A non-zero HC-IDENT-SEQ leaves     *
      * both order items as the driver set them.                       *
      *----------------------------------------------------------------*
       CHECK-CAPTURE-ORDER.
           IF HC-IDENT-SEQ = ZERO
               MOVE 'Y' TO HC-ORDER-VIOLATION
               MOVE 'select_lastchanged' TO HC-ORDER-VIOLATION-STMT
           END-IF.
      *----------------------------------------------------------------*
