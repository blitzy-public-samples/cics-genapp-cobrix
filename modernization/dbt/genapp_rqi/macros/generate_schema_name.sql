{#
    generate_schema_name.sql
    Schema-name resolution for the models of the GenApp Policy-Issue
    cloud-warehouse bridge. dbt discovers this macro through the macro-paths
    entry of dbt_project.yml and will apply it to every model in the project;
    nothing imports or registers it.

    Milestone status: this macro, dbt_project.yml, profiles.example.yml and the
    dbt source declaration are the only members of the dbt project present. The
    model tree and the singular tests are planned deliverables, not present at
    this milestone. The model behavior stated below is the planned schema-name
    contract.

    Returned value:
      A model that declares no custom schema resolves to the default schema of
      the active target.
      A model that declares a custom schema resolves to that name exactly as
      declared, trimmed of surrounding whitespace, with nothing prefixed or
      appended. The layer defaults of dbt_project.yml will resolve to the
      literal schemas staging, intermediate and canonical, and each planned
      mart of models/marts/canonical will land in canonical under the alias it
      sets in its own config block.
      A custom schema that is empty once trimmed resolves as though none were
      declared, so the macro never returns a blank name.

    Scope:
      Models only. The dbt source declaration in
      models/staging/genapp_class_exemplar/_genapp__sources.yml names its
      own schema and does not pass through this macro. The macro issues no DDL:
      the raw and canonical namespaces come from
      modernization/warehouse/ddl/01_schemas.sql, and dbt will provision
      staging and intermediate itself at run time.

    Arguments:
      custom_schema_name  the schema declared for a model, or none
      node                the node whose schema is being resolved, passed by dbt

    Planned to run unchanged on Amazon Redshift and DuckDB.
    Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
    in modernization/docs/architecture.md.
    Rationale for every choice in this file:
    modernization/docs/decision-log.md (planned deliverable; not present at this milestone)
#}
{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none or (custom_schema_name | trim) == '' -%}

        {{ default_schema }}

    {%- else -%}

        {{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}
