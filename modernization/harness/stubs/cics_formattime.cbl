      ******************************************************************
      *                                                                *
      *                        CICS-FORMATTIME                         *
      *                                                                *
      * Deterministic FORMATTIME service for the GnuCOBOL validation   *
      * harness.                                                       *
      *                                                                *
      ******************************************************************
      *
      * Stands in for EXEC CICS FORMATTIME. Renders the fixed harness
      * instant into the two character receivers its caller supplies and
      * does nothing else.
      *
      * Source construct : EXEC CICS FORMATTIME ABSTIME(ABS-TIME)
      *                    MMDDYYYY(DATE1) TIME(TIME1)
      *                    base/src/lgapol01.cbl:142-145
      *                    EXEC CICS FORMATTIME ABSTIME(ABS-TIME)
      *                    MMDDYYYY(DATE1) TIME(TIME1)
      *                    base/src/lgapdb01.cbl:568-571
      *                    EXEC CICS FORMATTIME ABSTIME(WS-ABSTIME)
      *                    MMDDYYYY(WS-DATE) TIME(WS-TIME)
      *                    base/src/lgapvs01.cbl:158-161
      * Target statement : CALL 'CICS-FORMATTIME' USING ABS-TIME DATE1
      *                    TIME1 in the translated LGAPOL01 and
      *                    LGAPDB01, and CALL 'CICS-FORMATTIME' USING
      *                    WS-ABSTIME WS-DATE WS-TIME in the translated
      *                    LGAPVS01
      * Target items     : HARNESS-MMDDYYYY, HARNESS-TIME, LK-ABSTIME,
      *                    LK-MMDDYYYY, LK-TIME
      * Related locators : base/src/lgapol01.cbl:36-38 and
      *                    base/src/lgapdb01.cbl:36-38, the ABS-TIME
      *                    PIC S9(8) COMP, TIME1 PIC X(8) and DATE1
      *                    PIC X(10) items of the calling sites, and
      *                    base/src/lgapvs01.cbl:54-56, the WS-ABSTIME,
      *                    WS-TIME and WS-DATE items of those same three
      *                    shapes; base/src/lgapol01.cbl:140,
      *                    base/src/lgapdb01.cbl:566 and
      *                    base/src/lgapvs01.cbl:156, the ASKTIME sites
      *                    that fill the abstime passed here;
      *                    base/src/lgapol01.cbl:146-147,
      *                    base/src/lgapdb01.cbl:572-573 and
      *                    base/src/lgapvs01.cbl:163-164, the MOVEs that
      *                    shorten these receivers into EM-DATE PIC X(8)
      *                    and EM-TIME PIC X(6);
      *                    base/src/lgapol01.cbl:137,
      *                    base/src/lgapdb01.cbl:562 and
      *                    base/src/lgapvs01.cbl:155, the
      *                    WRITE-ERROR-MESSAGE paragraphs that hold all
      *                    three sites
      *
      * Milestone note: modernization/harness/driver.cbl,
      * modernization/harness/run_harness.sh,
      * modernization/harness/translation-rules.md, eight of the other
      * eleven members of modernization/harness/stubs/, the generated
      * tree modernization/harness/build/,
      * modernization/validation/diff_harness_vs_warehouse.py,
      * modernization/docs/decision-log.md and
      * modernization/docs/traceability-matrix.md are planned artifacts
      * and are not present in the tree at this milestone; every
      * statement below about the harness or about a translated program
      * is the planned contract.
      *
      * modernization/harness/run_harness.sh is to compile this file as
      * a callable module with cobc -m -std=ibm -ffold-copy=LOWER -ext
      * cpy -I build/src -o build/bin/CICS-FORMATTIME.so. The module
      * basename equals the PROGRAM-ID, which is the name the dynamic
      * CALL resolves.
      *
      * Each translated program is to call this module where its source
      * issues FORMATTIME, passing the abstime item its own ASKTIME site
      * filled. Every one of the three sites sits inside a
      * WRITE-ERROR-MESSAGE paragraph. A case that returns '00' loads
      * this module and never calls it.
      *
      * The three parameters are the whole interface. LK-ABSTIME is
      * input and is neither read nor written here. LK-MMDDYYYY and
      * LK-TIME are output and are filled on every call.
      *
      * The instant reported is fixed: MMDDYYYY '08/19/2026' and TIME
      * '12:00:00', filling all ten and all eight characters. No clock,
      * calendar, environment variable or system service is read. No
      * arithmetic is performed on the abstime and the real CICS abstime
      * encoding is not reproduced. Every abstime value yields these
      * same two strings, including the +0 that
      * base/src/lgapol01.cbl:36, base/src/lgapdb01.cbl:36 and
      * base/src/lgapvs01.cbl:54 declare. Repeated runs of one sample
      * return identical values.
      *
      * modernization/harness/stubs/cics_asktime.cbl reports the same
      * instant as the abstime digits 20260819, and
      * modernization/harness/stubs/sql_insert_policy.cbl reports it as
      * the LASTCHANGED timestamp 2026-08-19-12.00.00.000000.
      *
      * The receivers are filled to their full declared width. The MOVEs
      * at base/src/lgapol01.cbl:146-147,
      * base/src/lgapdb01.cbl:572-573 and
      * base/src/lgapvs01.cbl:163-164 shorten them into EM-DATE
      * PIC X(8) and EM-TIME PIC X(6); that shortening stays in the
      * calling program.
      *
      * The shared capture group copied below declares no time-service
      * item. This module records nothing in that group and leaves every
      * field to its owner.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      * See modernization/docs/decision-log.md (planned deliverable; not
      * present at this milestone): "deterministic harness time data"
      * and "unexercised diagnostic paths".
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CICS-FORMATTIME.
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
      * HARNESS-MMDDYYYY - fixed date rendered by this module.         *
      *----------------------------------------------------------------*
      * The MMDDYYYY form of the harness instant 2026-08-19 12:00:00,
      * ten characters wide. Shape follows the receiving items DATE1
      * [base/src/lgapol01.cbl:38], DATE1 [base/src/lgapdb01.cbl:38]
      * and WS-DATE [base/src/lgapvs01.cbl:56].
       01  HARNESS-MMDDYYYY            PIC X(10) VALUE '08/19/2026'.
      *
      *----------------------------------------------------------------*
      * HARNESS-TIME - fixed time of day rendered by this module.      *
      *----------------------------------------------------------------*
      * The TIME form of that same instant, eight characters wide.
      * Shape follows the receiving items TIME1
      * [base/src/lgapol01.cbl:37], TIME1 [base/src/lgapdb01.cbl:37]
      * and WS-TIME [base/src/lgapvs01.cbl:55].
       01  HARNESS-TIME                PIC X(8)  VALUE '12:00:00'.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
       LINKAGE SECTION.
      *
      *----------------------------------------------------------------*
      * LK-ABSTIME - the ABSTIME operand of the calling site.          *
      *----------------------------------------------------------------*
      * First parameter, input. Holds the value the calling site took
      * from modernization/harness/stubs/cics_asktime.cbl. It is not
      * read and not written here. Shape follows ABS-TIME
      * [base/src/lgapol01.cbl:36], ABS-TIME
      * [base/src/lgapdb01.cbl:36] and WS-ABSTIME
      * [base/src/lgapvs01.cbl:54].
       01  LK-ABSTIME                  PIC S9(8) COMP.
      *
      *----------------------------------------------------------------*
      * LK-MMDDYYYY - the MMDDYYYY operand of the calling site.        *
      *----------------------------------------------------------------*
      * Second parameter, output. Receives all ten characters of
      * HARNESS-MMDDYYYY on every call.
       01  LK-MMDDYYYY                 PIC X(10).
      *
      *----------------------------------------------------------------*
      * LK-TIME - the TIME operand of the calling site.                *
      *----------------------------------------------------------------*
      * Third parameter, output. Receives all eight characters of
      * HARNESS-TIME on every call.
       01  LK-TIME                     PIC X(8).
      *
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION USING LK-ABSTIME, LK-MMDDYYYY, LK-TIME.
      *
      *----------------------------------------------------------------*
      * MAINLINE - renders the fixed instant and returns.              *
      *----------------------------------------------------------------*
      * Fills both receivers and returns control to the caller. The
      * calling program performs any shortening of its own.
       MAINLINE.
           MOVE HARNESS-MMDDYYYY TO LK-MMDDYYYY
           MOVE HARNESS-TIME     TO LK-TIME
           GOBACK.
      *----------------------------------------------------------------*
