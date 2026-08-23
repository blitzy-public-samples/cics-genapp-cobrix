# Comparison gate — harness captures against the two canonical relations

**Disposition — validated against local substitute, not AWS.** Every result in this report carries that disposition.

These results do not satisfy the formal AWS diff requirement, which remains OPEN: it closes only when the same dbt models run unmodified against real S3 and Amazon Redshift.

Flow context: Figure 5 — Validation Harness Control Flow in modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md.

## Run metadata

| Item | Value |
|---|---|
| generated at (UTC) | 2026-08-23T02:43:34Z |
| target | duckdb |
| adapter | duckdb 1.5.5 |
| python | 3.12.14 |
| connection | modernization/validation/local.duckdb |
| source-system key | GENAPP_CLASS_EXEMPLAR |
| amount tolerance | 0.01 |
| expected amount scale | 2 |
| field map | modernization/extraction/copybook_field_map.yml |
| harness run directory | modernization/harness/build/run |
| capture snapshots | modernization/validation/expected |
| cases requested | 01AMOT, 01ACOM |
| transform freshness | FRESH — dbt test recorded 64 nodes, 64 of them successful and 0 warned |
| gate artifact | modernization/validation/artifacts/gate-probe-redshift.log |
| disposition | validated against local substitute, not AWS |

## Verdict

| Case | Verdict | Coverage | Failed | Missing | Unexpected in tolerance | Disposition |
|---|---|---|---|---|---|---|
| 01AMOT | PASS | 20/20 | 0 | 0 | 0 | validated against local substitute, not AWS |
| 01ACOM | PASS | 20/20 | 0 | 0 | 0 | validated against local substitute, not AWS |

**Overall verdict: PASS** (exit status 0) — validated against local substitute, not AWS.

## Transform freshness precondition

| Item | Value |
|---|---|
| verdict | FRESH |
| dbt run artifact | modernization/dbt/genapp_rqi/target/run_results.json |
| dbt version | 1.12.3 |
| artifact schema | https://schemas.getdbt.com/dbt/run-results/v6.json |
| invocation id | 89049bd5-1ec9-4ab3-bf0a-d5de9af64c97 |
| recorded at | 2026-08-23T02:43:34.189103Z |
| subcommand | test |
| dbt target | local_substitute |
| elapsed seconds | 1.4484243392944336 |
| nodes recorded | 64 |
| nodes successful | 64 |
| nodes warned | 0 |
| nodes refused | 0 |
| statuses accepted | success, pass |
| statuses warned | warn |
| statuses refused | error, fail, skipped, runtime error |

Every node of the last dbt invocation recorded a successful status, so the warehouse state below is the state that invocation produced — validated against local substitute, not AWS.

## Canonical inventory

| Relation | Columns in ordinal order | Verdict |
|---|---|---|
| canonical.issued_policy | source_system_key, policy_number, policy_type, customer_number, request_id, return_code, issue_date, expiry_date, last_changed, broker_id, brokers_reference | PASS |
| canonical.preissued_rating | source_system_key, policy_number, policy_type, payment_amount, motor_premium_amount, fire_premium_amount, crime_premium_amount, flood_premium_amount, weather_premium_amount | PASS |

Schema canonical holds exactly issued_policy, preissued_rating — validated against local substitute, not AWS.

## Case 01AMOT

| Item | Value |
|---|---|
| fixture | 01amot |
| request id | 01AMOT |
| policy type | M |
| policy number | 1000001 |
| capture file | modernization/harness/build/run/01amot/captures.txt |
| returned COMMAREA | modernization/harness/build/run/01amot/commarea_post.dat |
| driver input | modernization/harness/build/samples/commarea_01amot.dat |
| capture snapshot | modernization/validation/expected/01amot/captures.normalized.json (matched) |
| verdict | PASS — validated against local substitute, not AWS |

coverage: 20/20 canonical column instances compared — validated against local substitute, not AWS.

### Canonical column comparison

| Relation | Column | Kind | Harness authority | COBOL item | Locator | Harness value | Warehouse value | Delta | Normalisation | Verdict | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| canonical.issued_policy | source_system_key | exact string | configured run value (--source-system-key) | none (warehouse-assigned) | user requirement (no COBOL item supplies it) | GENAPP_CLASS_EXEMPLAR | GENAPP_CLASS_EXEMPLAR | — | trailing-space trim | PASS | (empty) |
| canonical.issued_policy | policy_number | integer | returned COMMAREA bytes 19-28 (CA-POLICY-NUM); returned COMMAREA capture (capture key CA_POLICY_NUM); policy insert capture (capture key SQL_POLICY_ASSIGNED_NUMBER) | CA-POLICY-NUM | base/src/lgcmarea.cpy:35 | 1000001 | 1000001 | — | leading-zero-insensitive integer | PASS | (empty) |
| canonical.issued_policy | policy_type | single char | request routing derivation from CA-REQUEST-ID [base/src/lgapdb01.cbl:184-207]; policy insert capture (capture key SQL_POLICY_POLICYTYPE) | DB2-POLICYTYPE | base/src/lgpolicy.cpy:43 | M | M | — | trailing-space trim | PASS | (empty) |
| canonical.issued_policy | customer_number | integer | returned COMMAREA bytes 9-18 (CA-CUSTOMER-NUM); returned COMMAREA capture (capture key CA_CUSTOMER_NUM); driver input bytes 9-18; policy insert capture (capture key SQL_POLICY_CUSTOMERNUM) | CA-CUSTOMER-NUM | base/src/lgcmarea.cpy:12 | 1001 | 1001 | — | leading-zero-insensitive integer | PASS | (empty) |
| canonical.issued_policy | request_id | exact string | returned COMMAREA bytes 1-6 (CA-REQUEST-ID); returned COMMAREA capture (capture key CA_REQUEST_ID); driver input bytes 1-6 | CA-REQUEST-ID | base/src/lgcmarea.cpy:10 | 01AMOT | 01AMOT | — | trailing-space trim | PASS | (empty) |
| canonical.issued_policy | return_code | exact string | returned COMMAREA bytes 7-8 (CA-RETURN-CODE); returned COMMAREA capture (capture key CA_RETURN_CODE) | CA-RETURN-CODE | base/src/lgcmarea.cpy:11 | 00 | 00 | — | trailing-space trim | PASS | (empty) |
| canonical.issued_policy | issue_date | date | returned COMMAREA bytes 29-38 (CA-ISSUE-DATE); returned COMMAREA capture (capture key CA_ISSUE_DATE); driver input bytes 29-38; policy insert capture (capture key SQL_POLICY_ISSUEDATE) | CA-ISSUE-DATE / DB2-ISSUEDATE | base/src/lgcmarea.cpy:38 | 2026-08-19 | 2026-08-19 | — | ISO calendar date | PASS | (empty) |
| canonical.issued_policy | expiry_date | date | returned COMMAREA bytes 39-48 (CA-EXPIRY-DATE); returned COMMAREA capture (capture key CA_EXPIRY_DATE); driver input bytes 39-48; policy insert capture (capture key SQL_POLICY_EXPIRYDATE) | CA-EXPIRY-DATE / DB2-EXPIRYDATE | base/src/lgcmarea.cpy:39 | 2027-08-18 | 2027-08-18 | — | ISO calendar date | PASS | (empty) |
| canonical.issued_policy | last_changed | timestamp | returned COMMAREA bytes 49-74 (CA-LASTCHANGED); returned COMMAREA capture (capture key CA_LASTCHANGED); policy insert capture (capture key SQL_POLICY_ASSIGNED_LASTCHANGED) | CA-LASTCHANGED / DB2-LASTCHANGED | base/src/lgcmarea.cpy:40 | 2026-08-19 12:00:00.000000 | 2026-08-19 12:00:00.000000 | — | Db2 timestamp to microsecond precision | PASS | (empty) |
| canonical.issued_policy | broker_id | integer | returned COMMAREA bytes 75-84 (CA-BROKERID); returned COMMAREA capture (capture key CA_BROKERID); driver input bytes 75-84; policy insert capture (capture key SQL_POLICY_BROKERID) | CA-BROKERID / DB2-BROKERID | base/src/lgcmarea.cpy:41 | 42 | 42 | — | leading-zero-insensitive integer | PASS | (empty) |
| canonical.issued_policy | brokers_reference | exact string | returned COMMAREA bytes 85-94 (CA-BROKERSREF); returned COMMAREA capture (capture key CA_BROKERSREF); driver input bytes 85-94; policy insert capture (capture key SQL_POLICY_BROKERSREF) | CA-BROKERSREF / DB2-BROKERSREF | base/src/lgcmarea.cpy:42 | BRMOT001 | BRMOT001 | — | trailing-space trim | PASS | (empty) |
| canonical.preissued_rating | source_system_key | exact string | configured run value (--source-system-key) | none (warehouse-assigned) | user requirement (no COBOL item supplies it) | GENAPP_CLASS_EXEMPLAR | GENAPP_CLASS_EXEMPLAR | — | trailing-space trim | PASS | (empty) |
| canonical.preissued_rating | policy_number | integer | returned COMMAREA bytes 19-28 (CA-POLICY-NUM); returned COMMAREA capture (capture key CA_POLICY_NUM); policy insert capture (capture key SQL_POLICY_ASSIGNED_NUMBER) | CA-POLICY-NUM | base/src/lgcmarea.cpy:35 | 1000001 | 1000001 | — | leading-zero-insensitive integer | PASS | (empty) |
| canonical.preissued_rating | policy_type | single char | request routing derivation from CA-REQUEST-ID [base/src/lgapdb01.cbl:184-207]; policy insert capture (capture key SQL_POLICY_POLICYTYPE) | DB2-POLICYTYPE | base/src/lgpolicy.cpy:43 | M | M | — | trailing-space trim | PASS | (empty) |
| canonical.preissued_rating | payment_amount | amount | returned COMMAREA bytes 95-100 (CA-PAYMENT); returned COMMAREA capture (capture key CA_PAYMENT); driver input bytes 95-100; policy insert capture (capture key SQL_POLICY_PAYMENT) | CA-PAYMENT / DB2-PAYMENT | base/src/lgcmarea.cpy:43 | 500 | 500.00 | 0.00 | DISPLAY digits to decimal | PASS | warehouse scale 2 |
| canonical.preissued_rating | motor_premium_amount | amount | returned COMMAREA bytes 166-171 (CA-M-PREMIUM); returned COMMAREA capture (capture key CA_M_PREMIUM); driver input bytes 166-171; motor insert capture (capture key SQL_MOTOR_PREMIUM) | CA-M-PREMIUM / DB2-M-PREMIUM | base/src/lgcmarea.cpy:73 | 450 | 450.00 | 0.00 | DISPLAY digits to decimal | PASS | warehouse scale 2 |
| canonical.preissued_rating | fire_premium_amount | null expectation | none | CA-B-FirePremium / DB2-B-FirePremium | base/src/lgcmarea.cpy:85 | — | NULL | — | none | PASS | product_premium_nullability records this column as null for policy type M; the policy type of this case populates no value for this column and the warehouse carries NULL |
| canonical.preissued_rating | crime_premium_amount | null expectation | none | CA-B-CrimePremium / DB2-B-CrimePremium | base/src/lgcmarea.cpy:87 | — | NULL | — | none | PASS | product_premium_nullability records this column as null for policy type M; the policy type of this case populates no value for this column and the warehouse carries NULL |
| canonical.preissued_rating | flood_premium_amount | null expectation | none | CA-B-FloodPremium / DB2-B-FloodPremium | base/src/lgcmarea.cpy:89 | — | NULL | — | none | PASS | product_premium_nullability records this column as null for policy type M; the policy type of this case populates no value for this column and the warehouse carries NULL |
| canonical.preissued_rating | weather_premium_amount | null expectation | none | CA-B-WeatherPremium / DB2-B-WeatherPremium | base/src/lgcmarea.cpy:91 | — | NULL | — | none | PASS | product_premium_nullability records this column as null for policy type M; the policy type of this case populates no value for this column and the warehouse carries NULL |

### Chain completion

| Assertion | Expected | Observed | Locator | Verdict | Notes |
|---|---|---|---|---|---|
| CASE | 01AMOT | 01AMOT | modernization/harness/driver.cbl | PASS | (empty) |
| DRIVER_STATUS | PASS | PASS | modernization/harness/driver.cbl | PASS | (empty) |
| DRIVER_EXIT_STATUS | 00 | 00 | modernization/harness/driver.cbl | PASS | (empty) |
| CA_RETURN_CODE | 00 | 00 | base/src/lgapdb01.cbl:293 | PASS | (empty) |
| ABEND_PRESENT | N | N | base/src/lgapdb01.cbl:393 | PASS | (empty) |
| ABEND_CODE | (empty) | (empty) | base/src/lgapdb01.cbl:393 | PASS | (empty) |
| ABEND_COUNT | 0 | 0000 | base/src/lgapdb01.cbl:393 | PASS | (empty) |
| DIAG_LINK_COUNT | 0 | 0000 | base/src/lgapdb01.cbl:575-592 | PASS | (empty) |
| SQL_POLICY_PRESENT | Y | Y | base/src/lgapdb01.cbl:268-287 | PASS | (empty) |
| SQL_COMMERCIAL_PRESENT | N | N | base/src/lgapdb01.cbl:223-241 | PASS | (empty) |
| SQL_ENDOWMENT_PRESENT | N | N | base/src/lgapdb01.cbl:223-241 | PASS | (empty) |
| SQL_HOUSE_PRESENT | N | N | base/src/lgapdb01.cbl:223-241 | PASS | (empty) |
| SQL_MOTOR_PRESENT | Y | Y | base/src/lgapdb01.cbl:223-241 | PASS | (empty) |

Chain completion: PASS — validated against local substitute, not AWS.

### VSAM corroboration

| Assertion | Expected | Observed | Locator | Verdict | Notes |
|---|---|---|---|---|---|
| VSAM_PRESENT | Y | Y | base/src/lgapvs01.cbl:135-141 | PASS | (empty) |
| VSAM_LENGTH | 64 | 0064 | base/src/lgapvs01.cbl:137 | PASS | (empty) |
| VSAM_KEYLENGTH | 21 | 0021 | base/src/lgapvs01.cbl:139 | PASS | (empty) |
| VSAM_KEY | M00000010010001000001 | M00000010010001000001 | base/src/lgapvs01.cbl:26-29 | PASS | (empty) |
| VSAM_REQUEST_ID | M | M | base/src/lgapvs01.cbl:26-29 | PASS | (empty) |
| VSAM_CUSTOMER_NUM | 0000001001 | 0000001001 | base/src/lgapvs01.cbl:26-29 | PASS | (empty) |
| VSAM_POLICY_NUM | 0001000001 | 0001000001 | base/src/lgapvs01.cbl:26-29 | PASS | (empty) |
| product payload | 43 bytes, mapped to no canonical column | 43 bytes, not compared | base/src/lgapvs01.cbl:30 | PASS | the payload corroborates the write and the composite key alone |

VSAM corroboration: PASS — validated against local substitute, not AWS.

### Cross-relation identity

| Assertion | Expected | Observed | Locator | Verdict | Notes |
|---|---|---|---|---|---|
| source_system_key | canonical.issued_policy carries [GENAPP_CLASS_EXEMPLAR] | canonical.preissued_rating carries [GENAPP_CLASS_EXEMPLAR] | modernization/extraction/copybook_field_map.yml: targets | PASS | (empty) |
| policy_number | canonical.issued_policy carries [1000001] | canonical.preissued_rating carries [1000001] | modernization/extraction/copybook_field_map.yml: targets | PASS | (empty) |
| policy_type | canonical.issued_policy carries [M] | canonical.preissued_rating carries [M] | modernization/extraction/copybook_field_map.yml: targets | PASS | (empty) |

Cross-relation identity: PASS — validated against local substitute, not AWS.

unexpected_in_tolerance for 01AMOT: none — validated against local substitute, not AWS.

## Case 01ACOM

| Item | Value |
|---|---|
| fixture | 01acom |
| request id | 01ACOM |
| policy type | C |
| policy number | 1000002 |
| capture file | modernization/harness/build/run/01acom/captures.txt |
| returned COMMAREA | modernization/harness/build/run/01acom/commarea_post.dat |
| driver input | modernization/harness/build/samples/commarea_01acom.dat |
| capture snapshot | modernization/validation/expected/01acom/captures.normalized.json (matched) |
| verdict | PASS — validated against local substitute, not AWS |

coverage: 20/20 canonical column instances compared — validated against local substitute, not AWS.

### Canonical column comparison

| Relation | Column | Kind | Harness authority | COBOL item | Locator | Harness value | Warehouse value | Delta | Normalisation | Verdict | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| canonical.issued_policy | source_system_key | exact string | configured run value (--source-system-key) | none (warehouse-assigned) | user requirement (no COBOL item supplies it) | GENAPP_CLASS_EXEMPLAR | GENAPP_CLASS_EXEMPLAR | — | trailing-space trim | PASS | (empty) |
| canonical.issued_policy | policy_number | integer | returned COMMAREA bytes 19-28 (CA-POLICY-NUM); returned COMMAREA capture (capture key CA_POLICY_NUM); policy insert capture (capture key SQL_POLICY_ASSIGNED_NUMBER) | CA-POLICY-NUM | base/src/lgcmarea.cpy:35 | 1000002 | 1000002 | — | leading-zero-insensitive integer | PASS | (empty) |
| canonical.issued_policy | policy_type | single char | request routing derivation from CA-REQUEST-ID [base/src/lgapdb01.cbl:184-207]; policy insert capture (capture key SQL_POLICY_POLICYTYPE) | DB2-POLICYTYPE | base/src/lgpolicy.cpy:43 | C | C | — | trailing-space trim | PASS | (empty) |
| canonical.issued_policy | customer_number | integer | returned COMMAREA bytes 9-18 (CA-CUSTOMER-NUM); returned COMMAREA capture (capture key CA_CUSTOMER_NUM); driver input bytes 9-18; policy insert capture (capture key SQL_POLICY_CUSTOMERNUM) | CA-CUSTOMER-NUM | base/src/lgcmarea.cpy:12 | 2002 | 2002 | — | leading-zero-insensitive integer | PASS | (empty) |
| canonical.issued_policy | request_id | exact string | returned COMMAREA bytes 1-6 (CA-REQUEST-ID); returned COMMAREA capture (capture key CA_REQUEST_ID); driver input bytes 1-6 | CA-REQUEST-ID | base/src/lgcmarea.cpy:10 | 01ACOM | 01ACOM | — | trailing-space trim | PASS | (empty) |
| canonical.issued_policy | return_code | exact string | returned COMMAREA bytes 7-8 (CA-RETURN-CODE); returned COMMAREA capture (capture key CA_RETURN_CODE) | CA-RETURN-CODE | base/src/lgcmarea.cpy:11 | 00 | 00 | — | trailing-space trim | PASS | (empty) |
| canonical.issued_policy | issue_date | date | returned COMMAREA bytes 29-38 (CA-ISSUE-DATE); returned COMMAREA capture (capture key CA_ISSUE_DATE); driver input bytes 29-38; policy insert capture (capture key SQL_POLICY_ISSUEDATE) | CA-ISSUE-DATE / DB2-ISSUEDATE | base/src/lgcmarea.cpy:38 | 2026-08-19 | 2026-08-19 | — | ISO calendar date | PASS | (empty) |
| canonical.issued_policy | expiry_date | date | returned COMMAREA bytes 39-48 (CA-EXPIRY-DATE); returned COMMAREA capture (capture key CA_EXPIRY_DATE); driver input bytes 39-48; policy insert capture (capture key SQL_POLICY_EXPIRYDATE) | CA-EXPIRY-DATE / DB2-EXPIRYDATE | base/src/lgcmarea.cpy:39 | 2027-08-18 | 2027-08-18 | — | ISO calendar date | PASS | (empty) |
| canonical.issued_policy | last_changed | timestamp | returned COMMAREA bytes 49-74 (CA-LASTCHANGED); returned COMMAREA capture (capture key CA_LASTCHANGED); policy insert capture (capture key SQL_POLICY_ASSIGNED_LASTCHANGED) | CA-LASTCHANGED / DB2-LASTCHANGED | base/src/lgcmarea.cpy:40 | 2026-08-19 12:00:00.000000 | 2026-08-19 12:00:00.000000 | — | Db2 timestamp to microsecond precision | PASS | (empty) |
| canonical.issued_policy | broker_id | integer | returned COMMAREA bytes 75-84 (CA-BROKERID); returned COMMAREA capture (capture key CA_BROKERID); driver input bytes 75-84; policy insert capture (capture key SQL_POLICY_BROKERID) | CA-BROKERID / DB2-BROKERID | base/src/lgcmarea.cpy:41 | 84 | 84 | — | leading-zero-insensitive integer | PASS | (empty) |
| canonical.issued_policy | brokers_reference | exact string | returned COMMAREA bytes 85-94 (CA-BROKERSREF); returned COMMAREA capture (capture key CA_BROKERSREF); driver input bytes 85-94; policy insert capture (capture key SQL_POLICY_BROKERSREF) | CA-BROKERSREF / DB2-BROKERSREF | base/src/lgcmarea.cpy:42 | BRCOM001 | BRCOM001 | — | trailing-space trim | PASS | (empty) |
| canonical.preissued_rating | source_system_key | exact string | configured run value (--source-system-key) | none (warehouse-assigned) | user requirement (no COBOL item supplies it) | GENAPP_CLASS_EXEMPLAR | GENAPP_CLASS_EXEMPLAR | — | trailing-space trim | PASS | (empty) |
| canonical.preissued_rating | policy_number | integer | returned COMMAREA bytes 19-28 (CA-POLICY-NUM); returned COMMAREA capture (capture key CA_POLICY_NUM); policy insert capture (capture key SQL_POLICY_ASSIGNED_NUMBER) | CA-POLICY-NUM | base/src/lgcmarea.cpy:35 | 1000002 | 1000002 | — | leading-zero-insensitive integer | PASS | (empty) |
| canonical.preissued_rating | policy_type | single char | request routing derivation from CA-REQUEST-ID [base/src/lgapdb01.cbl:184-207]; policy insert capture (capture key SQL_POLICY_POLICYTYPE) | DB2-POLICYTYPE | base/src/lgpolicy.cpy:43 | C | C | — | trailing-space trim | PASS | (empty) |
| canonical.preissued_rating | payment_amount | amount | returned COMMAREA bytes 95-100 (CA-PAYMENT); returned COMMAREA capture (capture key CA_PAYMENT); driver input bytes 95-100; policy insert capture (capture key SQL_POLICY_PAYMENT) | CA-PAYMENT / DB2-PAYMENT | base/src/lgcmarea.cpy:43 | 1750 | 1750.00 | 0.00 | DISPLAY digits to decimal | PASS | warehouse scale 2 |
| canonical.preissued_rating | motor_premium_amount | null expectation | none | CA-M-PREMIUM / DB2-M-PREMIUM | base/src/lgcmarea.cpy:73 | — | NULL | — | none | PASS | product_premium_nullability records this column as null for policy type C; the policy type of this case populates no value for this column and the warehouse carries NULL |
| canonical.preissued_rating | fire_premium_amount | amount | returned COMMAREA bytes 900-907 (CA-B-FirePremium); returned COMMAREA capture (capture key CA_B_FIREPREMIUM); driver input bytes 900-907; commercial insert capture (capture key SQL_COMMERCIAL_FIREPREMIUM) | CA-B-FirePremium / DB2-B-FirePremium | base/src/lgcmarea.cpy:85 | 13500 | 13500.00 | 0.00 | DISPLAY digits to decimal | PASS | warehouse scale 2 |
| canonical.preissued_rating | crime_premium_amount | amount | returned COMMAREA bytes 912-919 (CA-B-CrimePremium); returned COMMAREA capture (capture key CA_B_CRIMEPREMIUM); driver input bytes 912-919; commercial insert capture (capture key SQL_COMMERCIAL_CRIMEPREMIUM) | CA-B-CrimePremium / DB2-B-CrimePremium | base/src/lgcmarea.cpy:87 | 3400 | 3400.00 | 0.00 | DISPLAY digits to decimal | PASS | warehouse scale 2 |
| canonical.preissued_rating | flood_premium_amount | amount | returned COMMAREA bytes 924-931 (CA-B-FloodPremium); returned COMMAREA capture (capture key CA_B_FLOODPREMIUM); driver input bytes 924-931; commercial insert capture (capture key SQL_COMMERCIAL_FLOODPREMIUM) | CA-B-FloodPremium / DB2-B-FloodPremium | base/src/lgcmarea.cpy:89 | 7800 | 7800.00 | 0.00 | DISPLAY digits to decimal | PASS | warehouse scale 2 |
| canonical.preissued_rating | weather_premium_amount | amount | returned COMMAREA bytes 936-943 (CA-B-WeatherPremium); returned COMMAREA capture (capture key CA_B_WEATHERPREMIUM); driver input bytes 936-943; commercial insert capture (capture key SQL_COMMERCIAL_WEATHERPREMIUM) | CA-B-WeatherPremium / DB2-B-WeatherPremium | base/src/lgcmarea.cpy:91 | 2600 | 2600.00 | 0.00 | DISPLAY digits to decimal | PASS | warehouse scale 2 |

### Chain completion

| Assertion | Expected | Observed | Locator | Verdict | Notes |
|---|---|---|---|---|---|
| CASE | 01ACOM | 01ACOM | modernization/harness/driver.cbl | PASS | (empty) |
| DRIVER_STATUS | PASS | PASS | modernization/harness/driver.cbl | PASS | (empty) |
| DRIVER_EXIT_STATUS | 00 | 00 | modernization/harness/driver.cbl | PASS | (empty) |
| CA_RETURN_CODE | 00 | 00 | base/src/lgapdb01.cbl:293 | PASS | (empty) |
| ABEND_PRESENT | N | N | base/src/lgapdb01.cbl:393 | PASS | (empty) |
| ABEND_CODE | (empty) | (empty) | base/src/lgapdb01.cbl:393 | PASS | (empty) |
| ABEND_COUNT | 0 | 0000 | base/src/lgapdb01.cbl:393 | PASS | (empty) |
| DIAG_LINK_COUNT | 0 | 0000 | base/src/lgapdb01.cbl:575-592 | PASS | (empty) |
| SQL_POLICY_PRESENT | Y | Y | base/src/lgapdb01.cbl:268-287 | PASS | (empty) |
| SQL_COMMERCIAL_PRESENT | Y | Y | base/src/lgapdb01.cbl:223-241 | PASS | (empty) |
| SQL_ENDOWMENT_PRESENT | N | N | base/src/lgapdb01.cbl:223-241 | PASS | (empty) |
| SQL_HOUSE_PRESENT | N | N | base/src/lgapdb01.cbl:223-241 | PASS | (empty) |
| SQL_MOTOR_PRESENT | N | N | base/src/lgapdb01.cbl:223-241 | PASS | (empty) |

Chain completion: PASS — validated against local substitute, not AWS.

### VSAM corroboration

| Assertion | Expected | Observed | Locator | Verdict | Notes |
|---|---|---|---|---|---|
| VSAM_PRESENT | Y | Y | base/src/lgapvs01.cbl:135-141 | PASS | (empty) |
| VSAM_LENGTH | 64 | 0064 | base/src/lgapvs01.cbl:137 | PASS | (empty) |
| VSAM_KEYLENGTH | 21 | 0021 | base/src/lgapvs01.cbl:139 | PASS | (empty) |
| VSAM_KEY | C00000020020001000002 | C00000020020001000002 | base/src/lgapvs01.cbl:26-29 | PASS | (empty) |
| VSAM_REQUEST_ID | C | C | base/src/lgapvs01.cbl:26-29 | PASS | (empty) |
| VSAM_CUSTOMER_NUM | 0000002002 | 0000002002 | base/src/lgapvs01.cbl:26-29 | PASS | (empty) |
| VSAM_POLICY_NUM | 0001000002 | 0001000002 | base/src/lgapvs01.cbl:26-29 | PASS | (empty) |
| product payload | 43 bytes, mapped to no canonical column | 43 bytes, not compared | base/src/lgapvs01.cbl:30 | PASS | the payload corroborates the write and the composite key alone |

VSAM corroboration: PASS — validated against local substitute, not AWS.

### Cross-relation identity

| Assertion | Expected | Observed | Locator | Verdict | Notes |
|---|---|---|---|---|---|
| source_system_key | canonical.issued_policy carries [GENAPP_CLASS_EXEMPLAR] | canonical.preissued_rating carries [GENAPP_CLASS_EXEMPLAR] | modernization/extraction/copybook_field_map.yml: targets | PASS | (empty) |
| policy_number | canonical.issued_policy carries [1000002] | canonical.preissued_rating carries [1000002] | modernization/extraction/copybook_field_map.yml: targets | PASS | (empty) |
| policy_type | canonical.issued_policy carries [C] | canonical.preissued_rating carries [C] | modernization/extraction/copybook_field_map.yml: targets | PASS | (empty) |

Cross-relation identity: PASS — validated against local substitute, not AWS.

unexpected_in_tolerance for 01ACOM: none — validated against local substitute, not AWS.

## Amount deltas inside the tolerance

unexpected_in_tolerance: none — validated against local substitute, not AWS.

## Warehouse amount scale

Every compared warehouse amount carries scale 2 — validated against local substitute, not AWS.

## Return-code vocabulary of the named chain

| Code | Observed meaning |
|---|---|
| 00 | success |
| 70 | policy insert returned SQLCODE -530 |
| 80 | VSAM write response was not normal |
| 90 | SQL failure |
| 98 | COMMAREA shorter than the required length |
| 99 | unsupported request id |

The harness executes the success path and a compared case carries 00; the remaining codes stand in the vocabulary of the chain and are unexercised by this run.

