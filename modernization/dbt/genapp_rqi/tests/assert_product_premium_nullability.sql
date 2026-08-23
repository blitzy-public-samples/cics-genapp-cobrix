-- assert_product_premium_nullability.sql
-- Singular test of the GenApp Policy-Issue cloud-warehouse bridge, and one of the four
-- singular tests of modernization/dbt/genapp_rqi/tests/. It asserts the product premium null
-- pattern and the amount values of the canonical rating mart, and the product premium
-- allocation of the landed record that mart is projected from.
-- The other three singular tests of that directory are
-- tests/assert_issued_policy_unique_key.sql and tests/assert_preissued_rating_unique_key.sql,
-- which assert the keys, the population, the text values and the physical shape of the two
-- canonical relations, the parity of their key sets and the relation inventory of the schema
-- holding them, and tests/assert_canonical_column_widths.sql, which asserts the declared type
-- and declared width of every column of both relations from the parsed project. None of the
-- three reads this file.
--
-- Convention. This test passes on zero returned rows. The statement returns one row for
-- every row of the asserted relation, every landed row the landed rules read, every supplied
-- expected request id and every amount column that breaks a rule stated below, one row when
-- the asserted relation carries no row at all, and no row when every rule holds.
--
-- Asserted relation. The model canonical_preissued_rating of models/marts/canonical, and no
-- other. The reference below spells that model name, which is the file stem of
-- models/marts/canonical/canonical_preissued_rating.sql; the model sets a relation alias, and
-- the alias is not the reference spelling. This statement names no relation literally.
--
-- Relations read. ref('canonical_preissued_rating'), the asserted relation;
-- ref('int_policy_issue_decoded'), the upstream record every row of that relation is
-- projected from, read for its key, its request id, its return code and its six amounts; and
-- source('genapp', 'genapp_policy_issue'), the landed relation the record is decoded from,
-- read for its key, its policy type, its return code and its five product premiums by the
-- landed rules below.
--
-- Columns read. policy_type and the six amount columns payment_amount,
-- motor_premium_amount, fire_premium_amount, crime_premium_amount, flood_premium_amount and
-- weather_premium_amount, together with the key columns source_system_key and policy_number.
-- The presence and the absence of an amount are read through is null and is not null. A zero
-- amount is a present value here, not an absent one. The landed rules read the same column
-- names of the landed relation together with return_code; every landed column is VARCHAR, and
-- a landed value is read as present unless it is null, empty or whitespace alone.
--
-- Columns returned. Five: assertion, the name of the rule the returned row breaches; subject,
-- the amount column or request id the breach concerns, the asserted relation for a null
-- pattern breach and for a non-emptiness breach, or the schema-qualified landed relation for
-- a landed product allocation breach; source_system_key and policy_number, the key of the
-- breaching row, null for a request-id breach and for a non-emptiness breach; and detail, the
-- observed values against the required values. A landed breach carries the landed
-- source_system_key in the key column of that name, null in policy_number, and the landed
-- policy number as text in detail: the landed column is VARCHAR and this test converts no
-- landed value.
--
-- Asserted rule motor_row_premium_pattern. For policy_type M, motor_premium_amount carries a
-- value, and fire_premium_amount, crime_premium_amount, flood_premium_amount and
-- weather_premium_amount are all null. Column provenance: CA-M-PREMIUM,
-- base/src/lgcmarea.cpy:73.
--
-- Asserted rule commercial_row_premium_pattern. For policy_type C, fire_premium_amount,
-- crime_premium_amount, flood_premium_amount and weather_premium_amount all carry a value,
-- and motor_premium_amount is null. Column provenance: CA-B-FirePremium, CA-B-CrimePremium,
-- CA-B-FloodPremium and CA-B-WeatherPremium, base/src/lgcmarea.cpy:85, :87, :89 and :91.
--
-- Asserted rule endowment_or_house_row_premium_pattern. For policy_type E and for policy_type
-- H, all five product premium columns are null. The two policy types are routed by the same
-- EVALUATE as M and C, at base/src/lgapdb01.cbl:188 and :192, and neither redefines a premium
-- item: the CA-ENDOWMENT overlay at base/src/lgcmarea.cpy:46 and the CA-HOUSE overlay at
-- base/src/lgcmarea.cpy:56 declare no premium.
--
-- Asserted rule policy_type_outside_routed_domain. A policy_type outside M, C, E and H is a
-- breach and is returned, and a null policy_type is a breach and is returned. The observed
-- domain of the column is E, H, M and C, assigned by the request-routing EVALUATE at
-- base/src/lgapdb01.cbl:184-207.
--
-- Landed rows read by the four landed rules below. The rows of
-- source('genapp', 'genapp_policy_issue') whose return_code is 00, which are the rows
-- models/marts/canonical/canonical_preissued_rating.sql materializes. A landed row carrying
-- 70, 80, 90, 98 or 99 reaches no canonical relation and is read by no rule of this file.
--
-- Presence of a landed value. Every landed column is VARCHAR. A landed rule reads a value
-- through nullif(trim(value), ''), the reading
-- models/staging/genapp_class_exemplar/stg_genapp__policy_issue.sql applies, so null, the
-- empty string and whitespace alone are absent and every other value is present: the text 0
-- standing in an inapplicable premium is a present value and breaches the rule that requires
-- that premium to be absent.
--
-- Layer the landed rules read. models/intermediate/int_policy_issue_decoded.sql selects each
-- product premium through a CASE on policy_type, so a value landed in a premium the policy
-- type does not carry reaches both that record and the asserted relation as null and agrees
-- with every mart rule above. The landed rules read the landed row itself, where that value
-- is still present.
--
-- Asserted rule landed_motor_row_premium_pattern. For a landed policy_type of M,
-- motor_premium_amount is present and fire_premium_amount, crime_premium_amount,
-- flood_premium_amount and weather_premium_amount are all absent. Request id 01AMOT selects
-- the motor overlay at base/src/lgapdb01.cbl:194-196, and the four commercial premium windows
-- then fall inside CA-M-FILLER, base/src/lgcmarea.cpy:75, whose content is not an amount of
-- the record. The same allocation is the allOf rule titled Motor product premium allocation
-- of modernization/landing/landing-schema.json.
--
-- Asserted rule landed_commercial_row_premium_pattern. For a landed policy_type of C,
-- fire_premium_amount, crime_premium_amount, flood_premium_amount and weather_premium_amount
-- are all present and motor_premium_amount is absent. Request id 01ACOM selects the commercial
-- overlay at base/src/lgapdb01.cbl:198-200, and the motor premium window then holds commercial
-- overlay content that is not an amount of the record. The same allocation is the allOf rule
-- titled Commercial product premium allocation of
-- modernization/landing/landing-schema.json.
--
-- Asserted rule landed_endowment_or_house_row_premium_pattern. For a landed policy_type of E
-- and for a landed policy_type of H, all five product premiums are absent. The endowment
-- overlay at base/src/lgcmarea.cpy:46 and the house overlay at base/src/lgcmarea.cpy:56
-- declare no premium item. The same allocation is the allOf rules titled Endowment product
-- premium allocation and House product premium allocation of
-- modernization/landing/landing-schema.json.
--
-- Asserted rule landed_policy_type_outside_routed_domain. A landed policy_type outside M, C,
-- E and H is a breach and is returned, and a null landed policy_type is a breach and is
-- returned, so no landed row of the rows read escapes the three landed allocation rules
-- above.
--
-- Asserted rule premium_relation_carries_no_row. The asserted relation carries at least one
-- row. The rule returns exactly one row when the relation carries none, whatever the
-- expected_request_ids variable holds, and the detail column carries the observed row count
-- against the required count. An emptied, wiped or fully filtered relation breaches it, and
-- no null pattern rule and no amount rule of this file then reads a row.
--
-- Asserted rule premium_row_missing_for_expected_request_id. Each request id of the
-- expected_request_ids variable is carried by at least one row of the asserted relation, read
-- through the upstream record because the relation carries no request_id column. That
-- variable defaults to an empty list, which withdraws this rule and leaves every other rule
-- of this file asserted; a run that requires the rule supplies the list itself, as in
-- --vars '{expected_request_ids: ["01AMOT", "01ACOM"]}', which names the request id
-- base/src/lgapdb01.cbl:196 resolves to policy type M and the request id
-- base/src/lgapdb01.cbl:200 resolves to policy type C, so on that run the motor rule and the
-- commercial rule above are each exercised by at least one row. The number of rows carrying a
-- supplied request id is not read, so a second source system, a further policy of the same
-- product and a backfill each add rows under a supplied request id without breaching this
-- rule, and each added row is read by the null pattern and amount rules above. A row carrying
-- a request id outside the supplied list neither satisfies nor breaches this rule.
--
-- Asserted rule rating_amount_presence_differs_from_upstream. Each amount is present in the
-- asserted relation exactly where ref('int_policy_issue_decoded') carries it for the same
-- key.
--
-- Asserted rule rating_amount_differs_from_upstream. Each amount equals the value
-- ref('int_policy_issue_decoded') carries for the same key. The two mart models apply no
-- arithmetic and no rescale to an amount, so the equality is exact. The rule returns a row
-- when the absolute delta exceeds 0.01, the value
-- modernization/extraction/copybook_field_map.yml records under
-- comparison.amount_tolerance_abs; a non-zero delta within that tolerance passes here and is
-- reported as unexpected by modernization/validation/diff_harness_vs_warehouse.py, which
-- applies the same tolerance to the harness-to-warehouse comparison.
--
-- Asserted rule rating_amount_negative. No amount is negative. All six COBOL declarations are
-- unsigned DISPLAY numerics carrying neither S nor V: CA-PAYMENT PIC 9(6),
-- base/src/lgcmarea.cpy:43; CA-M-PREMIUM PIC 9(6), base/src/lgcmarea.cpy:73; and the four
-- commercial premiums PIC 9(8), base/src/lgcmarea.cpy:85, :87, :89 and :91.
--
-- Asserted rule rating_amount_above_source_domain. No amount exceeds the largest value its
-- COBOL declaration holds: 999999 for the two PIC 9(6) declarations and 99999999 for the four
-- PIC 9(8) declarations. Those maxima are held by DECIMAL(8,2) and DECIMAL(10,2), the declared
-- types of the columns.
--
-- Not asserted here. No amount is compared with another amount and no amount is summed. No
-- key uniqueness, no key parity, no relation inventory and no physical column type is
-- asserted: tests/assert_issued_policy_unique_key.sql and
-- tests/assert_preissued_rating_unique_key.sql carry those rules, and the second of them
-- asserts the numeric precision and the numeric scale of all six amount columns. No rating
-- formula, rating factor, derived factor or commission value is asserted; the three named
-- programs base/src/lgapol01.cbl, base/src/lgapdb01.cbl and base/src/lgapvs01.cbl carry no
-- COMPUTE, MULTIPLY, DIVIDE or COMP-3 statement, and each amount reaches its Db2 host
-- variable through a plain MOVE. payment_amount is read by the value rules and by no null
-- pattern rule: it is declared in the product-independent group CA-POLICY-COMMON at
-- base/src/lgcmarea.cpy:37-43 and carries a value for every policy type, and no landed rule
-- reads the landed payment_amount. The landed rules read presence and absence and no landed
-- value is compared with a mart amount, converted or measured against a source domain; the
-- landed column set, the landed column order and the landed column types are asserted by
-- tests/assert_issued_policy_unique_key.sql,
-- models/staging/genapp_class_exemplar/_genapp__sources.yml and
-- modernization/warehouse/ddl/02_raw_genapp_policy_issue.sql.
--
-- Configuration. This file declares none. dbt applies its defaults for a singular test, and a
-- returned row fails the run. The one variable it reads, expected_request_ids, defaults to an
-- empty list in the call below, is declared in no project file, and is supplied on the command
-- line by a run that asserts the rule reading it.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

{% set rating = ref('canonical_preissued_rating') %}
{% set upstream = ref('int_policy_issue_decoded') %}
{% set landed = source('genapp', 'genapp_policy_issue') %}

{# Request ids each expected to be carried by at least one row. The default empty list
   withdraws that rule and leaves every other rule of this file asserted. #}
{% set expected_request_ids = var('expected_request_ids', []) %}

{# The absolute delta the amount comparison tolerates, as recorded under
   comparison.amount_tolerance_abs in modernization/extraction/copybook_field_map.yml. #}
{% set amount_tolerance_abs = 0.01 %}

{# The five product premium columns of the landed relation, read by the landed rules. The
   landed payment_amount is read by no landed rule: CA-PAYMENT is declared in the
   product-independent group CA-POLICY-COMMON at base/src/lgcmarea.cpy:37-43. #}
{% set landed_product_premium_columns = [
    'motor_premium_amount', 'fire_premium_amount', 'crime_premium_amount',
    'flood_premium_amount', 'weather_premium_amount'
] %}

{# The six amount columns, each with the COBOL declaration it passes through and the largest
   value that declaration holds. #}
{% set amount_columns = [
    {'name': 'payment_amount',         'item': 'CA-PAYMENT',          'picture': 'PIC 9(6)', 'maximum': 999999},
    {'name': 'motor_premium_amount',   'item': 'CA-M-PREMIUM',        'picture': 'PIC 9(6)', 'maximum': 999999},
    {'name': 'fire_premium_amount',    'item': 'CA-B-FirePremium',    'picture': 'PIC 9(8)', 'maximum': 99999999},
    {'name': 'crime_premium_amount',   'item': 'CA-B-CrimePremium',   'picture': 'PIC 9(8)', 'maximum': 99999999},
    {'name': 'flood_premium_amount',   'item': 'CA-B-FloodPremium',   'picture': 'PIC 9(8)', 'maximum': 99999999},
    {'name': 'weather_premium_amount', 'item': 'CA-B-WeatherPremium', 'picture': 'PIC 9(8)', 'maximum': 99999999}
] %}

with

-- Each row of the asserted relation beside the upstream row of the same key, for the amount
-- comparison. The join reads the successful upstream rows only.
rating_with_upstream as (

    select
        m.source_system_key,
        m.policy_number,
        u.request_id,
        {%- for column in amount_columns %}
        m.{{ column.name }} as mart_{{ column.name }},
        u.{{ column.name }} as upstream_{{ column.name }}{{ ',' if not loop.last }}
        {%- endfor %}

    from {{ rating }} m

    inner join {{ upstream }} u
        on m.source_system_key = u.source_system_key
        and m.policy_number = u.policy_number
        and u.return_code = '00'

),

-- The landed rows the asserted relation is materialized from, with every read column
-- normalized the way models/staging/genapp_class_exemplar/stg_genapp__policy_issue.sql
-- normalizes it: trimmed, and null where the trimmed value is empty. A value that survives
-- that normalization is a present value, the text 0 included. The key columns are renamed so
-- that no landed name is shadowed by an output column of the landed rule below.
landed_premiums as (

    select
        nullif(trim(source_system_key), '') as landed_source_system_key,
        nullif(trim(policy_number), '') as landed_policy_number,
        nullif(trim(policy_type), '') as landed_policy_type,
        {%- for column in landed_product_premium_columns %}
        nullif(trim({{ column }}), '') as {{ column }}{{ ',' if not loop.last }}
        {%- endfor %}

    from {{ landed }}

    where nullif(trim(return_code), '') = '00'

),

-- The rows of the asserted relation, counted for the non-emptiness rule. The count carries no
-- group by, so it yields exactly one row for an empty relation as well.
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

-- Rows of the asserted relation per request id, read through the upstream record.
rating_request_ids as (

    select
        request_id,
        count(*) as mart_rows

    from rating_with_upstream

    group by request_id

)

-- Product premium null pattern, one row per breaching row of the asserted relation.
select
    assertion,
    subject,
    source_system_key,
    policy_number,
    detail

from (

    select
        case

            -- policy_type M: the motor premium is present and the four commercial premiums
            -- are absent.
            when policy_type = 'M'
                and not (
                    motor_premium_amount is not null
                    and fire_premium_amount is null
                    and crime_premium_amount is null
                    and flood_premium_amount is null
                    and weather_premium_amount is null
                )
                then 'motor_row_premium_pattern'

            -- policy_type C: the four commercial premiums are present and the motor premium
            -- is absent.
            when policy_type = 'C'
                and not (
                    fire_premium_amount is not null
                    and crime_premium_amount is not null
                    and flood_premium_amount is not null
                    and weather_premium_amount is not null
                    and motor_premium_amount is null
                )
                then 'commercial_row_premium_pattern'

            -- policy_type E and policy_type H: all five product premiums are absent.
            when policy_type in ('E', 'H')
                and not (
                    motor_premium_amount is null
                    and fire_premium_amount is null
                    and crime_premium_amount is null
                    and flood_premium_amount is null
                    and weather_premium_amount is null
                )
                then 'endowment_or_house_row_premium_pattern'

            -- Totality guard. The first test below returns a policy_type outside M, C, E and
            -- H. The second returns a null policy_type, for which not in yields null rather
            -- than true.
            when policy_type not in ('M', 'C', 'E', 'H')
                then 'policy_type_outside_routed_domain'
            when policy_type is null
                then 'policy_type_outside_routed_domain'

        end as assertion,
        '{{ rating.identifier }}' as subject,
        source_system_key,
        policy_number,
        'policy_type=' || coalesce(policy_type, 'null')
            || ' motor=' || coalesce(cast(motor_premium_amount as varchar), 'null')
            || ' fire=' || coalesce(cast(fire_premium_amount as varchar), 'null')
            || ' crime=' || coalesce(cast(crime_premium_amount as varchar), 'null')
            || ' flood=' || coalesce(cast(flood_premium_amount as varchar), 'null')
            || ' weather=' || coalesce(cast(weather_premium_amount as varchar), 'null') as detail

    from {{ rating }}

) as premium_pattern_checks

where assertion is not null

union all

-- Product premium allocation of the landed relation, one row per breaching landed row. The
-- rules read presence and absence of a landed text value, so a premium the policy type does
-- not carry is returned here while it is still present in the landed row, before
-- ref('int_policy_issue_decoded') selects it through its CASE on policy_type.
select
    assertion,
    subject,
    source_system_key,
    policy_number,
    detail

from (

    select
        case

            -- Landed policy_type M: the motor premium is present and the four commercial
            -- premiums are absent.
            when landed_policy_type = 'M'
                and not (
                    motor_premium_amount is not null
                    and fire_premium_amount is null
                    and crime_premium_amount is null
                    and flood_premium_amount is null
                    and weather_premium_amount is null
                )
                then 'landed_motor_row_premium_pattern'

            -- Landed policy_type C: the four commercial premiums are present and the motor
            -- premium is absent.
            when landed_policy_type = 'C'
                and not (
                    fire_premium_amount is not null
                    and crime_premium_amount is not null
                    and flood_premium_amount is not null
                    and weather_premium_amount is not null
                    and motor_premium_amount is null
                )
                then 'landed_commercial_row_premium_pattern'

            -- Landed policy_type E and landed policy_type H: all five product premiums are
            -- absent.
            when landed_policy_type in ('E', 'H')
                and not (
                    motor_premium_amount is null
                    and fire_premium_amount is null
                    and crime_premium_amount is null
                    and flood_premium_amount is null
                    and weather_premium_amount is null
                )
                then 'landed_endowment_or_house_row_premium_pattern'

            -- Totality guard. The first test below returns a landed policy_type outside M, C,
            -- E and H. The second returns a null landed policy_type, for which not in yields
            -- null rather than true.
            when landed_policy_type not in ('M', 'C', 'E', 'H')
                then 'landed_policy_type_outside_routed_domain'
            when landed_policy_type is null
                then 'landed_policy_type_outside_routed_domain'

        end as assertion,
        '{{ landed.schema }}.{{ landed.identifier }}' as subject,
        landed_source_system_key as source_system_key,
        cast(null as bigint) as policy_number,
        'policy_number=' || coalesce(landed_policy_number, 'null')
            || ' policy_type=' || coalesce(landed_policy_type, 'null')
            {%- for column in landed_product_premium_columns %}
            || ' {{ column | replace('_premium_amount', '') }}='
                || coalesce({{ column }}, 'null')
            {%- endfor %} as detail

    from landed_premiums

) as landed_premium_pattern_checks

where assertion is not null

union all

-- One row when the asserted relation carries no row at all, so that no rule above reads an
-- empty relation.
select
    'premium_relation_carries_no_row' as assertion,
    '{{ rating.identifier }}' as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'rows=' || cast(mart_rows as varchar)
        || ' required at least 1' as detail

from rating_row_count

where mart_rows = 0

union all

-- One row per supplied expected request id no row of the asserted relation carries.
select
    'premium_row_missing_for_expected_request_id' as assertion,
    e.request_id as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'rows=' || cast(coalesce(m.mart_rows, 0) as varchar)
        || ' required at least 1' as detail

from expected_request_ids e

left join rating_request_ids m
    on e.request_id = m.request_id

where coalesce(m.mart_rows, 0) = 0
{% for column in amount_columns %}
union all

-- Presence, value, sign and magnitude of {{ column.name }}: {{ column.item }}
-- {{ column.picture }}, largest value {{ column.maximum }}.
select
    assertion,
    subject,
    source_system_key,
    policy_number,
    detail

from (

    select
        case
            when mart_{{ column.name }} is null and upstream_{{ column.name }} is not null
                then 'rating_amount_presence_differs_from_upstream'
            when mart_{{ column.name }} is not null and upstream_{{ column.name }} is null
                then 'rating_amount_presence_differs_from_upstream'
            when abs(mart_{{ column.name }} - upstream_{{ column.name }}) > {{ amount_tolerance_abs }}
                then 'rating_amount_differs_from_upstream'
            when mart_{{ column.name }} < 0
                then 'rating_amount_negative'
            when mart_{{ column.name }} > {{ column.maximum }}
                then 'rating_amount_above_source_domain'
        end as assertion,
        '{{ column.name }}' as subject,
        source_system_key,
        policy_number,
        'mart=' || coalesce(cast(mart_{{ column.name }} as varchar), 'null')
            || ' upstream=' || coalesce(cast(upstream_{{ column.name }} as varchar), 'null')
            || ' tolerance {{ amount_tolerance_abs }} maximum {{ column.maximum }}' as detail

    from rating_with_upstream

) as {{ column.name }}_checks

where assertion is not null
{% endfor %}
