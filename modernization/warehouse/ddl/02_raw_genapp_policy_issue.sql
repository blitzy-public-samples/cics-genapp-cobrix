-- 02_raw_genapp_policy_issue.sql
-- Warehouse bootstrap, step 2 of 2, for the GenApp Policy-Issue cloud-warehouse bridge.
-- Creates raw.genapp_policy_issue, the landing relation holding one landed GenApp
-- Policy-Issue record per row, and the sole dbt source of the bridge.
-- Run order: 01_schemas.sql first, then this file.
-- Column names, column order and VARCHAR lengths match the 17 keys of
-- modernization/landing/landing-schema.json, ordered by the landing.field_order block
-- of modernization/extraction/copybook_field_map.yml.
-- Every column is VARCHAR and accepts null. Typing is performed by the dbt models.
-- Natural key used by the loaders: (source_system_key, policy_number).
-- Idempotent and re-runnable.
-- Runs unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4, dbt Transformation DAG and Field Allocation,
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

CREATE TABLE IF NOT EXISTS raw.genapp_policy_issue (
    -- Source-system discriminator assigned by the warehouse.
    -- No COBOL source item.
    source_system_key       VARCHAR(64),
    -- Policy number recovered after the policy insert.
    -- CA-POLICY-NUM PIC 9(10), base/src/lgcmarea.cpy:35.
    -- Recovered at base/src/lgapdb01.cbl:307-311.
    policy_number           VARCHAR(10),
    -- Product discriminator E, H, M or C.
    -- DB2-POLICYTYPE PIC X, base/src/lgpolicy.cpy:43.
    -- Derived from CA-REQUEST-ID routing at base/src/lgapdb01.cbl:184-207.
    policy_type             VARCHAR(1),
    -- Customer number supplied in the request.
    -- CA-CUSTOMER-NUM PIC 9(10), base/src/lgcmarea.cpy:12.
    customer_number         VARCHAR(10),
    -- Request identifier, for example 01AMOT or 01ACOM.
    -- CA-REQUEST-ID PIC X(6), base/src/lgcmarea.cpy:10.
    request_id              VARCHAR(6),
    -- Returned chain outcome: 00, 70, 80, 90, 98 or 99.
    -- CA-RETURN-CODE PIC 9(2), base/src/lgcmarea.cpy:11.
    return_code             VARCHAR(2),
    -- Policy issue date as supplied.
    -- CA-ISSUE-DATE PIC X(10), base/src/lgcmarea.cpy:38.
    issue_date              VARCHAR(10),
    -- Policy expiry date as supplied.
    -- CA-EXPIRY-DATE PIC X(10), base/src/lgcmarea.cpy:39.
    expiry_date             VARCHAR(10),
    -- Timestamp read back after the policy insert, normalised to ISO-8601 by the
    -- extractor and still 26 characters wide.
    -- CA-LASTCHANGED PIC X(26), base/src/lgcmarea.cpy:40.
    -- Read back at base/src/lgapdb01.cbl:315-321.
    last_changed            VARCHAR(26),
    -- Broker identifier as supplied.
    -- CA-BROKERID PIC 9(10), base/src/lgcmarea.cpy:41.
    broker_id               VARCHAR(10),
    -- Broker reference as supplied, trimmed.
    -- CA-BROKERSREF PIC X(10), base/src/lgcmarea.cpy:42.
    brokers_reference       VARCHAR(10),
    -- Policy payment amount, passthrough. Carried for every policy type.
    -- CA-PAYMENT PIC 9(6), base/src/lgcmarea.cpy:43.
    -- DB2-PAYMENT PIC 9(6), base/src/lgpolicy.cpy:51.
    payment_amount          VARCHAR(6),
    -- Motor premium, passthrough. Populated on motor rows only.
    -- CA-M-PREMIUM PIC 9(6), base/src/lgcmarea.cpy:73.
    -- DB2-M-PREMIUM PIC 9(6), base/src/lgpolicy.cpy:80.
    motor_premium_amount    VARCHAR(6),
    -- Commercial fire premium, passthrough. Populated on commercial rows only.
    -- CA-B-FirePremium PIC 9(8), base/src/lgcmarea.cpy:85.
    -- DB2-B-FirePremium PIC 9(8), base/src/lgpolicy.cpy:91.
    fire_premium_amount     VARCHAR(8),
    -- Commercial crime premium, passthrough. Populated on commercial rows only.
    -- CA-B-CrimePremium PIC 9(8), base/src/lgcmarea.cpy:87.
    -- DB2-B-CrimePremium PIC 9(8), base/src/lgpolicy.cpy:93.
    crime_premium_amount    VARCHAR(8),
    -- Commercial flood premium, passthrough. Populated on commercial rows only.
    -- CA-B-FloodPremium PIC 9(8), base/src/lgcmarea.cpy:89.
    -- DB2-B-FloodPremium PIC 9(8), base/src/lgpolicy.cpy:95.
    flood_premium_amount    VARCHAR(8),
    -- Commercial weather premium, passthrough. Populated on commercial rows only.
    -- CA-B-WeatherPremium PIC 9(8), base/src/lgcmarea.cpy:91.
    -- DB2-B-WeatherPremium PIC 9(8), base/src/lgpolicy.cpy:97.
    weather_premium_amount  VARCHAR(8)
);
