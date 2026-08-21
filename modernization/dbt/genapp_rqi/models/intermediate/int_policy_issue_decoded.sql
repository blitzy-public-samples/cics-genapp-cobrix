-- int_policy_issue_decoded.sql
-- Intermediate model of the GenApp Policy-Issue cloud-warehouse bridge, and the only model
-- of the models/intermediate subtree.
--
-- Input. ref('stg_genapp__policy_issue'), the single model of
-- models/staging/genapp_class_exemplar and the only relation this model reads. That model
-- sets no relation alias, so its model name is the reference spelling. The dbt source
-- binding of the project is held by
-- models/staging/genapp_class_exemplar/_genapp__sources.yml and is not repeated here.
--
-- Output. The same 17 columns, under the same names and in the same order as the
-- landing.field_order block of modernization/extraction/copybook_field_map.yml, the naming
-- authority for this contract, each carrying its target type. No column is added and no
-- column is dropped. The 17 columns are the union of the two canonical relations: the 11
-- columns of canonical.issued_policy and the 9 columns of canonical.preissued_rating share
-- source_system_key, policy_number and policy_type.
--
-- What this model does. It applies every type conversion of the bridge. Staging carries all
-- 17 values as text and the models of models/marts/canonical apply no conversion. The
-- types applied here are the types both canonical relations carry:
--   bigint          policy_number, customer_number, broker_id
--   date            issue_date, expiry_date
--   timestamp       last_changed
--   decimal(8,2)    payment_amount, motor_premium_amount
--   decimal(10,2)   fire_premium_amount, crime_premium_amount, flood_premium_amount,
--                   weather_premium_amount
--   text unchanged  source_system_key, policy_type, request_id, return_code,
--                   brokers_reference
-- Each nullable value yields null when it holds only whitespace, and every cast is applied
-- to that guarded value. The product discriminator is checked against the request routing of
-- base/src/lgapdb01.cbl:184-207, and the product-specific premium null pattern recorded
-- under product_premium_nullability in modernization/extraction/copybook_field_map.yml is
-- applied.
--
-- What this model does not do. It derives no value and applies no arithmetic to any amount.
-- The three named programs base/src/lgapol01.cbl, base/src/lgapdb01.cbl and
-- base/src/lgapvs01.cbl carry no COMPUTE, MULTIPLY, DIVIDE or COMP-3 statement; each amount
-- reaches its Db2 host variable through a plain MOVE; and none of the chain's seven
-- ADD and SUBTRACT statements touches an amount, each operating on a COMMAREA length
-- constant at base/src/lgapol01.cbl:109 and base/src/lgapdb01.cbl:182, :187, :191, :195,
-- :199 and :339. No value is rounded or rescaled and no implied decimal is applied. No row
-- is filtered: every staging row reaches the output, including a row whose return_code is
-- not 00, and the filter to return_code 00 is applied by the models of
-- models/marts/canonical. No column is added: this model carries no rating formula, rating
-- factor, derived factor, commission, provenance, audit, surrogate key, hash or load
-- timestamp column. The four commercial peril declarations CA-B-FirePeril,
-- CA-B-CrimePeril, CA-B-FloodPeril and CA-B-WeatherPeril, each PIC 9(4) at
-- base/src/lgcmarea.cpy:84, :86, :88 and :90, are code items rather than amount items and
-- carry no column; the amount items are the adjacent PIC 9(8) premium declarations at
-- base/src/lgcmarea.cpy:85, :87, :89 and :91. DB2-POLICYNUMBER PIC 9(10),
-- base/src/lgpolicy.cpy:44, is declaration-only and carries no column. No column derives
-- from base/src/lgapvs01.cbl.
--
-- Grain. One staging row yields one output row. No row is combined, no row is removed and
-- no row is added. The motor sample row and the commercial sample row both reach the
-- output.
--
-- Configuration. The view materialization and the intermediate schema come from the
-- models/intermediate key of modernization/dbt/genapp_rqi/dbt_project.yml, and
-- macros/generate_schema_name.sql returns that schema name verbatim. This file declares no
-- configuration of its own. No relation alias is set, so the relation is named
-- int_policy_issue_decoded and the models of models/marts/canonical reach it as
-- ref('int_policy_issue_decoded').
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4, dbt Transformation DAG and Field Allocation,
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

with staged as (

    -- Every column of the staging model, named explicitly, in the order fixed by the
    -- landing contract. Every value arrives as text.
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

    from {{ ref('stg_genapp__policy_issue') }}

),

routed as (

    -- The product discriminator checked against the request routing, and the remaining 16
    -- columns carried forward as text for the typed select below.
    select
        source_system_key,
        policy_number,

        -- Product discriminator E, H, M or C. DB2-POLICYTYPE PIC X,
        -- base/src/lgpolicy.cpy:43, assigned by the request-routing EVALUATE at
        -- base/src/lgapdb01.cbl:184-207 and passed to the policy insert at
        -- base/src/lgapdb01.cbl:283. The routing recognises four request ids: 01AEND
        -- yields E at base/src/lgapdb01.cbl:188, 01AHOU yields H at :192, 01AMOT yields M
        -- at :196 and 01ACOM yields C at :200; the WHEN OTHER branch at :202-205 sets
        -- return code 99 and returns. modernization/extraction/extract_commarea.py derives
        -- the letter from the trimmed CA-REQUEST-ID through that same routing before
        -- landing. Each branch below carries the landed letter through only where it
        -- agrees with the request id; the four branches are the whole routing, and a
        -- landed letter that agrees with no branch yields null.
        case
            when trim(request_id) = '01AEND' and trim(policy_type) = 'E'
                then trim(policy_type)
            when trim(request_id) = '01AHOU' and trim(policy_type) = 'H'
                then trim(policy_type)
            when trim(request_id) = '01AMOT' and trim(policy_type) = 'M'
                then trim(policy_type)
            when trim(request_id) = '01ACOM' and trim(policy_type) = 'C'
                then trim(policy_type)
        end as policy_type,

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

    from staged

)

select
    -- Source-system discriminator assigned by the warehouse. No COBOL source item supplies
    -- it: this is the sole warehouse-assigned column of the record and of the whole design,
    -- and its evidence is the user requirement rather than a source locator. Carried
    -- unchanged as text. VARCHAR(64) in both canonical relations. First element of the
    -- natural key (source_system_key, policy_number).
    nullif(trim(source_system_key), '') as source_system_key,

    -- Policy number recovered after the policy insert. CA-POLICY-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:35. The policy insert supplies the literal DEFAULT for
    -- POLICYNUMBER at base/src/lgapdb01.cbl:279, IDENTITY_VAL_LOCAL() loads
    -- DB2-POLICYNUM-INT at base/src/lgapdb01.cbl:308-310 and base/src/lgapdb01.cbl:311
    -- moves the recovered value into the COMMAREA item, so the value exists only in the
    -- returned COMMAREA. Cast to bigint. Second element of the natural key.
    cast(nullif(trim(policy_number), '') as bigint) as policy_number,

    -- Product discriminator verified against the request routing in the routed block
    -- above. DB2-POLICYTYPE PIC X, base/src/lgpolicy.cpy:43. Carried as text and cast to
    -- char(1) by neither this model nor the marts. Decides the premium null pattern below.
    policy_type,

    -- Customer number supplied in the request. CA-CUSTOMER-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:12, moved to DB2-CUSTOMERNUM-INT at
    -- base/src/lgapdb01.cbl:176 and passed to the policy insert at
    -- base/src/lgapdb01.cbl:280. Cast to bigint.
    cast(nullif(trim(customer_number), '') as bigint) as customer_number,

    -- Request identifier the chain routes on. CA-REQUEST-ID PIC X(6),
    -- base/src/lgcmarea.cpy:10, evaluated at base/src/lgapdb01.cbl:184. Carried unchanged
    -- as text. VARCHAR(6) in canonical.issued_policy.
    nullif(trim(request_id), '') as request_id,

    -- Returned chain outcome. CA-RETURN-CODE PIC 9(2), base/src/lgcmarea.cpy:11. Each of
    -- the fourteen write sites moves a quoted two-character literal, at
    -- base/src/lgapol01.cbl:105 and :114, base/src/lgapdb01.cbl:172, :204, :211, :239,
    -- :293, :296, :301, :390, :428, :474 and :548, and base/src/lgapvs01.cbl:144. The six
    -- observed values are 00 success, 70 policy insert returned SQLCODE -530, 80 VSAM
    -- write response was not normal, 90 SQL failure, 98 COMMAREA shorter than the required
    -- length and 99 unsupported request id. Carried unchanged as text, with its leading
    -- zero preserved and no row filtered on it. CHAR(2) in canonical.issued_policy.
    nullif(trim(return_code), '') as return_code,

    -- Policy issue date supplied in the request. CA-ISSUE-DATE PIC X(10),
    -- base/src/lgcmarea.cpy:38; Db2-side DB2-ISSUEDATE PIC X(10),
    -- base/src/lgpolicy.cpy:46; passed to the policy insert as a character host variable
    -- at base/src/lgapdb01.cbl:281. Landed as YYYY-MM-DD and cast to date.
    cast(nullif(trim(issue_date), '') as date) as issue_date,

    -- Policy expiry date supplied in the request. CA-EXPIRY-DATE PIC X(10),
    -- base/src/lgcmarea.cpy:39; Db2-side DB2-EXPIRYDATE PIC X(10),
    -- base/src/lgpolicy.cpy:47; passed to the policy insert as a character host variable
    -- at base/src/lgapdb01.cbl:282. Landed as YYYY-MM-DD and cast to date.
    cast(nullif(trim(expiry_date), '') as date) as expiry_date,

    -- Policy last-changed timestamp read back after the policy insert. CA-LASTCHANGED
    -- PIC X(26), base/src/lgcmarea.cpy:40; Db2-side DB2-LASTCHANGED PIC X(26),
    -- base/src/lgpolicy.cpy:48. The insert writes CURRENT TIMESTAMP at
    -- base/src/lgapdb01.cbl:284 and the SELECT keyed on the recovered policy number at
    -- base/src/lgapdb01.cbl:316-321 reads the assigned value back into the COMMAREA item.
    -- modernization/extraction/extract_commarea.py normalises the returned 26-character
    -- value to ISO-8601 before landing. It arrives written YYYY-MM-DDTHH:MM:SS.ffffff.
    -- Cast to timestamp.
    cast(nullif(trim(last_changed), '') as timestamp) as last_changed,

    -- Broker identifier supplied in the request. CA-BROKERID PIC 9(10),
    -- base/src/lgcmarea.cpy:41; Db2-side DB2-BROKERID PIC 9(10),
    -- base/src/lgpolicy.cpy:49; moved to DB2-BROKERID-INT at base/src/lgapdb01.cbl:264 and
    -- passed to the policy insert at base/src/lgapdb01.cbl:285. Cast to bigint.
    cast(nullif(trim(broker_id), '') as bigint) as broker_id,

    -- Broker's reference supplied in the request. CA-BROKERSREF PIC X(10),
    -- base/src/lgcmarea.cpy:42; Db2-side DB2-BROKERSREF PIC X(10),
    -- base/src/lgpolicy.cpy:50; passed to the policy insert as a character host variable at
    -- base/src/lgapdb01.cbl:286. A blank-padded fixed-width alphanumeric window, carried
    -- unchanged as text. VARCHAR(10) in canonical.issued_policy.
    nullif(trim(brokers_reference), '') as brokers_reference,

    -- Policy payment amount. CA-PAYMENT PIC 9(6), base/src/lgcmarea.cpy:43; Db2-side
    -- DB2-PAYMENT PIC 9(6), base/src/lgpolicy.cpy:51; moved by MOVE CA-PAYMENT TO
    -- DB2-PAYMENT-INT at base/src/lgapdb01.cbl:265 and passed to the policy insert at
    -- base/src/lgapdb01.cbl:287. An unsigned DISPLAY numeric without an implied decimal,
    -- declaring 6 digits, cast to decimal(8,2) and otherwise unchanged. Declared in the
    -- product-independent group CA-POLICY-COMMON at base/src/lgcmarea.cpy:37-43. Carries a
    -- value for every policy type, and no product test is applied to it.
    cast(nullif(trim(payment_amount), '') as decimal(8, 2)) as payment_amount,

    -- Motor premium amount. CA-M-PREMIUM PIC 9(6), base/src/lgcmarea.cpy:73; Db2-side
    -- DB2-M-PREMIUM PIC 9(6), base/src/lgpolicy.cpy:80; moved by MOVE CA-M-PREMIUM TO
    -- DB2-M-PREMIUM-INT at base/src/lgapdb01.cbl:445 and passed to the motor insert at
    -- base/src/lgapdb01.cbl:469. An unsigned DISPLAY numeric without an implied decimal,
    -- declaring 6 digits, cast to decimal(8,2) and otherwise unchanged. Declared in the
    -- CA-MOTOR overlay at base/src/lgcmarea.cpy:65, one of the REDEFINES of
    -- CA-POLICY-SPECIFIC PIC X(32400) at base/src/lgcmarea.cpy:44, which the endowment,
    -- house, commercial and claim overlays at base/src/lgcmarea.cpy:46, :56, :77 and :96
    -- also redefine. Carried for policy type M; null for every other policy type, and
    -- never zero.
    case
        when policy_type = 'M'
            then cast(nullif(trim(motor_premium_amount), '') as decimal(8, 2))
    end as motor_premium_amount,

    -- Commercial fire premium amount. CA-B-FirePremium PIC 9(8),
    -- base/src/lgcmarea.cpy:85; Db2-side DB2-B-FirePremium PIC 9(8),
    -- base/src/lgpolicy.cpy:91; moved at base/src/lgapdb01.cbl:489 and passed to the
    -- commercial insert at base/src/lgapdb01.cbl:535. An unsigned DISPLAY numeric without
    -- an implied decimal, declaring 8 digits, cast to decimal(10,2) and otherwise
    -- unchanged. Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77.
    -- Carried for policy type C; null for every other policy type, and never zero.
    case
        when policy_type = 'C'
            then cast(nullif(trim(fire_premium_amount), '') as decimal(10, 2))
    end as fire_premium_amount,

    -- Commercial crime premium amount. CA-B-CrimePremium PIC 9(8),
    -- base/src/lgcmarea.cpy:87; Db2-side DB2-B-CrimePremium PIC 9(8),
    -- base/src/lgpolicy.cpy:93; moved at base/src/lgapdb01.cbl:491 and passed to the
    -- commercial insert at base/src/lgapdb01.cbl:537. An unsigned DISPLAY numeric without
    -- an implied decimal, declaring 8 digits, cast to decimal(10,2) and otherwise
    -- unchanged. Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77.
    -- Carried for policy type C; null for every other policy type, and never zero.
    case
        when policy_type = 'C'
            then cast(nullif(trim(crime_premium_amount), '') as decimal(10, 2))
    end as crime_premium_amount,

    -- Commercial flood premium amount. CA-B-FloodPremium PIC 9(8),
    -- base/src/lgcmarea.cpy:89; Db2-side DB2-B-FloodPremium PIC 9(8),
    -- base/src/lgpolicy.cpy:95; moved at base/src/lgapdb01.cbl:493 and passed to the
    -- commercial insert at base/src/lgapdb01.cbl:539. An unsigned DISPLAY numeric without
    -- an implied decimal, declaring 8 digits, cast to decimal(10,2) and otherwise
    -- unchanged. Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77.
    -- Carried for policy type C; null for every other policy type, and never zero.
    case
        when policy_type = 'C'
            then cast(nullif(trim(flood_premium_amount), '') as decimal(10, 2))
    end as flood_premium_amount,

    -- Commercial weather premium amount. CA-B-WeatherPremium PIC 9(8),
    -- base/src/lgcmarea.cpy:91; Db2-side DB2-B-WeatherPremium PIC 9(8),
    -- base/src/lgpolicy.cpy:97; moved at base/src/lgapdb01.cbl:495 and passed to the
    -- commercial insert at base/src/lgapdb01.cbl:541. An unsigned DISPLAY numeric without
    -- an implied decimal, declaring 8 digits, cast to decimal(10,2) and otherwise
    -- unchanged. Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77.
    -- Carried for policy type C; null for every other policy type, and never zero.
    case
        when policy_type = 'C'
            then cast(nullif(trim(weather_premium_amount), '') as decimal(10, 2))
    end as weather_premium_amount

from routed
