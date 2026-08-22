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
-- column is dropped. That column set is enforced: _int__models.yml beside this file declares
-- contract.enforced for this model and names all 17 columns with their data types, so a
-- column added here, dropped here or emitted at another data type fails this model before it
-- is materialized. The 17 columns are the union of the two canonical relations: the 11
-- columns of canonical.issued_policy and the 9 columns of canonical.preissued_rating share
-- source_system_key, policy_number and policy_type.
--
-- What this model does. It converts every value of the bridge out of text. Staging carries
-- all 17 values as text; the models of models/marts/canonical convert nothing out of text
-- and cast their five character columns to the widths the canonical contract fixes. The
-- types applied here are the types both canonical relations carry:
--   bigint          policy_number, customer_number, broker_id
--   date            issue_date, expiry_date
--   timestamp       last_changed
--   decimal(8,2)    payment_amount, motor_premium_amount
--   decimal(10,2)   fire_premium_amount, crime_premium_amount, flood_premium_amount,
--                   weather_premium_amount
--   varchar(64)     source_system_key
--   char(1)         policy_type
--   varchar(6)      request_id
--   char(2)         return_code
--   varchar(10)     brokers_reference
-- Each nullable value yields null when it holds only whitespace, and every cast is applied
-- to that guarded value. The product discriminator is checked against the request routing of
-- base/src/lgapdb01.cbl:184-207, and the product-specific premium null pattern recorded
-- under product_premium_nullability in modernization/extraction/copybook_field_map.yml is
-- applied.
--
-- What this model assumes of its input, and what it does with input that breaks the
-- assumption. modernization/extraction/extract_commarea.py validates every landed value
-- before the record is written: issue_date and expiry_date are real calendar dates written
-- YYYY-MM-DD, last_changed is the returned 26-character Db2 read-back of
-- base/src/lgapdb01.cbl:315-321 normalised to YYYY-MM-DDTHH:MM:SS.ffffff with a real
-- calendar date and a real clock time, and each applicable amount window is all digits.
-- modernization/landing/landing-schema.json restates the written form of each of those
-- values as a pattern, and both raw loaders validate the record against that schema before
-- inserting it. The casts below are therefore total over the landing contract. A value that
-- reaches this model outside it -- 2026-02-30, 2026-08-19T25:00:00.000000 or a non-numeric
-- amount -- fails its cast when a consumer reads this view. The relationships tests of
-- _int__models.yml read every date, timestamp and amount cast, so such a value fails those
-- tests, dbt then skips both models of models/marts/canonical, and no such row reaches a
-- canonical relation.
--
-- What this model does not do. It derives no value and applies no arithmetic to any amount.
-- The three named programs base/src/lgapol01.cbl, base/src/lgapdb01.cbl and
-- base/src/lgapvs01.cbl carry no COMPUTE, MULTIPLY, DIVIDE or COMP-3 statement; each amount
-- reaches its Db2 host variable through a plain MOVE; and none of the chain's seven
-- ADD and SUBTRACT statements touches an amount, each operating on a COMMAREA length
-- constant at base/src/lgapol01.cbl:109 and base/src/lgapdb01.cbl:182, :187, :191, :195,
-- :199 and :339. No value is rounded or rescaled and no implied decimal is applied. Each
-- typed amount below is exactly the landed digit string of its own column, guarded by
-- nullif(trim(...), '') and cast to its target type: no arithmetic operator, no default, no
-- other column and no literal takes part in it, and the only condition on it is the routed
-- policy type of the row. No row is filtered: every staging row reaches the output. Landing
-- admits exactly one record per successful execution of the LGAPOL01, LGAPDB01 and LGAPVS01
-- chain: modernization/extraction/extract_commarea.py refuses a record whose returned
-- CA-RETURN-CODE is not 00 and modernization/landing/landing-schema.json admits 00 alone, so
-- every row read here carries return_code 00 together with the policy number and the
-- last-changed timestamp the chain assigned. The return code is carried through as the
-- recorded outcome of the execution, and the models of models/marts/canonical restate that
-- filter on their own reads as an explicit guard. No column is added: this
-- model carries no rating formula, rating factor, derived factor, commission, provenance,
-- audit, surrogate key, hash or load timestamp column. The four commercial peril
-- declarations CA-B-FirePeril, CA-B-CrimePeril, CA-B-FloodPeril and CA-B-WeatherPeril, each
-- PIC 9(4) at base/src/lgcmarea.cpy:84, :86, :88 and :90, are code items rather than amount
-- items and carry no column; the amount items are the adjacent PIC 9(8) premium declarations
-- at base/src/lgcmarea.cpy:85, :87, :89 and :91. DB2-POLICYNUMBER PIC 9(10),
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
-- configuration of its own; the enforced contract is declared in _int__models.yml beside it.
-- No relation alias is set, so the relation is named int_policy_issue_decoded and the models
-- of models/marts/canonical reach it as ref('int_policy_issue_decoded').
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
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
    -- and its evidence is the user requirement rather than a source locator. Cast to
    -- varchar(64), the type both canonical relations carry. First element of the
    -- natural key (source_system_key, policy_number).
    cast(nullif(trim(source_system_key), '') as varchar(64)) as source_system_key,

    -- Policy number recovered after the policy insert. CA-POLICY-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:35. The policy insert supplies the literal DEFAULT for
    -- POLICYNUMBER at base/src/lgapdb01.cbl:279, IDENTITY_VAL_LOCAL() loads
    -- DB2-POLICYNUM-INT at base/src/lgapdb01.cbl:308-310 and base/src/lgapdb01.cbl:311
    -- moves the recovered value into the COMMAREA item, so the value exists only in the
    -- returned COMMAREA. Cast to bigint. Second element of the natural key.
    cast(nullif(trim(policy_number), '') as bigint) as policy_number,

    -- Product discriminator verified against the request routing in the routed block
    -- above. DB2-POLICYTYPE PIC X, base/src/lgpolicy.cpy:43. Cast to char(1), the type both
    -- canonical relations carry. Decides the premium null pattern below.
    cast(policy_type as char(1)) as policy_type,

    -- Customer number supplied in the request. CA-CUSTOMER-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:12, moved to DB2-CUSTOMERNUM-INT at
    -- base/src/lgapdb01.cbl:176 and passed to the policy insert at
    -- base/src/lgapdb01.cbl:280. Cast to bigint.
    cast(nullif(trim(customer_number), '') as bigint) as customer_number,

    -- Request identifier the chain routes on. CA-REQUEST-ID PIC X(6),
    -- base/src/lgcmarea.cpy:10, evaluated at base/src/lgapdb01.cbl:184. Cast to
    -- varchar(6), the type canonical.issued_policy carries.
    cast(nullif(trim(request_id), '') as varchar(6)) as request_id,

    -- Returned chain outcome. CA-RETURN-CODE PIC 9(2), base/src/lgcmarea.cpy:11. Each of
    -- the fourteen write sites moves a quoted two-character literal, at
    -- base/src/lgapol01.cbl:105 and :114, base/src/lgapdb01.cbl:172, :204, :211, :239,
    -- :293, :296, :301, :390, :428, :474 and :548, and base/src/lgapvs01.cbl:144. The six
    -- values the chain assigns are 00 success, 70 policy insert returned SQLCODE -530, 80
    -- VSAM write response was not normal, 90 SQL failure, 98 COMMAREA shorter than the
    -- required length and 99 unsupported request id; only a record carrying 00 is landed, so
    -- every row here holds 00. Carried unchanged, with its leading zero preserved and no row
    -- filtered on it. Cast to char(2), the type canonical.issued_policy carries.
    cast(nullif(trim(return_code), '') as char(2)) as return_code,

    -- Policy issue date supplied in the request. CA-ISSUE-DATE PIC X(10),
    -- base/src/lgcmarea.cpy:38; Db2-side DB2-ISSUEDATE PIC X(10),
    -- base/src/lgpolicy.cpy:46; passed to the policy insert as a character host variable
    -- at base/src/lgapdb01.cbl:281. Landed as a real calendar date written YYYY-MM-DD, a
    -- value modernization/extraction/extract_commarea.py resolves as a calendar date before
    -- landing and modernization/landing/landing-schema.json restates as a pattern. Cast to
    -- date, which yields the same calendar day and no time part. A value outside that
    -- contract fails this cast and aborts the model.
    cast(nullif(trim(issue_date), '') as date) as issue_date,

    -- Policy expiry date supplied in the request. CA-EXPIRY-DATE PIC X(10),
    -- base/src/lgcmarea.cpy:39; Db2-side DB2-EXPIRYDATE PIC X(10),
    -- base/src/lgpolicy.cpy:47; passed to the policy insert as a character host variable
    -- at base/src/lgapdb01.cbl:282. Landed as a real calendar date written YYYY-MM-DD, a
    -- value modernization/extraction/extract_commarea.py resolves as a calendar date before
    -- landing and modernization/landing/landing-schema.json restates as a pattern. Cast to
    -- date, which yields the same calendar day and no time part. A value outside that
    -- contract fails this cast and aborts the model. No ordering against issue_date is
    -- asserted here: the chain asserts none.
    cast(nullif(trim(expiry_date), '') as date) as expiry_date,

    -- Policy last-changed timestamp read back after the policy insert. CA-LASTCHANGED
    -- PIC X(26), base/src/lgcmarea.cpy:40; Db2-side DB2-LASTCHANGED PIC X(26),
    -- base/src/lgpolicy.cpy:48. The insert writes CURRENT TIMESTAMP at
    -- base/src/lgapdb01.cbl:284 and the SELECT keyed on the recovered policy number at
    -- base/src/lgapdb01.cbl:316-321 reads the assigned value back into the COMMAREA item.
    -- modernization/extraction/extract_commarea.py resolves the returned 26-character value
    -- as a calendar date and a clock time and normalises it to ISO-8601 before landing, and
    -- modernization/landing/landing-schema.json restates the written form as a pattern. It
    -- arrives written YYYY-MM-DDTHH:MM:SS.ffffff, 26 characters wide. Cast to timestamp,
    -- which yields the same instant to microsecond precision and applies no time zone. A
    -- value outside that contract fails this cast and aborts the model.
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
    -- unchanged and cast to varchar(10), the type canonical.issued_policy carries.
    cast(nullif(trim(brokers_reference), '') as varchar(10)) as brokers_reference,

    -- Policy payment amount. CA-PAYMENT PIC 9(6), base/src/lgcmarea.cpy:43; Db2-side
    -- DB2-PAYMENT PIC 9(6), base/src/lgpolicy.cpy:51; moved by MOVE CA-PAYMENT TO
    -- DB2-PAYMENT-INT at base/src/lgapdb01.cbl:265 and passed to the policy insert at
    -- base/src/lgapdb01.cbl:287. An unsigned DISPLAY numeric without an implied decimal,
    -- declaring 6 digits, cast to decimal(8,2) and otherwise unchanged: the expression is
    -- the landed digit string of this column and nothing else, and no arithmetic operator,
    -- default, literal or other column takes part in it. Declared in the
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
    -- also redefine. The expression is the landed digit string of this column and nothing
    -- else, and no arithmetic operator, default, literal or other column takes part in it.
    -- The CASE reads the verified policy_type of the row and nothing else, so the value is
    -- carried for policy type M and is null -- never zero -- for every other policy type.
    case
        when policy_type = 'M'
            then cast(nullif(trim(motor_premium_amount), '') as decimal(8, 2))
    end as motor_premium_amount,

    -- Commercial fire premium amount. CA-B-FirePremium PIC 9(8),
    -- base/src/lgcmarea.cpy:85; Db2-side DB2-B-FirePremium PIC 9(8),
    -- base/src/lgpolicy.cpy:91; moved at base/src/lgapdb01.cbl:489 and passed to the
    -- commercial insert at base/src/lgapdb01.cbl:535. An unsigned DISPLAY numeric without
    -- an implied decimal, declaring 8 digits, cast to decimal(10,2) and otherwise
    -- unchanged. Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77. The
    -- expression is the landed digit string of this column and nothing else, and no
    -- arithmetic operator, default, literal or other column takes part in it. The CASE reads
    -- the verified policy_type of the row and nothing else, so the value is carried for
    -- policy type C and is null -- never zero -- for every other policy type.
    case
        when policy_type = 'C'
            then cast(nullif(trim(fire_premium_amount), '') as decimal(10, 2))
    end as fire_premium_amount,

    -- Commercial crime premium amount. CA-B-CrimePremium PIC 9(8),
    -- base/src/lgcmarea.cpy:87; Db2-side DB2-B-CrimePremium PIC 9(8),
    -- base/src/lgpolicy.cpy:93; moved at base/src/lgapdb01.cbl:491 and passed to the
    -- commercial insert at base/src/lgapdb01.cbl:537. An unsigned DISPLAY numeric without
    -- an implied decimal, declaring 8 digits, cast to decimal(10,2) and otherwise
    -- unchanged. Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77. The
    -- expression is the landed digit string of this column and nothing else, and no
    -- arithmetic operator, default, literal or other column takes part in it. The CASE reads
    -- the verified policy_type of the row and nothing else, so the value is carried for
    -- policy type C and is null -- never zero -- for every other policy type.
    case
        when policy_type = 'C'
            then cast(nullif(trim(crime_premium_amount), '') as decimal(10, 2))
    end as crime_premium_amount,

    -- Commercial flood premium amount. CA-B-FloodPremium PIC 9(8),
    -- base/src/lgcmarea.cpy:89; Db2-side DB2-B-FloodPremium PIC 9(8),
    -- base/src/lgpolicy.cpy:95; moved at base/src/lgapdb01.cbl:493 and passed to the
    -- commercial insert at base/src/lgapdb01.cbl:539. An unsigned DISPLAY numeric without
    -- an implied decimal, declaring 8 digits, cast to decimal(10,2) and otherwise
    -- unchanged. Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77. The
    -- expression is the landed digit string of this column and nothing else, and no
    -- arithmetic operator, default, literal or other column takes part in it. The CASE reads
    -- the verified policy_type of the row and nothing else, so the value is carried for
    -- policy type C and is null -- never zero -- for every other policy type.
    case
        when policy_type = 'C'
            then cast(nullif(trim(flood_premium_amount), '') as decimal(10, 2))
    end as flood_premium_amount,

    -- Commercial weather premium amount. CA-B-WeatherPremium PIC 9(8),
    -- base/src/lgcmarea.cpy:91; Db2-side DB2-B-WeatherPremium PIC 9(8),
    -- base/src/lgpolicy.cpy:97; moved at base/src/lgapdb01.cbl:495 and passed to the
    -- commercial insert at base/src/lgapdb01.cbl:541. An unsigned DISPLAY numeric without
    -- an implied decimal, declaring 8 digits, cast to decimal(10,2) and otherwise
    -- unchanged. Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77. The
    -- expression is the landed digit string of this column and nothing else, and no
    -- arithmetic operator, default, literal or other column takes part in it. The CASE reads
    -- the verified policy_type of the row and nothing else, so the value is carried for
    -- policy type C and is null -- never zero -- for every other policy type.
    case
        when policy_type = 'C'
            then cast(nullif(trim(weather_premium_amount), '') as decimal(10, 2))
    end as weather_premium_amount

from routed
