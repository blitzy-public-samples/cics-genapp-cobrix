      ******************************************************************
      *                                                                *
      *                    CICS-ASKTIME                                *
      *                                                                *
      * Deterministic ASKTIME service for the GnuCOBOL validation      *
      * harness.                                                       *
      *                                                                *
      ******************************************************************
      *
      * Stands in for EXEC CICS ASKTIME. Returns the fixed harness
      * abstime in its single parameter and does nothing else.
      *
      * Source construct : EXEC CICS ASKTIME ABSTIME(ABS-TIME)
      *                    base/src/lgapol01.cbl:140
      *                    EXEC CICS ASKTIME ABSTIME(ABS-TIME)
      *                    base/src/lgapdb01.cbl:566
      *                    EXEC CICS ASKTIME ABSTIME(WS-ABSTIME)
      *                    base/src/lgapvs01.cbl:156
      * Target statement : CALL 'CICS-ASKTIME' USING ABS-TIME in the
      *                    translated LGAPOL01 and LGAPDB01, and
      *                    CALL 'CICS-ASKTIME' USING WS-ABSTIME in
      *                    the translated LGAPVS01
      * Target items     : HARNESS-ABSTIME, LK-ABSTIME
      * Related locators : base/src/lgapol01.cbl:36 and
      *                    base/src/lgapdb01.cbl:36, the ABS-TIME
      *                    items PIC S9(8) COMP that receive the
      *                    value, and base/src/lgapvs01.cbl:54, the
      *                    WS-ABSTIME item of the same shape;
      *                    base/src/lgapol01.cbl:142-145,
      *                    base/src/lgapdb01.cbl:568-571 and
      *                    base/src/lgapvs01.cbl:158-161, the
      *                    FORMATTIME blocks that consume the value;
      *                    base/src/lgapol01.cbl:137,
      *                    base/src/lgapdb01.cbl:562 and
      *                    base/src/lgapvs01.cbl:155, the
      *                    WRITE-ERROR-MESSAGE paragraphs that hold
      *                    all three sites
      *
      * Milestone note: modernization/harness/translate.py,
      * modernization/harness/driver.cbl,
      * modernization/harness/run_harness.sh,
      * modernization/harness/translation-rules.md, the other eleven
      * members of modernization/harness/stubs/, the generated tree
      * modernization/harness/build/,
      * modernization/validation/diff_harness_vs_warehouse.py,
      * modernization/docs/decision-log.md and
      * modernization/docs/traceability-matrix.md are planned
      * artifacts and are not present in the tree at this milestone;
      * every statement below about the harness or about a translated
      * program is the planned contract.
      *
      * modernization/harness/run_harness.sh is to compile this file
      * as a callable module with cobc -m -std=ibm -ffold-copy=LOWER
      * -ext cpy -I build/src -o build/bin/CICS-ASKTIME.so. The module
      * basename equals the PROGRAM-ID, which is the name the dynamic
      * CALL resolves.
      *
      * Each translated program is to call this module where its
      * source issues ASKTIME, then pass the returned item unchanged
      * to CICS-FORMATTIME. Every one of the three sites sits inside a
      * WRITE-ERROR-MESSAGE paragraph. A case that returns '00' loads
      * this module and never calls it.
      *
      * The value returned is a fixed constant. No clock, calendar,
      * environment variable or system service is read. Repeated runs
      * of one sample return the identical value.
      *
      * The parameter is the whole interface. The shared capture group
      * copied below declares no time-service item. This module
      * records nothing in that group and leaves every field to its
      * owner.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      * See modernization/docs/decision-log.md (planned deliverable;
      * not present at this milestone): "deterministic harness time
      * data" and "unexercised diagnostic paths".
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CICS-ASKTIME.
      *
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      *----------------------------------------------------------------*
      * HC-CAPTURE-STATE - shared harness capture group.               *
      *----------------------------------------------------------------*
      * Copied by modernization/harness/driver.cbl and by every member
      * of modernization/harness/stubs/. The group is EXTERNAL and
      * carries no VALUE clause. No item of it is read, written or
      * initialised here.
           COPY HCAPTURE.
      *
      *----------------------------------------------------------------*
      * HARNESS-ABSTIME - fixed instant reported by this module.       *
      *----------------------------------------------------------------*
      * The instant is 2026-08-19 12:00:00, carried as the digits
      * 20260819 of that date.
      * modernization/harness/stubs/cics_formattime.cbl is to render
      * this same value as MMDDYYYY '08/19/2026' and TIME '12:00:00',
      * and modernization/harness/stubs/sql_insert_policy.cbl is to
      * report the same instant as the LASTCHANGED timestamp
      * 2026-08-19-12.00.00.000000.
      * The real CICS abstime encoding is not reproduced. Each of the
      * three sites passes the value to FORMATTIME unchanged. No
      * statement of the three source programs performs arithmetic
      * on it.
      * Shape follows the receiving items ABS-TIME
      * [base/src/lgapol01.cbl:36], ABS-TIME
      * [base/src/lgapdb01.cbl:36] and WS-ABSTIME
      * [base/src/lgapvs01.cbl:54].
       01  HARNESS-ABSTIME             PIC S9(8) COMP VALUE +20260819.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
       LINKAGE SECTION.
      *
      *----------------------------------------------------------------*
      * LK-ABSTIME - the ABSTIME operand of the calling site.          *
      *----------------------------------------------------------------*
      * The single parameter of this module, passed by reference and
      * set on every call. Same shape as the three items named above.
       01  LK-ABSTIME                  PIC S9(8) COMP.
      *
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION USING LK-ABSTIME.
      *
      *----------------------------------------------------------------*
      * MAINLINE - reports the fixed instant and returns.              *
      *----------------------------------------------------------------*
       MAINLINE.
           MOVE HARNESS-ABSTIME TO LK-ABSTIME
           GOBACK.
      *----------------------------------------------------------------*
