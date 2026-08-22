# Sample COMMAREA definitions

> **Status — validated against local substitute, not AWS.** Every result these samples contribute to was produced on the
> local-substitute branch: a moto S3 endpoint in place of Amazon S3 and DuckDB in place of Amazon Redshift. The formal
> AWS diff requirement is **OPEN** and this has not yet happened. Local-substitute diff results do not close it and must
> never be represented as satisfying the Validation Framework's diff requirement.

This folder holds the two sample definitions that make the named GenApp Policy-Issue chain executable under GnuCOBOL,
and this README. Nothing generated is written here.

## Pipeline position

- `modernization/extraction/copybook_field_map.yml` — defines the contract these definitions satisfy, and supplies
  every offset, length and kind used below.
- `modernization/extraction/build_sample_commarea.py` — validates a definition and renders it into a full-length record.
- `modernization/harness/run_harness.sh` and `modernization/harness/driver.cbl` — consume the rendered record and
  execute `LGAPOL01` → `LGAPDB01` → `LGAPVS01`.
- `modernization/extraction/extract_commarea.py` — decodes the returned COMMAREA after the chain has run.
- `modernization/extraction/extraction-spec.md` and `modernization/validation/validation-evidence.md` — cite the two
  cases `01AMOT` and `01ACOM`.

Rendered records are written to `modernization/harness/build/`, which is the only ignored location involved. No
generated artifact belongs in this folder.

## The sample-definition contract

Defined by the `sample_definition_contract` block of `modernization/extraction/copybook_field_map.yml` and enforced by
`modernization/extraction/build_sample_commarea.py`.

| Aspect | Contract |
|---|---|
| Document shape | A flat JSON object. No nesting, no arrays. |
| Keys | COMMAREA item names exactly as declared in `base/src/lgcmarea.cpy`. Matching is case-insensitive, so `CA-B-FirePremium` and `ca-b-firepremium` both resolve; the declared spelling is what these files use. |
| Values | All values are strings. |
| Request id | `CA-REQUEST-ID` is required and must be `01AMOT` or `01ACOM`. The overlay is resolved from the routing table, mirroring `base/src/lgapdb01.cbl:184-207`. |
| Emitted length | 32,500 characters, whatever the definition supplies. |

Rejected keys:

- unknown keys;
- keys belonging to the other product's overlay — every product overlay `REDEFINES` the same bytes from 101 onward
  [`base/src/lgcmarea.cpy:44-94`], so only one product's items are addressable in one record;
- the chain-assigned items `CA-RETURN-CODE`, `CA-POLICY-NUM` and `CA-LASTCHANGED`;
- filler and padding items — `CA-E-PADDING-DATA` [`base/src/lgcmarea.cpy:54`], `CA-H-FILLER` [`:63`], `CA-M-FILLER`
  [`:75`], `CA-B-FILLER` [`:94`] and `CA-C-FILLER` [`:103`].

Required keys, by resolved request id:

| Request id | Required keys | Count |
|---|---|---|
| Both | `CA-REQUEST-ID`, `CA-CUSTOMER-NUM`, `CA-ISSUE-DATE`, `CA-EXPIRY-DATE`, `CA-BROKERID`, `CA-BROKERSREF`, `CA-PAYMENT` | 7 |
| `01AMOT` | the seven above plus `CA-M-PREMIUM` | 8 |
| `01ACOM` | the seven above plus `CA-B-FirePremium`, `CA-B-CrimePremium`, `CA-B-FloodPremium`, `CA-B-WeatherPremium` | 11 |

`CA-REQUEST-ID` is required by the contract block itself; the remainder are required through the logical entries that
record `populated_by: request` for the resolved policy type. Any other item of the resolved overlay may be supplied or
omitted.

Value rules:

- a supplied value must fit the declared length of its item, and must not be empty;
- `PIC 9` items carry digits only;
- `PIC X` items carry printable 7-bit ASCII only;
- an item recording an ISO date must be a real calendar date written as `YYYY-MM-DD`;
- a supplied numeric value must not exceed the largest whole number the host declaration the chain moves it into can
  hold;
- unset numeric items are zero-filled and unset alphanumeric items space-filled. Numeric values are right-justified,
  alphanumeric values left-justified.

A numeric window never contains spaces on an emitted record. `LGAPDB01` MOVEs those items into `COMP` host variables —
`base/src/lgapdb01.cbl:443-446` for motor and `:488-496` for commercial — and a space in such a window is not a valid
operand of that MOVE.

## Field values — `commarea_01amot.json`

Request `01AMOT`, 16 keys. Byte positions are 1-based positions in the emitted 32,500-character record.

| Key | PIC | Bytes | Value |
|---|---|---|---|
| `CA-REQUEST-ID` | X(6) | 1-6 | `01AMOT` |
| `CA-CUSTOMER-NUM` | 9(10) | 9-18 | `0000001001` |
| `CA-ISSUE-DATE` | X(10) | 29-38 | `2026-08-19` |
| `CA-EXPIRY-DATE` | X(10) | 39-48 | `2027-08-18` |
| `CA-BROKERID` | 9(10) | 75-84 | `0000000042` |
| `CA-BROKERSREF` | X(10) | 85-94 | `BRMOT001` |
| `CA-PAYMENT` | 9(6) | 95-100 | `000500` |
| `CA-M-MAKE` | X(15) | 101-115 | `FORD` |
| `CA-M-MODEL` | X(15) | 116-130 | `FIESTA` |
| `CA-M-VALUE` | 9(6) | 131-136 | `012500` |
| `CA-M-REGNUMBER` | X(7) | 137-143 | `AB12CDE` |
| `CA-M-COLOUR` | X(8) | 144-151 | `BLUE` |
| `CA-M-CC` | 9(4) | 152-155 | `1400` |
| `CA-M-MANUFACTURED` | X(10) | 156-165 | `2019-03-15` |
| `CA-M-PREMIUM` | 9(6) | 166-171 | `000450` |
| `CA-M-ACCIDENTS` | 9(6) | 172-177 | `000001` |

## Field values — `commarea_01acom.json`

Request `01ACOM`, 22 keys.

| Key | PIC | Bytes | Value |
|---|---|---|---|
| `CA-REQUEST-ID` | X(6) | 1-6 | `01ACOM` |
| `CA-CUSTOMER-NUM` | 9(10) | 9-18 | `0000002002` |
| `CA-ISSUE-DATE` | X(10) | 29-38 | `2026-08-19` |
| `CA-EXPIRY-DATE` | X(10) | 39-48 | `2027-08-18` |
| `CA-BROKERID` | 9(10) | 75-84 | `0000000084` |
| `CA-BROKERSREF` | X(10) | 85-94 | `BRCOM001` |
| `CA-PAYMENT` | 9(6) | 95-100 | `001750` |
| `CA-B-Address` | X(255) | 101-355 | `1 EXAMPLE INDUSTRIAL ESTATE, EXAMPLE TOWN` |
| `CA-B-Postcode` | X(8) | 356-363 | `EX1 2AB` |
| `CA-B-Latitude` | X(11) | 364-374 | `51.4779` |
| `CA-B-Longitude` | X(11) | 375-385 | `-0.0015` |
| `CA-B-Customer` | X(255) | 386-640 | `EXAMPLE MANUFACTURING LTD` |
| `CA-B-PropType` | X(255) | 641-895 | `WAREHOUSE` |
| `CA-B-FirePeril` | 9(4) | 896-899 | `0011` |
| `CA-B-FirePremium` | 9(8) | 900-907 | `00013500` |
| `CA-B-CrimePeril` | 9(4) | 908-911 | `0022` |
| `CA-B-CrimePremium` | 9(8) | 912-919 | `00003400` |
| `CA-B-FloodPeril` | 9(4) | 920-923 | `0033` |
| `CA-B-FloodPremium` | 9(8) | 924-931 | `00007800` |
| `CA-B-WeatherPeril` | 9(4) | 932-935 | `0044` |
| `CA-B-WeatherPremium` | 9(8) | 936-943 | `00002600` |
| `CA-B-Status` | 9(4) | 944-947 | `0000` |

Notes on both tables:

- `CA-B-RejectReason` (X(255), bytes 948-1202) is not supplied, and its window is space-filled by the builder.
- `CA-BROKERSREF` is shorter than its 10-character window in both samples, so its trailing bytes are space-filled and
  the staging trim is exercised.
- Every numeric value inside a record is distinct — `01AMOT` carries 1, 42, 450, 500, 1001, 1400 and 12500; `01ACOM`
  carries 0, 11, 22, 33, 44, 84, 1750, 2002, 2600, 3400, 7800 and 13500 — so a field-swap defect cannot pass the
  comparison by coincidence.
- If any value in a JSON file changes, this README changes in the same pass.

## Chain-assigned items

These three windows are written by the chain, not by a definition.

| Item | PIC | Bytes | Populated by |
|---|---|---|---|
| `CA-RETURN-CODE` | 9(2) | 7-8 | `base/src/lgapdb01.cbl:172` |
| `CA-POLICY-NUM` | 9(10) | 19-28 | `base/src/lgapdb01.cbl:308-311` |
| `CA-LASTCHANGED` | X(26) | 49-74 | `base/src/lgapdb01.cbl:316-321` |

Supplying any of them in a definition is rejected. On the emitted record, before the chain runs, the builder places the
content the `chain_populated_items` block of `modernization/extraction/copybook_field_map.yml` records for each window:
`CA-RETURN-CODE` carries the seed `55`, which is not one of the codes the chain produces; `CA-POLICY-NUM` is
zero-filled; `CA-LASTCHANGED` is space-filled.

Decision record: `modernization/docs/decision-log.md`, row **D-35**.

## Excluded items that are still digit-filled

| Item | PIC | Bytes | Warehouse target |
|---|---|---|---|
| `CA-B-FirePeril` | 9(4) | 896-899 | none |
| `CA-B-CrimePeril` | 9(4) | 908-911 | none |
| `CA-B-FloodPeril` | 9(4) | 920-923 | none |
| `CA-B-WeatherPeril` | 9(4) | 932-935 | none |
| `CA-B-Status` | 9(4) | 944-947 | none |

The four peril fields are `PIC 9(4)` **codes, not amounts** [`base/src/lgcmarea.cpy:84,86,88,90`], and they are
excluded from every warehouse target. They are digit-filled all the same, so the chain executes:
`base/src/lgapdb01.cbl:488-496` MOVEs each of them, and `CA-B-Status` with them, into `COMP` receivers. The requested
amount fields are the adjacent premium items at `base/src/lgcmarea.cpy:85,87,89,91`, not these codes.

Decision record: `modernization/docs/decision-log.md`, row **D-12**.

## Full-record generation

Run from the repository root, using the virtual-environment interpreter so a non-interactive shell cannot fall back to
system Python:

```bash
modernization/.venv/bin/python modernization/extraction/build_sample_commarea.py \
  --sample modernization/extraction/sample_input/commarea_01amot.json \
  --field-map modernization/extraction/copybook_field_map.yml \
  --output modernization/harness/build/samples/commarea_01amot.dat

modernization/.venv/bin/python modernization/extraction/build_sample_commarea.py \
  --sample modernization/extraction/sample_input/commarea_01acom.json \
  --field-map modernization/extraction/copybook_field_map.yml \
  --output modernization/harness/build/samples/commarea_01acom.dat
```

Output shape: exactly **32,500 characters** followed by one LF, so 32,501 bytes on disk. The record is always full
length, regardless of any product overlay's declared length.

That length reconciles against `base/src/lgcmarea.cpy` as 6 + 2 + 10 + 32,482 = 32,500: `CA-REQUEST-ID` X(6)
[`:10`], `CA-RETURN-CODE` 9(2) [`:11`], `CA-CUSTOMER-NUM` 9(10) [`:12`] and `CA-REQUEST-SPECIFIC` X(32482) [`:13`]
occupying bytes 19-32500. `CA-POLICY-REQUEST` redefines that last item [`:34`], and `CA-POLICY-SPECIFIC` X(32400)
[`:44`] covers bytes 101-32500, which every product overlay redefines in turn.

The same generation step runs as part of the `translate` target of `modernization/Makefile` and inside
`modernization/harness/run_harness.sh`; both write the record under `modernization/harness/build/samples/`. The
rendered record is read by `modernization/harness/driver.cbl`.

## The stale-length safeguard

| Measurement | Value | Evidence |
|---|---|---|
| Declared `WS-MOTOR-LEN` | 65 | `base/src/lgpolicy.cpy:21` |
| Declared `WS-FULL-MOTOR-LEN` | 137 | `base/src/lgpolicy.cpy:26` |
| Header constant `WS-CA-HEADER-LEN` | 28 | `base/src/lgapdb01.cbl:65` |
| Length actually checked for `01AMOT` | 28 + 137 = 165 | `base/src/lgapdb01.cbl:182,195` |
| True end of the motor overlay | byte 177 | `base/src/lgcmarea.cpy:65-75` |
| Shortfall | 12 bytes | `CA-M-PREMIUM` 166-171 plus `CA-M-ACCIDENTS` 172-177 |
| Declared `WS-COMM-LEN` | 1102 | `base/src/lgpolicy.cpy:22` |
| Declared `WS-FULL-COMM-LEN` | 1174 | `base/src/lgpolicy.cpy:27` |
| Length actually checked for `01ACOM` | 28 + 1174 = 1202 | `base/src/lgapdb01.cbl:182,199` |
| True end of the commercial overlay | byte 1202 | `base/src/lgcmarea.cpy:77-94` |

Behaviour:

- the source constant is **never changed**;
- `modernization/extraction/build_sample_commarea.py` always emits the full 32,500-character record, so the premium and
  accidents bytes are present regardless of the declared length;
- `modernization/extraction/extract_commarea.py` validates that the applicable amount bytes are numeric before landing,
  and refuses a blank numeric window;
- every measurement in the table above is asserted rather than merely recorded: the builder refuses a field map whose
  `overlay_length` or `overlay_end_byte` disagrees with the overlay's own item declarations, whose recorded
  `actual_*_overlay_*` measurement disagrees with the layout, or whose recorded shortfall disagrees with the declared
  constants, and it does so on every load of the map — so a stale value fails the `translate` stage rather than passing
  unread.

The commercial constants are exact — 28 + 1174 = 1202 is the true end of that overlay — so the shortfall is specific to
motor. The motor overlay is 77 bytes (15 + 15 + 6 + 7 + 8 + 4 + 10 + 6 + 6) beginning at byte 101, and the commercial
overlay is 1102 bytes beginning at byte 101.

Decision record: `modernization/docs/decision-log.md`, row **D-08**.

## Sample scope

This folder holds two definitions, `commarea_01amot.json` and `commarea_01acom.json`, and
`modernization/extraction/build_sample_commarea.py` emits a record for those two request ids alone.

- **No endowment definition and no endowment record.** No endowment record is generated by the sample builder or by the
  harness runner, and no harness case executes the endowment route. A full-length COMMAREA drives
  `SUBTRACT WS-REQUIRED-CA-LEN FROM EIBCALEN GIVING WS-VARY-LEN` [`base/src/lgapdb01.cbl:339-340`] to 32,348 on that
  route — 28 + `WS-FULL-ENDOW-LEN` 124 [`base/src/lgpolicy.cpy:24`] = 152, and 32,500 − 152 = 32,348 — against
  `WS-VARY-CHAR PIC X(3900)` in a `PIC S9(4) COMP` receiver [`base/src/lgapdb01.cbl:71-72`]. Decision record:
  `modernization/docs/decision-log.md`, row **D-18**.
- **No house definition.** The house record used by the harness is not authored here and is emitted by no sample
  builder: `modernization/harness/run_harness.sh` derives it from the generated `01AMOT` record, as the
  `derived_samples` block of `modernization/extraction/copybook_field_map.yml` records. Decision record:
  `modernization/docs/decision-log.md`.

## Chain value constraints the samples respect

Facts about the source, for anyone editing a value here.

- `CA-CUSTOMER-NUM` and `CA-BROKERID` are `PIC 9(10)`, but the chain MOVEs them into `PIC S9(9) COMP` receivers —
  `base/src/lgapdb01.cbl:176` into the variable declared at `:90`, and `:264` into the variable declared at `:91`. A
  value of 1,000,000,000 or more loses its high-order digit there, and the COMMAREA value would then no longer match
  the SQL capture. Both samples stay at nine significant digits or fewer.
- `CA-ISSUE-DATE` and `CA-EXPIRY-DATE` are passed straight into Db2 DATE host variables
  [`base/src/lgapdb01.cbl:281-282`] and land in canonical `DATE` columns, so both must be valid ten-character ISO
  `YYYY-MM-DD` values.
- The six amount items are unsigned DISPLAY numerics with **no implied decimal**: `PIC 9(6)` for `CA-PAYMENT` and
  `CA-M-PREMIUM`, and `PIC 9(8)` for the four commercial premiums [`base/src/lgcmarea.cpy:43,73,85,87,89,91`]. Sample
  values are therefore whole numbers, and the canonical scale-2 values normally end in `.00`.
- **There is no premium formula anywhere in the authorized source.** The executable amount paths use direct `MOVE`
  statements only — `base/src/lgapdb01.cbl:265` for payment, `:445` for the motor premium and `:489,491,493,495` for the
  four commercial premiums — and the three programs contain no `COMPUTE`, `MULTIPLY` or `DIVIDE` statement. This is a
  finding of this work. No formula, factor or derived value is constructed, inferred or backfilled to fill the gap, in
  these samples or anywhere else in `modernization/`.

## Expected canonical outcome per sample

Amount values as they appear in `canonical.preissued_rating`.

| Sample | policy_type | payment_amount | motor_premium_amount | fire | crime | flood | weather |
|---|---|---|---|---|---|---|---|
| `01AMOT` | `M` | 500.00 | 450.00 | NULL | NULL | NULL | NULL |
| `01ACOM` | `C` | 1750.00 | NULL | 13500.00 | 3400.00 | 7800.00 | 2600.00 |

A product-inapplicable premium column is NULL, never zero. Both samples are expected to return `CA-RETURN-CODE` `00`.
The two relations these values reach are `canonical.issued_policy` and `canonical.preissued_rating`.

Decision record for the NULL treatment: `modernization/docs/decision-log.md`, row **D-54**.

## Related documents

- `modernization/docs/decision-log.md` — the single source of truth for every "why", including the stale-length
  handling (**D-08**), the digit-filling of the excluded peril codes (**D-12**), the endowment route (**D-18**), the
  deterministic identity and timestamp seeds (**D-19**), the chain-assigned window seeds (**D-35**) and the
  NULL-never-zero treatment (**D-54**).
- `modernization/docs/architecture.md` — holds **Figure 5 — Validation Harness Control Flow**, the figure that shows
  where sample generation sits in the flow.
- `modernization/extraction/extraction-spec.md` — the extraction specification, which owns the per-column target
  mapping this README does not repeat.
- `modernization/extraction/copybook_field_map.yml` — the machine-readable field map behind every offset, length, kind
  and contract rule quoted above.
- `modernization/extraction/build_sample_commarea.py` — the builder that enforces the contract and renders the record.
- `modernization/extraction/extract_commarea.py` — the extractor that decodes the returned COMMAREA.
- `modernization/harness/run_harness.sh` and `modernization/harness/driver.cbl` — the runner and driver that execute the
  chain over a rendered record.
- `modernization/validation/validation-evidence.md` — the evidence document that records what each case produced.
