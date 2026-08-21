-- assert_product_premium_nullability.sql
-- Singular test of the GenApp Policy-Issue cloud-warehouse bridge. It asserts the product
-- premium null pattern of the canonical rating mart.
--
-- Convention. This test passes on zero returned rows. The statement returns one row for
-- every row of the asserted relation that breaks a rule stated below, and returns no row
-- when every row observes every rule.
--
-- Asserted relation. The model canonical_preissued_rating of models/marts/canonical, and
-- no other. The reference at the foot of this file spells that model name, which is the
-- file stem of models/marts/canonical/canonical_preissued_rating.sql; the model sets a
-- relation alias, and the alias is not the reference spelling. This statement names no
-- relation literally and reads no other model.
--
-- Columns read. policy_type and the five product premium columns motor_premium_amount,
-- fire_premium_amount, crime_premium_amount, flood_premium_amount and
-- weather_premium_amount. The presence and the absence of an amount are read only through
-- is null and is not null. A zero amount is a present value here, not an absent one.
--
-- Columns returned. source_system_key, policy_number and policy_type, which identify a
-- returned row.
--
-- Asserted rule for policy_type M. motor_premium_amount carries a value, and
-- fire_premium_amount, crime_premium_amount, flood_premium_amount and
-- weather_premium_amount are all null. Column provenance: CA-M-PREMIUM,
-- base/src/lgcmarea.cpy:73.
--
-- Asserted rule for policy_type C. fire_premium_amount, crime_premium_amount,
-- flood_premium_amount and weather_premium_amount all carry a value, and
-- motor_premium_amount is null. Column provenance: CA-B-FirePremium, CA-B-CrimePremium,
-- CA-B-FloodPremium and CA-B-WeatherPremium, base/src/lgcmarea.cpy:85, :87, :89 and :91.
--
-- Asserted rule for policy_type E and for policy_type H. All five product premium columns
-- are null.
--
-- Asserted totality guard. A policy_type outside M, C, E and H is a breach and is
-- returned, and a null policy_type is a breach and is returned. The observed domain of the
-- column is E, H, M and C, assigned by the request-routing EVALUATE at
-- base/src/lgapdb01.cbl:184-207.
--
-- Not asserted here. payment_amount is not read. No amount is compared with another
-- amount and no amount is summed. No amount magnitude, range or tolerance is read. No row
-- count is asserted. No rating formula, rating factor, derived factor or commission value
-- is asserted.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4, dbt Transformation DAG and Field Allocation,
-- in modernization/docs/architecture.md.
-- modernization/docs/decision-log.md

select

    source_system_key,
    policy_number,
    policy_type

from {{ ref('canonical_preissued_rating') }}

where

    -- policy_type M: the motor premium is present and the four commercial premiums are
    -- absent.
    (
        policy_type = 'M'
        and not (
            motor_premium_amount is not null
            and fire_premium_amount is null
            and crime_premium_amount is null
            and flood_premium_amount is null
            and weather_premium_amount is null
        )
    )

    -- policy_type C: the four commercial premiums are present and the motor premium is
    -- absent.
    or (
        policy_type = 'C'
        and not (
            fire_premium_amount is not null
            and crime_premium_amount is not null
            and flood_premium_amount is not null
            and weather_premium_amount is not null
            and motor_premium_amount is null
        )
    )

    -- policy_type E and policy_type H: all five product premiums are absent.
    or (
        policy_type in ('E', 'H')
        and not (
            motor_premium_amount is null
            and fire_premium_amount is null
            and crime_premium_amount is null
            and flood_premium_amount is null
            and weather_premium_amount is null
        )
    )

    -- Totality guard. The first disjunct below returns a policy_type outside M, C, E and
    -- H. The second returns a null policy_type, for which not in yields null rather than
    -- true.
    or policy_type not in ('M', 'C', 'E', 'H')
    or policy_type is null
