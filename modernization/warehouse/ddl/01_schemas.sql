-- 01_schemas.sql
-- Warehouse bootstrap, step 1 of 2, for the GenApp Policy-Issue cloud-warehouse bridge.
-- Creates the raw and canonical schemas.
-- Milestone status: this file is the only warehouse DDL present. Every other
-- modernization path named below is a planned deliverable, not present at this
-- milestone. The run order, the raw-relation owner and the loaders described here
-- are planned, not established.
-- Planned run order: this file first, then 02_raw_genapp_policy_issue.sql.
-- Idempotent and re-runnable.
-- Planned to run unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file:
-- modernization/docs/decision-log.md (planned deliverable; not present at this milestone)

-- Schema raw holds the landed policy-issue record exactly as extracted, every column VARCHAR.
-- Its planned relation is raw.genapp_policy_issue, which 02_raw_genapp_policy_issue.sql
-- will create. landing/load_redshift.sql will populate it with COPY on the real branch,
-- and landing/load_local.py will populate it on the local branch.
CREATE SCHEMA IF NOT EXISTS raw;

-- Schema canonical is the namespace for the two business relations canonical.issued_policy
-- and canonical.preissued_rating. The planned dbt marts under
-- dbt/genapp_rqi/models/marts/canonical/ will create those tables. This file creates the
-- namespace only.
CREATE SCHEMA IF NOT EXISTS canonical;
