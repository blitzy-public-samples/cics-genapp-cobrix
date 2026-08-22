# Extraction Specification — GenApp Policy-Issue Canonical Warehouse Bridge

This document specifies what is extracted from one executed GenApp Policy-Issue chain and where every extracted
value lands. It records the interface record and its byte grid, the point in the chain at which extraction reads,
the seventeen logical field entries the request names and how they resolve to sixteen runtime business values, the
measured finding that the chain contains no premium or rating formula, the two canonical relations and their full
column sets, the landing contract, and the sample and length facts that govern a run. It is the human-readable
counterpart of [`copybook_field_map.yml`](copybook_field_map.yml), which is the machine authority: where a reader
needs an offset, a type, a runtime status or a column name in a form a tool consumes, that file holds it, and every
value stated here is the value that file records.

> **Status — validated against local substitute, not AWS.** Every result this specification refers to was produced
> on the local-substitute branch: a moto S3 endpoint in place of Amazon S3 and DuckDB in place of Amazon Redshift.
> The formal AWS diff requirement is **OPEN** and this has not yet happened. Nothing in this document closes it,
> and no statement here may be read as satisfying it. Production-grade validation requires re-running the
> same dbt models unmodified against real S3 and Amazon Redshift once access is granted. Run results, versions and
> dispositions are recorded in [`../validation/validation-evidence.md`](../validation/validation-evidence.md),
> with the retained per-run captures and logs under [`../validation/artifacts/`](../validation/artifacts/).

## Authorities

This specification is derived from three of the five read-only source artifacts, which are unchanged by this work:

| Authority | Lines | What this specification takes from it |
|---|---:|---|
| `base/src/lgcmarea.cpy` | 103 | COMMAREA declarations, byte layout, the six amount items and the product overlays |
| `base/src/lgpolicy.cpy` | 107 | Length constants and the Db2-side field declarations |
| `base/src/lgapdb01.cbl` | 595 | Request routing, host-variable moves, the inserts, identity and timestamp recovery, and the return codes |

The statement census of section 4.1 is a measurement over all three programs of the chain, so it additionally cites
`base/src/lgapol01.cbl` (169 lines) and `base/src/lgapvs01.cbl` (188 lines); both are among the five read-only
source artifacts of this work. No other pre-existing repository file is cited as evidence, and no claim about the
existing system rests on anything outside those five files.

## Companion artifacts

| Artifact | Role |
|---|---|
| [`copybook_field_map.yml`](copybook_field_map.yml) | Machine authority for every offset, length, PICTURE, runtime status, target column and transformation |
| [`../docs/field-level-lineage.md`](../docs/field-level-lineage.md) | Canonical column to source declaration and locator, column by column |
| [`../docs/traceability-matrix.md`](../docs/traceability-matrix.md) | Forward and reverse coverage of every source construct and every created artifact |
| [`../docs/decision-log.md`](../docs/decision-log.md) | The single source of rationale, alternatives and risk for every decision named below |
| [`../docs/architecture.md`](../docs/architecture.md) | The single rendering authority for every figure; this document draws none and cites figures by name |

This document carries what each field is and how it is treated. Every decision it states an outcome for defers its
rationale to a row of the decision log, cited by row ID; no rationale is restated or re-argued here.

## Citation convention

Every locator is written `path:line` or `path:first-last`, resolving to one of the three authorities above — for
example `base/src/lgcmarea.cpy:43` is the `CA-PAYMENT` declaration. Within a table whose rows all cite one file, the
short form `:43` is used for that file and the full path appears in the column heading.

---

## 1. The interface record

The interface record shared by every program of the named chain is the 32,500-character `DFHCOMMAREA` declared by
`base/src/lgcmarea.cpy:10-103`. The copybook has no level-01 item of its own: its first declaration is at level 03
on `base/src/lgcmarea.cpy:10`, and each program supplies the enclosing group. Byte 1 of the grid below is the first
byte of that record.

The three header items occupy bytes 1-18 and are declared for every request type. `CA-REQUEST-SPECIFIC`
(`base/src/lgcmarea.cpy:13`) covers bytes 19-32500 and is redefined by three views; the view this work reads is
`CA-POLICY-REQUEST REDEFINES CA-REQUEST-SPECIFIC` at `base/src/lgcmarea.cpy:34`, which starts at byte 19.

### 1.1 Header — bytes 1-18, `base/src/lgcmarea.cpy`

| Item | PICTURE | Bytes | Length | Kind | Locator |
|---|---|---|---:|---|---|
| `CA-REQUEST-ID` | `X(6)` | 1-6 | 6 | alphanumeric | `:10` |
| `CA-RETURN-CODE` | `9(2)` | 7-8 | 2 | numeric display | `:11` |
| `CA-CUSTOMER-NUM` | `9(10)` | 9-18 | 10 | numeric display | `:12` |
| `CA-REQUEST-SPECIFIC` | `X(32482)` | 19-32500 | 32482 | alphanumeric | `:13` |

The length constant the chain applies to this region is `WS-CA-HEADER-LEN PIC S9(4) COMP VALUE +28`, declared at
`base/src/lgapdb01.cbl:65` and added to the required-length accumulator at `base/src/lgapdb01.cbl:182`. Its 28 bytes
cover the 18-byte header prefix above together with the 10-byte `CA-POLICY-NUM` that follows it, so bytes 1-28.

### 1.2 Policy-request view — bytes 19-32500, `base/src/lgcmarea.cpy`

| Item | PICTURE | Bytes | Length | Kind | Locator |
|---|---|---|---:|---|---|
| `CA-POLICY-NUM` | `9(10)` | 19-28 | 10 | numeric display | `:35` |
| `CA-ISSUE-DATE` | `X(10)` | 29-38 | 10 | alphanumeric | `:38` |
| `CA-EXPIRY-DATE` | `X(10)` | 39-48 | 10 | alphanumeric | `:39` |
| `CA-LASTCHANGED` | `X(26)` | 49-74 | 26 | alphanumeric | `:40` |
| `CA-BROKERID` | `9(10)` | 75-84 | 10 | numeric display | `:41` |
| `CA-BROKERSREF` | `X(10)` | 85-94 | 10 | alphanumeric | `:42` |
| `CA-PAYMENT` | `9(6)` | 95-100 | 6 | numeric display | `:43` |
| `CA-POLICY-SPECIFIC` | `X(32400)` | 101-32500 | 32400 | alphanumeric | `:44` |

`CA-ISSUE-DATE` through `CA-PAYMENT` are the members of the `CA-POLICY-COMMON` group declared at
`base/src/lgcmarea.cpy:37`, which spans bytes 29-100. `CA-POLICY-SPECIFIC` is redefined by five product overlays,
all starting at byte 101; the two this work exercises follow.

### 1.3 Motor overlay — `CA-MOTOR`, 77 bytes, bytes 101-177, `base/src/lgcmarea.cpy:65-75`

| Item | PICTURE | Bytes | Length | Kind | Locator |
|---|---|---|---:|---|---|
| `CA-M-MAKE` | `X(15)` | 101-115 | 15 | alphanumeric | `:66` |
| `CA-M-MODEL` | `X(15)` | 116-130 | 15 | alphanumeric | `:67` |
| `CA-M-VALUE` | `9(6)` | 131-136 | 6 | numeric display | `:68` |
| `CA-M-REGNUMBER` | `X(7)` | 137-143 | 7 | alphanumeric | `:69` |
| `CA-M-COLOUR` | `X(8)` | 144-151 | 8 | alphanumeric | `:70` |
| `CA-M-CC` | `9(4)` | 152-155 | 4 | numeric display | `:71` |
| `CA-M-MANUFACTURED` | `X(10)` | 156-165 | 10 | alphanumeric | `:72` |
| **`CA-M-PREMIUM`** | `9(6)` | **166-171** | 6 | numeric display | `:73` |
| `CA-M-ACCIDENTS` | `9(6)` | 172-177 | 6 | numeric display | `:74` |
| `CA-M-FILLER` | `X(32323)` | 178-32500 | 32323 | alphanumeric | `:75` |

### 1.4 Commercial overlay — `CA-COMMERCIAL`, 1102 bytes, bytes 101-1202, `base/src/lgcmarea.cpy:77-94`

| Item | PICTURE | Bytes | Length | Kind | Locator |
|---|---|---|---:|---|---|
| `CA-B-Address` | `X(255)` | 101-355 | 255 | alphanumeric | `:78` |
| `CA-B-Postcode` | `X(8)` | 356-363 | 8 | alphanumeric | `:79` |
| `CA-B-Latitude` | `X(11)` | 364-374 | 11 | alphanumeric | `:80` |
| `CA-B-Longitude` | `X(11)` | 375-385 | 11 | alphanumeric | `:81` |
| `CA-B-Customer` | `X(255)` | 386-640 | 255 | alphanumeric | `:82` |
| `CA-B-PropType` | `X(255)` | 641-895 | 255 | alphanumeric | `:83` |
| `CA-B-FirePeril` | `9(4)` | 896-899 | 4 | numeric display | `:84` |
| **`CA-B-FirePremium`** | `9(8)` | **900-907** | 8 | numeric display | `:85` |
| `CA-B-CrimePeril` | `9(4)` | 908-911 | 4 | numeric display | `:86` |
| **`CA-B-CrimePremium`** | `9(8)` | **912-919** | 8 | numeric display | `:87` |
| `CA-B-FloodPeril` | `9(4)` | 920-923 | 4 | numeric display | `:88` |
| **`CA-B-FloodPremium`** | `9(8)` | **924-931** | 8 | numeric display | `:89` |
| `CA-B-WeatherPeril` | `9(4)` | 932-935 | 4 | numeric display | `:90` |
| **`CA-B-WeatherPremium`** | `9(8)` | **936-943** | 8 | numeric display | `:91` |
| `CA-B-Status` | `9(4)` | 944-947 | 4 | numeric display | `:92` |
| `CA-B-RejectReason` | `X(255)` | 948-1202 | 255 | alphanumeric | `:93` |
| `CA-B-FILLER` | `X(31298)` | 1203-32500 | 31298 | alphanumeric | `:94` |

The overlays redefine the same bytes from offset 101 onward. An item of an overlay a request did not select reads as
content the selected overlay placed there. The applicability of a product premium is therefore decided by the policy
type alone, and blank or zero window content is not the test for an inapplicable premium. Section 5.2 states the
resulting NULL pattern and section 6.3 states how extraction applies it.

---

## 2. The extraction point

Extraction reads the **returned** COMMAREA: the record as it stands after the chain has completed. Two of the values
it lands are written by the chain itself and are absent from the record a caller supplies:

| Value | Mechanism observed in `base/src/lgapdb01.cbl` | Locator |
|---|---|---|
| `CA-POLICY-NUM` | The POLICY insert supplies `DEFAULT` for `POLICYNUMBER`; the assigned key is then loaded by `SET :DB2-POLICYNUM-INT = IDENTITY_VAL_LOCAL()` and `MOVE DB2-POLICYNUM-INT TO CA-POLICY-NUM` | `:279`, `:308-310`, `:311` |
| `CA-LASTCHANGED` | The POLICY insert writes `CURRENT TIMESTAMP`; the assigned value is read back by `SELECT LASTCHANGED INTO :CA-LASTCHANGED FROM POLICY WHERE POLICYNUMBER = :DB2-POLICYNUM-INT` | `:284`, `:316-321` |

Both statements follow the policy insert. `CA-RETURN-CODE` is likewise a chain-written value: it is initialised by
`MOVE '00' TO CA-RETURN-CODE` at `base/src/lgapdb01.cbl:172` and is set again by the outcome paths of section 2.1.
Every other landed value is carried in from the request and is read from the same returned record.

### 2.1 Observed return codes

The code is held in `CA-RETURN-CODE PIC 9(2)` at bytes 7-8 (`base/src/lgcmarea.cpy:11`). The programs compare it
against character literals, so it is carried through landing and the warehouse as a two-character zero-padded
string and is never converted to an integer.

| Code | Observed meaning | Locators |
|---|---|---|
| `00` | Success — the policy insert returned SQLCODE 0 | set at `base/src/lgapdb01.cbl:293`, checked at `:292` |
| `70` | The policy insert returned SQLCODE -530 | set at `base/src/lgapdb01.cbl:296`, checked at `:295`, returns at `:298` |
| `80` | The VSAM write response was not normal | set by `LGAPVS01` |
| `90` | SQL failure; the four product-subtype inserts also abend with code `LGSQ` | set at `base/src/lgapdb01.cbl:301`, `:390`, `:428`, `:474`, `:548`; abends at `:393`, `:431`, `:477`, `:551` |
| `98` | The COMMAREA is shorter than the required length | `IF EIBCALEN IS LESS THAN WS-REQUIRED-CA-LEN` at `base/src/lgapdb01.cbl:210-212` |
| `99` | Unsupported request id | set at `base/src/lgapdb01.cbl:204`, returns at `:205`; the product dispatch sets it again at `:239` |

Only `00` denotes a successfully issued policy, and only a record returning `00` is landed; the outcome for every
other code is recorded in the harness captures and driver logs rather than in the warehouse. Rationale:
[`../docs/decision-log.md`](../docs/decision-log.md), row **D-51**.

---

## 3. Field reconciliation — 17 logical entries, 16 runtime values, 18 column instances

The request names seventeen logical field entries: six amount concepts and eleven policy and request names. Fifteen
of the seventeen are active at run time, one is derived and one is declaration-only, giving sixteen distinct runtime
business values. Those sixteen values are projected into eighteen source-derived canonical column instances: policy
number and policy type each appear on both relations. Each relation additionally carries one warehouse-assigned
`source_system_key`. Rationale for this accounting: [`../docs/decision-log.md`](../docs/decision-log.md), row
**D-02**.

### 3.1 Group accounting

| Group | Logical entries | Runtime values | Target allocation | Column instances |
|---|---:|---:|---|---:|
| Premium and payment | 6 | 6 | the six `canonical.preissued_rating` amount columns | 6 |
| Policy and request | 11 | 10 | the ten `canonical.issued_policy` columns; policy number and policy type also identify `canonical.preissued_rating` | 12 |
| **Total** | **17** | **16** | source-derived instances across both relations | **18** |

The eleven policy and request names resolve to ten runtime values: `DB2-POLICYNUMBER` is declaration-only and adds
no runtime value, so it receives a lineage entry and no target column. Of the eighteen source-derived column
instances, ten stand on `canonical.issued_policy` and eight on `canonical.preissued_rating`; the two extra
instances in the policy and request group are the policy number and policy type repeated on the rating relation.
Adding the one warehouse-assigned column per relation gives the 11 and 9 total column counts of section 5.

### 3.2 Per-entry specification

Runtime status is one of **active** (the item holds a business value on every executed request of its applicable
product), **derived** (no COMMAREA item carries it; it is produced from another value) or **declaration-only** (no
statement of the chain references it). "Populated by" is *request* where the caller supplies the value, *chain*
where the chain writes it into the record, or *derivation*. Locators in the second column resolve to
`base/src/lgcmarea.cpy`, in the third to `base/src/lgpolicy.cpy` and in the fourth to `base/src/lgapdb01.cbl`.

Every Db2-side declaration named in the third column is a member of the group `DB2-POLICY`
(`base/src/lgpolicy.cpy:42`) or of its subordinate group `DB2-POLICY-COMMON` (`base/src/lgpolicy.cpy:45`), except
the product premium declarations, which belong to `DB2-MOTOR` (`base/src/lgpolicy.cpy:72`) and `DB2-COMMERCIAL`
(`base/src/lgpolicy.cpy:83`). The two groups themselves carry no value of their own and have no target column.

| Logical entry | COMMAREA declaration | Db2-side declaration | Program intermediate | Runtime status | Populated by | Target relation.column | Transformation |
|---|---|---|---|---|---|---|---|
| `payment` | `CA-PAYMENT` `9(6)` bytes 95-100 (`:43`) | `DB2-PAYMENT` `9(6)` (`:51`) | `DB2-PAYMENT-INT` `S9(9) COMP` (`:92`), set `:265`, inserted `:287` | active | request | `preissued_rating.payment_amount DECIMAL(8,2)` | Passthrough; leading zeros stripped for landing; cast to a scale-2 decimal in the warehouse |
| `motor_premium` | `CA-M-PREMIUM` `9(6)` bytes 166-171 (`:73`) | `DB2-M-PREMIUM` `9(6)` (`:80`) | `DB2-M-PREMIUM-int` `S9(9) COMP` (`:100`), set `:445`, inserted `:469` | active | request | `preissued_rating.motor_premium_amount DECIMAL(8,2)` | Passthrough; populated for policy type `M` only, NULL otherwise |
| `fire_premium` | `CA-B-FirePremium` `9(8)` bytes 900-907 (`:85`) | `DB2-B-FirePremium` `9(8)` (`:91`) | `DB2-B-FirePremium-Int` `S9(9) COMP` (`:103`), set `:489`, inserted `:535` | active | request | `preissued_rating.fire_premium_amount DECIMAL(10,2)` | Passthrough; populated for policy type `C` only, NULL otherwise |
| `crime_premium` | `CA-B-CrimePremium` `9(8)` bytes 912-919 (`:87`) | `DB2-B-CrimePremium` `9(8)` (`:93`) | `DB2-B-CrimePremium-Int` `S9(9) COMP` (`:105`), set `:491`, inserted `:537` | active | request | `preissued_rating.crime_premium_amount DECIMAL(10,2)` | Passthrough; populated for policy type `C` only, NULL otherwise |
| `flood_premium` | `CA-B-FloodPremium` `9(8)` bytes 924-931 (`:89`) | `DB2-B-FloodPremium` `9(8)` (`:95`) | `DB2-B-FloodPremium-Int` `S9(9) COMP` (`:107`), set `:493`, inserted `:539` | active | request | `preissued_rating.flood_premium_amount DECIMAL(10,2)` | Passthrough; populated for policy type `C` only, NULL otherwise |
| `weather_premium` | `CA-B-WeatherPremium` `9(8)` bytes 936-943 (`:91`) | `DB2-B-WeatherPremium` `9(8)` (`:97`) | `DB2-B-WeatherPremium-Int` `S9(9) COMP` (`:109`), set `:495`, inserted `:541` | active | request | `preissued_rating.weather_premium_amount DECIMAL(10,2)` | Passthrough; populated for policy type `C` only, NULL otherwise |
| `policy_number` | `CA-POLICY-NUM` `9(10)` bytes 19-28 (`:35`) | — | `DB2-POLICYNUM-INT` `S9(9) COMP VALUE +0` (`:117`), loaded `:308-310`, moved into the COMMAREA `:311` | active | chain | `issued_policy.policy_number BIGINT NOT NULL` and `preissued_rating.policy_number BIGINT NOT NULL` | Read from the returned record; leading zeros stripped for landing; cast to `BIGINT` |
| `DB2-POLICYNUMBER` | — | `DB2-POLICYNUMBER` `9(10)` (`:44`) | — | **declaration-only** | not populated | none | Not projected. The POLICY insert names `POLICYNUMBER` in its column list (`:270`) and supplies `DEFAULT` as its value (`:279`); the recovered key travels through `DB2-POLICYNUM-INT` instead |
| `policy_type` | — (not present in the COMMAREA) | `DB2-POLICYTYPE` `X` (`:43`) | set by the routing `EVALUATE` (`:184-207`) at `:188`, `:192`, `:196`, `:200`; supplied to the insert `:283` | **derived** | derivation | `issued_policy.policy_type CHAR(1) NOT NULL` and `preissued_rating.policy_type CHAR(1) NOT NULL` | Derived from `CA-REQUEST-ID` by the routing table of section 6.3 and verified against the policy SQL capture |
| `customer_number` | `CA-CUSTOMER-NUM` `9(10)` bytes 9-18 (`:12`) | — | `DB2-CUSTOMERNUM-INT` `S9(9) COMP` (`:90`), set `:176`, inserted `:280` | active | request | `issued_policy.customer_number BIGINT NOT NULL` | Passthrough; leading zeros stripped for landing; cast to `BIGINT` |
| `request_id` | `CA-REQUEST-ID` `X(6)` bytes 1-6 (`:10`) | — | — | active | request | `issued_policy.request_id VARCHAR(6) NOT NULL` | Trim; the value also drives the policy-type derivation |
| `return_code` | `CA-RETURN-CODE` `9(2)` bytes 7-8 (`:11`) | — | initialised `MOVE '00' TO CA-RETURN-CODE` (`:172`); set by the outcome paths of section 2.1 | active | chain | `issued_policy.return_code CHAR(2) NOT NULL` | Carried as a two-character zero-padded string; never converted to an integer |
| `issue_date` | `CA-ISSUE-DATE` `X(10)` bytes 29-38 (`:38`) | `DB2-ISSUEDATE` `X(10)` (`:46`) | passed straight to the insert `:281` | active | request | `issued_policy.issue_date DATE` | Trim; an empty trimmed value lands as NULL; cast to `DATE` |
| `expiry_date` | `CA-EXPIRY-DATE` `X(10)` bytes 39-48 (`:39`) | `DB2-EXPIRYDATE` `X(10)` (`:47`) | passed straight to the insert `:282` | active | request | `issued_policy.expiry_date DATE` | Trim; an empty trimmed value lands as NULL; cast to `DATE` |
| `last_changed` | `CA-LASTCHANGED` `X(26)` bytes 49-74 (`:40`) | `DB2-LASTCHANGED` `X(26)` (`:48`) | `CURRENT TIMESTAMP` written `:284`, read back into the COMMAREA `:316-321` | active | chain | `issued_policy.last_changed TIMESTAMP NOT NULL` | Read from the returned record; the 26-character Db2 timestamp is normalised to ISO-8601 before landing |
| `broker_id` | `CA-BROKERID` `9(10)` bytes 75-84 (`:41`) | `DB2-BROKERID` `9(10)` (`:49`) | `DB2-BROKERID-INT` `S9(9) COMP` (`:91`), set `:264`, inserted `:285` | active | request | `issued_policy.broker_id BIGINT` | Passthrough; a blank window lands as NULL; leading zeros stripped; cast to `BIGINT` |
| `brokers_reference` | `CA-BROKERSREF` `X(10)` bytes 85-94 (`:42`) | `DB2-BROKERSREF` `X(10)` (`:50`) | passed straight to the insert as a character host variable `:286` | active | request | `issued_policy.brokers_reference VARCHAR(10)` | Trim; an empty trimmed value lands as NULL |

Rationale for the treatment of `DB2-POLICYNUMBER` as declaration-only is recorded in
[`../docs/decision-log.md`](../docs/decision-log.md), row **D-02**; for the derivation of `policy_type` rather than
a passthrough, row **D-50**; for the ISO-8601 normalisation of `CA-LASTCHANGED`, row **D-53**.

### 3.3 `source_system_key` — the one warehouse-assigned column

`source_system_key VARCHAR(64) NOT NULL` stands on both canonical relations and is the first element of the natural
key of each. It has no COMMAREA declaration, no Db2-side declaration and no program intermediate: no item of the
three authorities supplies it, and its lineage entry cites the user requirement in place of a locator. It is
assigned by the extraction run, written unchanged to the landing record, to the S3 key prefix and to both relations,
and it is the **sole** documented exception to complete COBOL lineage. The run value of this exemplar is
`GENAPP_CLASS_EXEMPLAR`. It is counted separately from the seventeen logical field entries and is not one of the
sixteen runtime values. Rationale: [`../docs/decision-log.md`](../docs/decision-log.md), row **D-03**.

### 3.4 In-scope declarations that receive no target column

These declarations stand in the overlays this work exercises and carry no canonical column. They are listed so that
every in-scope declaration is individually visible with its locator and its treatment.

| Item | PICTURE | Bytes | Locator | Db2-side counterpart | Program intermediate | Classification | Target |
|---|---|---|---|---|---|---|---|
| `CA-B-FirePeril` | `9(4)` | 896-899 | `base/src/lgcmarea.cpy:84` | `DB2-B-FirePeril` (`base/src/lgpolicy.cpy:90`) | `DB2-B-FirePeril-Int` `S9(4) COMP` (`base/src/lgapdb01.cbl:102`), set `:488`, inserted `:534` | peril code, not an amount | none |
| `CA-B-CrimePeril` | `9(4)` | 908-911 | `base/src/lgcmarea.cpy:86` | `DB2-B-CrimePeril` (`base/src/lgpolicy.cpy:92`) | `DB2-B-CrimePeril-Int` `S9(4) COMP` (`base/src/lgapdb01.cbl:104`), set `:490`, inserted `:536` | peril code, not an amount | none |
| `CA-B-FloodPeril` | `9(4)` | 920-923 | `base/src/lgcmarea.cpy:88` | `DB2-B-FloodPeril` (`base/src/lgpolicy.cpy:94`) | `DB2-B-FloodPeril-Int` `S9(4) COMP` (`base/src/lgapdb01.cbl:106`), set `:492`, inserted `:538` | peril code, not an amount | none |
| `CA-B-WeatherPeril` | `9(4)` | 932-935 | `base/src/lgcmarea.cpy:90` | `DB2-B-WeatherPeril` (`base/src/lgpolicy.cpy:96`) | `DB2-B-WeatherPeril-Int` `S9(4) COMP` (`base/src/lgapdb01.cbl:108`), set `:494`, inserted `:540` | peril code, not an amount | none |
| `CA-B-Status` | `9(4)` | 944-947 | `base/src/lgcmarea.cpy:92` | `DB2-B-Status` (`base/src/lgpolicy.cpy:98`) | `DB2-B-Status-Int` `S9(4) COMP` (`base/src/lgapdb01.cbl:110`), set `:496`, inserted `:542` | present but unmapped status indicator | none |
| `CA-B-RejectReason` | `X(255)` | 948-1202 | `base/src/lgcmarea.cpy:93` | `DB2-B-RejectReason` (`base/src/lgpolicy.cpy:99`) | none; passed straight to the insert `:543` | present but unmapped free text | none |

The four peril codes are `PIC 9(4)` codes; the requested amount fields are the adjacent `PIC 9(8)` premium items at
`base/src/lgcmarea.cpy:85,87,89,91`. Rationale: [`../docs/decision-log.md`](../docs/decision-log.md), row **D-12**.

Three further items of the motor overlay are active at run time, carry a Db2-side declaration and a program
intermediate, and receive no target column:

| Item | PICTURE | Bytes | Locator | Db2-side counterpart | Program intermediate | Target |
|---|---|---|---|---|---|---|
| `CA-M-VALUE` | `9(6)` | 131-136 | `base/src/lgcmarea.cpy:68` | `DB2-M-VALUE` (`base/src/lgpolicy.cpy:75`) | `DB2-M-VALUE-INT` `S9(9) COMP` (`base/src/lgapdb01.cbl:98`), set `:443`, inserted `:464` | none |
| `CA-M-CC` | `9(4)` | 152-155 | `base/src/lgcmarea.cpy:71` | `DB2-M-CC` (`base/src/lgpolicy.cpy:78`) | `DB2-M-CC-SINT` `S9(4) COMP` (`base/src/lgapdb01.cbl:99`), set `:444`, inserted `:467` | none |
| `CA-M-ACCIDENTS` | `9(6)` | 172-177 | `base/src/lgcmarea.cpy:74` | `DB2-M-ACCIDENTS` (`base/src/lgpolicy.cpy:81`) | `DB2-M-ACCIDENTS-int` `S9(9) COMP` (`base/src/lgapdb01.cbl:101`), set `:446`, inserted `:470` | none |

Every remaining item of the two exercised overlays — the motor make, model, registration, colour and manufacture
date, and the commercial address, postcode, latitude, longitude, customer and property type — is a character
declaration passed straight to its insert with no program intermediate, at
`base/src/lgapdb01.cbl:462-468` for motor and `:528-533` for commercial. Each is listed with its PICTURE, byte
range and copybook locator in the byte grids of sections 1.3 and 1.4, each is populated in the sample records only
so the named chain executes its product route, none receives a target column, and extraction never reads any of
them. The same holds for the redefined group declarations `CA-REQUEST-SPECIFIC` (`base/src/lgcmarea.cpy:13`),
`CA-POLICY-REQUEST` (`:34`), `CA-POLICY-COMMON` (`:37`), `CA-POLICY-SPECIFIC` (`:44`), `CA-MOTOR` (`:65`) and
`CA-COMMERCIAL` (`:77`), and for the three fill items `CA-M-FILLER` (`:75`), `CA-B-FILLER` (`:94`) and the padding
of an unselected overlay: they carry storage rather than a business value and have no target column.

---

## 4. No premium or rating formula exists in the named chain

**There is no premium or rating formula anywhere in the named Policy-Issue chain.** The six amount values are
carried from the request into the Db2 inserts unchanged. This is a measured finding, not an inference from an
absence of documentation.

### 4.1 Statement census

Measured across the three programs of the chain — `base/src/lgapol01.cbl`, `base/src/lgapdb01.cbl` and
`base/src/lgapvs01.cbl`:

| Statement | Count | Locators |
|---|---:|---|
| `COMPUTE` | **0** | — |
| `MULTIPLY` | **0** | — |
| `DIVIDE` | **0** | — |
| `ADD` | 6 | `base/src/lgapol01.cbl:109`; `base/src/lgapdb01.cbl:182`, `:187`, `:191`, `:195`, `:199` |
| `SUBTRACT` | 1 | `base/src/lgapdb01.cbl:339` |

Every operand of all seven arithmetic statements is a COMMAREA length constant: the six `ADD` statements accumulate
`WS-CA-HEADER-LEN` and one product length constant into the required-length accumulator, and the single `SUBTRACT`
derives a varying-character length from the received length. None of them touches an amount.

The six amount items reach their Db2 host variables by plain `MOVE` and are inserted without modification:

| Amount | `MOVE` | Insert operand |
|---|---|---|
| `CA-PAYMENT` | `base/src/lgapdb01.cbl:265` | `:287` |
| `CA-M-PREMIUM` | `base/src/lgapdb01.cbl:445` | `:469` |
| `CA-B-FirePremium` | `base/src/lgapdb01.cbl:489` | `:535` |
| `CA-B-CrimePremium` | `base/src/lgapdb01.cbl:491` | `:537` |
| `CA-B-FloodPremium` | `base/src/lgapdb01.cbl:493` | `:539` |
| `CA-B-WeatherPremium` | `base/src/lgapdb01.cbl:495` | `:541` |

### 4.2 Consequence for this specification

The six amounts are a **passthrough projection**. No formula, rating factor, derived-factor column or backfilled
calculation is constructed, inferred or backfilled to fill the gap, and none appears in either canonical relation.
The finding itself is recorded in metadata and documentation — here, in the field map's `formula: none` member, in
[`../docs/field-level-lineage.md`](../docs/field-level-lineage.md) and in the project guide — and never as an
unsourced data column. Rationale: [`../docs/decision-log.md`](../docs/decision-log.md), row **D-11**.

The six declarations are unsigned DISPLAY numerics with no implied decimal — `PIC 9(6)` for payment and motor
premium and `PIC 9(8)` for the four commercial premiums (`base/src/lgcmarea.cpy:43,73,85,87,89,91`) — and they move
into binary integer host variables (`base/src/lgapdb01.cbl:92,100,103,105,107,109`). Every byte of such a window
holds one digit character and every stored value is a whole number, so a canonical amount typed at scale 2 normally
ends in `.00`. Rationale for typing the canonical amounts as scale-2 decimals rather than integers:
[`../docs/decision-log.md`](../docs/decision-log.md), row **D-55**.

### 4.3 Character-set representation

The local harness writes and reads the workstation character set, and extraction decodes the capture as ASCII. A
real z/OS extract carries the installation's EBCDIC code page, documented as CCSID 285 by default, and must be
decoded against it before any of these amounts can be trusted; this tooling does not decode EBCDIC. The
representation risk in this exercise is therefore encoding rather than arithmetic.

### 4.4 Amount comparison contract

Applied to the six amounts when the harness captures are compared with the canonical rows:

| Observation | Disposition |
|---|---|
| Exact equality | Expected; passes |
| Absolute delta ≤ 0.01 and non-zero | Passes, and is reported as unexpected |
| Absolute delta > 0.01 | Fails |

Every non-amount value is compared exactly, after the trim and normalisation rules stated in section 6.3. No
compared field may be skipped. Results are recorded in
[`../validation/validation-evidence.md`](../validation/validation-evidence.md). Rationale for retaining the ±0.01
threshold and for classifying a non-zero in-tolerance delta separately:
[`../docs/decision-log.md`](../docs/decision-log.md), rows **D-04** and **D-37**.

---

## 5. The two canonical relations

### 5.1 `canonical.issued_policy`

Grain: **one row per successful issued policy and source system.** Unique key: `(source_system_key,
policy_number)`. Eleven columns — ten source-derived and one warehouse-assigned. Locators in the last column resolve
to the file each names.

| Column | Type | Nullability | Source or rule | Locator |
|---|---|---|---|---|
| `source_system_key` | `VARCHAR(64)` | NOT NULL | User-mandated warehouse value | — (user requirement) |
| `policy_number` | `BIGINT` | NOT NULL | Returned `CA-POLICY-NUM` | `base/src/lgcmarea.cpy:35`; `base/src/lgapdb01.cbl:307-321` |
| `policy_type` | `CHAR(1)` | NOT NULL | `DB2-POLICYTYPE`, derived `E`/`H`/`M`/`C` from request routing and verified against the SQL capture | `base/src/lgpolicy.cpy:43`; `base/src/lgapdb01.cbl:184-207` |
| `customer_number` | `BIGINT` | NOT NULL | `CA-CUSTOMER-NUM` | `base/src/lgcmarea.cpy:12` |
| `request_id` | `VARCHAR(6)` | NOT NULL | `CA-REQUEST-ID` | `base/src/lgcmarea.cpy:10` |
| `return_code` | `CHAR(2)` | NOT NULL | Returned `CA-RETURN-CODE` | `base/src/lgcmarea.cpy:11` |
| `issue_date` | `DATE` | nullable | `CA-ISSUE-DATE` | `base/src/lgcmarea.cpy:38` |
| `expiry_date` | `DATE` | nullable | `CA-EXPIRY-DATE` | `base/src/lgcmarea.cpy:39` |
| `last_changed` | `TIMESTAMP` | NOT NULL | Returned `CA-LASTCHANGED`, normalised | `base/src/lgcmarea.cpy:40`; `base/src/lgapdb01.cbl:315-321` |
| `broker_id` | `BIGINT` | nullable | `CA-BROKERID` | `base/src/lgcmarea.cpy:41` |
| `brokers_reference` | `VARCHAR(10)` | nullable | Trimmed `CA-BROKERSREF` | `base/src/lgcmarea.cpy:42` |

The dbt mart model applies the predicate `return_code = '00'` before materialising an issued row. The raw and
staging layers retain the return code for evidence and failure analysis, and the column stands on the canonical
relation as well.

### 5.2 `canonical.preissued_rating`

Grain: **one row per successful issued policy and source system.** Unique key: `(source_system_key,
policy_number)`. Nine columns — eight source-derived and one warehouse-assigned.

| Column | Type | Nullability | Source or rule | Locator |
|---|---|---|---|---|
| `source_system_key` | `VARCHAR(64)` | NOT NULL | User-mandated warehouse value | — (user requirement) |
| `policy_number` | `BIGINT` | NOT NULL | Returned `CA-POLICY-NUM` | `base/src/lgcmarea.cpy:35`; `base/src/lgapdb01.cbl:307-321` |
| `policy_type` | `CHAR(1)` | NOT NULL | The same `DB2-POLICYTYPE` discriminator as `issued_policy` | `base/src/lgpolicy.cpy:43`; `base/src/lgapdb01.cbl:184-207` |
| `payment_amount` | `DECIMAL(8,2)` | nullable | `CA-PAYMENT` / `DB2-PAYMENT` | `base/src/lgcmarea.cpy:43`; `base/src/lgpolicy.cpy:51` |
| `motor_premium_amount` | `DECIMAL(8,2)` | nullable | `CA-M-PREMIUM` / `DB2-M-PREMIUM` | `base/src/lgcmarea.cpy:73`; `base/src/lgpolicy.cpy:80` |
| `fire_premium_amount` | `DECIMAL(10,2)` | nullable | `CA-B-FirePremium` / `DB2-B-FirePremium` | `base/src/lgcmarea.cpy:85`; `base/src/lgpolicy.cpy:91` |
| `crime_premium_amount` | `DECIMAL(10,2)` | nullable | `CA-B-CrimePremium` / `DB2-B-CrimePremium` | `base/src/lgcmarea.cpy:87`; `base/src/lgpolicy.cpy:93` |
| `flood_premium_amount` | `DECIMAL(10,2)` | nullable | `CA-B-FloodPremium` / `DB2-B-FloodPremium` | `base/src/lgcmarea.cpy:89`; `base/src/lgpolicy.cpy:95` |
| `weather_premium_amount` | `DECIMAL(10,2)` | nullable | `CA-B-WeatherPremium` / `DB2-B-WeatherPremium` | `base/src/lgcmarea.cpy:91`; `base/src/lgpolicy.cpy:97` |

A product-inapplicable premium column is **NULL, never zero**. The pattern by policy type:

| Policy type | Populated amount columns | NULL amount columns |
|---|---|---|
| `M` — motor | `payment_amount`, `motor_premium_amount` | the four commercial premiums |
| `C` — commercial | `payment_amount`, `fire_premium_amount`, `crime_premium_amount`, `flood_premium_amount`, `weather_premium_amount` | `motor_premium_amount` |
| `E` — endowment | `payment_amount` | all five product premiums |
| `H` — house | `payment_amount` | all five product premiums |

`payment_amount` is applicable to every product; it is declared in the common policy area rather than in a product
overlay. Zero is never substituted for an inapplicable premium, and the pattern is asserted by a singular dbt test
rather than left to convention. Rationale: [`../docs/decision-log.md`](../docs/decision-log.md), row **D-54**.

### 5.3 The canonical schema holds exactly these two relations

`canonical.issued_policy` and `canonical.preissued_rating` are the **only** two relations of the canonical schema in
this project. There is no third relation, no source-system registry, no provenance relation, no formula column, no
rating-factor column, no derived-factor column, no commission field, and no Quote or Loss model. A future source
system is onboarded by assigning it a new `source_system_key`, with no structural change to either relation.
Rationale: [`../docs/decision-log.md`](../docs/decision-log.md), rows **D-11** and **D-03**.

---

## 6. Landing contract and field allocation

### 6.1 The landed record

One extraction produces one landing record: a single JSON object carrying **exactly seventeen keys** — the sixteen
runtime business values plus `source_system_key` — in this order:

| # | Key | Nullable | # | Key | Nullable |
|---:|---|---|---:|---|---|
| 1 | `source_system_key` | no | 10 | `broker_id` | yes |
| 2 | `policy_number` | no | 11 | `brokers_reference` | yes |
| 3 | `policy_type` | no | 12 | `payment_amount` | yes |
| 4 | `customer_number` | no | 13 | `motor_premium_amount` | yes |
| 5 | `request_id` | no | 14 | `fire_premium_amount` | yes |
| 6 | `return_code` | no | 15 | `crime_premium_amount` | yes |
| 7 | `issue_date` | yes | 16 | `flood_premium_amount` | yes |
| 8 | `expiry_date` | yes | 17 | `weather_premium_amount` | yes |
| 9 | `last_changed` | no | | | |

Every value is a JSON **string or null**: no number, boolean, array or nested object is emitted. The object is
serialised as one line terminated by a single line feed, one object per object file, and no additional key —
provenance or otherwise — is permitted. The shape is constrained by
[`../landing/landing-schema.json`](../landing/landing-schema.json), which requires all seventeen keys and admits no
others. Rationale for landing every field as a string: [`../docs/decision-log.md`](../docs/decision-log.md), row
**D-52**.

`raw.genapp_policy_issue` stores every landed field as `VARCHAR`, nullable, with widths taken from the source
PICTURE of each field. All typing happens afterwards, in the dbt intermediate model. Rationale:
[`../docs/decision-log.md`](../docs/decision-log.md), row **D-41**.

### 6.2 S3 key prefix

The landed object is written under this key:

```text
s3://<bucket>/landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=YYYY-MM-DD/part-0000.json
```

The partition requirement applies to the S3 key prefix only; it is not a warehouse table property. The object name
is the literal `part-0000.json`. The prefix layout, its elements and its examples are documented in
[`../landing/partition-layout.md`](../landing/partition-layout.md).

### 6.3 Transformations performed by `extract_commarea.py`

[`extract_commarea.py`](extract_commarea.py) reads the returned COMMAREA capture — exactly 32,500 characters,
optionally followed by one line ending — and applies these rules and no others:

| Rule | Applied to |
|---|---|
| Trim leading and trailing spaces | every alphanumeric window |
| A blank window lands as null | `brokers_reference`, `issue_date`, `expiry_date` and `broker_id`; a blank window of an applicable amount or of a value the chain assigns is refused instead |
| Digits only, leading zeros stripped, an all-zero window landing as `0` | every numeric display window, the six amounts included |
| Derive `policy_type` from `CA-REQUEST-ID` | `01AEND` → `E`, `01AHOU` → `H`, `01AMOT` → `M`, `01ACOM` → `C`, per the routing `EVALUATE` at `base/src/lgapdb01.cbl:184-207` |
| Normalise the 26-character `CA-LASTCHANGED` to ISO-8601 | the Db2 form `YYYY-MM-DD-HH.MM.SS.ffffff` is accepted and emitted as `YYYY-MM-DDTHH:MM:SS.ffffff`, validated as a real date and clock time |
| Validate that an applicable amount window holds digits before landing | `payment_amount` always; `motor_premium_amount` for policy type `M`; the four commercial premiums for policy type `C` |
| Write an inapplicable product premium as null without reading its window | every amount the derived policy type does not apply to |
| Refuse a record whose returned `CA-RETURN-CODE` is not `00` | the whole record; nothing is written |

**No amount is derived.** No scaling, rounding, defaulting, unit conversion or arithmetic of any kind is applied to
any of the six amounts: each is landed as the digits the record carries. The four commercial peril codes are never
read.

### 6.4 Field allocation across the two relations

Field allocation across the two relations is shown in **Figure 4 — dbt Transformation DAG and Field Allocation** in
[`../docs/architecture.md`](../docs/architecture.md#figure-4), which is the single rendering authority for every
figure of this work and carries that figure's legend. The column-level allocation it depicts is specified in tables
here: sections 5.1 and 5.2 give the two column sets, section 3.1 gives the group accounting, and section 3.2 gives
the target relation and column of every logical entry.

---

## 7. Samples and length handling

### 7.1 The two sample cases

Two sample cases are defined, covering all six amounts between them:

| Request id | Policy type | Amounts exercised | Sample definition |
|---|---|---|---|
| `01AMOT` | `M` | `payment_amount`, `motor_premium_amount` | [`sample_input/commarea_01amot.json`](sample_input/commarea_01amot.json) |
| `01ACOM` | `C` | `payment_amount` and all four commercial premiums | [`sample_input/commarea_01acom.json`](sample_input/commarea_01acom.json) |

Each definition is a flat JSON document keyed by COMMAREA item name.
[`build_sample_commarea.py`](build_sample_commarea.py) validates it against the sample-definition contract of the
field map and renders a record of exactly 32,500 characters; these two request ids are the only ones an authored
sample definition describes and the only ones the builder emits a record for. A sample definition may not supply a
window the chain writes — the return code, the policy number and the timestamp — and each of those windows is
emitted carrying a seed outside the value domain the chain produces, so a post-chain value in one of them can only
have been written by the chain. Rationale: [`../docs/decision-log.md`](../docs/decision-log.md), row **D-35**.

**No endowment record is generated** by this work, by the sample builder or by the harness runner, and no harness
case executes the endowment route; the endowment routing branch remains documented in section 6.3 and in the field
map's routing table. Rationale: [`../docs/decision-log.md`](../docs/decision-log.md), row **D-18**. A house record
for request id `01AHOU` is derived by the harness runner from the generated `01AMOT` record for its own route
coverage; no sample definition describes it, the sample builder emits none, and it is not a landed sample of this
specification.

Sample record values are illustrative fixtures and carry no real customer, policy or broker data. Any future
expansion of the extracted field set requires a separate privacy and security review.

### 7.2 Measured length constants

The chain validates the received length against an accumulator, `WS-REQUIRED-CA-LEN` (`base/src/lgapdb01.cbl:66`),
compared with `EIBCALEN` at `base/src/lgapdb01.cbl:210`. The declared constants and the measured overlay lengths
are:

| Measurement | Value | Evidence |
|---|---:|---|
| Declared `WS-MOTOR-LEN` | 65 | `base/src/lgpolicy.cpy:21` |
| Declared `WS-FULL-MOTOR-LEN` | 137 | `base/src/lgpolicy.cpy:26` |
| Motor length the chain requires — header 28 + full motor 137 | 165 | `base/src/lgapdb01.cbl:182`, `:195` |
| Actual end byte of the motor overlay | 177 | `base/src/lgcmarea.cpy:65-75` |
| Motor shortfall — `CA-M-PREMIUM` 166-171 plus `CA-M-ACCIDENTS` 172-177 | 12 | `base/src/lgcmarea.cpy:73-74` |
| Declared `WS-COMM-LEN` | 1102 | `base/src/lgpolicy.cpy:22` |
| Declared `WS-FULL-COMM-LEN` | 1174 | `base/src/lgpolicy.cpy:27` |
| Commercial length the chain requires — header 28 + full commercial 1174 | 1202 | `base/src/lgapdb01.cbl:182`, `:199` |
| Actual end byte of the commercial overlay | 1202 | `base/src/lgcmarea.cpy:77-94` |
| Commercial shortfall | 0 | the two agree exactly |

The motor length the chain requires stops 12 bytes short of the end of the motor overlay, and those 12 bytes are
exactly the premium and accident-count windows. The handling is as follows, and it changes nothing in the source:

- No source length constant is altered; all five source artifacts remain byte-identical.
- Every generated sample record is the full 32,500 characters, so the premium window always holds its supplied
  digits whatever length the chain validates.
- Extraction validates that the applicable amount windows hold digits before landing, per section 6.3.

Rationale: [`../docs/decision-log.md`](../docs/decision-log.md), row **D-08**. The same measurement, stated from the
sample builder's point of view, is recorded in
[`sample_input/README.md`](sample_input/README.md).
