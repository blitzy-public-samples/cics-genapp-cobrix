      ******************************************************************
      *                                                                *
      *                     SQL-INSERT-MOTOR                           *
      *                                                                *
      *   Harness stand-in for the INSERT INTO MOTOR statement of      *
      *   the translated LGAPDB01                                      *
      *                                                                *
      ******************************************************************
      *
      * Emulates the SQL block at [base/src/lgapdb01.cbl:449-471] in
      * paragraph INSERT-MOTOR, INSERT INTO MOTOR. The translated
      * LGAPDB01 calls this module in place of that block and passes
      * the ten host variables of the block BY REFERENCE in source
      * order, as recorded by the dml entry insert_motor of
      * modernization/harness/statement_map.yml. That entry gives the
      * block arity 10; checks.using_counts records insert_motor 10.
      *
      * The block is reached on request id '01AMOT', which the routing
      * at [base/src/lgapdb01.cbl:231-232] pairs with paragraph
      * INSERT-MOTOR. No other request id reaches it.
      *
      * Parameters, in call order, each with the MOTOR column it
      * supplies and the capture item that witnesses it:
      *   1  DB2-POLICYNUM-INT    POLICYNUMBER      HC-MOT-POLICYNUM
      *   2  CA-M-MAKE            MAKE              HC-MOT-MAKE
      *   3  CA-M-MODEL           MODEL             HC-MOT-MODEL
      *   4  DB2-M-VALUE-INT      VALUE             HC-MOT-VALUE
      *   5  CA-M-REGNUMBER       REGNUMBER         HC-MOT-REGNUMBER
      *   6  CA-M-COLOUR          COLOUR            HC-MOT-COLOUR
      *   7  DB2-M-CC-SINT        CC                HC-MOT-CC
      *   8  CA-M-MANUFACTURED    YEAROFMANUFACTURE HC-MOT-MANUFACTURED
      *   9  DB2-M-PREMIUM-INT    PREMIUM           HC-MOT-PREMIUM
      *  10  DB2-M-ACCIDENTS-INT  ACCIDENTS         HC-MOT-ACCIDENTS
      * Every parameter is read here and none is written here.
      *
      * Parameters 4, 7, 9 and 10 reach the caller as binary integers
      * through the MOVE statements at [base/src/lgapdb01.cbl:443-446],
      * which load them from CA-M-VALUE PIC 9(6)
      * [base/src/lgcmarea.cpy:68], CA-M-CC PIC 9(4)
      * [base/src/lgcmarea.cpy:71], CA-M-PREMIUM PIC 9(6)
      * [base/src/lgcmarea.cpy:73] and CA-M-ACCIDENTS PIC 9(6)
      * [base/src/lgcmarea.cpy:74].
      *
      * Parameter 9 is recorded exactly as passed and reaches
      * canonical.preissued_rating.motor_premium_amount. No scaling,
      * rounding, sign change or derivation is applied to it here, and
      * none is applied to any other parameter;
      * modernization/validation/diff_harness_vs_warehouse.py compares
      * the captured value with the warehouse row.
      *
      * Capture control, following the contract stated by
      * modernization/harness/copybooks/hcapture.cpy: HC-MOT-PRESENT
      * becomes 'Y', HC-MOT-COUNT counts the executions of the block,
      * HC-EVENT-SEQ is advanced and its new value is stamped into
      * HC-MOT-SEQ, and HC-ORDER-LAST-STMT receives this statement's
      * key insert_motor. HC-ORDER-VIOLATION and
      * HC-ORDER-VIOLATION-STMT are not written here. The
      * execution_order block of
      * modernization/harness/statement_map.yml declares one
      * constraint, policy_before_commercial; insert_motor is neither
      * of its two members and has no prerequisite ordinal of its own.
      *
      * SQLCODE of the shared SQLCA is set to zero on every call. The
      * translated LGAPDB01 tests IF SQLCODE NOT EQUAL 0 at
      * [base/src/lgapdb01.cbl:473]; the '90' return code at line 474
      * and the ABCODE 'LGSQ' abend at line 477 follow a non-zero
      * value.
      *
      * No item of the caller's COMMAREA is addressed here. Of the
      * shared capture state, only HC-SQL-MOTOR, HC-EVENT-SEQ and
      * HC-ORDER-LAST-STMT are written. The group is EXTERNAL, carries
      * no VALUE clause and is initialised by
      * modernization/harness/driver.cbl before each case; no item of
      * it is initialised here.
      *
      * Rationale for the always-zero SQLCODE, for the passthrough
      * handling of the amounts and for the amount comparison
      * tolerance is recorded in modernization/docs/decision-log.md.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SQL-INSERT-MOTOR.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      * Shared capture state. This module writes the MOTOR group, the
      * shared event sequence and the last-statement name.
       COPY HCAPTURE.
      *
      * Shared SQL communications area read by the translated LGAPDB01.
       COPY HSQLCA.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
      * The ten host variables of the block at
      * [base/src/lgapdb01.cbl:449-471], in the order the dml entry
      * insert_motor of modernization/harness/statement_map.yml lists
      * them. Each shape follows the declaration cited against it.
       LINKAGE SECTION.
      *
      * Slot 1, column POLICYNUMBER. Receives the caller's
      * DB2-POLICYNUM-INT PIC S9(9) COMP [base/src/lgapdb01.cbl:117].
       01  LK-POLICYNUM-INT        PIC S9(9) COMP.
      *
      * Slot 2, column MAKE. Receives CA-M-MAKE
      * [base/src/lgcmarea.cpy:66].
       01  LK-M-MAKE               PIC X(15).
      *
      * Slot 3, column MODEL. Receives CA-M-MODEL
      * [base/src/lgcmarea.cpy:67].
       01  LK-M-MODEL              PIC X(15).
      *
      * Slot 4, column VALUE. Receives DB2-M-VALUE-INT PIC S9(9) COMP
      * [base/src/lgapdb01.cbl:98].
       01  LK-M-VALUE-INT          PIC S9(9) COMP.
      *
      * Slot 5, column REGNUMBER. Receives CA-M-REGNUMBER
      * [base/src/lgcmarea.cpy:69].
       01  LK-M-REGNUMBER          PIC X(7).
      *
      * Slot 6, column COLOUR. Receives CA-M-COLOUR
      * [base/src/lgcmarea.cpy:70].
       01  LK-M-COLOUR             PIC X(8).
      *
      * Slot 7, column CC. Receives DB2-M-CC-SINT PIC S9(4) COMP
      * [base/src/lgapdb01.cbl:99].
       01  LK-M-CC-SINT            PIC S9(4) COMP.
      *
      * Slot 8, column YEAROFMANUFACTURE. Receives CA-M-MANUFACTURED
      * [base/src/lgcmarea.cpy:72].
       01  LK-M-MANUFACTURED       PIC X(10).
      *
      * Slot 9, column PREMIUM. Receives DB2-M-PREMIUM-INT
      * PIC S9(9) COMP [base/src/lgapdb01.cbl:100].
       01  LK-M-PREMIUM-INT        PIC S9(9) COMP.
      *
      * Slot 10, column ACCIDENTS. Receives DB2-M-ACCIDENTS-INT
      * PIC S9(9) COMP [base/src/lgapdb01.cbl:101].
       01  LK-M-ACCIDENTS-INT      PIC S9(9) COMP.
      *
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION USING LK-POLICYNUM-INT
                                LK-M-MAKE
                                LK-M-MODEL
                                LK-M-VALUE-INT
                                LK-M-REGNUMBER
                                LK-M-COLOUR
                                LK-M-CC-SINT
                                LK-M-MANUFACTURED
                                LK-M-PREMIUM-INT
                                LK-M-ACCIDENTS-INT.
      *
      *----------------------------------------------------------------*
      * Records the ten host values, stamps the capture control items  *
      * and reports success.                                           *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM CAPTURE-MOTOR-HOSTS
           PERFORM STAMP-CAPTURE-CONTROL
           MOVE ZERO TO SQLCODE
           GOBACK.
      *
      *----------------------------------------------------------------*
      * Moves each parameter into the capture slot of the MOTOR group  *
      * named against it above. Each value is moved as received: no    *
      * trimming, re-formatting, scaling or rounding is applied.       *
      *----------------------------------------------------------------*
       CAPTURE-MOTOR-HOSTS.
           MOVE LK-POLICYNUM-INT    TO HC-MOT-POLICYNUM
           MOVE LK-M-MAKE           TO HC-MOT-MAKE
           MOVE LK-M-MODEL          TO HC-MOT-MODEL
           MOVE LK-M-VALUE-INT      TO HC-MOT-VALUE
           MOVE LK-M-REGNUMBER      TO HC-MOT-REGNUMBER
           MOVE LK-M-COLOUR         TO HC-MOT-COLOUR
           MOVE LK-M-CC-SINT        TO HC-MOT-CC
           MOVE LK-M-MANUFACTURED   TO HC-MOT-MANUFACTURED
           MOVE LK-M-PREMIUM-INT    TO HC-MOT-PREMIUM
           MOVE LK-M-ACCIDENTS-INT  TO HC-MOT-ACCIDENTS.
      *
      *----------------------------------------------------------------*
      * Marks the block captured, counts the execution, stamps the     *
      * ordinal from the shared event sequence and names the           *
      * statement. The order-guard items are not written here.         *
      *----------------------------------------------------------------*
       STAMP-CAPTURE-CONTROL.
           MOVE 'Y' TO HC-MOT-PRESENT
           ADD 1 TO HC-MOT-COUNT
           ADD 1 TO HC-EVENT-SEQ
           MOVE HC-EVENT-SEQ TO HC-MOT-SEQ
           MOVE 'insert_motor' TO HC-ORDER-LAST-STMT.
