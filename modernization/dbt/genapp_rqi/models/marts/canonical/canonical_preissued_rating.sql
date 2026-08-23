-- canonical_preissued_rating.sql
-- Mart model of the GenApp Policy-Issue cloud-warehouse bridge, and one of the two models
-- of the models/marts/canonical subtree. Defines the canonical relation
-- canonical.preissued_rating.
--
-- Meaning. One row per successful issued policy and source system: the premium and payment
-- amounts of a policy-issue request the named chain completed with return code 00.
--
-- Grain. One row per (source_system_key, policy_number). One row of the intermediate model
-- whose return_code is 00 yields one row here. No row is combined, no row is added and no
-- row is removed beyond the return-code filter. The motor sample row and the commercial
-- sample row both reach the output.
--
-- Input. ref('int_policy_issue_decoded'), the single model of models/intermediate and the
-- only relation this model reads. That model sets no relation alias, so its model name is
-- the reference spelling. The dbt source binding of the project is declared in
-- models/staging/genapp_class_exemplar/_genapp__sources.yml and is read by the staging
-- model alone; no source binding appears in this file, and no relation is named here
-- outside the ref above.
--
-- Output. The 9 columns of canonical.preissued_rating, under the names, in the order and
-- with the types recorded in the targets: canonical.preissued_rating block of
-- modernization/extraction/copybook_field_map.yml, the naming authority for this contract.
-- Eight are source-derived and source_system_key is warehouse-assigned. The six amount
-- columns and policy_number carry the types the intermediate model applies; the two
-- character columns carry the width the select list below casts to. Each type below is the
-- data_type the contract of models/marts/canonical/_canonical__models.yml enforces. The two
-- text widths are the logical widths of that contract: Amazon Redshift stores them as
-- declared and DuckDB reports both columns as varchar, enforcing no length. The six amount
-- types are stored as declared on either adapter:
--   source_system_key       VARCHAR(64)    not null
--   policy_number           BIGINT         not null
--   policy_type             CHAR(1)        not null
--   payment_amount          DECIMAL(8,2)   nullable
--   motor_premium_amount    DECIMAL(8,2)   nullable
--   fire_premium_amount     DECIMAL(10,2)  nullable
--   crime_premium_amount    DECIMAL(10,2)  nullable
--   flood_premium_amount    DECIMAL(10,2)  nullable
--   weather_premium_amount  DECIMAL(10,2)  nullable
-- The six amount columns are the whole premium and payment surface of the warehouse and
-- appear on no other relation. source_system_key, policy_number and policy_type are the
-- three columns this relation shares with canonical.issued_policy.
--
-- What this model does. It names the 9 columns explicitly, casts source_system_key and
-- policy_type to the character widths the enforced contract in _canonical__models.yml
-- declares for them, varchar(64) and char(1), keeps the rows whose return_code is 00, and
-- materializes them as a table. A cast to a character width changes no character of a
-- value: modernization/landing/landing-schema.json accepts at most 64 characters for the
-- source-system key and exactly one of E, H, M and C for the policy type, so both values
-- are already within the width cast here. Every other value passes through unchanged.
--
-- Where the declared width is observable. Amazon Redshift carries the declared width and
-- character_maximum_length reports it; DuckDB collapses varchar(n) and char(n) to VARCHAR,
-- reports no character_maximum_length and enforces no width, so the widths of the two
-- columns are asserted from the value side by
-- modernization/dbt/genapp_rqi/tests/assert_preissued_rating_unique_key.sql, which also
-- compares both values with their upstream values and asserts the physical column set of
-- this relation, including the precision and the scale of the six amount columns, against
-- the contract.
--
-- What this model does not do. It converts no value from text and changes no numeric,
-- date or timestamp type: every cast from text, every trim and every null guard of the
-- bridge is applied by models/intermediate/int_policy_issue_decoded.sql and none is
-- repeated here, and the six amount columns and policy_number arrive carrying their
-- contract type. It applies no arithmetic to any amount and derives no value. The
-- three named programs base/src/lgapol01.cbl, base/src/lgapdb01.cbl and
-- base/src/lgapvs01.cbl carry no COMPUTE, MULTIPLY, DIVIDE or COMP-3 statement, each amount
-- reaches its Db2 host variable through a plain MOVE, and the named source carries no
-- premium formula, rating factor or derived factor. No amount is rounded, rescaled, summed
-- or defaulted to zero, and no implied decimal is applied. The comparison tolerance
-- recorded under comparison.amount_tolerance_abs in
-- modernization/extraction/copybook_field_map.yml is applied by no expression in this
-- file: modernization/dbt/genapp_rqi/tests/assert_product_premium_nullability.sql applies
-- it to the comparison of each amount of this relation with the value
-- ref('int_policy_issue_decoded') carries for the same key, alongside its assertions of the
-- presence pattern, the non-negative domain and the source-domain magnitude of each amount,
-- and modernization/validation/diff_harness_vs_warehouse.py applies it to the harness
-- capture; that comparison is recorded in
-- modernization/validation/artifacts/diff-report.md under the disposition
-- validated against local substitute, not AWS.
-- It re-derives no product null pattern: the pattern arrives from the intermediate model
-- and is carried through. It adds no column: no return_code column, no premium formula,
-- rating factor, derived factor, commission, provenance, audit, surrogate key, hash or load
-- timestamp column, and no peril column. CA-B-FirePeril, CA-B-CrimePeril, CA-B-FloodPeril
-- and CA-B-WeatherPeril, each PIC 9(4) at base/src/lgcmarea.cpy:84, :86, :88 and :90, are
-- code items rather than amount items; the amount items are the adjacent PIC 9(8) premium
-- declarations at base/src/lgcmarea.cpy:85, :87, :89 and :91. DB2-POLICYNUMBER PIC 9(10),
-- base/src/lgpolicy.cpy:44, is declaration-only and carries no column. No column derives
-- from base/src/lgapvs01.cbl. No row is deduplicated and no row is collapsed.
--
-- Product null pattern carried from the intermediate model. payment_amount is declared in
-- the product-independent group CA-POLICY-COMMON at base/src/lgcmarea.cpy:37-43 and carries
-- a value for every policy type. Each product premium is declared in an overlay of
-- CA-POLICY-SPECIFIC PIC X(32400), base/src/lgcmarea.cpy:44, which the endowment, house,
-- motor, commercial and claim overlays at base/src/lgcmarea.cpy:46, :56, :65, :77 and :96
-- each redefine; those overlays occupy the same bytes and are mutually exclusive. A row of
-- policy type M carries motor_premium_amount, a row of policy type C carries the four
-- commercial premiums, and a row of policy type E or H carries no product premium. Every
-- inapplicable product premium is null and never zero.
--
-- Configuration. This file declares one config key, the relation alias preissued_rating,
-- which names the relation canonical.preissued_rating. The table materialization and the
-- canonical schema come from the models/marts/canonical key of
-- modernization/dbt/genapp_rqi/dbt_project.yml, and macros/generate_schema_name.sql returns
-- that schema name verbatim; neither is declared here.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- The column contract and the column-level lineage of this relation are held by
-- models/marts/canonical/_canonical__models.yml.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

{{ config(alias='preissued_rating') }}

with decoded as (

    -- The 9 columns of this relation read from the intermediate model in contract order,
    -- followed by return_code, which the where clause at the foot of this file reads and
    -- the select list below does not carry. policy_number and the six amounts arrive
    -- carrying their contract type; source_system_key and policy_type arrive as text for
    -- the select list below to cast to their contract width.
    select
        source_system_key,
        policy_number,
        policy_type,
        payment_amount,
        motor_premium_amount,
        fire_premium_amount,
        crime_premium_amount,
        flood_premium_amount,
        weather_premium_amount,
        return_code

    from {{ ref('int_policy_issue_decoded') }}

)

select

    -- 1. Source-system discriminator assigned by the warehouse. No COBOL source item
    -- supplies it: it is the sole warehouse-assigned column of this relation, and its
    -- evidence is the user requirement rather than a source locator. VARCHAR(64), not null.
    -- First element of the natural key (source_system_key, policy_number), whose uniqueness
    -- tests/assert_preissued_rating_unique_key.sql asserts. A row of a future source system
    -- carries its own value in this column and needs no change to this relation.
    cast(source_system_key as varchar(64)) as source_system_key,

    -- 2. Policy number recovered after the policy insert. CA-POLICY-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:35. The policy insert supplies the literal DEFAULT for
    -- POLICYNUMBER at base/src/lgapdb01.cbl:279, IDENTITY_VAL_LOCAL() loads
    -- DB2-POLICYNUM-INT at base/src/lgapdb01.cbl:308-310, and base/src/lgapdb01.cbl:311
    -- moves the recovered value into the COMMAREA item, so the value exists only in the
    -- returned COMMAREA. BIGINT, not null. Second element of the natural key. The same
    -- value canonical.issued_policy carries for the same policy.
    policy_number,

    -- 3. Product discriminator. DB2-POLICYTYPE PIC X, base/src/lgpolicy.cpy:43, assigned by
    -- the request-routing EVALUATE at base/src/lgapdb01.cbl:184-207, where 01AEND yields E
    -- at :188, 01AHOU yields H at :192, 01AMOT yields M at :196 and 01ACOM yields C at
    -- :200, and passed to the policy insert at base/src/lgapdb01.cbl:283. It is not a
    -- COMMAREA item: modernization/extraction/extract_commarea.py derived the letter from
    -- the trimmed CA-REQUEST-ID before landing and the intermediate model checked it against
    -- that routing. CHAR(1), not null. The same discriminator canonical.issued_policy
    -- carries, and the value that decides which product premium columns below hold a value.
    cast(policy_type as char(1)) as policy_type,

    -- 4. Policy payment amount. CA-PAYMENT PIC 9(6), base/src/lgcmarea.cpy:43; Db2-side
    -- DB2-PAYMENT PIC 9(6), base/src/lgpolicy.cpy:51. MOVE CA-PAYMENT TO DB2-PAYMENT-INT at
    -- base/src/lgapdb01.cbl:265 loads DB2-PAYMENT-INT PIC S9(9) COMP,
    -- base/src/lgapdb01.cbl:92, and base/src/lgapdb01.cbl:287 passes it to the policy
    -- insert. An unsigned DISPLAY numeric without an implied decimal, declaring 6 digits.
    -- DECIMAL(8,2). Declared in CA-POLICY-COMMON and carried for every policy type.
    payment_amount,

    -- 5. Motor premium amount. CA-M-PREMIUM PIC 9(6), base/src/lgcmarea.cpy:73; Db2-side
    -- DB2-M-PREMIUM PIC 9(6), base/src/lgpolicy.cpy:80. MOVE CA-M-PREMIUM TO
    -- DB2-M-PREMIUM-INT at base/src/lgapdb01.cbl:445 loads DB2-M-PREMIUM-int PIC S9(9)
    -- COMP, base/src/lgapdb01.cbl:100, and base/src/lgapdb01.cbl:469 passes it to the motor
    -- insert. An unsigned DISPLAY numeric without an implied decimal, declaring 6 digits.
    -- DECIMAL(8,2). Declared in the CA-MOTOR overlay at base/src/lgcmarea.cpy:65. Holds a
    -- value for policy type M; null for every other policy type, and never zero.
    motor_premium_amount,

    -- 6. Commercial fire premium amount. CA-B-FirePremium PIC 9(8),
    -- base/src/lgcmarea.cpy:85; Db2-side DB2-B-FirePremium PIC 9(8),
    -- base/src/lgpolicy.cpy:91. MOVE CA-B-FirePremium To DB2-B-FirePremium-Int at
    -- base/src/lgapdb01.cbl:489 loads DB2-B-FirePremium-Int PIC S9(9) COMP,
    -- base/src/lgapdb01.cbl:103, and base/src/lgapdb01.cbl:535 passes it to the commercial
    -- insert. An unsigned DISPLAY numeric without an implied decimal, declaring 8 digits.
    -- DECIMAL(10,2). Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77.
    -- Holds a value for policy type C; null for every other policy type, and never zero.
    fire_premium_amount,

    -- 7. Commercial crime premium amount. CA-B-CrimePremium PIC 9(8),
    -- base/src/lgcmarea.cpy:87; Db2-side DB2-B-CrimePremium PIC 9(8),
    -- base/src/lgpolicy.cpy:93. MOVE CA-B-CrimePremium To DB2-B-CrimePremium-Int at
    -- base/src/lgapdb01.cbl:491 loads DB2-B-CrimePremium-Int PIC S9(9) COMP,
    -- base/src/lgapdb01.cbl:105, and base/src/lgapdb01.cbl:537 passes it to the commercial
    -- insert. An unsigned DISPLAY numeric without an implied decimal, declaring 8 digits.
    -- DECIMAL(10,2). Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77.
    -- Holds a value for policy type C; null for every other policy type, and never zero.
    crime_premium_amount,

    -- 8. Commercial flood premium amount. CA-B-FloodPremium PIC 9(8),
    -- base/src/lgcmarea.cpy:89; Db2-side DB2-B-FloodPremium PIC 9(8),
    -- base/src/lgpolicy.cpy:95. MOVE CA-B-FloodPremium To DB2-B-FloodPremium-Int at
    -- base/src/lgapdb01.cbl:493 loads DB2-B-FloodPremium-Int PIC S9(9) COMP,
    -- base/src/lgapdb01.cbl:107, and base/src/lgapdb01.cbl:539 passes it to the commercial
    -- insert. An unsigned DISPLAY numeric without an implied decimal, declaring 8 digits.
    -- DECIMAL(10,2). Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77.
    -- Holds a value for policy type C; null for every other policy type, and never zero.
    flood_premium_amount,

    -- 9. Commercial weather premium amount. CA-B-WeatherPremium PIC 9(8),
    -- base/src/lgcmarea.cpy:91; Db2-side DB2-B-WeatherPremium PIC 9(8),
    -- base/src/lgpolicy.cpy:97. MOVE CA-B-WeatherPremium To DB2-B-WeatherPremium-Int at
    -- base/src/lgapdb01.cbl:495 loads DB2-B-WeatherPremium-Int PIC S9(9) COMP,
    -- base/src/lgapdb01.cbl:109, and base/src/lgapdb01.cbl:541 passes it to the commercial
    -- insert. An unsigned DISPLAY numeric without an implied decimal, declaring 8 digits.
    -- DECIMAL(10,2). Declared in the CA-COMMERCIAL overlay at base/src/lgcmarea.cpy:77.
    -- Holds a value for policy type C; null for every other policy type, and never zero.
    weather_premium_amount

from decoded

-- Returned chain outcome of the row, read here and absent from the select list above.
-- CA-RETURN-CODE PIC 9(2), base/src/lgcmarea.cpy:11, carried as text by the intermediate
-- model. Each of its fourteen write sites moves a quoted two-character literal, at
-- base/src/lgapol01.cbl:105 and :114, base/src/lgapdb01.cbl:172, :204, :211, :239, :293,
-- :296, :301, :390, :428, :474 and :548, and base/src/lgapvs01.cbl:144. The comparison
-- below is a string comparison and reads the leading zero. The six observed values are 00
-- success, 70 policy insert returned SQLCODE -530, 80 VSAM write response was not normal,
-- 90 SQL failure, 98 COMMAREA shorter than the required length and 99 unsupported request
-- id; 00 is the only one that reaches this relation. The comparison is applied as a second
-- guard over the landing contract: models/staging/genapp_class_exemplar/_genapp__models.yml
-- accepts all six of those codes, and it and ref('int_policy_issue_decoded') carry a row of
-- any of them as failure evidence, while modernization/extraction/extract_commarea.py lands
-- a record only for a returned CA-RETURN-CODE of 00 and refuses every other code of the
-- domain, and that success-only landing contract is what makes 00 the only value observed
-- upstream of this model. The column itself belongs to canonical.issued_policy and no column
-- of this relation carries it, and
-- modernization/dbt/genapp_rqi/tests/assert_preissued_rating_unique_key.sql returns any row
-- of this relation whose upstream record carries no successful outcome.
where return_code = '00'
