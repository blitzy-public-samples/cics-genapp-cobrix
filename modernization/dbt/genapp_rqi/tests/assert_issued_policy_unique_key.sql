-- assert_issued_policy_unique_key.sql
-- Singular data test of the GenApp Policy-Issue cloud-warehouse bridge, and one of the
-- three singular tests of modernization/dbt/genapp_rqi/tests/. dbt discovers this file
-- through the test-paths entry of modernization/dbt/genapp_rqi/dbt_project.yml; nothing
-- imports it and no other file of the project reads it.
-- The other two singular tests of that directory are
-- tests/assert_preissued_rating_unique_key.sql, which asserts the same key and population
-- rules on the rating mart together with the parity of the key sets of the two relations,
-- and tests/assert_product_premium_nullability.sql, which asserts the product premium null
-- pattern and the amount values of that mart. Neither reads this file.
--
-- Relation under test. The model canonical_issued_policy, of
-- models/marts/canonical/canonical_issued_policy.sql, which materializes the relation
-- issued_policy in the schema canonical. canonical_issued_policy is the model name and is
-- the stem of that model file; issued_policy is the relation alias the model sets in its
-- own config block and is not a reference spelling. This statement reaches the relation
-- through the dbt references below and names no relation and no schema of its own: dbt
-- resolves each reference to the schema-qualified relation of the active output, and the
-- resolved names appear in the compiled statement written under target/.
--
-- Relations read. ref('canonical_issued_policy'), the relation under test;
-- ref('int_policy_issue_decoded'), the upstream record every row of that relation is
-- projected from; ref('canonical_preissued_rating'), read for its resolved schema and
-- identifier and for no value; and information_schema.tables and information_schema.columns
-- of the active output, read for the physical inventory and shape. The catalog reads are
-- read-only: this statement issues no DDL and writes nothing.
--
-- Assertions. Each rule below names one breach class; a returned row carries the name of
-- the rule it breaches in its assertion column.
--
--   issued_key_not_unique
--     The natural key of the relation under test is the pair
--     (source_system_key, policy_number). No pair is carried by more than one row.
--     models/marts/canonical/_canonical__models.yml carries the enforced column contract of
--     that relation and declares no key constraint; this file is where the key is asserted.
--     The same pair is the key the raw loaders modernization/landing/load_local.py and
--     modernization/landing/load_redshift.sql guard their delete-then-insert on.
--
--   issued_row_missing_for_upstream_key
--     Every row of ref('int_policy_issue_decoded') carrying return_code 00 is carried by a
--     row of the relation under test with the same key. The expectation is read from the
--     upstream relation and no policy number is written into this file.
--
--   issued_key_absent_from_upstream
--     Every key of the relation under test is carried by a row of
--     ref('int_policy_issue_decoded').
--
--   issued_key_without_successful_upstream_row
--     Every key of the relation under test is carried by an upstream row whose return_code
--     is 00. A key whose upstream rows carry only 70, 80, 90, 98 or 99 is returned, and the
--     detail column names the observed codes. The model admits successful rows through its
--     own return_code filter; this rule reads the upstream outcome independently of it.
--
--   issued_row_count_differs_from_upstream
--     One key of the upstream relation carrying return_code 00 yields exactly one row of
--     the relation under test.
--
--   issued_request_id_not_carried_once
--     Each request id of the expected_request_ids variable is carried by exactly one row of
--     the relation under test. The default of that variable is the two request ids of the
--     authored sample definitions under modernization/extraction/sample_input/: 01AMOT,
--     which the routing EVALUATE at base/src/lgapdb01.cbl:196 resolves to policy type M,
--     and 01ACOM, which base/src/lgapdb01.cbl:200 resolves to policy type C. A row carrying
--     any other routed request id is not read by this rule, so the 01AEND and 01AHOU rows
--     the same routing admits at base/src/lgapdb01.cbl:188 and :192 neither satisfy nor
--     breach it. An emptied, wiped or fully filtered relation breaches it.
--
--   issued_text_value_outside_declared_width
--     Each text value observes the width its contract declares: source_system_key at most
--     64 characters, request_id at most 6, brokers_reference at most 10, policy_type
--     exactly 1 and return_code exactly 2. Amazon Redshift enforces those widths itself;
--     DuckDB collapses varchar(n) and char(n) to VARCHAR and enforces no width, so this
--     rule is the assertion of the declared width on that adapter.
--
--   issued_text_value_differs_from_upstream
--     Each text value equals the value ref('int_policy_issue_decoded') carries for the same
--     key. The model applies a width-bounding cast to each of the five columns and changes
--     no character of a value that fits its declared width.
--
--   issued_contract_column_missing_from_relation
--   issued_relation_column_absent_from_contract
--   issued_column_position_differs
--   issued_column_type_family_differs
--   issued_column_width_bound_differs
--   issued_column_nullability_differs
--     The physical relation carries exactly the 11 columns of the contract in
--     models/marts/canonical/_canonical__models.yml, in the order that file declares them,
--     each with the type family and the nullability declared there. The declared width of
--     a text column is compared where the adapter reports one: Amazon Redshift reports
--     character_maximum_length and DuckDB reports none for VARCHAR, and the width of every
--     value is asserted by the two value rules above on both adapters.
--     The type family folds the spellings the two adapters report onto one name: DuckDB
--     reports VARCHAR, BIGINT, DATE, TIMESTAMP and DECIMAL(p,s), and Amazon Redshift reports
--     character varying, character, bigint, date, timestamp without time zone and numeric.
--     The relation declares no decimal column, so no numeric precision and no numeric scale
--     is compared here; tests/assert_preissued_rating_unique_key.sql compares both for the
--     six amount columns of the rating mart. dbt matches a contract to a model by column
--     name and does not compare column order, so the order is asserted here.
--
--   canonical_schema_relation_missing
--   canonical_schema_relation_unexpected
--     The schema holding the two marts carries exactly two relations, named issued_policy
--     and preissued_rating. A third relation, a renamed alias and a mart materialized
--     elsewhere are each returned. The schema is read from the resolved reference and is not
--     written into this file; the two required identifiers are the relation names of AAP
--     section 0.3.2.
--
--   canonical_mart_identifier_in_another_schema
--     No other schema of the active output carries a relation named issued_policy or
--     preissued_rating.
--
--   canonical_marts_not_in_one_schema
--     Both marts resolve to one database and one schema. This rule is evaluated while the
--     statement is compiled, from the resolved references, and is returned as a row.
--
--   upstream_record_column_missing
--   upstream_record_column_unexpected
--   upstream_record_column_position_differs
--     ref('int_policy_issue_decoded') carries exactly the 17 columns of the landing record,
--     in the order the landing.field_order block of
--     modernization/extraction/copybook_field_map.yml fixes. The two marts project their
--     columns from that record by name. The types and the nullability of that relation are
--     declared in models/intermediate/_int__models.yml and are not compared here.
--
--   landed_record_column_missing
--   landed_record_column_unexpected
--   landed_record_column_position_differs
--     source('genapp', 'genapp_policy_issue') carries exactly the same 17 column names, in
--     the same order. An eighteenth physical column of that relation is returned here: the
--     staging model selects the 17 landed columns by name and the raw loaders
--     modernization/landing/load_local.py and modernization/landing/load_redshift.sql name
--     the same 17 in their write, so a column beside them reaches no other assertion of this
--     project. dbt declares no enforceable contract on a source, and the column types of
--     that relation, all VARCHAR, are declared in
--     models/staging/genapp_class_exemplar/_genapp__sources.yml and in
--     modernization/warehouse/ddl/02_raw_genapp_policy_issue.sql; they are not compared here.
--
-- Result. A dbt singular test passes on zero returned rows. Each row returned here carries
-- five columns:
--   assertion          the name of the rule the row breaches
--   subject            the relation, column or request id the breach concerns
--   source_system_key  first key element of the breaching row; null for a catalog breach
--   policy_number      second key element of the breaching row; null for a catalog breach
--   detail             the observed values against the required values
-- A row that breaches more than one rule of one block is returned once, under the first
-- rule of that block it breaches.
--
-- Scope. The key, the population, the text values and the physical shape of
-- canonical.issued_policy, the relation inventory of the schema holding the two marts, and
-- the column sets of the landed relation and of the upstream record. No amount is read: payment_amount,
-- motor_premium_amount, fire_premium_amount, crime_premium_amount, flood_premium_amount and
-- weather_premium_amount are columns of canonical.preissued_rating, and their values are
-- asserted by tests/assert_product_premium_nullability.sql. The accepted values of
-- policy_type, request_id and return_code, and the null behaviour of every column, are
-- asserted by the built-in tests of models/marts/canonical/_canonical__models.yml.
--
-- Configuration. This file declares none. dbt applies its defaults for a singular test,
-- and a returned row fails the run. The one variable it reads, expected_request_ids,
-- carries its default in the call below and is declared in no project file.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB. The catalog reads name
-- information_schema relations both adapters carry and compare no adapter-specific
-- spelling.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

{% set issued = ref('canonical_issued_policy') %}
{% set rating = ref('canonical_preissued_rating') %}
{% set upstream = ref('int_policy_issue_decoded') %}
{% set landed = source('genapp', 'genapp_policy_issue') %}

{# Request ids expected to be carried by exactly one row each. #}
{% set expected_request_ids = var('expected_request_ids', ['01AMOT', '01ACOM']) %}

{# The two canonical relation names of AAP section 0.3.2. #}
{% set required_identifiers = ['issued_policy', 'preissued_rating'] %}

{# The five text columns of the relation, with the width each contract declares and
    whether that width is the exact length of every value. #}
{% set text_columns = [
    {'name': 'source_system_key', 'declared': 'VARCHAR(64)', 'width': 64, 'exact': false},
    {'name': 'policy_type',       'declared': 'CHAR(1)',     'width': 1,  'exact': true},
    {'name': 'request_id',        'declared': 'VARCHAR(6)',  'width': 6,  'exact': false},
    {'name': 'return_code',       'declared': 'CHAR(2)',     'width': 2,  'exact': true},
    {'name': 'brokers_reference', 'declared': 'VARCHAR(10)', 'width': 10, 'exact': false}
] %}

{# The 11 columns of the contract in models/marts/canonical/_canonical__models.yml, in the
    order that file declares them: name, position, type family, declared text width and
    is_nullable as information_schema reports it. #}
{% set contract_columns = [
    {'name': 'source_system_key', 'position': 1,  'family': 'text',      'width': 64,   'nullable': 'NO'},
    {'name': 'policy_number',     'position': 2,  'family': 'bigint',    'width': none, 'nullable': 'NO'},
    {'name': 'policy_type',       'position': 3,  'family': 'text',      'width': 1,    'nullable': 'NO'},
    {'name': 'customer_number',   'position': 4,  'family': 'bigint',    'width': none, 'nullable': 'NO'},
    {'name': 'request_id',        'position': 5,  'family': 'text',      'width': 6,    'nullable': 'NO'},
    {'name': 'return_code',       'position': 6,  'family': 'text',      'width': 2,    'nullable': 'NO'},
    {'name': 'issue_date',        'position': 7,  'family': 'date',      'width': none, 'nullable': 'YES'},
    {'name': 'expiry_date',       'position': 8,  'family': 'date',      'width': none, 'nullable': 'YES'},
    {'name': 'last_changed',      'position': 9,  'family': 'timestamp', 'width': none, 'nullable': 'NO'},
    {'name': 'broker_id',         'position': 10, 'family': 'bigint',    'width': none, 'nullable': 'YES'},
    {'name': 'brokers_reference', 'position': 11, 'family': 'text',      'width': 10,   'nullable': 'YES'}
] %}

{# The 17 columns of the landing record, in the order of the landing.field_order block of
    modernization/extraction/copybook_field_map.yml. #}
{% set upstream_columns = [
    'source_system_key', 'policy_number', 'policy_type', 'customer_number', 'request_id',
    'return_code', 'issue_date', 'expiry_date', 'last_changed', 'broker_id',
    'brokers_reference', 'payment_amount', 'motor_premium_amount', 'fire_premium_amount',
    'crime_premium_amount', 'flood_premium_amount', 'weather_premium_amount'
] %}

with

-- Rows of the relation under test per key pair.
issued_keys as (

    select
        source_system_key,
        policy_number,
        count(*) as mart_rows

    from {{ issued }}

    group by source_system_key, policy_number

),

-- Rows of the upstream record per key pair, with the successful rows counted separately and
-- the observed return codes carried for the failure detail.
upstream_keys as (

    select
        source_system_key,
        policy_number,
        count(*) as upstream_rows,
        sum(case when return_code = '00' then 1 else 0 end) as upstream_successful_rows,
        min(return_code) as lowest_return_code,
        max(return_code) as highest_return_code

    from {{ upstream }}

    group by source_system_key, policy_number

),

-- Every key either relation carries, with the counts of both sides.
key_parity as (

    select
        coalesce(m.source_system_key, u.source_system_key) as source_system_key,
        coalesce(m.policy_number, u.policy_number) as policy_number,
        coalesce(m.mart_rows, 0) as mart_rows,
        coalesce(u.upstream_rows, 0) as upstream_rows,
        coalesce(u.upstream_successful_rows, 0) as upstream_successful_rows,
        u.lowest_return_code,
        u.highest_return_code

    from issued_keys m

    full outer join upstream_keys u
        on m.source_system_key = u.source_system_key
        and m.policy_number = u.policy_number

),

-- The first key rule each key breaches, or null where it breaches none.
key_breaches as (

    select
        case
            when mart_rows > 1
                then 'issued_key_not_unique'
            when upstream_successful_rows > 0 and mart_rows = 0
                then 'issued_row_missing_for_upstream_key'
            when mart_rows > 0 and upstream_rows = 0
                then 'issued_key_absent_from_upstream'
            when mart_rows > 0 and upstream_successful_rows = 0
                then 'issued_key_without_successful_upstream_row'
            when mart_rows <> upstream_successful_rows
                then 'issued_row_count_differs_from_upstream'
        end as assertion,
        source_system_key,
        policy_number,
        mart_rows,
        upstream_rows,
        upstream_successful_rows,
        lowest_return_code,
        highest_return_code

    from key_parity

),

-- The request ids expected to be carried by exactly one row each.
expected_request_ids as (
{% for request_id in expected_request_ids %}
    select '{{ request_id }}' as request_id
    {% if not loop.last %}
    union all
    {% endif %}
{% endfor %}
),

-- Rows of the relation under test per request id.
issued_request_ids as (

    select
        request_id,
        count(*) as mart_rows

    from {{ issued }}

    group by request_id

),

-- Each row of the relation under test beside the upstream row of the same key, for the text
-- value comparison. The join reads the successful upstream rows only.
issued_with_upstream as (

    select
        m.source_system_key,
        m.policy_number,
        {% for column in text_columns %}
        m.{{ column.name }} as mart_{{ column.name }},
        u.{{ column.name }} as upstream_{{ column.name }}{{ ',' if not loop.last }}
        {% endfor %}

    from {{ issued }} m

    inner join {{ upstream }} u
        on m.source_system_key = u.source_system_key
        and m.policy_number = u.policy_number
        and u.return_code = '00'

),

-- The contract of the relation under test, one row per declared column.
contract_columns as (
{% for column in contract_columns %}
    select
        '{{ column.name }}' as column_name,
        cast({{ column.position }} as integer) as ordinal_position,
        '{{ column.family }}' as type_family,
        cast({{ column.width if column.width is not none else 'null' }} as integer) as character_maximum_length,
        '{{ column.nullable }}' as is_nullable
    {% if not loop.last %}
    union all
    {% endif %}
{% endfor %}
),

-- The physical columns of the relation under test, with the type spelling of the active
-- adapter folded onto the type family names the contract block above uses.
catalog_columns as (

    select
        column_name,
        cast(ordinal_position as integer) as ordinal_position,
        case
            when lower(data_type) in ('varchar', 'character varying', 'char', 'character',
                                      'bpchar', 'text', 'string')
                then 'text'
            when lower(data_type) in ('bigint', 'int8')
                then 'bigint'
            when lower(data_type) like 'decimal%' or lower(data_type) like 'numeric%'
                then 'decimal'
            when lower(data_type) = 'date'
                then 'date'
            when lower(data_type) like 'timestamp%'
                then 'timestamp'
            else lower(data_type)
        end as type_family,
        cast(character_maximum_length as integer) as character_maximum_length,
        upper(is_nullable) as is_nullable

    from information_schema.columns

    where table_catalog = '{{ issued.database }}'
        and table_schema = '{{ issued.schema }}'
        and table_name = '{{ issued.identifier }}'

),

-- The first shape rule each column of either side breaches, or null where it breaches none.
column_breaches as (

    select
        case
            when a.column_name is null
                then 'issued_contract_column_missing_from_relation'
            when e.column_name is null
                then 'issued_relation_column_absent_from_contract'
            when a.ordinal_position <> e.ordinal_position
                then 'issued_column_position_differs'
            when a.type_family <> e.type_family
                then 'issued_column_type_family_differs'
            when e.character_maximum_length is not null
                and a.character_maximum_length is not null
                and a.character_maximum_length <> e.character_maximum_length
                then 'issued_column_width_bound_differs'
            when a.is_nullable <> e.is_nullable
                then 'issued_column_nullability_differs'
        end as assertion,
        coalesce(e.column_name, a.column_name) as column_name,
        'required position ' || coalesce(cast(e.ordinal_position as varchar), '-')
            || ' family ' || coalesce(e.type_family, '-')
            || ' width ' || coalesce(cast(e.character_maximum_length as varchar), 'unbounded')
            || ' nullable ' || coalesce(e.is_nullable, '-')
            || '; observed position ' || coalesce(cast(a.ordinal_position as varchar), '-')
            || ' family ' || coalesce(a.type_family, '-')
            || ' width ' || coalesce(cast(a.character_maximum_length as varchar), 'unbounded')
            || ' nullable ' || coalesce(a.is_nullable, '-') as detail

    from contract_columns e

    full outer join catalog_columns a
        on e.column_name = a.column_name

),

-- The two relation names the canonical schema is required to carry.
required_relations as (
{% for identifier in required_identifiers %}
    select '{{ identifier }}' as table_name
    {% if not loop.last %}
    union all
    {% endif %}
{% endfor %}
),

-- The relations the schema holding the two marts actually carries.
schema_relations as (

    select table_name

    from information_schema.tables

    where table_catalog = '{{ issued.database }}'
        and table_schema = '{{ issued.schema }}'

),

-- The 17 columns of the landing record the two marts project from.
upstream_contract_columns as (
{% for column_name in upstream_columns %}
    select
        '{{ column_name }}' as column_name,
        cast({{ loop.index }} as integer) as ordinal_position
    {% if not loop.last %}
    union all
    {% endif %}
{% endfor %}
),

-- The physical columns of the upstream relation.
upstream_catalog_columns as (

    select
        column_name,
        cast(ordinal_position as integer) as ordinal_position

    from information_schema.columns

    where table_catalog = '{{ upstream.database }}'
        and table_schema = '{{ upstream.schema }}'
        and table_name = '{{ upstream.identifier }}'

),

-- The physical columns of the landed relation the staging model reads.
landed_catalog_columns as (

    select
        column_name,
        cast(ordinal_position as integer) as ordinal_position

    from information_schema.columns

    where table_catalog = '{{ landed.database }}'
        and table_schema = '{{ landed.schema }}'
        and table_name = '{{ landed.identifier }}'

)

-- Key and population of the relation under test.
select
    assertion,
    '{{ issued.identifier }}' as subject,
    source_system_key,
    policy_number,
    'mart_rows=' || cast(mart_rows as varchar)
        || ' upstream_rows=' || cast(upstream_rows as varchar)
        || ' upstream_successful_rows=' || cast(upstream_successful_rows as varchar)
        || ' upstream_return_codes=' || coalesce(lowest_return_code, '-')
        || '..' || coalesce(highest_return_code, '-') as detail

from key_breaches

where assertion is not null

union all

-- One row per expected request id.
select
    'issued_request_id_not_carried_once' as assertion,
    e.request_id as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'rows=' || cast(coalesce(m.mart_rows, 0) as varchar) || ' required 1' as detail

from expected_request_ids e

left join issued_request_ids m
    on e.request_id = m.request_id

where coalesce(m.mart_rows, 0) <> 1
{% for column in text_columns %}
union all

-- Width and value of {{ column.name }}, declared {{ column.declared }}.
select
    assertion,
    subject,
    source_system_key,
    policy_number,
    detail

from (

    select
        case
            when mart_{{ column.name }} is not null
                and length(mart_{{ column.name }}) {{ '<>' if column.exact else '>' }} {{ column.width }}
                then 'issued_text_value_outside_declared_width'
            when mart_{{ column.name }} is null and upstream_{{ column.name }} is not null
                then 'issued_text_value_differs_from_upstream'
            when mart_{{ column.name }} is not null and upstream_{{ column.name }} is null
                then 'issued_text_value_differs_from_upstream'
            when mart_{{ column.name }} <> upstream_{{ column.name }}
                then 'issued_text_value_differs_from_upstream'
        end as assertion,
        '{{ column.name }}' as subject,
        source_system_key,
        policy_number,
        'mart=' || coalesce(mart_{{ column.name }}, 'null')
            || ' upstream=' || coalesce(upstream_{{ column.name }}, 'null')
            || ' declared {{ column.declared }}' as detail

    from issued_with_upstream

) as {{ column.name }}_checks

where assertion is not null
{% endfor %}
union all

-- Physical column shape of the relation under test.
select
    assertion,
    column_name as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    detail

from column_breaches

where assertion is not null

union all

-- Relation inventory of the schema holding the two marts.
select
    case
        when a.table_name is null then 'canonical_schema_relation_missing'
        else 'canonical_schema_relation_unexpected'
    end as assertion,
    coalesce(e.table_name, a.table_name) as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'schema {{ issued.database }}.{{ issued.schema }} required exactly '
        || '{{ required_identifiers | length }} relations' as detail

from required_relations e

full outer join schema_relations a
    on e.table_name = a.table_name

where e.table_name is null or a.table_name is null

union all

-- A canonical relation name carried by another schema of the active output.
select
    'canonical_mart_identifier_in_another_schema' as assertion,
    table_schema || '.' || table_name as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'expected only in schema {{ issued.schema }}' as detail

from information_schema.tables

where table_catalog = '{{ issued.database }}'
    and table_schema <> '{{ issued.schema }}'
    and table_name in (
        {% for identifier in required_identifiers %}
        '{{ identifier }}'{{ ',' if not loop.last }}
        {% endfor %}
    )
{% if issued.database != rating.database or issued.schema != rating.schema %}
union all

-- The two marts resolve to different schemas.
select
    'canonical_marts_not_in_one_schema' as assertion,
    '{{ issued.identifier }} and {{ rating.identifier }}' as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'issued {{ issued.database }}.{{ issued.schema }} rating {{ rating.database }}.{{ rating.schema }}' as detail
{% endif %}
union all

-- Column set of the upstream record the two marts project from.
select
    case
        when a.column_name is null then 'upstream_record_column_missing'
        when e.column_name is null then 'upstream_record_column_unexpected'
        else 'upstream_record_column_position_differs'
    end as assertion,
    coalesce(e.column_name, a.column_name) as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'required position ' || coalesce(cast(e.ordinal_position as varchar), '-')
        || '; observed position ' || coalesce(cast(a.ordinal_position as varchar), '-')
        || ' in {{ upstream.identifier }}' as detail

from upstream_contract_columns e

full outer join upstream_catalog_columns a
    on e.column_name = a.column_name

where a.column_name is null
    or e.column_name is null
    or a.ordinal_position <> e.ordinal_position

union all

-- Column set of the landed relation the staging model reads.
select
    case
        when a.column_name is null then 'landed_record_column_missing'
        when e.column_name is null then 'landed_record_column_unexpected'
        else 'landed_record_column_position_differs'
    end as assertion,
    coalesce(e.column_name, a.column_name) as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'required position ' || coalesce(cast(e.ordinal_position as varchar), '-')
        || '; observed position ' || coalesce(cast(a.ordinal_position as varchar), '-')
        || ' in {{ landed.schema }}.{{ landed.identifier }}' as detail

from upstream_contract_columns e

full outer join landed_catalog_columns a
    on e.column_name = a.column_name

where a.column_name is null
    or e.column_name is null
    or a.ordinal_position <> e.ordinal_position
