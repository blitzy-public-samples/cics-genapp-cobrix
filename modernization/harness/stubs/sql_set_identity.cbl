      ******************************************************************
      *                                                                *
      *                     SQL-SET-IDENTITY                           *
      *                                                                *
      *   Harness stand-in for the SET IDENTITY_VAL_LOCAL() statement  *
      *   of the translated LGAPDB01                                   *
      *                                                                *
      ******************************************************************
      *
      * Emulates the SQL block at [base/src/lgapdb01.cbl:308-310] in
      * paragraph INSERT-POLICY, SET :DB2-POLICYNUM-INT =
      * IDENTITY_VAL_LOCAL(). The translated LGAPDB01 calls this module
      * in place of that block and passes the single host variable of
      * the block BY REFERENCE, as recorded by the dml entry
      * set_identity of modernization/harness/statement_map.yml. That
      * entry gives the block arity 1 and direction out, and
      * checks.using_counts records set_identity 1.
      *
      * Parameter, with the value it stands for and the capture item
      * that witnesses it:
      *   1  DB2-POLICYNUM-INT  IDENTITY_VAL_LOCAL()  HC-IDENT-POLICYNUM
      * The parameter is written here and never read here.
      *
      * The value returned is the identity that
      * modernization/harness/stubs/sql_insert_policy.cbl resolved and
      * left in HC-SEED-POLICYNUM. That module runs first: the source
      * performs INSERT-POLICY at [base/src/lgapdb01.cbl:219] and its
      * INSERT INTO POLICY block at [base/src/lgapdb01.cbl:268-288]
      * precedes this block inside that paragraph. No environment
      * variable is read here, no default is applied here, and no value
      * is generated, incremented or randomised here.
      *
      * The translated LGAPDB01 moves the returned value to
      * CA-POLICY-NUM PIC 9(10) [base/src/lgcmarea.cpy:35] at
      * [base/src/lgapdb01.cbl:311] and on to EM-POLNUM at
      * [base/src/lgapdb01.cbl:313]. The same host variable is host 1 of
      * every product insert and the WHERE predicate host of the
      * LASTCHANGED read-back at [base/src/lgapdb01.cbl:316-321].
      *
      * HC-SEED-POLICYNUM at zero or below reports that the INSERT INTO
      * POLICY block did not run before this one. The stored value is
      * returned unaltered and the condition is reported on the run
      * log; no substitute value is supplied.
      *
      * Capture control, following the contract stated by
      * modernization/harness/copybooks/hcapture.cpy: HC-IDENT-PRESENT
      * becomes 'Y', HC-IDENT-COUNT counts the executions of the block,
      * HC-EVENT-SEQ is advanced and its new value is stamped into
      * HC-IDENT-SEQ, and HC-ORDER-LAST-STMT receives this statement's
      * key set_identity. HC-ORDER-VIOLATION and
      * HC-ORDER-VIOLATION-STMT are not written here. The
      * execution_order block of
      * modernization/harness/statement_map.yml declares one
      * constraint, policy_before_commercial; set_identity is neither
      * of its two members and has no prerequisite ordinal of its own.
      *
      * SQLCODE of the shared SQLCA is set to zero on every call.
      *
      * No item of the caller's COMMAREA is addressed here. Of the
      * shared capture state, only HC-SQL-SET-IDENTITY, HC-EVENT-SEQ
      * and HC-ORDER-LAST-STMT are written. HC-SEED-POLICYNUM is read
      * and left holding the identity that the product insert stubs and
      * the KSDSPOLY key of the translated LGAPVS01 receive after this
      * call.
      *
      * Rationale for the deterministic seeding of the identity and for
      * the always-zero SQLCODE is to be recorded in
      * modernization/docs/decision-log.md (planned deliverable; not
      * present at this milestone).
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SQL-SET-IDENTITY.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      * Shared capture state. This module writes the SET-IDENTITY
      * group, the shared event sequence and the last-statement name,
      * and reads the seeded identity.
       COPY HCAPTURE.
      *
      * Shared SQL communications area read by the translated LGAPDB01.
       COPY HSQLCA.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
      * The single host variable of the block at
      * [base/src/lgapdb01.cbl:308-310], in the order the dml entry
      * set_identity of modernization/harness/statement_map.yml lists
      * it. The shape follows the declaration cited against it.
       LINKAGE SECTION.
      *
      * Slot 1, IDENTITY_VAL_LOCAL(), direction out. Receives the
      * caller's DB2-POLICYNUM-INT PIC S9(9) COMP
      * [base/src/lgapdb01.cbl:117] BY REFERENCE.
       01  LK-POLICYNUM-INT        PIC S9(9) COMP.
      *
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION USING LK-POLICYNUM-INT.
      *
      *----------------------------------------------------------------*
      * Supplies the seeded identity, stamps the capture control       *
      * items, reports an unseeded identity and reports success.       *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM SUPPLY-SEEDED-IDENTITY
           PERFORM STAMP-CAPTURE-CONTROL
           PERFORM CHECK-SEEDED-IDENTITY
           MOVE ZERO TO SQLCODE
           GOBACK.
      *
      *----------------------------------------------------------------*
      * Moves the identity held in HC-SEED-POLICYNUM into the output   *
      * parameter and into its capture slot. The seed item is left     *
      * unchanged.                                                     *
      *----------------------------------------------------------------*
       SUPPLY-SEEDED-IDENTITY.
           MOVE HC-SEED-POLICYNUM TO LK-POLICYNUM-INT
           MOVE HC-SEED-POLICYNUM TO HC-IDENT-POLICYNUM.
      *
      *----------------------------------------------------------------*
      * Marks the block captured, counts the execution, stamps the     *
      * ordinal from the shared event sequence and names the           *
      * statement. The order-guard items are not written here.         *
      *----------------------------------------------------------------*
       STAMP-CAPTURE-CONTROL.
           MOVE 'Y' TO HC-IDENT-PRESENT
           ADD 1 TO HC-IDENT-COUNT END-ADD
           ADD 1 TO HC-EVENT-SEQ END-ADD
           MOVE HC-EVENT-SEQ TO HC-IDENT-SEQ
           MOVE 'set_identity' TO HC-ORDER-LAST-STMT.
      *
      *----------------------------------------------------------------*
      * Reports on the run log an identity of zero or below. The       *
      * value already returned is not altered and no substitute is     *
      * supplied.                                                      *
      *----------------------------------------------------------------*
       CHECK-SEEDED-IDENTITY.
           IF HC-SEED-POLICYNUM IS NOT GREATER THAN ZERO
               DISPLAY 'SQL-SET-IDENTITY: HC-SEED-POLICYNUM HOLDS '
                       HC-SEED-POLICYNUM
                       ' - SQL-INSERT-POLICY DID NOT RUN FIRST'
               END-DISPLAY
           END-IF.
