-- canonical_issued_policy.sql
-- Mart model of the GenApp Policy-Issue cloud-warehouse bridge, and one of the two models
-- of the models/marts/canonical subtree.
--
-- Relation. canonical.issued_policy. The schema canonical comes from the
-- models/marts/canonical key of modernization/dbt/genapp_rqi/dbt_project.yml, which
-- macros/generate_schema_name.sql returns verbatim; the relation name comes from the alias
-- set below. modernization/warehouse/ddl/01_schemas.sql creates the canonical namespace
-- and no relation within it, and this file creates this relation.
--
-- Meaning. One row per successful issued policy and source system.
--
-- Grain. One row per (source_system_key, policy_number), the natural key both raw loaders
-- guard on and the key models/marts/canonical asserts uniqueness on. One input row yields
-- at most one output row: no row is combined, no row is added and no de-duplication is
-- applied.
--
-- Input. ref('int_policy_issue_decoded'), the single model of models/intermediate and the
-- only relation this model reads. That model sets no relation alias, so its model name is
-- the reference spelling. The dbt source binding of the project is held by
-- models/staging/genapp_class_exemplar/_genapp__sources.yml and is read by the staging
-- model alone.
--
-- Output. The 11 columns below, under the names and in the order of the
-- targets: canonical.issued_policy: columns block of
-- modernization/extraction/copybook_field_map.yml, the naming authority for this contract,
-- and of models/marts/canonical/_canonical__models.yml, which carries the enforced column
-- contract and the per-column lineage. Ten columns derive from a source item and
-- source_system_key is warehouse-assigned.
--
-- What this model does. It selects, filters and projects. Every type conversion of the
-- bridge is applied by ref('int_policy_issue_decoded') and none is repeated here: no value
-- is cast, trimmed, null-guarded, rounded, rescaled or renamed, and policy_type is not
-- re-derived. The rows admitted are those carrying return code 00, the successful chain
-- outcome.
--
-- What this model does not do. It carries no amount: payment_amount,
-- motor_premium_amount, fire_premium_amount, crime_premium_amount, flood_premium_amount
-- and weather_premium_amount are columns of canonical.preissued_rating and enter the scope
-- of neither block below. It applies no arithmetic and holds no rating formula, rating
-- factor, derived factor or commission column; the three named programs
-- base/src/lgapol01.cbl, base/src/lgapdb01.cbl and base/src/lgapvs01.cbl carry no
-- COMPUTE, MULTIPLY, DIVIDE or COMP-3 statement. It adds no provenance, audit, surrogate
-- key, hash, row-number or load-timestamp column. DB2-POLICYNUMBER PIC 9(10),
-- base/src/lgpolicy.cpy:44, is declaration-only and carries no column: the policy insert
-- supplies the literal DEFAULT for POLICYNUMBER at base/src/lgapdb01.cbl:279 and the
-- recovered key reaches the COMMAREA through DB2-POLICYNUM-INT at
-- base/src/lgapdb01.cbl:308-311. No column derives from base/src/lgapvs01.cbl. No row
-- limit, no DISTINCT and no window function is applied: the motor sample row and the
-- commercial sample row both reach the output.
--
-- Configuration. The table materialization and the canonical schema come from the
-- models/marts/canonical key of dbt_project.yml. This file declares one configuration,
-- the relation alias.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4, dbt Transformation DAG and Field Allocation,
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

{{ config(alias='issued_policy') }}

with decoded as (

    -- The 11 columns of this relation, named explicitly, in the order fixed by the
    -- canonical contract. Each value arrives carrying its final type. The six amount
    -- columns of ref('int_policy_issue_decoded') are not selected.
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
        brokers_reference

    from {{ ref('int_policy_issue_decoded') }}

)

select
    -- Source-system discriminator assigned by the warehouse. No COBOL source item supplies
    -- it: this is the sole warehouse-assigned column of this relation, and its evidence is
    -- the user requirement rather than a source locator. VARCHAR(64), never null. First
    -- element of the grain.
    source_system_key,

    -- Policy number recovered after the policy insert. CA-POLICY-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:35. IDENTITY_VAL_LOCAL() loads DB2-POLICYNUM-INT at
    -- base/src/lgapdb01.cbl:308-310 and base/src/lgapdb01.cbl:311 moves the recovered
    -- value into the COMMAREA item, so the value exists only in the returned COMMAREA.
    -- BIGINT, never null. Second element of the grain.
    policy_number,

    -- Product discriminator E, H, M or C. DB2-POLICYTYPE PIC X, base/src/lgpolicy.cpy:43,
    -- assigned by the request-routing EVALUATE at base/src/lgapdb01.cbl:184-207 and
    -- checked against the request id by ref('int_policy_issue_decoded'). CHAR(1), never
    -- null.
    policy_type,

    -- Customer number supplied in the request. CA-CUSTOMER-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:12, moved to DB2-CUSTOMERNUM-INT at
    -- base/src/lgapdb01.cbl:176 and passed to the policy insert at
    -- base/src/lgapdb01.cbl:280. BIGINT, never null.
    customer_number,

    -- Request identifier the chain routes on. CA-REQUEST-ID PIC X(6),
    -- base/src/lgcmarea.cpy:10, evaluated at base/src/lgapdb01.cbl:184. VARCHAR(6), never
    -- null.
    request_id,

    -- Returned chain outcome, carried as text. CA-RETURN-CODE PIC 9(2),
    -- base/src/lgcmarea.cpy:11. Each of the fourteen write sites moves a quoted
    -- two-character literal, at base/src/lgapol01.cbl:105 and :114,
    -- base/src/lgapdb01.cbl:172, :204, :211, :239, :293, :296, :301, :390, :428, :474 and
    -- :548, and base/src/lgapvs01.cbl:144; the six observed values are 00 success, 70
    -- policy insert returned SQLCODE -530, 80 VSAM write response was not normal, 90 SQL
    -- failure, 98 COMMAREA shorter than the required length and 99 unsupported request id.
    -- Every row of this relation carries 00. CHAR(2), never null.
    return_code,

    -- Policy issue date supplied in the request. CA-ISSUE-DATE PIC X(10),
    -- base/src/lgcmarea.cpy:38; Db2-side DB2-ISSUEDATE PIC X(10),
    -- base/src/lgpolicy.cpy:46; passed to the policy insert at
    -- base/src/lgapdb01.cbl:281. DATE, nullable.
    issue_date,

    -- Policy expiry date supplied in the request. CA-EXPIRY-DATE PIC X(10),
    -- base/src/lgcmarea.cpy:39; Db2-side DB2-EXPIRYDATE PIC X(10),
    -- base/src/lgpolicy.cpy:47; passed to the policy insert at
    -- base/src/lgapdb01.cbl:282. DATE, nullable.
    expiry_date,

    -- Policy last-changed timestamp read back after the policy insert. CA-LASTCHANGED
    -- PIC X(26), base/src/lgcmarea.cpy:40; Db2-side DB2-LASTCHANGED PIC X(26),
    -- base/src/lgpolicy.cpy:48. The insert writes CURRENT TIMESTAMP at
    -- base/src/lgapdb01.cbl:284 and the SELECT keyed on the recovered policy number at
    -- base/src/lgapdb01.cbl:316-321 reads the assigned value back into the COMMAREA item,
    -- so the value exists only in the returned COMMAREA. TIMESTAMP, never null.
    last_changed,

    -- Broker identifier supplied in the request. CA-BROKERID PIC 9(10),
    -- base/src/lgcmarea.cpy:41; Db2-side DB2-BROKERID PIC 9(10),
    -- base/src/lgpolicy.cpy:49; moved to DB2-BROKERID-INT at base/src/lgapdb01.cbl:264 and
    -- passed to the policy insert at base/src/lgapdb01.cbl:285. BIGINT, nullable.
    broker_id,

    -- Broker's reference supplied in the request. CA-BROKERSREF PIC X(10),
    -- base/src/lgcmarea.cpy:42; Db2-side DB2-BROKERSREF PIC X(10),
    -- base/src/lgpolicy.cpy:50; passed to the policy insert as a character host variable
    -- at base/src/lgapdb01.cbl:286 and trimmed by ref('int_policy_issue_decoded').
    -- VARCHAR(10), nullable.
    brokers_reference

from decoded

-- Successful chain outcome. Admits the rows of a successfully issued policy; a row
-- carrying 70, 80, 90, 98 or 99 reaches this model and is not materialized.
where return_code = '00'
