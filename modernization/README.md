# GenApp Policy-Issue Cloud-Warehouse Bridge

Entry point for everything under `modernization/`. It holds the exact setup commands, the precondition-gate
check and the `make all` workflow. The integrative guide is [`docs/project-guide.md`](docs/project-guide.md);
every "why" in this tree lives in [`docs/decision-log.md`](docs/decision-log.md), the single rationale source.
This file records what the bridge is, what was measured and how to run it.

> **Status — validated against local substitute, not AWS.** The local-substitute branch is active: a moto S3
> endpoint stands in for Amazon S3 and DuckDB stands in for Amazon Redshift. The formal AWS diff requirement is
> **OPEN**. Production-grade validation requires re-running the **same dbt models unmodified** against real S3
> and real Amazon Redshift once access is granted, and **this has not yet happened**. Nothing in this tree may
> be read as closing that requirement: a local-substitute diff result never satisfies the formal AWS diff
> requirement, and no document here presents one as satisfying it.

**Measured gate outcome.** In this checkout there is no `aws` CLI, no `~/.aws` directory, no resolvable
credentials and no region, no `S3_BUCKET` and no `REDSHIFT_*` configuration. Both real-target probes fail, the
local-substitute branch (moto plus DuckDB) applies, and the formal AWS diff stays **OPEN**. The recorded
selection stands in `validation/artifacts/gate-selection.json`.

---

## 1. What this tree is

An additive S3 → dbt → warehouse projection of the fixed GenApp CICS Policy-Issue chain
`LGAPOL01` → `LGAPDB01` → `LGAPVS01`. The chain is executed as an oracle under GnuCOBOL, the post-chain
COMMAREA is extracted, one source record lands in S3, and the same dbt models populate exactly two canonical
relations. No byte of the legacy source changes and no legacy behaviour is replaced: the CICS chain remains the
authoritative operational writer of Db2 and VSAM, and this tree reads one executed result to build an
analytical representation of it.

Topology is documented as diagrams, not prose. See, all in [`docs/architecture.md`](docs/architecture.md):

- **Figure 1 — BEFORE: GenApp Policy-Issue Chain, As-Is** — the named chain before this work.
- **Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge** — what this tree delivers.
- **Figure 5 — Validation Harness Control Flow** — the executable order and the comparison gate.

That document also carries **Figure 3 — AFTER (PROPOSED, NOT BUILT): AWS-Native Multi-RQI Warehouse** and
**Figure 4 — dbt Transformation DAG and Field Allocation**. Figure 3 is a proposal and is marked as one: the
AWS Glue catalog, the orchestration choice, the Loss domain and derived rating factors it shows are not built
by this work and exist nowhere in this tree.

## 2. The read-only source boundary

Five source artifacts are authorized, read-only inputs. They are byte-identical to their committed state. The
SHA-256 baseline and line counts below were measured in this checkout:

| File | Lines | SHA-256 |
|---|---:|---|
| `base/src/lgapol01.cbl` | 169 | `4dddd29539dd96aaec9f6885d3d62d19d40a1c6c888636623164bc5f5b232f6f` |
| `base/src/lgapdb01.cbl` | 595 | `3d21ad353a03c63d05defc511372e14477613fa4c51068a51a84d3c840c29815` |
| `base/src/lgapvs01.cbl` | 188 | `e0bca62eed2d6390852befdbaddd684833040c8be183d23f4fca368834709215` |
| `base/src/lgcmarea.cpy` | 103 | `4ecc9ed8dbf0936a8b0738cbb03a947e937206100b0e34f749fbb9e0b03f701d` |
| `base/src/lgpolicy.cpy` | 107 | `717c8f5c50738a2ef4d432e4b397e21bdc0423a9fc789246eb3360aa3f99eaa5` |

Reproduce it with `sha256sum` and `wc -l` over those five paths from the repository root.

Operating rules of the boundary:

- No pre-existing repository file is modified. Every authored artifact of this work is a new file under
  `modernization/`. The repository-root documentation is untouched, and this file is the discoverability
  surface for the bridge.
- The three programs are never preprocessed in place. Translation writes read-only copies, with the two
  copybooks, into `harness/build/**` only.
- [`validation/verify_readonly.sh`](validation/verify_readonly.sh) is the guard. It checks the five hashes, an
  empty `git status --porcelain -- base/` and the absence of any tracked modification. `make all` runs it after
  each generating stage and as the final gate; run it directly with `bash validation/verify_readonly.sh
  --stage <name>`, and `--self-test` exercises the script itself.

### The measured no-formula finding

The three programs contain **zero** `COMPUTE`, `MULTIPLY` and `DIVIDE` statements. Every amount reaches Db2
through a plain `MOVE` into a binary integer host variable — `CA-PAYMENT` at `base/src/lgapdb01.cbl:264-265`,
`CA-M-PREMIUM` among the motor moves at `base/src/lgapdb01.cbl:443-446`, and the four commercial premiums at
`base/src/lgapdb01.cbl:488-496`. No rating formula, rating factor or derived-factor column is constructed,
inferred or backfilled anywhere in this tree. The full accounting is in
[`extraction/extraction-spec.md`](extraction/extraction-spec.md).

## 3. Environment setup

Non-interactive, from the repository root. This is the pinned procedure:

```bash
DEBIAN_FRONTEND=noninteractive apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install --reinstall -y \
    python3.12=3.12.3-1ubuntu0.15 python3.12-venv=3.12.3-1ubuntu0.15 \
    gnucobol3=3.1.2-5.1ubuntu1 git=1:2.43.0-1ubuntu7.3
python3.12 -m venv --clear modernization/.venv
. modernization/.venv/bin/activate
python -m pip install --upgrade pip==25.3
python -m pip install -r modernization/requirements.txt
```

On the host of this checkout — Ubuntu 25.10 "questing" — the four apt pins of that block do not resolve: the
package set carries no `python3.12` and no `python3.12-venv`, and the pinned `gnucobol3` and `git` versions are
absent from its archive, so the `apt-get install` line ends in the resolver with exit status 100 and installs
nothing. *Measured state of this checkout*, below, records what this host carries instead, and `make verify-env`
records each of these as a deviation and still passes. The `apt-get update` line and the four
virtual-environment lines of the block run unchanged here.

`modernization/requirements.txt` carries ten exact `==` pins: dbt-core 1.12.2, dbt-duckdb 1.11.0,
dbt-redshift 1.11.0, duckdb 1.5.5, redshift-connector 2.1.16, boto3 1.43.74, botocore 1.43.74,
moto[s3,server] 5.2.2, PyYAML 6.0.3 and jsonschema 4.26.0. After installation, `pip check` reports no broken
requirements.

Every recipe of the Makefile calls tools through explicit `.venv/bin/...` paths, and a non-interactive shell
cannot fall back to a system interpreter. Measured facts about the interpreters of this checkout: the system
interpreter is Python 3.13.7 at `/usr/bin/python3`, it carries `boto3` and `botocore` 1.43.78 against the pinned
1.43.74, and `duckdb`, `moto`, `redshift-connector` and `dbt` are absent system-wide. All ten pins are installed
inside `modernization/.venv`, whose interpreter and `pip` measure 3.12.14 and 25.3.

### Measured state of this checkout

| Component | Pin | Measured here |
|---|---|---|
| operating system | Ubuntu 24.04 package set | Ubuntu 25.10; apt carries no `python3.12` package |
| `python3.12` | 3.12.3 (`3.12.3-1ubuntu0.15`) | 3.12.14 at `/usr/local/bin/python3.12`, built from source |
| `cobc` (GnuCOBOL) | 3.1.2.0 (`gnucobol3` 3.1.2-5.1ubuntu1) | 3.2.0 at `/usr/bin/cobc`, from `gnucobol3` 3.2-4, installed |
| `git` | 2.43.0 (`1:2.43.0-1ubuntu7.3`) | 2.51.0 (`1:2.51.0-1ubuntu1`) |
| `pip` | 25.3 | 25.3 in `modernization/.venv` |
| apt package lists | populated | populated |
| the ten Python pins | see `requirements.txt` | each installed at its exact pin in `modernization/.venv` |

`make verify-env` measures every value above and writes `validation/artifacts/verify-env.txt`. A missing tool,
an interpreter or compiler outside the accepted series, and any package version other than its pin each end the
run at the first such finding, with the pinned and the measured value named. A tool version inside the accepted
series that differs from its pin is recorded as a deviation and the stage passes; this checkout records seven
deviations (`python3.12`, `cobc`, `git` and four apt package pins) and passes. Setting
`HARNESS_STRICT_TOOL_VERSIONS` makes a deviation end the run as well. `verify-env` installs nothing.

## 4. The `make` workflow

Run every target from the `modernization/` directory. The Makefile requires that working directory and names
the invocation in its own error message when it is called from elsewhere:

```bash
make -C modernization all          # the whole order, stopping at the first failure
make -C modernization verify-env   # one stage
```

The `land` and `load` stages address an S3 API and an existing bucket. §5.1 supplies both on the
local-substitute branch — through the optional `local-endpoint` target or the manual equivalent beside it — and
`make all` reaches `land` only with them in place. With the bucket or the endpoint setting missing on that
branch, `make land` and `make load` each end the run naming the missing setting and naming `local-endpoint`.

| Target | What it does |
|---|---|
| `verify-env` | Measures `python3.12`, `cobc`, `git`, the virtual environment, `pip` and every pin of `requirements.txt`, and writes `validation/artifacts/verify-env.txt`. Installs nothing. |
| `gate` | Runs the two real-target probes, selects `redshift` when both pass and `local_substitute` otherwise, and records the selection and probe results in `validation/artifacts/gate-selection.json`, which `land`, `load`, `dbt` and `diff` read. Provisions nothing. |
| `translate` | Writes the two 32,500-character sample records and translates read-only copies of the three programs, with the two verbatim copybooks, into `harness/build`. |
| `compile` | Compiles the three translated programs and the twelve stubs as callable modules and `harness/driver.cbl` as an executable, keeping the compiler output including warnings in `validation/artifacts/compile-modules.log`. |
| `execute` | Runs `harness/run_harness.sh` for the case selection named by `CASES_MODE` — by default every case of the authored table — then asserts the per-case pass conditions of §4.3 and that the harness executed the selection it was asked for. |
| `extract` | Decodes the post-chain COMMAREA of each case into one landing record under `harness/build/landing`. |
| `land` | Writes the landing record of the case named by `CASE` as one S3 object under the landing prefix, at the part number this Makefile records for that case, through the endpoint the selected run mode requires. |
| `load` | Loads the landed object of the case named by `CASE`, at that same part number, into `raw.genapp_policy_issue`. The only target-specific stage; it edits no dbt model file. |
| `dbt` | Cleans the dbt project, then runs and tests it against the selected target, keeping the output under `validation/artifacts`. |
| `diff` | Compares the harness captures of both cases with the two canonical rows and writes `validation/artifacts/diff-report.md` and `diff-report.json`. |
| `verify-readonly` | Runs `validation/verify_readonly.sh` for the stage named by `STAGE`: the five source hashes, an empty `git status --porcelain -- base/` and no tracked modification. |
| `all` | Runs every stage above in the recorded order and stops at the first failure. |
| `local-endpoint` | Optional, local-substitute branch only, and no stage of `all`: starts the pinned `moto` server of the virtual environment at `S3_ENDPOINT_URL` when nothing answers there, keeping its log under `harness/build/logs`, then creates the bucket named by `S3_BUCKET` when that bucket is absent. Both settings are required; the endpoint has to be a loopback `http://` URL on a port of 1024 or above, and a non-loopback endpoint or a `DBT_TARGET` of `redshift` ends the run. Re-running it changes nothing once the endpoint answers and the bucket exists, and it provisions nothing on AWS. |

Overridable variables: `CASE`, `CASES`, `CASES_MODE`, `SOURCE_SYSTEM_KEY`, `EXTRACT_DATE`, `STAGE`, `COBC`,
`DBT_TARGET`, `DBT_PROFILES_DIR`, `HARNESS_STRICT_TOOL_VERSIONS`. Connection settings are read from the
environment alone (§5). No recipe is interactive, none installs a package and none provisions an AWS resource.

`CASES_MODE` selects what the `execute` stage runs. It accepts two values and refuses any other, naming both:

| Value | What runs | Measured here |
|---|---|---|
| `all` (default) | every case of the authored table — the two success cases plus the ten return-code, abend and route characterisation cases | 12 cases, 902 assertions |
| `success-only` | the two success cases `01AMOT` and `01ACOM` alone, the fast path | 2 cases, 243 assertions |

Both values publish the same evidence set, because only a success case carries a capture file, a driver log and
a post-chain record. `make all` inherits the default, so the observed return-code contract — `00`, `70`, `80`,
`90`, `98`, `99` and the `LGSQ` abend — is exercised by the one documented entry point rather than only by a
direct invocation of the script.

### 4.1 Executable order

1. Environment verification
2. AWS gate
3. Source baseline
4. Samples
5. Translate
6. Compile
7. Execute
8. Extract
9. Land
10. Raw load
11. dbt `run` and `test`
12. Diff
13. Read-only verification
14. Evidence and documentation finalization

The first failure stops `make all`. Within that order `make all` re-runs `verify-readonly` after each
generating stage, under the stage labels `baseline`, `translate`, `compile`, `execute`, `load`, `dbt` and
`final`, and it runs `land` and `load` once per case.

### 4.2 The two executed cases

| Case | Amount coverage |
|---|---|
| `01AMOT` | payment and the motor premium |
| `01ACOM` | payment and all four commercial premiums — fire, crime, flood and weather |

No endowment sample exists. Sample values and the record-length facts are documented in
[`extraction/sample_input/README.md`](extraction/sample_input/README.md).

These two are the cases the extraction, landing, warehouse and comparison stages consume. The remaining ten
cases of the authored table are characterisation cases: they assert the return code, the abend and the routing
the chain produces on a path that issues no policy, so they publish no landing record. `CASES_MODE=all` runs
all twelve; `CASES_MODE=success-only` runs these two.

### 4.2.1 Identity and timestamp seeds, and the capture snapshots

The harness assigns each case a deterministic policy number and timestamp. `HARNESS_POLICY_NUMBER` overrides the
identity seed of the first case — parallel checkouts of this repository each take their own seed — and
`HARNESS_LASTCHANGED` overrides the timestamp seed. Both are supported on any run, including `make all`:

```bash
HARNESS_POLICY_NUMBER=1000101 make -C modernization all
```

The per-case capture snapshots under `validation/expected/` are **seed-independent**. Each records the run's
assigned identity and timestamp as a symbol — `<policy-number:10>` where the ten-digit `CA-POLICY-NUM` form
stands, `<policy-number>` for the digits alone, `<last-changed>` for the 26-character timestamp, and the
composite VSAM key as its literal type letter and customer digits followed by the padded symbol — and every
other captured value literally. A run under any seed therefore matches the committed snapshot, leaves it
byte-identical, and still fails the diff stage on any other drift.

A snapshot needs re-baselining only when the harness output legitimately changes shape — a new capture key, a
renamed window, a changed fixture value. That is an explicit action, never a side effect of a run:

```bash
# from modernization/, after a clean `make all`
make --dry-run diff        # prints the argument list the stage uses
.venv/bin/python validation/diff_harness_vs_warehouse.py --cases 01AMOT,01ACOM \
  --run-dir modernization/harness/build/run \
  --field-map modernization/extraction/copybook_field_map.yml \
  --target duckdb --database modernization/validation/local.duckdb \
  --source-system-key GENAPP_CLASS_EXEMPLAR \
  --report modernization/validation/artifacts/diff-report.md \
  --json modernization/validation/artifacts/diff-report.json \
  --expected-dir modernization/validation/expected --refresh-snapshot
```

`--refresh-snapshot` rewrites the snapshot of each compared case, reports it as `refreshed` and compares nothing
for that case; review `git diff modernization/validation/expected` and commit the result. Without the option a
present snapshot is compared and never rewritten, an absent one is written, and a difference fails the stage
naming every differing key.

### 4.3 Pass conditions to expect

Per executed case:

- the sample traverses all three programs, `LGAPOL01` → `LGAPDB01` → `LGAPVS01`;
- `CA-RETURN-CODE` is `00`;
- the policy SQL capture and the product SQL capture are present;
- the returned COMMAREA carries an assigned policy number and a 26-character timestamp;
- the VSAM capture is 64 bytes and its key is the request-type letter followed by the customer number and the
  policy number;
- no abend is recorded.

Then, for the run as a whole: dbt `run` and `dbt test` complete with zero errors and zero warnings, and the
diff passes with each of the six amount deltas within ±0.01. A non-zero delta inside that tolerance passes and
is reported as unexpected. `validation/artifacts/diff-report.md` and `diff-report.json` carry the verdict, and
[`validation/validation-evidence.md`](validation/validation-evidence.md) carries the executed run.

### 4.4 Compile facts

The compiler flags are the four mandated options `-std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy`. The
three translated programs and the twelve stubs are compiled as callable modules with `cobc -m`,
`harness/driver.cbl` is compiled as an executable with `cobc -x`, and `COB_LIBRARY_PATH` is set to the module
directory before execution. `harness/run_harness.sh`, which `make execute` invokes, builds the modules it runs
under the same four options and additionally pins the compiler environment for that build. The rewrites the
translated copies carry are documented in [`harness/translation-rules.md`](harness/translation-rules.md).

## 5. Configuration contract and the AWS gate

Every connection value is supplied by the environment. No credential, bucket name, host name, role identifier
or password appears in any file of this tree, and no stage prints a credential, an endpoint URL, a host name, a
role identifier or a password. Two stages do print the destination they address: `land` names the bucket and its
region in its `addressing bucket` line and repeats the bucket name in the `s3://` object URI it prints last, and
`load` names the same bucket and region in its `reading bucket` line while redacting the object URI, the
source-system key and the policy number.

| Setting | Read by | Notes |
|---|---|---|
| AWS credentials — `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, optionally `AWS_SESSION_TOKEN` or `AWS_PROFILE` | the gate and the landing tooling | resolved by botocore in its own order; no value is committed |
| `AWS_REGION` | the gate and the landing tooling | region of the bucket, and of the cluster under IAM authentication |
| `S3_BUCKET` | the landing tooling | an existing bucket; this bridge creates none |
| `S3_ENDPOINT_URL` | the landing tooling | the loopback S3-compatible endpoint of the local-substitute branch; unset for AWS S3 |
| `SOURCE_SYSTEM_KEY` | every stage from extraction onward | defaults to `GENAPP_CLASS_EXEMPLAR` |
| `DBT_TARGET` | dbt, the landing writer and the raw loader | `local_substitute` or `redshift`; defaults to `local_substitute` |
| `LOCAL_DUCKDB_PATH`, and `DUCKDB_DATABASE` when the first carries no value | the local raw loader and the dbt profile | with neither set, the database is the repository-relative path `modernization/validation/local.duckdb`. Either variable is accepted carrying that relative form — `modernization/validation/<file>` — or an absolute path ending in those same three components; any other value, including one with a `..` component or one naming a directory below `modernization/validation`, ends the run naming the variable it came from, the accepted forms and the value supplied. A relative value resolves against the working directory of the process that reads it, so dbt is invoked from the repository root, naming the project with `--project-dir modernization/dbt/genapp_rqi`; the `dbt` and `load` targets of the Makefile pass the absolute form themselves |
| `REDSHIFT_HOST`, `REDSHIFT_DATABASE`, `REDSHIFT_USER`, `REDSHIFT_PASSWORD`, `REDSHIFT_SCHEMA` | the dbt profile and `redshift-connector` | no default; an unset value ends the run before a connection is opened |
| `REDSHIFT_PORT`, `REDSHIFT_CONNECT_TIMEOUT`, `REDSHIFT_RETRIES` | the dbt profile | default to 5439, 30 seconds and 1 retry |
| `REDSHIFT_CLUSTER_ID`, `REDSHIFT_IAM_PROFILE` | the dbt profile under IAM authentication | read only while the IAM keys of the profile are uncommented |
| `REDSHIFT_IAM_ROLE` | `landing/load_redshift.sql` | the role the real-target `COPY` assumes |
| `WAREHOUSE_TARGET` | `validation/diff_harness_vs_warehouse.py` | `duckdb` or `redshift`, read only when `--target` is absent; the `diff` target of the Makefile always passes `--target`, so this applies to a direct invocation of the comparison gate. Defaults to `duckdb` |
| `GENAPP_SHOW_IDENTIFIERS` | `extraction/extract_commarea.py` | `1`, `true`, `yes` or `on` — any case, surrounding spaces ignored — carries the business identifiers onto the summary line and record values into diagnostics, the same effect as `--show-identifiers`. Any other value, an empty value and an absent variable leave `policy_number`, `customer_number`, `broker_id` and `brokers_reference` withheld, with the policy number reported as a `sha256-` digest. The extractor is the only tool that reads it; see `docs/project-guide.md` §9.3 |

The template that resolves these is [`dbt/genapp_rqi/profiles.example.yml`](dbt/genapp_rqi/profiles.example.yml).
Copy it unchanged to `profiles.yml` in the directory dbt reads profiles from; the copy needs no edit and carries
no credential. That directory is `~/.dbt` by default, and dbt ends the run with `Invalid value for
'--profiles-dir': Path '<home>/.dbt' does not exist` when it is not there; `DBT_PROFILES_DIR` names a different
directory instead, and the `dbt` target passes the directory it names on to dbt. Do not create a `profiles.yml`
inside this repository tree.

### 5.1 Local-substitute prerequisites

`land` and `load` address an S3 API and an existing bucket on either branch, and this bridge creates no bucket.
On the local-substitute branch, supply both from the pinned `moto` of the virtual environment before running
`make all`. From the repository root, with `<port>` a free loopback port of 1024 or above and `<bucket>` a name
of your choosing:

```bash
export AWS_ACCESS_KEY_ID=<any-non-empty-value> AWS_SECRET_ACCESS_KEY=<any-non-empty-value>
export AWS_REGION=<region-name> AWS_DEFAULT_REGION="$AWS_REGION"
export S3_ENDPOINT_URL=http://127.0.0.1:<port>
export S3_BUCKET=<bucket>
make -C modernization local-endpoint
make -C modernization all
```

`local-endpoint` starts the endpoint only when nothing answers at `S3_ENDPOINT_URL` and creates the bucket only
when it is absent, so running it again over a live endpoint changes nothing; the server log stays under
`modernization/harness/build/logs`. It serves the local-substitute branch alone: a non-loopback endpoint, or
`DBT_TARGET` naming `redshift`, ends the run, and it provisions nothing on AWS. It is no stage of `all`.

The explicit alternative starts the same server and creates the same bucket by hand, with the four exports above
already in place:

```bash
setsid nohup modernization/.venv/bin/python -m moto.server -H 127.0.0.1 -p <port> \
    > "${TMPDIR:-/tmp}/moto-$$.log" 2>&1 < /dev/null &
modernization/.venv/bin/python - <<'PY'
import os, boto3
boto3.client("s3", endpoint_url=os.environ["S3_ENDPOINT_URL"],
             region_name=os.environ["AWS_REGION"]).create_bucket(Bucket=os.environ["S3_BUCKET"])
PY
```

The log path carries the process id of the shell that starts the server, so parallel operators and parallel
clones on one host each keep their own log instead of overwriting one shared file.

The endpoint holds its objects in memory: restarting it discards every bucket and object, and the bucket has to
be created again. Placeholder credentials are what the loopback endpoint accepts; they reach no AWS service, and
the gate treats them as the local branch. `make land` and `make load` each end the run with the setting named,
and with `local-endpoint` named, when `S3_BUCKET` is unset, or when `S3_ENDPOINT_URL` is unset on the
local-substitute branch.

**Gate behaviour.** `make gate` re-runs before build work and is the one selector of the run:

- The real branch is selected only when **both** probes succeed. The S3 probe resolves credentials and a
  region, reaches the configured bucket, then writes and deletes a task-scoped probe object. The Redshift probe
  connects to the configured cluster or Serverless workgroup, executes `SELECT 1`, and makes a write probe that
  is rolled back or dropped.
- Either probe failing or being unavailable selects the local-substitute branch, and the formal AWS diff stays
  **OPEN**.
- With both real probes passing, no moto endpoint and no DuckDB database is started.
- `DBT_TARGET=redshift` with a probe that did not pass ends the run at the gate.
- The gate provisions nothing: no bucket, cluster, workgroup, network or IAM object. On the real branch the
  provisioning ceiling for the whole bridge is one bucket and one Redshift target, both pre-existing.

**A measured trap.** This environment exports `AWS_ANTHROPIC_API_URL`, `AWS_ANTHROPIC_API_KEY` and
`AWS_ANTHROPIC_WORKSPACE_ID`. These are **not** AWS credentials and grant no AWS access. The presence of an
`AWS_`-prefixed variable is never evidence of AWS access; only the two gate probes are.

The step-by-step runbook for closing the AWS validation, once real values exist, is in
[`docs/project-guide.md`](docs/project-guide.md). It is not duplicated here.

## 6. What gets built

**One landed object per case**, under an S3 key prefix of exactly this shape:

```text
s3://<bucket>/landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=YYYY-MM-DD/part-<NNNN>.json
```

`part-<NNNN>` is the part element of the object name, four zero-padded digits selected by `--part` on the landing and
loading tools and `0000` when no part is named, so a single-record landing writes exactly `part-0000.json`. `make all`
lands `01amot` at part `0000` and `01acom` at part `0001`, each with its own `part-<NNNN>.manifest.json` beside it, so
both objects of a two-sample run coexist and either can be reloaded on its own. Partitioning applies to the S3 key
prefix only; no warehouse object is partitioned. The full key contract is in
[`landing/partition-layout.md`](landing/partition-layout.md).

**One raw relation.** `raw.genapp_policy_issue` holds every landed field as `VARCHAR`.

**Exactly two canonical relations**, built by the dbt marts:

| Relation | Content |
|---|---|
| `canonical.issued_policy` | the policy and request identity of one issued policy: policy number, policy type, customer number, request id, return code, issue and expiry dates, last-changed timestamp, broker id and brokers reference |
| `canonical.preissued_rating` | the six amount values — payment, motor premium and the fire, crime, flood and weather premiums — with the policy number and policy type that identify them |

Both relations carry `source_system_key`, both are filtered to `return_code = '00'`, and the grain of each is
one row per `(source_system_key, policy_number)`. Product-inapplicable premium columns are **NULL, never zero**.
No third canonical relation exists, including any source-system registry, and no formula, rating-factor,
derived-factor, commission, Quote or Loss column exists in either relation. A future source system slots into
these same two tables under its own `source_system_key`, with no structural change.

Raw loading is the only target-specific stage. The dbt model files, the source declaration, the singular tests
and `macros/generate_schema_name.sql` are identical for both targets, and the models are what create the
canonical tables. Column-level allocation is drawn in **Figure 4 — dbt Transformation DAG and Field
Allocation** in [`docs/architecture.md`](docs/architecture.md).

### 6.1 Each tool proves its own gates

Every command-line tool of this tree carries a `--self-test` that drives its checks in process against
constructed inputs. It needs no warehouse, no S3 endpoint and no harness output, writes only inside a directory
it creates and removes, and returns its own exit status when one of its own cases does not hold — a status no
ordinary run returns. These are the case counts measured in this checkout:

| Command | Cases |
|---|---:|
| `bash validation/verify_readonly.sh --self-test` | 52 |
| `.venv/bin/python extraction/build_sample_commarea.py --self-test` | 114 |
| `.venv/bin/python extraction/extract_commarea.py --self-test` | 213 |
| `.venv/bin/python harness/translate.py --self-test` | 93 |
| `.venv/bin/python landing/land_to_s3.py --self-test` | 44 |
| `.venv/bin/python landing/load_local.py --self-test` | 38 |
| `.venv/bin/python validation/diff_harness_vs_warehouse.py --self-test` | 34 |

The dbt project's own gates are its four enforced contracts and its 64 data tests, run by `make dbt`. `make all`
runs the pipeline rather than the self-tests: a self-test proves that a gate can fail, and the pipeline proves
that it does not fail on the delivered tree.

## 7. Where everything is documented

| Document | Content |
|---|---|
| [`docs/project-guide.md`](docs/project-guide.md) | the integrative guide: built and proposed architecture, the no-formula finding, outstanding AWS status, the AWS closure runbook and the future-source onboarding procedure |
| [`docs/architecture.md`](docs/architecture.md) | all five named Mermaid figures, each with a visible legend |
| [`docs/decision-log.md`](docs/decision-log.md) | the single source of truth for every "why": decision, alternatives, rationale and risk |
| [`docs/traceability-matrix.md`](docs/traceability-matrix.md) | bidirectional source-to-target coverage, forward and reverse |
| [`docs/field-level-lineage.md`](docs/field-level-lineage.md) | every canonical column traced to its COBOL item and locator, and the one column that has no COBOL origin |
| [`extraction/extraction-spec.md`](extraction/extraction-spec.md) | the field entries, their runtime status, the measured no-formula finding and the landing contract |
| [`harness/translation-rules.md`](harness/translation-rules.md) | what the translator rewrites, where each rewrite applies and what the harness cannot reproduce |
| [`landing/partition-layout.md`](landing/partition-layout.md) | the exact object-key contract of the landing step |
| [`validation/validation-evidence.md`](validation/validation-evidence.md) | commands, versions, measured results, the selected target and the open items of the executed run |
| [`dbt/genapp_rqi/profiles.example.yml`](dbt/genapp_rqi/profiles.example.yml) | the connection template and the environment variables it resolves |

A reader looking for the reasoning behind any choice in this tree goes to
[`docs/decision-log.md`](docs/decision-log.md). Every other artifact, this file included, carries operational
content only.

## 8. Generated content

These paths are produced by a stage that owns them and are ignored by `modernization/.gitignore`:

- `.venv/` — the virtual environment
- `harness/build/` — samples, translated copies, compiled modules, run output. `harness/build/evidence/` keeps
  the newest staged evidence directories only, the staging directory of the running run included: five of them
  by default, or the count `HARNESS_EVIDENCE_RETAIN` names, which is a whole number from 1 to 1000 — a value
  outside that range ends the run in its preflight, naming the value and the range. `harness/run_harness.sh`
  prunes the superseded ones in that preflight while it holds the harness lock, and only an entry standing
  directly in that directory, which is a directory and carries a run-identifier name, is eligible.
- `dbt/genapp_rqi/target/` and `dbt/genapp_rqi/logs/` — dbt output
- `validation/local.duckdb` — the local-substitute database

`validation/expected/` and `validation/artifacts/` are generated **evidence that is tracked**: capture
snapshots, compile and execution logs, gate and version reports, and the diff report are committed as the
record of the executed run.
