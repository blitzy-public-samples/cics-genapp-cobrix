      ******************************************************************
      *                                                                *
      *                       CICS-ABEND                               *
      *                                                                *
      *   Abend emulation for the GnuCOBOL validation harness          *
      *                                                                *
      ******************************************************************
      *
      * Emulates the abend command of the Policy-Issue chain, records
      * the abend in the shared harness capture state and returns to
      * its caller.
      *
      * Source construct : Abend AbCode(...) NoDump commands
      * Code operand     : the ABCODE literal, four characters
      * Target module    : CICS-ABEND
      *
      * The six command sites and the code each one supplies:
      *   base/src/lgapol01.cbl:101   'LGCA'
      *   base/src/lgapdb01.cbl:168   'LGCA'
      *   base/src/lgapdb01.cbl:393   'LGSQ'
      *   base/src/lgapdb01.cbl:431   'LGSQ'
      *   base/src/lgapdb01.cbl:477   'LGSQ'
      *   base/src/lgapdb01.cbl:551   'LGSQ'
      * Every site states NODUMP, which has no harness counterpart.
      *
      * Milestone note: modernization/harness/translate.py, the three
      * translated programs it produces, modernization/harness/
      * driver.cbl, modernization/harness/run_harness.sh and the
      * generated tree modernization/harness/build/ are planned
      * artifacts and are not present in the tree at this milestone;
      * every statement below about the harness, about a translated
      * program or about the driver is the planned contract.
      *
      * Caller: modernization/harness/translate.py emits, at each of
      * the six sites, a move of that site's literal into the
      * HARNESS-ABEND-CODE item it declares in the translated program,
      * a call of this module with that item, and a GOBACK. The caller
      * issues that GOBACK itself, so this module returns normally and
      * ends no run unit. It names no termination service and leaves
      * the caller's storage unchanged.
      *
      * Arity: one parameter, matching the one operand the generated
      * call supplies. The code is read and recorded as received. This
      * module tests no value of it and maps it to no message and to
      * no return code.
      *
      * Capture surface, all declared by
      * modernization/harness/copybooks/hcapture.cpy:
      * HC-ABEND-PRESENT, HC-ABEND-CODE, HC-ABEND-COUNT, HC-ABEND-SEQ,
      * and the two shared items HC-EVENT-SEQ and HC-ORDER-LAST-STMT.
      * No other item of that group is written: the seed, SQL, VSAM,
      * diagnostic-link and order-violation items keep the values
      * their own owners set. The group carries no VALUE clause and is
      * initialised procedurally by modernization/harness/driver.cbl,
      * which this module never repeats.
      *
      * Rationale is recorded in modernization/docs/decision-log.md
      * (planned deliverable; not present at this milestone), rows:
      * called abend stub records and returns; shared EXTERNAL harness
      * state; shared event-sequence ordering witness and order guard;
      * abend sites unexercised by the two passing samples.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CICS-ABEND.
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
      *
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      *----------------------------------------------------------------*
      * Name this module reports as the statement captured most        *
      * recently, moved into HC-ORDER-LAST-STMT. An abend site is      *
      * reported under the name of the recording module.               *
      *----------------------------------------------------------------*
       77  WS-STMT-NAME         PIC X(10) VALUE 'cics_abend'.
      *
      *----------------------------------------------------------------*
      * Shared harness capture state. The group carries the EXTERNAL   *
      * clause. This module addresses the same storage as the driver   *
      * and as every other capture stub of the run unit.               *
      *----------------------------------------------------------------*
       COPY HCAPTURE.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N                             *
      ******************************************************************
       LINKAGE SECTION.
      *
      * Parameter 1, read. The four-character code the emulated command
      * supplies through ABCODE, held by the translated program in
      * HARNESS-ABEND-CODE. Recorded in HC-ABEND-CODE. This module
      * never assigns to it.
       01  LK-ABEND-CODE            PIC X(4).
      *
      *----------------------------------------------------------------*
      ******************************************************************
       PROCEDURE DIVISION USING LK-ABEND-CODE.
      *
      *----------------------------------------------------------------*
       MAINLINE SECTION.
      *----------------------------------------------------------------*
      *
      * Report an abend as recorded and hold the code received. The
      * code supersedes one held from an earlier site of the same case,
      * so the item carries the most recent one.
           SET  HC-ABEND-RECORDED   TO TRUE
           MOVE LK-ABEND-CODE       TO HC-ABEND-CODE
      *
      * Count this site. A case that reaches no site leaves the count
      * at the zero the driver set.
           ADD  1                   TO HC-ABEND-COUNT
      *
      * Stamp the execution ordinal from the shared event sequence and
      * report this module as the statement captured most recently.
      * This module has no declared prerequisite ordinal. It leaves
      * HC-ORDER-VIOLATION and HC-ORDER-VIOLATION-STMT holding the
      * values the driver set.
           ADD  1                   TO HC-EVENT-SEQ
           MOVE HC-EVENT-SEQ        TO HC-ABEND-SEQ
           MOVE WS-STMT-NAME        TO HC-ORDER-LAST-STMT.
      *
      *----------------------------------------------------------------*
       A-EXIT.
      * Return control to the caller, which issues its own GOBACK.
           GOBACK.
      *----------------------------------------------------------------*
