-- stg_genapp__policy_issue.sql
-- Staging model of the GenApp Policy-Issue cloud-warehouse bridge, and the only model of
-- the models/staging subtree.
--
-- Input. The dbt source binding source('genapp', 'genapp_policy_issue'), declared in
-- models/staging/genapp_class_exemplar/_genapp__sources.yml, which resolves to the landing
-- relation defined by modernization/warehouse/ddl/02_raw_genapp_policy_issue.sql. That
-- binding is the only relation this model reads, and the schema and relation it resolves to
-- are carried by the source declaration rather than written anywhere in this file. The
-- relation is populated by modernization/landing/load_redshift.sql on Amazon Redshift and
-- by modernization/landing/load_local.py on DuckDB; each loader removes any row already
-- carrying the natural key (source_system_key, policy_number) it is about to write and then
-- writes, so the motor sample row and the commercial sample row coexist and this model reads
-- every row present.
--
-- Output. The same 17 columns, under the same names and in the same order as the
-- landing.field_order block of modernization/extraction/copybook_field_map.yml, the naming
-- authority for this contract. No column is added and no column is dropped. That column set
-- is enforced: _genapp__models.yml beside this file declares contract.enforced for this
-- model and names all 17 columns with their data types, so a column added here, dropped
-- here or emitted at another type fails this model before it is materialized.
--
-- What this model does. It names every column explicitly, removes leading and trailing
-- whitespace from each value, yields null for a value that holds only whitespace, and casts
-- each value to the VARCHAR width its column declares in
-- modernization/warehouse/ddl/02_raw_genapp_policy_issue.sql. Every value stays text: no
-- value is converted to a number, a date or a timestamp, and the width cast changes no
-- value, because each landed value already fits the width the landing relation declares.
-- Type conversion is applied by the models of models/intermediate, and this model applies
-- none.
--
-- What this model does not do. It derives no value.
-- modernization/extraction/extract_commarea.py has already derived policy_type from the
-- trimmed CA-REQUEST-ID through the request routing of base/src/lgapdb01.cbl:184-207,
-- already normalised the returned 26-character CA-LASTCHANGED of base/src/lgcmarea.cpy:40 to
-- ISO-8601, and already applied the product-specific premium null pattern. No amount is
-- derived anywhere in the bridge: the three named programs base/src/lgapol01.cbl,
-- base/src/lgapdb01.cbl and base/src/lgapvs01.cbl carry no COMPUTE, MULTIPLY, DIVIDE or
-- COMP-3 statement, and each amount reaches its Db2 host variable through a plain MOVE.
--
-- Grain. One landed row yields one output row. No row is combined, no row is removed and no
-- row is added, and this model filters on no column. Every landed row reaches the output.
-- Landing admits exactly one record per successful execution of the LGAPOL01, LGAPDB01 and
-- LGAPVS01 chain: modernization/extraction/extract_commarea.py refuses a record whose returned
-- CA-RETURN-CODE is not 00 and modernization/landing/landing-schema.json admits 00 alone, so a
-- failed execution reaches neither the landing object nor this model, and every row read here
-- carries return_code 00 together with the policy number and the last-changed timestamp the
-- chain assigned. The return code is carried through verbatim as the recorded outcome of the
-- execution, and the models of models/marts/canonical restate that filter on their own reads as
-- an explicit guard.
--
-- Configuration. The view materialization and the staging schema come from the
-- models/staging/genapp_class_exemplar key of modernization/dbt/genapp_rqi/dbt_project.yml,
-- and macros/generate_schema_name.sql returns that schema name verbatim. No relation alias
-- is set, so the relation is named stg_genapp__policy_issue and the models of
-- models/intermediate reach it as ref('stg_genapp__policy_issue').
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

with landed as (

    -- Every column of the landing relation, named explicitly, in the order fixed by the
    -- landing contract. The four commercial peril codes CA-B-FirePeril, CA-B-CrimePeril,
    -- CA-B-FloodPeril and CA-B-WeatherPeril, each PIC 9(4) at base/src/lgcmarea.cpy:84,
    -- :86, :88 and :90, are code items rather than amount items and are not landed columns,
    -- so none of them is read here; the amount items are the adjacent PIC 9(8) premium
    -- declarations at base/src/lgcmarea.cpy:85, :87, :89 and :91.
    select
        source_system_key,
        policy_number,
        policy_type,
        customer_number,
        request_id,
        return_code,
        issue_date,
        expiry_date,
        last_changed,
        broker_id,
        brokers_reference,
        payment_amount,
        motor_premium_amount,
        fire_premium_amount,
        crime_premium_amount,
        flood_premium_amount,
        weather_premium_amount

    from {{ source('genapp', 'genapp_policy_issue') }}

)

select
    -- Source-system discriminator assigned by the warehouse. No COBOL source item; this is
    -- the sole warehouse-assigned column of the record. First element of the natural key.
    cast(nullif(trim(source_system_key), '') as varchar(64)) as source_system_key,

    -- Policy number recovered after the policy insert. CA-POLICY-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:35. The policy insert supplies DEFAULT for POLICYNUMBER at
    -- base/src/lgapdb01.cbl:279 and IDENTITY_VAL_LOCAL() recovers the assigned value at
    -- base/src/lgapdb01.cbl:308-311, so it exists only in the returned COMMAREA. The
    -- Db2-side DB2-POLICYNUMBER PIC 9(10), base/src/lgpolicy.cpy:44, is declaration-only.
    -- Second element of the natural key.
    cast(nullif(trim(policy_number), '') as varchar(10)) as policy_number,

    -- Product discriminator E, H, M or C. DB2-POLICYTYPE PIC X,
    -- base/src/lgpolicy.cpy:43, assigned by the request-routing EVALUATE at
    -- base/src/lgapdb01.cbl:184-207: 01AEND yields E at :188, 01AHOU yields H at :192,
    -- 01AMOT yields M at :196 and 01ACOM yields C at :200.
    cast(nullif(trim(policy_type), '') as varchar(1)) as policy_type,

    -- Customer number supplied in the request. CA-CUSTOMER-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:12, moved to DB2-CUSTOMERNUM-INT at base/src/lgapdb01.cbl:176.
    cast(nullif(trim(customer_number), '') as varchar(10)) as customer_number,

    -- Request identifier the chain routes on. CA-REQUEST-ID PIC X(6),
    -- base/src/lgcmarea.cpy:10, evaluated at base/src/lgapdb01.cbl:184.
    cast(nullif(trim(request_id), '') as varchar(6)) as request_id,

    -- Returned chain outcome. CA-RETURN-CODE PIC 9(2), base/src/lgcmarea.cpy:11. The chain
    -- assigns 00, 70, 80, 90, 98 or 99; only a record carrying 00 is landed, so every row
    -- read here holds 00. Carried through unchanged and unfiltered.
    cast(nullif(trim(return_code), '') as varchar(2)) as return_code,

    -- Policy issue date supplied in the request. CA-ISSUE-DATE PIC X(10),
    -- base/src/lgcmarea.cpy:38; Db2-side DB2-ISSUEDATE, base/src/lgpolicy.cpy:46.
    cast(nullif(trim(issue_date), '') as varchar(10)) as issue_date,

    -- Policy expiry date supplied in the request. CA-EXPIRY-DATE PIC X(10),
    -- base/src/lgcmarea.cpy:39; Db2-side DB2-EXPIRYDATE, base/src/lgpolicy.cpy:47.
    cast(nullif(trim(expiry_date), '') as varchar(10)) as expiry_date,

    -- Policy last-changed timestamp read back after the policy insert. CA-LASTCHANGED
    -- PIC X(26), base/src/lgcmarea.cpy:40; Db2-side DB2-LASTCHANGED,
    -- base/src/lgpolicy.cpy:48. The insert writes CURRENT TIMESTAMP at
    -- base/src/lgapdb01.cbl:284 and the SELECT at base/src/lgapdb01.cbl:316-321 reads the
    -- assigned value back into the COMMAREA item. Already ISO-8601 when landed.
    cast(nullif(trim(last_changed), '') as varchar(26)) as last_changed,

    -- Broker identifier supplied in the request. CA-BROKERID PIC 9(10),
    -- base/src/lgcmarea.cpy:41; Db2-side DB2-BROKERID, base/src/lgpolicy.cpy:49; moved to
    -- DB2-BROKERID-INT at base/src/lgapdb01.cbl:264.
    cast(nullif(trim(broker_id), '') as varchar(10)) as broker_id,

    -- Broker's reference supplied in the request. CA-BROKERSREF PIC X(10),
    -- base/src/lgcmarea.cpy:42; Db2-side DB2-BROKERSREF, base/src/lgpolicy.cpy:50. A
    -- blank-padded fixed-width alphanumeric window; a window of only spaces yields null.
    cast(nullif(trim(brokers_reference), '') as varchar(10)) as brokers_reference,

    -- Policy payment amount. CA-PAYMENT PIC 9(6), base/src/lgcmarea.cpy:43; Db2-side
    -- DB2-PAYMENT PIC 9(6), base/src/lgpolicy.cpy:51; moved by MOVE CA-PAYMENT TO
    -- DB2-PAYMENT-INT at base/src/lgapdb01.cbl:265, which applies no arithmetic. An
    -- unsigned DISPLAY numeric without an implied decimal. Carried for every policy type.
    cast(nullif(trim(payment_amount), '') as varchar(6)) as payment_amount,

    -- Motor premium amount. CA-M-PREMIUM PIC 9(6), base/src/lgcmarea.cpy:73; Db2-side
    -- DB2-M-PREMIUM PIC 9(6), base/src/lgpolicy.cpy:80; moved by MOVE CA-M-PREMIUM TO
    -- DB2-M-PREMIUM-INT at base/src/lgapdb01.cbl:445, which applies no arithmetic. An
    -- unsigned DISPLAY numeric without an implied decimal. Null unless policy_type is M.
    cast(nullif(trim(motor_premium_amount), '') as varchar(6)) as motor_premium_amount,

    -- Commercial fire premium amount. CA-B-FirePremium PIC 9(8),
    -- base/src/lgcmarea.cpy:85; Db2-side DB2-B-FirePremium PIC 9(8),
    -- base/src/lgpolicy.cpy:91; moved at base/src/lgapdb01.cbl:489, which applies no
    -- arithmetic. An unsigned DISPLAY numeric without an implied decimal. Null unless
    -- policy_type is C.
    cast(nullif(trim(fire_premium_amount), '') as varchar(8)) as fire_premium_amount,

    -- Commercial crime premium amount. CA-B-CrimePremium PIC 9(8),
    -- base/src/lgcmarea.cpy:87; Db2-side DB2-B-CrimePremium PIC 9(8),
    -- base/src/lgpolicy.cpy:93; moved at base/src/lgapdb01.cbl:491, which applies no
    -- arithmetic. An unsigned DISPLAY numeric without an implied decimal. Null unless
    -- policy_type is C.
    cast(nullif(trim(crime_premium_amount), '') as varchar(8)) as crime_premium_amount,

    -- Commercial flood premium amount. CA-B-FloodPremium PIC 9(8),
    -- base/src/lgcmarea.cpy:89; Db2-side DB2-B-FloodPremium PIC 9(8),
    -- base/src/lgpolicy.cpy:95; moved at base/src/lgapdb01.cbl:493, which applies no
    -- arithmetic. An unsigned DISPLAY numeric without an implied decimal. Null unless
    -- policy_type is C.
    cast(nullif(trim(flood_premium_amount), '') as varchar(8)) as flood_premium_amount,

    -- Commercial weather premium amount. CA-B-WeatherPremium PIC 9(8),
    -- base/src/lgcmarea.cpy:91; Db2-side DB2-B-WeatherPremium PIC 9(8),
    -- base/src/lgpolicy.cpy:97; moved at base/src/lgapdb01.cbl:495, which applies no
    -- arithmetic. An unsigned DISPLAY numeric without an implied decimal. Null unless
    -- policy_type is C.
    cast(nullif(trim(weather_premium_amount), '') as varchar(8)) as weather_premium_amount

from landed
