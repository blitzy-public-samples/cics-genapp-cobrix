# Project Guide — GenApp Policy-Issue Canonical Warehouse Bridge

> **Status — validated against local substitute, not AWS.** The local-substitute branch is active: a moto S3 endpoint
> stands in for Amazon S3 and DuckDB stands in for Amazon Redshift. The formal AWS diff requirement is **OPEN**.
> Production-grade validation requires re-running the **same dbt models unmodified** against real S3 and real Amazon
> Redshift once access is granted, and **this has not yet happened**. Nothing in this document may be read as closing
> that requirement.

This is the integrative guide to the bridge: what was built, what was measured, what is still open, and how a future
source system is onboarded. Read it after `modernization/README.md`, which holds the entry point and the exact
setup commands.

Two conventions govern everything below, and both are deliberate.

- **Facts here, reasons elsewhere.** This guide states findings, facts, status and procedures. Every "why" belongs to
  [`decision-log.md`](decision-log.md), which is the single rationale source for the whole `modernization/` tree; where
  a reader would ask why a choice was made, this guide names the row that answers it (`D-01` … `D-65`). Construct-level
  and artifact-level source-to-target coverage belongs to [`traceability-matrix.md`](traceability-matrix.md) and
  column-level coverage to [`field-level-lineage.md`](field-level-lineage.md); neither is reproduced here.
- **Topology by figure, never by prose.** All five figures live in [`architecture.md`](architecture.md) and are cited
  here by their exact names. This guide draws no diagram.

Every claim below about the existing system carries an inline `[base/src/<file>:<locator>]` citation, and no citation in
this document points outside the five authorized source artifacts.

## Contents

1. [Status and mandatory labelling](#1-status-and-mandatory-labelling)
2. [What this is, and what it is not](#2-what-this-is-and-what-it-is-not)
3. [The no-formula finding](#3-the-no-formula-finding)
4. [Architecture: built and proposed](#4-architecture-built-and-proposed)
5. [The preserved interface](#5-the-preserved-interface)
6. [Environment, runtimes and how to run it](#6-environment-runtimes-and-how-to-run-it)
7. [Outstanding AWS status and the closure runbook](#7-outstanding-aws-status-and-the-closure-runbook)
8. [Onboarding a future source system](#8-onboarding-a-future-source-system)
9. [Encoding, representation and privacy](#9-encoding-representation-and-privacy)
10. [Validation — measured results and where the evidence lives](#10-validation--measured-results-and-where-the-evidence-lives)
11. [Success-criteria checklist](#11-success-criteria-checklist)
12. [Document map](#12-document-map)
13. [Standing non-goals](#13-standing-non-goals)

## 1. Status and mandatory labelling

The active branch is the local substitute, and every result this project has produced so far is labelled
**validated against local substitute, not AWS**.

| Item | State |
|---|---|
| Selected target of the run of record | `local_substitute` |
| S3 API surface | moto endpoint on the loopback interface, in place of Amazon S3 |
| Warehouse | DuckDB, in place of Amazon Redshift |
| Formal AWS diff requirement | **OPEN** |
| AWS infrastructure provisioned by this work | none: zero buckets, zero clusters, zero Serverless workgroups, zero networks, zero IAM objects |

The branch is not a build-time constant. `make gate` re-probes real S3 and real Amazon Redshift on every invocation and
records the selection in `modernization/validation/artifacts/gate-selection.json`, so the branch is a measured property
of each run (`D-05`); proceeding on the local branch rather than blocking is `D-07`.

Production-grade validation requires re-running the **same dbt models unmodified** against real S3 and real Amazon
Redshift once access is granted, and **this has not yet happened**. Until it has:

- **no document may present local-substitute results as closing the formal AWS diff requirement** — not this guide, not
  [`../validation/validation-evidence.md`](../validation/validation-evidence.md), not the published evidence set;
- the local run demonstrates the transform logic, the harness behaviour and the read-only guarantee, and nothing about a
  real target;
- the formal AWS diff stays **OPEN** in every checklist, including the one in
  [section 11](#11-success-criteria-checklist).

The ordered steps that close it are in [section 7](#7-outstanding-aws-status-and-the-closure-runbook). None of them
edits a model file.

## 2. What this is, and what it is not

The legacy CICS/COBOL/Db2/VSAM Issue chain remains authoritative and continues to own every operational write. This work
retires nothing, replaces nothing and changes no behaviour: it adds a **parallel analytical projection** that reads one
executed result of the chain and lands it in a canonical warehouse shape. The as-is chain is the subject of
**Figure 1 — BEFORE: GenApp Policy-Issue Chain, As-Is** and the bridge added beside it is the subject of
**Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge**, both in [`architecture.md`](architecture.md).

### 2.1 Built scope

Exactly **two** canonical relations exist: `canonical.issued_policy` with **11 columns** and
`canonical.preissued_rating` with **9 columns**. Both carry `source_system_key`.

| Relation | Columns | Column set |
|---|---:|---|
| `canonical.issued_policy` | 11 | `source_system_key`, `policy_number`, `policy_type`, `customer_number`, `request_id`, `return_code`, `issue_date`, `expiry_date`, `last_changed`, `broker_id`, `brokers_reference` |
| `canonical.preissued_rating` | 9 | `source_system_key`, `policy_number`, `policy_type`, `payment_amount`, `motor_premium_amount`, `fire_premium_amount`, `crime_premium_amount`, `flood_premium_amount`, `weather_premium_amount` |

One successful issued policy produces one row in each relation. `source_system_key` is the sole canonical column with no
COBOL origin (`D-03`); every other column traces to a named COBOL item, and
[`field-level-lineage.md`](field-level-lineage.md) carries that trace column by column. The enforced column contracts
live in `modernization/dbt/genapp_rqi/models/marts/canonical/_canonical__models.yml`, which is the only declaration of
the canonical column set.

### 2.2 Not in scope

Stated without elaboration; each exclusion has its row in [`decision-log.md`](decision-log.md).

- No third canonical relation and no source registry (`D-11`).
- No rating formula, no rating factor and no derived-factor column (`D-11`).
- No Quote model.
- No Loss build — the Loss domain appears only as a future domain in
  **Figure 3 — AFTER (PROPOSED, NOT BUILT): AWS-Native Multi-RQI Warehouse**.
- No commission field.
- No extra provenance column beyond the required `source_system_key`.
- The prior warehouse and every other RQI are out of scope.
- AWS Glue, orchestration and every future domain are **documented proposals, not built infrastructure** (`D-13`).

### 2.3 The read-only guarantee

The five authorized source artifacts are byte-identical to their state before this work, and no pre-existing repository
file is modified (`D-01`). Their verified baseline is 169 lines for `base/src/lgapol01.cbl`, 595 for
`base/src/lgapdb01.cbl`, 188 for `base/src/lgapvs01.cbl`, 103 for `base/src/lgcmarea.cpy` and 107 for
`base/src/lgpolicy.cpy`.

The guarantee is machine-enforced rather than asserted. `modernization/validation/verify_readonly.sh` is the live gate:
it compares the five SHA-256 hashes with the baseline it embeds, requires `git status --porcelain -- base/` to be empty
and requires `git diff --name-only HEAD` to hold no tracked modification outside the generated evidence it exempts. It
runs before any generated output, after each harness stage and as the final gate of `make all`.

## 3. The no-formula finding

The named chain contains **no premium or rating formula**. This is a measured finding, not an inference, and the
measurement is reproducible from the three programs.

### 3.1 The statement census

| Statement | `base/src/lgapol01.cbl` | `base/src/lgapdb01.cbl` | `base/src/lgapvs01.cbl` | Total |
|---|---:|---:|---:|---:|
| `COMPUTE` | 0 | 0 | 0 | **0** |
| `MULTIPLY` | 0 | 0 | 0 | **0** |
| `DIVIDE` | 0 | 0 | 0 | **0** |
| `ADD` | 1 | 5 | 0 | **6** |
| `SUBTRACT` | 0 | 1 | 0 | **1** |

The whole arithmetic surface of the corpus is those 6 `ADD` statements
[base/src/lgapol01.cbl:109; base/src/lgapdb01.cbl:182,187,191,195,199] and that 1 `SUBTRACT`
[base/src/lgapdb01.cbl:339-340]. Every one of the seven operates on a **length constant** — a COMMAREA header length or
a product record length — and not one of them touches an amount.

### 3.2 The amounts are passthroughs

The six amount values reach Db2 through plain `MOVE` statements and nothing else:

| Amount | Move |
|---|---|
| Payment | `MOVE CA-PAYMENT TO DB2-PAYMENT-INT` [base/src/lgapdb01.cbl:265] |
| Motor premium | `MOVE CA-M-PREMIUM TO DB2-M-PREMIUM-INT` [base/src/lgapdb01.cbl:445] |
| Fire premium | `MOVE CA-B-FirePremium To DB2-B-FirePremium-Int` [base/src/lgapdb01.cbl:489] |
| Crime premium | `MOVE CA-B-CrimePremium To DB2-B-CrimePremium-Int` [base/src/lgapdb01.cbl:491] |
| Flood premium | `MOVE CA-B-FloodPremium To DB2-B-FloodPremium-Int` [base/src/lgapdb01.cbl:493] |
| Weather premium | `MOVE CA-B-WeatherPremium To DB2-B-WeatherPremium-Int` [base/src/lgapdb01.cbl:495] |

The six declarations are unsigned display numerics with **no implied decimal**: `PIC 9(6)` for payment and motor premium
and `PIC 9(8)` for the four commercial premiums [base/src/lgcmarea.cpy:43,73,85,87,89,91]. An amount enters the chain
from the caller, is moved once and is written; the chain derives nothing.

### 3.3 The consequence

The gap is a finding, and it stays a finding:
**do not construct, infer, or backfill a rating formula to fill this gap.**
It is recorded in metadata and documentation — the field map, the extraction specification, the lineage document
and this guide — and never as an unsourced canonical data column (`D-11`). An analyst who expects a rating or factor
column should read its absence as the measurement above, not as an omission.

### 3.4 What is not an amount

The four commercial peril fields `CA-B-FirePeril`, `CA-B-CrimePeril`, `CA-B-FloodPeril` and `CA-B-WeatherPeril` are
`PIC 9(4)` **codes**, not amounts [base/src/lgcmarea.cpy:84,86,88,90], and they are excluded from the canonical amount
columns (`D-12`). The requested amounts are the adjacent `PIC 9(8)` premium items
[base/src/lgcmarea.cpy:85,87,89,91]. The harness stubs still accept the peril operands, which the named chain cannot
execute without, so their presence in a capture is expected.

## 4. Architecture: built and proposed

Three states are documented, and they are kept unmistakably distinct. All three figures live in
[`architecture.md`](architecture.md) with their legends.

### 4.1 Before

**Figure 1 — BEFORE: GenApp Policy-Issue Chain, As-Is** is the chain as it stands, unchanged by this work.

### 4.2 After, as built

**Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge** is what this work delivers. Two properties of the built path
are not visible in a figure and matter more than the topology:

- **The dbt model files are unchanged between the two targets.** The staging model, the intermediate model, both mart
  models, the source declaration, the singular tests and `macros/generate_schema_name.sql` are byte-identical whether
  the run targets DuckDB or Amazon Redshift; the target is selected by `DBT_TARGET` outside the models.
- **Engine-specific behaviour is confined to raw loading**, below dbt: `modernization/landing/load_local.py` inserts
  into DuckDB on the local branch and `modernization/landing/load_redshift.sql` issues a `COPY` on the real branch. Both
  derive the raw shape from one contract, `modernization/landing/landing-schema.json`, so a Redshift run is a
  configuration change and not a model edit (`D-09`).

### 4.3 After, as proposed — not built

**Figure 3 — AFTER (PROPOSED, NOT BUILT): AWS-Native Multi-RQI Warehouse** is a proposal. Nothing in it beyond the
built bridge exists:

- AWS Glue is **proposed only**; no Glue job, crawler or catalog is built or provisioned by this work.
- The Loss domain is a **future domain only**; no Loss relation, model or column is built.
- Future derived rating factors are **proposed only** for a source system that has an actual rating engine; none is
  created for this exemplar (`D-11`).
- Orchestration is recorded as an **explicitly flagged open decision** between **AWS Glue jobs**, **AWS Step Functions**
  and **Apache Airflow**, rather than a resolved choice. It is deliberately unresolved and this guide expresses no
  preference among the three (`D-14`).

### 4.4 The AWS provisioning cap

A standing constraint, independent of which branch is active:

| Branch | Permitted provisioning |
|---|---|
| Local substitute (active) | **None.** Nothing was provisioned; the gate probes and never provisions. |
| Real target | At most **one S3 bucket** and **one Amazon Redshift cluster or Serverless workgroup**, both pre-existing and named by configuration. |

No AWS Glue resource, no orchestration resource, no network and no IAM object is provisioned by this work on either
branch, and the bridge creates no bucket.

## 5. The preserved interface

Nothing in the interface changed. The facts below were read from the frozen sources and are reproduced by the harness
without a source edit; the rewrites the harness applies to its generated copies are the subject of
[`../harness/translation-rules.md`](../harness/translation-rules.md) (`D-06`).

### 5.1 The shared record

The three programs share one **32,500-byte** COMMAREA, laid out as `CA-REQUEST-ID` `X(6)` + `CA-RETURN-CODE` `9(2)` +
`CA-CUSTOMER-NUM` `9(10)` + `CA-REQUEST-SPECIFIC` `X(32482)` [base/src/lgcmarea.cpy:10-13]. The validated policy header
is **28 bytes** [base/src/lgapol01.cbl:59; base/src/lgapdb01.cbl:65].

### 5.2 Call order and link lengths

Both chain links pass `LENGTH(32500)` [base/src/lgapol01.cbl:121-124; base/src/lgapdb01.cbl:243-246]. `LGAPVS01` is
linked only after the policy insert [base/src/lgapdb01.cbl:219] and the product insert selected by request routing
[base/src/lgapdb01.cbl:223-241].

### 5.3 The VSAM projection

`LGAPVS01` writes a **64-byte** record under a **21-byte** key, the key being the request-type letter followed by the
customer number and the policy number [base/src/lgapvs01.cbl:25-30,135-141]. The two lengths are distinct and are never
interchanged: 64 is the record, 21 is the key.

### 5.4 The return-code contract

| Code | Observed meaning | Source sites | Exercised by the two executed samples |
|---|---|---|---|
| `00` | Success | [base/src/lgapol01.cbl:105; base/src/lgapdb01.cbl:172,293] | Yes, both cases |
| `70` | Policy insert returned SQLCODE −530 | [base/src/lgapdb01.cbl:296] | No |
| `80` | VSAM write response was not normal | [base/src/lgapvs01.cbl:144] | No |
| `90` | SQL failure; a subtype insert failure also abends `LGSQ` | [base/src/lgapdb01.cbl:301,390,428,474,548] | No |
| `98` | COMMAREA too short | [base/src/lgapol01.cbl:114; base/src/lgapdb01.cbl:211] | No |
| `99` | Unsupported request id | [base/src/lgapdb01.cbl:204,239] | No |

Two abend codes complete the contract: `LGCA` on a zero-length COMMAREA [base/src/lgapol01.cbl:101;
base/src/lgapdb01.cbl:168] and `LGSQ` on a subtype insert failure [base/src/lgapdb01.cbl:393,431,477,551].

**Coverage, stated plainly.** The two executed samples exercise `00` only. Every SQL stub of those two cases reported
`SQLCODE 0` and the VSAM write reported the normal response, so `70`, `90`, `98`, `99`, `80` and both `LGSQ` abend sites
are **documented from source but unexercised** by them. The harness case table carries ten further cases that reach the
remaining codes and both abends through deterministic injection (`D-20`), and the pipeline's `execute` stage does not
select them. The **endowment route is not executed** at all (`D-18`), and the **house route compiles but is not
executed**. No behaviour is claimed for an unexercised path.

### 5.5 The two post-chain values, and the record extraction reads

`CA-POLICY-NUM` and `CA-LASTCHANGED` do not exist in the request: both are assigned inside `INSERT-POLICY`, the first
from `IDENTITY_VAL_LOCAL()` and the second from a read-back of the inserted row [base/src/lgapdb01.cbl:307-321], so the
whole design extracts from the **returned** COMMAREA rather than from the request.

### 5.6 `policy_type` is derived, not carried

`policy_type` is not a COMMAREA field. `LGAPDB01` derives it from the request id — `01AEND` → `E`, `01AHOU` → `H`,
`01AMOT` → `M`, `01ACOM` → `C` — while validating the product length [base/src/lgapdb01.cbl:184-207], and `LGAPVS01`
independently takes the same letter with `Move CA-Request-ID(4:1) To WF-Request-ID` [base/src/lgapvs01.cbl:99].
Extraction reproduces that derivation and verifies it against the policy SQL capture (`D-50`).

## 6. Environment, runtimes and how to run it

### 6.1 Runtimes

The specification pins one runtime set; the run of record measured another on the host available to it. Both are stated,
and every difference is reported rather than hidden (`D-48`).

| Item | Pinned by the specification | Measured in the run of record |
|---|---|---|
| Operating system | Ubuntu 24.04 LTS | Ubuntu 25.10 |
| Python | 3.12.3 | 3.12.14, built from source; the host's configured apt suites carry no `python3.12` package |
| `cobc` (GnuCOBOL) | 3.1.2, the stable distribution package used by this project | 3.2.0 |
| `git` | 2.43.0 | 2.51.0 |
| `pip` in the virtual environment | 25.3 | 25.3 |

`cobc` was **not installed** in the environment observed when this work was planned, and it must be installed before
anything can be compiled — nothing in this project vendors a COBOL compiler. The per-item deviation table of the run of
record is in [`../validation/validation-evidence.md`](../validation/validation-evidence.md) §2.

### 6.2 The virtual environment

All Python and dbt tooling runs from `modernization/.venv` through explicit `.venv/bin/...` paths, so a non-interactive
shell cannot fall back to a system interpreter. `make verify-env` measures every runtime and every package pin of
`modernization/requirements.txt` and runs **before** the AWS gate: a missing tool, an interpreter or compiler outside
the accepted series, or any package version other than its pin ends the run at the first such finding, with the pinned
and the measured value named. It installs nothing.

### 6.3 The executable order

`modernization/README.md` holds the exact setup commands. [`../Makefile`](../Makefile) is the executable order,
invoked as `make -C modernization <target>`; its targets, in sequence, are:

`verify-env` → `gate` → `translate` → `compile` → `execute` → `extract` → `land` → `load` → `dbt` → `diff` →
`verify-readonly`, and `all`, which runs that sequence end to end.

`make all` runs every stage in the order above, interleaves `verify-readonly` between the stages, and **stops at the
first failure**. Callers may override `CASE`, `CASES`, `SOURCE_SYSTEM_KEY`, `EXTRACT_DATE`, `STAGE`, `COBC`, `DBT_TARGET`,
`DBT_PROFILES_DIR` and `HARNESS_STRICT_TOOL_VERSIONS`.

### 6.4 The compile contract

Recorded here in outline only; the rewrite rules and the harness limitations belong to
[`../harness/translation-rules.md`](../harness/translation-rules.md).

- Translated programs and stubs compile as callable modules with `cobc -m`; `harness/driver.cbl` compiles as an
  executable with `cobc -x`.
- Compiler options are fixed at `-std=ibm -ffold-copy=LOWER -ext cpy`. `harness/run_harness.sh` compiles with the same
  options plus `-fbinary-truncate` (`D-23`).
- `COB_LIBRARY_PATH` is set before execution so the driver resolves the compiled modules.
- Compilation reads only generated copies under `modernization/harness/build/**`; no source artifact is preprocessed in
  place (`D-06`).

### 6.5 The configuration contract

Every credential, endpoint, bucket, path and target selection is resolved from environment variables.
[`../dbt/genapp_rqi/profiles.example.yml`](../dbt/genapp_rqi/profiles.example.yml) is a **template**, not a profile: copy
it unchanged into the directory dbt reads profiles from, and supply values through the environment (`D-44`).
`modernization/README.md` lists the settings a run needs. By name and never by value:

| Group | Settings |
|---|---|
| AWS access | the standard AWS credential settings, `AWS_REGION` |
| Object storage | `S3_BUCKET` (an existing bucket; the bridge creates none), `S3_ENDPOINT_URL` (the loopback endpoint of the local branch) |
| Amazon Redshift | `REDSHIFT_HOST` or the Serverless workgroup endpoint, `REDSHIFT_PORT`, `REDSHIFT_DATABASE`, `REDSHIFT_USER`, `REDSHIFT_PASSWORD` or `REDSHIFT_CLUSTER_ID` with `REDSHIFT_IAM_PROFILE`, `REDSHIFT_SCHEMA`, and `REDSHIFT_IAM_ROLE` for the `COPY` |
| Local branch | `LOCAL_DUCKDB_PATH` |
| Selection and identity | `DBT_TARGET` (`local_substitute` or `redshift`), `DBT_PROFILES_DIR`, `SOURCE_SYSTEM_KEY` |

**No secret, credential, account identifier, ARN or real bucket name is committed to this repository**, and no recipe
prints one. Every value shown anywhere in this tree is a placeholder.

## 7. Outstanding AWS status and the closure runbook

### 7.1 The gate outcome

The gate measured the ambient environment and found no AWS access of any kind: no resolved credentials, no resolved
region, no configured S3 bucket, no Amazon Redshift cluster or Serverless workgroup, no named AWS profile, no `~/.aws`
directory and no AWS CLI. Both real-target probes failed. The local-substitute branch therefore applies and the
**formal AWS diff remains OPEN** (`D-07`).

### 7.2 What would select the real branch

The real target is selected only if **both** probes succeed:

| Probe | What it does |
|---|---|
| S3 | resolves credentials and region, accesses the configured bucket, then writes and deletes a task-scoped probe object |
| Amazon Redshift | connects to the configured cluster or workgroup, executes `SELECT 1`, then performs a task-scoped write probe that is rolled back or dropped |

If both succeed, the run does not start moto and does not use DuckDB. If either fails or is unavailable, the local branch
proceeds and the AWS diff stays OPEN. **The gate provisions nothing** — no bucket, cluster, workgroup, network or IAM
object — and it re-probes on every invocation rather than trusting an earlier observation (`D-05`).

### 7.3 The closure runbook

An ordered procedure. No step edits a dbt model file.

| # | Step |
|---|---|
| 1 | Set the AWS credential settings, `AWS_REGION` and `S3_BUCKET`, naming an existing bucket. |
| 2 | Set the Amazon Redshift connection settings that `profiles.example.yml` and `redshift-connector` read — host or Serverless workgroup endpoint, port, database, user and authentication, schema — plus `REDSHIFT_IAM_ROLE` for the `COPY` of `modernization/landing/load_redshift.sql`. Commit no value. |
| 3 | Unset the loopback endpoint setting and run `make -C modernization gate`. Both real-target probes must pass and the recorded selection must read `redshift`. |
| 4 | Run `land` for each case, writing the validated object under the real S3 prefix defined by [`../landing/partition-layout.md`](../landing/partition-layout.md). |
| 5 | Run `load`, which applies the schema and raw bootstrap of `modernization/warehouse/ddl/` and then the rendered statements of `modernization/landing/load_redshift.sql`, including the real `COPY`. |
| 6 | Select the Redshift dbt target and run `dbt run` and `dbt test` using the **same dbt models unmodified**. |
| 7 | Query `canonical.issued_policy` and `canonical.preissued_rating` on Amazon Redshift through `redshift-connector`. |
| 8 | Run the **same** comparison, `modernization/validation/diff_harness_vs_warehouse.py`, against the real target and attach the real-target logs to [`../validation/validation-evidence.md`](../validation/validation-evidence.md). |
| 9 | Change the formal AWS diff disposition from **OPEN** only after every gate above has passed. |

Until step 9 has been reached, every result of this project is labelled
**validated against local substitute, not AWS**. Production-grade validation requires re-running the **same dbt models
unmodified** against real S3 and real Amazon Redshift once access is granted, and **this has not yet happened**.

## 8. Onboarding a future source system

The procedure below is repeatable and is the intended route for the next RQI. It changes neither canonical table.

| Stage | Required action | Evidence |
|---|---|---|
| **Discover** | Locate the new system's issue path, the logic that carries its premium and payment values, and its executable validation boundary. | A named source inventory and scope approval. |
| **Specify** | Produce the same structured extraction specification: declarations, runtime status, types and source locators. | A reviewed source specification. |
| **Identify** | Assign a new `source_system_key`, **without changing either canonical table**. | The landing prefix carrying the new key, and a canonical sample row bearing it. |
| **Transform** | Build source-specific extraction and staging logic that lands in the same issued and preissued/rating contracts. | dbt contracts and lineage. |
| **Validate** | Compile and execute the new source where that is possible, then diff its own output against both transformed rows. | A source-system-specific validation report. |

**Extensibility guarantee.**
Each entity carries a source-system key so rows from a future RQI slot into the same tables without structural change.
`source_system_key` is the first element of the natural key on both relations, S3 objects land
under a `source_system_key=<value>` prefix, and staging is grouped by source system, so a new source adds rows and never
columns.

**Derived factors.** A future source system with an **actual** rating engine may add justified derived-factor columns to
the existing preissued/rating domain. **No such column is created for this exemplar**, and none may be added on the
strength of this one (`D-11`): no factor can be sourced from this chain, which is what the measurement in
[section 3](#3-the-no-formula-finding) records.

## 9. Encoding, representation and privacy

### 9.1 Character-set encoding

The local harness reads and writes the workstation character set of the host it runs on. A real z/OS extract would have
to decode the installation's EBCDIC CCSID instead; the documented default is **CCSID 285**. This is an assumption
recorded for a **future real extract** and it does not apply to the local run, which never sees EBCDIC data.

### 9.2 Amount representation and the comparison contract

| Property | Value |
|---|---|
| Canonical amount type | `DECIMAL` with scale 2, so values should normally end in `.00` (`D-55`) |
| Expected comparison outcome | exact equality |
| Acceptance threshold | ±0.01 |
| Absolute delta at or below 0.01 | passes, and is called out as unexpected |
| Absolute delta above 0.01 | fails |
| Product-inapplicable premium | `NULL`, never zero (`D-54`) |

The representation risk here is **encoding, not arithmetic**: the source amounts are whole-number display values moved
without computation (see [section 3](#3-the-no-formula-finding)), so a difference could only arise from how a value is
carried or decoded. The threshold and the treatment of an in-tolerance delta are `D-04`.

### 9.3 Privacy posture

No privacy conclusion follows from the narrow field set, and none is drawn here. Customer, policy and broker identifiers
may be personal data even without names or addresses.

- Extraction is limited to the values the two canonical relations require, and nothing else is read out of the COMMAREA.
- No credential and no real customer record is committed to this repository; the samples are authored fixtures.
- Masking, retention and access-control design are outside this task.
- **Any future field expansion requires a separate privacy and security review.**

### 9.4 A source finding operators should know: the stale motor length

The declared constants are `WS-MOTOR-LEN +65` [base/src/lgpolicy.cpy:21] and `WS-FULL-MOTOR-LEN +137`
[base/src/lgpolicy.cpy:26], so `LGAPDB01` validates the motor request against 28 + 137 = **165** bytes
[base/src/lgapdb01.cbl:182,195]. The motor overlay actually ends at byte **177**: starting at COMMAREA byte 101 it runs
make 15, model 15, value 6, registration 7, colour 8, cc 4, manufactured date 10, premium 6 and accidents 6 — a 77-byte
overlay [base/src/lgcmarea.cpy:65-75]. The **12-byte shortfall** is exactly `CA-M-PREMIUM` (6) plus `CA-M-ACCIDENTS`
(6), which places the premium under test beyond the length the program checks.

The source constant is unchanged, and the bridge always emits the full 32,500-byte sample record, so no run of this
project depends on the shortfall; extraction additionally validates that the applicable amount bytes are numeric before
landing (`D-08`). The consequence for a caller stands regardless: a caller that passes only the declared length leaves
the premium bytes unset and the chain still accepts the request. Operators of the legacy chain inherit that, not this
bridge.

## 10. Validation — measured results and where the evidence lives

Every result in this section carries the label **validated against local substitute, not AWS**, and none of them closes
the formal AWS diff requirement. The commands, the exact versions, the per-case captures, the per-column comparison and
the artifact index are recorded in [`../validation/validation-evidence.md`](../validation/validation-evidence.md); they
are not restated here.

| Gate | Result of the run of record | Status |
|---|---|---|
| `verify-env` | PASS, with each runtime deviation of [section 6.1](#61-runtimes) named | validated against local substitute, not AWS |
| `gate` | selected `local_substitute`; both real-target probes failed; nothing provisioned | validated against local substitute, not AWS |
| `verify-readonly`, at every stage | PASS; all five source hashes and line counts unchanged; no tracked modification | validated against local substitute, not AWS |
| `translate` and `compile` | the three translated programs, the twelve stubs and the driver built, with the modules as `cobc -m` and the driver as `cobc -x` | validated against local substitute, not AWS |
| `execute` | both samples traversed `LGAPOL01` → `LGAPDB01` → `LGAPVS01` with `CA-RETURN-CODE` `00`, the policy and product SQL captures present, a 64-byte VSAM record under a 21-byte key, and no abend | validated against local substitute, not AWS |
| `extract`, `land`, `load` | one landing record per case, one S3 object per case under the documented prefix, and both rows in `raw.genapp_policy_issue` | validated against local substitute, not AWS |
| `dbt` | `dbt run` and `dbt test` both PASS with no warning and no error | validated against local substitute, not AWS |
| `diff` | PASS: all 20 canonical column instances per case compared — 11 of `canonical.issued_policy` and 9 of `canonical.preissued_rating` — 40 of 40 across the two cases, zero column failures, nothing skipped, and no non-zero in-tolerance amount delta to disclose | validated against local substitute, not AWS |
| Formal AWS diff | **OPEN.** Not performed; no real target was reached | not closed by anything in this document |

The two executed samples are `01AMOT`, covering payment and the motor premium, and `01ACOM`, covering payment and all
four commercial premiums. No endowment sample is executed (`D-18`).

## 11. Success-criteria checklist

Every row carries its disposition, and every locally closed row carries the label
**validated against local substitute, not AWS**. The formal AWS diff is **OPEN** and is never shown as closed. The
recorded commands, versions and results behind these dispositions are in
[`../validation/validation-evidence.md`](../validation/validation-evidence.md).

| # | Criterion | Disposition | Status |
|---|---|---|---|
| 1 | Extraction specification covers both entities | Closed locally — [`../extraction/extraction-spec.md`](../extraction/extraction-spec.md) with the field map and the enforced contracts | validated against local substitute, not AWS |
| 2 | Exactly two canonical relations | Closed locally — schema `canonical` holds `issued_policy` and `preissued_rating` and nothing else | validated against local substitute, not AWS |
| 3 | Both relations populated correctly | Closed locally — one matching row per sample and relation, contract and data tests passing | validated against local substitute, not AWS |
| 4 | 100% field lineage | Closed locally — every source-derived column traced in [`field-level-lineage.md`](field-level-lineage.md); `source_system_key` is the sole warehouse-assigned exception | validated against local substitute, not AWS |
| 5 | Three programs compile and execute | Closed locally — every compile returned 0; both samples returned `00` with complete captures | validated against local substitute, not AWS |
| 6 | Currency comparison within ±0.01 | Closed locally — every amount delta 0.00; no non-zero in-tolerance delta to disclose | validated against local substitute, not AWS |
| 7 | Non-currency comparison exact after the documented normalisation | Closed locally — every non-amount value matched exactly | validated against local substitute, not AWS |
| 8 | **Formal AWS diff** | **OPEN while the local branch applies** — cannot close locally; requires the runbook of [section 7.3](#73-the-closure-runbook) | no AWS result exists |
| 9 | Local-substitute disclosure present | Required now, present — the exact label stands in the header, in [section 1](#1-status-and-mandatory-labelling), in [section 10](#10-validation--measured-results-and-where-the-evidence-lives) and in this checklist | validated against local substitute, not AWS |
| 10 | Project guide complete | Closed by review of this document — extraction and lineage pointers, the no-formula finding, built and proposed architecture, the AWS runbook and the onboarding procedure are all present | validated against local substitute, not AWS |
| 11 | Source preservation | Closed — five hashes and line counts unchanged at every gate run; no pre-existing tracked file modified | validated against local substitute, not AWS |
| 12 | Zero fabricated domains or formulas | Closed — no third relation, no registry, no Quote, no Loss build, no commission, no formula and no derived-factor column | validated against local substitute, not AWS |
| 13 | AWS infrastructure limit respected | Closed — nothing provisioned on this branch; at most one bucket and one Redshift target on the real branch | validated against local substitute, not AWS |

Rows 1 through 7 and 9 through 13 can close on the local branch. Row 8 cannot: it closes only against real S3 and real
Amazon Redshift, and no local result contributes to it.

## 12. Document map

| Document | What it owns |
|---|---|
| `modernization/README.md` | Entry point, environment setup and the commands to run the bridge |
| [`architecture.md`](architecture.md) | The five named Mermaid figures with their legends — the only place topology is drawn |
| [`decision-log.md`](decision-log.md) | All rationale: every non-trivial decision with its alternatives, reasoning and risk, `D-01` onward |
| [`traceability-matrix.md`](traceability-matrix.md) | Bidirectional source-to-target coverage, construct by construct and artifact by artifact |
| [`field-level-lineage.md`](field-level-lineage.md) | Per-column lineage from each canonical column to its COBOL item and locator |
| [`../extraction/extraction-spec.md`](../extraction/extraction-spec.md) | The extraction specification: the interface grid, the field reconciliation, the no-formula finding and the landing contract |
| [`../harness/translation-rules.md`](../harness/translation-rules.md) | The source-to-generated rewrites and the harness limitations |
| [`../landing/partition-layout.md`](../landing/partition-layout.md) | The S3 key layout and its partition prefixes |
| [`../validation/validation-evidence.md`](../validation/validation-evidence.md) | Executed evidence: commands, versions, measured results, statuses and open items |
| This document | What was built, what was measured, what is open, and how a future source system is onboarded |

## 13. Standing non-goals

No throughput, service-level, cost or scheduling target is stated anywhere in this project, and none is invented here.
Scalability is structural only: `source_system_key` in the grain of both relations, source-system prefixes in S3,
staging grouped by source system, Redshift automatic table optimization until a measured workload justifies otherwise
(`D-10`), and one landed record producing one row in each canonical relation with no cross-record join.
