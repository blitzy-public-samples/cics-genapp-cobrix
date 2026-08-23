# Validation evidence — GenApp Policy-Issue canonical warehouse bridge

> **Status — validated against local substitute, not AWS.**
> Selected target: `local_substitute`. Formal AWS diff disposition: **OPEN**. Run date (UTC): 2026-08-22.
> Rationale for every choice this record reports lives in `modernization/docs/decision-log.md`; this document records
> facts only — commands, versions, measured results, statuses and open items.

Every value below is an output of the single executed pipeline run of 2026-08-22 or of a measurement named beside it. A
step that was not executed is recorded as OPEN and carries no result. Every path is repository-root-relative, the
convention the published evidence set follows.

The local results in this document do not satisfy the formal AWS diff requirement. That requirement remains **OPEN**
and is unaffected by anything recorded here.

## 1. Scope of this record

The executed pipeline is the one-phase order of `modernization/Makefile`, run in one invocation as
`make -C modernization all` and stopping at the first failure. Its stages, in the order the run executed them:
`verify-env`, `gate`, `verify-readonly` (stage `baseline`), `translate`, `verify-readonly` (`translate`), `compile`,
`verify-readonly` (`compile`), `execute`, `verify-readonly` (`execute`), `extract`, `land` and `load` for `01amot`,
`land` and `load` for `01acom`, `verify-readonly` (`load`), `dbt`, `verify-readonly` (`dbt`), `diff`,
`verify-readonly` (stage `final`). The run printed
`all: every stage of <repository root>/modernization/Makefile completed` as its last line.

The two executed sample cases are `01AMOT` (motor) and `01ACOM` (commercial). The order and the gates of this run are
the subject of **Figure 5 — Validation Harness Control Flow** in `modernization/docs/architecture.md`; the artifact path
from source to canonical relation is the subject of **Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge** in the same
document.

| # | Stage | Result observed | Evidence | Status |
|---|---|---|---|---|
| 1 | `verify-env` | PASS with 4 deviation(s) | `modernization/validation/artifacts/verify-env.txt` | validated against local substitute, not AWS |
| 2 | `gate` | selected target `local_substitute`; both real-target probes exited 3 | `modernization/validation/artifacts/gate-selection.json` | validated against local substitute, not AWS |
| 3 | `verify-readonly` `baseline` | verdict PASS, exit_code 0 | the `make all` console, block `stage: baseline`; no file retains it after the run | validated against local substitute, not AWS |
| 4 | `translate` | 2 sample records and the translated tree under `modernization/harness/build` | `modernization/validation/artifacts/translate.log` | validated against local substitute, not AWS |
| 5 | `verify-readonly` `translate` | verdict PASS, exit_code 0 | the `make all` console, block `stage: translate`; no file retains it after the run | validated against local substitute, not AWS |
| 6 | `compile` | 15 modules and one driver | `modernization/validation/artifacts/compile-modules.log` | validated against local substitute, not AWS |
| 7 | `verify-readonly` `compile` | verdict PASS, exit_code 0 | the `make all` console, block `stage: compile`; no file retains it after the run | validated against local substitute, not AWS |
| 8 | `execute` | both cases returned `00` with the policy, product and VSAM captures present | `modernization/validation/artifacts/execute-harness.log` | validated against local substitute, not AWS |
| 9 | `verify-readonly` `execute` | verdict PASS, exit_code 0 | the `make all` console, block `stage: execute`, retained in `modernization/harness/build/logs/readonly-check.log` | validated against local substitute, not AWS |
| 10 | `extract` | one landing record per case, 17 keys each | the landing records `modernization/harness/build/landing/landing_01amot.json` and `landing_01acom.json`; the stage's console output is not separately retained | validated against local substitute, not AWS |
| 11 | `land` and `load`, twice | one object plus its COPY manifest per case; `raw.genapp_policy_issue` carries 2 rows | the loaded relation in `modernization/validation/local.duckdb`; the stage's console output is not separately retained | validated against local substitute, not AWS |
| 12 | `verify-readonly` `load` | verdict PASS, exit_code 0 | the `make all` console, block `stage: load`, retained in `modernization/harness/build/logs/readonly-check.log` | validated against local substitute, not AWS |
| 13 | `dbt` | `dbt run` PASS=4, `dbt test` PASS=64, no warning and no error | `modernization/validation/artifacts/dbt-run.log`, `modernization/validation/artifacts/dbt-test.log` | validated against local substitute, not AWS |
| 14 | `verify-readonly` `dbt` | verdict PASS, exit_code 0 | the `make all` console, block `stage: dbt`, retained in `modernization/harness/build/logs/readonly-check.log` | validated against local substitute, not AWS |
| 15 | `diff` | PASS, 2 cases, 40 of 40 canonical column instances compared, 0 failed | `modernization/validation/artifacts/diff-report.md` | validated against local substitute, not AWS |
| 16 | `verify-readonly` `final` | verdict PASS, exit_code 0, 0 tracked modifications | the `make all` console, block `stage: final`, retained in `modernization/harness/build/logs/readonly-check.log` | validated against local substitute, not AWS |

Where the seven `verify-readonly` blocks of rows 3, 5, 7, 9, 12, 14 and 16 stand: the gate prints each block on the
console of the run and appends it to `modernization/harness/build/logs/readonly-check.log`, a generated path
`modernization/.gitignore` ignores, inside the only directory the gate accepts a log in. The preflight of
`modernization/harness/run_harness.sh` empties that log once per run, inside the `execute` stage, so at the end of a full
`make all` the `execute`, `load`, `dbt` and `final` blocks stand in it and the `baseline`, `translate` and `compile`
blocks do not. The published `modernization/validation/artifacts/readonly-check.log` carries the four `harness-*` blocks
of the run recorded in section 4 and no Makefile stage block (`D-72`, `D-106`).

## 2. Environment and versions

Measured host of the run: Ubuntu 25.10 (Questing Quokka), `x86_64`. The Python interpreter this project runs on is
`/usr/local/bin/python3.12`, built from source; the configured apt suites of this host carry no `python3.12` package.
`modernization/.venv` holds the project interpreter and every pinned package, and `modernization/Makefile` invokes
Python and dbt through `.venv/bin/...` by explicit path.

`make verify-env` result: **PASS with 4 deviation(s)**, report `modernization/validation/artifacts/verify-env.txt`,
`HARNESS_STRICT_TOOL_VERSIONS` unset (`strict tool versions: no`). The stage installs nothing.

Each runtime now carries two accepted values: the pin, which records the version this project was built and measured
against, and a minimum, which is the lowest version the stage accepts because a lower one carries a published advisory
with an available fix. A measured version at or above the minimum and different from the pin is reported as a deviation
and passes in the default mode; a measured version below the minimum fails the stage whatever the mode (`D-119`).

| Item | Pinned | Minimum accepted | Measured in this run | Verdict | Status |
|---|---|---|---|---|---|
| `python3.12` on PATH | 3.12.14 | 3.12.14 | 3.12.14 | MATCH | validated against local substitute, not AWS |
| `cobc` (GnuCOBOL) | 3.1.2.0 | 3.1.2 | 3.2.0 | DEVIATION | validated against local substitute, not AWS |
| `git` | 2.51.0 | 2.43.7 | 2.51.0 | MATCH | validated against local substitute, not AWS |
| apt `python3.12` | 3.12.3-1ubuntu0.15 | — | not installed through apt | DEVIATION | validated against local substitute, not AWS |
| apt `python3.12-venv` | 3.12.3-1ubuntu0.15 | — | not installed through apt | DEVIATION | validated against local substitute, not AWS |
| apt `gnucobol3` | 3.1.2-5.1ubuntu1 | — | 3.2-4 | DEVIATION | validated against local substitute, not AWS |
| apt `git` | 1:2.51.0-1ubuntu1 | — | 1:2.51.0-1ubuntu1 | MATCH | validated against local substitute, not AWS |
| `.venv/bin/python` | 3.12 series | 3.12.14 | 3.12.14 | in series, at the minimum | validated against local substitute, not AWS |
| `pip` in the virtual environment | 26.2.1 | 26.2.1 | 26.2.1 | MATCH | validated against local substitute, not AWS |

The apt `python3.12` pin is reported with the note that the release it packages, 3.12.3, is **below** the accepted
interpreter minimum of 3.12.14: no apt `python3.12` package reaches 3.12.14, so the interpreter checks above govern and
that pin records the packaging alone. On this host the interpreter is built from source, which is why the two apt Python
rows read `not installed through apt`.

Every direct Python pin of `modernization/requirements.txt` was measured inside the virtual environment and matched
exactly; the stage reported `pins measured: 10`.

| Package | Pinned | Measured | Verdict | Status |
|---|---|---|---|---|
| `dbt-core` | 1.12.3 | 1.12.3 | MATCH | validated against local substitute, not AWS |
| `dbt-duckdb` | 1.11.0 | 1.11.0 | MATCH | validated against local substitute, not AWS |
| `dbt-redshift` | 1.11.1 | 1.11.1 | MATCH | validated against local substitute, not AWS |
| `duckdb` | 1.5.5 | 1.5.5 | MATCH | validated against local substitute, not AWS |
| `redshift-connector` | 2.1.16 | 2.1.16 | MATCH | validated against local substitute, not AWS |
| `boto3` | 1.43.74 | 1.43.74 | MATCH | validated against local substitute, not AWS |
| `botocore` | 1.43.74 | 1.43.74 | MATCH | validated against local substitute, not AWS |
| `moto[s3,server]` | 5.2.2 | 5.2.2 | MATCH | validated against local substitute, not AWS |
| `PyYAML` | 6.0.3 | 6.0.3 | MATCH | validated against local substitute, not AWS |
| `jsonschema` | 4.26.0 | 4.26.0 | MATCH | validated against local substitute, not AWS |

`modernization/validation/artifacts/runtime-versions.txt` carries the same runtime measurements and apt-availability
findings together with the resolved compiler dialect chain, the numeric-store keys of that chain, the hash-pinned closure
and one capability probe per behaviour the harness relies on. The decision-log rows that cover version pinning and the
accepted deviations are D-45 and D-48 in `modernization/docs/decision-log.md`; the security floors are D-119 and the
hash-pinned lock is D-120.

**The restriction that stood on this dependency set is lifted.** It read: these pins resolve the transitive package
`sqlparse` at 0.5.5, the release that fixes its published advisories is excluded by the declared constraint of both
`dbt-core` 1.12.2 and `dbt-redshift` 1.11.0, and the set is therefore not approved for production use (D-75). The set now
pins `dbt-core` 1.12.3 and `dbt-redshift` 1.11.1, the lowest releases whose declared constraints admit `sqlparse` 0.6.0,
and the resolved closure carries that release. Measured on 2026-08-23 with `pip-audit` 2.10.1 in a separate virtual
environment, so that the audited environment is not modified: over `modernization/requirements.txt`, `No known
vulnerabilities found`, exit 0; over the installed closure of `modernization/.venv` — 107 distributions listed by
`pip freeze --all` — 0 known vulnerabilities, against 10 vulnerabilities in 2 packages measured the same way before the
change. `pip` is pinned at 26.2.1 and `git` carries a 2.43.7 floor for the same reason. The lifting, its measurement and
what it does not cover are recorded as D-118 in `modernization/docs/decision-log.md`, and D-75 is marked superseded
there. The formal AWS diff of section 12 is unaffected: it was independent of this restriction and remains **OPEN**.

## 3. AWS precondition gate

Measurements taken on the ambient environment of this checkout, with no project variable exported:

| Probe of the environment | Command | Observed | Status |
|---|---|---|---|
| AWS CLI | `command -v aws` | absent | validated against local substitute, not AWS |
| Shared credentials directory | test on `$HOME/.aws` | absent | validated against local substitute, not AWS |
| boto3 credential resolution | `botocore.session.get_session().get_credentials()` | none resolved | validated against local substitute, not AWS |
| boto3 region resolution | `get_config_variable('region')` | none | validated against local substitute, not AWS |
| Destination bucket | `S3_BUCKET` in the environment | not set | validated against local substitute, not AWS |
| Redshift connection settings | `REDSHIFT_*` in the environment | none set | validated against local substitute, not AWS |
| Named profile | `AWS_PROFILE` in the environment | not set | validated against local substitute, not AWS |

`make gate` runs the two real-target probes of `modernization/landing/land_to_s3.py` and provisions nothing. Observed in
this run:

| Probe | Command | Exit status | Log | Status |
|---|---|---|---|---|
| Real S3 | `.venv/bin/python landing/land_to_s3.py --probe --run-mode redshift` | 3 | `modernization/validation/artifacts/gate-probe-s3.log` | validated against local substitute, not AWS |
| Real Redshift | `.venv/bin/python landing/land_to_s3.py --probe-redshift --run-mode redshift` | 3 | `modernization/validation/artifacts/gate-probe-redshift.log` | validated against local substitute, not AWS |

Neither probe reached a real target. Each reported that a loopback endpoint was configured for the local-substitute
branch while the probe addressed AWS, and neither log echoes an endpoint, a bucket or a credential value. The stage then
printed `gate: selected target local_substitute` and
`gate: validated against local substitute, not AWS; the formal AWS diff stays OPEN`.

Recorded selection, `modernization/validation/artifacts/gate-selection.json`:

| Key | Recorded value |
|---|---|
| `selected_target` | `local_substitute` |
| `formal_aws_diff` | `OPEN` |
| `provisioned` | `[]` |
| `source_system_key` | `GENAPP_CLASS_EXEMPLAR` |
| `extract_date` | `2026-08-22` |
| `status_label` | validated against local substitute, not AWS |
| `probes.s3.passed` | `false`, exit status 3 |
| `probes.redshift.passed` | `false`, exit status 3 |

On this branch the local S3-compatible endpoint provided by `moto` serves the S3 API surface and DuckDB serves as the
warehouse. **No AWS infrastructure was provisioned by this run: zero S3 buckets, zero Redshift clusters, zero Redshift
Serverless workgroups, zero networks and zero IAM objects.** The gate re-probes on every invocation and selects the real
branch only when both the S3 and the Redshift probe exit 0; the stages that follow read the selection from the artifact
above rather than from a build-time constant. The rationale for the branch selection and for the probe-never-provision
rule is recorded as D-05 and D-07 in `modernization/docs/decision-log.md`.

## 4. Source baseline and read-only gates

The five authorized source artifacts were measured through a held descriptor at every gate run of this pipeline. Each
measurement equalled the embedded baseline:

| Path | Lines | SHA-256 | Gate A verdict | Status |
|---|---|---|---|---|
| `base/src/lgapol01.cbl` | 169 | `4dddd29539dd96aaec9f6885d3d62d19d40a1c6c888636623164bc5f5b232f6f` | PASS | validated against local substitute, not AWS |
| `base/src/lgapdb01.cbl` | 595 | `3d21ad353a03c63d05defc511372e14477613fa4c51068a51a84d3c840c29815` | PASS | validated against local substitute, not AWS |
| `base/src/lgapvs01.cbl` | 188 | `e0bca62eed2d6390852befdbaddd684833040c8be183d23f4fca368834709215` | PASS | validated against local substitute, not AWS |
| `base/src/lgcmarea.cpy` | 103 | `4ecc9ed8dbf0936a8b0738cbb03a947e937206100b0e34f749fbb9e0b03f701d` | PASS | validated against local substitute, not AWS |
| `base/src/lgpolicy.cpy` | 107 | `717c8f5c50738a2ef4d432e4b397e21bdc0423a9fc789246eb3360aa3f99eaa5` | PASS | validated against local substitute, not AWS |

`modernization/validation/verify_readonly.sh` ran after each major stage and as the final gate. Every run reported
`gate A result: PASS (5 of 5 baseline entries matched)`, `gate B result: PASS` with
`git status --porcelain -- base/ produced no output`, `gate C result: PASS`, and `gate D result: PASS` with
`generated evidence paths standing in this checkout: 22 of 22` and `paths the manifest does not cover: 0`:

| Gate run | Stage label | Where the block stands | Verdict | Exit code | Status |
|---|---|---|---|---|---|
| 1 | `baseline` | the `make all` console; emptied from the gate's git-ignored log by the harness preflight | PASS | 0 | validated against local substitute, not AWS |
| 2 | `translate` | the `make all` console; emptied from the gate's git-ignored log by the harness preflight | PASS | 0 | validated against local substitute, not AWS |
| 3 | `compile` | the `make all` console; emptied from the gate's git-ignored log by the harness preflight | PASS | 0 | validated against local substitute, not AWS |
| 4 | `execute` | the `make all` console and `modernization/harness/build/logs/readonly-check.log` | PASS | 0 | validated against local substitute, not AWS |
| 5 | `load` | the `make all` console and `modernization/harness/build/logs/readonly-check.log` | PASS | 0 | validated against local substitute, not AWS |
| 6 | `dbt` | the `make all` console and `modernization/harness/build/logs/readonly-check.log` | PASS | 0 | validated against local substitute, not AWS |
| 7 | `final` | the `make all` console and `modernization/harness/build/logs/readonly-check.log` | PASS | 0 | validated against local substitute, not AWS |

`modernization/harness/run_harness.sh` ran the same gate at four further points inside the `execute` stage — labels
`harness-preflight`, `harness-compile`, `harness-execute` and `harness-final` — and reported
`source guard: PASS at 4 of 4 points`. Eleven gate runs passed in this pipeline in total. The published
`modernization/validation/artifacts/readonly-check.log` is the copy the harness publishes after its own last gate, so it
carries those four `harness-*` blocks and none of the seven Makefile stage blocks above (`D-72`, `D-106`). The harness
runs the gate with `--reproducible`, which puts `not recorded (--reproducible)` in the `timestamp_utc` record of each
published block: the time of a run is read from the artifacts that carry it, not transcribed into this table (`D-107`).

At the final gate, the `git diff --name-only HEAD, tracked modifications:` record read `(no tracked modification)` and
the count below it read `tracked modifications: 0`: every path that command named was recorded as exempt and none was
counted against the gate. Every block of the published `modernization/validation/artifacts/readonly-check.log` records
that same `tracked modifications: 0`, which is what a passing gate C means, and each block carries beside it the exempt
inventory in full — 23 exact paths — the exempt paths that block itself found modified, and its own
`exempt generated evidence paths modified:` count. That count is not transcribed here: it follows the tracked state the
gate read, naming the published files the run had already rewritten when that gate ran, so it is read from the block
that recorded it (`D-106`, `D-107`). No pre-existing repository file was modified by this work: every authored file of the
bridge lives under `modernization/`, and the five source artifacts above are byte-identical to their baseline. The
exempt inventory and its extension to the Makefile stage records are recorded as D-47 and D-65 in
`modernization/docs/decision-log.md`.

Gate D closes the gap that the exemption of gate C opens. A path recorded as exempt generated evidence is allowed to
differ from its committed copy, so gate C alone accepts any content in it; gate D reads
`modernization/validation/artifacts/evidence-manifest.sha256` and requires every one of those 22 paths to match the
digest its manifest entry states. Every gate run of this pipeline reported `digest lines: 22`,
`covered by a matching digest: 22` and `paths the manifest does not cover: 0`. A published artifact whose bytes do not
match its entry, or which stands with no entry at all, ends the gate with verdict `FAIL-EVIDENCE-COVERAGE` and exit
status 6; the measured failure and the manifest's own residual limit are in section 16 (`D-121`).

## 5. Translate and compile

Every generated artifact of this stage was written into `modernization/harness/build/**` alone; no source file was
preprocessed in place. **GnuCOBOL executes translated copies with CICS and Db2 services emulated by the harness** — the
five named source artifacts are untouched, and the translator reads them and writes elsewhere.

`make translate` printed `translate: 2 sample records and the translated tree stand under harness/build`. Measured per
program, from `modernization/validation/artifacts/translate.log`:

| Generated program | Source lines | Generated lines | `EXEC CICS` sites | `EXEC SQL` blocks | Lines copied unchanged | Status |
|---|---|---|---|---|---|---|
| `harness/build/src/lgapol01.cbl` | 169 | 162 | 9 | 0 | 143 | validated against local substitute, not AWS |
| `harness/build/src/lgapdb01.cbl` | 595 | 514 | 20 | 11 | 391 | validated against local substitute, not AWS |
| `harness/build/src/lgapvs01.cbl` | 188 | 183 | 7 | 0 | 160 | validated against local substitute, not AWS |

`modernization/validation/artifacts/translation-report.json` records `exec_cics_sites` 36 against
`expected_exec_cics_sites` 36, `exec_sql_blocks` 11 against `expected_exec_sql_blocks` 11, four abend sites each
followed by a return, and observed equal to expected for every structural count: `COPY DFHEIBLK.` 3, `COPY DFHRESP.` 1,
`COPY HSQLCA.` 1, `COPY LGCMAREA.` 3, `COPY LGPOLICY.` 1 and `PROCEDURE DIVISION USING DFHCOMMAREA.` 3. Both chain
links were recorded with `COMMAREA DFHCOMMAREA, LENGTH 32500`: `lgapol01.cbl:121-124` to `LGAPDB01` and
`lgapdb01.cbl:243-246` to `LGAPVS01`. The report's `read_only_checks` block records
`source_digests_reverified: true` and `reported_changes: 0` for pathspec `base/src/`. Six copybooks were placed
verbatim and the response-condition item is `DFHRESP-NORMAL`.

Fixed-format assertion: the translator verifies that generated text occupies columns 8-72 only, and an independent
measurement over every generated file confirmed the result.

```bash
awk 'length($0)>72 {c++} END {print "lines longer than 72:", c+0}' \
  modernization/harness/build/src/*.cbl modernization/harness/build/src/*.cpy
# lines longer than 72: 0
```

`make compile` recorded its command line and compiler in the first two lines of
`modernization/validation/artifacts/compile-modules.log`:

```text
compile: cobc -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy
cobc (GnuCOBOL) 3.2.0
```

| Compilation | Command form | Count | Return code | Status |
|---|---|---|---|---|
| Translated programs | `cobc -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy -m -I harness/build/src -o <module>.so <source>` | 3 | 0 for each | validated against local substitute, not AWS |
| Harness stubs | `cobc -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy -m -I harness/build/src -o <module>.so <source>` | 12 | 0 for each | validated against local substitute, not AWS |
| Driver | `cobc -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy -x -I harness/build/src -o harness/build/compile/driver harness/driver.cbl` | 1 | 0 | validated against local substitute, not AWS |

The stage ended with `compile: 15 modules and one driver, compiler output in validation/artifacts/compile-modules.log`
and requires every expected module and the driver to exist. Retained warnings: 16 occurrences of the host-toolchain
warning that `_FORTIFY_SOURCE` is redefined on the command line, each with its paired `note:` line locating the previous
definition, and no COBOL diagnostic.

The `execute` stage compiles the same set through `modernization/harness/run_harness.sh`, under the same four mandated
options and with the compiler environment pinned, which the `compile` stage does not do.
`modernization/validation/artifacts/compile.log` records
for that build: compiler `3.2.0 (cobc)`; options `-std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy`;
`COB_CONFIG_DIR: /usr/share/gnucobol/config (pinned)`; `COB_RUNTIME_CONFIG: unset (pinned)`; `COB_CFLAGS` pinned to the
values `cobc --info` reports; `ambient compiler environment ignored: none`; the dialect chain `ibm.conf`,
`ibm-strict.conf`, `ibm.words` and `lax.conf-inc` with a SHA-256 per file; the resolved dialect keys `binary-size 2-4-8`,
`binary-truncate no`, `binary-byteorder big-endian`, `hostsign yes` and `defaultbyte 0`;
`binary truncation in force: yes`; twelve stub modules and three program modules built with `cobc -m` and the driver
with `cobc -x`; and zero warnings. Module lookup for execution used
`COB_LIBRARY_PATH=<repository root>/modernization/harness/build/bin`. The four mandated compile options, including the
added `-fbinary-truncate`, are recorded as D-23 in `modernization/docs/decision-log.md`, and the pinned compiler
environment of this build as D-71.

## 6. Execution evidence, per case

The driver supplied a 32,500-character COMMAREA for each case, built by
`modernization/extraction/build_sample_commarea.py` from the sample definition of that case. Each executed case
traversed `LGAPOL01`, then `LGAPDB01`, then `LGAPVS01`, and returned to the driver. Each returned record measured 32,501
bytes on disk: 32,500 characters and the terminating newline.

| Observation | `01AMOT` | `01ACOM` | Status |
|---|---|---|---|
| Driver COMMAREA supplied | 32,500 characters | 32,500 characters | validated against local substitute, not AWS |
| Chain traversed | `LGAPOL01`, `LGAPDB01`, `LGAPVS01` | `LGAPOL01`, `LGAPDB01`, `LGAPVS01` | validated against local substitute, not AWS |
| `CA-RETURN-CODE` | `00` | `00` | validated against local substitute, not AWS |
| Policy SQL capture | `SQL_POLICY_PRESENT=Y` | `SQL_POLICY_PRESENT=Y` | validated against local substitute, not AWS |
| Product SQL capture | `SQL_MOTOR_PRESENT=Y` | `SQL_COMMERCIAL_PRESENT=Y` | validated against local substitute, not AWS |
| Captured `DB2-POLICYTYPE` | `M` | `C` | validated against local substitute, not AWS |
| Assigned policy number in the returned COMMAREA | `0001000001` (seed 1000001) | `0001000002` (seed 1000002) | validated against local substitute, not AWS |
| Assigned timestamp in the returned COMMAREA | `2026-08-19-12.00.00.000000`, 26 characters | `2026-08-19-12.00.00.000000`, 26 characters | validated against local substitute, not AWS |
| VSAM capture length | `0064` | `0064` | validated against local substitute, not AWS |
| VSAM key length | `0021` | `0021` | validated against local substitute, not AWS |
| VSAM key | `M00000010010001000001` | `C00000020020001000002` | validated against local substitute, not AWS |
| Abend recorded | `ABEND_PRESENT=N`, `ABEND_COUNT=0000` | `ABEND_PRESENT=N`, `ABEND_COUNT=0000` | validated against local substitute, not AWS |
| Diagnostic links | `DIAG_LINK_COUNT=0000` | `DIAG_LINK_COUNT=0000` | validated against local substitute, not AWS |
| Driver verdict and exit code | `DRIVER_STATUS=PASS`, `DRIVER_EXIT_STATUS=00`, process exit 0 | `DRIVER_STATUS=PASS`, `DRIVER_EXIT_STATUS=00`, process exit 0 | validated against local substitute, not AWS |
| Harness assertions passed | 93 | 106 | validated against local substitute, not AWS |

The 21-byte key carries the request-type letter, then the ten-digit customer number, then the ten-digit policy number
[base/src/lgapvs01.cbl:26-29]; the letter is the fourth character of the request id
[base/src/lgapvs01.cbl:99]. The written record is 64 bytes: the 21-byte key and a 43-byte product payload
[base/src/lgapvs01.cbl:30,135-141].

Harness totals for the `execute` stage: `cases executed: 2; assertions passed: 243` — 93 and 106 for the two cases and
44 in the five infrastructure probes the harness runs before them. Retained per-case evidence:
`modernization/validation/artifacts/driver_01amot.log`, `captures_01amot.txt`, `commarea_post_01amot.dat` and the
matching three files for `01acom`, with the stage output in
`modernization/validation/artifacts/execute-harness.log`.

The six amount windows carry unsigned display numerics with no implied decimal — `PIC 9(6)` for `CA-PAYMENT`
[base/src/lgcmarea.cpy:43] and `CA-M-PREMIUM` [base/src/lgcmarea.cpy:73], `PIC 9(8)` for the four commercial premiums
[base/src/lgcmarea.cpy:85,87,89,91]. The three named programs contain no `COMPUTE`, `MULTIPLY` or `DIVIDE` statement on
any amount path: the amounts reach the Db2 host variables by `MOVE`
[base/src/lgapdb01.cbl:265,445,489,491,493,495]. No rating formula, rating factor or derived-factor value exists in the
source, and none was constructed, inferred or backfilled anywhere in this bridge.

`policy_type` is carried by no COMMAREA item. It is derived from the request routing — `01AEND` to `E`, `01AHOU` to `H`,
`01AMOT` to `M`, `01ACOM` to `C` [base/src/lgapdb01.cbl:184-207] — and verified in this run against the captured
`DB2-POLICYTYPE` [base/src/lgpolicy.cpy:43]. `policy_number` and `last_changed` are post-chain values, recovered after
the policy insert [base/src/lgapdb01.cbl:307-321], and were read out of the returned COMMAREA.

The length constants `WS-MOTOR-LEN +65` [base/src/lgpolicy.cpy:21] and `WS-FULL-MOTOR-LEN +137`
[base/src/lgpolicy.cpy:26] are unchanged in source. The sample builder emitted the full 32,500-character record for
every case of this run, and extraction validated that the applicable amount bytes were numeric before landing. The
handling of that constant is recorded as D-08 in `modernization/docs/decision-log.md`.

## 7. Return-code contract, preserved and reported

The observed return convention of the chain, with the source locator of each code and whether this pipeline run
exercised it:

| Code | Observed meaning | Source locator | Exercised by this run |
|---|---|---|---|
| `00` | Success | [base/src/lgapol01.cbl:104-126], [base/src/lgapdb01.cbl:290-294] | Yes — the two success cases `01AMOT` and `01ACOM` |
| `70` | Policy insert returned SQLCODE −530 | [base/src/lgapdb01.cbl:290-299] | Yes — case `01AMOT-RC70` |
| `80` | VSAM write response was not normal | [base/src/lgapvs01.cbl:142-147] | Yes — case `01AMOT-RC80` |
| `90` | SQL failure; subtype insert failures also abend `LGSQ` | [base/src/lgapdb01.cbl:300-303,389-395,427-433,473-479,547-553] | Yes — case `01AMOT-RC90`, with the abend path in `01AMOT-LGSQ`, `01ACOM-LGSQ` and `01AHOU-LGSQ` |
| `98` | COMMAREA too short | [base/src/lgapol01.cbl:108-116], [base/src/lgapdb01.cbl:181-213] | Yes — cases `01AMOT-RC98` and `01AMOT-LGCA` |
| `99` | Unsupported request id | [base/src/lgapdb01.cbl:184-207] | Yes — case `01AXXX-RC99` |

The `execute` stage runs the case selection named by `CASES_MODE`, and its default `all` selects the whole authored
table: **12 cases, 902 assertions**, observed as `execute: CASES_MODE all, 12 case(s) executed with 902 assertion(s)
passed`. Every code of the contract above is therefore exercised by `make all` itself, together with the `LGSQ` abend
path and the house route (`01AHOU-ROUTE`, `01AHOU-LGSQ`). `CASES_MODE=success-only` selects the two success cases alone
— 2 cases, 243 assertions — and remains available as the fast path. Both selections publish the same evidence set,
because only a success case carries a capture file, a driver log and a post-chain record; the ten characterisation cases
assert a return code, an abend or a route and land nothing.

In the two success cases the captures record `INJECT_POLICY_SQLCODE=0`, `INJECT_SUBTYPE_SQLCODE=0`, `SQLCODE_LAST=0` and
`INJECT_VSAM_RESP=0`: every SQL stub reported SQLCODE 0 and the VSAM write reported the normal response, so those two
cases traverse the success path only, and the non-`00` codes are exercised by the characterisation cases named beside
them. The endowment route was **not executed** — no endowment sample exists — and the house route is exercised for its
routing and its abend path but issues no policy. The unexercised routes and paths that remain are recorded as D-18,
D-20 and D-21, and the orchestrated selection as D-95 and D-96, in `modernization/docs/decision-log.md`.

The interface this work preserves was reproduced without a source change: the shared 32,500-byte COMMAREA, the call
order `LGAPOL01`, `LGAPDB01`, `LGAPVS01`, both links at `LENGTH(32500)` [base/src/lgapol01.cbl:121-124;
base/src/lgapdb01.cbl:243-246], the request routing [base/src/lgapdb01.cbl:184-207] and the return codes above.

## 8. Extract, land and raw load

The artifact path this section records is the subject of
**Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge** in `modernization/docs/architecture.md`.

`make extract` decoded the returned COMMAREA of each case with
`modernization/extraction/copybook_field_map.yml` and wrote one landing record per case. No amount was derived at any
point in extraction: each amount is the decoded window of the returned record.

| Observation | `01AMOT` | `01ACOM` | Status |
|---|---|---|---|
| Landing record | `modernization/harness/build/landing/landing_01amot.json` | `modernization/harness/build/landing/landing_01acom.json` | validated against local substitute, not AWS |
| Keys in the record | 17 | 17 | validated against local substitute, not AWS |
| Non-null values / nulls | 13 / 4 | 16 / 1 | validated against local substitute, not AWS |
| Derived `policy_type` | `M` | `C` | validated against local substitute, not AWS |
| `return_code` | `00` | `00` | validated against local substitute, not AWS |
| `source_system_key` | `GENAPP_CLASS_EXEMPLAR` | `GENAPP_CLASS_EXEMPLAR` | validated against local substitute, not AWS |
| Normalised `last_changed` | `2026-08-19T12:00:00.000000` | `2026-08-19T12:00:00.000000` | validated against local substitute, not AWS |
| Object bytes validated for landing | 499 | 508 | validated against local substitute, not AWS |

The extractor validated every decoded window against the shape the field map declares for it as it built each record,
and the landing writer validated the finished record against `modernization/landing/landing-schema.json` — whose 17
properties are all required — before writing the object, reporting `validated '<record>' carrying <n> bytes for key
'<key>'`. The landed values are JSON strings and nulls; typing happens in dbt.

`make land` wrote one object per case through boto3 to the local S3-compatible endpoint, under the documented prefix,
into the bucket named by the `S3_BUCKET` environment variable:

```text
landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0000.json
landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0000.manifest.json
landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0001.json
landing/source_system_key=GENAPP_CLASS_EXEMPLAR/entity=policy_issue/extract_date=2026-08-22/part-0001.manifest.json
```

The object name carries a part element: `make all` lands `01amot` at part `0000` and `01acom` at part `0001`, so the two
records of a run stand side by side under one extract-date prefix rather than one replacing the other. A listing of that
prefix returned four objects — the 499-byte motor record and the 508-byte commercial record, each with its own 269-byte
COPY manifest naming that record and its byte count. Rationale: `modernization/docs/decision-log.md`, rows **D-80** and
**D-81**.

The writer reported `run mode 'local_substitute' from --run-mode, addressing the loopback endpoint` for both cases and a
269-byte COPY manifest beside each data object. Neither case reported a replacement of the other's object, because each
addresses its own part; a re-run of one case does report its documented warning that that part's key already carries an
object, which that landing replaces. No credential, endpoint URL, host, role or password value is echoed by the writer.
It does name the destination on the console, in the form
`land_to_s3: addressing bucket '<bucket>' in region '<region>' through a loopback endpoint`, and the `s3://` object URI
it prints as its last line carries the same bucket name. The stage created no bucket.

Replay was measured rather than assumed: with every row of `raw.genapp_policy_issue` deleted and no landing performed,
`make load CASE=01amot` followed by `make load CASE=01acom` rebuilt both raw rows from object storage alone, each
reporting `removed=0 written=1`, leaving the relation at 2 rows carrying policies 1000001 (`M`, `01AMOT`) and 1000002
(`C`, `01ACOM`) — validated against local substitute, not AWS.

`make load` used `modernization/landing/load_local.py` on this branch. It names the source bucket and its region on the
console in the same form as the writer — `load_local: reading bucket '<bucket>' in region '<region>' through a loopback
endpoint` — and redacts the object URI as `s3://<redacted>`, the source-system key and the policy number (`D-108`). Per
case it bound the download to the exact object length (499 and 508 bytes), reported `17 landed columns` with the SHA-256
of the object, applied 2 statements from `modernization/warehouse/ddl/01_schemas.sql` and 1 statement from
`modernization/warehouse/ddl/02_raw_genapp_policy_issue.sql`, then loaded the row on the natural key with
`keys=2 removed=1 written=1`. `modernization/landing/load_redshift.sql` is authored and was **not executed** on this
branch.

| Relation | Rows after both loads | Status |
|---|---|---|
| `raw.genapp_policy_issue` | 2 | validated against local substitute, not AWS |

The single-object-per-prefix contract and the key-scoped load are recorded as D-38, D-39 and D-40 in
`modernization/docs/decision-log.md`.

## 9. dbt

`make dbt` ran `dbt clean`, then `dbt run`, then `dbt test` against the target the gate recorded, with the model files
unchanged. The load stage is the only target-specific stage of the pipeline; no model file was edited for this target.

```text
Running with dbt=1.12.2
Registered adapter: duckdb=1.11.0
Found 4 models, 64 data tests, 1 source, 501 macros
```

| Model | Materialization | Relation created | Result | Status |
|---|---|---|---|---|
| `stg_genapp__policy_issue` | view | `staging.stg_genapp__policy_issue` | OK | validated against local substitute, not AWS |
| `int_policy_issue_decoded` | table | `intermediate.int_policy_issue_decoded` | OK | validated against local substitute, not AWS |
| `canonical_issued_policy` | table | `canonical.issued_policy` | OK | validated against local substitute, not AWS |
| `canonical_preissued_rating` | table | `canonical.preissued_rating` | OK | validated against local substitute, not AWS |

`dbt run` finished `Completed successfully` with `Done. PASS=4 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=4`.
`dbt test` finished `Completed successfully` with `Done. PASS=64 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=64`, the
64 data tests comprising the generic tests declared in the model YAML files — the enforced contracts, `not_null`,
`accepted_values` and `relationships` — and the four singular tests `assert_issued_policy_unique_key`,
`assert_preissued_rating_unique_key`, `assert_product_premium_nullability` and `assert_canonical_column_widths`. Output retained in
`modernization/validation/artifacts/dbt-clean.log`, `dbt-run.log` and `dbt-test.log`.

Catalog check against `modernization/validation/local.duckdb` after the run:

| Check | Observed | Status |
|---|---|---|
| Relations in schema `canonical` | exactly `issued_policy` and `preissued_rating`, both base tables | validated against local substitute, not AWS |
| Registry, Quote, Loss, commission, formula or derived-factor relation | none | validated against local substitute, not AWS |
| Columns of `canonical.issued_policy`, ordinal order | `source_system_key`, `policy_number`, `policy_type`, `customer_number`, `request_id`, `return_code`, `issue_date`, `expiry_date`, `last_changed`, `broker_id`, `brokers_reference` — 11 | validated against local substitute, not AWS |
| Columns of `canonical.preissued_rating`, ordinal order | `source_system_key`, `policy_number`, `policy_type`, `payment_amount`, `motor_premium_amount`, `fire_premium_amount`, `crime_premium_amount`, `flood_premium_amount`, `weather_premium_amount` — 9 | validated against local substitute, not AWS |
| Formula, factor or commission column | none on either relation | validated against local substitute, not AWS |
| Rows in `canonical.issued_policy` | 2, and 2 distinct `(source_system_key, policy_number)` | validated against local substitute, not AWS |
| Rows in `canonical.preissued_rating` | 2, and 2 distinct `(source_system_key, policy_number)` | validated against local substitute, not AWS |

Product-specific NULL pattern, read from the two rows of `canonical.preissued_rating`:

| Policy type | `payment_amount` | `motor_premium_amount` | `fire_premium_amount` | `crime_premium_amount` | `flood_premium_amount` | `weather_premium_amount` | Status |
|---|---|---|---|---|---|---|---|
| `M` (policy 1000001) | 500.00 | 450.00 | NULL | NULL | NULL | NULL | validated against local substitute, not AWS |
| `C` (policy 1000002) | 1750.00 | NULL | 13500.00 | 3400.00 | 7800.00 | 2600.00 | validated against local substitute, not AWS |

Every product-inapplicable premium column carries NULL, never zero.

## 10. Comparison gate

This is the last gate of the order named in **Figure 5 — Validation Harness Control Flow** in
`modernization/docs/architecture.md`. Command executed by the `diff` stage:

```bash
.venv/bin/python validation/diff_harness_vs_warehouse.py \
  --cases 01AMOT,01ACOM \
  --run-dir <repository root>/modernization/harness/build/run \
  --field-map <repository root>/modernization/extraction/copybook_field_map.yml \
  --target duckdb \
  --database <repository root>/modernization/validation/local.duckdb \
  --source-system-key GENAPP_CLASS_EXEMPLAR \
  --report <repository root>/modernization/validation/artifacts/diff-report.md \
  --json <repository root>/modernization/validation/artifacts/diff-report.json \
  --expected-dir <repository root>/modernization/validation/expected
```

Before it opens the warehouse the gate reads the dbt run artifact of that project,
`modernization/dbt/genapp_rqi/target/run_results.json`, and publishes no verdict unless every node dbt recorded there
carries a successful status; `warn` passes and is named, and an absent or unusable artifact is a refusal. This run
recorded `transform freshness | FRESH — dbt test recorded 64 nodes, 64 of them successful and 0 warned`. The refusal
path was measured, not inferred: with a raw row carrying the non-numeric payment amount `ABCDEF`, `make dbt` ended at
the intermediate model with both marts skipped, and the gate invoked directly over that state returned exit status 3
naming `model.genapp_rqi.int_policy_issue_decoded` `[error]` with dbt's own conversion message and both mart models
`[skipped]`, where before this precondition existed the same invocation returned PASS. Rationale:
`modernization/docs/decision-log.md`, rows **D-82** and **D-83**.

Run metadata recorded in the report: the time of the run, carried by the `generated_at` key of
`modernization/validation/artifacts/diff-report.json` and the `generated at (UTC)` row of
`modernization/validation/artifacts/diff-report.md` and read from there rather than transcribed here (`D-107`); target
`duckdb`; adapter `duckdb 1.5.5`; python 3.12.14; connection `modernization/validation/local.duckdb`; source-system key
`GENAPP_CLASS_EXEMPLAR`; amount tolerance `0.01`; expected amount scale 2; capture snapshots under
`modernization/validation/expected` matched for both cases.

Coverage: all 20 canonical column instances were compared for each case — 11 of `canonical.issued_policy` and 9 of
`canonical.preissued_rating` — together with the chain-completion assertions and the VSAM key corroboration. Across the
two cases that is 40 of 40 instances, with no expected field skipped. Of the 20 instances per case, 18 carry a named
COBOL item with its source locator and 2 are the warehouse-assigned `source_system_key`, one per relation. That
per-column enumeration, together with the gate results of section 4, is the measurement
`modernization/docs/traceability-matrix.md` cites for coverage.

| Case | Verdict | Coverage | Column failures | Missing | Non-zero deltas within tolerance | Status |
|---|---|---|---|---|---|---|
| `01AMOT` | PASS | 20/20 | 0 | 0 | 0 | validated against local substitute, not AWS |
| `01ACOM` | PASS | 20/20 | 0 | 0 | 0 | validated against local substitute, not AWS |
| Overall | PASS, exit status 0 | 40/40 | 0 | 0 | 0 | validated against local substitute, not AWS |

Amount comparisons, harness capture against warehouse value, tolerance `0.01`:

| Case | Column | Harness value | Warehouse value | Absolute delta | Verdict | Status |
|---|---|---|---|---|---|---|
| `01AMOT` | `payment_amount` | 500 | 500.00 | 0.00 | PASS | validated against local substitute, not AWS |
| `01AMOT` | `motor_premium_amount` | 450 | 450.00 | 0.00 | PASS | validated against local substitute, not AWS |
| `01AMOT` | `fire_premium_amount` | no value populated for this product | NULL | null expectation | PASS | validated against local substitute, not AWS |
| `01AMOT` | `crime_premium_amount` | no value populated for this product | NULL | null expectation | PASS | validated against local substitute, not AWS |
| `01AMOT` | `flood_premium_amount` | no value populated for this product | NULL | null expectation | PASS | validated against local substitute, not AWS |
| `01AMOT` | `weather_premium_amount` | no value populated for this product | NULL | null expectation | PASS | validated against local substitute, not AWS |
| `01ACOM` | `payment_amount` | 1750 | 1750.00 | 0.00 | PASS | validated against local substitute, not AWS |
| `01ACOM` | `motor_premium_amount` | no value populated for this product | NULL | null expectation | PASS | validated against local substitute, not AWS |
| `01ACOM` | `fire_premium_amount` | 13500 | 13500.00 | 0.00 | PASS | validated against local substitute, not AWS |
| `01ACOM` | `crime_premium_amount` | 3400 | 3400.00 | 0.00 | PASS | validated against local substitute, not AWS |
| `01ACOM` | `flood_premium_amount` | 7800 | 7800.00 | 0.00 | PASS | validated against local substitute, not AWS |
| `01ACOM` | `weather_premium_amount` | 2600 | 2600.00 | 0.00 | PASS | validated against local substitute, not AWS |

**No non-zero in-tolerance delta occurred in this run.** Every compared amount matched exactly at scale 2, and the
report's `unexpected_in_tolerance` count is `none` for both cases. Had any absolute delta been greater than zero and no
greater than 0.01, the report would have counted it separately and named it as unexpected; a delta above 0.01 fails the
gate. The threshold is a module constant of the comparison tool with no command-line or environment override, and the
tool cross-checks it against the threshold declared in the field map. The interpretation of the threshold is recorded as
D-04 and D-37 in `modernization/docs/decision-log.md`.

Every non-amount value matched exactly after the documented normalisation the report names per column: trailing-space
trim for fixed-width text, leading-zero-insensitive comparison for display integers, ISO calendar date for the two date
windows, and Db2 timestamp to microsecond precision for `CA-LASTCHANGED`. Chain completion passed for both cases —
including `CA_RETURN_CODE=00`, `ABEND_PRESENT=N`, `DIAG_LINK_COUNT=0000` and the expected present-or-absent state of each
SQL capture group — and the VSAM corroboration passed with length 64, key length 21 and the composite key of each case.
The 43-byte product payload of the VSAM record is mapped to no canonical column and was not compared.

**The gate's failure verdicts are exercised, not inferred.** A run in which nothing fails demonstrates only the passing
path, so the comparison tool carries its own self-test, which drives the comparison functions in process against
constructed values and needs no warehouse, no S3 endpoint and no harness output:

```bash
.venv/bin/python validation/diff_harness_vs_warehouse.py --self-test
```

Observed: `self-test summary cases=41 passed=41 failed=0`, exit status 0. Among the verdicts those cases reach — none of
which the passing run above produces — are a mismatched non-amount value reaching the failure status and the
comparison-failure exit status 1, an absolute amount delta of exactly 0.01 reaching the in-tolerance pass status with the
anomaly recorded, a delta above 0.01 failing, an absent harness authority reaching the missing status and exit status 2,
a warehouse amount carried at a scale the canonical type does not declare raising the scale anomaly, the exit-status
precedence the tool applies when more than one condition holds, and the four transform-freshness cases — a healthy dbt
run artifact accepted, a warned node accepted and named, a failed or skipped node refused, an absent or malformed
artifact refused, and the refusal itself carried into both published reports. The self-test writes only inside a private directory it
creates and removes, and returns exit status 5 when one of its own cases does not hold — a status no comparison run
returns. It is recorded here because it is what makes the PASS above meaningful: the gate is known to be able to fail.

Reports: `modernization/validation/artifacts/diff-report.md` and
`modernization/validation/artifacts/diff-report.json`.

These local results do **not** satisfy the formal AWS diff requirement. That requirement remains **OPEN**. The
comparison run recorded here exercises the transform logic against the local substitute; it closes nothing on the real
target.

## 11. Success-criteria checklist

| Criterion | Verification performed | Observed outcome | Disposition | Status |
|---|---|---|---|---|
| Extraction spec covers both entities | `modernization/extraction/extraction-spec.md` against the `counts` block of `modernization/extraction/copybook_field_map.yml` and the enforced dbt contracts | 17 logical field entries, 15 active, 1 derived, 1 declaration-only, 16 runtime business values, 18 source-derived column instances, 11 and 9 total columns, 17 landing fields; the no-formula finding stated explicitly | Closed on the local branch | validated against local substitute, not AWS |
| Exactly two canonical relations | Catalog query of `modernization/validation/local.duckdb` plus the enforced contracts of `_canonical__models.yml` | Schema `canonical` holds `issued_policy` and `preissued_rating` and nothing else | Closed on the local branch | validated against local substitute, not AWS |
| Both relations populated correctly | Row counts, contract tests, 64 data tests and the comparison gate | 2 rows and 2 distinct natural keys per relation; one matching row per sample and relation | Closed on the local branch | validated against local substitute, not AWS |
| 100% field lineage | Per-column item and locator of the comparison report, for every compared instance | 18 of 20 instances per case carry a named COBOL item with its locator; the 2 remaining instances are `source_system_key`, the sole warehouse-assigned column, one per relation | Closed on the local branch | validated against local substitute, not AWS |
| Three programs compile and execute | Compiler logs and harness captures | 15 modules and one driver compiled with return code 0 each; both cases returned `00` with complete captures | Closed on the local branch | validated against local substitute, not AWS |
| Currency comparison | Comparison report, tolerance `0.01` | Six amount comparisons across the two cases, every absolute delta 0.00; no non-zero in-tolerance delta to disclose | Closed on the local branch | validated against local substitute, not AWS |
| Non-currency comparison | Comparison report | Every non-amount value matched exactly after the documented trim and normalisation | Closed on the local branch | validated against local substitute, not AWS |
| Formal AWS diff | Real S3 and Amazon Redshift logs, and the same comparison against the real target | Not performed: both real-target gate probes exited 3 and no real target was reached | **OPEN** | not closed by this record; no AWS result exists |
| Local-substitute disclosure | This document and the published evidence set | The exact status label stands in the header of this document and beside every claimed result, and in the status line of the published evidence artifacts | Required now, present | validated against local substitute, not AWS |
| Project guide complete | Content review of `modernization/docs/project-guide.md` | Not a result of this pipeline run | Closed by that document's own review, not by this record | not a result of this run |
| Source preservation | Five file hashes and the two git checks, at eleven gate runs | All five hashes and line counts unchanged; `git status --porcelain -- base/` empty; no tracked modification outside the exempt generated-evidence inventory | Closed | validated against local substitute, not AWS |
| Zero fabricated domains or formulas | Schema review of both relations and a statement census of the three programs | No third relation, no registry, no Quote, no Loss, no commission, no formula and no derived-factor column; zero `COMPUTE`, `MULTIPLY` and `DIVIDE` statements in the three programs | Closed | validated against local substitute, not AWS |
| AWS infrastructure limit | Provisioning evidence of the gate and the landing writer | Nothing provisioned: `provisioned` is empty in the recorded selection, and no bucket, cluster, workgroup, network or IAM object was created | Closed | validated against local substitute, not AWS |

## 12. Outstanding items and the AWS closure runbook

Outstanding item, one: the formal AWS diff. Its disposition is **OPEN**. Production-grade validation requires re-running
the same dbt models unmodified against real S3 and Amazon Redshift, and this has not yet happened. Nothing in this
document may be read as closing that requirement.

The dependency restriction that used to stand beside it no longer does: the transitive `sqlparse` exception of D-75 is
closed by the raised pins of section 2 and superseded by D-118, and the audited closure of this environment carries no
known vulnerability with an available fix. Nothing in that closure bears on the formal AWS diff, which was independent of
it and remains OPEN.

The ordered steps that close it, none of which edits a model file:

1. Set AWS credentials, `AWS_REGION` and `S3_BUCKET` in the environment, naming an existing bucket; the bridge creates
   no bucket.
2. Set the Redshift connection settings that `modernization/dbt/genapp_rqi/profiles.example.yml` and the connector read —
   host or workgroup endpoint, port, database, user and authentication, schema — and `REDSHIFT_IAM_ROLE` for the `COPY`
   of `modernization/landing/load_redshift.sql`. No value is committed to this repository.
3. Unset the local-substitute endpoint setting and run `make -C modernization gate`. Both real-target probes must exit
   0, and the recorded selection must read `redshift`.
4. Run the pipeline through `land` for each case, writing the validated object and its COPY manifest to the real S3
   prefix under `landing/source_system_key=<key>/entity=policy_issue/extract_date=<YYYY-MM-DD>/`.
5. Run `load`, which applies `modernization/warehouse/ddl/01_schemas.sql` and
   `modernization/warehouse/ddl/02_raw_genapp_policy_issue.sql` and then the rendered statements of
   `modernization/landing/load_redshift.sql`, including the real `COPY`.
6. Run `dbt run` and `dbt test` with the Redshift target selected, using the same dbt models unmodified.
7. Query `canonical.issued_policy` and `canonical.preissued_rating` on Redshift through `redshift-connector`.
8. Run the same comparison, `validation/diff_harness_vs_warehouse.py --target redshift`, and attach the real-target
   logs to this document.
9. Change the formal AWS diff disposition from **OPEN** only after every gate above has passed.

Until those steps have run, every result in this document and in the published evidence set carries the label
validated against local substitute, not AWS.

## 13. Artifact index

Tracked evidence, committed in this repository:

| Path | Content | Written by |
|---|---|---|
| `modernization/validation/artifacts/verify-env.txt` | measured runtime and package versions with each deviation | `make verify-env` |
| `modernization/validation/artifacts/gate-selection.json` | recorded target selection, probe statuses and AWS disposition | `make gate` |
| `modernization/validation/artifacts/gate-probe-s3.log` | real-S3 probe output | `make gate` |
| `modernization/validation/artifacts/gate-probe-redshift.log` | real-Redshift probe output | `make gate` |
| `modernization/validation/artifacts/source-baseline.sha256` | the five source hashes of the run | `run_harness.sh` |
| `modernization/validation/artifacts/readonly-check.log` | the four read-only gate blocks the harness runs inside the `execute` stage — `harness-preflight`, `harness-compile`, `harness-execute` and `harness-final` | `run_harness.sh` |
| `modernization/validation/artifacts/translate.log` | per-program translation summary | `run_harness.sh` |
| `modernization/validation/artifacts/translation-report.json` | per-rule, per-site translation record | `run_harness.sh` |
| `modernization/validation/artifacts/compile.log` | pinned compiler environment, dialect chain and compile commands | `run_harness.sh` |
| `modernization/validation/artifacts/compile-modules.log` | compiler output of the `compile` stage, warnings included | `make compile` |
| `modernization/validation/artifacts/execute-harness.log` | harness output of the `execute` stage | `make execute` |
| `modernization/validation/artifacts/driver_01amot.log`, `captures_01amot.txt`, `commarea_post_01amot.dat` | driver log, capture file and returned record of `01AMOT` | `run_harness.sh` |
| `modernization/validation/artifacts/driver_01acom.log`, `captures_01acom.txt`, `commarea_post_01acom.dat` | the same three files for `01ACOM` | `run_harness.sh` |
| `modernization/validation/artifacts/dbt-clean.log`, `dbt-run.log`, `dbt-test.log` | dbt output of the `dbt` stage | `make dbt` |
| `modernization/validation/artifacts/diff-report.md`, `diff-report.json` | comparison gate reports | `make diff` |
| `modernization/validation/artifacts/evidence-manifest.sha256` | provenance and a SHA-256 line per published file | `run_harness.sh` |
| `modernization/validation/artifacts/runtime-versions.txt` | version, dialect and capability report of the environment | measured separately from the pipeline |
| `modernization/validation/expected/01amot/captures.normalized.json`, `modernization/validation/expected/01acom/captures.normalized.json` | capture snapshots the comparison matched | comparison gate |

Generated and ignored, present only in a working checkout:

| Path | Content |
|---|---|
| `modernization/harness/build/logs/translate.log`, `compile.log`, `source-baseline.sha256`, `translation-report.json` | the stage files the harness collects before publishing them |
| `modernization/harness/build/logs/readonly-check.log` | the read-only gate log every gate run of the pipeline appends to, emptied by the harness preflight and published once per run; at the end of a full `make all` it carries the four `harness-*` blocks and the `execute`, `load`, `dbt` and `final` stage blocks |
| `modernization/harness/build/run/<case>/commarea_post.dat`, `captures.txt`, `driver.log` | per-case returned record, captures and driver log, for every case the run selected |
| `modernization/harness/build/src`, `bin`, `compile`, `samples`, `landing`, `evidence` | translated copies, modules and driver, generated samples, landing records and staged evidence |
| `modernization/validation/local.duckdb` | the local warehouse of this branch |
| `modernization/.venv` | the project virtual environment |
| `modernization/dbt/genapp_rqi/target`, `modernization/dbt/genapp_rqi/logs` | dbt artifacts and logs |

`modernization/.gitignore` ignores exactly five roots: `/.venv/`, `/harness/build/`,
`/dbt/genapp_rqi/target/`, `/dbt/genapp_rqi/logs/` and the exactly-named `/validation/local.duckdb`.
`modernization/validation/expected/` and `modernization/validation/artifacts/` are deliberately **not** ignored: 24
artifact files and 2 expected-capture files are tracked in this repository.

## 14. Encoding note

The local harness reads and writes the workstation character set of this host; a real z/OS extract would decode the
installation's EBCDIC CCSID, documented as 285 by default, and that assumption is recorded in
`modernization/docs/project-guide.md`.

## 15. Test-infrastructure remediation after the final QA pass

> **Status — validated against local substitute, not AWS.** Every observation in this section was made on the
> local-substitute branch. The formal AWS diff requirement is **OPEN** and nothing here closes it.

The dedicated final QA pass over this project's own test infrastructure executed every authored gate, then mutated each
gate's inputs to prove it fails for the defect it claims to catch. Twenty-four of twenty-five mutation families failed at
the intended gate. The eight findings it raised — four MEDIUM, four LOW, none blocking, none an AAP-compliance,
user-rule or security defect — were gaps in that assertion surface, and each is recorded below with the behaviour
measured before the fix and the behaviour measured after it. Rationale for each choice is in
`modernization/docs/decision-log.md`, rows **D-86** through **D-105**.

| # | Gap the QA pass measured | Behaviour before | Behaviour now, observed | Where the assertion lives |
|---|---|---|---|---|
| 1 | The field map's overlay geometry was recorded and read by no tool, so the stale-length finding of D-08 had no runtime witness | `overlay_length` 77→65 and `overlay_end_byte` 177→165: builder exit **0**, extract exit 0, diff exit 0 | builder exit **3**, `field map layout group 'motor_overlay': 'overlay_length' must be 77, the summed length of the 9 item(s) declared before filler 'CA-M-FILLER', found 65`; the same contradiction ends `make translate` with exit 2. `length_constants.measured` mutated the same way: exit **3** naming the layout value it must equal | `_check_overlay_geometry` and `_check_measured_lengths`, `modernization/extraction/build_sample_commarea.py` |
| 2 | The builder consumed the `fields` census without checking it | one of the 17 entries removed: builder exit **0** (the extractor and the comparison gate did catch it) | builder exit **3**, `field map fields declares 16 logical entries and the census this builder reads holds 17`; ten further census mutants each exit 3 naming the contradicted `counts` member | `_check_field_census`, `modernization/extraction/build_sample_commarea.py` |
| 3 | `translate.py` was the only tool with no `--self-test` | no such option; the translator's rules and guards were provable only by mutating its inputs from outside | `--self-test` → `self-test summary cases=93 passed=93 failed=0`, exit 0; with rule R7 mutated (`GOBACK` → `CONTINUE`) → exit **5**, `self-test FAIL r7_return_becomes_goback`, 92 of 93 | `--self-test` in `modernization/harness/translate.py` |
| 4 | `make all` exercised 2 of the 12 authored cases and 243 of 902 assertions; the return-code, abend and route characterisation had no orchestrated entry point | `execute` invoked `run_harness.sh --success-only` unconditionally | `make all` → `execute: CASES_MODE all, 12 case(s) executed with 902 assertion(s) passed`; `CASES_MODE=success-only` → 2 cases, 243 assertions; `CASES_MODE=Both` → exit 2 naming both accepted values | `CASES_MODE` and the `execute` recipe of `modernization/Makefile` |
| 5 | No authored test saw an inapplicable product premium standing in the raw relation; the intermediate model nulled it and the suite stayed green | `update raw.genapp_policy_issue set fire_premium_amount='1000'` on an `M` row → `dbt build` **PASS**, value silently discarded | `dbt build` exit **1**, `FAIL 1 assert_product_premium_nullability`, row `landed_motor_row_premium_pattern … policy_type=M motor=450 fire=1000`; the same with all four commercial premiums set to `'0'` on the `M` row → 1 failing row; restored data → `PASS=68` | the landed leg of `modernization/dbt/genapp_rqi/tests/assert_product_premium_nullability.sql` |
| 6 | The enforced contract compares the type family and not the width on the local adapter, so a width regression in a mart cast passed | `cast(policy_type as char(1))` → `varchar(20)`: `dbt build` **PASS** | `dbt build` exit **1**, `FAIL 1 assert_canonical_column_widths`, row `canonical_model_cast_type_differs_from_contract … declared data_type char(1); model casts to varchar(20)`; restored → `PASS=68` | `modernization/dbt/genapp_rqi/tests/assert_canonical_column_widths.sql` |
| 7 | The capture snapshots pinned the default identity seed, so a documented per-checkout override failed the diff gate, and no re-baseline path existed | `HARNESS_POLICY_NUMBER=1000101 make all` → diff exit **2**, five differing keys per case, `make all` exit 2 | `HARNESS_POLICY_NUMBER=1000101 make all` → exit **0**, `PASS - 2 cases, 40 of 40 canonical column instances compared`, `git status --porcelain modernization/validation/expected` empty; the same with `HARNESS_POLICY_NUMBER=777000123 HARNESS_LASTCHANGED=1999-12-31-23.59.59.999999` → exit 0. A tampered non-seed value (`CA_CUSTOMER_NUM`) still ends the stage with exit 2 naming the key | `snapshot_seeds`, `_snapshot_value` and `--refresh-snapshot` in `modernization/validation/diff_harness_vs_warehouse.py`; the two files under `modernization/validation/expected/` |
| 8 | `validation/artifacts/verify-env.txt` named the absolute checkout it was produced in, and the extraction tool followed a symlinked read input while the translator refused one | line 1 was `verify-env report of <absolute path>/modernization`, so every checkout dirtied the file for path reasons alone; `--commarea` and `--field-map` as symbolic links → exit 0 | line 1 is `verify-env report of modernization in this checkout` and the interpreter is named `modernization/.venv/bin/python`; symlinked `--commarea` → exit **4** `the COMMAREA capture is a symbolic link`, symlinked `--field-map` → exit **4**, real files → exit 0 | the `verify-env` recipe of `modernization/Makefile`; `_read_bounded_bytes` in `modernization/extraction/extract_commarea.py` |

Two published artifacts still carry an absolute path: `dbt-clean.log` and `execute-harness.log`. Both are the verbatim
output of their producer — the dbt CLI and `harness/run_harness.sh` — and both already differ between two runs of one
checkout through clock times, a process identifier, a staging directory name and measured durations, so relativising
their paths would not make either byte-stable. That scope choice is D-99.

The read-input symlink refusal is scoped to `extraction/extract_commarea.py`, the tool the finding names.
`landing/land_to_s3.py`, `landing/load_local.py` and the comparison tool's text reader still follow a symbolic link
standing at a read input; no write in this tree traverses a link and every read input is content-validated, so no
exposure was measured. That scope choice is D-100.

One diagnostic imprecision is recorded and not changed: when a capture snapshot does not match, the comparison tool
reports the coverage of that case as `0 of 40` although every column was compared before the snapshot was read. The
verdict and the differing keys are correct; only the coverage figure of a failing run understates what ran.

## 16. Security remediation after the security QA pass

> **Status — validated against local substitute, not AWS.** Every observation in this section was made on the
> local-substitute branch, against the moto S3 endpoint of this checkout. The formal AWS diff requirement is **OPEN** and
> nothing here closes it.

A dedicated security pass over this tree exercised the source and repository boundary, path traversal and unintended
writes, command injection, SQL injection and template rendering, credential and provisioning handling, denial and error
behaviour, the privacy and status language, and the diff-gate integrity. It raised **14 findings — 0 critical, 0 high,
6 medium and 8 low, of which 4 were blocking** — and recorded the remaining categories as passing. Each finding is
recorded below with the behaviour measured before the fix and the behaviour measured after it, in this checkout, by
re-executing the reproduction the finding named. Rationale for each choice is in `modernization/docs/decision-log.md`,
rows **D-116** through **D-127**; the decision log is the only place that rationale lives, and the code carries a row
pointer and no argument.

| # | Finding, severity | Behaviour before | Behaviour now, observed | Where the control lives |
|---|---|---|---|---|
| F-1 | Command injection through `DBT_PROFILES_DIR`, MEDIUM, blocking | The value was interpolated into the three dbt recipe lines unquoted, so the shell parsed it: `DBT_PROFILES_DIR='/tmp; touch <marker>' make dbt` created the marker | Both routes are refused before any recipe runs: `Makefile:394: *** DBT_PROFILES_DIR is set to "..." which carries ";"`, exit **2**, no marker created; a legitimate value renders as `--profiles-dir '/tmp/dbt_profiles_clone1'`, single-quoted | `CALLER_ACCEPTED_CHARACTERS`, `check_caller_word` and `check_caller_words` of `modernization/Makefile`, applied to `DBT_PROFILES_DIR`, `CASE`, `CASES`, `CASES_MODE`, `SOURCE_SYSTEM_KEY`, `EXTRACT_DATE`, `STAGE`, `COBC` and `COBFLAGS` (`D-116`) |
| F-2 | `--output` writes to an arbitrary absolute path, LOW | Any canonical path outside the repository was a legal destination: `--output /etc/passwd --overwrite` was accepted by the confinement check | `--output /etc/passwd --overwrite` → exit **4**, and `/etc/passwd` unchanged (1171 bytes, 23 lines, mtime unchanged); a symlinked parent → exit **4** naming the canonical path it resolved to; the documented temporary-directory destination → exit 0, 17 keys written | `confine_destination` of `modernization/extraction/extract_commarea.py`: the generated roots this tool owns, or below the canonical system temporary directory, and nothing else (`D-125`) |
| F-3 | `--json`, `--report` and `--expected-dir` write outside the repository, LOW | Only `base/` and `synthetic_class/` were refused; every other absolute path was accepted | `--json /etc/...` → exit **4**; `--expected-dir /etc` → exit **4**, naming the snapshot path it would have written; `--report base/src/...` → exit **4**; `--json` into a sibling clone of this repository → exit **4** naming that checkout; `--report ../base/src/qa.md`, which resolves beside this checkout in the shared workspace directory → exit **4** naming that directory; the default in-repo destinations → exit 0. Every destination is validated in `resolve_settings`, before the tool reads a warehouse or a capture | `_refuse_protected_path`, `_enclosing_repository_checkout` and `resolve_settings` of `modernization/validation/diff_harness_vs_warehouse.py`, one policy shared with the extraction tool (`D-125`, narrowed by `D-128`) |
| F-4 | Unhandled `RecursionError` on deeply nested JSON, MEDIUM | A 200,000-deep document raised through the parser to the top level: a traceback naming absolute paths and exit status 1, outside the documented contract | A 200,000-deep document passed as `--record` → exit **2**, 2 lines on stderr, **0** tracebacks; the same document planted as the landed object, with a correct digest and a correct manifest so that every earlier gate accepts it → exit **2**, 0 tracebacks | `MAX_JSON_NESTING_DEPTH`, `json_nesting_depth` and `UnparsableDocumentError` in `modernization/landing/land_to_s3.py` and `modernization/landing/load_local.py`: a single-pass string-aware scan ahead of the parser, plus conversion of the parser's own `RecursionError` and of a non-`JSONDecodeError` `ValueError` — the second path a 5,000-digit integer reaches (`D-122`) |
| F-5 | `HARNESS_LOCK_WAIT` silently defaulted on invalid input, LOW | The documented `HARNESS_LOCK_WAIT_SECONDS` was validated and failed closed; an ambient value under the internal name was overwritten without a word | All four payloads → exit **2** with `ambient HARNESS_LOCK_WAIT holds <value>; a whole number of seconds from 1 to 3600 is accepted under that name`, and no side effect | `HARNESS_INTERNAL_AMBIENT`, `seconds_value_accepted`, `check_seconds_contract` and `preflight_internal_names` of `modernization/harness/run_harness.sh` (`D-117`) |
| F-6 | `GENAPP_SHOW_IDENTIFIERS=1` was not equivalent to `--show-identifiers`, LOW | The resolved value was computed and stored, but the two report call sites passed the flag alone, so the environment form never reached the output its own `--help` promised | `diff` of the two stdout captures — `--show-identifiers` against `GENAPP_SHOW_IDENTIFIERS=1` — is **IDENTICAL** | `_run` of `modernization/landing/load_local.py` now passes `show_identifiers_enabled()` at both call sites, and `SHOW_IDENTIFIERS_VARIABLE` joins `_CONSULTED_VARIABLES` (`D-123`) |
| F-7 | 4 advisories in transitive `sqlparse` 0.5.5 with the fix unreachable under the pins, MEDIUM, blocking | `dbt-core` 1.12.2 and `dbt-redshift` 1.11.0 excluded the fixing release, and the set carried a standing "not approved for production use" restriction (D-75) | `pip-audit` 2.10.1 over `modernization/requirements.txt` → `No known vulnerabilities found`, exit 0; the resolved closure carries `sqlparse` 0.6.0 | `dbt-core==1.12.3` and `dbt-redshift==1.11.1` in `modernization/requirements.txt` — the lowest releases whose declared constraints admit the fix (`D-118`) |
| F-8 | `pip` 25.3 carried 5 advisories, all with fixed releases, MEDIUM, blocking | The pinned and installed `pip` was 25.3 | `pip` 26.2.1 installed and pinned; `pip-audit` over `pip freeze --all` (107 distributions, `pip` among them) → **0** vulnerabilities, against 10 vulnerabilities in 2 packages measured the same way before the change | `PIP_PIN`/`PIP_MINIMUM` of `modernization/Makefile`, and the install instructions of `modernization/README.md` (`D-119`) |
| F-9 | The pinned-runtime baseline named versions behind their security fixes, MEDIUM, blocking | `PYTHON_PIN` 3.12.3, `GIT_PIN` 2.43.0, `APT_PIN_GIT` 1:2.43.0-1ubuntu7.3, and no floor below which the stage refuses | `make verify-env` → exit **0**, `python3.12: pinned 3.12.14 minimum 3.12.14 measured 3.12.14`, `git: pinned 2.51.0 minimum 2.43.7 measured 2.51.0`, `pip: pinned 26.2.1 measured 26.2.1`, `PASS with 4 deviation(s)`, every deviation an honest one this host cannot avoid; `HARNESS_STRICT_TOOL_VERSIONS=1` → exit **2** | `PYTHON_PIN`/`PYTHON_MINIMUM`, `GIT_PIN`/`GIT_MINIMUM`, `PIP_PIN`/`PIP_MINIMUM` and `APT_PIN_GIT` of `modernization/Makefile`, with the section 2 table above as the published record (`D-119`) |
| F-10 | No artifact hash pinning; 97 transitive packages floated, LOW | `requirements.txt` pinned the 10 direct packages by version and nothing pinned the rest by content | `modernization/requirements-lock.txt` carries **106** hash-pinned distributions and covers all 10 direct pins; `pip install --require-hashes -r modernization/requirements-lock.txt` into a fresh 3.12.14 virtual environment succeeded and reproduced the closure — 107 distributions, `dbt-core` 1.12.3 and `sqlparse` 0.6.0 among them; `make verify-env` cross-checks the lock against the direct pins | the new `modernization/requirements-lock.txt` and the lock check of the `verify-env` recipe (`D-120`) |
| F-11 | The YAML loader was weaker than its own documented contract, LOW | The field map's stated contract refused aliases and merge keys; two of its three readers accepted them | An alias in the field map → exit **3** from the extraction tool and exit **4** from the comparison tool, both reporting `the field map refers to anchor '*qa' at line 2320; an alias is not accepted`; a merge key → exit **3**; the unmodified map loads in every reader | `_FieldMapLoader` with `MAX_DOCUMENT_DEPTH` in `modernization/extraction/extract_commarea.py` and `modernization/validation/diff_harness_vs_warehouse.py`, matching the builder's loader, and the corrected contract text of `modernization/extraction/copybook_field_map.yml` (`D-126`) |
| F-12 | The decision-bearing evidence was not hash-covered, LOW | The manifest covered 11 harness files and itself; the 12 artifacts the Makefile stages publish — the comparison reports, the dbt logs, `verify-env.txt`, the gate records, `compile-modules.log`, `execute-harness.log` — carried no digest, and no gate verified one | The manifest covers **22** paths, and a fourth gate verifies each. Appending one line to `diff-report.md` → gate C **PASS**, gate D **FAIL** `does not match the digest its manifest entry states`, verdict `FAIL-EVIDENCE-COVERAGE`, exit **6**, with `sha256sum -c` independently reporting 21 of 22 OK; restoring the file byte-identically → verdict **PASS**, exit 0 | `EXIT_EVIDENCE` and gate D of `modernization/validation/verify_readonly.sh`, its `--record-evidence` mode, `CARRIED_EVIDENCE_NAMES`/`collect_carried_evidence` of `modernization/harness/run_harness.sh`, and the six `record_evidence` calls of `modernization/Makefile` (`D-121`) |
| F-13 | No object-integrity verification between land and load, MEDIUM | A tampered landed object loaded silently into the canonical relations: the loader read whatever the bucket returned | A same-length out-of-band `put_object` that replaced `BRMOT001` with `TAMPERED` while preserving the object metadata → `load_local` exit **2**, `the bytes on the bucket are not the bytes that were landed, so nothing is loaded`, and the relation unchanged; a legitimate re-land and load → exit 0, `written=1` | `RECORDED_SHA256_METADATA` and `RECORDED_LENGTH_METADATA` written as metadata of the existing `PutObject` in `modernization/landing/land_to_s3.py`, and `confirm_recorded_identity`, `fetch_manifest_bytes` and `confirm_manifest_binding` in `modernization/landing/load_local.py`, all three ahead of the parse and ahead of the database being opened (`D-124`) |
| F-14 | Identifier-bearing artifacts were created world-readable, LOW | `captures_*.txt`, `commarea_post_*.dat`, `local.duckdb` and every `artifacts/*.json` stood at mode **644**, so every account on the host could read the customer, policy and broker identifiers they carry | `make all` reports `artifact modes: 64 entries this run created, each file at 600 and the staging directory at 700`; `stat` after the run shows `captures_01amot.txt`, `captures_01acom.txt`, `commarea_post_01amot.dat`, `commarea_post_01acom.dat`, `local.duckdb` and every `artifacts/*.json` at **600** — the four paths the finding names among them; the published set measures 23 files at 600 and 1 at 644 | eight producers set the mode rather than inheriting it: `modernization/harness/run_harness.sh` (with a stage-6 gate `check_artifact_modes`), `modernization/landing/load_local.py`, `modernization/validation/diff_harness_vs_warehouse.py`, `modernization/landing/land_to_s3.py`, `modernization/Makefile`, `modernization/extraction/build_sample_commarea.py`, `modernization/harness/translate.py` and `modernization/validation/verify_readonly.sh` (`D-127`) |

**The order the verifications had to run in.** The read-only gate runs four checks in sequence and stops at the first
failure: the five source hashes, `git status --porcelain -- base/`, the tracked-modification check, and the new evidence
digest check. The third short-circuits the fourth, so while the authored fixes stood uncommitted the tracked-modification
check failed and gate D could not be reached at all. F-12 was therefore verified after the fixes were committed, on a
clean tree, which is the state the gate is designed for.

**What the fixes changed in the measured test surface.** Every tool's self-test grew by the cases its own fix needed, and
each suite passes in full in this checkout: `verify_readonly.sh` 61, `build_sample_commarea.py` 115,
`extract_commarea.py` 220, `translate.py` 93, `land_to_s3.py` 47, `load_local.py` 43,
`diff_harness_vs_warehouse.py` 41 — 620 cases in total. The harness case table is unchanged at 12 cases and 902
assertions, because the artifact-mode gate counts its checks separately from the assertion total; the dbt project is
unchanged at 4 models and 64 data tests; and the comparison gate still reports 2 cases and 40 of 40 canonical column
instances compared with 0 failures.

**Residual exposure that is recorded and not closed.**

- The evidence manifest cannot hash itself, so an actor who rewrites a published artifact **and** its manifest entry is
  not detected by gate D. What covers that case is the git history of the tracked manifest, not the gate (`D-121`).
- Of the 24 tracked files under `modernization/validation/artifacts/`, 22 are exempt generated evidence a run rewrites and
  gate D covers by digest, the 23rd is the manifest itself, and the 24th is `runtime-versions.txt`, which no run writes.
  That last file is not in the exempt inventory at all, so it is covered by gate C instead: any modification to it counts
  as a tracked modification and fails the gate until it is committed. Every tracked artifact is therefore covered by one
  of the two gates, by digest or by tracked-file equality.
- A stage that fails after rewriting its artifact leaves that artifact's manifest entry unrefreshed, and gate D then
  fails closed until the stage succeeds. That is deliberate, and it was observed exactly once during this pass, after a
  strict-mode `verify-env` probe was made to fail on purpose; one successful `make verify-env` cleared it.
- The land-time digest is object metadata on the object it describes, so a caller who can rewrite the object can also
  rewrite its metadata; the control detects out-of-band tampering, not a fully compromised prefix. Objects landed before
  this change carry no digest and fail closed until they are landed again. On the real target the same binding is
  recorded in `modernization/landing/load_redshift.sql` as provenance only: Amazon Redshift enforces no digest for a JSON
  `COPY`, so the real-target leg of this control stays **OPEN** with the formal AWS diff (`D-124`).
- No apt `python3.12` package in any configured suite reaches the accepted interpreter minimum of 3.12.14, so the
  documented apt line alone cannot satisfy the floor; this host's interpreter is built from source, and section 2 records
  the packaging pin separately from the interpreter measurement (`D-119`).
- The digests of `modernization/requirements-lock.txt` are those of the `cp312` `linux-x86_64` wheels this project
  resolves; another interpreter series or platform requires the lock to be regenerated, and `pip` refuses the install
  rather than silently resolving something else (`D-120`).
- The write-confinement policy still accepts any destination below the resolved temporary directory that is not a
  repository checkout and is not the directory holding this checkout. That is the documented landing-into-a-temporary-
  directory workflow, and it was deliberately kept: what was closed instead is the reach into another working tree. A
  working tree with no `.git` entry — an exported archive — is not recognised as a checkout and is accepted as an
  ordinary temporary destination (`D-128`).
- Three file-mode exceptions stand by design: `modernization/validation/artifacts/runtime-versions.txt` stays at 644
  because no producer writes it and it carries no identifier; a directory that already existed keeps its mode, so a
  long-lived checkout can hold staging directories at 755 while a fresh clone creates them at 700, and the files inside
  are 600 either way; and the compiled driver, the shared-object modules and the zero-byte lock file are not narrowed
  because they are executed or appended to rather than read for their content (`D-127`).

**One divergence from the AAP dependency inventory, taken deliberately.** AAP §0.5.2 pins `python3.12` 3.12.3,
`pip` 25.3, `git` 2.43.0, `dbt-core` 1.12.2 and `dbt-redshift` 1.11.0. Findings F-7, F-8 and F-9 are precisely that four
of those five values name releases with published advisories and available fixes, so the delivered pins are
`dbt-core` 1.12.3, `dbt-redshift` 1.11.1, `pip` 26.2.1, `git` 2.51.0 and `python3.12` 3.12.14, each with a floor below
which `verify-env` refuses. The GnuCOBOL pins are untouched, because no finding names them. The divergence, what it
buys and what it costs are recorded as D-118 and D-119; `modernization/docs/traceability-matrix.md` carries the lock file
as a created artifact.

