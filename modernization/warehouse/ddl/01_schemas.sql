-- 01_schemas.sql
-- Warehouse bootstrap, step 1 of 2, for the GenApp Policy-Issue cloud-warehouse bridge.
-- Creates the raw and canonical schemas and no relation.
-- Run order: this file first, then 02_raw_genapp_policy_issue.sql, which creates the raw
-- relation. Together those two files are the whole warehouse DDL of the bridge; every
-- relation of the canonical schema is created by the dbt marts named below.
-- Idempotent and re-runnable: each statement is guarded by IF NOT EXISTS, so a re-run
-- against a bootstrapped target changes nothing.
-- Authored to run unchanged on Amazon Redshift and DuckDB. Applied on DuckDB by
-- modernization/landing/load_local.py before it loads the raw relation on the local
-- branch, and applied against Amazon Redshift before modernization/landing/load_redshift.sql
-- runs on the real branch; that has not yet happened, no branch of this bridge having
-- reached a real Amazon Redshift target.
-- Milestone status: every modernization path named below is authored and present at this
-- milestone. An executed result is recorded in
-- modernization/validation/validation-evidence.md, a planned deliverable not present at
-- this milestone.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file:
-- modernization/docs/decision-log.md (planned deliverable; not present at this milestone)

-- Schema raw holds the landed policy-issue record exactly as extracted, every column VARCHAR.
-- Its relation is raw.genapp_policy_issue, created by 02_raw_genapp_policy_issue.sql, which
-- owns its column names, column order and VARCHAR lengths. landing/load_redshift.sql
-- populates it with COPY on the real branch, and landing/load_local.py populates it on the
-- local branch; both files are present and both write the same 17 columns in the same order.
CREATE SCHEMA IF NOT EXISTS raw;

-- Schema canonical is the namespace for the two business relations canonical.issued_policy
-- and canonical.preissued_rating. The dbt marts under
-- dbt/genapp_rqi/models/marts/canonical/ create and own those two tables and no other, and
-- are present there as canonical_issued_policy.sql, under the alias issued_policy, and
-- canonical_preissued_rating.sql, under the alias preissued_rating; this file creates the
-- namespace only and no file of this directory creates a canonical relation.
CREATE SCHEMA IF NOT EXISTS canonical;
