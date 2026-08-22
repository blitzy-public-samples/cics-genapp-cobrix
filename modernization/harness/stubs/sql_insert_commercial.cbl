      ******************************************************************
      *                                                                *
      *                   SQL-INSERT-COMMERCIAL                        *
      *                                                                *
      *   Harness stand-in for the INSERT INTO COMMERCIAL statement    *
      *   of the translated LGAPDB01                                   *
      *                                                                *
      ******************************************************************
      *
      * Emulates the SQL block at [base/src/lgapdb01.cbl:499-545] in
      * paragraph INSERT-COMMERCIAL. The translated LGAPDB01 calls this
      * module in place of that block and passes the twenty host
      * variables of the block BY REFERENCE in source order, as
      * recorded by the dml entry insert_commercial of
      * modernization/harness/statement_map.yml. The block is reached
      * on request id '01ACOM' [base/src/lgapdb01.cbl:234-235].
      *
      * The nine integer hosts at positions 11 to 19 are loaded from
      * their CA-B counterparts by the nine MOVE statements at
      * [base/src/lgapdb01.cbl:488-496]. Three column names differ from
      * the COBOL item paired with them: CA-LASTCHANGED supplies
      * RequestDate at [base/src/lgapdb01.cbl:525], CA-B-Postcode
      * supplies Zipcode at [base/src/lgapdb01.cbl:529] and
      * CA-B-RejectReason supplies RejectionReason at
      * [base/src/lgapdb01.cbl:543].
      *
      * Parameters, each with the COMMERCIAL column it is paired with.
      * The capture item that witnesses each one is named against its
      * LINKAGE declaration below and is the receiving field of the
      * matching statement in CAPTURE-COMMERCIAL-VALUES.
      *    1  DB2-POLICYNUM-INT         PolicyNumber
      *    2  CA-LASTCHANGED            RequestDate
      *    3  CA-ISSUE-DATE             StartDate
      *    4  CA-EXPIRY-DATE            RenewalDate
      *    5  CA-B-Address              Address
      *    6  CA-B-Postcode             Zipcode
      *    7  CA-B-Latitude             LatitudeN
      *    8  CA-B-Longitude            LongitudeW
      *    9  CA-B-Customer             Customer
      *   10  CA-B-PropType             PropertyType
      *   11  DB2-B-FirePeril-Int       FirePeril
      *   12  DB2-B-FirePremium-Int     FirePremium
      *   13  DB2-B-CrimePeril-Int      CrimePeril
      *   14  DB2-B-CrimePremium-Int    CrimePremium
      *   15  DB2-B-FloodPeril-Int      FloodPeril
      *   16  DB2-B-FloodPremium-Int    FloodPremium
      *   17  DB2-B-WeatherPeril-Int    WeatherPeril
      *   18  DB2-B-WeatherPremium-Int  WeatherPremium
      *   19  DB2-B-Status-Int          Status
      *   20  CA-B-RejectReason         RejectionReason
      *
      * Every value is recorded exactly as received, with no trimming,
      * reformatting or scaling, and no value is derived from any
      * parameter. The four premiums at positions 12, 14, 16 and 18 are
      * recorded as passed and reach
      * canonical.preissued_rating.fire_premium_amount,
      * crime_premium_amount, flood_premium_amount and
      * weather_premium_amount. The four peril codes at positions 11,
      * 13, 15 and 17 are recorded as passed and are not amount fields;
      * they map to no canonical column. Position 19 carries Status and
      * is likewise not an amount field.
      *
      * Position 2 witnesses CA-LASTCHANGED, which only the read-back
      * at [base/src/lgapdb01.cbl:316-321] populates. That read-back
      * runs inside INSERT-POLICY, performed at
      * [base/src/lgapdb01.cbl:219] ahead of INSERT-COMMERCIAL at
      * [base/src/lgapdb01.cbl:235]. The parameter is recorded
      * unconditionally and in full, whatever it holds. The seed item
      * HC-SEED-LASTCHANGED is neither read nor written here.
      *
      * Capture control, following the contract stated by
      * modernization/harness/copybooks/hcapture.cpy: HC-COM-PRESENT
      * becomes 'Y', HC-COM-COUNT counts the executions of the block,
      * HC-EVENT-SEQ is advanced and its new value is stamped into
      * HC-COM-SEQ, and HC-ORDER-LAST-STMT receives this statement's
      * key insert_commercial.
      *
      * insert_commercial is the successor of the execution_order entry
      * lastchanged_before_commercial of
      * modernization/harness/statement_map.yml, whose predecessor
      * ordinal is HC-LCHG-SEQ: the read-back that ordinal stamps is
      * the only statement that populates the CA-LASTCHANGED of
      * position 2 and is the last EXEC SQL block of paragraph
      * INSERT-POLICY, performed at [base/src/lgapdb01.cbl:219] ahead
      * of INSERT-COMMERCIAL at [base/src/lgapdb01.cbl:235]. A non-zero
      * HC-LCHG-SEQ therefore also stands for the identity recovery at
      * [base/src/lgapdb01.cbl:307-311] and for the POLICY insert at
      * [base/src/lgapdb01.cbl:268-288] ahead of both. This module
      * reads that ordinal after stamping its own. An HC-LCHG-SEQ still
      * at zero reports the constraint as violated in
      * HC-ORDER-VIOLATION and HC-ORDER-VIOLATION-STMT; a non-zero
      * HC-LCHG-SEQ leaves both items as the driver set them. Each of
      * the seven other members of modernization/harness/stubs/ that
      * carries an ordering constraint of the read-only source tests it
      * in this same shape and writes the same two items:
      * sql_insert_policy.cbl, sql_set_identity.cbl,
      * sql_select_lastchanged.cbl, sql_insert_motor.cbl,
      * sql_insert_endowment.cbl, sql_insert_house.cbl and
      * cics_write.cbl. Where more than one of them reports,
      * HC-ORDER-VIOLATION-STMT names the one that reported last and
      * HC-ORDER-VIOLATION stays at 'Y'.
      * modernization/harness/translate.py reconciles every one of
      * those guards with the entry the map declares for it on every
      * run.
      *
      * The execution_order block of
      * modernization/harness/statement_map.yml declares eight ordering
      * constraints, and each names in its enforced_by field the one
      * stub that tests it at run time. This module is the enforced_by
      * module of lastchanged_before_commercial, the constraint the
      * guard above tests: predecessor select_lastchanged, successor
      * insert_commercial, reason_kind data_dependency on
      * CA-LASTCHANGED, witness ordinals HC-LCHG-SEQ and HC-COM-SEQ.
      *
      * The ordinal stamped here is read by one further constraint that
      * this module does not enforce,
      * policy_and_product_before_vsam_write: HC-COM-SEQ is one of the
      * four alternative product predecessors its
      * predecessor_ordinal_items_any names, beside HC-MOT-SEQ,
      * HC-END-SEQ and HC-HOU-SEQ, its predecessor_ordinal_item is
      * HC-POL-SEQ, its successor is the KSDSPOLY write at
      * [base/src/lgapvs01.cbl:135-141], and
      * modernization/harness/stubs/cics_write.cbl is its enforced_by
      * module. The other six constraints name neither insert_commercial
      * nor HC-COM-SEQ.
      *
      * SQLCODE of the shared SQLCA reports HC-INJECT-SUB-SQLCODE on
      * every call. The translated LGAPDB01 tests it with IF SQLCODE
      * NOT EQUAL 0 at [base/src/lgapdb01.cbl:547]; zero leaves the
      * '90' move at [base/src/lgapdb01.cbl:548], the diagnostic write
      * at [base/src/lgapdb01.cbl:549] and the ABEND ABCODE('LGSQ') at
      * [base/src/lgapdb01.cbl:551] unexecuted, and any other value
      * takes all three and the return at
      * [base/src/lgapdb01.cbl:552]. The twenty host values, the
      * capture control items and the order test are recorded before
      * the code is reported, on both paths: the block executed
      * whatever it then reported.
      *
      * No item of the caller's COMMAREA is addressed here, no
      * parameter is assigned to, and no capture item outside
      * HC-SQL-COMMERCIAL, HC-EVENT-SEQ and the HC-ORDER items named
      * above is written. HC-INJECT-SUB-SQLCODE is read here and never
      * written. The shared group is never initialised here.
      *
      * Rationale for the reported SQLCODE, for recording the
      * premiums as passed, for excluding the peril codes from the
      * canonical schema, for the amount comparison tolerance, for the
      * order guard and for the arity of twenty belongs to
      * modernization/docs/decision-log.md, rows: deterministic failure
      * injection through shared harness state; uniform stub-side
      * capture-order guard.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SQL-INSERT-COMMERCIAL.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      * Shared capture state. This module writes the COMMERCIAL group,
      * the shared event sequence and the order items, and reads the
      * injected SQLCODE.
       COPY HCAPTURE.
      *
      * Shared SQL communications area read by the translated LGAPDB01.
       COPY HSQLCA.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N                             *
      ******************************************************************
      * The twenty host variables of [base/src/lgapdb01.cbl:499-545],
      * in the source order of the block, which is the order the dml
      * entry insert_commercial of
      * modernization/harness/statement_map.yml records. Shapes follow
      * the declarations cited against each item. The source spells
      * several of these names in mixed case and they are transcribed
      * as spelled.
       LINKAGE SECTION.
      *
      * Slot 1, column PolicyNumber. DB2-POLICYNUM-INT
      * [base/src/lgapdb01.cbl:117], holding the identity assigned for
      * [base/src/lgapdb01.cbl:308-310], as passed by
      * [base/src/lgapdb01.cbl:524]. Recorded in HC-COM-POLICYNUM.
       01  DB2-POLICYNUM-INT         PIC S9(9) COMP.
      *
      * Slot 2, column RequestDate. CA-LASTCHANGED
      * [base/src/lgcmarea.cpy:40], as passed by
      * [base/src/lgapdb01.cbl:525]. All 26 characters are recorded in
      * HC-COM-LASTCHANGED.
       01  CA-LASTCHANGED            PIC X(26).
      *
      * Slot 3, column StartDate. CA-ISSUE-DATE
      * [base/src/lgcmarea.cpy:38], as passed by
      * [base/src/lgapdb01.cbl:526]. Recorded in HC-COM-ISSUE-DATE.
       01  CA-ISSUE-DATE             PIC X(10).
      *
      * Slot 4, column RenewalDate. CA-EXPIRY-DATE
      * [base/src/lgcmarea.cpy:39], as passed by
      * [base/src/lgapdb01.cbl:527]. Recorded in HC-COM-EXPIRY-DATE.
       01  CA-EXPIRY-DATE            PIC X(10).
      *
      * Slot 5, column Address. CA-B-Address
      * [base/src/lgcmarea.cpy:78], as passed by
      * [base/src/lgapdb01.cbl:528]. Recorded in HC-COM-ADDRESS with
      * its trailing spaces intact.
       01  CA-B-Address              PIC X(255).
      *
      * Slot 6, column Zipcode. CA-B-Postcode
      * [base/src/lgcmarea.cpy:79], as passed by
      * [base/src/lgapdb01.cbl:529]. Recorded in HC-COM-POSTCODE.
       01  CA-B-Postcode             PIC X(8).
      *
      * Slot 7, column LatitudeN. CA-B-Latitude
      * [base/src/lgcmarea.cpy:80], as passed by
      * [base/src/lgapdb01.cbl:530]. Recorded in HC-COM-LATITUDE.
       01  CA-B-Latitude             PIC X(11).
      *
      * Slot 8, column LongitudeW. CA-B-Longitude
      * [base/src/lgcmarea.cpy:81], as passed by
      * [base/src/lgapdb01.cbl:531]. Recorded in HC-COM-LONGITUDE.
       01  CA-B-Longitude            PIC X(11).
      *
      * Slot 9, column Customer. CA-B-Customer
      * [base/src/lgcmarea.cpy:82], as passed by
      * [base/src/lgapdb01.cbl:532]. Recorded in HC-COM-CUSTOMER with
      * its trailing spaces intact.
       01  CA-B-Customer             PIC X(255).
      *
      * Slot 10, column PropertyType. CA-B-PropType
      * [base/src/lgcmarea.cpy:83], as passed by
      * [base/src/lgapdb01.cbl:533]. Recorded in HC-COM-PROPTYPE with
      * its trailing spaces intact.
       01  CA-B-PropType             PIC X(255).
      *
      * Slot 11, column FirePeril. DB2-B-FirePeril-Int
      * [base/src/lgapdb01.cbl:102], loaded from CA-B-FirePeril
      * PIC 9(4) [base/src/lgcmarea.cpy:84] by the MOVE at
      * [base/src/lgapdb01.cbl:488], as passed by
      * [base/src/lgapdb01.cbl:534]. Recorded in HC-COM-FIREPERIL. A
      * peril code, not an amount field.
       01  DB2-B-FirePeril-Int       PIC S9(4) COMP.
      *
      * Slot 12, column FirePremium. DB2-B-FirePremium-Int
      * [base/src/lgapdb01.cbl:103], loaded from CA-B-FirePremium
      * PIC 9(8) [base/src/lgcmarea.cpy:85] by the MOVE at
      * [base/src/lgapdb01.cbl:489], as passed by
      * [base/src/lgapdb01.cbl:535]. Recorded in HC-COM-FIREPREMIUM as
      * passed and compared against
      * canonical.preissued_rating.fire_premium_amount.
       01  DB2-B-FirePremium-Int     PIC S9(9) COMP.
      *
      * Slot 13, column CrimePeril. DB2-B-CrimePeril-Int
      * [base/src/lgapdb01.cbl:104], loaded from CA-B-CrimePeril
      * PIC 9(4) [base/src/lgcmarea.cpy:86] by the MOVE at
      * [base/src/lgapdb01.cbl:490], as passed by
      * [base/src/lgapdb01.cbl:536]. Recorded in HC-COM-CRIMEPERIL. A
      * peril code, not an amount field.
       01  DB2-B-CrimePeril-Int      PIC S9(4) COMP.
      *
      * Slot 14, column CrimePremium. DB2-B-CrimePremium-Int
      * [base/src/lgapdb01.cbl:105], loaded from CA-B-CrimePremium
      * PIC 9(8) [base/src/lgcmarea.cpy:87] by the MOVE at
      * [base/src/lgapdb01.cbl:491], as passed by
      * [base/src/lgapdb01.cbl:537]. Recorded in HC-COM-CRIMEPREMIUM as
      * passed and compared against
      * canonical.preissued_rating.crime_premium_amount.
       01  DB2-B-CrimePremium-Int    PIC S9(9) COMP.
      *
      * Slot 15, column FloodPeril. DB2-B-FloodPeril-Int
      * [base/src/lgapdb01.cbl:106], loaded from CA-B-FloodPeril
      * PIC 9(4) [base/src/lgcmarea.cpy:88] by the MOVE at
      * [base/src/lgapdb01.cbl:492], as passed by
      * [base/src/lgapdb01.cbl:538]. Recorded in HC-COM-FLOODPERIL. A
      * peril code, not an amount field.
       01  DB2-B-FloodPeril-Int      PIC S9(4) COMP.
      *
      * Slot 16, column FloodPremium. DB2-B-FloodPremium-Int
      * [base/src/lgapdb01.cbl:107], loaded from CA-B-FloodPremium
      * PIC 9(8) [base/src/lgcmarea.cpy:89] by the MOVE at
      * [base/src/lgapdb01.cbl:493], as passed by
      * [base/src/lgapdb01.cbl:539]. Recorded in HC-COM-FLOODPREMIUM as
      * passed and compared against
      * canonical.preissued_rating.flood_premium_amount.
       01  DB2-B-FloodPremium-Int    PIC S9(9) COMP.
      *
      * Slot 17, column WeatherPeril. DB2-B-WeatherPeril-Int
      * [base/src/lgapdb01.cbl:108], loaded from CA-B-WeatherPeril
      * PIC 9(4) [base/src/lgcmarea.cpy:90] by the MOVE at
      * [base/src/lgapdb01.cbl:494], as passed by
      * [base/src/lgapdb01.cbl:540]. Recorded in HC-COM-WEATHERPERIL. A
      * peril code, not an amount field.
       01  DB2-B-WeatherPeril-Int    PIC S9(4) COMP.
      *
      * Slot 18, column WeatherPremium. DB2-B-WeatherPremium-Int
      * [base/src/lgapdb01.cbl:109], loaded from CA-B-WeatherPremium
      * PIC 9(8) [base/src/lgcmarea.cpy:91] by the MOVE at
      * [base/src/lgapdb01.cbl:495], as passed by
      * [base/src/lgapdb01.cbl:541]. Recorded in
      * HC-COM-WEATHERPREMIUM as passed and compared against
      * canonical.preissued_rating.weather_premium_amount.
       01  DB2-B-WeatherPremium-Int  PIC S9(9) COMP.
      *
      * Slot 19, column Status. DB2-B-Status-Int
      * [base/src/lgapdb01.cbl:110], loaded from CA-B-Status PIC 9(4)
      * [base/src/lgcmarea.cpy:92] by the MOVE at
      * [base/src/lgapdb01.cbl:496], as passed by
      * [base/src/lgapdb01.cbl:542]. Recorded in HC-COM-STATUS. Not an
      * amount field.
       01  DB2-B-Status-Int          PIC S9(4) COMP.
      *
      * Slot 20, column RejectionReason. CA-B-RejectReason
      * [base/src/lgcmarea.cpy:93], as passed by
      * [base/src/lgapdb01.cbl:543]. Recorded in HC-COM-REJECTREASON
      * with its trailing spaces intact.
       01  CA-B-RejectReason         PIC X(255).
      *
      ******************************************************************
      *    P R O C E D U R E S                                         *
      ******************************************************************
       PROCEDURE DIVISION USING DB2-POLICYNUM-INT
                                CA-LASTCHANGED
                                CA-ISSUE-DATE
                                CA-EXPIRY-DATE
                                CA-B-Address
                                CA-B-Postcode
                                CA-B-Latitude
                                CA-B-Longitude
                                CA-B-Customer
                                CA-B-PropType
                                DB2-B-FirePeril-Int
                                DB2-B-FirePremium-Int
                                DB2-B-CrimePeril-Int
                                DB2-B-CrimePremium-Int
                                DB2-B-FloodPeril-Int
                                DB2-B-FloodPremium-Int
                                DB2-B-WeatherPeril-Int
                                DB2-B-WeatherPremium-Int
                                DB2-B-Status-Int
                                CA-B-RejectReason.
      *
      *----------------------------------------------------------------*
      * Records the block, stamps its capture control items, tests the *
      * declared predecessor ordinal and reports the SQLCODE this run  *
      * selected to the caller.                                        *
      *----------------------------------------------------------------*
       MAINLINE.
           PERFORM CAPTURE-COMMERCIAL-VALUES
           PERFORM STAMP-CAPTURE-CONTROL
           PERFORM CHECK-CAPTURE-ORDER
           MOVE HC-INJECT-SUB-SQLCODE TO SQLCODE
           GOBACK.
      *
      *----------------------------------------------------------------*
      * Moves the twenty host values into their capture slots, in the  *
      * order the block passes them. Each value is transferred as it   *
      * stands and under no condition. Every receiving slot carries    *
      * the same picture as its parameter. The four premiums at slots  *
      * 12, 14, 16 and 18, the four peril codes at slots 11, 13, 15    *
      * and 17 and the character fields are recorded unaltered,        *
      * padding included.                                              *
      *----------------------------------------------------------------*
       CAPTURE-COMMERCIAL-VALUES.
           MOVE DB2-POLICYNUM-INT        TO HC-COM-POLICYNUM
           MOVE CA-LASTCHANGED           TO HC-COM-LASTCHANGED
           MOVE CA-ISSUE-DATE            TO HC-COM-ISSUE-DATE
           MOVE CA-EXPIRY-DATE           TO HC-COM-EXPIRY-DATE
           MOVE CA-B-Address             TO HC-COM-ADDRESS
           MOVE CA-B-Postcode            TO HC-COM-POSTCODE
           MOVE CA-B-Latitude            TO HC-COM-LATITUDE
           MOVE CA-B-Longitude           TO HC-COM-LONGITUDE
           MOVE CA-B-Customer            TO HC-COM-CUSTOMER
           MOVE CA-B-PropType            TO HC-COM-PROPTYPE
           MOVE DB2-B-FirePeril-Int      TO HC-COM-FIREPERIL
           MOVE DB2-B-FirePremium-Int    TO HC-COM-FIREPREMIUM
           MOVE DB2-B-CrimePeril-Int     TO HC-COM-CRIMEPERIL
           MOVE DB2-B-CrimePremium-Int   TO HC-COM-CRIMEPREMIUM
           MOVE DB2-B-FloodPeril-Int     TO HC-COM-FLOODPERIL
           MOVE DB2-B-FloodPremium-Int   TO HC-COM-FLOODPREMIUM
           MOVE DB2-B-WeatherPeril-Int   TO HC-COM-WEATHERPERIL
           MOVE DB2-B-WeatherPremium-Int TO HC-COM-WEATHERPREMIUM
           MOVE DB2-B-Status-Int         TO HC-COM-STATUS
           MOVE CA-B-RejectReason        TO HC-COM-REJECTREASON.
      *
      *----------------------------------------------------------------*
      * Marks the block captured, counts the execution, stamps the     *
      * ordinal from the shared event sequence and names the           *
      * statement with its statement_map.yml key.                      *
      *----------------------------------------------------------------*
       STAMP-CAPTURE-CONTROL.
           MOVE 'Y'                 TO HC-COM-PRESENT
           ADD  1                   TO HC-COM-COUNT
           END-ADD
           ADD  1                   TO HC-EVENT-SEQ
           END-ADD
           MOVE HC-EVENT-SEQ        TO HC-COM-SEQ
           MOVE 'insert_commercial' TO HC-ORDER-LAST-STMT.
      *
      *----------------------------------------------------------------*
      * Tests the predecessor ordinal of the declared constraint       *
      * lastchanged_before_commercial, read after this block stamped   *
      * its own ordinal. HC-LCHG-SEQ at zero reports that the SELECT   *
      * LASTCHANGED read-back at [base/src/lgapdb01.cbl:316-321] was   *
      * not captured before this block, so the CA-LASTCHANGED of       *
      * [base/src/lgapdb01.cbl:525] is unpopulated. A non-zero         *
      * HC-LCHG-SEQ leaves both order items as the driver set them.    *
      * The seven other stubs that carry a source-derived predecessor  *
      * test theirs in this same shape.                                *
      *----------------------------------------------------------------*
       CHECK-CAPTURE-ORDER.
           IF HC-LCHG-SEQ = ZERO
               MOVE 'Y' TO HC-ORDER-VIOLATION
               MOVE 'insert_commercial' TO HC-ORDER-VIOLATION-STMT
           END-IF.
      *----------------------------------------------------------------*
