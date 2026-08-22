# Translation Rules — GnuCOBOL Harness for the GenApp Policy-Issue Chain

> **Status — validated against local substitute, not AWS.**
> GnuCOBOL compiles and executes *translated copies* of the three named programs, with the CICS and Db2
> services those copies call emulated by the harness stubs of this directory. The five named source
> artifacts are inputs only and remain byte-identical; no statement below changes one of them.

This document records **what** the harness rewrites, **where** each rewrite applies and **what the harness
cannot reproduce**. It carries no rationale. Every "why" belongs to
[`modernization/docs/decision-log.md`](../docs/decision-log.md); the rows this harness depends on are named
in [§7 Rationale](#7-rationale).

The topology of the compile, execute, transform and compare gates is
**Figure 5 — Validation Harness Control Flow** in
[`modernization/docs/architecture.md`](../docs/architecture.md). This document defines no diagram of its own.

---

## 1. Scope and the read-only guarantee

### 1.1 The only inputs

The translator reads exactly five files, and nothing else in the repository:

| Input | Role |
|---|---|
| `base/src/lgapol01.cbl` | Entry program: header validation, the first chain link, return behaviour |
| `base/src/lgapdb01.cbl` | Db2 program: request routing, host-variable moves, the SQL blocks, identity and timestamp recovery, the second chain link |
| `base/src/lgapvs01.cbl` | VSAM program: composite-key construction and the 64-byte write |
| `base/src/lgcmarea.cpy` | COMMAREA declarations; copied verbatim into the generated tree |
| `base/src/lgpolicy.cpy` | Length constants and Db2 host-variable declarations; copied verbatim into the generated tree |

### 1.2 What the guarantee is

- No source file is ever preprocessed in place. The three `.cbl` files are read, rewritten and written as
  **new files** under `modernization/harness/build/src/`; the two `.cpy` files are copied there byte-for-byte.
- `modernization/harness/build/**` is the only path any harness stage writes program text into.
- Before it generates anything, `modernization/harness/translate.py` records the SHA-256 digest of each of
  the five inputs to **`build/logs/source-baseline.sha256`** in `sha256sum` format, and re-verifies those
  digests after generation. The run also asserts that `git status --porcelain -- base/src/` reports no change.
- `modernization/validation/verify_readonly.sh` re-verifies the same five digests and line counts, requires
  `git status --porcelain -- base/` to be empty and requires `git diff --name-only HEAD` to hold no tracked
  modification. It runs before generation, after each harness stage and as the final gate.
- The published copy of the baseline is `modernization/validation/artifacts/source-baseline.sha256`.

### 1.3 What is never consulted

The nine diagnostic `LINK` sites name a program outside the authorized surface. The harness substitutes a
stub for all nine and **never reads that program's implementation**; the substitution is derived from the call
sites alone — the area operand and its length. No other pre-existing repository file is opened, listed or
searched by the translator or by this document.

---

## 2. Measured statement census

Every figure below is measured from the five inputs, with comment lines excluded and continuation lines
folded into the statement they belong to.

### 2.1 Embedded statements per program

| Program | Lines | `EXEC CICS` | `EXEC SQL` | SQL breakdown |
|---|---:|---:|---:|---|
| `base/src/lgapol01.cbl` | 169 | 9 | 0 | — |
| `base/src/lgapdb01.cbl` | 595 | 20 | 11 | 3 `INCLUDE` + 8 DML |
| `base/src/lgapvs01.cbl` | 188 | 7 | 0 | — |
| **Total** | **952** | **36** | **11** | **3 `INCLUDE` + 8 DML** |

### 2.2 Distinct CICS verbs

| Verb | Sites | Where |
|---|---:|---|
| `ABEND` | 6 | `lgapol01.cbl:101`; `lgapdb01.cbl:168,393,431,477,551` |
| `ASKTIME` | 3 | `lgapol01.cbl:140-141`; `lgapdb01.cbl:566-567`; `lgapvs01.cbl:156-157` |
| `FORMATTIME` | 3 | `lgapol01.cbl:142-145`; `lgapdb01.cbl:568-571`; `lgapvs01.cbl:158-161` |
| `LINK` | 11 | 1 to `LGAPDB01`, 1 to `LGAPVS01`, 9 to the literal `'LGSTSQ'` |
| `RETURN` | 12 | `lgapol01.cbl:115,126`; `lgapdb01.cbl:205,212,250,298,303,394,432,478,552`; `lgapvs01.cbl:146` |
| `WRITE` | 1 | `lgapvs01.cbl:135-141` |
| **Total** | **36** | 6 + 3 + 3 + 11 + 12 + 1 = 36, which is 9 + 20 + 7 |

### 2.3 EIB fields referenced

The three programs reference **exactly five** EIB fields, and no sixth EIB symbol appears anywhere in the
five inputs:

| Field | References | Where |
|---|---:|---|
| `EIBCALEN` | 17 | `lgapol01.cbl:91,98,113,154,155,156`; `lgapdb01.cbl:154,165,210,339,580,581,582`; `lgapvs01.cbl:97,173,174,175` |
| `EIBRESP2` | 1 | `lgapvs01.cbl:143` |
| `EIBTASKN` | 2 | `lgapol01.cbl:90`; `lgapdb01.cbl:153` |
| `EIBTRMID` | 2 | `lgapol01.cbl:89`; `lgapdb01.cbl:152` |
| `EIBTRNID` | 2 | `lgapol01.cbl:88`; `lgapdb01.cbl:151` |
| **Total** | **24** | across five distinct names |

### 2.4 Line width

The maximum line length is **exactly 72** in all five inputs. Every generated line is held to the same
bound: `translate.py` fails the run rather than emit a line reaching column 73, and the generated programs
measure 72 as their maximum as well.

---

## 3. Generated layout

`modernization/harness/build/` is regenerated by every run and is ignored by `modernization/.gitignore`
through the entry `/harness/build/`. Nothing in it is tracked.

| Path | Contents |
|---|---|
| `build/src/` | The three translated programs `lgapol01.cbl`, `lgapdb01.cbl`, `lgapvs01.cbl`; verbatim `lgcmarea.cpy` and `lgpolicy.cpy`; and verbatim copies of the four members of `modernization/harness/copybooks/` — `dfheiblk.cpy`, `dfhresp.cpy`, `hsqlca.cpy`, `hcapture.cpy`. Nine files, so the single option `-I modernization/harness/build/src` resolves every `COPY` of every compile. |
| `build/bin/` | 15 callable modules named `<PROGRAM-ID>.so` — 12 stubs and the 3 translated programs — plus the `driver` executable. |
| `build/samples/` | The generated fixed-width sample records, one per case, each exactly 32,500 characters. |
| `build/run/<case>/` | Per-case output: `commarea_post.dat`, `captures.txt`, `driver.log`. |
| `build/logs/` | `source-baseline.sha256`, `translation-report.json`, `translate.log`, `compile.log`, `evidence-manifest.sha256`. |
| `build/evidence/<timestamp>-<pid>/` | The evidence set staged by a run before it is published to `modernization/validation/artifacts/`. |
| `build/probe/<name>/` | Scratch tree of the environment probes a run executes alongside the case table. |

`translate.py` creates `src`, `bin`, `samples`, `logs` and `run`, and refuses any build directory other than
the `modernization/harness/build` tree of its own checkout.

---

## 4. The rewrite rules

Fourteen rules cover every line of the three programs. Rules R1–R13 rewrite a construct; R14 carries
everything else through unchanged. `translate.py` holds the expected site count of each rule and **fails the
run when an observed count differs**, so the table below is enforced rather than merely documented. The
observed counts of the current build are recorded per rule and per site in
`build/logs/translation-report.json`.

| Rule | Source construct | Source locators (sites) | Generated construct | Required control |
|---|---|---|---|---|
| **R1** | `PROCESS SQL` compiler directive | `lgapdb01.cbl:1` (1) | Fixed-format comment: `*PROCESS SQL  (R1: commented for the harness build)` | Comment stays within column 72; the directive reaches no compiler |
| **R2** | `EXEC SQL INCLUDE … END-EXEC` | `lgapdb01.cbl:75-77`, `lgapdb01.cbl:124-126`, `lgapdb01.cbl:135-137` (3) | `COPY LGPOLICY.` · `COPY HSQLCA.` · `COPY LGCMAREA.` | Each member resolves from `build/src`. The `LGCMAREA` block stays nested inside the `01  DFHCOMMAREA.` group declared at `lgapdb01.cbl:134`: `lgcmarea.cpy` begins at level 03 and supplies no level-01 of its own. `SQLCA` resolves to the harness member `hsqlca.cpy`. Each replacement inherits the trailing period of the `END-EXEC` line it replaces |
| **R3** | `PROCEDURE DIVISION.` | `lgapol01.cbl:77`, `lgapdb01.cbl:143`, `lgapvs01.cbl:91` (3) | `PROCEDURE DIVISION USING DFHCOMMAREA.` | Binds the linkage record for the dynamic `CALL … USING DFHCOMMAREA` that R5 and the driver issue |
| **R4** | `WORKING-STORAGE SECTION` anchor line | one per program (3) | Inserted after the anchor: `COPY DFHEIBLK.`, `01  HARNESS-ABEND-CODE           PIC X(4)  VALUE SPACES.`, `01  HARNESS-DIAG-LEN             PIC S9(8) COMP VALUE +0.` — plus `COPY DFHRESP.` in `lgapvs01.cbl` **only** | The anchor line itself is copied unchanged and the rule consumes no source line. `DFHEIBLK` backs the five EIB fields with `EXTERNAL` storage shared with the driver and the stubs |
| **R5** | Chain `EXEC CICS LINK` with `LENGTH(32500)` | `lgapol01.cbl:121-124` → `LGAPDB01`; `lgapdb01.cbl:243-246` → `LGAPVS01` (2) | `MOVE 32500 TO EIBCALEN` followed by `CALL LGAPDB01 USING DFHCOMMAREA.` / `CALL LGAPVS01 USING DFHCOMMAREA.` | Both call operands are **identifiers, not literals**: the `PIC X(8)` data items declared at `lgapol01.cbl:51` (`VALUE 'LGAPDB01'`) and `lgapdb01.cbl:119` (`VALUE 'LGAPVS01'`). Link length 32500 and the call order `LGAPOL01` → `LGAPDB01` → `LGAPVS01` are preserved unchanged |
| **R6** | Diagnostic `EXEC CICS LINK PROGRAM('LGSTSQ')` | `lgapol01.cbl:149-152,157-160,163-166`; `lgapdb01.cbl:575-578,583-586,589-592`; `lgapvs01.cbl:169-172,176-179,182-185` (9) | `MOVE LENGTH OF <area> TO HARNESS-DIAG-LEN` followed by `CALL 'CICS-DIAG-LINK' USING <area> HARNESS-DIAG-LEN` | The stub accepts any area length; the nine sites supply four different ones. The named program's implementation is never read |
| **R7** | `EXEC CICS RETURN` | `lgapol01.cbl:115,126`; `lgapdb01.cbl:205,212,250,298,303,394,432,478,552`; `lgapvs01.cbl:146` (12) | `GOBACK`, emitted **inline** | No called stub — see [§4.1](#41-two-rules-that-are-easy-to-get-wrong). The trailing period of the source statement is inherited |
| **R8** | `EXEC CICS ABEND ABCODE(…) NODUMP` | `lgapol01.cbl:101` (`'LGCA'`); `lgapdb01.cbl:168` (`'LGCA'`), `393`, `431`, `477`, `551` (`'LGSQ'`) (6) | `MOVE '<code>' TO HARNESS-ABEND-CODE`, then `CALL 'CICS-ABEND' USING HARNESS-ABEND-CODE`, then `GOBACK` | The **caller** issues the `GOBACK`; the stub records the code and terminates nothing. `NODUMP` has no harness counterpart. No later business step runs |
| **R9** | `WRITE FILE('KSDSPOLY')` | `lgapvs01.cbl:135-141` (1) | `CALL 'CICS-WRITE' USING 'KSDSPOLY' WF-Policy-Info '00064' WF-Policy-Key '00021' WS-RESP` | All six operands reach the capture module in source-operand order. The two lengths — the 64-byte record at `lgapvs01.cbl:137` and the 21-byte key at `lgapvs01.cbl:139` — are passed as zero-padded 5-digit alphanumeric literals read by `PIC 9(5)` receivers. The stub sets the normal response by default |
| **R10** | `EXEC CICS ASKTIME ABSTIME(…)` | `lgapol01.cbl:140-141`; `lgapdb01.cbl:566-567`; `lgapvs01.cbl:156-157` (3) | `CALL 'CICS-ASKTIME' USING <abstime>` | Deterministic harness time; the source's own `ABSTIME` operand is passed unchanged |
| **R11** | `EXEC CICS FORMATTIME` | `lgapol01.cbl:142-145`; `lgapdb01.cbl:568-571`; `lgapvs01.cbl:158-161` (3) | `CALL 'CICS-FORMATTIME' USING <abstime> <mmddyyyy> <time>` | Formats the same deterministic value; the three source operands are passed in source order |
| **R12** | `DFHRESP(NORMAL)` macro | `lgapvs01.cbl:142` (1) | The named constant `DFHRESP-NORMAL`, declared `PIC S9(8) COMP VALUE +0` by `dfhresp.cpy` | Only `NORMAL` has a harness constant; any other response condition fails the run. The rest of the condition is left unchanged |
| **R13** | The 8 `EXEC SQL` DML blocks | `lgapdb01.cbl:268-288`, `lgapdb01.cbl:308-310`, `lgapdb01.cbl:316-321`, `lgapdb01.cbl:346-366`, `lgapdb01.cbl:368-386`, `lgapdb01.cbl:409-425`, `lgapdb01.cbl:449-471`, `lgapdb01.cbl:499-545` (8) | The **7** `SQL-*` stub calls defined by `statement_map.yml` — see [§4.2](#42-the-statement_mapyml-contract) | Every host variable is named in an explicit `USING` list in source order. A block present in the source with no entry in the map fails the run |
| **R14** | Everything else | 694 source lines | Copied **byte-for-byte** | Its count is observed rather than pinned to a construct; the report records it |

Site totals: R1–R13 rewrite `1 + 3 + 3 + 3 + 2 + 9 + 12 + 6 + 1 + 3 + 3 + 1 + 8` constructs. Of these, the
36 `EXEC CICS` sites are covered by R5 (2) + R6 (9) + R7 (12) + R8 (6) + R9 (1) + R10 (3) + R11 (3) = 36, and
the 11 `EXEC SQL` blocks by R2 (3) + R13 (8) = 11. R1, R3, R4 and R12 act on ordinary source lines rather
than on embedded statements.

### 4.1 Two rules that are easy to get wrong

**A called `RETURN` stub is prohibited.** R7 emits `GOBACK` inline. A called stub would return control to the
statement after the call and execution would resume. The concrete evidence sits in the entry program: the
`EXEC CICS RETURN` at `lgapol01.cbl:126` is the only statement preventing `MAINLINE` from running on through
`MAINLINE-EXIT` at `128-129` — whose `EXIT` is a no-op — and into the `WRITE-ERROR-MESSAGE` paragraph at
`lgapol01.cbl:137`. Every one of the 12 return sites is a real exit.

**The mixed-case `Copy LGCMAREA.` statements are left untouched.** `lgapol01.cbl:71` and `lgapvs01.cbl:87`
already spell a plain COBOL `COPY`, not an `EXEC SQL INCLUDE`, and they resolve as written under the mandated
`-ffold-copy=LOWER -ext cpy`. R2 does not apply to them and R14 carries them through byte-for-byte; they
appear at `lgapol01.cbl:74` and `lgapvs01.cbl:91` in the generated copies, shifted by the three lines R4
inserted above them. The generated tree therefore holds three resolved `COPY LGCMAREA` statements: these two
plus the one R2 produced at `lgapdb01.cbl:134`.

### 4.2 The `statement_map.yml` contract

`modernization/harness/statement_map.yml` maps all 11 `EXEC SQL` blocks: 3 under `includes` (R2) and 8 under
`dml` (R13). The 8 DML entries resolve to **7** distinct `call_program` names.

| `call_program` | Block(s) | `USING` arity | Notes |
|---|---|---:|---|
| `SQL-INSERT-POLICY` | `lgapdb01.cbl:268-288` | **7** | Nine columns, two of which take no host variable: `POLICYNUMBER` is supplied by the keyword `DEFAULT` at `lgapdb01.cbl:279` and `LASTCHANGED` by `CURRENT TIMESTAMP` at `lgapdb01.cbl:284` |
| `SQL-SET-IDENTITY` | `lgapdb01.cbl:308-310` | **1** | `DB2-POLICYNUM-INT`, direction `out`; the statement names no table |
| `SQL-SELECT-LASTCHANGED` | `lgapdb01.cbl:316-321` | **2** | The `INTO` target `CA-LASTCHANGED` first, then the `WHERE` predicate host `DB2-POLICYNUM-INT` |
| `SQL-INSERT-ENDOWMENT` | `lgapdb01.cbl:346-366` **and** `lgapdb01.cbl:368-386` | **9** | One normalised superset list serving both source branches, ordered exactly as the with-varchar branch declares it. The shorter branch's 8 operands are a prefix of the 9. The stub ignores the padding argument when `WS-VARY-LEN` is zero or negative |
| `SQL-INSERT-HOUSE` | `lgapdb01.cbl:409-425` | **7** | |
| `SQL-INSERT-MOTOR` | `lgapdb01.cbl:449-471` | **10** | Includes `DB2-M-PREMIUM-INT` |
| `SQL-INSERT-COMMERCIAL` | `lgapdb01.cbl:499-545` | **20** | Includes all four commercial premium hosts, and the four peril codes the chain cannot execute without |

**The measured ordering constraint.** `INSERT-POLICY` must precede `INSERT-COMMERCIAL`: the commercial insert
supplies `:CA-LASTCHANGED` as its `RequestDate` value at `lgapdb01.cbl:525`, and `CA-LASTCHANGED` is populated
by exactly one statement — the read-back at `lgapdb01.cbl:316-321`, the last `EXEC SQL` block of paragraph
`INSERT-POLICY`. The map records this as the `execution_order` entry `lastchanged_before_commercial`, with
`reason_kind: data_dependency` on host `CA-LASTCHANGED`. Seven further entries cover the same ground for the
other statements: `policy_first_captured`, `policy_before_identity`, `identity_before_lastchanged`,
`lastchanged_before_motor`, `lastchanged_before_house`, `lastchanged_before_endowment` and
`policy_and_product_before_vsam_write`. Each names the ordinal items of
`modernization/harness/copybooks/hcapture.cpy` that witness it at run time, and `translate.py` fails when the
map, the copybook and the driver's order table disagree.

---

## 5. Build, run and output conventions

The ordered gates these commands sit in are
**Figure 5 — Validation Harness Control Flow** in [`modernization/docs/architecture.md`](../docs/architecture.md).

### 5.1 Compile recipe

`modernization/harness/run_harness.sh` is the authoritative build: it translates, compiles, executes and
publishes the evidence. Its mandated compiler options are fixed at **four**, and the option list accepts only
allow-listed additions from the environment:

```
-std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy
```

Every command is issued from the repository root, with the include directory, the output name and the source
given as repository-relative paths:

```
# 12 stubs, compiled from modernization/harness/stubs/
cobc -m -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy \
     -I modernization/harness/build/src \
     -o modernization/harness/build/bin/<PROGRAM-ID>.so \
     modernization/harness/stubs/<member>.cbl

# 3 translated programs, compiled from the generated tree
cobc -m -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy \
     -I modernization/harness/build/src \
     -o modernization/harness/build/bin/<PROGRAM-ID>.so \
     modernization/harness/build/src/<program>.cbl

# the driver, compiled as an executable
cobc -x -std=ibm -fbinary-truncate -ffold-copy=LOWER -ext cpy \
     -I modernization/harness/build/src \
     -o modernization/harness/build/bin/driver \
     modernization/harness/driver.cbl
```

Fifteen modules are produced, and **each module's output name is its `PROGRAM-ID`**, which is the name a
dynamic `CALL` of a literal resolves:

| Group | Modules |
|---|---|
| CICS stubs (5) | `CICS-ABEND`, `CICS-WRITE`, `CICS-ASKTIME`, `CICS-FORMATTIME`, `CICS-DIAG-LINK` |
| SQL stubs (7) | `SQL-INSERT-POLICY`, `SQL-INSERT-MOTOR`, `SQL-INSERT-COMMERCIAL`, `SQL-INSERT-ENDOWMENT`, `SQL-INSERT-HOUSE`, `SQL-SET-IDENTITY`, `SQL-SELECT-LASTCHANGED` |
| Translated programs (3) | `LGAPOL01`, `LGAPDB01`, `LGAPVS01` |

At run time the harness exports `COB_LIBRARY_PATH=modernization/harness/build/bin`, so the run-time resolves
`LGAPOL01` and every emulated service by module name, and `COB_LS_FIXED=1`, without which the
32,500-character post-chain record is not written in full.

The compiler is required to be the **GnuCOBOL 3 series at 3.1.2 or above**; the specification pins `3.1.2.0`.
A measured version inside the series but different from the pin is reported as a named deviation and does not
fail the run — `HARNESS_STRICT_TOOL_VERSIONS` makes any compiler difference fatal instead. Where `cobc` is
absent from a fresh checkout and `/var/lib/apt/lists/` is empty, the index refresh must precede the install:

```
DEBIAN_FRONTEND=noninteractive apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install --reinstall -y gnucobol3=3.1.2-5.1ubuntu1
```

`modernization/Makefile` carries a second, independent compile check in its `compile` target. It is not the
harness build and does not feed the evidence: its `COBFLAGS` are `-std=ibm -ffold-copy=LOWER -ext cpy`,
without `-fbinary-truncate`, and it writes modules named after their **source file** into
`modernization/harness/build/compile/`. The Makefile's `execute` target delegates to `run_harness.sh`, so the
four mandated options govern every module the chain actually runs.

### 5.2 Harness environment contract

**The driver opens no path it composed, and reads no `DD_*` variable.** `DD_SAMPLEFILE`, `DD_POSTFILE` and
`DD_CAPTFILE`, in upper case, lower case or bare form, are **not read**. Each of the driver's three files is a
descriptor its caller already opened:

| File | Direction | Bound to |
|---|---|---|
| `SAMPLEFILE` | input | standard input, through the `KEYBOARD` device |
| `POSTFILE` | output | descriptor 3, through `/dev/fd/3` |
| `CAPTFILE` | output | descriptor 4, through `/dev/fd/4` |

`run_harness.sh` opens both outputs as `exec 3>` and `exec 4>` and checks each open before running the driver.

Environment items the driver does read:

| Item | Requirement | Default |
|---|---|---|
| `HARNESS_CASE` | Required. 1–24 characters of `A`–`Z`, `0`–`9`, `-`. Emitted as the `CASE` capture | — |
| `HARNESS_FIXTURE` | Required. 1–16 characters of `a`–`z`, `0`–`9`. Emitted as the `FIXTURE` capture | — |
| `HARNESS_POLICY_NUMBER` | Identity seed, 1–9 digits above zero | `1000001` |
| `HARNESS_LASTCHANGED` | Timestamp seed, exactly 26 characters as `YYYY-MM-DD-HH.MM.SS.NNNNNN`, naming a real date and time | `2026-08-19-12.00.00.000000` |
| `COB_LS_FIXED` | Must hold a true value | set by the runner |

`HARNESS_POLICY_NUMBER` seeds the **first** case of the table; each later case takes the next consecutive
value. At the default, `01AMOT` receives **1000001** and `01ACOM` receives **1000002**. The two cases must
receive different policy numbers: both canonical relations are keyed on
`(source_system_key, policy_number)`, and equal identities would make the uniqueness assertions pass
vacuously with both samples loaded.

The runner also accepts optional per-case inputs — `HARNESS_COMMAREA_LENGTH` (0 to 32500, default 32500),
`HARNESS_REQUEST_ID`, and the four injection items `HARNESS_INJECT_POLICY_SQLCODE`,
`HARNESS_INJECT_SUBTYPE_SQLCODE`, `HARNESS_INJECT_VSAM_RESP` and `HARNESS_INJECT_VSAM_RESP2` — and per-case
expectations `HARNESS_EXPECT_RETURN_CODE`, `HARNESS_EXPECT_ABEND`, `HARNESS_EXPECT_PRODUCT`,
`HARNESS_EXPECT_POLICY_SQL`, `HARNESS_EXPECT_VSAM`, `HARNESS_EXPECT_VALUES`,
`HARNESS_EXPECT_PRODUCT_VALUES` and `HARNESS_EXPECT_DIAG_LINKS`. The driver's exit status is 0 on success and
1–7 for a return-code, abend, capture, file, environment, value or call failure respectively.

### 5.3 `captures.txt` conventions

The comparison step depends on these conventions exactly:

- One `NAME=VALUE` per line; keys **upper case**; **no spaces** around `=`.
- `PIC 9(n)` values keep their **declared width and leading zeros** — `CA_CUSTOMER_NUM=0000001001`,
  `CA_POLICY_NUM=0001000001`, `CA_PAYMENT=000500`, `CA_M_PREMIUM=000450`.
- Alphanumeric values are **right-trimmed** — `CA_BROKERSREF=BRMOT001`.
- Binary `COMP` and `COMP-5` values are **plain integers** with no padding — `EIBCALEN_AT_CALL=32500`.
- An absent value is **empty**: the key is present and nothing follows the `=`.
- The first line of every capture file is
  `STATUS_LABEL=validated against local substitute, not AWS`.

### 5.4 `commarea_post.dat`

Each case writes `build/run/<case>/commarea_post.dat` as **exactly 32,500 characters plus one trailing LF**,
32,501 bytes in total, one line. It is byte-symmetric with the generated sample record the case read, and it
is the `--commarea` input to `modernization/extraction/extract_commarea.py`.

### 5.5 Deterministic EIB values

The driver seeds the five shared EIB fields before the single call to `LGAPOL01`:

| Field | Value |
|---|---|
| `EIBCALEN` | 32500 (the value of `HARNESS_COMMAREA_LENGTH`) |
| `EIBTRNID` | `HARN` |
| `EIBTRMID` | `HTRM` |
| `EIBTASKN` | 1 |
| `EIBRESP2` | 0 |

Of these, **only `EIBCALEN` participates in business logic** — the zero-length abend test and the two length
checks. The other four are read solely into diagnostic message fields.

---

## 6. Limitations

What the harness cannot reproduce, stated plainly.

### 6.1 Emulated services, not real ones

There is **no real Db2, no VSAM dataset, no TSQ or TDQ, and no CICS transaction, task, syncpoint or rollback
semantics**. A capture proves that a stub ran with given values; it does not prove that a real Db2 insert or a
real VSAM write would have succeeded. The diagnostic link is satisfied by `CICS-DIAG-LINK`, which counts the
call and binds the area without reading it, so **nothing about the diagnostic payload is captured** and the
implementation of the linked program is never read.

The abend emulation reproduces the *control-flow* effect of an abend and not its *transactional* effect: the
caller returns immediately and no later business step runs, but no backout of the preceding policy insert
occurs. The rollback the four `LGSQ` sites exist to trigger is therefore not demonstrated.

### 6.2 Paths that exist in the generated code but are not exercised

The SQL stubs report `SQLCODE = 0` unless a case injects otherwise, and `CICS-WRITE` returns the normal
response unless a case injects otherwise. For the **two success samples `01AMOT` and `01ACOM`**, this means
the `70` path (policy insert `SQLCODE -530`), the `90` path (SQL failure) and the `LGSQ` abend paths are
present in the generated code but **not traversed**; the `80` path (VSAM response not normal) is likewise not
traversed. Those codes are reached only by the runner's injected cases.

Two paths are not exercised by any case:

- **No endowment sample is executed.** With a full 32,500-byte COMMAREA, the endowment route's
  `SUBTRACT WS-REQUIRED-CA-LEN FROM EIBCALEN GIVING WS-VARY-LEN` at `lgapdb01.cbl:339-340` computes
  `32,500 − 152 = 32,348` — the requirement being `WS-CA-HEADER-LEN +28` at `lgapdb01.cbl:65` plus
  `WS-FULL-ENDOW-LEN +124` at `lgpolicy.cpy:24`. The receiver is `WS-VARY-LEN PIC S9(4) COMP`
  [`lgapdb01.cbl:71`] and the item it then reference-modifies is `WS-VARY-CHAR PIC X(3900)`
  [`lgapdb01.cbl:72`]. Measured on a probe, the stored value is 32,348 without binary truncation and 2,348
  with it. `sql_insert_endowment.cbl` merely tolerates and ignores the padding argument when `WS-VARY-LEN` is
  zero or negative. The route is compiled and callable; no endowment behaviour is demonstrated and no
  endowment canonical value is claimed anywhere in this work.
- **The `01AHOU` route** is compiled and callable, and reached only by the runner's own route case; the two
  selected success samples are `01AMOT` and `01ACOM` alone.

### 6.3 Determinism replaces real allocation

Time is deterministic: `CICS-ASKTIME` and `CICS-FORMATTIME` return fixed harness values. The Db2 identity and
the read-back timestamp are **environment-seeded** rather than allocated by a database — the real chain lets
Db2 assign the key through `IDENTITY_VAL_LOCAL()` at `lgapdb01.cbl:307-311` and reads the timestamp back from
the row at `lgapdb01.cbl:315-321`. No conclusion about real key allocation may be drawn from a harness
identity.

### 6.4 The `EIBCALEN` surrogate and preserved truncation

`dfheiblk.cpy` declares `EIBCALEN` as `PIC S9(4) COMP-5`, a harness surrogate for a field the compiler does
not supply. The **source's own receivers are preserved exactly as declared** and still truncate:
`WS-CALEN PIC S9(4) COMP` [`lgapol01.cbl:33`; `lgapdb01.cbl:33`] and `WS-VARY-LEN PIC S9(4) COMP`
[`lgapdb01.cbl:71`]. Under the mandated `-fbinary-truncate` a binary receiver keeps only the digits its
PICTURE declares, which is faithful to `TRUNC(STD)` behaviour. The effect is confined to two places: the
`WS-CALEN` debug field, and the endowment padding arithmetic of §6.2.

### 6.5 The stale `MOTOR` length constant, as a measurement

| Measurement | Value | Locator |
|---|---:|---|
| Declared `WS-MOTOR-LEN` | +65 | `lgpolicy.cpy:21` |
| Declared `WS-FULL-MOTOR-LEN` | +137 | `lgpolicy.cpy:26` |
| Validation threshold, header + full motor | 28 + 137 = **165** | `lgapdb01.cbl:182,195` |
| Actual end of the motor overlay | **177** | `lgcmarea.cpy:65-75` |
| Shortfall | **12** | `CA-M-PREMIUM` 6 + `CA-M-ACCIDENTS` 6 |

The overlay is 77 bytes — make 15, model 15, value 6, registration 7, colour 8, CC 4, manufactured date 10,
premium 6, accidents 6 — and beginning at COMMAREA byte 101 it places `CA-M-PREMIUM` at bytes 166–171 and
`CA-M-ACCIDENTS` at 172–177, both beyond the 165-byte threshold the program checks. **The constant is not
changed**: the file is read-only. Samples are always emitted at the full 32,500-character length, and
extraction validates that the applicable amount bytes are numeric before landing.

### 6.6 Two consecutive `GOBACK` statements

**Four** `ABEND` sites are immediately followed by an `EXEC CICS RETURN` — `lgapdb01.cbl:393/394`, `431/432`,
`477/478` and `551/552` — so R8's `GOBACK` and R7's `GOBACK` land next to each other and the second is
unreachable. The count is 4, not 6: the remaining two abend sites, `lgapol01.cbl:101` and `lgapdb01.cbl:168`,
are each followed by an `END-IF`. The generated tree measures exactly four consecutive-`GOBACK` pairs, all in
`lgapdb01.cbl`, and `translate.py` records the adjacency per site and reports the total as
`abend_sites_followed_by_return` in `build/logs/translation-report.json`. GnuCOBOL may emit an
unreachable-statement warning at such a pair; the recorded build under the mandated options emitted none.
Warnings are never suppressed — they are appended to `build/logs/compile.log` and retained as evidence.

### 6.7 Encoding boundary

The local harness runs entirely in the **workstation character set**. A real z/OS extract must decode the
installation's EBCDIC CCSID instead; no byte of this harness's output carries an EBCDIC representation.

---

## 7. Rationale

**This document contains no rationale.** Every decision the harness rests on is recorded once, in
[`modernization/docs/decision-log.md`](../docs/decision-log.md), which is the single source of truth for
"why". The rows this harness depends on, named only:

| Row | Subject |
|---|---|
| D-06 | Translate read-only copies into the build tree; never preprocess a source file in place |
| D-29 | `no called RETURN stub` |
| D-30 | `called abend stub records and returns` |
| D-31 | `diagnostic-link stub in place of the linked program` |
| D-32 | `diagnostic area bound without reference` |
| D-17 | `single-superset SQL-INSERT-ENDOWMENT call` |
| D-18 | `endowment route not executed` |
| D-19 | Deterministic identity and timestamp seeding |
| D-26 | `shared EXTERNAL harness state` |
| D-27 | `shared event-sequence ordering witness and order guard` |
| D-15 | The policy insert as a hard prerequisite of every product insert |
| D-16 | One map covering `INCLUDE` and DML blocks alike |
| D-22 | Source halfword receivers preserved exactly as declared |
| D-23 | The fixed compile options, including `-fbinary-truncate` |
| D-33 | `WRITE length operands as 5-digit literals` |
| D-21 | `abend sites unexercised by the two passing samples`; `unexercised diagnostic paths` |
| D-20 | `deterministic failure injection through shared harness state` |
| D-34 | `chain traversal witnessed through the emulated services` |
| D-24 | One operating-system process per case, preserving cross-call accumulation |
| D-08 | The stale motor length constant left unchanged, samples emitted at full length |
| D-48 | Measured runtime versions accepted, each difference from a pin reported as a deviation |
| D-58 | The stable GnuCOBOL 3 series as the compiler |

Two conventions this document records carry **no row** in that log at this milestone: the `PIC S9(4) COMP-5`
declaration of the `EIBCALEN` surrogate, whose shared declaration falls under D-26 and whose truncation
semantics fall under D-22 and D-23; and the `COB_LS_FIXED` fixed-length line-sequential requirement, whose
contract is stated in `modernization/harness/driver.cbl` and `modernization/harness/run_harness.sh`.

---

## 8. Related artifacts

| Artifact | Relationship to this document |
|---|---|
| [`modernization/harness/translate.py`](translate.py) | Implements R1–R14 and enforces every site count in §4 |
| [`modernization/harness/statement_map.yml`](statement_map.yml) | Drives R2 and R13; source of §4.2 |
| [`modernization/harness/run_harness.sh`](run_harness.sh) | Implements the recipe and environment contract of §5 |
| [`modernization/harness/driver.cbl`](driver.cbl) | Supplies the file and environment contract of §5.2 and the EIB values of §5.5 |
| [`modernization/harness/copybooks/`](copybooks/) | `dfheiblk.cpy`, `dfhresp.cpy`, `hsqlca.cpy`, `hcapture.cpy` — the members R2 and R4 resolve |
| [`modernization/harness/stubs/`](stubs/) | The 12 emulated services called by R6, R8, R9, R10, R11 and R13; R7 and R12 call nothing |
| [`modernization/validation/verify_readonly.sh`](../validation/verify_readonly.sh) | Re-verifies the §1.2 baseline |
| [`modernization/docs/architecture.md`](../docs/architecture.md) | Holds **Figure 5 — Validation Harness Control Flow** |
| [`modernization/docs/decision-log.md`](../docs/decision-log.md) | The single source of truth for "why"; see §7 |
