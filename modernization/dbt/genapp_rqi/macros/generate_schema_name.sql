{#
    generate_schema_name.sql
    Schema-name resolution for the models of the GenApp Policy-Issue
    cloud-warehouse bridge. dbt discovers this macro through the macro-paths
    entry of dbt_project.yml and applies it to every model in the project;
    nothing imports or registers it.

    Milestone status: every member of the dbt project is present — this macro,
    dbt_project.yml, profiles.example.yml, the dbt source declaration, the four
    models stg_genapp__policy_issue, int_policy_issue_decoded,
    canonical_issued_policy and canonical_preissued_rating with the property
    file beside each model subtree, and the three singular tests under tests/.
    The schema-name contract stated below is the contract every model of the
    project resolves under. This file claims no run of its own; per-target run
    status is recorded in modernization/validation/validation-evidence.md,
    which records the DuckDB local_substitute run and no Amazon Redshift run.

    Returned value:
      A model that declares no custom schema resolves to the default schema of
      the active target.
      A model that declares a custom schema resolves to that name exactly as
      declared, trimmed of surrounding whitespace, with nothing prefixed or
      appended. The layer defaults of dbt_project.yml therefore resolve to the
      literal schemas staging, intermediate and canonical: stg_genapp__policy_issue
      lands in staging, int_policy_issue_decoded lands in intermediate, and
      canonical_issued_policy and canonical_preissued_rating land in canonical
      under the aliases issued_policy and preissued_rating they set in their own
      config blocks.
      A custom schema that is empty once trimmed resolves as though none were
      declared, so the macro never returns a blank name.

    Scope:
      Models only. The dbt source declaration in
      models/staging/genapp_class_exemplar/_genapp__sources.yml names its
      own schema and does not pass through this macro. The macro issues no DDL:
      the raw and canonical namespaces come from
      modernization/warehouse/ddl/01_schemas.sql, and dbt provisions staging and
      intermediate itself at run time.

    Arguments:
      custom_schema_name  the schema declared for a model, or none
      node                the node whose schema is being resolved, passed by dbt

    No adapter-specific behavior is written into this macro; the same text
    serves the Amazon Redshift and the DuckDB output of profiles.example.yml.
    Execution against real Amazon Redshift has not yet happened.
    Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
    in modernization/docs/architecture.md.
    Rationale for every choice in this file: modernization/docs/decision-log.md
#}
{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none or (custom_schema_name | trim) == '' -%}

        {{ default_schema }}

    {%- else -%}

        {{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}
