-- assert_product_premium_nullability.sql
-- Singular test of the GenApp Policy-Issue cloud-warehouse bridge, and one of the three
-- singular tests of modernization/dbt/genapp_rqi/tests/. It asserts the product premium null
-- pattern and the amount values of the canonical rating mart.
-- The other two singular tests of that directory are
-- tests/assert_issued_policy_unique_key.sql and tests/assert_preissued_rating_unique_key.sql,
-- which assert the keys, the population, the text values and the physical shape of the two
-- canonical relations, the parity of their key sets and the relation inventory of the schema
-- holding them. Neither reads this file.
--
-- Convention. This test passes on zero returned rows. The statement returns one row for
-- every row of the asserted relation, every expected request id and every amount column that
-- breaks a rule stated below, and returns no row when every rule holds.
--
-- Asserted relation. The model canonical_preissued_rating of models/marts/canonical, and no
-- other. The reference below spells that model name, which is the file stem of
-- models/marts/canonical/canonical_preissued_rating.sql; the model sets a relation alias, and
-- the alias is not the reference spelling. This statement names no relation literally.
--
-- Relations read. ref('canonical_preissued_rating'), the asserted relation, and
-- ref('int_policy_issue_decoded'), the upstream record every row of that relation is
-- projected from, read for its key, its request id, its return code and its six amounts.
--
-- Columns read. policy_type and the six amount columns payment_amount,
-- motor_premium_amount, fire_premium_amount, crime_premium_amount, flood_premium_amount and
-- weather_premium_amount, together with the key columns source_system_key and policy_number.
-- The presence and the absence of an amount are read through is null and is not null. A zero
-- amount is a present value here, not an absent one.
--
-- Columns returned. Five: assertion, the name of the rule the returned row breaches; subject,
-- the amount column or request id the breach concerns, or the asserted relation for a null
-- pattern breach; source_system_key and policy_number, the key of the breaching row, null for
-- a request-id breach; and detail, the observed values against the required values.
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
-- Asserted rule premium_row_missing_for_expected_request_id. Each request id of the
-- expected_request_ids variable is carried by exactly one row of the asserted relation, read
-- through the upstream record because the relation carries no request_id column. The default
-- of that variable is 01AMOT, which base/src/lgapdb01.cbl:196 resolves to policy type M, and
-- 01ACOM, which base/src/lgapdb01.cbl:200 resolves to policy type C, so the motor rule and
-- the commercial rule above are each exercised by one row. A row carrying any other routed
-- request id neither satisfies nor breaches this rule. An emptied, wiped or fully filtered
-- relation breaches it, and no rule above can then hold vacuously.
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
-- base/src/lgcmarea.cpy:37-43 and carries a value for every policy type.
--
-- Configuration. This file declares none. dbt applies its defaults for a singular test, and a
-- returned row fails the run. The one variable it reads, expected_request_ids, carries its
-- default in the call below and is declared in no project file.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

{% set rating = ref('canonical_preissued_rating') %}
{% set upstream = ref('int_policy_issue_decoded') %}

{# Request ids expected to be carried by exactly one row each. #}
{% set expected_request_ids = var('expected_request_ids', ['01AMOT', '01ACOM']) %}

{# The absolute delta the amount comparison tolerates, as recorded under
   comparison.amount_tolerance_abs in modernization/extraction/copybook_field_map.yml. #}
{% set amount_tolerance_abs = 0.01 %}

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

-- The request ids expected to be carried by exactly one row each.
expected_request_ids as (
{% for request_id in expected_request_ids %}
    select '{{ request_id }}' as request_id
    {%- if not loop.last %}
    union all
    {%- endif %}
{%- endfor %}
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

-- One row per expected request id, so that the motor rule and the commercial rule above are
-- each exercised by one row.
select
    'premium_row_missing_for_expected_request_id' as assertion,
    e.request_id as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    'rows=' || cast(coalesce(m.mart_rows, 0) as varchar) || ' required 1' as detail

from expected_request_ids e

left join rating_request_ids m
    on e.request_id = m.request_id

where coalesce(m.mart_rows, 0) <> 1
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
