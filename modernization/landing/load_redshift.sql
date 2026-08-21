-- load_redshift.sql
-- Real-target raw loader for the GenApp Policy-Issue cloud-warehouse bridge.
-- Loads one landed Amazon S3 object into raw.genapp_policy_issue on Amazon Redshift.
-- The counterpart loader is modernization/landing/load_local.py, which reads the same
-- object and inserts the same 17 columns, in the same order, into the same relation on
-- the local DuckDB target.
--
-- Run order. modernization/warehouse/ddl/01_schemas.sql provides the raw schema and
-- modernization/warehouse/ddl/02_raw_genapp_policy_issue.sql defines the relation and
-- owns its column widths. This file only reads an object and writes rows: it defines,
-- alters and drops nothing, and it provisions no AWS resource of any kind.
--
-- Column contract. The column names and the column order below match the 17 keys of
-- modernization/landing/landing-schema.json, ordered by the landing.field_order block
-- of modernization/extraction/copybook_field_map.yml. Every target column is VARCHAR
-- and accepts null, and this load stores each landed value as the string that was
-- landed. All typing is performed by the dbt models downstream. A JSON null lands as
-- SQL NULL. A premium that does not apply to the policy type stays null, and never
-- becomes an empty string or a zero.
--
-- Natural key used by the loaders: (source_system_key, policy_number).
--
-- Execution status. Authored, not executed. No Amazon Redshift cluster or workgroup
-- and no AWS access is available on this branch, and these statements have never been
-- run against a real target. The recorded status is held in
-- modernization/validation/validation-evidence.md.
--
-- Placeholders. The caller substitutes every ${...} token below before sending these
-- statements to Amazon Redshift. No secret, account identifier, role identifier,
-- bucket name, endpoint or region literal is written into this file.
--   ${S3_BUCKET}          name of the S3 bucket holding the landed object
--   ${SOURCE_SYSTEM_KEY}  source-system discriminator of the landed record, and the
--                         first key=value segment of the landed object key
--   ${ENTITY}             entity name segment of the landed object key
--   ${EXTRACT_DATE}       extract date segment of the landed object key, form
--                         YYYY-MM-DD
--   ${POLICY_NUMBER}      policy number of the landed record, matched by the delete
--                         guard below
--   ${REDSHIFT_IAM_ROLE}  identifier of the IAM role that authorises this load to read
--                         the bucket
--   ${AWS_REGION}         region of the S3 bucket named above
--
-- Rationale for every choice in this file: modernization/docs/decision-log.md

BEGIN;

-- Delete guard, keyed on the natural key (source_system_key, policy_number).
-- Matches only the record this load is about to land. Every other landed record keeps
-- its row, and loading the same record again leaves exactly one row for it.
-- The policy number is assigned once per issued policy by the chain: the policy insert
-- supplies DEFAULT for POLICYNUMBER at base/src/lgapdb01.cbl:279 and the assigned value
-- is recovered by IDENTITY_VAL_LOCAL at base/src/lgapdb01.cbl:308-311.
DELETE FROM raw.genapp_policy_issue
 WHERE source_system_key = '${SOURCE_SYSTEM_KEY}'
   AND policy_number = '${POLICY_NUMBER}';

-- Load the landed object. The 17 target columns are named explicitly, in the order
-- fixed by the landing contract. JSON 'auto' matches each lowercase object key of the
-- landed record to the column of the same name, so only these 17 columns can receive a
-- value and no other column of the relation is written.
-- The four commercial peril codes at base/src/lgcmarea.cpy:84, 86, 88 and 90 are not
-- landed fields and have no column here.
COPY raw.genapp_policy_issue (
    -- Source-system discriminator assigned by the warehouse. No COBOL source item.
    source_system_key,
    -- CA-POLICY-NUM PIC 9(10), base/src/lgcmarea.cpy:35.
    policy_number,
    -- DB2-POLICYTYPE PIC X, base/src/lgpolicy.cpy:43, derived from CA-REQUEST-ID
    -- routing at base/src/lgapdb01.cbl:184-207.
    policy_type,
    -- CA-CUSTOMER-NUM PIC 9(10), base/src/lgcmarea.cpy:12.
    customer_number,
    -- CA-REQUEST-ID PIC X(6), base/src/lgcmarea.cpy:10.
    request_id,
    -- CA-RETURN-CODE PIC 9(2), base/src/lgcmarea.cpy:11.
    return_code,
    -- CA-ISSUE-DATE PIC X(10), base/src/lgcmarea.cpy:38.
    issue_date,
    -- CA-EXPIRY-DATE PIC X(10), base/src/lgcmarea.cpy:39.
    expiry_date,
    -- CA-LASTCHANGED PIC X(26), base/src/lgcmarea.cpy:40, read back at
    -- base/src/lgapdb01.cbl:315-321 and normalised to ISO-8601 by the extractor.
    last_changed,
    -- CA-BROKERID PIC 9(10), base/src/lgcmarea.cpy:41.
    broker_id,
    -- CA-BROKERSREF PIC X(10), base/src/lgcmarea.cpy:42.
    brokers_reference,
    -- CA-PAYMENT PIC 9(6), base/src/lgcmarea.cpy:43, moved unchanged at
    -- base/src/lgapdb01.cbl:265. Carried for every policy type.
    payment_amount,
    -- CA-M-PREMIUM PIC 9(6), base/src/lgcmarea.cpy:73, moved unchanged at
    -- base/src/lgapdb01.cbl:445. Populated on motor rows only, null otherwise.
    motor_premium_amount,
    -- CA-B-FirePremium PIC 9(8), base/src/lgcmarea.cpy:85, moved unchanged at
    -- base/src/lgapdb01.cbl:489. Populated on commercial rows only, null otherwise.
    fire_premium_amount,
    -- CA-B-CrimePremium PIC 9(8), base/src/lgcmarea.cpy:87, moved unchanged at
    -- base/src/lgapdb01.cbl:491. Populated on commercial rows only, null otherwise.
    crime_premium_amount,
    -- CA-B-FloodPremium PIC 9(8), base/src/lgcmarea.cpy:89, moved unchanged at
    -- base/src/lgapdb01.cbl:493. Populated on commercial rows only, null otherwise.
    flood_premium_amount,
    -- CA-B-WeatherPremium PIC 9(8), base/src/lgcmarea.cpy:91, moved unchanged at
    -- base/src/lgapdb01.cbl:495. Populated on commercial rows only, null otherwise.
    weather_premium_amount
)
FROM 's3://${S3_BUCKET}/landing/source_system_key=${SOURCE_SYSTEM_KEY}/entity=${ENTITY}/extract_date=${EXTRACT_DATE}/part-0000.json'
IAM_ROLE '${REDSHIFT_IAM_ROLE}'
FORMAT AS JSON 'auto'
REGION '${AWS_REGION}';

COMMIT;
