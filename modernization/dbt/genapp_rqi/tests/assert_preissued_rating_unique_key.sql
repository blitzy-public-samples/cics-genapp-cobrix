-- assert_preissued_rating_unique_key.sql
-- Singular data test of the GenApp Policy-Issue cloud-warehouse bridge, and one of the
-- three tests of modernization/dbt/genapp_rqi/tests/. dbt discovers this file through the
-- test-paths entry of modernization/dbt/genapp_rqi/dbt_project.yml; nothing imports it.
--
-- What this test asserts. The pair (source_system_key, policy_number) identifies at most
-- one row of the relation preissued_rating of the canonical schema. That pair is the
-- natural key and the grain of the relation, and the assertion is made on the pair, not on
-- either column alone.
--
-- Convention. A dbt singular test is one select statement whose returned row count dbt
-- reads as the result: zero rows is a pass, and any returned row is a failure. The select
-- below returns one row for each key pair held by more than one row, so a pass returns
-- nothing and a failure names every pair it found more than once.
--
-- Columns returned on failure. The two key columns source_system_key and policy_number,
-- and row_count, the number of rows the pair holds. Every returned row carries a row_count
-- of 2 or more, so the failure output names the offending key and its multiplicity.
--
-- Relation under test. ref('canonical_preissued_rating'), the model
-- models/marts/canonical/canonical_preissued_rating.sql, which sets the relation alias
-- preissued_rating and materializes the relation in the canonical schema. The reference
-- spelling is the model name, which is the stem of that model file; the relation alias is
-- not a model name and is not the reference spelling. The ref below is the only relation
-- reference this file writes, and no relation name is hard-coded anywhere in it.
--
-- Columns read. source_system_key and policy_number, and no other column of the relation.
-- The whole column set of the relation is 9 columns, each declared with its type and its
-- column-level lineage in models/marts/canonical/_canonical__models.yml, which declares the
-- contract of the relation enforced.
--
-- What this test does not assert. It reads no amount column and applies no amount
-- predicate: the product null pattern of the six amount columns is asserted by
-- tests/assert_product_premium_nullability.sql, and the comparison tolerance is applied by
-- modernization/validation/diff_harness_vs_warehouse.py. It asserts no total row count for
-- the relation, and it names no request id and no source-system value. It sets no dbt
-- config of any kind, so every dbt default applies to it.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file:
-- modernization/docs/decision-log.md

select

    -- First element of the natural key. Source-system discriminator carried by every row of
    -- the relation.
    source_system_key,

    -- Second element of the natural key. CA-POLICY-NUM PIC 9(10),
    -- base/src/lgcmarea.cpy:35, recovered after the policy insert: the insert supplies the
    -- literal DEFAULT for POLICYNUMBER at base/src/lgapdb01.cbl:279, IDENTITY_VAL_LOCAL()
    -- loads DB2-POLICYNUM-INT at base/src/lgapdb01.cbl:308-310, and
    -- base/src/lgapdb01.cbl:311 moves the recovered value into the COMMAREA item.
    policy_number,

    -- Number of rows the key pair holds, returned so that a failure is diagnosable from the
    -- returned row alone.
    count(*) as row_count

from {{ ref('canonical_preissued_rating') }}

-- Grouped on the two key columns by name. No ordinal position is used.
group by
    source_system_key,
    policy_number

-- A pair held by more than one row is returned; a pair held by exactly one row is not.
having count(*) > 1
