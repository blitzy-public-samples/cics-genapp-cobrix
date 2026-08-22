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
| 1 | `verify-env` | PASS with 7 deviation(s) | `modernization/validation/artifacts/verify-env.txt` | validated against local substitute, not AWS |
| 2 | `gate` | selected target `local_substitute`; both real-target probes exited 3 | `modernization/validation/artifacts/gate-selection.json` | validated against local substitute, not AWS |
| 3 | `verify-readonly` `baseline` | verdict PASS, exit_code 0 | `modernization/validation/artifacts/readonly-check.log` | validated against local substitute, not AWS |
| 4 | `translate` | 2 sample records and the translated tree under `modernization/harness/build` | `modernization/validation/artifacts/translate.log` | validated against local substitute, not AWS |
| 5 | `verify-readonly` `translate` | verdict PASS, exit_code 0 | `modernization/validation/artifacts/readonly-check.log` | validated against local substitute, not AWS |
| 6 | `compile` | 15 modules and one driver | `modernization/validation/artifacts/compile-modules.log` | validated against local substitute, not AWS |
| 7 | `verify-readonly` `compile` | verdict PASS, exit_code 0 | `modernization/validation/artifacts/readonly-check.log` | validated against local substitute, not AWS |
| 8 | `execute` | both cases returned `00` with the policy, product and VSAM captures present | `modernization/validation/artifacts/execute-harness.log` | validated against local substitute, not AWS |
| 9 | `verify-readonly` `execute` | verdict PASS, exit_code 0 | `modernization/validation/artifacts/readonly-check.log` | validated against local substitute, not AWS |
| 10 | `extract` | one landing record per case, 17 keys each | the landing records `modernization/harness/build/landing/landing_01amot.json` and `landing_01acom.json`; the stage's console output is not separately retained | validated against local substitute, not AWS |
| 11 | `land` and `load`, twice | one object plus its COPY manifest per case; `raw.genapp_policy_issue` carries 2 rows | the loaded relation in `modernization/validation/local.duckdb`; the stage's console output is not separately retained | validated against local substitute, not AWS |
| 12 | `verify-readonly` `load` | verdict PASS, exit_code 0 | `modernization/validation/artifacts/readonly-check.log` | validated against local substitute, not AWS |
| 13 | `dbt` | `dbt run` PASS=4, `dbt test` PASS=63, no warning and no error | `modernization/validation/artifacts/dbt-run.log`, `modernization/validation/artifacts/dbt-test.log` | validated against local substitute, not AWS |
| 14 | `verify-readonly` `dbt` | verdict PASS, exit_code 0 | `modernization/validation/artifacts/readonly-check.log` | validated against local substitute, not AWS |
| 15 | `diff` | PASS, 2 cases, 40 of 40 canonical column instances compared, 0 failed | `modernization/validation/artifacts/diff-report.md` | validated against local substitute, not AWS |
| 16 | `verify-readonly` `final` | verdict PASS, exit_code 0, 0 tracked modifications | `modernization/validation/artifacts/readonly-check.log` | validated against local substitute, not AWS |

## 2. Environment and versions

Measured host of the run: Ubuntu 25.10 (Questing Quokka), `x86_64`. The Python interpreter this project runs on is
`/usr/local/bin/python3.12`, built from source; the configured apt suites of this host carry no `python3.12` package.
`modernization/.venv` holds the project interpreter and every pinned package, and `modernization/Makefile` invokes
Python and dbt through `.venv/bin/...` by explicit path.

`make verify-env` result: **PASS with 7 deviation(s)**, report `modernization/validation/artifacts/verify-env.txt`,
`HARNESS_STRICT_TOOL_VERSIONS` unset (`strict tool versions: no`). The stage installs nothing.

| Item | Pinned | Measured in this run | Verdict | Status |
|---|---|---|---|---|
| `python3.12` on PATH | 3.12.3 | 3.12.14 | DEVIATION | validated against local substitute, not AWS |
| `cobc` (GnuCOBOL) | 3.1.2.0 | 3.2.0 | DEVIATION | validated against local substitute, not AWS |
| `git` | 2.43.0 | 2.51.0 | DEVIATION | validated against local substitute, not AWS |
| apt `python3.12` | 3.12.3-1ubuntu0.15 | not installed through apt | DEVIATION | validated against local substitute, not AWS |
| apt `python3.12-venv` | 3.12.3-1ubuntu0.15 | not installed through apt | DEVIATION | validated against local substitute, not AWS |
| apt `gnucobol3` | 3.1.2-5.1ubuntu1 | 3.2-4 | DEVIATION | validated against local substitute, not AWS |
| apt `git` | 1:2.43.0-1ubuntu7.3 | 1:2.51.0-1ubuntu1 | DEVIATION | validated against local substitute, not AWS |
| `.venv/bin/python` | 3.12 series | 3.12.14 | in series | validated against local substitute, not AWS |
| `pip` in the virtual environment | 25.3 | 25.3 | MATCH | validated against local substitute, not AWS |

Every direct Python pin of `modernization/requirements.txt` was measured inside the virtual environment and matched
exactly; the stage reported `pins measured: 10`.

| Package | Pinned | Measured | Verdict | Status |
|---|---|---|---|---|
| `dbt-core` | 1.12.2 | 1.12.2 | MATCH | validated against local substitute, not AWS |
| `dbt-duckdb` | 1.11.0 | 1.11.0 | MATCH | validated against local substitute, not AWS |
| `dbt-redshift` | 1.11.0 | 1.11.0 | MATCH | validated against local substitute, not AWS |
| `duckdb` | 1.5.5 | 1.5.5 | MATCH | validated against local substitute, not AWS |
| `redshift-connector` | 2.1.16 | 2.1.16 | MATCH | validated against local substitute, not AWS |
| `boto3` | 1.43.74 | 1.43.74 | MATCH | validated against local substitute, not AWS |
| `botocore` | 1.43.74 | 1.43.74 | MATCH | validated against local substitute, not AWS |
| `moto[s3,server]` | 5.2.2 | 5.2.2 | MATCH | validated against local substitute, not AWS |
| `PyYAML` | 6.0.3 | 6.0.3 | MATCH | validated against local substitute, not AWS |
| `jsonschema` | 4.26.0 | 4.26.0 | MATCH | validated against local substitute, not AWS |

`modernization/validation/artifacts/runtime-versions.txt` carries the same three system-runtime deviations together with
the resolved compiler dialect chain, the numeric-store keys of that chain and one capability probe per behaviour the
harness relies on. The decision-log rows that cover version pinning and the accepted deviations are D-45 and D-48 in
`modernization/docs/decision-log.md`.

**Standing restriction on this dependency set.** These pins resolve the transitive package `sqlparse` at 0.5.5, and the
release that fixes its published advisories is excluded by the declared constraint of both `dbt-core` 1.12.2 and
`dbt-redshift` 1.11.0, so **this dependency set is not approved for production use**. Every result recorded in this
document was produced under that restriction: the dbt CLI was run as a bounded batch invocation over the authored model
and test set of `modernization/dbt/genapp_rqi`, with no dbt server, no RPC mode and no process accepting SQL from a
caller. The exception, its owner and its review trigger are recorded as D-75 in
`modernization/docs/decision-log.md`. It is independent of the formal AWS diff of section 12: neither closes or lifts
the other.

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
`git status --porcelain -- base/ produced no output`, and `gate C result: PASS`:

| Gate run | Stage label | Timestamp (UTC) | Verdict | Exit code | Status |
|---|---|---|---|---|---|
| 1 | `baseline` | 2026-08-22T15:20:59Z | PASS | 0 | validated against local substitute, not AWS |
| 2 | `translate` | 2026-08-22T15:21:00Z | PASS | 0 | validated against local substitute, not AWS |
| 3 | `compile` | 2026-08-22T15:21:02Z | PASS | 0 | validated against local substitute, not AWS |
| 4 | `execute` | 2026-08-22T15:21:10Z | PASS | 0 | validated against local substitute, not AWS |
| 5 | `load` | 2026-08-22T15:21:13Z | PASS | 0 | validated against local substitute, not AWS |
| 6 | `dbt` | 2026-08-22T15:21:24Z | PASS | 0 | validated against local substitute, not AWS |
| 7 | `final` | 2026-08-22T15:21:24Z | PASS | 0 | validated against local substitute, not AWS |

`modernization/harness/run_harness.sh` ran the same gate at four further points inside the `execute` stage — labels
`harness-preflight`, `harness-compile`, `harness-execute` and `harness-final` — and reported
`source guard: PASS at 4 of 4 points`. Eleven gate runs passed in this pipeline in total.

At the final gate, `git diff --name-only HEAD` reported `(no tracked modification)` and
`tracked modifications: 0`; 7 of the 23 exact paths of the exempt generated-evidence inventory were reported modified,
each recorded as exempt and none counted. No pre-existing repository file was modified by this work: every authored file
of the bridge lives under `modernization/`, and the five source artifacts above are byte-identical to their baseline.
The exempt inventory and its extension to the Makefile stage records are recorded as D-47 and D-65 in
`modernization/docs/decision-log.md`.

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
| `00` | Success | [base/src/lgapol01.cbl:104-126], [base/src/lgapdb01.cbl:290-294] | Yes — both executed cases |
| `70` | Policy insert returned SQLCODE −530 | [base/src/lgapdb01.cbl:290-299] | No |
| `80` | VSAM write response was not normal | [base/src/lgapvs01.cbl:142-147] | No |
| `90` | SQL failure; subtype insert failures also abend `LGSQ` | [base/src/lgapdb01.cbl:300-303,389-395,427-433,473-479,547-553] | No |
| `98` | COMMAREA too short | [base/src/lgapol01.cbl:108-116], [base/src/lgapdb01.cbl:181-213] | No |
| `99` | Unsupported request id | [base/src/lgapdb01.cbl:184-207] | No |

In the two cases this pipeline executed the captures record `INJECT_POLICY_SQLCODE=0`, `INJECT_SUBTYPE_SQLCODE=0`,
`SQLCODE_LAST=0` and `INJECT_VSAM_RESP=0`: every SQL stub reported SQLCODE 0 and the VSAM write reported the normal
response, so the `70`, `90`, `98`, `99`, `80` and `LGSQ` paths are documented here and were **not exercised** by this
run. The endowment route was **not executed**, and the house route was compiled and **not exercised** by this run. The
`execute` stage selects the two success cases through `run_harness.sh --success-only`; the case table of
`modernization/harness/run_harness.sh` carries ten further cases that this stage does not select, and this record claims
no result for them. The unexercised routes and paths are recorded as D-18, D-20 and D-21 in
`modernization/docs/decision-log.md`.

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
```

The writer reported `run mode 'local_substitute' from --run-mode, addressing the loopback endpoint` for both cases, a
269-byte COPY manifest beside each data object, and — for the second case — its documented warning that the key already
carried an object which that landing replaced. No credential, bucket or endpoint value is echoed by the writer, and the
stage created no bucket.

`make load` used `modernization/landing/load_local.py` on this branch. Per case it bound the download to the exact
object length (499 and 508 bytes), reported `17 landed columns` with the SHA-256 of the object, applied 2 statements
from `modernization/warehouse/ddl/01_schemas.sql` and 1 statement from
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
Found 4 models, 63 data tests, 1 source, 501 macros
```

| Model | Materialization | Relation created | Result | Status |
|---|---|---|---|---|
| `stg_genapp__policy_issue` | view | `staging.stg_genapp__policy_issue` | OK | validated against local substitute, not AWS |
| `int_policy_issue_decoded` | view | `intermediate.int_policy_issue_decoded` | OK | validated against local substitute, not AWS |
| `canonical_issued_policy` | table | `canonical.issued_policy` | OK | validated against local substitute, not AWS |
| `canonical_preissued_rating` | table | `canonical.preissued_rating` | OK | validated against local substitute, not AWS |

`dbt run` finished `Completed successfully` with `Done. PASS=4 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=4`.
`dbt test` finished `Completed successfully` with `Done. PASS=63 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=63`, the
63 data tests comprising the generic tests declared in the model YAML files — the enforced contracts, `not_null`,
`accepted_values` and `relationships` — and the three singular tests `assert_issued_policy_unique_key`,
`assert_preissued_rating_unique_key` and `assert_product_premium_nullability`. Output retained in
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

Run metadata recorded in the report: generated at 2026-08-22T15:21:24Z; target `duckdb`; adapter `duckdb 1.5.5`;
python 3.12.14; connection `modernization/validation/local.duckdb`; source-system key `GENAPP_CLASS_EXEMPLAR`; amount
tolerance `0.01`; expected amount scale 2; capture snapshots under `modernization/validation/expected` matched for both
cases.

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

Observed: `self-test summary cases=27 passed=27 failed=0`, exit status 0. Among the verdicts those cases reach — none of
which the passing run above produces — are a mismatched non-amount value reaching the failure status and the
comparison-failure exit status 1, an absolute amount delta of exactly 0.01 reaching the in-tolerance pass status with the
anomaly recorded, a delta above 0.01 failing, an absent harness authority reaching the missing status and exit status 2,
a warehouse amount carried at a scale the canonical type does not declare raising the scale anomaly, and the exit-status
precedence the tool applies when more than one condition holds. The self-test writes only inside a private directory it
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
| Both relations populated correctly | Row counts, contract tests, 63 data tests and the comparison gate | 2 rows and 2 distinct natural keys per relation; one matching row per sample and relation | Closed on the local branch | validated against local substitute, not AWS |
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

One standing restriction stands beside it and is not a validation item: the dependency set of this environment is **not
approved for production use** while the transitive `sqlparse` exception of section 2 stands (D-75). It is not closed by
this runbook, and closing the formal AWS diff does not lift it.

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
| `modernization/validation/artifacts/readonly-check.log` | every read-only gate block of the run | `run_harness.sh` |
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
