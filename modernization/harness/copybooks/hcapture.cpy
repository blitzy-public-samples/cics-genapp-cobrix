      ******************************************************************
      *                                                                *
      *                       HCAPTURE                                 *
      *                                                                *
      *   Shared capture state for the GnuCOBOL validation harness     *
      *                                                                *
      ******************************************************************
      *
      * Records what the translated Policy-Issue chain handed to each
      * emulated service. The SQL groups hold the host-variable values
      * the translated LGAPDB01 passed to each INSERT, SET and SELECT
      * block. The VSAM group holds the record, key, lengths and
      * response of the KSDSPOLY write issued by the translated
      * LGAPVS01. The abend and diagnostic-link items hold the failure
      * signals raised by any of the three translated programs.
      *
      * modernization/validation/diff_harness_vs_warehouse.py reads
      * these values, as emitted by the driver, and compares them with
      * canonical.issued_policy and canonical.preissued_rating.
      *
      * COPYed by modernization/harness/driver.cbl and by the twelve
      * members of modernization/harness/stubs/. It is not inserted
      * into the three translated programs. translate.py copies this
      * member verbatim into the generated build tree; it is never
      * preprocessed in place.
      *
      * One 01 group carries the EXTERNAL clause, so every compilation
      * unit that COPYs this member addresses the same storage.
      *
      * No item is initialised here: this member declares no VALUE
      * clause on any data item. modernization/harness/driver.cbl
      * initialises the whole group procedurally before each case. The
      * level-88 entries below name conditions and allocate no storage.
      *
      * Each presence flag holds 'N' before its statement has been
      * captured and 'Y' afterwards; each counter starts at zero.
      * modernization/harness/driver.cbl moves those two states into
      * every flag and counter at the start of each case.
      *
      * Statement arities are fixed by the checks.using_counts block
      * of modernization/harness/statement_map.yml: insert_policy 7,
      * set_identity 1, select_lastchanged 2, insert_endowment 9,
      * insert_house 7, insert_motor 10, insert_commercial 20, giving
      * 56 host-variable slots. Capture is per statement and is not
      * deduplicated: each product group holds its own policy-number
      * item.
      *
      * Rationale is recorded in modernization/docs/decision-log.md,
      * rows: shared EXTERNAL harness state; HC- capture prefix;
      * commercial peril-code capture without canonical mapping;
      * flat VSAM payload capture.
      *
      * Harness topology: Figure 5 "Validation Harness Control Flow"
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       01  HC-CAPTURE-STATE EXTERNAL.
      *
      *================================================================*
      * Deterministic seeds supplied by the driver                     *
      *================================================================*
      * The two items below hold the values the driver supplies to the
      * chain. The values the stubs record are held in the SQL groups
      * that follow: the assigned identity that reaches CA-POLICY-NUM
      * at [base/src/lgapdb01.cbl:311], and the timestamp read back at
      * [base/src/lgapdb01.cbl:316-321].
      * modernization/harness/run_harness.sh exports
      * HARNESS_POLICY_NUMBER and HARNESS_LASTCHANGED;
      * modernization/harness/driver.cbl reads them into these items.
           03 HC-SEED.
      *
      * Identity that sql_set_identity.cbl returns to the translated
      * LGAPDB01 in place of IDENTITY_VAL_LOCAL()
      * [base/src/lgapdb01.cbl:308-310]. Shape follows the receiving
      * host variable DB2-POLICYNUM-INT [base/src/lgapdb01.cbl:117].
              05 HC-SEED-POLICYNUM        PIC S9(9) COMP.
      *
      * Timestamp that sql_select_lastchanged.cbl returns for the
      * LASTCHANGED read-back [base/src/lgapdb01.cbl:316-321]. Shape
      * follows CA-LASTCHANGED [base/src/lgcmarea.cpy:40].
              05 HC-SEED-LASTCHANGED      PIC X(26).
      *
      *================================================================*
      * SQL: INSERT INTO POLICY                                        *
      *   paragraph INSERT-POLICY, block [base/src/lgapdb01.cbl:       *
      *   268-288]. Arity 7.                                           *
      *================================================================*
      * Columns POLICYNUMBER and LASTCHANGED take no host variable:
      * the source supplies DEFAULT at [base/src/lgapdb01.cbl:279] and
      * CURRENT TIMESTAMP at [base/src/lgapdb01.cbl:284]. Neither is
      * captured here. The assigned key and timestamp are recorded by
      * the SET-IDENTITY and SELECT-LASTCHANGED groups below.
           03 HC-SQL-POLICY.
      *
      * Set to 'Y' by sql_insert_policy.cbl when the block executes.
              05 HC-POL-PRESENT           PIC X.
                 88 HC-POL-CAPTURED       VALUE 'Y'.
                 88 HC-POL-MISSING        VALUE 'N'.
      *
      * Number of times the block executed. One execution is expected
      * per case; the value also orders this block ahead of
      * INSERT-COMMERCIAL, which consumes CA-LASTCHANGED at
      * [base/src/lgapdb01.cbl:525].
              05 HC-POL-COUNT             PIC 9(4).
      *
      * Slot 1, column CUSTOMERNUMBER. Witnesses DB2-CUSTOMERNUM-INT
      * [base/src/lgapdb01.cbl:90], loaded from CA-CUSTOMER-NUM
      * PIC 9(10) [base/src/lgcmarea.cpy:12] by the MOVE at
      * [base/src/lgapdb01.cbl:176]. Nine digits, as received.
              05 HC-POL-CUSTOMERNUM       PIC S9(9) COMP.
      *
      * Slot 2, column ISSUEDATE. Witnesses CA-ISSUE-DATE
      * [base/src/lgcmarea.cpy:38].
              05 HC-POL-ISSUE-DATE        PIC X(10).
      *
      * Slot 3, column EXPIRYDATE. Witnesses CA-EXPIRY-DATE
      * [base/src/lgcmarea.cpy:39].
              05 HC-POL-EXPIRY-DATE       PIC X(10).
      *
      * Slot 4, column POLICYTYPE. Witnesses DB2-POLICYTYPE
      * [base/src/lgpolicy.cpy:43], set to 'E', 'H', 'M' or 'C' by the
      * request routing at [base/src/lgapdb01.cbl:184-207].
              05 HC-POL-POLICYTYPE        PIC X.
      *
      * Slot 5, column BROKERID. Witnesses DB2-BROKERID-INT
      * [base/src/lgapdb01.cbl:91], loaded from CA-BROKERID PIC 9(10)
      * [base/src/lgcmarea.cpy:41] by the MOVE at
      * [base/src/lgapdb01.cbl:264]. Nine digits, as received.
              05 HC-POL-BROKERID          PIC S9(9) COMP.
      *
      * Slot 6, column BROKERSREFERENCE. Witnesses CA-BROKERSREF
      * [base/src/lgcmarea.cpy:42].
              05 HC-POL-BROKERSREF        PIC X(10).
      *
      * Slot 7, column PAYMENT. Witnesses DB2-PAYMENT-INT
      * [base/src/lgapdb01.cbl:92], loaded from CA-PAYMENT PIC 9(6)
      * [base/src/lgcmarea.cpy:43] by the MOVE at
      * [base/src/lgapdb01.cbl:265].
              05 HC-POL-PAYMENT           PIC S9(9) COMP.
      *
      *================================================================*
      * SQL: SET :DB2-POLICYNUM-INT = IDENTITY_VAL_LOCAL()             *
      *   paragraph INSERT-POLICY, block [base/src/lgapdb01.cbl:       *
      *   308-310]. Arity 1, direction out.                            *
      *================================================================*
           03 HC-SQL-SET-IDENTITY.
      *
      * Set to 'Y' by sql_set_identity.cbl when the block executes.
              05 HC-IDENT-PRESENT         PIC X.
                 88 HC-IDENT-CAPTURED     VALUE 'Y'.
                 88 HC-IDENT-MISSING      VALUE 'N'.
      *
      * Number of times the block executed.
              05 HC-IDENT-COUNT           PIC 9(4).
      *
      * Slot 1, the assigned identity. Witnesses DB2-POLICYNUM-INT
      * [base/src/lgapdb01.cbl:117] as returned to the translated
      * program, which then moves it to CA-POLICY-NUM
      * [base/src/lgcmarea.cpy:35] at [base/src/lgapdb01.cbl:311].
              05 HC-IDENT-POLICYNUM       PIC S9(9) COMP.
      *
      *================================================================*
      * SQL: SELECT LASTCHANGED read-back                              *
      *   paragraph INSERT-POLICY, block [base/src/lgapdb01.cbl:       *
      *   316-321]. Arity 2, in the source order of the block: the     *
      *   INTO target first, then the WHERE predicate host.            *
      *================================================================*
           03 HC-SQL-SELECT-LASTCHANGED.
      *
      * Set to 'Y' by sql_select_lastchanged.cbl when the block
      * executes.
              05 HC-LCHG-PRESENT          PIC X.
                 88 HC-LCHG-CAPTURED      VALUE 'Y'.
                 88 HC-LCHG-MISSING       VALUE 'N'.
      *
      * Number of times the block executed.
              05 HC-LCHG-COUNT            PIC 9(4).
      *
      * Slot 1, column LASTCHANGED, direction out. Witnesses
      * CA-LASTCHANGED [base/src/lgcmarea.cpy:40] as returned into the
      * COMMAREA by [base/src/lgapdb01.cbl:318]. This block is the only
      * one that populates CA-LASTCHANGED.
              05 HC-LCHG-LASTCHANGED      PIC X(26).
      *
      * Slot 2, column POLICYNUMBER, the WHERE predicate host.
      * Witnesses DB2-POLICYNUM-INT [base/src/lgapdb01.cbl:117] as read
      * by [base/src/lgapdb01.cbl:320].
              05 HC-LCHG-POLICYNUM        PIC S9(9) COMP.
      *
      *================================================================*
      * SQL: INSERT INTO MOTOR                                         *
      *   paragraph INSERT-MOTOR, block [base/src/lgapdb01.cbl:        *
      *   449-471]. Arity 10. Reached on request id '01AMOT'           *
      *   [base/src/lgapdb01.cbl:231-232].                             *
      *================================================================*
      * The four integer hosts are loaded from their CA-M counterparts
      * by the MOVE statements at [base/src/lgapdb01.cbl:443-446].
           03 HC-SQL-MOTOR.
      *
      * Set to 'Y' by sql_insert_motor.cbl when the block executes.
              05 HC-MOT-PRESENT           PIC X.
                 88 HC-MOT-CAPTURED       VALUE 'Y'.
                 88 HC-MOT-MISSING        VALUE 'N'.
      *
      * Number of times the block executed.
              05 HC-MOT-COUNT             PIC 9(4).
      *
      * Slot 1, column POLICYNUMBER. Witnesses DB2-POLICYNUM-INT
      * [base/src/lgapdb01.cbl:117] as passed by
      * [base/src/lgapdb01.cbl:461]. Held per statement, so the
      * recovered identity can be compared against the value the
      * SET-IDENTITY group recorded.
              05 HC-MOT-POLICYNUM         PIC S9(9) COMP.
      *
      * Slot 2, column MAKE. Witnesses CA-M-MAKE
      * [base/src/lgcmarea.cpy:66].
              05 HC-MOT-MAKE              PIC X(15).
      *
      * Slot 3, column MODEL. Witnesses CA-M-MODEL
      * [base/src/lgcmarea.cpy:67].
              05 HC-MOT-MODEL             PIC X(15).
      *
      * Slot 4, column VALUE. Witnesses DB2-M-VALUE-INT
      * [base/src/lgapdb01.cbl:98], loaded from CA-M-VALUE PIC 9(6)
      * [base/src/lgcmarea.cpy:68] at [base/src/lgapdb01.cbl:443].
              05 HC-MOT-VALUE             PIC S9(9) COMP.
      *
      * Slot 5, column REGNUMBER. Witnesses CA-M-REGNUMBER
      * [base/src/lgcmarea.cpy:69].
              05 HC-MOT-REGNUMBER         PIC X(7).
      *
      * Slot 6, column COLOUR. Witnesses CA-M-COLOUR
      * [base/src/lgcmarea.cpy:70].
              05 HC-MOT-COLOUR            PIC X(8).
      *
      * Slot 7, column CC. Witnesses DB2-M-CC-SINT
      * [base/src/lgapdb01.cbl:99], loaded from CA-M-CC PIC 9(4)
      * [base/src/lgcmarea.cpy:71] at [base/src/lgapdb01.cbl:444].
              05 HC-MOT-CC                PIC S9(4) COMP.
      *
      * Slot 8, column YEAROFMANUFACTURE. Witnesses CA-M-MANUFACTURED
      * [base/src/lgcmarea.cpy:72].
              05 HC-MOT-MANUFACTURED      PIC X(10).
      *
      * Slot 9, column PREMIUM. Witnesses DB2-M-PREMIUM-INT
      * [base/src/lgapdb01.cbl:100], loaded from CA-M-PREMIUM PIC 9(6)
      * [base/src/lgcmarea.cpy:73] at [base/src/lgapdb01.cbl:445].
      * Compared against canonical.preissued_rating.
      * motor_premium_amount.
              05 HC-MOT-PREMIUM           PIC S9(9) COMP.
      *
      * Slot 10, column ACCIDENTS. Witnesses DB2-M-ACCIDENTS-INT
      * [base/src/lgapdb01.cbl:101], loaded from CA-M-ACCIDENTS
      * PIC 9(6) [base/src/lgcmarea.cpy:74] at
      * [base/src/lgapdb01.cbl:446].
              05 HC-MOT-ACCIDENTS         PIC S9(9) COMP.
      *
      *================================================================*
      * SQL: INSERT INTO COMMERCIAL                                    *
      *   paragraph INSERT-COMMERCIAL, block [base/src/lgapdb01.cbl:   *
      *   499-545]. Arity 20. Reached on request id '01ACOM'           *
      *   [base/src/lgapdb01.cbl:234-235].                             *
      *================================================================*
      * The nine integer hosts are loaded from their CA-B counterparts
      * by the MOVE statements at [base/src/lgapdb01.cbl:488-496]. The
      * block's column names are transcribed as the source spells them
      * at [base/src/lgapdb01.cbl:502-521].
      * See modernization/docs/decision-log.md, row: commercial
      * peril-code capture without canonical mapping.
           03 HC-SQL-COMMERCIAL.
      *
      * Set to 'Y' by sql_insert_commercial.cbl when the block
      * executes.
              05 HC-COM-PRESENT           PIC X.
                 88 HC-COM-CAPTURED       VALUE 'Y'.
                 88 HC-COM-MISSING        VALUE 'N'.
      *
      * Number of times the block executed. Read together with
      * HC-POL-COUNT it shows that INSERT-POLICY ran first, which is
      * the ordering the CA-LASTCHANGED dependency requires.
              05 HC-COM-COUNT             PIC 9(4).
      *
      * Slot 1, column PolicyNumber. Witnesses DB2-POLICYNUM-INT
      * [base/src/lgapdb01.cbl:117] as passed by
      * [base/src/lgapdb01.cbl:524].
              05 HC-COM-POLICYNUM         PIC S9(9) COMP.
      *
      * Slot 2, column RequestDate. Witnesses CA-LASTCHANGED
      * [base/src/lgcmarea.cpy:40] as passed by
      * [base/src/lgapdb01.cbl:525], populated only by the read-back at
      * [base/src/lgapdb01.cbl:316-321].
              05 HC-COM-LASTCHANGED       PIC X(26).
      *
      * Slot 3, column StartDate. Witnesses CA-ISSUE-DATE
      * [base/src/lgcmarea.cpy:38].
              05 HC-COM-ISSUE-DATE        PIC X(10).
      *
      * Slot 4, column RenewalDate. Witnesses CA-EXPIRY-DATE
      * [base/src/lgcmarea.cpy:39].
              05 HC-COM-EXPIRY-DATE       PIC X(10).
      *
      * Slot 5, column Address. Witnesses CA-B-Address
      * [base/src/lgcmarea.cpy:78].
              05 HC-COM-ADDRESS           PIC X(255).
      *
      * Slot 6, column Zipcode. Witnesses CA-B-Postcode
      * [base/src/lgcmarea.cpy:79].
              05 HC-COM-POSTCODE          PIC X(8).
      *
      * Slot 7, column LatitudeN. Witnesses CA-B-Latitude
      * [base/src/lgcmarea.cpy:80].
              05 HC-COM-LATITUDE          PIC X(11).
      *
      * Slot 8, column LongitudeW. Witnesses CA-B-Longitude
      * [base/src/lgcmarea.cpy:81].
              05 HC-COM-LONGITUDE         PIC X(11).
      *
      * Slot 9, column Customer. Witnesses CA-B-Customer
      * [base/src/lgcmarea.cpy:82].
              05 HC-COM-CUSTOMER          PIC X(255).
      *
      * Slot 10, column PropertyType. Witnesses CA-B-PropType
      * [base/src/lgcmarea.cpy:83].
              05 HC-COM-PROPTYPE          PIC X(255).
      *
      * Slot 11, column FirePeril. Witnesses DB2-B-FirePeril-Int
      * [base/src/lgapdb01.cbl:102], loaded from CA-B-FirePeril
      * PIC 9(4) [base/src/lgcmarea.cpy:84] at
      * [base/src/lgapdb01.cbl:488].
              05 HC-COM-FIREPERIL         PIC S9(4) COMP.
      *
      * Slot 12, column FirePremium. Witnesses DB2-B-FirePremium-Int
      * [base/src/lgapdb01.cbl:103], loaded from CA-B-FirePremium
      * PIC 9(8) [base/src/lgcmarea.cpy:85] at
      * [base/src/lgapdb01.cbl:489]. Compared against
      * canonical.preissued_rating.fire_premium_amount.
              05 HC-COM-FIREPREMIUM       PIC S9(9) COMP.
      *
      * Slot 13, column CrimePeril. Witnesses DB2-B-CrimePeril-Int
      * [base/src/lgapdb01.cbl:104], loaded from CA-B-CrimePeril
      * PIC 9(4) [base/src/lgcmarea.cpy:86] at
      * [base/src/lgapdb01.cbl:490].
              05 HC-COM-CRIMEPERIL        PIC S9(4) COMP.
      *
      * Slot 14, column CrimePremium. Witnesses
      * DB2-B-CrimePremium-Int [base/src/lgapdb01.cbl:105], loaded
      * from CA-B-CrimePremium PIC 9(8) [base/src/lgcmarea.cpy:87] at
      * [base/src/lgapdb01.cbl:491]. Compared against
      * canonical.preissued_rating.crime_premium_amount.
              05 HC-COM-CRIMEPREMIUM      PIC S9(9) COMP.
      *
      * Slot 15, column FloodPeril. Witnesses DB2-B-FloodPeril-Int
      * [base/src/lgapdb01.cbl:106], loaded from CA-B-FloodPeril
      * PIC 9(4) [base/src/lgcmarea.cpy:88] at
      * [base/src/lgapdb01.cbl:492].
              05 HC-COM-FLOODPERIL        PIC S9(4) COMP.
      *
      * Slot 16, column FloodPremium. Witnesses
      * DB2-B-FloodPremium-Int [base/src/lgapdb01.cbl:107], loaded
      * from CA-B-FloodPremium PIC 9(8) [base/src/lgcmarea.cpy:89] at
      * [base/src/lgapdb01.cbl:493]. Compared against
      * canonical.preissued_rating.flood_premium_amount.
              05 HC-COM-FLOODPREMIUM      PIC S9(9) COMP.
      *
      * Slot 17, column WeatherPeril. Witnesses
      * DB2-B-WeatherPeril-Int [base/src/lgapdb01.cbl:108], loaded
      * from CA-B-WeatherPeril PIC 9(4) [base/src/lgcmarea.cpy:90] at
      * [base/src/lgapdb01.cbl:494].
              05 HC-COM-WEATHERPERIL      PIC S9(4) COMP.
      *
      * Slot 18, column WeatherPremium. Witnesses
      * DB2-B-WeatherPremium-Int [base/src/lgapdb01.cbl:109], loaded
      * from CA-B-WeatherPremium PIC 9(8) [base/src/lgcmarea.cpy:91]
      * at [base/src/lgapdb01.cbl:495]. Compared against
      * canonical.preissued_rating.weather_premium_amount.
              05 HC-COM-WEATHERPREMIUM    PIC S9(9) COMP.
      *
      * Slot 19, column Status. Witnesses DB2-B-Status-Int
      * [base/src/lgapdb01.cbl:110], loaded from CA-B-Status PIC 9(4)
      * [base/src/lgcmarea.cpy:92] at [base/src/lgapdb01.cbl:496].
              05 HC-COM-STATUS            PIC S9(4) COMP.
      *
      * Slot 20, column RejectionReason. Witnesses CA-B-RejectReason
      * [base/src/lgcmarea.cpy:93].
              05 HC-COM-REJECTREASON      PIC X(255).

      *
      *================================================================*
      * SQL: INSERT INTO ENDOWMENT                                     *
      *   paragraph INSERT-ENDOW, blocks [base/src/lgapdb01.cbl:       *
      *   346-366] and [base/src/lgapdb01.cbl:368-386]. Arity 9, the   *
      *   superset of the two source branches. Reached on request id   *
      *   '01AEND' [base/src/lgapdb01.cbl:225-226].                    *
      *================================================================*
      * The guard at [base/src/lgapdb01.cbl:342] selects the branch:
      * the 346-366 block carries all nine hosts, the 368-386 block
      * omits the ninth. The captured length in HC-END-VARY-LEN below
      * records which branch ran.
      * The two integer hosts are loaded from their CA-E counterparts
      * by the MOVE statements at [base/src/lgapdb01.cbl:330-331].
      * Request ids '01AMOT' and '01ACOM' leave this group at the state
      * driver.cbl initialised, and its presence flag reports 'N'.
           03 HC-SQL-ENDOWMENT.
      *
      * Set to 'Y' by sql_insert_endowment.cbl when either block
      * executes.
              05 HC-END-PRESENT           PIC X.
                 88 HC-END-CAPTURED       VALUE 'Y'.
                 88 HC-END-MISSING        VALUE 'N'.
      *
      * Number of times either block executed.
              05 HC-END-COUNT             PIC 9(4).
      *
      * Slot 1, column POLICYNUMBER. Witnesses DB2-POLICYNUM-INT
      * [base/src/lgapdb01.cbl:117] as passed by
      * [base/src/lgapdb01.cbl:357] or [base/src/lgapdb01.cbl:378].
              05 HC-END-POLICYNUM         PIC S9(9) COMP.
      *
      * Slot 2, column WITHPROFITS. Witnesses CA-E-WITH-PROFITS
      * [base/src/lgcmarea.cpy:47].
              05 HC-END-WITH-PROFITS      PIC X.
      *
      * Slot 3, column EQUITIES. Witnesses CA-E-EQUITIES
      * [base/src/lgcmarea.cpy:48].
              05 HC-END-EQUITIES          PIC X.
      *
      * Slot 4, column MANAGEDFUND. Witnesses CA-E-MANAGED-FUND
      * [base/src/lgcmarea.cpy:49].
              05 HC-END-MANAGED-FUND      PIC X.
      *
      * Slot 5, column FUNDNAME. Witnesses CA-E-FUND-NAME
      * [base/src/lgcmarea.cpy:50].
              05 HC-END-FUND-NAME         PIC X(10).
      *
      * Slot 6, column TERM. Witnesses DB2-E-TERM-SINT
      * [base/src/lgapdb01.cbl:93], loaded from CA-E-TERM PIC 99
      * [base/src/lgcmarea.cpy:51] at [base/src/lgapdb01.cbl:330].
              05 HC-END-TERM              PIC S9(4) COMP.
      *
      * Slot 7, column SUMASSURED. Witnesses DB2-E-SUMASSURED-INT
      * [base/src/lgapdb01.cbl:94], loaded from CA-E-SUM-ASSURED
      * PIC 9(6) [base/src/lgcmarea.cpy:52] at
      * [base/src/lgapdb01.cbl:331].
              05 HC-END-SUMASSURED        PIC S9(9) COMP.
      *
      * Slot 8, column LIFEASSURED. Witnesses CA-E-LIFE-ASSURED
      * [base/src/lgcmarea.cpy:53].
              05 HC-END-LIFE-ASSURED      PIC X(31).
      *
      * Slot 9, column PADDINGDATA. Witnesses the varchar host
      * structure WS-VARY-FIELD [base/src/lgapdb01.cbl:70-72], passed
      * by [base/src/lgapdb01.cbl:365] and absent from the
      * [base/src/lgapdb01.cbl:368-386] block. The source declares its
      * two parts at level 49, a Db2 varchar convention; they are held
      * here at levels 05 and 07 with the same pictures.
              05 HC-END-VARY-FIELD.
      *
      * Length half of the varchar host. Witnesses WS-VARY-LEN
      * [base/src/lgapdb01.cbl:71], computed by the SUBTRACT at
      * [base/src/lgapdb01.cbl:339-340] and tested at
      * [base/src/lgapdb01.cbl:342]. Zero or negative means the
      * 368-386 block ran and the character half carries no data.
                 07 HC-END-VARY-LEN       PIC S9(4) COMP.
      *
      * Character half of the varchar host. Witnesses WS-VARY-CHAR
      * [base/src/lgapdb01.cbl:72], filled from CA-E-PADDING-DATA
      * [base/src/lgcmarea.cpy:54] by the reference-modified MOVE at
      * [base/src/lgapdb01.cbl:344-345].
                 07 HC-END-VARY-CHAR      PIC X(3900).
      *
      *================================================================*
      * SQL: INSERT INTO HOUSE                                         *
      *   paragraph INSERT-HOUSE, block [base/src/lgapdb01.cbl:        *
      *   409-425]. Arity 7. Reached on request id '01AHOU'            *
      *   [base/src/lgapdb01.cbl:228-229].                             *
      *================================================================*
      * The two integer hosts are loaded from their CA-H counterparts
      * by the MOVE statements at [base/src/lgapdb01.cbl:405-406].
      * Request ids '01AMOT' and '01ACOM' leave this group at the state
      * driver.cbl initialised, and its presence flag reports 'N'.
           03 HC-SQL-HOUSE.
      *
      * Set to 'Y' by sql_insert_house.cbl when the block executes.
              05 HC-HOU-PRESENT           PIC X.
                 88 HC-HOU-CAPTURED       VALUE 'Y'.
                 88 HC-HOU-MISSING        VALUE 'N'.
      *
      * Number of times the block executed.
              05 HC-HOU-COUNT             PIC 9(4).
      *
      * Slot 1, column POLICYNUMBER. Witnesses DB2-POLICYNUM-INT
      * [base/src/lgapdb01.cbl:117] as passed by
      * [base/src/lgapdb01.cbl:418].
              05 HC-HOU-POLICYNUM         PIC S9(9) COMP.
      *
      * Slot 2, column PROPERTYTYPE. Witnesses CA-H-PROPERTY-TYPE
      * [base/src/lgcmarea.cpy:57].
              05 HC-HOU-PROPERTY-TYPE     PIC X(15).
      *
      * Slot 3, column BEDROOMS. Witnesses DB2-H-BEDROOMS-SINT
      * [base/src/lgapdb01.cbl:96], loaded from CA-H-BEDROOMS PIC 9(3)
      * [base/src/lgcmarea.cpy:58] at [base/src/lgapdb01.cbl:406].
              05 HC-HOU-BEDROOMS          PIC S9(4) COMP.
      *
      * Slot 4, column VALUE. Witnesses DB2-H-VALUE-INT
      * [base/src/lgapdb01.cbl:97], loaded from CA-H-VALUE PIC 9(8)
      * [base/src/lgcmarea.cpy:59] at [base/src/lgapdb01.cbl:405].
              05 HC-HOU-VALUE             PIC S9(9) COMP.
      *
      * Slot 5, column HOUSENAME. Witnesses CA-H-HOUSE-NAME
      * [base/src/lgcmarea.cpy:60].
              05 HC-HOU-HOUSE-NAME        PIC X(20).
      *
      * Slot 6, column HOUSENUMBER. Witnesses CA-H-HOUSE-NUMBER
      * [base/src/lgcmarea.cpy:61].
              05 HC-HOU-HOUSE-NUMBER      PIC X(4).
      *
      * Slot 7, column POSTCODE. Witnesses CA-H-POSTCODE
      * [base/src/lgcmarea.cpy:62].
              05 HC-HOU-POSTCODE          PIC X(8).

      *
      *================================================================*
      * VSAM: WRITE FILE('KSDSPOLY') record image                      *
      *   [base/src/lgapvs01.cbl:135-141], issued by the translated    *
      *   LGAPVS01 and recorded by cics_write.cbl.                     *
      *================================================================*
      * Mirrors the nested structure WF-Policy-Info
      * [base/src/lgapvs01.cbl:25-30] at the same relative depth, so
      * this one group supplies both the 64-byte record image passed as
      * From(WF-Policy-Info) and the 21-byte key passed as
      * Ridfld(WF-Policy-Key). The group holds the record only; the
      * lengths, response and counters are held in HC-VSAM-CONTROL
      * below, which keeps this group exactly 64 bytes.
      * Item order follows the declaration order at
      * [base/src/lgapvs01.cbl:27-29], not the MOVE order at
      * [base/src/lgapvs01.cbl:99-101].
      * See modernization/docs/decision-log.md, row: flat VSAM payload
      * capture.
           03 HC-VSAM-RECORD.
      *
      * Key half of the record image, 1 + 10 + 10 = 21 bytes, matching
      * the KeyLength(21) of [base/src/lgapvs01.cbl:139]. Witnesses
      * WF-Policy-Key [base/src/lgapvs01.cbl:26].
              05 HC-VSAM-KEY.
      *
      * Request-type letter. Witnesses WF-Request-ID
      * [base/src/lgapvs01.cbl:27], set from CA-REQUEST-ID(4:1)
      * [base/src/lgcmarea.cpy:10] at [base/src/lgapvs01.cbl:99]:
      * 'M' for request id '01AMOT', 'C' for '01ACOM'.
                 07 HC-VSAM-REQUEST-ID    PIC X.
      *
      * Customer number. Witnesses WF-Customer-Num
      * [base/src/lgapvs01.cbl:28], set from CA-CUSTOMER-NUM
      * [base/src/lgcmarea.cpy:12] at [base/src/lgapvs01.cbl:101].
                 07 HC-VSAM-CUSTOMER-NUM  PIC X(10).
      *
      * Policy number. Witnesses WF-Policy-Num
      * [base/src/lgapvs01.cbl:29], set from CA-POLICY-NUM
      * [base/src/lgcmarea.cpy:35] at [base/src/lgapvs01.cbl:100].
                 07 HC-VSAM-POLICY-NUM    PIC X(10).
      *
      * Payload half of the record image, 43 bytes, completing the
      * Length(64) of [base/src/lgapvs01.cbl:137]. Witnesses
      * WF-Policy-Data [base/src/lgapvs01.cbl:30] as one field. The
      * four REDEFINES overlays at [base/src/lgapvs01.cbl:31-51] are
      * not reproduced.
              05 HC-VSAM-POLICY-DATA      PIC X(43).
      *
      *----------------------------------------------------------------*
      * VSAM: WRITE control values                                     *
      *----------------------------------------------------------------*
           03 HC-VSAM-CONTROL.
      *
      * Set to 'Y' by cics_write.cbl when the WRITE executes.
              05 HC-VSAM-PRESENT          PIC X.
                 88 HC-VSAM-CAPTURED      VALUE 'Y'.
                 88 HC-VSAM-MISSING       VALUE 'N'.
      *
      * Number of times the WRITE executed.
              05 HC-VSAM-COUNT            PIC 9(4).
      *
      * Record length passed as Length
      * [base/src/lgapvs01.cbl:137]. The source passes the literal 64.
              05 HC-VSAM-RECORD-LEN       PIC 9(4).
      *
      * Key length passed as KeyLength
      * [base/src/lgapvs01.cbl:139]. The source passes the literal 21.
              05 HC-VSAM-KEY-LEN          PIC 9(4).
      *
      * Response returned through RESP [base/src/lgapvs01.cbl:140].
      * Witnesses WS-RESP [base/src/lgapvs01.cbl:18], which the
      * translated program compares against DFHRESP-NORMAL at
      * [base/src/lgapvs01.cbl:142]; an unequal compare sets
      * CA-RETURN-CODE to '80' at [base/src/lgapvs01.cbl:144].
              05 HC-VSAM-RESP             PIC S9(8) COMP.
      *
      *================================================================*
      * Abend capture                                                  *
      *   recorded by cics_abend.cbl for every EXEC CICS ABEND site    *
      *   of the three translated programs.                            *
      *================================================================*
      * The six sites are [base/src/lgapol01.cbl:101] and
      * [base/src/lgapdb01.cbl:168], both ABCODE('LGCA'), and
      * [base/src/lgapdb01.cbl:393], [base/src/lgapdb01.cbl:431],
      * [base/src/lgapdb01.cbl:477] and [base/src/lgapdb01.cbl:551],
      * all ABCODE('LGSQ'). A passing case records none of them.
           03 HC-ABEND.
      *
      * Set to 'Y' by cics_abend.cbl when any site is reached.
              05 HC-ABEND-PRESENT         PIC X.
                 88 HC-ABEND-RECORDED     VALUE 'Y'.
                 88 HC-ABEND-NONE         VALUE 'N'.
      *
      * The four-character code of the most recent site reached:
      * 'LGCA' for a zero-length COMMAREA, 'LGSQ' for a product-insert
      * SQL failure that also sets CA-RETURN-CODE to '90'.
              05 HC-ABEND-CODE            PIC X(4).
      *
      * Number of sites reached.
              05 HC-ABEND-COUNT           PIC 9(4).
      *
      *================================================================*
      * Diagnostic-link capture                                        *
      *   counted by cics_diag_link.cbl for every diagnostic           *
      *   EXEC CICS LINK PROGRAM('LGSTSQ') site.                       *
      *================================================================*
      * The nine sites are [base/src/lgapol01.cbl:149],
      * [base/src/lgapol01.cbl:157], [base/src/lgapol01.cbl:163],
      * [base/src/lgapdb01.cbl:575], [base/src/lgapdb01.cbl:583],
      * [base/src/lgapdb01.cbl:589], [base/src/lgapvs01.cbl:169],
      * [base/src/lgapvs01.cbl:176] and [base/src/lgapvs01.cbl:182].
      * Each sits inside an error paragraph, so a passing case leaves
      * this counter at zero.
           03 HC-DIAG-LINK-COUNT          PIC 9(4).
      *----------------------------------------------------------------*

