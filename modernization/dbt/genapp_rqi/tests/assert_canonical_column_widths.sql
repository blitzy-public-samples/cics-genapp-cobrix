-- assert_canonical_column_widths.sql
-- Singular test of the GenApp Policy-Issue cloud-warehouse bridge, and one of the four
-- singular tests of modernization/dbt/genapp_rqi/tests/. dbt discovers this file through the
-- test-paths entry of modernization/dbt/genapp_rqi/dbt_project.yml; nothing imports it and no
-- other file of the project reads it.
-- It asserts the declared type and the declared width of every column of the two canonical
-- relations on every adapter, including an adapter that reports no width.
-- The other three singular tests of that directory are
-- tests/assert_issued_policy_unique_key.sql and
-- tests/assert_preissued_rating_unique_key.sql, which assert the keys, the population, the
-- text values and the physical shape of the two canonical relations, and
-- tests/assert_product_premium_nullability.sql, which asserts the product premium null
-- pattern of the rating mart at the canonical layer and at the landed layer. None of the
-- three reads this file.
--
-- Convention. This test passes on zero returned rows. Every rule below is evaluated while the
-- statement is compiled, from the project dbt has parsed, and each breach is emitted into the
-- statement as one returned row; a run with no breach emits the empty typed statement alone.
--
-- What is read. The parsed project, through the graph variable dbt places in the context of a
-- singular test: for each of the two mart models, the columns block declared in
-- models/marts/canonical/_canonical__models.yml, which is the enforced contract of that
-- model, and the model SQL of models/marts/canonical/canonical_issued_policy.sql and
-- models/marts/canonical/canonical_preissued_rating.sql. No relation is queried for a value:
-- both mart models are named through a dbt reference, which is what makes dbt run this test
-- after both are built, and no row of either is read. No catalog relation is read here.
--
-- Adapter reach. dbt compares a contract with the columns a model emits through the active
-- adapter. Amazon Redshift carries varchar(n) and char(n), reports the width as
-- character_maximum_length and enforces it; DuckDB collapses varchar(n) and char(n) to
-- VARCHAR, reports no character_maximum_length and enforces no width, so on DuckDB the
-- enforced contract compares the type family and not the width and a changed width in a mart
-- model reaches the relation unreported by dbt itself. Both sides of every comparison below
-- are project text rather than adapter output, so every rule of this file is asserted
-- identically on both adapters. The width Amazon Redshift reports for a built relation is
-- compared with the declared width by the catalog rules issued_column_width_bound_differs of
-- tests/assert_issued_policy_unique_key.sql and rating_column_width_bound_differs of
-- tests/assert_preissued_rating_unique_key.sql, and the length of every stored text value is
-- compared with the declared width on both adapters by the value rules
-- issued_text_value_outside_declared_width and rating_text_value_outside_declared_width of
-- those two files. This file compares neither a stored value nor a catalog report and
-- duplicates neither rule.
--
-- Decimal columns. The six amount columns of canonical.preissued_rating are declared
-- decimal(8,2) and decimal(10,2) and are asserted by rule
-- canonical_contract_type_differs_from_required below together with every other column. Their
-- precision and scale also reach both adapters through the enforced contract, which compares
-- decimal(p,s) in full on DuckDB as well, and are compared with the catalog by the rules
-- rating_column_numeric_precision_differs and rating_column_numeric_scale_differs of
-- tests/assert_preissued_rating_unique_key.sql. The width collapse above applies to
-- varchar(n) and char(n) alone.
--
-- Asserted rule canonical_model_not_in_project_graph. Each of the two mart model names is
-- carried by the parsed project as a model node with a non-empty columns block. A renamed
-- model file, a model moved out of the project and a contract with no column reach this rule,
-- and the rules below then read nothing for that model: this rule is what makes their silence
-- a failure rather than a pass.
--
-- Asserted rule canonical_contract_column_not_declared. Each column instance required below
-- is declared in the columns block of its model with a data_type value.
--
-- Asserted rule canonical_contract_column_unexpected. The columns block of each model
-- declares no column beside the instances required below, so the declared column set of each
-- relation is exactly the set of AAP section 0.3.2: 11 columns for canonical.issued_policy
-- and 9 for canonical.preissued_rating, 20 column instances in total.
--
-- Asserted rule canonical_contract_type_differs_from_required. The data_type declared for
-- each column instance is the type the canonical contract fixes: varchar(64)
-- source_system_key, char(1) policy_type, varchar(6) request_id, char(2) return_code,
-- varchar(10) brokers_reference, bigint policy_number, bigint customer_number, bigint
-- broker_id, date issue_date, date expiry_date, timestamp last_changed, decimal(8,2)
-- payment_amount and motor_premium_amount, and decimal(10,2) for each of the four commercial
-- premium columns. A width narrowed or widened in
-- models/marts/canonical/_canonical__models.yml is returned here on both adapters.
--
-- Asserted rule canonical_model_cast_type_differs_from_contract. Where the select list of a
-- mart model casts a declared column, it casts it to the type that column's contract
-- declares. cast(policy_type as varchar(20)) under a char(1) contract is returned here, and
-- so is any other cast whose type or width differs from the declaration, including a cast of
-- a bigint, date, timestamp or decimal column.
--
-- Asserted rule canonical_model_cast_missing. Each column whose declared type carries a
-- character width is cast to that type by the select list of its model: source_system_key,
-- policy_type, request_id, return_code and brokers_reference of canonical_issued_policy, and
-- source_system_key and policy_type of canonical_preissued_rating. A removed cast leaves the
-- width of that column to the adapter, and is returned here.
--
-- Asserted rule canonical_model_cast_column_absent_from_contract. The select list of a mart
-- model casts no column outside the declared column set of that model.
--
-- Asserted rule canonical_model_cast_shape_unrecognised. Every cast of a mart model is read
-- by this test. The shape read is cast(<column> as <type>) as <column>, the shape both mart
-- models use, outside the line and block comments this test removes before reading; the
-- number of casts read is compared with the number of cast keywords present, and a difference
-- is returned. A cast written in another shape is therefore returned as a breach rather than
-- passing unread.
--
-- Type spellings. A spelling is compared after lowercasing, removing whitespace and folding
-- the synonym pairs listed in the type_synonyms block below, so character varying(64) and
-- varchar(64), character(1) and char(1), and numeric(10,2) and decimal(10,2) each compare
-- equal. Nothing else is folded: a width, a precision and a scale are compared as written.
--
-- Columns returned. Five, the columns the other three singular tests return: assertion, the
-- name of the rule the returned row breaches; subject, the model and column the breach
-- concerns, or the model name for a model-level breach; source_system_key and policy_number,
-- null in every row, because no rule of this file reads a data row; and detail, the observed
-- declaration against the required declaration, naming the column, the declared type and the
-- type found.
--
-- Not asserted here. No stored value, no row count, no key, no relation inventory and no
-- catalog report is read; the three files named above carry those rules. No column order and
-- no nullability is compared: the physical order and the reported nullability of both
-- relations are asserted against the contract by the two unique-key tests. This file adds no
-- column, changes no model and reads no relation outside the two marts.
--
-- Configuration. This file declares none. dbt applies its defaults for a singular test, and a
-- returned row fails the run. It reads no variable.
--
-- This file is applied unchanged on Amazon Redshift and DuckDB.
-- Diagram reference: Figure 4 — dbt Transformation DAG and Field Allocation
-- in modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md

{% set issued = ref('canonical_issued_policy') %}
{% set rating = ref('canonical_preissued_rating') %}

{# The two mart models, each with the column instances of AAP section 0.3.2: the model name,
   the type the canonical contract fixes for the column, and whether the select list of the
   model is required to cast the column to that type. cast is required for a declared type
   carrying a character width, the widths DuckDB collapses. #}
{% set required_contracts = [
    {
        'model': 'canonical_issued_policy',
        'columns': [
            {'name': 'source_system_key', 'type': 'varchar(64)', 'cast': true},
            {'name': 'policy_number',     'type': 'bigint',      'cast': false},
            {'name': 'policy_type',       'type': 'char(1)',     'cast': true},
            {'name': 'customer_number',   'type': 'bigint',      'cast': false},
            {'name': 'request_id',        'type': 'varchar(6)',  'cast': true},
            {'name': 'return_code',       'type': 'char(2)',     'cast': true},
            {'name': 'issue_date',        'type': 'date',        'cast': false},
            {'name': 'expiry_date',       'type': 'date',        'cast': false},
            {'name': 'last_changed',      'type': 'timestamp',   'cast': false},
            {'name': 'broker_id',         'type': 'bigint',      'cast': false},
            {'name': 'brokers_reference', 'type': 'varchar(10)', 'cast': true}
        ]
    },
    {
        'model': 'canonical_preissued_rating',
        'columns': [
            {'name': 'source_system_key',      'type': 'varchar(64)',   'cast': true},
            {'name': 'policy_number',          'type': 'bigint',        'cast': false},
            {'name': 'policy_type',            'type': 'char(1)',       'cast': true},
            {'name': 'payment_amount',         'type': 'decimal(8,2)',  'cast': false},
            {'name': 'motor_premium_amount',   'type': 'decimal(8,2)',  'cast': false},
            {'name': 'fire_premium_amount',    'type': 'decimal(10,2)', 'cast': false},
            {'name': 'crime_premium_amount',   'type': 'decimal(10,2)', 'cast': false},
            {'name': 'flood_premium_amount',   'type': 'decimal(10,2)', 'cast': false},
            {'name': 'weather_premium_amount', 'type': 'decimal(10,2)', 'cast': false}
        ]
    }
] %}

{# Synonym pairs folded before two type spellings are compared, applied in this order to the
   lowercased spelling with its whitespace removed. #}
{% set type_synonyms = [
    ('charactervarying', 'varchar'),
    ('character(', 'char('),
    ('bpchar', 'char'),
    ('numeric', 'decimal'),
    ('int8', 'bigint'),
    ('timestampwithouttimezone', 'timestamp')
] %}

{# The cast shape this test reads, cast(<column> as <type>) as <column>, with the type
   carrying an optional width or an optional precision and scale, and the keyword occurrence
   counted against it. #}
{% set cast_pattern = 'cast\\s*\\(\\s*([a-z_][a-z0-9_]*)\\s+as\\s+([a-z][a-z0-9_]*(?:\\s+[a-z][a-z0-9_]*)*\\s*(?:\\(\\s*\\d+\\s*(?:,\\s*\\d+\\s*)?\\))?)\\s*\\)\\s*as\\s+([a-z_][a-z0-9_]*)' %}
{% set cast_keyword_pattern = 'cast\\s*\\(' %}

{# The line and block comment shapes removed from a model before its casts are read. #}
{% set block_comment_pattern = '/\\*[\\s\\S]*?\\*/' %}
{% set line_comment_pattern = '--[^\\n]*' %}

{# One entry per breach, each carrying the rule name, the subject and the detail of the row
   returned for it. #}
{% set breaches = [] %}

{% if execute %}

    {% for contract in required_contracts %}

        {# The model node of the parsed project carrying this model name. #}
        {% set found = namespace(node = none) %}
        {% for unique_id, node in graph.nodes.items() %}
            {% if node.resource_type == 'model' and node.name == contract.model %}
                {% set found.node = node %}
            {% endif %}
        {% endfor %}

        {% if found.node is none or not found.node.columns %}

            {% do breaches.append({
                'assertion': 'canonical_model_not_in_project_graph',
                'subject': contract.model,
                'detail': 'required a parsed model node carrying a contract columns block; found '
                    ~ ('no model node' if found.node is none else 'a model node declaring no column')
            }) %}

        {% else %}

            {# The declared type of each column of the contract, folded for comparison. #}
            {% set declared = {} %}
            {% for column_name, column in found.node.columns.items() %}
                {% set spelling = namespace(text = (column.data_type | default('', true)) | lower | replace(' ', '')) %}
                {% for synonym in type_synonyms %}
                    {% set spelling.text = spelling.text | replace(synonym[0], synonym[1]) %}
                {% endfor %}
                {% do declared.update({column_name: {'raw': column.data_type | default('', true), 'folded': spelling.text}}) %}
            {% endfor %}

            {# The casts of the model select list, read from the model SQL with its comments
               removed, and the number of cast keywords that SQL carries. #}
            {% set model_sql = modules.re.sub(line_comment_pattern, ' ',
                    modules.re.sub(block_comment_pattern, ' ', found.node.raw_code | lower)) %}
            {% set model_casts = modules.re.findall(cast_pattern, model_sql) %}
            {% set cast_keywords = modules.re.findall(cast_keyword_pattern, model_sql) %}
            {% set cast_types = {} %}
            {% for model_cast in model_casts %}
                {% set spelling = namespace(text = model_cast[1] | lower | replace(' ', '')) %}
                {% for synonym in type_synonyms %}
                    {% set spelling.text = spelling.text | replace(synonym[0], synonym[1]) %}
                {% endfor %}
                {% do cast_types.update({model_cast[2]: {'raw': model_cast[1], 'folded': spelling.text}}) %}
            {% endfor %}

            {% if model_casts | length != cast_keywords | length %}
                {% do breaches.append({
                    'assertion': 'canonical_model_cast_shape_unrecognised',
                    'subject': contract.model,
                    'detail': 'required every cast of ' ~ found.node.original_file_path
                        ~ ' in the shape cast(<column> as <type>) as <column>; read '
                        ~ model_casts | length ~ ' of ' ~ cast_keywords | length
                        ~ ' cast keywords'
                }) %}
            {% endif %}

            {% for column in contract.columns %}

                {% set requirement = namespace(text = column.type | lower | replace(' ', '')) %}
                {% for synonym in type_synonyms %}
                    {% set requirement.text = requirement.text | replace(synonym[0], synonym[1]) %}
                {% endfor %}

                {% if column.name not in declared or not declared[column.name].raw %}

                    {% do breaches.append({
                        'assertion': 'canonical_contract_column_not_declared',
                        'subject': contract.model ~ '.' ~ column.name,
                        'detail': 'required data_type ' ~ column.type ~ ' in the columns block; found '
                            ~ ('no data_type' if column.name in declared else 'no column')
                    }) %}

                {% elif declared[column.name].folded != requirement.text %}

                    {% do breaches.append({
                        'assertion': 'canonical_contract_type_differs_from_required',
                        'subject': contract.model ~ '.' ~ column.name,
                        'detail': 'required data_type ' ~ column.type ~ '; declared '
                            ~ declared[column.name].raw
                    }) %}

                {% endif %}

                {% if column.name in cast_types and column.name in declared and declared[column.name].raw
                        and cast_types[column.name].folded != declared[column.name].folded %}

                    {% do breaches.append({
                        'assertion': 'canonical_model_cast_type_differs_from_contract',
                        'subject': contract.model ~ '.' ~ column.name,
                        'detail': 'declared data_type ' ~ declared[column.name].raw
                            ~ '; model casts to ' ~ cast_types[column.name].raw
                    }) %}

                {% endif %}

                {% if column.cast and column.name not in cast_types %}

                    {% do breaches.append({
                        'assertion': 'canonical_model_cast_missing',
                        'subject': contract.model ~ '.' ~ column.name,
                        'detail': 'required the select list to cast the column to '
                            ~ column.type ~ '; found no cast of it in '
                            ~ found.node.original_file_path
                    }) %}

                {% endif %}

            {% endfor %}

            {% set required_names = contract.columns | map(attribute='name') | list %}

            {% for column_name in declared %}
                {% if column_name not in required_names %}
                    {% do breaches.append({
                        'assertion': 'canonical_contract_column_unexpected',
                        'subject': contract.model ~ '.' ~ column_name,
                        'detail': 'required the ' ~ required_names | length
                            ~ ' contract columns of this relation and no other; declared '
                            ~ (declared[column_name].raw or 'no data_type')
                    }) %}
                {% endif %}
            {% endfor %}

            {% for column_name in cast_types %}
                {% if column_name not in required_names %}
                    {% do breaches.append({
                        'assertion': 'canonical_model_cast_column_absent_from_contract',
                        'subject': contract.model ~ '.' ~ column_name,
                        'detail': 'the select list casts this column to '
                            ~ cast_types[column_name].raw
                            ~ '; the contract of this relation declares no such column'
                    }) %}
                {% endif %}
            {% endfor %}

        {% endif %}

    {% endfor %}

{% endif %}

-- The typed empty statement every breach below is unioned onto. It carries no row: the two
-- marts are named so that dbt runs this test after both are built, and no value of either is
-- read.
select
    cast(null as varchar) as assertion,
    cast(null as varchar) as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    cast(null as varchar) as detail

from {{ issued }}

where 1 = 0
{% for breach in breaches %}
union all

-- {{ breach.assertion }}: {{ breach.subject }}
select
    '{{ breach.assertion | replace("'", "''") }}' as assertion,
    '{{ breach.subject | replace("'", "''") }}' as subject,
    cast(null as varchar) as source_system_key,
    cast(null as bigint) as policy_number,
    '{{ breach.detail | replace("'", "''") }}' as detail
{% endfor %}
