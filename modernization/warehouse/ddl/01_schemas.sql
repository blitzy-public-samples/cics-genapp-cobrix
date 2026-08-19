-- 01_schemas.sql
-- Warehouse bootstrap, step 1 of 2, for the GenApp Policy-Issue cloud-warehouse bridge.
-- Creates the raw and canonical schemas.
-- Run order: this file first, then 02_raw_genapp_policy_issue.sql.
-- Idempotent and re-runnable.
-- Runs unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4, dbt Transformation DAG and Field Allocation,
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

-- Schema raw holds the landed policy-issue record exactly as extracted, every column VARCHAR.
-- Its relation is raw.genapp_policy_issue, created by 02_raw_genapp_policy_issue.sql.
-- Populated by landing/load_redshift.sql with COPY on the real branch, and by
-- landing/load_local.py on the local branch.
CREATE SCHEMA IF NOT EXISTS raw;

-- Schema canonical is the namespace for the two business relations canonical.issued_policy
-- and canonical.preissued_rating. Those tables are created by the dbt marts under
-- dbt/genapp_rqi/models/marts/canonical/. This file creates the namespace only.
CREATE SCHEMA IF NOT EXISTS canonical;
