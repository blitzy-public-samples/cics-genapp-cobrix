# Field-Level Lineage — GenApp Policy-Issue Canonical Warehouse Bridge

This document traces every column of the two canonical relations to the COBOL item it derives from, column by column,
and names the one column that has no COBOL origin. It is the column-level half of the source-to-target coverage
guarantee of this work: [`traceability-matrix.md`](traceability-matrix.md) carries construct-level and artifact-level
coverage, and this file carries column-level coverage.

> **Status — validated against local substitute, not AWS.** Every result this document refers to was produced on the
> local-substitute branch: a moto S3 endpoint in place of Amazon S3 and DuckDB in place of Amazon Redshift. The formal
> AWS diff requirement is **OPEN** and this has not yet happened. Nothing here closes it, and no lineage statement
> below may be read as satisfying it. Production-grade validation requires re-running the same dbt models unmodified
> against real S3 and Amazon Redshift once access is granted.

## Authority

This document narrates [`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml), the
machine-readable authority for every offset, PICTURE, runtime status, target column and transformation named below.
**Where this document and that file disagree, the field map governs and the disagreement is a defect to fix in this
document.** Every value stated here is the value that file records.

The lineage itself rests on five read-only source artifacts, unchanged by this work and byte-identical to their prior
state: `base/src/lgapol01.cbl`, `base/src/lgapdb01.cbl`, `base/src/lgapvs01.cbl`, `base/src/lgcmarea.cpy` and
`base/src/lgpolicy.cpy`. No locator below points outside those five files, and no claim about the existing system
rests on anything else.

| Companion artifact | Role relative to this document |
|---|---|
| [`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml) | Machine authority; this document is its column-oriented narration |
| [`../extraction/extraction-spec.md`](../extraction/extraction-spec.md) | Source-entry-oriented specification: the interface record, the extraction point and the per-entry treatment |
| [`traceability-matrix.md`](traceability-matrix.md) | Forward and reverse coverage of every source construct and every created artifact |
| [`decision-log.md`](decision-log.md) | The single source of rationale, alternatives and risk for every decision this document states an outcome for |
| [`architecture.md`](architecture.md) | The single rendering authority for every figure; this document draws none and cites figures by name |
| [`../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml`](../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml) | The enforced canonical column contract: names, types, nullability |
| [`../landing/landing-schema.json`](../landing/landing-schema.json) | The landed-record contract narrated in section 4 |

This file states lineage **facts**. Every justification is deferred to a named row of
[`decision-log.md`](decision-log.md) and is not restated or re-argued here.

## Citation convention

Every locator is written `path:line` or `path:first-last` and resolves to one of the five read-only sources — for
example `base/src/lgcmarea.cpy:43` is the `CA-PAYMENT` declaration. A cell reading `—` means the item does not exist,
never that a locator was unavailable. Byte ranges are 1-based positions in the 32,500-byte `DFHCOMMAREA` and are
quoted only where the declaration widths of `base/src/lgcmarea.cpy` establish them.

## Counts

| Step | Count | What it counts |
|---|---:|---|
| Logical field entries | **17** | 6 premium and payment entries plus 11 policy and request entries |
| Distinct runtime business values | **16** | 15 active entries plus 1 derived entry; `DB2-POLICYNUMBER` is declaration-only and adds no runtime value |
| Source-derived canonical column instances | **18** | 10 on `canonical.issued_policy` plus 8 on `canonical.preissued_rating` |
| Warehouse-assigned column instances | **2** | `source_system_key`, once on each relation |
| **Total canonical column instances** | **20** | 11 columns of `canonical.issued_policy` plus 9 of `canonical.preissued_rating` |

The 18 source-derived instances exceed the 16 runtime values by 2: `policy_number` and `policy_type` each appear on
**both** relations. These figures are the `counts` block of
[`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml) and the column sets of the enforced dbt
contract, and they are the same figures [`traceability-matrix.md`](traceability-matrix.md) asserts. Rationale for this
accounting: [`decision-log.md`](decision-log.md), row **D-02**.

Allocation of columns across the two relations is depicted in
**Figure 4 — dbt Transformation DAG and Field Allocation** in
[`architecture.md`](architecture.md#figure-4), which carries that figure's legend and is the single rendering
authority for it. This document draws no diagram; rationale: [`decision-log.md`](decision-log.md), row **D-64**.

## Runtime status vocabulary

The field map records status as two keys, `runtime_status` and `populated_by`. The single **runtime status** column of
the tables below combines them:

| Runtime status used here | Field map equivalent | Meaning |
|---|---|---|
| active — request-supplied | `runtime_status: active`, `populated_by: request` | The caller supplies the value in the COMMAREA; the chain carries it unchanged |
| active — chain-assigned | `runtime_status: active`, `populated_by: chain` | The chain writes the value into the COMMAREA during execution |
| derived | `runtime_status: derived`, `populated_by: derivation` | No COMMAREA item carries it; it is produced from another value |
| declaration-only | `runtime_status: declaration_only` | No statement of the chain references the declaration |
| warehouse-assigned | not a field entry | No COBOL item supplies it; see section 1.1 |

The chain assigns three COMMAREA windows: `CA-RETURN-CODE`, `CA-POLICY-NUM` and `CA-LASTCHANGED`. The two business
values among them are the policy number and the last-changed timestamp. Extraction reads the **returned** COMMAREA,
not the request record the driver supplied.

---

## 1. `canonical.issued_policy` — 11 column instances

One row per successful issued policy and source system. Grain and natural key: `(source_system_key, policy_number)`.

| # | Canonical column | Canonical type | Source COBOL item(s) | PICTURE | Locator | Runtime status | Transformation |
|---:|---|---|---|---|---|---|---|
| 1 | `source_system_key` | VARCHAR(64) NOT NULL | — | — | — | warehouse-assigned | Assigned by the extraction run and written unchanged to the landing record and both relations |
| 2 | `policy_number` | BIGINT NOT NULL | `CA-POLICY-NUM`; program intermediate `DB2-POLICYNUM-INT` | `9(10)`; `S9(9) COMP VALUE +0` | `base/src/lgcmarea.cpy:35`; `base/src/lgapdb01.cbl:117` | active — chain-assigned | Read from the returned COMMAREA; leading zeros stripped for landing; cast to `BIGINT` |
| 3 | `policy_type` | CHAR(1) NOT NULL | `DB2-POLICYTYPE` | `X` | `base/src/lgpolicy.cpy:43` | derived | Derived from `CA-REQUEST-ID` [base/src/lgcmarea.cpy:10] by the routing table of section 1.3 and verified against the policy SQL capture |
| 4 | `customer_number` | BIGINT NOT NULL | `CA-CUSTOMER-NUM`; program intermediate `DB2-CUSTOMERNUM-INT` | `9(10)`; `S9(9) COMP` | `base/src/lgcmarea.cpy:12`; `base/src/lgapdb01.cbl:90` | active — request-supplied | Passthrough; leading zeros stripped for landing; cast to `BIGINT` |
| 5 | `request_id` | VARCHAR(6) NOT NULL | `CA-REQUEST-ID` | `X(6)` | `base/src/lgcmarea.cpy:10` | active — request-supplied | Trimmed; the same value drives the policy-type derivation |
| 6 | `return_code` | CHAR(2) NOT NULL | `CA-RETURN-CODE` | `9(2)` | `base/src/lgcmarea.cpy:11` | active — chain-assigned | Carried as a two-character zero-padded string; never converted to an integer |
| 7 | `issue_date` | DATE | `CA-ISSUE-DATE`; Db2-side `DB2-ISSUEDATE` | `X(10)`; `X(10)` | `base/src/lgcmarea.cpy:38`; `base/src/lgpolicy.cpy:46` | active — request-supplied | Trimmed; an empty trimmed value lands as NULL; cast to `DATE` |
| 8 | `expiry_date` | DATE | `CA-EXPIRY-DATE`; Db2-side `DB2-EXPIRYDATE` | `X(10)`; `X(10)` | `base/src/lgcmarea.cpy:39`; `base/src/lgpolicy.cpy:47` | active — request-supplied | Trimmed; an empty trimmed value lands as NULL; cast to `DATE` |
| 9 | `last_changed` | TIMESTAMP NOT NULL | `CA-LASTCHANGED`; Db2-side `DB2-LASTCHANGED` | `X(26)`; `X(26)` | `base/src/lgcmarea.cpy:40`; `base/src/lgpolicy.cpy:48` | active — chain-assigned | Read from the returned COMMAREA; the 26-character Db2 timestamp is normalised to ISO-8601 before landing |
| 10 | `broker_id` | BIGINT | `CA-BROKERID`; Db2-side `DB2-BROKERID`; program intermediate `DB2-BROKERID-INT` | `9(10)`; `9(10)`; `S9(9) COMP` | `base/src/lgcmarea.cpy:41`; `base/src/lgpolicy.cpy:49`; `base/src/lgapdb01.cbl:91` | active — request-supplied | Passthrough; a blank window lands as NULL; leading zeros stripped; cast to `BIGINT` |
| 11 | `brokers_reference` | VARCHAR(10) | `CA-BROKERSREF`; Db2-side `DB2-BROKERSREF` | `X(10)`; `X(10)` | `base/src/lgcmarea.cpy:42`; `base/src/lgpolicy.cpy:50` | active — request-supplied | Trailing spaces trimmed (fixed-width field); an empty trimmed value lands as NULL |

Ten of the eleven columns derive from a named COBOL item. The eleventh is `source_system_key`.

### 1.1 `source_system_key` — the sole warehouse-assigned column

`source_system_key` has **no COBOL source**. It carries no COMMAREA declaration, no Db2-side declaration and no
program intermediate, and its locator cell reads `—` in both relations rather than a fabricated citation. It is the
**sole user-mandated warehouse-assigned canonical column** of this work and the only documented exception to complete
COBOL lineage; it is counted separately from the 17 logical field entries and is not one of the 16 runtime values. It
stands first in the natural key of each relation. Rationale for the exception: [`decision-log.md`](decision-log.md),
row **D-03**.

### 1.2 `policy_number` — recovered after the policy insert

`CA-POLICY-NUM` `PIC 9(10)` occupies COMMAREA bytes 19-28 [base/src/lgcmarea.cpy:35]. The caller does not supply it.
The Db2 program declares the program intermediate `DB2-POLICYNUM-INT PIC S9(9) COMP VALUE +0`
[base/src/lgapdb01.cbl:117], loads it with the identity of the row just inserted through
`SET :DB2-POLICYNUM-INT = IDENTITY_VAL_LOCAL()` [base/src/lgapdb01.cbl:308-310], and then executes
`MOVE DB2-POLICYNUM-INT TO CA-POLICY-NUM` [base/src/lgapdb01.cbl:311] — the recovery block at
[base/src/lgapdb01.cbl:307-311]. The value therefore exists only in the returned COMMAREA, which is the record
extraction reads. The same value identifies `canonical.preissued_rating`, giving the first of the two duplicated
column instances.

### 1.3 `policy_type` — derived, and not a COMMAREA field

**`policy_type` is not a COMMAREA field.** No item of `base/src/lgcmarea.cpy` carries it. Its Db2-side declaration is
`DB2-POLICYTYPE PIC X` [base/src/lgpolicy.cpy:43], set by the request-routing `EVALUATE`
[base/src/lgapdb01.cbl:184-207] and supplied to the POLICY insert as a host variable
[base/src/lgapdb01.cbl:283]:

| `CA-REQUEST-ID` | `DB2-POLICYTYPE` | Locator of the move |
|---|---|---|
| `01AEND` | `E` | `base/src/lgapdb01.cbl:188` |
| `01AHOU` | `H` | `base/src/lgapdb01.cbl:192` |
| `01AMOT` | `M` | `base/src/lgapdb01.cbl:196` |
| `01ACOM` | `C` | `base/src/lgapdb01.cbl:200` |

The VSAM program derives the same letter independently as `Move CA-Request-ID(4:1) To WF-Request-ID`
[base/src/lgapvs01.cbl:99], where `WF-Request-ID` is the leading `X(1)` of the 21-byte composite key
`WF-Policy-Key` [base/src/lgapvs01.cbl:26-29] inside the 64-byte record `WF-Policy-Info`
[base/src/lgapvs01.cbl:25-30]. That derivation corroborates the letter; no canonical column derives from
`base/src/lgapvs01.cbl`. Extraction reproduces the routing table above and the comparison gate verifies the derived
value against the policy SQL capture. Rationale for deriving rather than reading this column:
[`decision-log.md`](decision-log.md), row **D-50**.

### 1.4 `return_code` — retained as a column, filtered in the mart

`CA-RETURN-CODE` `PIC 9(2)` occupies COMMAREA bytes 7-8 [base/src/lgcmarea.cpy:11]. Both the entry program and the
Db2 program initialise it with `MOVE '00' TO CA-RETURN-CODE` [base/src/lgapol01.cbl:105;
base/src/lgapdb01.cbl:172], and each outcome path then sets its own value — `00`, `70`, `80`, `90`, `98` or `99`
[base/src/lgapol01.cbl:108-116; base/src/lgapdb01.cbl:204,211,290-305; base/src/lgapvs01.cbl:142-147].

The canonical models filter to `return_code = '00'`: the predicate stands at the foot of
[`../dbt/genapp_rqi/models/marts/canonical/canonical_issued_policy.sql`](../dbt/genapp_rqi/models/marts/canonical/canonical_issued_policy.sql)
and of
[`../dbt/genapp_rqi/models/marts/canonical/canonical_preissued_rating.sql`](../dbt/genapp_rqi/models/marts/canonical/canonical_preissued_rating.sql).
The raw, staging and intermediate layers apply no such predicate: each carries `return_code` unfiltered so a code
other than `00` remains available for failure analysis wherever one is present. Extraction itself admits only a
record whose returned code is `00`, so the mart predicate acts as a second guard over the landing contract.
Rationale: [`decision-log.md`](decision-log.md), row **D-51**.

### 1.5 `last_changed` — read back from the inserted row

`CA-LASTCHANGED` `PIC X(26)` occupies COMMAREA bytes 49-74 [base/src/lgcmarea.cpy:40]; its Db2-side counterpart is
`DB2-LASTCHANGED PIC X(26)` [base/src/lgpolicy.cpy:48]. The POLICY insert supplies `CURRENT TIMESTAMP` for the
`LASTCHANGED` column [base/src/lgapdb01.cbl:284], and the chain then reads the stored value back into the COMMAREA:

```text
SELECT LASTCHANGED
  INTO :CA-LASTCHANGED
  FROM POLICY
 WHERE POLICYNUMBER = :DB2-POLICYNUM-INT
```

[base/src/lgapdb01.cbl:315-321]. The returned 26-character value is normalised to ISO-8601 before landing; rationale:
[`decision-log.md`](decision-log.md), row **D-53**. The same item is consumed a second time inside the chain as the
`RequestDate` value of the COMMERCIAL insert [base/src/lgapdb01.cbl:525], which is a use of the value rather than a
second source for it: `canonical.issued_policy.last_changed` derives from the returned COMMAREA window alone.

### 1.6 Insert-time binding of the remaining columns

Each request-supplied column of this relation reaches the POLICY insert as a host variable, one per value:

| Canonical column | Host variable bound in the POLICY insert | Set at | Bound at |
|---|---|---|---|
| `customer_number` | `:DB2-CUSTOMERNUM-INT` | `base/src/lgapdb01.cbl:176` | `base/src/lgapdb01.cbl:280` |
| `issue_date` | `:CA-ISSUE-DATE` | — (passed straight from the COMMAREA) | `base/src/lgapdb01.cbl:281` |
| `expiry_date` | `:CA-EXPIRY-DATE` | — (passed straight from the COMMAREA) | `base/src/lgapdb01.cbl:282` |
| `policy_type` | `:DB2-POLICYTYPE` | `base/src/lgapdb01.cbl:188,192,196,200` | `base/src/lgapdb01.cbl:283` |
| `broker_id` | `:DB2-BROKERID-INT` | `base/src/lgapdb01.cbl:264` | `base/src/lgapdb01.cbl:285` |
| `brokers_reference` | `:CA-BROKERSREF` | — (passed straight from the COMMAREA) | `base/src/lgapdb01.cbl:286` |

`request_id` and `return_code` are not bound to the POLICY insert at all: the first is the routing discriminator
[base/src/lgapdb01.cbl:184-207] and the second is the outcome the chain reports in the COMMAREA. Both are read from
the returned record.

---

## 2. `canonical.preissued_rating` — 9 column instances

One row per successful issued policy and source system. Grain and natural key: `(source_system_key, policy_number)`,
the same key as `canonical.issued_policy`.

### 2.1 The three-tier amount lineage

Each of the six amounts is declared three times in the source, and the three declarations are not
interchangeable. Every amount row of the table below therefore names all three tiers:

| Tier | What it is | Where it is declared |
|---|---|---|
| **Tier 1 — active runtime carrier** | The COMMAREA item the caller populates and the chain reads | `base/src/lgcmarea.cpy` |
| **Tier 2 — Db2-side counterpart, declaration-only** | The Db2-side declaration of the same concept, in DISPLAY form | `base/src/lgpolicy.cpy` |
| **Tier 3 — actual runtime intermediate** | The separate **binary** `PIC S9(9) COMP` host variable named in the INSERT's `VALUES` list | `base/src/lgapdb01.cbl` |

**Verified fact:** the six Tier 2 DISPLAY declarations — `DB2-PAYMENT`, `DB2-M-PREMIUM`, `DB2-B-FirePremium`,
`DB2-B-CrimePremium`, `DB2-B-FloodPremium` and `DB2-B-WeatherPremium` — have **zero exact-name references** in
`base/src/lgapdb01.cbl`. They are the Db2-side declaration of the concept, not the runtime host variable. The host
variable each insert actually binds is the Tier 3 item.

### 2.2 Column lineage

| # | Canonical column | Canonical type | Tier 1 — active runtime carrier | Tier 2 — Db2-side counterpart | Tier 3 — runtime intermediate | Runtime status | Transformation |
|---:|---|---|---|---|---|---|---|
| 1 | `source_system_key` | VARCHAR(64) NOT NULL | — | — | — | warehouse-assigned | Assigned by the extraction run; the second of the two warehouse-assigned instances |
| 2 | `policy_number` | BIGINT NOT NULL | `CA-POLICY-NUM` `9(10)` bytes 19-28 [base/src/lgcmarea.cpy:35] | — (none; `DB2-POLICYNUMBER` is a separate declaration-only entry, section 3.1) | `DB2-POLICYNUM-INT` `S9(9) COMP VALUE +0` [base/src/lgapdb01.cbl:117], loaded [base/src/lgapdb01.cbl:308-310], moved into the COMMAREA [base/src/lgapdb01.cbl:311] | active — chain-assigned | Read from the returned COMMAREA; leading zeros stripped for landing; cast to `BIGINT` |
| 3 | `policy_type` | CHAR(1) NOT NULL | — (not a COMMAREA field) | `DB2-POLICYTYPE` `X` [base/src/lgpolicy.cpy:43] — active, set by the routing `EVALUATE` [base/src/lgapdb01.cbl:184-207] | — (the `EVALUATE` sets the Db2-side item directly; no separate intermediate) | derived | Derived from `CA-REQUEST-ID` by the routing table of section 1.3 and verified against the policy SQL capture |
| 4 | `payment_amount` | DECIMAL(8,2) | `CA-PAYMENT` `9(6)` bytes 95-100 [base/src/lgcmarea.cpy:43] | `DB2-PAYMENT` `9(6)` [base/src/lgpolicy.cpy:51] — **declaration-only** | `DB2-PAYMENT-INT` `S9(9) COMP` [base/src/lgapdb01.cbl:92], set by `MOVE CA-PAYMENT TO DB2-PAYMENT-INT` [base/src/lgapdb01.cbl:265], bound [base/src/lgapdb01.cbl:287] | active — request-supplied | **Passthrough** to decimal scale 2 — no formula; leading zeros stripped for landing |
| 5 | `motor_premium_amount` | DECIMAL(8,2) | `CA-M-PREMIUM` `9(6)` bytes 166-171 [base/src/lgcmarea.cpy:73] | `DB2-M-PREMIUM` `9(6)` [base/src/lgpolicy.cpy:80] — **declaration-only** | `DB2-M-PREMIUM-int` `S9(9) COMP` [base/src/lgapdb01.cbl:100], set by `MOVE CA-M-PREMIUM TO DB2-M-PREMIUM-INT` [base/src/lgapdb01.cbl:445], bound [base/src/lgapdb01.cbl:469] | active — request-supplied | **Passthrough** to decimal scale 2 — no formula; populated for policy type `M` only, NULL otherwise |
| 6 | `fire_premium_amount` | DECIMAL(10,2) | `CA-B-FirePremium` `9(8)` bytes 900-907 [base/src/lgcmarea.cpy:85] | `DB2-B-FirePremium` `9(8)` [base/src/lgpolicy.cpy:91] — **declaration-only** | `DB2-B-FirePremium-Int` `S9(9) COMP` [base/src/lgapdb01.cbl:103], set [base/src/lgapdb01.cbl:489], bound [base/src/lgapdb01.cbl:535] | active — request-supplied | **Passthrough** to decimal scale 2 — no formula; populated for policy type `C` only, NULL otherwise |
| 7 | `crime_premium_amount` | DECIMAL(10,2) | `CA-B-CrimePremium` `9(8)` bytes 912-919 [base/src/lgcmarea.cpy:87] | `DB2-B-CrimePremium` `9(8)` [base/src/lgpolicy.cpy:93] — **declaration-only** | `DB2-B-CrimePremium-Int` `S9(9) COMP` [base/src/lgapdb01.cbl:105], set [base/src/lgapdb01.cbl:491], bound [base/src/lgapdb01.cbl:537] | active — request-supplied | **Passthrough** to decimal scale 2 — no formula; populated for policy type `C` only, NULL otherwise |
| 8 | `flood_premium_amount` | DECIMAL(10,2) | `CA-B-FloodPremium` `9(8)` bytes 924-931 [base/src/lgcmarea.cpy:89] | `DB2-B-FloodPremium` `9(8)` [base/src/lgpolicy.cpy:95] — **declaration-only** | `DB2-B-FloodPremium-Int` `S9(9) COMP` [base/src/lgapdb01.cbl:107], set [base/src/lgapdb01.cbl:493], bound [base/src/lgapdb01.cbl:539] | active — request-supplied | **Passthrough** to decimal scale 2 — no formula; populated for policy type `C` only, NULL otherwise |
| 9 | `weather_premium_amount` | DECIMAL(10,2) | `CA-B-WeatherPremium` `9(8)` bytes 936-943 [base/src/lgcmarea.cpy:91] | `DB2-B-WeatherPremium` `9(8)` [base/src/lgpolicy.cpy:97] — **declaration-only** | `DB2-B-WeatherPremium-Int` `S9(9) COMP` [base/src/lgapdb01.cbl:109], set [base/src/lgapdb01.cbl:495], bound [base/src/lgapdb01.cbl:541] | active — request-supplied | **Passthrough** to decimal scale 2 — no formula; populated for policy type `C` only, NULL otherwise |

Eight of the nine columns derive from a named COBOL item. The ninth is `source_system_key`, whose locator cells read
`—` exactly as in section 1: no COBOL source, warehouse-assigned, rationale in
[`decision-log.md`](decision-log.md), row **D-03**.

`policy_number` and `policy_type` carry the identical lineage they carry on `canonical.issued_policy` — sections 1.2
and 1.3. These two are the duplicated instances that make 16 runtime values become 18 source-derived column
instances.

The six amounts are typed `DECIMAL` with scale 2 although no source declaration carries an implied decimal; rationale:
[`decision-log.md`](decision-log.md), row **D-55**. The comparison contract for the six amounts is an absolute delta
of at most 0.01, with any non-zero in-tolerance delta reported as an anomaly; rationale:
[`decision-log.md`](decision-log.md), row **D-04**.

### 2.3 Product-specific NULL pattern

Which amount columns carry a value is decided by `policy_type`, never by the content of a window:

| `policy_type` | `payment_amount` | `motor_premium_amount` | The four commercial premium columns |
|---|---|---|---|
| `M` (motor) | value | value | NULL |
| `C` (commercial) | value | NULL | value in each of the four |
| `E` (endowment), `H` (house) | value | NULL | NULL |

An inapplicable premium is **NULL, never zero**. The product overlays redefine the same COMMAREA bytes from byte 101
[base/src/lgcmarea.cpy:44-94], so an item of an unselected overlay can read as non-blank content placed by the
selected overlay; a blank or zero window is therefore not the test for an inapplicable premium and the policy type is.
The pattern is asserted by
[`../dbt/genapp_rqi/tests/assert_product_premium_nullability.sql`](../dbt/genapp_rqi/tests/assert_product_premium_nullability.sql).
Rationale: [`decision-log.md`](decision-log.md), row **D-54**.

### 2.4 No formula, at field level

Every one of the six amounts reaches its Db2 host variable through a plain `MOVE` and is inserted unchanged. The
statement census over the three programs of the chain — `base/src/lgapol01.cbl`, `base/src/lgapdb01.cbl` and
`base/src/lgapvs01.cbl` — is:

| Statement | Count | Locators |
|---|---:|---|
| `COMPUTE` | **0** | — |
| `MULTIPLY` | **0** | — |
| `DIVIDE` | **0** | — |
| `ADD` | 6 | base/src/lgapol01.cbl:109; base/src/lgapdb01.cbl:182,187,191,195,199 |
| `SUBTRACT` | 1 | base/src/lgapdb01.cbl:339 |

All seven arithmetic statements operate on length values only: the 28-byte header constant `WS-CA-HEADER-LEN`
[base/src/lgapol01.cbl:59; base/src/lgapdb01.cbl:65], the per-product full-record constants
[base/src/lgpolicy.cpy:24-27] and the received length `EIBCALEN`. None touches an amount. The six amount moves stand at
[base/src/lgapdb01.cbl:265,445,489,491,493,495]. No `COMP-3` declaration appears in either copybook or in any of the
three programs.

**No rating formula, rating factor or derived column is inferred, constructed or backfilled here.** No such column
exists on either canonical relation, and the absence of executable rating logic is a measured finding of this work
rather than an omission. Rationale: [`decision-log.md`](decision-log.md), row **D-11**.


---

## 3. Declaration-only entries and excluded items

These declarations are in scope, carry a locator and receive **no canonical column**. They are listed individually so
that their absence from sections 1 and 2 is deliberate and visible rather than an omission.

### 3.1 `DB2-POLICYNUMBER` — declaration-only

| Item | PICTURE | Locator | Runtime status | Target |
|---|---|---|---|---|
| `DB2-POLICYNUMBER` | `9(10)` | `base/src/lgpolicy.cpy:44` | **declaration-only** | none |

**Verified:** `DB2-POLICYNUMBER` has **zero references anywhere in `base/src/lgapdb01.cbl`**. The POLICY insert names
`POLICYNUMBER` in its column list [base/src/lgapdb01.cbl:270] and supplies the literal `DEFAULT` as its value
[base/src/lgapdb01.cbl:279]; the recovered key then travels through the separate binary intermediate
`DB2-POLICYNUM-INT` into `CA-POLICY-NUM` [base/src/lgapdb01.cbl:307-311]. This is the one entry that makes 17 logical
entries resolve to 16 runtime business values. It receives this lineage entry and no column. Rationale:
[`decision-log.md`](decision-log.md), row **D-02**.

### 3.2 The six Tier 2 amount declarations — declaration-only in this chain

Established in section 2.1 and repeated here as lineage entries in their own right:

| Item | PICTURE | Locator | Runtime status | Target |
|---|---|---|---|---|
| `DB2-PAYMENT` | `9(6)` | `base/src/lgpolicy.cpy:51` | declaration-only | none; the Tier 3 intermediate carries the value |
| `DB2-M-PREMIUM` | `9(6)` | `base/src/lgpolicy.cpy:80` | declaration-only | none; the Tier 3 intermediate carries the value |
| `DB2-B-FirePremium` | `9(8)` | `base/src/lgpolicy.cpy:91` | declaration-only | none; the Tier 3 intermediate carries the value |
| `DB2-B-CrimePremium` | `9(8)` | `base/src/lgpolicy.cpy:93` | declaration-only | none; the Tier 3 intermediate carries the value |
| `DB2-B-FloodPremium` | `9(8)` | `base/src/lgpolicy.cpy:95` | declaration-only | none; the Tier 3 intermediate carries the value |
| `DB2-B-WeatherPremium` | `9(8)` | `base/src/lgpolicy.cpy:97` | declaration-only | none; the Tier 3 intermediate carries the value |

Each of the six is the Db2-side declaration of an amount concept that **is** projected: the canonical column derives
from its Tier 1 COMMAREA carrier and travels through its Tier 3 intermediate. The declaration itself is referenced by
no statement of the chain.

### 3.3 Excluded peril codes

The four commercial peril fields are `PIC 9(4)` **codes**, not amounts. The requested amount fields are the adjacent
`PIC 9(8)` premium items at `base/src/lgcmarea.cpy:85,87,89,91`, which section 2.2 projects. Each peril field has a
program intermediate and a move, and neither maps to a canonical column:

| Item | PICTURE | Bytes | Locator | Db2-side counterpart | Program intermediate | Move | Bound at | Target |
|---|---|---|---|---|---|---|---|---|
| `CA-B-FirePeril` | `9(4)` | 896-899 | `base/src/lgcmarea.cpy:84` | `DB2-B-FirePeril` [base/src/lgpolicy.cpy:90] | `DB2-B-FirePeril-Int` `S9(4) COMP` [base/src/lgapdb01.cbl:102] | `base/src/lgapdb01.cbl:488` | `base/src/lgapdb01.cbl:534` | none |
| `CA-B-CrimePeril` | `9(4)` | 908-911 | `base/src/lgcmarea.cpy:86` | `DB2-B-CrimePeril` [base/src/lgpolicy.cpy:92] | `DB2-B-CrimePeril-Int` `S9(4) COMP` [base/src/lgapdb01.cbl:104] | `base/src/lgapdb01.cbl:490` | `base/src/lgapdb01.cbl:536` | none |
| `CA-B-FloodPeril` | `9(4)` | 920-923 | `base/src/lgcmarea.cpy:88` | `DB2-B-FloodPeril` [base/src/lgpolicy.cpy:94] | `DB2-B-FloodPeril-Int` `S9(4) COMP` [base/src/lgapdb01.cbl:106] | `base/src/lgapdb01.cbl:492` | `base/src/lgapdb01.cbl:538` | none |
| `CA-B-WeatherPeril` | `9(4)` | 932-935 | `base/src/lgcmarea.cpy:90` | `DB2-B-WeatherPeril` [base/src/lgpolicy.cpy:96] | `DB2-B-WeatherPeril-Int` `S9(4) COMP` [base/src/lgapdb01.cbl:108] | `base/src/lgapdb01.cbl:494` | `base/src/lgapdb01.cbl:540` | none |

Extraction never reads a peril window. Rationale for the exclusion: [`decision-log.md`](decision-log.md), row
**D-12**. Every remaining in-scope declaration that receives no target column — the other overlay items, the
redefined group declarations and the fill items — is enumerated in
[`../extraction/extraction-spec.md`](../extraction/extraction-spec.md) section 3.4 and in the `excluded` and
`out_of_scope_overlays` blocks of [`../extraction/copybook_field_map.yml`](../extraction/copybook_field_map.yml).

---

## 4. Landing-record cross-walk

One extraction produces one landing record: a single JSON object carrying exactly **17 keys** — the 16 runtime
business values plus `source_system_key` — in the key order of
[`../landing/landing-schema.json`](../landing/landing-schema.json). That schema requires all 17 and admits no
additional key.

| # | Landing key | Landed JSON type | Canonical column instance(s) | Canonical type |
|---:|---|---|---|---|
| 1 | `source_system_key` | string | `issued_policy.source_system_key`, `preissued_rating.source_system_key` | VARCHAR(64) NOT NULL |
| 2 | `policy_number` | string | `issued_policy.policy_number`, `preissued_rating.policy_number` | BIGINT NOT NULL |
| 3 | `policy_type` | string | `issued_policy.policy_type`, `preissued_rating.policy_type` | CHAR(1) NOT NULL |
| 4 | `customer_number` | string | `issued_policy.customer_number` | BIGINT NOT NULL |
| 5 | `request_id` | string | `issued_policy.request_id` | VARCHAR(6) NOT NULL |
| 6 | `return_code` | string | `issued_policy.return_code` | CHAR(2) NOT NULL |
| 7 | `issue_date` | string or null | `issued_policy.issue_date` | DATE |
| 8 | `expiry_date` | string or null | `issued_policy.expiry_date` | DATE |
| 9 | `last_changed` | string | `issued_policy.last_changed` | TIMESTAMP NOT NULL |
| 10 | `broker_id` | string or null | `issued_policy.broker_id` | BIGINT |
| 11 | `brokers_reference` | string or null | `issued_policy.brokers_reference` | VARCHAR(10) |
| 12 | `payment_amount` | string or null | `preissued_rating.payment_amount` | DECIMAL(8,2) |
| 13 | `motor_premium_amount` | string or null | `preissued_rating.motor_premium_amount` | DECIMAL(8,2) |
| 14 | `fire_premium_amount` | string or null | `preissued_rating.fire_premium_amount` | DECIMAL(10,2) |
| 15 | `crime_premium_amount` | string or null | `preissued_rating.crime_premium_amount` | DECIMAL(10,2) |
| 16 | `flood_premium_amount` | string or null | `preissued_rating.flood_premium_amount` | DECIMAL(10,2) |
| 17 | `weather_premium_amount` | string or null | `preissued_rating.weather_premium_amount` | DECIMAL(10,2) |

Three keys map to two column instances each — `source_system_key`, `policy_number` and `policy_type` — and the
remaining 14 map to one each, giving 17 keys and 20 canonical column instances.

**Every landed value is a JSON string or null, never a number**, and every column of
`raw.genapp_policy_issue` is `VARCHAR`, nullable. All typing happens afterwards, in the dbt intermediate model.
The type column of the lineage tables in sections 1 and 2 therefore describes the **canonical** type, not the landed
one. Rationale for landing every field as a string: [`decision-log.md`](decision-log.md), row **D-52**; for the
all-`VARCHAR` raw relation: row **D-41**.

One nuance of the character columns, stated without argument: the enforced dbt contract declares the five character
columns with their logical widths — `varchar(64)` for `source_system_key`, `char(1)` for `policy_type`, `varchar(6)`
for `request_id`, `char(2)` for `return_code` and `varchar(10)` for `brokers_reference` — and contract enforcement of
the declared **width** reaches Amazon Redshift only; DuckDB accepts each spelling, collapses it to `VARCHAR` and
reports no maximum length. The same logical widths are stated in the contract's column descriptions and asserted from
the value side by the project's own singular tests. Rationale: [`decision-log.md`](decision-log.md), row **D-49**.

---

## 5. Coverage assertion

| Relation | Total column instances | Source-derived | Warehouse-assigned | Unmapped |
|---|---:|---:|---:|---:|
| `canonical.issued_policy` | 11 | 10 | 1 | **0** |
| `canonical.preissued_rating` | 9 | 8 | 1 | **0** |
| **Total** | **20** | **18** | **2** | **0** |

**11 + 9 = 20 canonical column instances are documented above.** **18** are source-derived and each carries a named
COBOL item, its PICTURE and a `path:line` locator. **2** are warehouse-assigned — `source_system_key` on each
relation — and each carries `—` in place of a locator, labelled warehouse-assigned in its runtime status and
attributed to the user requirement. **0** are unmapped.

The canonical schema holds exactly these two relations. No third relation, and no audit, provenance, surrogate-key,
hash, load-timestamp, peril-code, rating-factor or commission column, stands on either of them; the enforced contract
[`../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml`](../dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml)
is the single declaration of both column sets. These are the same figures
[`traceability-matrix.md`](traceability-matrix.md) asserts, and they must agree exactly.
