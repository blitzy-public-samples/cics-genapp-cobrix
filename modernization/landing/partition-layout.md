# Landing Partition Layout — GenApp Policy-Issue Bridge

> **Status — validated against local substitute, not AWS.** The local-substitute branch applies: no AWS credentials, no
> region, no S3 bucket and no Amazon Redshift cluster or Serverless workgroup is available to this work, so every result
> the landing step has produced came from a moto S3 endpoint standing in for Amazon S3 and a DuckDB database standing in
> for Amazon Redshift. The formal AWS diff requirement is **OPEN**. Production-grade validation requires re-running the
> **same dbt models unmodified** against real S3 and real Amazon Redshift once access is granted, and
> **this has not yet happened**. Nothing in this document may be read as closing the formal AWS diff requirement.

This file is the object-key contract of the landing step. [`land_to_s3.py`](land_to_s3.py) builds the key below,
[`load_local.py`](load_local.py) rebuilds it to fetch the object it loads, and
[`load_redshift.sql`](load_redshift.sql) reads its `COPY` location from the same components. The record shape the key
carries is declared by [`landing-schema.json`](landing-schema.json). Every choice this contract records is accounted for
in [`../docs/decision-log.md`](../docs/decision-log.md), the single source of "why" for this tree; this document states
the contract and nothing else.

## The landing key

```text
s3://<bucket>/landing/source_system_key=<SOURCE_SYSTEM_KEY>/entity=<ENTITY>/extract_date=<YYYY-MM-DD>/part-0000.json
```

### Key segments

| Literal form | Current value | Permitted values and format | Where the value comes from |
| --- | --- | --- | --- |
| `<bucket>` | none committed | 3 to 63 characters of lowercase letters, digits, dot and hyphen, beginning and ending with a letter or digit, no adjacent dots, not written as an IPv4 address, none of the prefixes and suffixes the service reserves | `S3_BUCKET` or `--bucket`. There is no built-in bucket name, and no bucket literal appears in this tree |
| `landing` | `landing` | The fixed root segment. It is not configurable | The landing contract |
| `source_system_key=<KEY>` | `source_system_key=GENAPP_CLASS_EXEMPLAR` | `<KEY>` matches `[A-Za-z0-9_.-]{1,64}`, so it carries no `/`, no whitespace and no `=` — it becomes one path segment. It must equal the `source_system_key` value the record itself carries | `SOURCE_SYSTEM_KEY` or `--source-system-key`, defaulting to `GENAPP_CLASS_EXEMPLAR`; the segment written is the value the validated record carries |
| `entity=<ENTITY>` | `entity=policy_issue` | The fixed literal `policy_issue`. `--entity` is accepted only when it repeats that literal; any other value is refused | The landing contract |
| `extract_date=<YYYY-MM-DD>` | one value per run | A strict ISO calendar date, four digits, month `01`-`12` and a day the named month really has | `--extract-date`, defaulting to the current UTC date. `make` passes its `EXTRACT_DATE` variable, itself defaulting to the current UTC date |
| `part-0000.json` | `part-0000.json` | The fixed object name of the record. It is not configurable | The landing contract |

### Mechanical rules

- The key is the root segment `landing`, then one Hive-style `key=value` segment per partition field in the order
  `source_system_key`, `entity`, `extract_date`, then the object name.
- The key carries no leading slash, no trailing slash and no empty segment, so `//` never appears within it.
- The `=` of each partition segment is a literal `=`; it is not URL-encoded, and neither is any other character of the
  key.
- The landed object carries `ContentType: application/json`.
- The object body is one JSON object serialised as a single line terminated by one line feed, holding the landed keys in
  the order [`landing-schema.json`](landing-schema.json) fixes.

### Objects under one prefix

| Object | Object name | What it holds | Which loader reads it |
| --- | --- | --- | --- |
| Landed record | `part-0000.json` | The 17-key landing record | [`load_local.py`](load_local.py) downloads it and writes one raw row |
| `COPY` manifest | `part-0000.manifest.json` | One entry naming the landed record's own `s3://` URI, its mandatory flag and its byte count | [`load_redshift.sql`](load_redshift.sql) names it as the `COPY` location and sets `MANIFEST`, so exactly the one validated object is read |

Both objects sit under the same landing prefix, differ only in object name, and carry
`ContentType: application/json`. [`land_to_s3.py`](land_to_s3.py) writes the record first and the manifest second, on
the local branch and on the real branch alike.

## Worked examples

Both examples use the placeholder bucket name `example-bucket-not-real`, which names no bucket that exists. Both are
resolved for one run whose extract date is `2026-08-22`.

### Motor sample `01AMOT`

```text
s3://example-bucket-not-real/landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0000.json
s3://example-bucket-not-real/landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0000.manifest.json
```

The record this key carries populates `payment_amount` and `motor_premium_amount`. Its four commercial premium fields —
`fire_premium_amount`, `crime_premium_amount`, `flood_premium_amount` and `weather_premium_amount` — are `null`.

| Landed field | COMMAREA item and locator | Sample COMMAREA value | Landed value |
| --- | --- | --- | --- |
| `payment_amount` | `CA-PAYMENT` `PIC 9(6)`, `base/src/lgcmarea.cpy:43` | `000500` | `"500"` |
| `motor_premium_amount` | `CA-M-PREMIUM` `PIC 9(6)`, `base/src/lgcmarea.cpy:73` | `000450` | `"450"` |
| `fire_premium_amount` | `CA-B-FirePremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:85` | not carried by a motor request | `null` |
| `crime_premium_amount` | `CA-B-CrimePremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:87` | not carried by a motor request | `null` |
| `flood_premium_amount` | `CA-B-FloodPremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:89` | not carried by a motor request | `null` |
| `weather_premium_amount` | `CA-B-WeatherPremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:91` | not carried by a motor request | `null` |

### Commercial sample `01ACOM`

```text
s3://example-bucket-not-real/landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0000.json
s3://example-bucket-not-real/landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0000.manifest.json
```

The record this key carries populates `payment_amount` and all four commercial premium fields. Its
`motor_premium_amount` is `null`.

| Landed field | COMMAREA item and locator | Sample COMMAREA value | Landed value |
| --- | --- | --- | --- |
| `payment_amount` | `CA-PAYMENT` `PIC 9(6)`, `base/src/lgcmarea.cpy:43` | `001750` | `"1750"` |
| `motor_premium_amount` | `CA-M-PREMIUM` `PIC 9(6)`, `base/src/lgcmarea.cpy:73` | not carried by a commercial request | `null` |
| `fire_premium_amount` | `CA-B-FirePremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:85` | `00013500` | `"13500"` |
| `crime_premium_amount` | `CA-B-CrimePremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:87` | `00003400` | `"3400"` |
| `flood_premium_amount` | `CA-B-FloodPremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:89` | `00007800` | `"7800"` |
| `weather_premium_amount` | `CA-B-WeatherPremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:91` | `00002600` | `"2600"` |

An inapplicable product premium is `null`, never zero, on every layer that carries it — the landed object, the raw
relation and `canonical.preissued_rating`. The six amount values reach the landed object through six plain `MOVE`
statements, at `base/src/lgapdb01.cbl:265`, `445`, `489`, `491`, `493` and `495`; the three named programs carry no
`COMPUTE`, no `MULTIPLY`, no `DIVIDE` statement and no `COMP-3` item, so a landed amount is the digit string the chain
moved, with leading zeros removed and nothing else applied.

### The same key on the local endpoint

```text
s3://example-bucket-not-real/landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0000.json
```

The bucket, the key and the `s3://` URI are identical on both targets. The only difference is the endpoint the client
addresses: with `S3_ENDPOINT_URL` set, requests reach the loopback moto endpoint it names, and with `S3_ENDPOINT_URL`
unset the client resolves the real AWS endpoint itself. An endpoint override is accepted only as a local substitute —
`http` or `https`, a host that is a loopback literal or exactly `localhost`, an explicit port of 1024 or above, no user
information, no path beyond `/`, no query and no fragment. No segment of the key changes with the endpoint, and no dbt
model file changes with it either.

## The raw relation the landed object becomes

`raw.genapp_policy_issue` stores every landed field as `VARCHAR`, nullable, with each width taken from the source
PICTURE of the field it carries. Typing occurs later, in the dbt intermediate model
`int_policy_issue_decoded`, never at the raw layer. The relation is defined by
[`../warehouse/ddl/02_raw_genapp_policy_issue.sql`](../warehouse/ddl/02_raw_genapp_policy_issue.sql), and both loaders
write these 17 columns in this fixed order.

| Position | Column | Raw type | Source item and locator |
| --- | --- | --- | --- |
| 1 | `source_system_key` | `VARCHAR(64)` | Warehouse-assigned and user-mandated. It is the one landed field with no COBOL source item |
| 2 | `policy_number` | `VARCHAR(10)` | `CA-POLICY-NUM` `PIC 9(10)`, `base/src/lgcmarea.cpy:35`, recovered after the policy insert at `base/src/lgapdb01.cbl:308-311`, the insert having supplied `DEFAULT` at `base/src/lgapdb01.cbl:279` |
| 3 | `policy_type` | `VARCHAR(1)` | `DB2-POLICYTYPE` `PIC X`, `base/src/lgpolicy.cpy:43`, derived from the `CA-REQUEST-ID` routing at `base/src/lgapdb01.cbl:184-207` (`01AEND` to `E`, `01AHOU` to `H`, `01AMOT` to `M`, `01ACOM` to `C`). It is not a COMMAREA field |
| 4 | `customer_number` | `VARCHAR(10)` | `CA-CUSTOMER-NUM` `PIC 9(10)`, `base/src/lgcmarea.cpy:12` |
| 5 | `request_id` | `VARCHAR(6)` | `CA-REQUEST-ID` `PIC X(6)`, `base/src/lgcmarea.cpy:10` |
| 6 | `return_code` | `VARCHAR(2)` | `CA-RETURN-CODE` `PIC 9(2)`, `base/src/lgcmarea.cpy:11` |
| 7 | `issue_date` | `VARCHAR(10)` | `CA-ISSUE-DATE` `PIC X(10)`, `base/src/lgcmarea.cpy:38` |
| 8 | `expiry_date` | `VARCHAR(10)` | `CA-EXPIRY-DATE` `PIC X(10)`, `base/src/lgcmarea.cpy:39` |
| 9 | `last_changed` | `VARCHAR(26)` | `CA-LASTCHANGED` `PIC X(26)`, `base/src/lgcmarea.cpy:40`, read back at `base/src/lgapdb01.cbl:316-321` after the insert supplied `CURRENT TIMESTAMP` at `base/src/lgapdb01.cbl:284`, and normalised to ISO-8601 before landing |
| 10 | `broker_id` | `VARCHAR(10)` | `CA-BROKERID` `PIC 9(10)`, `base/src/lgcmarea.cpy:41` |
| 11 | `brokers_reference` | `VARCHAR(10)` | `CA-BROKERSREF` `PIC X(10)`, `base/src/lgcmarea.cpy:42` |
| 12 | `payment_amount` | `VARCHAR(6)` | `CA-PAYMENT` `PIC 9(6)`, `base/src/lgcmarea.cpy:43`, moved at `base/src/lgapdb01.cbl:265`. Carried for every policy type |
| 13 | `motor_premium_amount` | `VARCHAR(6)` | `CA-M-PREMIUM` `PIC 9(6)`, `base/src/lgcmarea.cpy:73`, moved at `base/src/lgapdb01.cbl:445`. Motor rows only |
| 14 | `fire_premium_amount` | `VARCHAR(8)` | `CA-B-FirePremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:85`, moved at `base/src/lgapdb01.cbl:489`. Commercial rows only |
| 15 | `crime_premium_amount` | `VARCHAR(8)` | `CA-B-CrimePremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:87`, moved at `base/src/lgapdb01.cbl:491`. Commercial rows only |
| 16 | `flood_premium_amount` | `VARCHAR(8)` | `CA-B-FloodPremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:89`, moved at `base/src/lgapdb01.cbl:493`. Commercial rows only |
| 17 | `weather_premium_amount` | `VARCHAR(8)` | `CA-B-WeatherPremium` `PIC 9(8)`, `base/src/lgcmarea.cpy:91`, moved at `base/src/lgapdb01.cbl:495`. Commercial rows only |

## What partitioning covers

Partitioning in this project applies to the S3 key prefix alone, and never to a warehouse object. There is no
Amazon Redshift partition, no external table, no Amazon Redshift Spectrum partition and no
`ALTER TABLE ... ADD PARTITION` statement anywhere in this tree. The partition segments exist in the object key and are
read only when the object key is built or parsed.

Amazon Redshift uses automatic table optimization. No `DISTKEY`, no `SORTKEY` and no `DISTSTYLE` is declared on any
relation of this project — not on `raw.genapp_policy_issue`, not on either canonical relation, and not on the transient
staging relation the `COPY` creates and drops inside its own transaction.

## What a landed record carries

A landed record holds `source_system_key` plus the 16 runtime business values above: 17 keys, and nothing else. The
schema requires all 17 and admits no eighteenth, so an object carrying an extra key is refused before it reaches the
bucket and again before it reaches the raw relation.

No amount is computed, inferred, scaled, rounded, padded, zero-filled, defaulted or backfilled at any point of the
landing step. The following are never landed, and none appears in the record, the raw relation or either canonical
relation: the four commercial peril-code fields `CA-B-FirePeril`, `CA-B-CrimePeril`, `CA-B-FloodPeril` and
`CA-B-WeatherPeril` at `base/src/lgcmarea.cpy:84`, `86`, `88` and `90`; any rating factor; any rating formula output;
any commission field; any source-system registry; and any provenance column beyond `source_system_key` itself. The
canonical layer holds exactly two relations, `canonical.issued_policy` and `canonical.preissued_rating`; no Quote domain
and no Loss domain is built.

## Landing and loading order

The contract fixes one object name under one prefix, so one key carries one record per source system, entity and extract
date. The operational consequences are these:

- A second landing for the same source system, entity and extract date addresses that same key and replaces the object
  it carries. The two landed objects of a two-sample run do not coexist.
- [`land_to_s3.py`](land_to_s3.py) head-requests the key before it writes and names an object already there in one
  warning line. That warning fails no landing.
- The order a run follows is: land one record, load it into `raw.genapp_policy_issue`, then land the next. `make all`
  runs `land CASE=01amot`, `load CASE=01amot`, `land CASE=01acom`, `load CASE=01acom` in that order.
- Both raw rows survive that sequence. Each load removes only a row already carrying the natural key
  `(source_system_key, policy_number)` of the object it just downloaded, then writes that object as one row; no
  statement removes a row carrying any other natural key.
- A landing whose `extract_date` differs yields a distinct key, and the objects under those two keys do coexist.

## Provisioning

Nothing in this folder creates a bucket, an Amazon Redshift cluster, a Serverless workgroup, an IAM role or any other
AWS resource. The landing tools address a bucket that must already exist and refuse the run when none is named. On the
real branch at most one bucket and one Amazon Redshift target are used, and both must already exist. On the
local-substitute branch no AWS resource exists at all.

## A new source system

Each entity carries a source-system key so rows from a future RQI slot into the same tables without structural change.
Onboarding one means a new `SOURCE_SYSTEM_KEY` value, which yields a new `source_system_key=` segment and therefore a new
S3 prefix, and source-specific extraction feeding the same 17-key landing record. There is no change to
`canonical.issued_policy`, no change to `canonical.preissued_rating`, and no third canonical relation.

## Configuration inputs

Every setting is read from the environment or from a command-line option. This document carries no credential, no
endpoint value, no account identifier and no Redshift connection value, and it names no bucket that exists;
`modernization/README.md` records the setup.

| Name | Read by |
| --- | --- |
| `S3_BUCKET` | Both loaders and the `COPY` location. There is no built-in bucket name |
| `SOURCE_SYSTEM_KEY` | The `source_system_key=` segment, checked against the record's own value |
| `S3_ENDPOINT_URL` | The loopback endpoint of the local-substitute branch. Required there, refused on the real branch |
| `AWS_REGION`, then `AWS_DEFAULT_REGION` | The region the client addresses, and the `REGION` of the `COPY` |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | The standard boto3 credential variables. The session resolves them; the landing tools never read or print their values |
| `DBT_TARGET` | The run-mode selector, `local_substitute` or `redshift`, shared by landing, raw loading and dbt |
| `LOCAL_DUCKDB_PATH`, then `DUCKDB_DATABASE` | The DuckDB database of the local-substitute branch |
| `${REDSHIFT_IAM_ROLE}` | The `IAM_ROLE` the `COPY` substitutes |
| The `REDSHIFT_*` connection settings — host, user, credential, database, schema, port and connect timeout | The real-target probe and the dbt profile |

`AWS_ANTHROPIC_API_URL`, `AWS_ANTHROPIC_API_KEY` and `AWS_ANTHROPIC_WORKSPACE_ID` are present in this environment and
are **not** AWS credentials. The presence of a variable whose name begins with `AWS_` is never evidence of AWS access,
and no tool of this bridge matches a variable on that prefix.

## Where the landing step sits

The landing step is the edge between the executed COBOL chain and the warehouse. Its place in the wider pipeline is
shown by **Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge** in
[`../docs/architecture.md`](../docs/architecture.md#figure-2), which carries that figure with its legend and is the one
authoritative copy of it.
