-- assert_preissued_rating_unique_key.sql
-- Singular data test of the GenApp Policy-Issue cloud-warehouse bridge, and one of the
-- three singular tests of modernization/dbt/genapp_rqi/tests/. dbt discovers this file
-- through the test-paths entry of modernization/dbt/genapp_rqi/dbt_project.yml; nothing
-- imports it.
-- The other two singular tests of that directory are
-- tests/assert_issued_policy_unique_key.sql, which asserts the same key and population rules
-- on the issued mart together with the relation inventory of the canonical schema and the
-- column set of the upstream record, and tests/assert_product_premium_nullability.sql, which
-- asserts the product premium null pattern and the amount values of this mart. Neither reads
-- this file.
--
-- Relation under test. ref('canonical_preissued_rating'), the model
-- models/marts/canonical/canonical_preissued_rating.sql, which sets the relation alias
-- preissued_rating and materializes the relation in the canonical schema. The reference
-- spelling is the model name, which is the stem of that model file; the relation alias is
-- not a model name and is not the reference spelling. Every relation this file reaches is
-- reached through a dbt reference or through information_schema, and no relation name is
-- hard-coded anywhere in it.
--
-- Relations read. ref('canonical_preissued_rating'), the relation under test;
-- ref('int_policy_issue_decoded'), the upstream record every row of that relation is
-- projected from, read for its key, its request id, its return code and its two text
-- columns; ref('canonical_issued_policy'), read for its key set; and
-- information_schema.columns of the active output, read for the physical shape. The catalog
-- read is read-only: this statement issues no DDL and writes nothing.
--
-- Assertions. Each rule below names one breach class; a returned row carries the name of
-- the rule it breaches in its assertion column.
--
--   rating_key_not_unique
--     The pair (source_system_key, policy_number) is the natural key and the grain of the
--     relation under test, and no pair is carried by more than one row. The assertion is
--     made on the pair, not on either column alone.
--
--   rating_row_missing_for_upstream_key
--     Every row of ref('int_policy_issue_decoded') carrying return_code 00 is carried by a
--     row of the relation under test with the same key. The expectation is read from the
--     upstream relation and no policy number is written into this file.
--
--   rating_key_absent_from_upstream
--     Every key of the relation under test is carried by a row of
--     ref('int_policy_issue_decoded').
--
--   rating_key_without_successful_upstream_row
--     Every key of the relation under test is carried by an upstream row whose return_code
--     is 00. This relation carries no return_code column of its own; the outcome is read
--     from the upstream record, and the detail column names the observed codes.
--
--   rating_row_count_differs_from_upstream
--     One key of the upstream relation carrying return_code 00 yields exactly one row of
--     the relation under test.
--
--   rating_relation_carries_no_row
--     The relation under test carries at least one row. The rule returns exactly one row
--     when it carries none, whatever the expected_request_ids variable holds, and the detail
--     column carries the observed row count against the required count. An emptied, wiped or
--     fully filtered relation breaches it, and no value rule of this file then reads a row.
--
--   rating_request_id_not_carried
--     Each request id of the expected_request_ids variable is carried by at least one row
--     of the relation under test, read through the upstream record because this relation
--     carries no request_id column. That variable defaults to an empty list, which withdraws
--     this rule and leaves every other rule of this file asserted; a run that requires the
--     rule supplies the list itself, as in
--     --vars '{expected_request_ids: ["01AMOT", "01ACOM"]}', the two request ids of
--     the authored sample definitions under modernization/extraction/sample_input/: 01AMOT,
--     which the routing EVALUATE at base/src/lgapdb01.cbl:196 resolves to policy type M, and
--     01ACOM, which base/src/lgapdb01.cbl:200 resolves to policy type C. The number of rows
--     carrying a supplied request id is not read, so a second source system, a further
--     policy of the same product and a backfill each add rows under a supplied request id
--     without breaching this rule; the uniqueness of the natural key of every one of those
--     rows is asserted by rating_key_not_unique above. A row carrying a request id outside
--     the supplied list is not read by this rule, so the 01AEND and 01AHOU rows the routing
--     admits at base/src/lgapdb01.cbl:188 and :192 neither satisfy nor breach it under the
--     two-sample list.
--
--   rating_key_absent_from_issued_policy
--   issued_policy_key_absent_from_rating
--   cross_mart_key_not_carried_once_by_each
--     canonical.issued_policy and canonical.preissued_rating carry the same key set, and
--     each key is carried by exactly one row of each relation. Dropping, emptying or
--     further filtering either relation is returned.
--
--   rating_text_value_outside_declared_width
--     Each text value observes the width its contract declares: source_system_key at most
--     64 characters and policy_type exactly 1. Amazon Redshift enforces those widths itself;
--     DuckDB collapses varchar(n) and char(n) to VARCHAR and enforces no width, so this rule
--     is the assertion of the declared width on that adapter.
--
--   rating_text_value_differs_from_upstream
--     Each text value equals the value ref('int_policy_issue_decoded') carries for the same
--     key. The model applies a width-bounding cast to both columns and changes no character
--     of a value that fits its declared width.
--
--   rating_contract_column_missing_from_relation
--   rating_relation_column_absent_from_contract
--   rating_column_position_differs
--   rating_column_type_family_differs
--   rating_column_width_bound_differs
--   rating_column_numeric_precision_differs
--   rating_column_numeric_scale_differs
--   rating_column_nullability_differs
--     The physical relation carries exactly the 9 columns of the contract in
--     models/marts/canonical/_canonical__models.yml, in the order that file declares them,
--     each with the type family and the nullability declared there. The declared width of a
--     text column is compared where the adapter reports one: Amazon Redshift reports
--     character_maximum_length and DuckDB reports none for VARCHAR, and the width of every
--     value is asserted by the two value rules above on both adapters. Each of the six amount
--     columns carries the numeric precision and the numeric scale of its
--     declaration: DECIMAL(8,2) for payment_amount and motor_premium_amount, the digit count
--     of PIC 9(6) plus two, and DECIMAL(10,2) for the four commercial premiums, the digit
--     count of PIC 9(8) plus two. The type family folds the spellings the two adapters report
--     onto one name: DuckDB reports VARCHAR, BIGINT and DECIMAL(p,s), and Amazon Redshift
--     reports character varying, character, bigint and numeric. Precision and scale are
--     compared for the six amount columns, the columns for which both adapters report the
--     declared values. dbt matches a contract to a model by column name and does not compare
--     column order, so the order is asserted here.
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
-- What this test does not assert. It applies no amount predicate: the product null pattern
-- of the six amount columns, the equality of each amount with its upstream value, the
-- comparison tolerance modernization/extraction/copybook_field_map.yml records under
-- comparison.amount_tolerance_abs, the non-negative domain and the source-domain magnitude
-- of each amount are asserted by tests/assert_product_premium_nullability.sql, and the
-- harness-to-warehouse comparison is applied by
-- modernization/validation/diff_harness_vs_warehouse.py, whose comparison is recorded in
-- modernization/validation/artifacts/diff-report.md under the disposition
-- validated against local substitute, not AWS. It asserts no relation inventory:
-- tests/assert_issued_policy_unique_key.sql asserts that the schema holding the two marts
-- carries exactly issued_policy and preissued_rating. The accepted values of policy_type and
-- the null behaviour of every column are asserted by the built-in tests of
-- models/marts/canonical/_canonical__models.yml.
--
-- Configuration. It sets no dbt config of any kind, so every dbt default applies to it and
-- a returned row fails the run. The one variable it reads, expected_request_ids, defaults to
-- an empty list in the call below, is declared in no project file, and is supplied on the
-- command line by a run that asserts the rule reading it.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB. The catalog read names an
-- information_schema relation both adapters carry and compares no adapter-specific spelling.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file:
-- modernization/docs/decision-log.md

{% set rating = ref('canonical_preissued_rating') %}
{% set issued = ref('canonical_issued_policy') %}
{% set upstream = ref('int_policy_issue_decoded') %}

{# Request ids each expected to be carried by at least one row. The default empty list
   withdraws that rule and leaves every other rule of this file asserted. #}
{% set expected_request_ids = var('expected_request_ids', []) %}

{# The two text columns of the relation, with the width each contract declares and whether
   that width is the exact length of every value. #}
{% set text_columns = [
    {'name': 'source_system_key', 'declared': 'VARCHAR(64)', 'width': 64, 'exact': false},
    {'name': 'policy_type',       'declared': 'CHAR(1)',     'width': 1,  'exact': true}
] %}

{# The 9 columns of the contract in models/marts/canonical/_canonical__models.yml, in the
   order that file declares them: name, position, type family, declared text width, declared
   numeric precision and scale, and is_nullable as information_schema reports it. #}
{% set contract_columns = [
    {'name': 'source_system_key',      'position': 1, 'family': 'text',    'width': 64,   'precision': none, 'scale': none, 'nullable': 'NO'},
    {'name': 'policy_number',          'position': 2, 'family': 'bigint',  'width': none, 'precision': none, 'scale': none, 'nullable': 'NO'},
    {'name': 'policy_type',            'position': 3, 'family': 'text',    'width': 1,    'precision': none, 'scale': none, 'nullable': 'NO'},
    {'name': 'payment_amount',         'position': 4, 'family': 'decimal', 'width': none, 'precision': 8,    'scale': 2,    'nullable': 'YES'},
    {'name': 'motor_premium_amount',   'position': 5, 'family': 'decimal', 'width': none, 'precision': 8,    'scale': 2,    'nullable': 'YES'},
    {'name': 'fire_premium_amount',    'position': 6, 'family': 'decimal', 'width': none, 'precision': 10,   'scale': 2,    'nullable': 'YES'},
    {'name': 'crime_premium_amount',   'position': 7, 'family': 'decimal', 'width': none, 'precision': 10,   'scale': 2,    'nullable': 'YES'},
    {'name': 'flood_premium_amount',   'position': 8, 'family': 'decimal', 'width': none, 'precision': 10,   'scale': 2,    'nullable': 'YES'},
    {'name': 'weather_premium_amount', 'position': 9, 'family': 'decimal', 'width': none, 'precision': 10,   'scale': 2,    'nullable': 'YES'}
] %}

with

-- Rows of the relation under test per key pair.
rating_keys as (

    select
        source_system_key,
        policy_number,
        count(*) as mart_rows

    from {{ rating }}

    group by source_system_key, policy_number

),

-- Rows of the issued mart per key pair, for the cross-relation key parity.
issued_keys as (

    select
        source_system_key,
        policy_number,
        count(*) as issued_rows

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

-- Every key either the relation under test or the upstream record carries.
key_parity as (

    select
        coalesce(m.source_system_key, u.source_system_key) as source_system_key,
        coalesce(m.policy_number, u.policy_number) as policy_number,
        coalesce(m.mart_rows, 0) as mart_rows,
        coalesce(u.upstream_rows, 0) as upstream_rows,
        coalesce(u.upstream_successful_rows, 0) as upstream_successful_rows,
        u.lowest_return_code,
        u.highest_return_code

    from rating_keys m

    full outer join upstream_keys u
        on m.source_system_key = u.source_system_key
        and m.policy_number = u.policy_number

),

-- The first key rule each key breaches, or null where it breaches none.
key_breaches as (

    select
        case
            when mart_rows > 1
                then 'rating_key_not_unique'
            when upstream_successful_rows > 0 and mart_rows = 0
                then 'rating_row_missing_for_upstream_key'
            when mart_rows > 0 and upstream_rows = 0
                then 'rating_key_absent_from_upstream'
            when mart_rows > 0 and upstream_successful_rows = 0
                then 'rating_key_without_successful_upstream_row'
            when mart_rows <> upstream_successful_rows
                then 'rating_row_count_differs_from_upstream'
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

-- Every key either canonical relation carries.
cross_mart_parity as (

    select
        coalesce(r.source_system_key, i.source_system_key) as source_system_key,
        coalesce(r.policy_number, i.policy_number) as policy_number,
        coalesce(r.mart_rows, 0) as rating_rows,
        coalesce(i.issued_rows, 0) as issued_rows

    from rating_keys r

    full outer join issued_keys i
        on r.source_system_key = i.source_system_key
        and r.policy_number = i.policy_number

),

-- The rows of the relation under test, counted for the non-emptiness rule. The count carries
-- no group by, so it yields exactly one row for an empty relation as well.
rating_row_count as (

    select count(*) as mart_rows

    from {{ rating }}

),

-- The request ids each expected to be carried by at least one row. An empty list yields the
-- typed relation below, which carries no row, so the rule reading it returns none.
expected_request_ids as (
{%- if expected_request_ids %}
{% for request_id in expected_request_ids %}
    select '{{ request_id }}' as request_id
    {%- if not loop.last %}
    union all
    {%- endif %}
{%- endfor %}
{%- else %}
    select cast(null as varchar) as request_id

    from {{ rating }}

    where 1 = 0
{%- endif %}
),

-- Rows of the relation under test per request id, read through the upstream record.
rating_request_ids as (

    select
        u.request_id,
        count(*) as mart_rows

    from {{ rating }} m

    inner join {{ upstream }} u
        on m.source_system_key = u.source_system_key
        and m.policy_number = u.policy_number
        and u.return_code = '00'

    group by u.request_id

),

-- Each row of the relation under test beside the upstream row of the same key, for the text
-- value comparison. The join reads the successful upstream rows only.
rating_with_upstream as (

    select
        m.source_system_key,
        m.policy_number,
        {%- for column in text_columns %}
        m.{{ column.name }} as mart_{{ column.name }},
        u.{{ column.name }} as upstream_{{ column.name }}{{ ',' if not loop.last }}
        {%- endfor %}

    from {{ rating }} m

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
        cast({{ column.precision if column.precision is not none else 'null' }} as integer) as numeric_precision,
        cast({{ column.scale if column.scale is not none else 'null' }} as integer) as numeric_scale,
        '{{ column.nullable }}' as is_nullable
    {%- if not loop.last %}
    union all
    {%- endif %}
{%- endfor %}
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
        cast(numeric_precision as integer) as numeric_precision,
        cast(numeric_scale as integer) as numeric_scale,
        upper(is_nullable) as is_nullable

    from information_schema.columns

    where table_catalog = '{{ rating.database }}'
        and table_schema = '{{ rating.schema }}'
        and table_name = '{{ rating.identifier }}'

),

-- The first shape rule each column of either side breaches, or null where it breaches none.
column_breaches as (

    select
        case
            when a.column_name is null
                then 'rating_contract_column_missing_from_relation'
            when e.column_name is null
                then 'rating_relation_column_absent_from_contract'
            when a.ordinal_position <> e.ordinal_position
                then 'rating_column_position_differs'
            when a.type_family <> e.type_family
                then 'rating_column_type_family_differs'
            when e.character_maximum_length is not null
                and a.character_maximum_length is not null
                and a.character_maximum_length <> e.character_maximum_length
                then 'rating_column_width_bound_differs'
            when e.numeric_precision is not null
                and coalesce(a.numeric_precision, -1) <> e.numeric_precision
                then 'rating_column_numeric_precision_differs'
            when e.numeric_scale is not null
                and coalesce(a.numeric_scale, -1) <> e.numeric_scale
                then 'rating_column_numeric_scale_differs'
            when a.is_nullable <> e.is_nullable
                then 'rating_column_nullability_differs'
        end as assertion,
        coalesce(e.column_name, a.column_name) as column_name,
        'required position ' || coalesce(cast(e.ordinal_position as varchar), '-')
            || ' family ' || coalesce(e.type_family, '-')
            || ' width ' || coalesce(cast(e.character_maximum_length as varchar), 'unbounded')
            || ' precision ' || coalesce(cast(e.numeric_precision as varchar), '-')
            || ' scale ' || coalesce(cast(e.numeric_scale as varchar), '-')
            || ' nullable ' || coalesce(e.is_nullable, '-')
            || '; observed position ' || coalesce(cast(a.ordinal_position as varchar), '-')
            || ' family ' || coalesce(a.type_family, '-')
            || ' width ' || coalesce(cast(a.character_maximum_length as varchar), 'unbounded')
            || ' precision ' || coalesce(cast(a.numeric_precision as varchar), '-')
            || ' scale ' || coalesce(cast(a.numeric_scale as varchar), '-')
            || ' nullable ' || coalesce(a.is_nullable, '-') as detail

    from contract_columns e

    full outer join catalog_columns a
        on e.column_name = a.column_name

)

-- Key and population of the relation under test.
select
    assertion,
    '{{ rating.identifier }}' as subject,
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

-- One row when the relation under test carries no row at all, so that no rule above reads an
-- empty relation.
select
    'rating_relation_carries_no_row' as assertion,
    '{{ rating.identifier }}' as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'rows=' || cast(mart_rows as varchar)
        || ' required at least 1' as detail

from rating_row_count

where mart_rows = 0

union all

-- One row per supplied expected request id no row of the relation under test carries.
select
    'rating_request_id_not_carried' as assertion,
    e.request_id as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'rows=' || cast(coalesce(m.mart_rows, 0) as varchar)
        || ' required at least 1' as detail

from expected_request_ids e

left join rating_request_ids m
    on e.request_id = m.request_id

where coalesce(m.mart_rows, 0) = 0

union all

-- One row per key in each of the two canonical relations.
select
    case
        when issued_rows = 0
            then 'rating_key_absent_from_issued_policy'
        when rating_rows = 0
            then 'issued_policy_key_absent_from_rating'
        else 'cross_mart_key_not_carried_once_by_each'
    end as assertion,
    '{{ issued.identifier }} and {{ rating.identifier }}' as subject,
    source_system_key,
    policy_number,
    'rating_rows=' || cast(rating_rows as varchar)
        || ' issued_rows=' || cast(issued_rows as varchar)
        || ' required 1 of each' as detail

from cross_mart_parity

where rating_rows <> 1 or issued_rows <> 1
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
                then 'rating_text_value_outside_declared_width'
            when mart_{{ column.name }} is null and upstream_{{ column.name }} is not null
                then 'rating_text_value_differs_from_upstream'
            when mart_{{ column.name }} is not null and upstream_{{ column.name }} is null
                then 'rating_text_value_differs_from_upstream'
            when mart_{{ column.name }} <> upstream_{{ column.name }}
                then 'rating_text_value_differs_from_upstream'
        end as assertion,
        '{{ column.name }}' as subject,
        source_system_key,
        policy_number,
        'mart=' || coalesce(mart_{{ column.name }}, 'null')
            || ' upstream=' || coalesce(upstream_{{ column.name }}, 'null')
            || ' declared {{ column.declared }}' as detail

    from rating_with_upstream

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
