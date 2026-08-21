-- assert_issued_policy_unique_key.sql
-- Singular data test of the GenApp Policy-Issue cloud-warehouse bridge, and one of the
-- three singular tests of modernization/dbt/genapp_rqi/tests/. dbt discovers this file
-- through the test-paths entry of modernization/dbt/genapp_rqi/dbt_project.yml; nothing
-- imports it and no other file of the project reads it.
-- The other two singular tests of that directory are
-- tests/assert_preissued_rating_unique_key.sql, which asserts the same key pair on the
-- rating mart, and tests/assert_product_premium_nullability.sql, which asserts the
-- product premium null pattern of that mart. Neither reads this file.
--
-- Relation under test. The model canonical_issued_policy, of
-- models/marts/canonical/canonical_issued_policy.sql, which materializes the relation
-- issued_policy in the schema canonical. canonical_issued_policy is the model name and is
-- the stem of that model file; issued_policy is the relation alias the model sets in its
-- own config block and is not a reference spelling. This statement reaches the relation
-- through the single dbt reference below and names no relation and no schema of its own:
-- dbt resolves that reference to the schema-qualified relation of the active output, and
-- the resolved name appears in the compiled statement written under target/.
--
-- Assertion. The natural key of the relation under test is the pair
-- (source_system_key, policy_number), and each pair occurs at most once.
-- models/marts/canonical/_canonical__models.yml carries the enforced column contract of
-- that relation and declares no key constraint; this file is where the key is asserted.
-- The same pair is the key the raw loaders modernization/landing/load_local.py and
-- modernization/landing/load_redshift.sql guard their delete-then-insert on.
--
-- Key columns, in the order the contract declares them.
--   source_system_key. Source-system discriminator assigned by the warehouse; no COBOL
--   item supplies it. Declared varchar, logical width 64, never null. First element of
--   the key. The value modernization/extraction/extract_commarea.py writes for this
--   exemplar is GENAPP_CLASS_EXEMPLAR.
--
--   policy_number. Policy number recovered after the policy insert. CA-POLICY-NUM
--   PIC 9(10), base/src/lgcmarea.cpy:35. The policy insert supplies the literal DEFAULT
--   for POLICYNUMBER at base/src/lgapdb01.cbl:279, IDENTITY_VAL_LOCAL() loads the integer
--   host variable DB2-POLICYNUM-INT at base/src/lgapdb01.cbl:308-310, and
--   base/src/lgapdb01.cbl:311 moves the recovered value into the COMMAREA item. Declared
--   bigint, never null. Second element of the key.
--
-- Result. A dbt singular test passes on zero returned rows. Each row this statement
-- returns carries one violated key: the two key column values, and row_count, the number
-- of rows of the relation carrying that pair. row_count is a diagnostic column of the
-- failure output and is not part of the key.
--
-- Scope. The two key columns and one aggregate over them. The nine remaining columns of
-- the relation, policy_type, customer_number, request_id, return_code, issue_date,
-- expiry_date, last_changed, broker_id and brokers_reference, are outside this assertion;
-- their names, types, positions, null behaviour and accepted values are asserted by
-- _canonical__models.yml. This statement applies no row filter, asserts no row count,
-- reads no second relation, and holds over every row the mart materializes.
--
-- Configuration. This file declares none. dbt applies its defaults for a singular test,
-- and a returned row fails the run.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4, dbt Transformation DAG and Field Allocation,
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

select

    -- First element of the key.
    source_system_key,

    -- Second element of the key.
    policy_number,

    -- Rows of the relation carrying the pair above. Diagnostic column of the failure
    -- output, and not part of the key.
    count(*) as row_count

from {{ ref('canonical_issued_policy') }}

-- Grouped on the two key columns, each named.
group by source_system_key, policy_number

-- A pair carried by more than one row. Zero returned rows is the passing result.
having count(*) > 1
