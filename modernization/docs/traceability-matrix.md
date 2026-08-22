# Traceability Matrix — GenApp Policy-Issue Canonical Warehouse Bridge

> **Status — validated against local substitute, not AWS.** Every result referenced by this matrix was produced on the
> local-substitute branch: a moto S3 endpoint in place of Amazon S3 and DuckDB in place of Amazon Redshift. The formal
> AWS diff requirement is **OPEN** and this has not yet happened. No mapping row below closes it, and no row may be read
> as presenting a local-substitute result as satisfying it. Production-grade validation requires re-running the same dbt
> models unmodified against real S3 and Amazon Redshift once access is granted.

This document is the bidirectional source-to-target coverage deliverable of this work. It records **what maps to what**,
in two visibly separate directions:

- **[Part A](#part-a--forward-direction-field-entries-declarations-and-intermediates)** and
  **[Part B](#part-b--forward-direction-non-field-source-constructs)** carry the **forward** direction: every in-scope
  source construct → its target implementation, or an explicit reasoned outcome of **declaration-only** or **excluded**
  where the construct legitimately has no target. A source item with no target is a mapping outcome with its own row,
  never an omission.
- **[Part C](#part-c--reverse-direction-every-created-artifact)** and
  **[Part D](#part-d--reverse-direction-every-canonical-column)** carry the **reverse** direction: every created
  artifact and every canonical column instance → the source requirement, source construct, user rule or explicit
  warehouse assignment that justifies it.
- **[Part E](#part-e--coverage-assertion-and-gap-statement)** states coverage and the zero-gap position, and names the
  counts a reviewer recomputes to check it.

This file states mapping **facts**. Every justification is a pointer to a named row of
[`decision-log.md`](decision-log.md) and is not restated or re-argued here. This file draws **no diagram** and describes
no topology; [`architecture.md`](architecture.md) is the single rendering authority for all five figures and they are
cited here by name only.

## Coverage summary

| Measure | Count | What it counts |
|---|---:|---|
| Logical field entries | **17** | 6 premium and payment entries plus 11 policy and request names |
| Distinct runtime business values | **16** | 15 active entries plus 1 derived entry; `DB2-POLICYNUMBER` is declaration-only and adds no runtime value |
| Source-derived canonical column instances | **18** | 10 on `canonical.issued_policy` plus 8 on `canonical.preissued_rating` |
| Warehouse-assigned column instances | **2** | `source_system_key`, once on each relation |
| Total canonical column instances | **20** | 11 columns of `canonical.issued_policy` plus 9 of `canonical.preissued_rating` |
| Canonical relations | **2** | `canonical.issued_policy` and `canonical.preissued_rating`, and no third relation |
| Created artifacts | **61** | authored files beneath `modernization/`; generated paths are excluded and named in [§C.9](#c9-generated-paths-excluded-from-the-authored-count) |
| Referenced read-only source files | **5** | `lgapol01.cbl` 169 lines · `lgapdb01.cbl` 595 · `lgapvs01.cbl` 188 · `lgcmarea.cpy` 103 · `lgpolicy.cpy` 107 |
| Pre-existing files modified | **0** | there is no UPDATE row in this project; the five sources are REFERENCE only |
| Unmapped items | **0** | in either direction — see [Part E](#part-e--coverage-assertion-and-gap-statement) |

The 18 source-derived instances exceed the 16 runtime values by 2 because `policy_number` and `policy_type` each stand
on **both** relations. Rationale for this accounting: [`decision-log.md`](decision-log.md), row **D-02**.

## Authority order

| Authority | Role |
|---|---|
| [`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml) | **Machine-readable authority.** Every offset, PICTURE, runtime status, target column and transformation stated here is the value that file records, and its `counts` block is the arithmetic this matrix asserts |
| [`field-level-lineage.md`](field-level-lineage.md) | **Column-level narrative.** Part D of this matrix is its construct-oriented counterpart and must agree with it column for column |
| [`../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml`](../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml) | The enforced canonical contract: the single declaration of both column sets, their types and their nullability |
| [`../harness/statement_map.yml`](../harness/statement_map.yml) | The SQL-block accounting and the execution-order constraints this matrix cites |
| [`../harness/translation-rules.md`](../harness/translation-rules.md) | The rewrite-rule inventory that is the target side of every non-field construct row of Part B |
| [`../landing/landing-schema.json`](../landing/landing-schema.json) | The landed-record contract: 17 required keys, no additional key |
| [`../extraction/extraction-spec.md`](../extraction/extraction-spec.md) | The entry-oriented specification, including the enumeration of in-scope declarations that receive no column |
| [`../validation/validation-evidence.md`](../validation/validation-evidence.md) | The recorded run results referenced by the exercise-status column of [§B.8](#b8-return-code-and-abend-contract) |
| [`decision-log.md`](decision-log.md) | The single source of rationale, alternatives and risk for every outcome recorded here |

**This matrix must agree with the field map and with the enforced dbt contract exactly.** A disagreement between them
and this document is a defect to fix, not a difference to document.

## Conventions

- Every locator is written `path:line` or `path:first-last` and resolves to one of the five read-only sources. No
  locator here points outside those five files, and no claim about the existing system rests on anything else.
- A cell reading `—` means the item does not exist, never that a locator was unavailable.
- Byte ranges are 1-based positions in the 32,500-byte `DFHCOMMAREA`, established by the declaration widths of
  `base/src/lgcmarea.cpy`.
- **Runtime status** uses the field map's vocabulary: *active* (a statement of the chain reads or writes it),
  *derived* (produced from another value; no COMMAREA item carries it), *declaration-only* (no statement of the chain
  references the declaration), *warehouse-assigned* (no COBOL item supplies it).
- A **target treatment** of `lineage entry, no column` or `excluded` is a mapping outcome, not a gap.

---

# Part A — FORWARD direction: field entries, declarations and intermediates

## A.1 The 17 logical field entries

Six amount concepts and eleven policy and request names. Fifteen entries are active, one is derived and one is
declaration-only, which is what makes 17 entries resolve to 16 runtime business values.

### A.1.1 The six premium and payment entries — three tiers each

Each amount is declared three times and the three declarations are not interchangeable: the COMMAREA carrier is the
active runtime item, the `base/src/lgpolicy.cpy` counterpart is **declaration-only**, and the binary
`PIC S9(9) COMP` item in `base/src/lgapdb01.cbl` is the host variable the INSERT actually binds. **Verified:** the six
Db2-side DISPLAY declarations have **zero exact-name references** in `base/src/lgapdb01.cbl`.

| # | Source item / concept | Declaring file `path:line` | PIC | Runtime status | Target treatment | Notes |
|---:|---|---|---|---|---|---|
| 1 | payment — Tier 1 carrier `CA-PAYMENT` | `base/src/lgcmarea.cpy:43` | `9(6)` | active — request-supplied | `canonical.preissued_rating.payment_amount` `DECIMAL(8,2)` | Bytes 95-100; landing key `payment_amount`; passthrough, no formula |
| 2 | payment — Tier 2 counterpart `DB2-PAYMENT` | `base/src/lgpolicy.cpy:51` | `9(6)` | declaration-only | lineage entry, no column | Zero exact-name references in `base/src/lgapdb01.cbl` |
| 3 | payment — Tier 3 intermediate `DB2-PAYMENT-INT` | `base/src/lgapdb01.cbl:92` | `S9(9) COMP` | active | carries the value into the POLICY insert | Set `base/src/lgapdb01.cbl:265`; bound `:287` |
| 4 | motor premium — Tier 1 carrier `CA-M-PREMIUM` | `base/src/lgcmarea.cpy:73` | `9(6)` | active — request-supplied | `canonical.preissued_rating.motor_premium_amount` `DECIMAL(8,2)` | Bytes 166-171; populated for policy type `M` only, NULL otherwise |
| 5 | motor premium — Tier 2 counterpart `DB2-M-PREMIUM` | `base/src/lgpolicy.cpy:80` | `9(6)` | declaration-only | lineage entry, no column | Zero exact-name references in `base/src/lgapdb01.cbl` |
| 6 | motor premium — Tier 3 intermediate `DB2-M-PREMIUM-int` | `base/src/lgapdb01.cbl:100` | `S9(9) COMP` | active | carries the value into the MOTOR insert | Set `base/src/lgapdb01.cbl:445`; bound `:469` |
| 7 | fire premium — Tier 1 carrier `CA-B-FirePremium` | `base/src/lgcmarea.cpy:85` | `9(8)` | active — request-supplied | `canonical.preissued_rating.fire_premium_amount` `DECIMAL(10,2)` | Bytes 900-907; policy type `C` only |
| 8 | fire premium — Tier 2 counterpart `DB2-B-FirePremium` | `base/src/lgpolicy.cpy:91` | `9(8)` | declaration-only | lineage entry, no column | Zero exact-name references in `base/src/lgapdb01.cbl` |
| 9 | fire premium — Tier 3 intermediate `DB2-B-FirePremium-Int` | `base/src/lgapdb01.cbl:103` | `S9(9) COMP` | active | carries the value into the COMMERCIAL insert | Set `base/src/lgapdb01.cbl:489`; bound `:535` |
| 10 | crime premium — Tier 1 carrier `CA-B-CrimePremium` | `base/src/lgcmarea.cpy:87` | `9(8)` | active — request-supplied | `canonical.preissued_rating.crime_premium_amount` `DECIMAL(10,2)` | Bytes 912-919; policy type `C` only |
| 11 | crime premium — Tier 2 counterpart `DB2-B-CrimePremium` | `base/src/lgpolicy.cpy:93` | `9(8)` | declaration-only | lineage entry, no column | Zero exact-name references in `base/src/lgapdb01.cbl` |
| 12 | crime premium — Tier 3 intermediate `DB2-B-CrimePremium-Int` | `base/src/lgapdb01.cbl:105` | `S9(9) COMP` | active | carries the value into the COMMERCIAL insert | Set `base/src/lgapdb01.cbl:491`; bound `:537` |
| 13 | flood premium — Tier 1 carrier `CA-B-FloodPremium` | `base/src/lgcmarea.cpy:89` | `9(8)` | active — request-supplied | `canonical.preissued_rating.flood_premium_amount` `DECIMAL(10,2)` | Bytes 924-931; policy type `C` only |
| 14 | flood premium — Tier 2 counterpart `DB2-B-FloodPremium` | `base/src/lgpolicy.cpy:95` | `9(8)` | declaration-only | lineage entry, no column | Zero exact-name references in `base/src/lgapdb01.cbl` |
| 15 | flood premium — Tier 3 intermediate `DB2-B-FloodPremium-Int` | `base/src/lgapdb01.cbl:107` | `S9(9) COMP` | active | carries the value into the COMMERCIAL insert | Set `base/src/lgapdb01.cbl:493`; bound `:539` |
| 16 | weather premium — Tier 1 carrier `CA-B-WeatherPremium` | `base/src/lgcmarea.cpy:91` | `9(8)` | active — request-supplied | `canonical.preissued_rating.weather_premium_amount` `DECIMAL(10,2)` | Bytes 936-943; policy type `C` only |
| 17 | weather premium — Tier 2 counterpart `DB2-B-WeatherPremium` | `base/src/lgpolicy.cpy:97` | `9(8)` | declaration-only | lineage entry, no column | Zero exact-name references in `base/src/lgapdb01.cbl` |
| 18 | weather premium — Tier 3 intermediate `DB2-B-WeatherPremium-Int` | `base/src/lgapdb01.cbl:109` | `S9(9) COMP` | active | carries the value into the COMMERCIAL insert | Set `base/src/lgapdb01.cbl:495`; bound `:541` |

Six logical entries, eighteen declarations, six canonical columns. The amounts are moved by plain `MOVE` with no
arithmetic anywhere in the corpus — see [§B.9](#b9-arithmetic-inventory-and-the-no-formula-finding). Amount typing at
scale 2: [`decision-log.md`](decision-log.md), row **D-55**; the ±0.01 comparison contract: row **D-04**; the
product-specific NULL pattern: row **D-54**.

### A.1.2 The eleven policy and request entries

| # | Source item / concept | Declaring file `path:line` | PIC | Runtime status | Target treatment | Notes |
|---:|---|---|---|---|---|---|
| 1 | policy number — `CA-POLICY-NUM` | `base/src/lgcmarea.cpy:35` | `9(10)` | active — chain-assigned | `issued_policy.policy_number` **and** `preissued_rating.policy_number` `BIGINT` | Assigned post-insert from `DB2-POLICYNUM-INT` `base/src/lgapdb01.cbl:307-311`; one of the two duplicated instances |
| 2 | Db2-side policy number — `DB2-POLICYNUMBER` | `base/src/lgpolicy.cpy:44` | `9(10)` | **declaration-only** | **lineage entry, no column** | Zero references anywhere in `base/src/lgapdb01.cbl`; the POLICY insert supplies the literal `DEFAULT` `base/src/lgapdb01.cbl:279`. This single item is what makes 17 entries resolve to 16 runtime values. Rationale: **D-02** |
| 3 | policy type — `DB2-POLICYTYPE` | `base/src/lgpolicy.cpy:43` | `X` | **derived** | `issued_policy.policy_type` **and** `preissued_rating.policy_type` `CHAR(1)` | 5 references: set at `base/src/lgapdb01.cbl:188,192,196,200` and bound at `:283`. Not a COMMAREA field; derived from `CA-REQUEST-ID`. Rationale: **D-50** |
| 4 | customer number — `CA-CUSTOMER-NUM` | `base/src/lgcmarea.cpy:12` | `9(10)` | active — request-supplied | `issued_policy.customer_number` `BIGINT` | Bytes 9-18; intermediate `DB2-CUSTOMERNUM-INT` `base/src/lgapdb01.cbl:90` |
| 5 | request id — `CA-REQUEST-ID` | `base/src/lgcmarea.cpy:10` | `X(6)` | active — request-supplied | `issued_policy.request_id` `VARCHAR(6)` | Bytes 1-6; also drives the policy-type derivation and the routing table |
| 6 | return code — `CA-RETURN-CODE` | `base/src/lgcmarea.cpy:11` | `9(2)` | active — chain-assigned | `issued_policy.return_code` `CHAR(2)` | Bytes 7-8; carried as a two-character string, never converted to an integer |
| 7 | issue date — `CA-ISSUE-DATE` | `base/src/lgcmarea.cpy:38` | `X(10)` | active — request-supplied | `issued_policy.issue_date` `DATE` | Bytes 29-38; bound into the POLICY insert `base/src/lgapdb01.cbl:281` |
| 8 | expiry date — `CA-EXPIRY-DATE` | `base/src/lgcmarea.cpy:39` | `X(10)` | active — request-supplied | `issued_policy.expiry_date` `DATE` | Bytes 39-48; bound `base/src/lgapdb01.cbl:282` |
| 9 | last changed — `CA-LASTCHANGED` | `base/src/lgcmarea.cpy:40` | `X(26)` | active — chain-assigned | `issued_policy.last_changed` `TIMESTAMP` | Bytes 49-74; read back `base/src/lgapdb01.cbl:315-321`; normalised to ISO-8601 before landing. Rationale: **D-53** |
| 10 | broker id — `CA-BROKERID` | `base/src/lgcmarea.cpy:41` | `9(10)` | active — request-supplied | `issued_policy.broker_id` `BIGINT` | Bytes 75-84; intermediate `DB2-BROKERID-INT` `base/src/lgapdb01.cbl:91` |
| 11 | brokers reference — `CA-BROKERSREF` | `base/src/lgcmarea.cpy:42` | `X(10)` | active — request-supplied | `issued_policy.brokers_reference` `VARCHAR(10)` | Bytes 85-94; trailing spaces trimmed; bound `base/src/lgapdb01.cbl:286` |

Eleven entries, ten runtime values, twelve source-derived column instances — the ten `issued_policy` columns plus the
policy number and policy type repeated on `canonical.preissued_rating`.

## A.2 Declaration register — `base/src/lgcmarea.cpy`

The per-declaration view of the same ground as [§A.1](#a1-the-17-logical-field-entries), keyed by declaration rather
than by logical entry. Every in-scope COMMAREA declaration appears **exactly once** below, with its locator, its byte
range and its target treatment.

| # | COMMAREA declaration | Locator | PIC | Bytes | Runtime status | Target treatment |
|---:|---|---|---|---|---|---|
| 1 | `CA-REQUEST-ID` | `base/src/lgcmarea.cpy:10` | `X(6)` | 1-6 | active — request-supplied | `issued_policy.request_id`; also the input of the policy-type derivation |
| 2 | `CA-RETURN-CODE` | `base/src/lgcmarea.cpy:11` | `9(2)` | 7-8 | active — chain-assigned | `issued_policy.return_code` |
| 3 | `CA-CUSTOMER-NUM` | `base/src/lgcmarea.cpy:12` | `9(10)` | 9-18 | active — request-supplied | `issued_policy.customer_number` |
| 4 | `CA-POLICY-NUM` | `base/src/lgcmarea.cpy:35` | `9(10)` | 19-28 | active — chain-assigned | `issued_policy.policy_number` and `preissued_rating.policy_number` |
| 5 | `CA-ISSUE-DATE` | `base/src/lgcmarea.cpy:38` | `X(10)` | 29-38 | active — request-supplied | `issued_policy.issue_date` |
| 6 | `CA-EXPIRY-DATE` | `base/src/lgcmarea.cpy:39` | `X(10)` | 39-48 | active — request-supplied | `issued_policy.expiry_date` |
| 7 | `CA-LASTCHANGED` | `base/src/lgcmarea.cpy:40` | `X(26)` | 49-74 | active — chain-assigned | `issued_policy.last_changed`; also the commercial `RequestDate` operand — see [§B.11](#b11-the-measured-ordering-constraint) |
| 8 | `CA-BROKERID` | `base/src/lgcmarea.cpy:41` | `9(10)` | 75-84 | active — request-supplied | `issued_policy.broker_id` |
| 9 | `CA-BROKERSREF` | `base/src/lgcmarea.cpy:42` | `X(10)` | 85-94 | active — request-supplied | `issued_policy.brokers_reference` |
| 10 | `CA-PAYMENT` | `base/src/lgcmarea.cpy:43` | `9(6)` | 95-100 | active — request-supplied | `preissued_rating.payment_amount` |
| 11 | `CA-M-PREMIUM` | `base/src/lgcmarea.cpy:73` | `9(6)` | 166-171 | active — request-supplied | `preissued_rating.motor_premium_amount` |
| 12 | `CA-B-FirePremium` | `base/src/lgcmarea.cpy:85` | `9(8)` | 900-907 | active — request-supplied | `preissued_rating.fire_premium_amount` |
| 13 | `CA-B-CrimePremium` | `base/src/lgcmarea.cpy:87` | `9(8)` | 912-919 | active — request-supplied | `preissued_rating.crime_premium_amount` |
| 14 | `CA-B-FloodPremium` | `base/src/lgcmarea.cpy:89` | `9(8)` | 924-931 | active — request-supplied | `preissued_rating.flood_premium_amount` |
| 15 | `CA-B-WeatherPremium` | `base/src/lgcmarea.cpy:91` | `9(8)` | 936-943 | active — request-supplied | `preissued_rating.weather_premium_amount` |

Fifteen in-scope COMMAREA declarations; every one carries a target. The remaining declarations of the copybook receive
no column and are registered in [§A.6](#a6-excluded-and-no-target-declarations).

## A.3 Declaration register — `base/src/lgpolicy.cpy` Db2-side counterparts

Thirteen in-scope counterparts, each appearing **exactly once**. The reference count in the fourth column is the
measured number of exact-name references in `base/src/lgapdb01.cbl`.

| # | Db2-side declaration | Locator | PIC | Exact-name refs in `lgapdb01.cbl` | Runtime status | Target treatment |
|---:|---|---|---|---:|---|---|
| 1 | `DB2-POLICYTYPE` | `base/src/lgpolicy.cpy:43` | `X` | 5 (`:188,192,196,200,283`) | active — derived by the routing `EVALUATE` | `issued_policy.policy_type` and `preissued_rating.policy_type` |
| 2 | `DB2-POLICYNUMBER` | `base/src/lgpolicy.cpy:44` | `9(10)` | 0 | **declaration-only** | **lineage entry, no column** |
| 3 | `DB2-ISSUEDATE` | `base/src/lgpolicy.cpy:46` | `X(10)` | 0 | declaration-only | companion declaration of a projected concept; the column derives from `CA-ISSUE-DATE`, which the insert binds directly at `base/src/lgapdb01.cbl:281` |
| 4 | `DB2-EXPIRYDATE` | `base/src/lgpolicy.cpy:47` | `X(10)` | 0 | declaration-only | companion declaration; the column derives from `CA-EXPIRY-DATE`, bound at `base/src/lgapdb01.cbl:282` |
| 5 | `DB2-LASTCHANGED` | `base/src/lgpolicy.cpy:48` | `X(26)` | 0 | declaration-only | companion declaration; the column derives from `CA-LASTCHANGED`, the `INTO` target of the read-back at `base/src/lgapdb01.cbl:316-321` |
| 6 | `DB2-BROKERID` | `base/src/lgpolicy.cpy:49` | `9(10)` | 0 | declaration-only | companion declaration; the insert binds the binary intermediate `DB2-BROKERID-INT` at `base/src/lgapdb01.cbl:285` |
| 7 | `DB2-BROKERSREF` | `base/src/lgpolicy.cpy:50` | `X(10)` | 0 | declaration-only | companion declaration; the column derives from `CA-BROKERSREF`, bound at `base/src/lgapdb01.cbl:286` |
| 8 | `DB2-PAYMENT` | `base/src/lgpolicy.cpy:51` | `9(6)` | 0 | **declaration-only** | **lineage entry, no column** |
| 9 | `DB2-M-PREMIUM` | `base/src/lgpolicy.cpy:80` | `9(6)` | 0 | **declaration-only** | **lineage entry, no column** |
| 10 | `DB2-B-FirePremium` | `base/src/lgpolicy.cpy:91` | `9(8)` | 0 | **declaration-only** | **lineage entry, no column** |
| 11 | `DB2-B-CrimePremium` | `base/src/lgpolicy.cpy:93` | `9(8)` | 0 | **declaration-only** | **lineage entry, no column** |
| 12 | `DB2-B-FloodPremium` | `base/src/lgpolicy.cpy:95` | `9(8)` | 0 | **declaration-only** | **lineage entry, no column** |
| 13 | `DB2-B-WeatherPremium` | `base/src/lgpolicy.cpy:97` | `9(8)` | 0 | **declaration-only** | **lineage entry, no column** |

Rows 8-13 are the six Db2-side amount declarations, and row 2 is `DB2-POLICYNUMBER`: seven declaration-only entries
whose target treatment is a lineage entry rather than a column. Rows 3-7 are companion declarations of concepts that
**are** projected, from their COMMAREA carriers.

## A.4 Program intermediates and length work items

Every in-scope working-storage item the chain uses to move an in-scope value or to compute a required length. Each
appears **exactly once**.

| # | Program intermediate | Locator | PIC | Runtime status | Target treatment |
|---:|---|---|---|---|---|
| 1 | `DB2-CUSTOMERNUM-INT` | `base/src/lgapdb01.cbl:90` | `S9(9) COMP` | active | carries `CA-CUSTOMER-NUM` into the POLICY insert; set `:176`, bound `:280` |
| 2 | `DB2-BROKERID-INT` | `base/src/lgapdb01.cbl:91` | `S9(9) COMP` | active | carries `CA-BROKERID` into the POLICY insert; set `:264`, bound `:285` |
| 3 | `DB2-PAYMENT-INT` | `base/src/lgapdb01.cbl:92` | `S9(9) COMP` | active | carries `CA-PAYMENT`; set `:265`, bound `:287` |
| 4 | `DB2-M-PREMIUM-int` | `base/src/lgapdb01.cbl:100` | `S9(9) COMP` | active | carries `CA-M-PREMIUM`; set `:445`, bound `:469` |
| 5 | `DB2-B-FirePremium-Int` | `base/src/lgapdb01.cbl:103` | `S9(9) COMP` | active | carries `CA-B-FirePremium`; set `:489`, bound `:535` |
| 6 | `DB2-B-CrimePremium-Int` | `base/src/lgapdb01.cbl:105` | `S9(9) COMP` | active | carries `CA-B-CrimePremium`; set `:491`, bound `:537` |
| 7 | `DB2-B-FloodPremium-Int` | `base/src/lgapdb01.cbl:107` | `S9(9) COMP` | active | carries `CA-B-FloodPremium`; set `:493`, bound `:539` |
| 8 | `DB2-B-WeatherPremium-Int` | `base/src/lgapdb01.cbl:109` | `S9(9) COMP` | active | carries `CA-B-WeatherPremium`; set `:495`, bound `:541` |
| 9 | `DB2-POLICYNUM-INT` | `base/src/lgapdb01.cbl:117` | `S9(9) COMP VALUE +0` | active — chain-assigned | receives the recovered identity `:308-310` and is moved into `CA-POLICY-NUM` `:311`; also the `WHERE` host of the read-back `:320` and the `POLICYNUMBER` operand of every product insert |
| 10 | `WS-CA-HEADER-LEN` (Db2 program) | `base/src/lgapdb01.cbl:65` | `S9(4) COMP VALUE +28` | active | length arithmetic only; no canonical column. Reproduced by the harness header validation |
| 11 | `WS-REQUIRED-CA-LEN` (Db2 program) | `base/src/lgapdb01.cbl:66` | `S9(4) VALUE +0` | active | accumulator compared with `EIBCALEN` at `:210`; no canonical column. Never re-initialised — see **D-24** |
| 12 | `WS-VARY-LEN` | `base/src/lgapdb01.cbl:71` | `S9(4) COMP` | active on the endowment route only | receives `EIBCALEN` less the required length `:339-340`; no canonical column. The endowment route is compiled and not executed — **D-18** |
| 13 | `WS-VARY-CHAR` | `base/src/lgapdb01.cbl:72` | `X(3900)` | active on the endowment route only | reference-modified target of the padding move `:344-345`; the enclosing group `WS-VARY-FIELD` `:70` is the operand the endowment insert binds `:365`; no canonical column |
| 14 | `WS-CA-HEADER-LEN` (entry program) | `base/src/lgapol01.cbl:59` | `S9(4) COMP VALUE +28` | active | the 28-byte header requirement added at `:109`; no canonical column |
| 15 | `WS-REQUIRED-CA-LEN` (entry program) | `base/src/lgapol01.cbl:60` | `S9(4) VALUE +0` | active | accumulator compared with `EIBCALEN` at `:113`; no canonical column |

Preservation of the halfword receivers exactly as declared, with no widening in the generated copies:
[`decision-log.md`](decision-log.md), row **D-22**.

## A.5 Length constants used by the chain

| # | Constant | Locator | Value | Applied at | Target treatment |
|---:|---|---|---:|---|---|
| 1 | `WS-MOTOR-LEN` | `base/src/lgpolicy.cpy:21` | +65 | — (never applied by the chain) | **unchanged, stale — 12-byte shortfall recorded**; rationale **D-08** |
| 2 | `WS-COMM-LEN` | `base/src/lgpolicy.cpy:22` | +1102 | — (never applied by the chain) | unchanged; equals the measured commercial overlay length, so no shortfall |
| 3 | `WS-FULL-ENDOW-LEN` | `base/src/lgpolicy.cpy:24` | +124 | `base/src/lgapdb01.cbl:187` | unchanged; drives the endowment length check and the subtraction of **D-18** |
| 4 | `WS-FULL-HOUSE-LEN` | `base/src/lgpolicy.cpy:25` | +130 | `base/src/lgapdb01.cbl:191` | unchanged; house route compiled, and not exercised by the two executed samples |
| 5 | `WS-FULL-MOTOR-LEN` | `base/src/lgpolicy.cpy:26` | +137 | `base/src/lgapdb01.cbl:195` | unchanged; the motor route validates 28 + 137 = 165 bytes |
| 6 | `WS-FULL-COMM-LEN` | `base/src/lgpolicy.cpy:27` | +1174 | `base/src/lgapdb01.cbl:199` | unchanged; the commercial route validates 28 + 1174 = 1202 bytes |

The stale-constant measurement, reproduced from the source and mapped to a handling rather than to a column:

| Measurement | Value | Evidence |
|---|---:|---|
| Header requirement added by both programs | 28 | `base/src/lgapol01.cbl:59,109`; `base/src/lgapdb01.cbl:65,182` |
| Declared full motor requirement | 137 | `base/src/lgpolicy.cpy:26`, added `base/src/lgapdb01.cbl:195` |
| Length the motor route therefore validates | 165 | 28 + 137 |
| Measured end byte of the motor overlay | 177 | `base/src/lgcmarea.cpy:65-75` |
| Shortfall | **12** | `CA-M-PREMIUM` 6 bytes plus `CA-M-ACCIDENTS` 6 bytes |

Target treatment of the shortfall: the sample builder always emits the full 32,500-character record and extraction
validates that the applicable amount bytes are numeric before landing. No source constant is changed. Rationale:
[`decision-log.md`](decision-log.md), row **D-08**.

## A.6 Excluded and no-target declarations

Every item below is in scope, carries a locator and receives **no canonical column**. Its absence from Parts A.1-A.2
is deliberate and recorded here rather than left implicit.

### A.6.1 The four commercial peril codes — excluded

`PIC 9(4)` **codes**, not amounts. The requested amount fields are the adjacent `PIC 9(8)` premium items at
`base/src/lgcmarea.cpy:85,87,89,91`. Rationale: [`decision-log.md`](decision-log.md), row **D-12**.

| # | Excluded item | Locator | PIC | Bytes | Program intermediate | Move | Bound at | Target treatment |
|---:|---|---|---|---|---|---|---|---|
| 1 | `CA-B-FirePeril` | `base/src/lgcmarea.cpy:84` | `9(4)` | 896-899 | `DB2-B-FirePeril-Int` `S9(4) COMP` `base/src/lgapdb01.cbl:102` | `:488` | `:534` | excluded — accepted by the commercial stub so the chain executes; no canonical column |
| 2 | `CA-B-CrimePeril` | `base/src/lgcmarea.cpy:86` | `9(4)` | 908-911 | `DB2-B-CrimePeril-Int` `S9(4) COMP` `base/src/lgapdb01.cbl:104` | `:490` | `:536` | excluded — as above |
| 3 | `CA-B-FloodPeril` | `base/src/lgcmarea.cpy:88` | `9(4)` | 920-923 | `DB2-B-FloodPeril-Int` `S9(4) COMP` `base/src/lgapdb01.cbl:106` | `:492` | `:538` | excluded — as above |
| 4 | `CA-B-WeatherPeril` | `base/src/lgcmarea.cpy:90` | `9(4)` | 932-935 | `DB2-B-WeatherPeril-Int` `S9(4) COMP` `base/src/lgapdb01.cbl:108` | `:494` | `:540` | excluded — as above |

Their four Db2-side counterparts `DB2-B-FirePeril`, `DB2-B-CrimePeril`, `DB2-B-FloodPeril` and `DB2-B-WeatherPeril`
[`base/src/lgpolicy.cpy:90,92,94,96`] carry the same treatment: excluded, no canonical column. Extraction never reads a
peril window.

### A.6.2 Non-requested product-overlay fields — accepted by the stubs, mapped to nothing

| # | Group | Locators | Target treatment |
|---:|---|---|---|
| 1 | Commercial status and rejection reason — `CA-B-Status`, `CA-B-RejectReason` | `base/src/lgcmarea.cpy:92,93`; Db2-side `base/src/lgpolicy.cpy:98,99`; intermediate `DB2-B-Status-Int` `base/src/lgapdb01.cbl:110`, moved `:496`, bound `:542` and `:543` | present but unmapped: neither is an amount; no canonical column |
| 2 | Motor numerics other than the premium — `CA-M-VALUE`, `CA-M-CC`, `CA-M-ACCIDENTS` | `base/src/lgcmarea.cpy:68,71,74`; intermediates `base/src/lgapdb01.cbl:98,99,101`, moved `:443,444,446`, bound `:464,467,470` | active at run time, no canonical column: populated in the samples only so the motor route executes |
| 3 | Character items of the two exercised overlays — motor make, model, registration, colour and manufacture date; commercial address, postcode, latitude, longitude, customer and property type | `base/src/lgcmarea.cpy:66,67,69,70,72` and `:78-83`; passed straight to their inserts at `base/src/lgapdb01.cbl:462-468` and `:528-533` | accepted by the motor and commercial stubs so the named chain executes; no canonical column; extraction never reads them |
| 4 | Redefined group declarations — `CA-REQUEST-SPECIFIC`, `CA-POLICY-REQUEST`, `CA-POLICY-COMMON`, `CA-POLICY-SPECIFIC`, `CA-MOTOR`, `CA-COMMERCIAL` | `base/src/lgcmarea.cpy:13,34,37,44,65,77` | storage and addressing constructs; the byte grid of `copybook_field_map.yml` carries their offsets; no canonical column |
| 5 | Fill and padding items — `CA-M-FILLER`, `CA-B-FILLER`, and the padding of an unselected overlay | `base/src/lgcmarea.cpy:75,94` | carry storage rather than a business value; no canonical column |
| 6 | Overlays the named chain does not exercise — `CA-CUSTOMER-REQUEST`, `CA-CUSTSECR-REQUEST`, `CA-ENDOWMENT`, `CA-HOUSE`, `CA-CLAIM` | `base/src/lgcmarea.cpy:15,28,46,56,96` | out of scope for this chain; recorded in the `out_of_scope_overlays` block of the field map and expanded nowhere; no canonical column |
| 7 | Db2-side structures of other entities — `DB2-CUSTOMER`, `DB2-ENDOWMENT`, `DB2-HOUSE`, `DB2-CLAIM`, and the non-amount members of `DB2-MOTOR` and `DB2-COMMERCIAL` | `base/src/lgpolicy.cpy:31,53,64,101` and the members under `:72-99` | out of scope: no entry of this work projects them; no canonical column |
| 8 | Diagnostic and run-time work areas — `WS-HEADER`, `ERROR-MSG`, `CA-ERROR-MSG`, `ABS-TIME`, `TIME1`, `DATE1`, `WS-RESP`, `WS-RESP2`, `WF-*` payload items | `base/src/lgapol01.cbl:25-50`; `base/src/lgapdb01.cbl:25-57`; `base/src/lgapvs01.cbl:18-81` | reproduced by the harness so the error and write paths execute; no canonical column. The `WF-*` items are treated in [§B.7](#b7-vsam-projection) |


---

# Part B — FORWARD direction: non-field source constructs

Every construct of the three programs that is not a field declaration. The target side is the rewrite inventory of
[`../harness/translation-rules.md`](../harness/translation-rules.md) and the SQL accounting of
[`../harness/statement_map.yml`](../harness/statement_map.yml); the counts below are those artifacts' counts and this
matrix asserts the same figures. Every rewrite applies **only** to generated copies under
`modernization/harness/build/**`; no source file is preprocessed in place. Rationale:
[`decision-log.md`](decision-log.md), row **D-06**.

## B.1 Interface contract and header validation

| # | Source construct | Locator | Target implementation |
|---:|---|---|---|
| 1 | The 32,500-byte `DFHCOMMAREA` — header items plus the redefining request views | `base/src/lgcmarea.cpy:10-13` | The byte grid of [`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml) `layout` block, the full-length record emitted by `build_sample_commarea.py`, and the landed JSON record of 17 keys declared by [`../landing/landing-schema.json`](../landing/landing-schema.json) |
| 2 | `01 DFHCOMMAREA.` with a level-03 copybook nested beneath it | `base/src/lgapol01.cbl:70-71`; `base/src/lgapdb01.cbl:134-137`; `base/src/lgapvs01.cbl:86-87` | Preserved in the generated copies: `lgcmarea.cpy` begins at level 03 and supplies no level-01, so the `COPY` stays nested inside the enclosing group (rewrite rule R2 for the Db2 program; the two plain `Copy` statements are carried through unchanged) |
| 3 | The 28-byte header requirement — `WS-CA-HEADER-LEN` added, then `EIBCALEN` compared | `base/src/lgapol01.cbl:59,109,113-116`; `base/src/lgapdb01.cbl:65,182,210-213` | Reproduced unchanged in the generated copies and exercised by the harness driver; the outcome is asserted per case and recorded in [`../validation/validation-evidence.md`](../validation/validation-evidence.md) |
| 4 | Product-specific length requirement added by the routing `EVALUATE` | `base/src/lgapdb01.cbl:184-207` | Preserved; the per-route required length is the length arithmetic registered in [§A.5](#a5-length-constants-used-by-the-chain) |

## B.2 Call order and link lengths

| # | Source construct | Locator | Target implementation |
|---:|---|---|---|
| 1 | `EXEC CICS Link Program(LGAPDB01) Commarea(DFHCOMMAREA) LENGTH(32500)` | `base/src/lgapol01.cbl:121-124` | `MOVE 32500 TO EIBCALEN` followed by a dynamic `CALL LGAPDB01 USING DFHCOMMAREA` (rewrite rule R5) |
| 2 | `EXEC CICS Link Program(LGAPVS01) Commarea(DFHCOMMAREA) LENGTH(32500)` | `base/src/lgapdb01.cbl:243-246` | `MOVE 32500 TO EIBCALEN` followed by a dynamic `CALL LGAPVS01 USING DFHCOMMAREA` (rewrite rule R5) |
| 3 | Both `LINK` targets are **data items, not literals** — `01 LGAPDB01 PIC X(8) VALUE 'LGAPDB01'` and `01 LGAPVS01 PIC X(8) VALUE 'LGAPVS01'` | `base/src/lgapol01.cbl:51`; `base/src/lgapdb01.cbl:119` | Carried through unchanged, so each generated `CALL` names an identifier and resolves the program name from that item at run time |
| 4 | Call order `LGAPOL01` → `LGAPDB01` → `LGAPVS01`, with the product inserts between the two links | `base/src/lgapol01.cbl:121-124`; `base/src/lgapdb01.cbl:219-246` | Preserved exactly; both link lengths stay 32500. Chain traversal is witnessed by the joint presence of the policy, product and VSAM captures — rationale **D-34** |
| 5 | `PROCEDURE DIVISION.` with no `USING` phrase | `base/src/lgapol01.cbl:77`; `base/src/lgapdb01.cbl:143`; `base/src/lgapvs01.cbl:91` | `PROCEDURE DIVISION USING DFHCOMMAREA.` in each generated copy (rewrite rule R3), which is what binds the linkage record for the dynamic calls above |

## B.3 Statement census → rewrite and stub inventory

Measured with comment lines excluded and continuation lines folded into the statement they belong to.

| Program | Lines | `EXEC CICS` | `EXEC SQL` | SQL breakdown |
|---|---:|---:|---:|---|
| `base/src/lgapol01.cbl` | 169 | 9 | 0 | — |
| `base/src/lgapdb01.cbl` | 595 | 20 | 11 | 3 `INCLUDE` + 8 DML |
| `base/src/lgapvs01.cbl` | 188 | 7 | 0 | — |
| **Total** | **952** | **36** | **11** | **3 `INCLUDE` + 8 DML** |

**Counting note.** Match `EXEC CICS` **case-insensitively**. The VSAM write is spelled
`Exec CICS Write File('KSDSPOLY')` in mixed case at `base/src/lgapvs01.cbl:135`, so a case-sensitive count wrongly
yields 6 for that program instead of 7.

Six distinct CICS verbs account for all 36 sites, and each maps to one target construct:

| # | CICS verb | Sites | Locators | Target implementation |
|---:|---|---:|---|---|
| 1 | `RETURN` | 12 | `base/src/lgapol01.cbl:115,126`; `base/src/lgapdb01.cbl:205,212,250,298,303,394,432,478,552`; `base/src/lgapvs01.cbl:146` | `GOBACK`, emitted **inline** (rule R7); no called return stub exists — rationale **D-29** |
| 2 | `LINK` | 11 | 2 chain links per [§B.2](#b2-call-order-and-link-lengths); 9 diagnostic links per row 3 below | two targets: dynamic `CALL` for the chain links, the `CICS-DIAG-LINK` stub for the diagnostic links |
| 3 | `LINK PROGRAM('LGSTSQ')` — the diagnostic subset | 9 | `base/src/lgapol01.cbl:149,157,163`; `base/src/lgapdb01.cbl:575,583,589`; `base/src/lgapvs01.cbl:169,176,182` | `MOVE LENGTH OF <area> TO HARNESS-DIAG-LEN` then `CALL 'CICS-DIAG-LINK' USING <area> HARNESS-DIAG-LEN` (rule R6). The named program's own implementation is **out of scope and is never opened**; the stub accepts any area length. Rationale **D-31**, **D-32** |
| 4 | `ABEND` | 6 | `base/src/lgapol01.cbl:101` (`LGCA`); `base/src/lgapdb01.cbl:168` (`LGCA`), `:393,431,477,551` (`LGSQ`) | `MOVE '<code>' TO HARNESS-ABEND-CODE`, `CALL 'CICS-ABEND' USING HARNESS-ABEND-CODE`, then `GOBACK` **in the caller** (rule R8); the stub records and terminates nothing. Rationale **D-30** |
| 5 | `FORMATTIME` | 3 | `base/src/lgapol01.cbl:142-145`; `base/src/lgapdb01.cbl:568-571`; `base/src/lgapvs01.cbl:158-161` | `CALL 'CICS-FORMATTIME'` with the three source operands in source order (rule R11); deterministic harness time |
| 6 | `ASKTIME` | 3 | `base/src/lgapol01.cbl:140-141`; `base/src/lgapdb01.cbl:566-567`; `base/src/lgapvs01.cbl:156-157` | `CALL 'CICS-ASKTIME'` with the source's own `ABSTIME` operand (rule R10); deterministic harness time |
| 7 | `WRITE FILE('KSDSPOLY')` | 1 | `base/src/lgapvs01.cbl:135-141` | `CALL 'CICS-WRITE'` with all six operands in source-operand order (rule R9); the stub captures the record and sets the normal response by default. The two length operands pass as zero-padded 5-digit literals — rationale **D-33** |

Verb arithmetic: 12 + 11 + 6 + 3 + 3 + 1 = 36 = 9 + 20 + 7. Rows 2 and 3 describe the same 11 `LINK` sites, split by
target, and row 3 is not added again.

## B.4 SQL accounting

Eleven `EXEC SQL` blocks: 3 `INCLUDE` and 8 DML.

| # | SQL block | Locator | Target implementation | `USING` arity |
|---:|---|---|---|---:|
| 1 | `INCLUDE LGPOLICY` | `base/src/lgapdb01.cbl:75-77` | `COPY LGPOLICY.` (rule R2), resolved from the generated build tree | — |
| 2 | `INCLUDE SQLCA` | `base/src/lgapdb01.cbl:124-126` | `COPY HSQLCA.` (rule R2), the minimal harness SQLCA | — |
| 3 | `INCLUDE LGCMAREA` | `base/src/lgapdb01.cbl:135-137` | `COPY LGCMAREA.` (rule R2), nested inside the `01 DFHCOMMAREA.` group | — |
| 4 | `INSERT INTO POLICY` | `base/src/lgapdb01.cbl:268-288` | `CALL 'SQL-INSERT-POLICY'` | **7** |
| 5 | `SET :DB2-POLICYNUM-INT = IDENTITY_VAL_LOCAL()` | `base/src/lgapdb01.cbl:308-310` | `CALL 'SQL-SET-IDENTITY'`, direction out | **1** |
| 6 | `SELECT LASTCHANGED INTO :CA-LASTCHANGED` | `base/src/lgapdb01.cbl:316-321` | `CALL 'SQL-SELECT-LASTCHANGED'` — `INTO` target first, then the `WHERE` host | **2** |
| 7 | `INSERT INTO ENDOWMENT` with the varchar column | `base/src/lgapdb01.cbl:346-366` | `CALL 'SQL-INSERT-ENDOWMENT'` — one normalised superset list in this branch's declared order | **9** |
| 8 | `INSERT INTO ENDOWMENT` without the varchar column | `base/src/lgapdb01.cbl:368-386` | the **same** `SQL-INSERT-ENDOWMENT` call; this branch's 8 operands are a prefix of the 9 and the stub ignores the padding argument when `WS-VARY-LEN` is not positive. Rationale **D-17** | 9 (shared) |
| 9 | `INSERT INTO HOUSE` | `base/src/lgapdb01.cbl:409-425` | `CALL 'SQL-INSERT-HOUSE'` | **7** |
| 10 | `INSERT INTO MOTOR` | `base/src/lgapdb01.cbl:449-471` | `CALL 'SQL-INSERT-MOTOR'`, including `DB2-M-PREMIUM-INT` | **10** |
| 11 | `INSERT INTO COMMERCIAL` | `base/src/lgapdb01.cbl:499-545` | `CALL 'SQL-INSERT-COMMERCIAL'`, including the four commercial premium hosts and the four peril codes the chain cannot execute without | **20** |

Eight DML blocks resolve to **7** distinct stub programs because rows 7 and 8 share one call. Two POLICY columns take
no host variable: `POLICYNUMBER` is supplied by the keyword `DEFAULT` at `base/src/lgapdb01.cbl:279` and `LASTCHANGED`
by `CURRENT TIMESTAMP` at `:284`. Every host variable is named in an explicit `USING` list in source order; a block
present in the source with no map entry fails the run.

## B.5 EIB fields

Exactly five EIB fields are referenced, and no sixth EIB symbol appears in the five inputs.

| # | EIB field | References | Locators | Target implementation |
|---:|---|---:|---|---|
| 1 | `EIBCALEN` | 17 | `base/src/lgapol01.cbl:91,98,113,154,155,156`; `base/src/lgapdb01.cbl:154,165,210,339,580,581,582`; `base/src/lgapvs01.cbl:97,173,174,175` | shared `EXTERNAL` item of `modernization/harness/copybooks/dfheiblk.cpy`, set to 32500 before each chain call by rule R5 and by the driver |
| 2 | `EIBTRNID` | 2 | `base/src/lgapol01.cbl:88`; `base/src/lgapdb01.cbl:151` | same surrogate copybook; deterministic harness value |
| 3 | `EIBTRMID` | 2 | `base/src/lgapol01.cbl:89`; `base/src/lgapdb01.cbl:152` | same surrogate copybook; deterministic harness value |
| 4 | `EIBTASKN` | 2 | `base/src/lgapol01.cbl:90`; `base/src/lgapdb01.cbl:153` | same surrogate copybook; deterministic harness value |
| 5 | `EIBRESP2` | 1 | `base/src/lgapvs01.cbl:143` | same surrogate copybook; written by the write stub's response path |

Inserted into each generated copy by rule R4 as `COPY DFHEIBLK.`, so the driver, the three translated programs and the
twelve stubs address one instance. Rationale for the shared `EXTERNAL` state: [`decision-log.md`](decision-log.md),
row **D-26**.

## B.6 Compiler directive, response macro and remaining single-site constructs

| # | Source construct | Locator | Target implementation |
|---:|---|---|---|
| 1 | `PROCESS SQL` compiler directive | `base/src/lgapdb01.cbl:1` | a fixed-format comment in the generated copy (rule R1); the directive reaches no compiler and the line stays within column 72 |
| 2 | `DFHRESP(NORMAL)` macro | `base/src/lgapvs01.cbl:142` | the named constant `DFHRESP-NORMAL` from `modernization/harness/copybooks/dfhresp.cpy` (rule R12); only `NORMAL` has a harness constant and any other response condition fails the run |
| 3 | `WORKING-STORAGE SECTION` anchor of each program | `base/src/lgapol01.cbl:19`; `base/src/lgapdb01.cbl:19`; `base/src/lgapvs01.cbl:16` | the anchor line is copied unchanged and rule R4 inserts the harness declarations after it — `COPY DFHEIBLK.`, `HARNESS-ABEND-CODE`, `HARNESS-DIAG-LEN`, plus `COPY DFHRESP.` in the VSAM program only |
| 4 | Every remaining source line | 694 lines across the three programs | copied **byte-for-byte** (rule R14); the observed count is recorded per run in the translation report |
| 5 | Maximum source line width | 72 in all five inputs | every generated line is held to the same bound; the translator fails rather than emit a line reaching column 73 |

## B.7 VSAM projection

| # | Source construct | Locator | Target implementation |
|---:|---|---|---|
| 1 | `WF-Policy-Info` — the **64-byte record** written to `KSDSPOLY` | `base/src/lgapvs01.cbl:25-30` with the payload redefinitions at `:31-51` | captured whole by the `CICS-WRITE` stub and asserted to be 64 bytes long; corroborates chain completion only |
| 2 | `WF-Policy-Key` — the **21-byte key**, in the order request-type letter, customer number, policy number | `base/src/lgapvs01.cbl:26-29`, built at `:99-101` | captured and compared against the type, customer and policy identifiers of the same sample by the comparison gate. **The 64-byte record and the 21-byte key are distinct and are never conflated** |
| 3 | `Move CA-Request-ID(4:1) To WF-Request-ID` | `base/src/lgapvs01.cbl:99` | an independent corroboration of the derived `policy_type`; see [§B.10](#b10-request-routing-and-the-derived-policy-type) |
| 4 | The product payload projections — commercial, endowment, house and motor `WHEN` branches and the `WHEN Other` blanking | `base/src/lgapvs01.cbl:103-132` | executed unchanged in the generated copy so the write reproduces the source record; **no canonical column** derives from these payload fields |

## B.8 Return-code and abend contract

The observed convention is preserved unchanged and reported. Two exercise columns are reported: the pipeline's
`execute` stage selects the two success cases only, while the harness case table drives the failure conditions by
deterministic injection (**D-20**).

| # | Code | Observed meaning | Set at | Exercised by the two pipeline samples | Exercised by the full harness case table |
|---:|---|---|---|---|---|
| 1 | `00` | success | `base/src/lgapol01.cbl:105`; `base/src/lgapdb01.cbl:172,293` | **Yes** — both executed samples | Yes — motor, commercial and house routes |
| 2 | `70` | policy insert returned SQLCODE −530 | `base/src/lgapdb01.cbl:296` (checked `:295`, returns `:298`) | No — documented from source, unexercised by those samples | Yes, by injected SQLCODE |
| 3 | `80` | VSAM write response was not normal | `base/src/lgapvs01.cbl:144` (checked `:142`, returns `:146`) | No — documented from source, unexercised by those samples | Yes, by injected write response |
| 4 | `90` | SQL failure; the subtype inserts also abend `LGSQ` | `base/src/lgapdb01.cbl:301,390,428,474,548` | No — documented from source, unexercised by those samples | Yes, by injected SQLCODE |
| 5 | `98` | COMMAREA shorter than the required length | `base/src/lgapol01.cbl:114`; `base/src/lgapdb01.cbl:211` | No — documented from source, unexercised by those samples | Yes |
| 6 | `99` | unsupported request id | `base/src/lgapdb01.cbl:204,239` | No — documented from source, unexercised by those samples | Yes |
| 7 | Abend `LGCA` | no COMMAREA received | `base/src/lgapol01.cbl:101`; `base/src/lgapdb01.cbl:168` | No — documented from source, unexercised by those samples | Yes |
| 8 | Abend `LGSQ` | backout of the policy insert after a failed subtype insert | `base/src/lgapdb01.cbl:393,431,477,551` | No — documented from source, unexercised by those samples | Yes |

Unexercised routes, stated rather than implied: the **endowment route is compiled and never executed** in either run,
and the **house route is compiled and not exercised by the two pipeline samples**. Rationale and the bounds of the
emulation: [`decision-log.md`](decision-log.md), rows **D-18**, **D-20**, **D-21** and **D-30**. The recorded outcome
of each run is in [`../validation/validation-evidence.md`](../validation/validation-evidence.md).

## B.9 Arithmetic inventory and the no-formula finding

| # | Arithmetic construct | Sites | Locators | Target treatment |
|---:|---|---:|---|---|
| 1 | `ADD` | 6 | `base/src/lgapol01.cbl:109`; `base/src/lgapdb01.cbl:182,187,191,195,199` | all six operate on length constants; **no canonical column** derives from them. Registered in [§A.5](#a5-length-constants-used-by-the-chain) |
| 2 | `SUBTRACT` | 1 | `base/src/lgapdb01.cbl:339-340` | length arithmetic on the endowment route; **no canonical column**. Its measured result is the reason no endowment sample is executed — **D-18** |
| 3 | `COMPUTE` | **0** | — | nothing to map |
| 4 | `MULTIPLY` | **0** | — | nothing to map |
| 5 | `DIVIDE` | **0** | — | nothing to map |
| 6 | The six amount paths | 6 `MOVE` statements | `base/src/lgapdb01.cbl:265,445,489,491,493,495` | passthrough into binary host variables with no arithmetic; the six canonical amount columns are passthrough values |

**Target treatment of the no-formula finding: documented finding, no derived column created.** No rating formula,
rating factor, derived-factor column, commission field or backfilled calculation exists in the target, in either
direction. The finding is recorded in [`../extraction/extraction-spec.md`](../extraction/extraction-spec.md), in
[`field-level-lineage.md`](field-level-lineage.md) and in the `formula: none` key of the field map. Rationale:
[`decision-log.md`](decision-log.md), row **D-11**.

## B.10 Request routing and the derived policy type

| # | Source construct | Locator | Target implementation |
|---:|---|---|---|
| 1 | `EVALUATE CA-REQUEST-ID` — `01AEND` → `E`, `01AHOU` → `H`, `01AMOT` → `M`, `01ACOM` → `C`, `WHEN OTHER` → return code `99` | `base/src/lgapdb01.cbl:184-207` | the `request_routing` block of [`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml), read by `extract_commarea.py` to derive `policy_type`, and the same routing preserved unchanged in the generated copy |
| 2 | The routed value bound into the POLICY insert as `:DB2-POLICYTYPE` | `base/src/lgapdb01.cbl:283` | the policy SQL capture the comparison gate checks the derived `policy_type` against, so the derivation is verified rather than trusted |
| 3 | The second routing `EVALUATE`, selecting the product insert paragraph | `base/src/lgapdb01.cbl:223-241` | preserved unchanged; it selects which product stub is called and therefore which premium columns are populated |
| 4 | `Move CA-Request-ID(4:1) To WF-Request-ID` | `base/src/lgapvs01.cbl:99` | an independent second derivation of the same letter, captured with the VSAM key and used to corroborate the routed type |

Rationale for deriving rather than reading `policy_type`: [`decision-log.md`](decision-log.md), row **D-50**.

## B.11 The measured ordering constraint

| # | Source construct | Locator | Target implementation |
|---:|---|---|---|
| 1 | `PERFORM INSERT-POLICY` before product routing | `base/src/lgapdb01.cbl:219,223-241` | the `policy_first_captured` entry of the `execution_order` block in [`../harness/statement_map.yml`](../harness/statement_map.yml) |
| 2 | `:CA-LASTCHANGED` supplied as the commercial `RequestDate` value, while `CA-LASTCHANGED` is populated only by the read-back that follows the policy insert | `base/src/lgapdb01.cbl:525`; populated at `:316-321` | the `lastchanged_before_commercial` entry of the same block, `reason_kind: data_dependency` on host `CA-LASTCHANGED`, witnessed at run time by the shared capture ordinals |
| 3 | Identity recovery before the timestamp read-back | `base/src/lgapdb01.cbl:308-310` then `:316-321` | the `policy_before_identity` and `identity_before_lastchanged` entries |
| 4 | Both inserts before the VSAM link | `base/src/lgapdb01.cbl:219-241` then `:243-246` | the `policy_and_product_before_vsam_write` entry |

Eight ordering entries in total; the map, the shared capture copybook and the driver's order table must agree or the
run fails. Rationale: [`decision-log.md`](decision-log.md), rows **D-15** and **D-27**.


---

# Part C — REVERSE direction: every created artifact

All **61** authored artifacts of this work, each with the requirement, source construct or user rule that justifies it.
Paths are relative to `modernization/`. Group sizes are stated per section and checked in
[§C.8](#c8-artifact-count-check).

**No row of this part names a pre-existing repository file as a target.** The mode distribution of this work is
REFERENCE 5, CREATE 61, UPDATE 0: the five source artifacts are read-only and byte-identical, and no other pre-existing
file is modified. Rationale: [`decision-log.md`](decision-log.md), row **D-01**.

## C.1 Scaffolding — 4 artifacts

| # | Created artifact | Justified by |
|---:|---|---|
| 1 | `README.md` | The requirement for a discoverable entry point: environment setup, the precondition gate and the one-phase `make all` workflow, sited inside the new tree under the read-only boundary (**D-01**) |
| 2 | `requirements.txt` | The requirement to pin every direct Python and dbt dependency exactly, with both adapters and both drivers installed on either branch (**D-45**) |
| 3 | `Makefile` | The requirement for a non-interactive one-phase execution order — `verify-env`, `gate`, `translate`, `compile`, `execute`, `extract`, `land`, `load`, `dbt`, `diff`, `verify-readonly`, `all` — that stops at the first failing gate |
| 4 | `.gitignore` | The requirement to exclude only generated bridge artifacts, from a nested file that touches no pre-existing ignore file (**D-47**) |

## C.2 Extraction — 7 artifacts

| # | Created artifact | Justified by |
|---:|---|---|
| 5 | `extraction/extraction-spec.md` | The requested extraction specification: both entity specifications, the 17 logical entries, every in-scope declaration and intermediate, the 16 runtime values and the explicit no-formula statement, each with a source locator |
| 6 | `extraction/copybook_field_map.yml` | The requirement for one machine-readable metadata spine — source concept, declarations and intermediates, runtime status, offset and length, target column and transformation — consumed by extraction, landing, warehouse typing and lineage (**D-16** for the scope split against the statement map) |
| 7 | `extraction/build_sample_commarea.py` | The requirement to drive the chain with a full-length record: it validates the sample JSON and emits the 32,500-character COMMAREA, which is also the handling of the stale motor constant (**D-08**) and of the out-of-domain seeds (**D-35**) |
| 8 | `extraction/extract_commarea.py` | The post-chain extraction requirement: decode the returned COMMAREA against the field map, derive `policy_type` (**D-50**), normalise the timestamp (**D-53**) and derive **no** amount |
| 9 | `extraction/sample_input/commarea_01amot.json` | The requirement for a motor sample covering payment and the motor premium, routed by `01AMOT` [base/src/lgapdb01.cbl:194-196] |
| 10 | `extraction/sample_input/commarea_01acom.json` | The requirement for a commercial sample covering payment and all four commercial premiums, routed by `01ACOM` [base/src/lgapdb01.cbl:198-200] |
| 11 | `extraction/sample_input/README.md` | The requirement to explain the sample values, full-record generation and the stale-length safeguard measured in [§A.5](#a5-length-constants-used-by-the-chain) |

## C.3 Harness — 21 artifacts

| # | Created artifact | Justified by |
|---:|---|---|
| 12 | `harness/translate.py` | GnuCOBOL rejects the embedded CICS and SQL syntax of the three programs while the originals must stay byte-identical, so the rewrite rules of [Part B](#part-b--forward-direction-non-field-source-constructs) are applied to copies only (**D-06**) |
| 13 | `harness/translation-rules.md` | The requirement to document every source-to-generated rewrite and its limitations; it is the target side of Part B |
| 14 | `harness/statement_map.yml` | The requirement to map all 11 `EXEC SQL` blocks to a `COPY` replacement or an explicit stub `USING` list, plus the ordering constraints of [§B.11](#b11-the-measured-ordering-constraint) |
| 15 | `harness/copybooks/dfheiblk.cpy` | The five referenced EIB fields of [§B.5](#b5-eib-fields), which the compiler does not supply, shared as `EXTERNAL` state (**D-26**) |
| 16 | `harness/copybooks/dfhresp.cpy` | The `DFHRESP(NORMAL)` test at [base/src/lgapvs01.cbl:142], which needs a named constant rather than a CICS macro |
| 17 | `harness/copybooks/hsqlca.cpy` | The `SQLCODE` usage of the Db2 program [base/src/lgapdb01.cbl:124-126,290-305,389,427,473,547] |
| 18 | `harness/copybooks/hcapture.cpy` | The requirement for an independent capture of the values handed to the inserts, the VSAM write and any abend, shared across modules with a monotonic ordering witness (**D-26**, **D-27**) |
| 19 | `harness/stubs/cics_abend.cbl` | The 6 `ABEND` sites of [§B.3](#b3-statement-census--rewrite-and-stub-inventory) (**D-30**) |
| 20 | `harness/stubs/cics_write.cbl` | The single `WRITE FILE('KSDSPOLY')` site [base/src/lgapvs01.cbl:135-141] and the 64-byte record and 21-byte key capture (**D-33**) |
| 21 | `harness/stubs/cics_asktime.cbl` | The 3 `ASKTIME` sites of the error paths, needing deterministic time |
| 22 | `harness/stubs/cics_formattime.cbl` | The 3 `FORMATTIME` sites of the error paths, needing deterministic formatting |
| 23 | `harness/stubs/cics_diag_link.cbl` | The 9 literal diagnostic `LINK` sites, whose target program is outside the authorized source surface and is never opened (**D-31**, **D-32**) |
| 24 | `harness/stubs/sql_insert_policy.cbl` | The POLICY insert [base/src/lgapdb01.cbl:268-288], plus the deterministic identity and timestamp the chain then recovers (**D-19**) |
| 25 | `harness/stubs/sql_insert_motor.cbl` | The MOTOR insert [base/src/lgapdb01.cbl:449-471] and its 10 host values including the premium |
| 26 | `harness/stubs/sql_insert_commercial.cbl` | The COMMERCIAL insert [base/src/lgapdb01.cbl:499-545] and its 20 host values including the four premiums and the four peril codes (**D-12**) |
| 27 | `harness/stubs/sql_insert_endowment.cbl` | Both ENDOWMENT branches [base/src/lgapdb01.cbl:346-366,368-386], normalised to one 9-item superset (**D-17**) |
| 28 | `harness/stubs/sql_insert_house.cbl` | The HOUSE insert [base/src/lgapdb01.cbl:409-425], so the routed program is complete and compilable |
| 29 | `harness/stubs/sql_set_identity.cbl` | `SET :DB2-POLICYNUM-INT = IDENTITY_VAL_LOCAL()` [base/src/lgapdb01.cbl:308-310] |
| 30 | `harness/stubs/sql_select_lastchanged.cbl` | The `LASTCHANGED` read-back [base/src/lgapdb01.cbl:316-321] |
| 31 | `harness/driver.cbl` | The requirement for an authorized caller: it supplies the shared COMMAREA the entry program expects [base/src/lgapol01.cbl:70-77], sets the EIB surrogate values and reports the post-chain record and the captures |
| 32 | `harness/run_harness.sh` | The requirement to build, translate, compile the modules with `cobc -m` and the driver with `cobc -x`, execute the cases and retain the logs (**D-20**, **D-23**, **D-24**, **D-25**) |

## C.4 Landing and warehouse bootstrap — 7 artifacts

| # | Created artifact | Justified by |
|---:|---|---|
| 33 | `landing/landing-schema.json` | The landed-record contract: `source_system_key` plus the 16 runtime values, every field a string, no additional key (**D-52**) |
| 34 | `landing/land_to_s3.py` | The requirement to land one post-chain record in S3 under a `source_system_key` prefix before transformation, through the same client on both endpoints (**D-56**, **D-57**) |
| 35 | `landing/load_redshift.sql` | The real-target raw load: a `COPY` into `raw.genapp_policy_issue` from a manifest object (**D-40**), key-scoped so a re-run is idempotent (**D-38**) |
| 36 | `landing/load_local.py` | The local-substitute raw load of the same landed object into DuckDB, producing the identical raw shape so the dbt models need no edit (**D-09**) |
| 37 | `landing/partition-layout.md` | The user requirement for an S3 prefix partitioned by source system, entity and extract date, distinct from warehouse table design (**D-10**) |
| 38 | `warehouse/ddl/01_schemas.sql` | The requirement to bootstrap the `raw` and `canonical` schemas where the target needs it explicitly (**D-43**) |
| 39 | `warehouse/ddl/02_raw_genapp_policy_issue.sql` | The all-`VARCHAR` raw relation that preserves exactly what landed; canonical tables are owned by dbt instead (**D-41**, **D-42**) |

## C.5 dbt project — 14 artifacts

| # | Created artifact | Justified by |
|---:|---|---|
| 40 | `dbt/genapp_rqi/dbt_project.yml` | The requirement for one portable dbt project: model paths, clean targets and per-layer materialisation defaults |
| 41 | `dbt/genapp_rqi/profiles.example.yml` | The environment contract for both targets from environment variables, with no committed credential (**D-44**) |
| 42 | `dbt/genapp_rqi/models/staging/genapp_class_exemplar/_genapp__sources.yml` | The requirement that `raw.genapp_policy_issue` is the sole dbt source and that staging reads it through `source()` |
| 43 | `dbt/genapp_rqi/models/staging/genapp_class_exemplar/_genapp__models.yml` | The staging column contract, descriptions and generic tests carried from the field map |
| 44 | `dbt/genapp_rqi/models/staging/genapp_class_exemplar/stg_genapp__policy_issue.sql` | The requirement to standardise names and trim fixed-width whitespace while preserving the 1:1 grain |
| 45 | `dbt/genapp_rqi/models/intermediate/int_policy_issue_decoded.sql` | The requirement to type one record once, in engine-common SQL, and to apply the product-specific NULL logic (**D-41**, **D-54**) |
| 46 | `dbt/genapp_rqi/models/intermediate/_int__models.yml` | The typed intermediate contract and its data tests |
| 47 | `dbt/genapp_rqi/models/marts/canonical/canonical_issued_policy.sql` | The requested relation `canonical.issued_policy`, successful rows only (**D-51**) |
| 48 | `dbt/genapp_rqi/models/marts/canonical/canonical_preissued_rating.sql` | The requested relation `canonical.preissued_rating`, successful rows only |
| 49 | `dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml` | The single declaration of both canonical column sets, enforced as a contract, and the per-column lineage metadata (**D-42**, **D-49**) |
| 50 | `dbt/genapp_rqi/macros/generate_schema_name.sql` | The requirement that the literal schema names `staging`, `intermediate` and `canonical` are preserved on both adapters (**D-43**) |
| 51 | `dbt/genapp_rqi/tests/assert_issued_policy_unique_key.sql` | The requirement of one row per `(source_system_key, policy_number)` on the issued relation (**D-46**) |
| 52 | `dbt/genapp_rqi/tests/assert_preissued_rating_unique_key.sql` | The same grain requirement on the rating relation (**D-46**) |
| 53 | `dbt/genapp_rqi/tests/assert_product_premium_nullability.sql` | The requirement that a motor row carries only the motor premium, a commercial row only the four commercial premiums, and any other product no product premium — NULL, never zero (**D-54**) |

## C.6 Validation — 3 artifacts

| # | Created artifact | Justified by |
|---:|---|---|
| 54 | `validation/validation-evidence.md` | The requirement to record the commands, versions, results, the visible local-versus-AWS status and the open items of every gate |
| 55 | `validation/diff_harness_vs_warehouse.py` | The requirement to compare both canonical rows field by field against the independent harness captures, exactly except for the ±0.01 amount tolerance (**D-04**, **D-37**, **D-59**) |
| 56 | `validation/verify_readonly.sh` | The scope guarantee itself: the five-file SHA-256 baseline, an empty `git status --porcelain -- base/` and no tracked modification (**D-01**, **D-65**) |

## C.7 Documentation — 5 artifacts

| # | Created artifact | Justified by |
|---:|---|---|
| 57 | `docs/project-guide.md` | The requested project guide: the no-formula finding, the built and proposed architectures cited by figure name, the outstanding-AWS status and the repeatable future-RQI onboarding procedure |
| 58 | `docs/field-level-lineage.md` | The requirement that every source-derived canonical column trace to a named COBOL item and locator, with `source_system_key` marked as the sole user-mandated warehouse-assigned exception |
| 59 | `docs/decision-log.md` | **User Rule 1 — Explainability.** The rule requires a Markdown decision log stating what was decided, the alternatives, the rationale and the risk, and makes it the single source of "why" |
| 60 | `docs/traceability-matrix.md` — this file | **User Rule 1 — Explainability.** The rule requires, for a migration or refactor, a bidirectional traceability matrix mapping source constructs to target implementations with 100% coverage and no gaps |
| 61 | `docs/architecture.md` | **User Rule 2 — Visual Architecture Documentation.** The rule requires Mermaid figures with descriptive names and visible legends, referenced by name, and both the before and the after state of a modified architecture |

**These three documents exist because of the user rules, not because of a technical need.** Nothing in the bridge
imports them, and the pipeline runs without them; they are deliverables the rules define. `decision-log.md` and
`traceability-matrix.md` trace back to **Rule 1**, and `architecture.md` traces back to **Rule 2**. The rule-conflict
resolutions that produced them are rows **D-61** through **D-64**.

## C.8 Artifact count check

| Group | Artifacts | Rows |
|---|---:|---|
| Scaffolding | 4 | 1-4 |
| Extraction | 7 | 5-11 |
| Harness | 21 | 12-32 |
| Landing and warehouse bootstrap | 7 | 33-39 |
| dbt project | 14 | 40-53 |
| Validation | 3 | 54-56 |
| Documentation | 5 | 57-61 |
| **Total** | **61** | 1-61, numbered consecutively with no gap and no repeat |

**4 + 7 + 21 + 7 + 14 + 3 + 5 = 61.** The group sizes sum to the stated total and to the CREATE count of this work,
and every one of the 61 carries a justification row above.

## C.9 Generated paths excluded from the authored count

These are produced by a run rather than authored, and are deliberately outside the 61. Only trailing wildcards are
used, and the DuckDB database is named exactly.

| # | Generated path | Produced by |
|---:|---|---|
| 1 | `.venv/**` | environment creation from `requirements.txt` |
| 2 | `harness/build/**` | `harness/translate.py` and `harness/run_harness.sh`, regenerated on every run |
| 3 | `validation/expected/**` | the harness, as the normalised expected captures per case |
| 4 | `validation/artifacts/**` | the harness and the Makefile stages, as the published evidence set |
| 5 | `dbt/genapp_rqi/target/**` | the dbt CLI |
| 6 | `dbt/genapp_rqi/logs/**` | the dbt CLI |
| 7 | `validation/local.duckdb` | `landing/load_local.py` and the local dbt target |

Rows 1, 2, 5, 6 and 7 are ignored by `modernization/.gitignore`; rows 3 and 4 stay tracked because they are the
evidence deliverable. Rationale: [`decision-log.md`](decision-log.md), rows **D-47** and **D-65**.


---

# Part D — REVERSE direction: every canonical column

One row per canonical column instance: **11** on `canonical.issued_policy` and **9** on
`canonical.preissued_rating`, **20** in total. Types are those of the enforced contract
[`../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml`](../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml),
and every row agrees with [`field-level-lineage.md`](field-level-lineage.md).

## D.1 `canonical.issued_policy` — 11 column instances

Grain and natural key `(source_system_key, policy_number)`.

| # | Canonical column | Type | Traces back to | Locator |
|---:|---|---|---|---|
| 1 | `source_system_key` | `varchar(64)` NOT NULL | **User requirement**, not a COBOL construct: each entity carries a source-system key so rows from a future RQI slot into the same tables without structural change | `—` |
| 2 | `policy_number` | `bigint` NOT NULL | Returned `CA-POLICY-NUM`, assigned from `DB2-POLICYNUM-INT` after the policy insert | `base/src/lgcmarea.cpy:35`; `base/src/lgapdb01.cbl:117,307-311` |
| 3 | `policy_type` | `char(1)` NOT NULL | `DB2-POLICYTYPE`, derived from `CA-REQUEST-ID` by the routing `EVALUATE` and verified against the policy SQL capture | `base/src/lgpolicy.cpy:43`; `base/src/lgapdb01.cbl:184-207,283` |
| 4 | `customer_number` | `bigint` NOT NULL | `CA-CUSTOMER-NUM`, via `DB2-CUSTOMERNUM-INT` | `base/src/lgcmarea.cpy:12`; `base/src/lgapdb01.cbl:90,176,280` |
| 5 | `request_id` | `varchar(6)` NOT NULL | `CA-REQUEST-ID` | `base/src/lgcmarea.cpy:10` |
| 6 | `return_code` | `char(2)` NOT NULL | Returned `CA-RETURN-CODE` | `base/src/lgcmarea.cpy:11` |
| 7 | `issue_date` | `date` | `CA-ISSUE-DATE`, bound directly by the policy insert | `base/src/lgcmarea.cpy:38`; `base/src/lgapdb01.cbl:281` |
| 8 | `expiry_date` | `date` | `CA-EXPIRY-DATE`, bound directly by the policy insert | `base/src/lgcmarea.cpy:39`; `base/src/lgapdb01.cbl:282` |
| 9 | `last_changed` | `timestamp` NOT NULL | Returned `CA-LASTCHANGED`, the `INTO` target of the read-back | `base/src/lgcmarea.cpy:40`; `base/src/lgapdb01.cbl:315-321` |
| 10 | `broker_id` | `bigint` | `CA-BROKERID`, via `DB2-BROKERID-INT` | `base/src/lgcmarea.cpy:41`; `base/src/lgapdb01.cbl:91,264,285` |
| 11 | `brokers_reference` | `varchar(10)` | `CA-BROKERSREF`, trimmed of the fixed-width trailing spaces | `base/src/lgcmarea.cpy:42`; `base/src/lgapdb01.cbl:286` |

Ten of the eleven trace to a named COBOL item; the eleventh is `source_system_key`.

## D.2 `canonical.preissued_rating` — 9 column instances

Same grain and natural key as `canonical.issued_policy`.

| # | Canonical column | Type | Traces back to | Locator |
|---:|---|---|---|---|
| 1 | `source_system_key` | `varchar(64)` NOT NULL | **User requirement**, not a COBOL construct: the second of the two warehouse-assigned instances, present so a future RQI needs no structural change | `—` |
| 2 | `policy_number` | `bigint` NOT NULL | Returned `CA-POLICY-NUM`, identical lineage to `issued_policy.policy_number` | `base/src/lgcmarea.cpy:35`; `base/src/lgapdb01.cbl:117,307-311` |
| 3 | `policy_type` | `char(1)` NOT NULL | `DB2-POLICYTYPE`, identical lineage to `issued_policy.policy_type` | `base/src/lgpolicy.cpy:43`; `base/src/lgapdb01.cbl:184-207,283` |
| 4 | `payment_amount` | `decimal(8,2)` | `CA-PAYMENT`, via `DB2-PAYMENT-INT`; passthrough, no formula | `base/src/lgcmarea.cpy:43`; `base/src/lgapdb01.cbl:92,265,287` |
| 5 | `motor_premium_amount` | `decimal(8,2)` | `CA-M-PREMIUM`, via `DB2-M-PREMIUM-int`; policy type `M` only | `base/src/lgcmarea.cpy:73`; `base/src/lgapdb01.cbl:100,445,469` |
| 6 | `fire_premium_amount` | `decimal(10,2)` | `CA-B-FirePremium`, via `DB2-B-FirePremium-Int`; policy type `C` only | `base/src/lgcmarea.cpy:85`; `base/src/lgapdb01.cbl:103,489,535` |
| 7 | `crime_premium_amount` | `decimal(10,2)` | `CA-B-CrimePremium`, via `DB2-B-CrimePremium-Int`; policy type `C` only | `base/src/lgcmarea.cpy:87`; `base/src/lgapdb01.cbl:105,491,537` |
| 8 | `flood_premium_amount` | `decimal(10,2)` | `CA-B-FloodPremium`, via `DB2-B-FloodPremium-Int`; policy type `C` only | `base/src/lgcmarea.cpy:89`; `base/src/lgapdb01.cbl:107,493,539` |
| 9 | `weather_premium_amount` | `decimal(10,2)` | `CA-B-WeatherPremium`, via `DB2-B-WeatherPremium-Int`; policy type `C` only | `base/src/lgcmarea.cpy:91`; `base/src/lgapdb01.cbl:109,495,541` |

Eight of the nine trace to a named COBOL item; the ninth is `source_system_key`.

## D.3 `source_system_key` — the only canonical field without a COBOL origin

Both instances — row 1 of [§D.1](#d1-canonicalissued_policy--11-column-instances) and row 1 of
[§D.2](#d2-canonicalpreissued_rating--9-column-instances) — cite the **user requirement** and carry `—` in place of a
locator. No item of the COMMAREA and no Db2-side declaration identifies the source system, so no COBOL construct could
supply it and none is invented for it. It is the sole declared exception to complete COBOL lineage in this work.
Rationale: [`decision-log.md`](decision-log.md), row **D-03**.

## D.4 Reverse coverage assertions for the canonical layer

| Assertion | Value |
|---|---:|
| Canonical column instances documented above | **20** |
| Instances tracing to a named COBOL item and locator | **18** |
| Instances tracing to the stated warehouse assignment | **2** |
| Canonical columns lacking a reverse entry | **0** |
| Canonical columns beyond the declared 20 | **0** |
| Canonical relations | **2** |
| Third relation of any kind, including a source-system registry | **none** |
| Registry, provenance, audit, surrogate-key, hash, load-timestamp, formula, derived-factor, rating-factor, commission, Quote or Loss column | **none** |

The enforced contract is the single declaration of both column sets: a renamed, added, dropped or retyped column fails
the dbt build. These are the same figures [`field-level-lineage.md`](field-level-lineage.md) and the `counts` block of
[`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml) assert, and they must agree exactly.

---

# Part E — Coverage assertion and gap statement

## E.1 Forward coverage is complete

Every in-scope source declaration, program intermediate and non-field construct of the five read-only artifacts has a
target treatment recorded above:

| Forward scope | Where recorded | Outcome |
|---|---|---|
| 17 logical field entries | [§A.1](#a1-the-17-logical-field-entries) | 15 active, 1 derived, 1 declaration-only → 16 runtime values |
| 15 in-scope COMMAREA declarations | [§A.2](#a2-declaration-register--basesrclgcmareacpy) | each with a locator, a byte range and a target column |
| 13 in-scope `lgpolicy.cpy` counterparts | [§A.3](#a3-declaration-register--basesrclgpolicycpy-db2-side-counterparts) | 1 active-derived, 12 declaration-only — 7 of them with the explicit treatment `lineage entry, no column` |
| 15 program intermediates and length work items | [§A.4](#a4-program-intermediates-and-length-work-items) | 9 value carriers, 6 length or padding items; none becomes a column of its own |
| 6 length constants | [§A.5](#a5-length-constants-used-by-the-chain) | unchanged; the 12-byte motor shortfall is recorded with its handling |
| 4 peril codes plus 8 further no-target groups | [§A.6](#a6-excluded-and-no-target-declarations) | excluded or unmapped, each with an explicit reason |
| 36 `EXEC CICS` sites across 6 verbs | [§B.3](#b3-statement-census--rewrite-and-stub-inventory) | every site mapped to `GOBACK`, a dynamic `CALL` or a named stub |
| 11 `EXEC SQL` blocks | [§B.4](#b4-sql-accounting) | 3 `COPY` replacements and 8 DML blocks resolving to 7 stub calls with declared arities |
| 5 EIB fields | [§B.5](#b5-eib-fields) | one shared `EXTERNAL` surrogate |
| Interface, call order, link lengths, directive, response macro, procedure headers, VSAM projection, return codes, abends, arithmetic, routing and ordering | [§B.1](#b1-interface-contract-and-header-validation), [§B.2](#b2-call-order-and-link-lengths), [§B.6](#b6-compiler-directive-response-macro-and-remaining-single-site-constructs)-[§B.11](#b11-the-measured-ordering-constraint) | preserved and reproduced, or recorded as a documented finding where no target exists |

**No in-scope source construct is absent from the forward direction, and no source item is left without an outcome.**
Where an item legitimately has no target, the outcome is written as `declaration-only`, `excluded` or `no canonical
column` rather than left out.

## E.2 Reverse coverage is complete

| Reverse scope | Where recorded | Outcome |
|---|---|---|
| 61 created artifacts | [§C.1](#c1-scaffolding--4-artifacts)-[§C.7](#c7-documentation--5-artifacts) | each with the requirement, source construct or user rule that justifies it; 4 + 7 + 21 + 7 + 14 + 3 + 5 = 61 |
| 3 rule-forced documents | [§C.7](#c7-documentation--5-artifacts) | `decision-log.md` → Rule 1, `traceability-matrix.md` → Rule 1, `architecture.md` → Rule 2 |
| 7 generated paths | [§C.9](#c9-generated-paths-excluded-from-the-authored-count) | deliberately outside the authored count, each attributed to the run step that produces it |
| 20 canonical column instances | [§D.1](#d1-canonicalissued_policy--11-column-instances)-[§D.2](#d2-canonicalpreissued_rating--9-column-instances) | 18 to a named COBOL item and locator, 2 to the stated warehouse assignment |

**No created artifact and no canonical column stands without a reverse entry**, and no target of this work is a
pre-existing repository file.

## E.3 Gap statement

**Zero gaps in either direction.** Forward: every in-scope source declaration, intermediate and construct has a target
treatment, including the explicit declaration-only and excluded outcomes. Reverse: every created artifact and every
canonical column instance traces to a requirement, a source construct, a user rule or the one stated warehouse
assignment. Unmapped items: **0** forward, **0** reverse.

Two statements this matrix does **not** make. It claims no result on the real AWS target: the formal AWS diff
requirement is OPEN, and the status header's label governs every result any row references. And it introduces nothing
that the sources do not carry — no formula, factor, derived column, registry, third relation, Quote model, Loss build
or commission field appears in either direction.

## E.4 How to re-verify these counts

Each figure above is recomputable from a named authority; a disagreement is a defect in this document.

| Count to recompute | Authority | Where it lives |
|---|---|---|
| 17 logical entries · 16 runtime values · 18 source-derived instances · 11 + 9 total columns · 17 landing fields · 2 relations | the `counts` block | [`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml) |
| 20 canonical column instances, their names, types and nullability | the two `columns` lists of the enforced contract | [`../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml`](../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml) |
| 3 `INCLUDE` + 8 DML = 11 blocks · the seven `USING` arities · 8 ordering constraints | the `checks` block | [`../harness/statement_map.yml`](../harness/statement_map.yml) |
| 36 `EXEC CICS` sites · the six verb totals · the five EIB fields · the 14 rewrite rules | the measured census and rewrite tables | [`../harness/translation-rules.md`](../harness/translation-rules.md) |
| 17 landed keys, all required, no additional key | the `properties` and `required` members | [`../landing/landing-schema.json`](../landing/landing-schema.json) |
| Five source files, their line counts and their SHA-256 baseline · no tracked modification | the baseline list and the gate verdict | [`../validation/verify_readonly.sh`](../validation/verify_readonly.sh) |
| Column-level lineage, column for column | the counts table and the coverage assertion | [`field-level-lineage.md`](field-level-lineage.md) |
| Recorded run results behind the exercise columns of [§B.8](#b8-return-code-and-abend-contract) | the per-stage evidence sections | [`../validation/validation-evidence.md`](../validation/validation-evidence.md) |

Two counts are measured directly from the read-only sources rather than from a bridge artifact: the `EXEC CICS` census
must be taken **case-insensitively** — see the counting note in [§B.3](#b3-statement-census--rewrite-and-stub-inventory)
— and the arithmetic inventory of [§B.9](#b9-arithmetic-inventory-and-the-no-formula-finding) counts statements only,
excluding the word `ADD` where it appears in a comment line.

Topology is not restated here: the pipeline these mappings describe is drawn in
**Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge**, the column allocation in
**Figure 4 — dbt Transformation DAG and Field Allocation** and the gate order in
**Figure 5 — Validation Harness Control Flow**, all in [`architecture.md`](architecture.md), which is their single
rendering authority.

