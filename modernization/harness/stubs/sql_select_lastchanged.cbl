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
      * resolved in the shared seed group on every call. The move is
      * unconditional and fills all 26 characters, in the Db2 external
      * form YYYY-MM-DD-HH.MM.SS.NNNNNN. No environment variable is
      * read here, no default is applied here, no clock is read and the
      * value is neither trimmed nor reformatted.
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
      * key select_lastchanged. HC-ORDER-VIOLATION and
      * HC-ORDER-VIOLATION-STMT are not written here: the
      * execution_order block of
      * modernization/harness/statement_map.yml declares no prerequisite
      * for select_lastchanged.
      *
      * SQLCODE of the shared SQLCA is set to zero on every call. The
      * translated LGAPDB01 issues no SQLCODE test after this block; the
      * value SQLCODE carries reaches EM-SQLRC at
      * [base/src/lgapdb01.cbl:564] on the diagnostic path.
      *
      * No item of the caller's COMMAREA other than parameter 1 is
      * addressed here, no capture item outside
      * HC-SQL-SELECT-LASTCHANGED, HC-EVENT-CONTROL and
      * HC-ORDER-LAST-STMT is written, and the shared group is never
      * initialised here.
      *
      * Rationale for the deterministic seeding of the timestamp and for
      * the always-zero SQLCODE is recorded in
      * modernization/docs/decision-log.md.
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
      * stamps the capture control items and reports success to the    *
      * caller.                                                        *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM RETURN-LASTCHANGED
           PERFORM CAPTURE-SELECT-VALUES
           PERFORM STAMP-CAPTURE-CONTROL
           MOVE ZERO TO SQLCODE
           GOBACK.
      *
      *----------------------------------------------------------------*
      * Moves the seeded 26-character timestamp into the INTO          *
      * target. The field is copied in full, under no condition.       *
      *----------------------------------------------------------------*
       RETURN-LASTCHANGED.
           MOVE HC-SEED-LASTCHANGED TO CA-LASTCHANGED.
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
      * statement. The order-guard items are not written here.         *
      *----------------------------------------------------------------*
       STAMP-CAPTURE-CONTROL.
           SET  HC-LCHG-CAPTURED    TO TRUE
           ADD  1                   TO HC-LCHG-COUNT
           ADD  1                   TO HC-EVENT-SEQ
           MOVE HC-EVENT-SEQ        TO HC-LCHG-SEQ
           MOVE 'select_lastchanged' TO HC-ORDER-LAST-STMT.
      *----------------------------------------------------------------*
