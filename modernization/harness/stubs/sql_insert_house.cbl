      ******************************************************************
      *                                                                *
      *                     SQL-INSERT-HOUSE                           *
      *                                                                *
      *   Harness stand-in for the INSERT INTO HOUSE statement of      *
      *   the translated LGAPDB01                                      *
      *                                                                *
      ******************************************************************
      *
      * Emulates the SQL block at [base/src/lgapdb01.cbl:409-425] in
      * paragraph INSERT-HOUSE. The translated LGAPDB01 calls this
      * module in place of that block and passes the seven host
      * variables of the block BY REFERENCE in source order, as
      * recorded by the dml entry insert_house of
      * modernization/harness/statement_map.yml. That entry gives the
      * block arity 7, and checks.using_counts records insert_house 7.
      *
      * Each of the seven HOUSE columns takes one host variable: the
      * column list at [base/src/lgapdb01.cbl:411-417] and the VALUES
      * list at [base/src/lgapdb01.cbl:418-424] hold the same order,
      * which the parameter order below reproduces.
      *
      * Parameters, each with the HOUSE column it is paired with and
      * the capture item that witnesses it:
      *   1  DB2-POLICYNUM-INT    POLICYNUMBER  HC-HOU-POLICYNUM
      *   2  CA-H-PROPERTY-TYPE   PROPERTYTYPE  HC-HOU-PROPERTY-TYPE
      *   3  DB2-H-BEDROOMS-SINT  BEDROOMS      HC-HOU-BEDROOMS
      *   4  DB2-H-VALUE-INT      VALUE         HC-HOU-VALUE
      *   5  CA-H-HOUSE-NAME      HOUSENAME     HC-HOU-HOUSE-NAME
      *   6  CA-H-HOUSE-NUMBER    HOUSENUMBER   HC-HOU-HOUSE-NUMBER
      *   7  CA-H-POSTCODE        POSTCODE      HC-HOU-POSTCODE
      * Each value is recorded as received, without trimming or
      * reformatting. No value is derived from any parameter.
      *
      * Parameters 3 and 4 arrive already in integer form: the caller
      * loads DB2-H-VALUE-INT from CA-H-VALUE PIC 9(8) and
      * DB2-H-BEDROOMS-SINT from CA-H-BEDROOMS PIC 9(3) by the MOVE
      * statements at [base/src/lgapdb01.cbl:405-406]. No arithmetic is
      * performed on this path, here or in the caller.
      *
      * The HOUSE column list at [base/src/lgapdb01.cbl:411-417] holds
      * no premium and no other amount column, and this module records
      * none.
      *
      * Capture control, following the contract stated by
      * modernization/harness/copybooks/hcapture.cpy: HC-HOU-PRESENT
      * becomes 'Y', HC-HOU-COUNT counts the executions of the block,
      * HC-EVENT-SEQ is advanced and its new value is stamped into
      * HC-HOU-SEQ, and HC-ORDER-LAST-STMT receives this statement's
      * key insert_house. HC-ORDER-VIOLATION and
      * HC-ORDER-VIOLATION-STMT are not written here. The
      * execution_order block of
      * modernization/harness/statement_map.yml declares one
      * constraint, policy_before_commercial; insert_house is neither
      * of its two members and has no prerequisite ordinal of its own.
      *
      * SQLCODE of the shared SQLCA reports HC-INJECT-SUB-SQLCODE on
      * every call. The translated LGAPDB01 tests it with IF SQLCODE
      * NOT EQUAL 0 at [base/src/lgapdb01.cbl:427]; the unequal branch
      * at [base/src/lgapdb01.cbl:428-432] moves '90' to
      * CA-RETURN-CODE, writes the diagnostic, abends with ABCODE
      * 'LGSQ' and returns. Zero leaves that branch untaken. The seven
      * host values and the capture control items are recorded before
      * the code is reported, on both paths: the block executed
      * whatever it then reported.
      *
      * The block is reached on request id '01AHOU', routed at
      * [base/src/lgapdb01.cbl:228-229]. The samples 01AMOT and 01ACOM
      * do not reach it: on those two cases this module is loadable and
      * uncalled, and HC-HOU-PRESENT holds the 'N' the driver set.
      *
      * No item of the caller's COMMAREA is addressed here, and no
      * capture item outside HC-SQL-HOUSE, HC-EVENT-SEQ and
      * HC-ORDER-LAST-STMT is written. HC-INJECT-SUB-SQLCODE is read
      * here and never written.
      *
      * Rationale for compiling a route the two samples do not exercise
      * and for the reported SQLCODE belongs to
      * modernization/docs/decision-log.md (planned deliverable; not
      * present at this milestone), row: deterministic failure
      * injection through shared harness state.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SQL-INSERT-HOUSE.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      * Shared capture state. This module writes the HOUSE group, the
      * shared event sequence and the last-statement name, and reads
      * the injected SQLCODE.
       COPY HCAPTURE.
      *
      * Shared SQL communications area read by the translated LGAPDB01.
       COPY HSQLCA.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
      * The seven host variables of [base/src/lgapdb01.cbl:409-425], in
      * the source order of the block. Shapes follow the declarations
      * cited against each item.
       LINKAGE SECTION.
      *
      * Slot 1, column POLICYNUMBER. DB2-POLICYNUM-INT
      * [base/src/lgapdb01.cbl:117], holding the identity supplied by
      * the SET block at [base/src/lgapdb01.cbl:308-310].
       01  DB2-POLICYNUM-INT       PIC S9(9) COMP.
      *
      * Slot 2, column PROPERTYTYPE. CA-H-PROPERTY-TYPE
      * [base/src/lgcmarea.cpy:57].
       01  CA-H-PROPERTY-TYPE      PIC X(15).
      *
      * Slot 3, column BEDROOMS. DB2-H-BEDROOMS-SINT
      * [base/src/lgapdb01.cbl:96], loaded from CA-H-BEDROOMS PIC 9(3)
      * [base/src/lgcmarea.cpy:58] by the MOVE at
      * [base/src/lgapdb01.cbl:406].
       01  DB2-H-BEDROOMS-SINT     PIC S9(4) COMP.
      *
      * Slot 4, column VALUE. DB2-H-VALUE-INT
      * [base/src/lgapdb01.cbl:97], loaded from CA-H-VALUE PIC 9(8)
      * [base/src/lgcmarea.cpy:59] by the MOVE at
      * [base/src/lgapdb01.cbl:405].
       01  DB2-H-VALUE-INT         PIC S9(9) COMP.
      *
      * Slot 5, column HOUSENAME. CA-H-HOUSE-NAME
      * [base/src/lgcmarea.cpy:60].
       01  CA-H-HOUSE-NAME         PIC X(20).
      *
      * Slot 6, column HOUSENUMBER. CA-H-HOUSE-NUMBER
      * [base/src/lgcmarea.cpy:61].
       01  CA-H-HOUSE-NUMBER       PIC X(4).
      *
      * Slot 7, column POSTCODE. CA-H-POSTCODE
      * [base/src/lgcmarea.cpy:62].
       01  CA-H-POSTCODE           PIC X(8).
      *
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION USING DB2-POLICYNUM-INT
                                CA-H-PROPERTY-TYPE
                                DB2-H-BEDROOMS-SINT
                                DB2-H-VALUE-INT
                                CA-H-HOUSE-NAME
                                CA-H-HOUSE-NUMBER
                                CA-H-POSTCODE.
      *
      *----------------------------------------------------------------*
      * Records the seven host values, stamps the capture control      *
      * items and reports the SQLCODE this run selected.               *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM CAPTURE-HOUSE-VALUES
           PERFORM STAMP-CAPTURE-CONTROL
           MOVE HC-INJECT-SUB-SQLCODE TO SQLCODE
           GOBACK.
      *
      *----------------------------------------------------------------*
      * Moves the seven host values into their capture slots, each as  *
      * received.                                                      *
      *----------------------------------------------------------------*
       CAPTURE-HOUSE-VALUES.
           MOVE DB2-POLICYNUM-INT   TO HC-HOU-POLICYNUM
           MOVE CA-H-PROPERTY-TYPE  TO HC-HOU-PROPERTY-TYPE
           MOVE DB2-H-BEDROOMS-SINT TO HC-HOU-BEDROOMS
           MOVE DB2-H-VALUE-INT     TO HC-HOU-VALUE
           MOVE CA-H-HOUSE-NAME     TO HC-HOU-HOUSE-NAME
           MOVE CA-H-HOUSE-NUMBER   TO HC-HOU-HOUSE-NUMBER
           MOVE CA-H-POSTCODE       TO HC-HOU-POSTCODE.
      *
      *----------------------------------------------------------------*
      * Marks the block captured, counts the execution, stamps the     *
      * ordinal from the shared event sequence and names the           *
      * statement. The order-guard items are not written here.         *
      *----------------------------------------------------------------*
       STAMP-CAPTURE-CONTROL.
           MOVE 'Y' TO HC-HOU-PRESENT
           ADD 1 TO HC-HOU-COUNT
           END-ADD
           ADD 1 TO HC-EVENT-SEQ
           END-ADD
           MOVE HC-EVENT-SEQ TO HC-HOU-SEQ
           MOVE 'insert_house' TO HC-ORDER-LAST-STMT.
