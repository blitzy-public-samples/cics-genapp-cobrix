      ******************************************************************
      *                                                                *
      *                        CICS-FORMATTIME                         *
      *                                                                *
      * Deterministic FORMATTIME service for the GnuCOBOL validation   *
      * harness.                                                       *
      *                                                                *
      ******************************************************************
      *
      * Stands in for EXEC CICS FORMATTIME. Renders the date the
      * abstime it receives names, and the fixed harness time of day,
      * into the two character receivers its caller supplies and does
      * nothing else.
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
      * Target items     : HARNESS-FALLBACK-DATE, HARNESS-TIME,
      *                    WS-ABSTIME-DIGITS, WS-ABS-YEAR,
      *                    WS-ABS-MONTH, WS-ABS-DAY, WS-RENDERED-DATE,
      *                    LK-ABSTIME, LK-MMDDYYYY, LK-TIME
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
      * Harness status: modernization/harness/driver.cbl,
      * modernization/harness/run_harness.sh and the other eleven
      * members of modernization/harness/stubs/ stand in the tree, and
      * every run of the harness regenerates the tree
      * modernization/harness/build/.
      * modernization/harness/translation-rules.md,
      * modernization/validation/diff_harness_vs_warehouse.py,
      * modernization/docs/decision-log.md and
      * modernization/docs/traceability-matrix.md are planned artifacts
      * and are not present in the tree.
      *
      * modernization/harness/run_harness.sh compiles this file as a
      * callable module with cobc -m -std=ibm -fbinary-truncate
      * -ffold-copy=LOWER -ext cpy -I build/src
      * -o build/bin/CICS-FORMATTIME.so. The module
      * basename equals the PROGRAM-ID, which is the name the dynamic
      * CALL resolves.
      *
      * Each translated program calls this module where its source
      * issues FORMATTIME, passing the abstime item its own ASKTIME site
      * filled. Every one of the three sites sits inside a
      * WRITE-ERROR-MESSAGE paragraph. A case that returns '00' loads
      * this module and never calls it.
      *
      * The three parameters are the whole interface. LK-ABSTIME is
      * input and is read on every call. LK-MMDDYYYY and LK-TIME are
      * output and are filled on every call.
      *
      * The date rendered into LK-MMDDYYYY is the date LK-ABSTIME
      * names. modernization/harness/stubs/cics_asktime.cbl carries the
      * harness abstime surrogate as the eight digits YYYYMMDD of the
      * instant it reports. This module moves the received value into
      * an eight-digit item, reads its year, month and day halves and
      * lays them out as MM/DD/YYYY. The harness abstime 20260819
      * renders '08/19/2026', and an abstime naming another date
      * renders that date: the ASKTIME site of the calling paragraph
      * supplies the value this module reports.
      *
      * A received value that cannot name a date is rendered as the
      * documented fallback date '08/19/2026', and the run log receives
      * a report of the value and of the substitution. That covers the
      * +0 that base/src/lgapol01.cbl:36, base/src/lgapdb01.cbl:36 and
      * base/src/lgapvs01.cbl:54 declare, a negative value, a month
      * outside 01 through 12 and a day outside 01 through 31. The
      * range test reaches no further than the MM/DD/YYYY layout: a
      * month of 01 through 12 carrying a day of 01 through 31 is
      * rendered as received, so an abstime naming 20260231 renders
      * '02/31/2026' rather than the fallback date.
      *
      * The time of day rendered into LK-TIME is fixed at '12:00:00'.
      * The abstime surrogate carries a date and no time component, and
      * no parameter of this module supplies a time of day. The two
      * stubs carry the same instant in seeds of their own: the
      * surrogate 20260819 in
      * modernization/harness/stubs/cics_asktime.cbl and the time of
      * day here. modernization/harness/stubs/sql_insert_policy.cbl
      * reports that same instant as the LASTCHANGED timestamp
      * 2026-08-19-12.00.00.000000.
      *
      * No clock, calendar, environment variable or system service is
      * read, no arithmetic is performed on the abstime and the real
      * CICS abstime encoding is not reproduced. Repeated runs of one
      * sample return identical values.
      *
      * The receivers are filled to their full declared width, all ten
      * and all eight characters. The MOVEs
      * at base/src/lgapol01.cbl:146-147,
      * base/src/lgapdb01.cbl:572-573 and
      * base/src/lgapvs01.cbl:163-164 shorten them into EM-DATE
      * PIC X(8) and EM-TIME PIC X(6); that shortening stays in the
      * calling program, so a rendered date reaches the diagnostic as
      * its first eight characters and a rendered time as its first
      * six.
      *
      * The shared capture group copied below declares no time-service
      * item. This module records nothing in that group and leaves every
      * field to its owner. It carries no prerequisite ordinal.
      * HC-ORDER-VIOLATION and HC-ORDER-VIOLATION-STMT are neither read
      * nor written here.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      * See modernization/docs/decision-log.md: "deterministic harness
      * time data", "FORMATTIME rendered from the ASKTIME surrogate",
      * "uniform stub-side capture-order guard" and "unexercised
      * diagnostic paths".
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
      * HARNESS-FALLBACK-DATE - date rendered for an abstime that      *
      * cannot name one.                                               *
      *----------------------------------------------------------------*
      * The MMDDYYYY form of the harness instant 2026-08-19 12:00:00,
      * ten characters wide, which is also the form the harness abstime
      * surrogate 20260819 renders through WS-DATE-OUT below. Shape
      * follows the receiving items DATE1
      * [base/src/lgapol01.cbl:38], DATE1 [base/src/lgapdb01.cbl:38]
      * and WS-DATE [base/src/lgapvs01.cbl:56].
       01  HARNESS-FALLBACK-DATE       PIC X(10) VALUE '08/19/2026'.
      *
      *----------------------------------------------------------------*
      * HARNESS-TIME - fixed time of day rendered by this module.      *
      *----------------------------------------------------------------*
      * The TIME form of that same instant, eight characters wide. The
      * abstime surrogate carries no time component; this value is
      * seeded here and is derived from no parameter.
      * Shape follows the receiving items TIME1
      * [base/src/lgapol01.cbl:37], TIME1 [base/src/lgapdb01.cbl:37]
      * and WS-TIME [base/src/lgapvs01.cbl:55].
       01  HARNESS-TIME                PIC X(8)  VALUE '12:00:00'.
      *
      *----------------------------------------------------------------*
      * WS-ABSTIME-DIGITS - the received abstime read as YYYYMMDD.     *
      *----------------------------------------------------------------*
      * Receives LK-ABSTIME on the path that renders it. The
      * redefinition reads the same eight digits as the year, month and
      * day they spell, and is addressed only after the value has been
      * found positive. modernization/harness/stubs/cics_asktime.cbl
      * declares the shape of the surrogate this item decomposes.
       01  WS-ABSTIME-DIGITS           PIC 9(8).
      *
       01  WS-ABSTIME-PARTS REDEFINES WS-ABSTIME-DIGITS.
           03 WS-ABS-YEAR              PIC 9(4).
           03 WS-ABS-MONTH             PIC 9(2).
           03 WS-ABS-DAY               PIC 9(2).
      *
      *----------------------------------------------------------------*
      * WS-DATE-OUT - the MM/DD/YYYY layout this module renders.       *
      *----------------------------------------------------------------*
      * Ten characters in the order and with the separators the
      * MMDDYYYY operand of the emulated command carries. The three
      * numeric items receive the halves of WS-ABSTIME-PARTS above and
      * the two separators are fixed.
       01  WS-DATE-OUT.
           03 WS-OUT-MONTH             PIC 9(2).
           03 FILLER                   PIC X     VALUE '/'.
           03 WS-OUT-DAY               PIC 9(2).
           03 FILLER                   PIC X     VALUE '/'.
           03 WS-OUT-YEAR              PIC 9(4).
      *
      *----------------------------------------------------------------*
      * WS-RENDERED-DATE - the date handed to the caller.              *
      *----------------------------------------------------------------*
      * Holds WS-DATE-OUT on the rendered path and
      * HARNESS-FALLBACK-DATE on the reported one. Same shape as the
      * receiving parameter.
       01  WS-RENDERED-DATE            PIC X(10).
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
      * from modernization/harness/stubs/cics_asktime.cbl. It is read
      * on every call, to render the date, and is never written here.
      * Shape follows ABS-TIME
      * [base/src/lgapol01.cbl:36], ABS-TIME
      * [base/src/lgapdb01.cbl:36] and WS-ABSTIME
      * [base/src/lgapvs01.cbl:54].
       01  LK-ABSTIME                  PIC S9(8) COMP.
      *
      *----------------------------------------------------------------*
      * LK-MMDDYYYY - the MMDDYYYY operand of the calling site.        *
      *----------------------------------------------------------------*
      * Second parameter, output. Receives all ten characters of
      * WS-RENDERED-DATE on every call.
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
      * MAINLINE - renders the date and the time and returns.          *
      *----------------------------------------------------------------*
      * Fills both receivers and returns control to the caller. The
      * calling program performs any shortening of its own.
       MAINLINE.
           PERFORM RENDER-DATE-FROM-ABSTIME
           MOVE WS-RENDERED-DATE TO LK-MMDDYYYY
           MOVE HARNESS-TIME     TO LK-TIME
           GOBACK.
      *
      *----------------------------------------------------------------*
      * RENDER-DATE-FROM-ABSTIME - lays the received abstime out as    *
      * MM/DD/YYYY, or reports it and renders the fallback date.       *
      *----------------------------------------------------------------*
      * The eight digits of a positive abstime are read as YYYYMMDD, a
      * month of 01 through 12 and a day of 01 through 31 are laid out
      * as MM/DD/YYYY, and every other value is reported and replaced.
      * WS-ABSTIME-PARTS is addressed only inside the positive branch,
      * so no negative value is read as digits.
       RENDER-DATE-FROM-ABSTIME.
           IF LK-ABSTIME IS GREATER THAN ZERO
               MOVE LK-ABSTIME TO WS-ABSTIME-DIGITS
               IF WS-ABS-MONTH IS NOT LESS THAN 1
                   AND WS-ABS-MONTH IS NOT GREATER THAN 12
                   AND WS-ABS-DAY IS NOT LESS THAN 1
                   AND WS-ABS-DAY IS NOT GREATER THAN 31
                   MOVE WS-ABS-MONTH TO WS-OUT-MONTH
                   MOVE WS-ABS-DAY   TO WS-OUT-DAY
                   MOVE WS-ABS-YEAR  TO WS-OUT-YEAR
                   MOVE WS-DATE-OUT  TO WS-RENDERED-DATE
               ELSE
                   PERFORM REPORT-UNRENDERABLE-ABSTIME
               END-IF
           ELSE
               PERFORM REPORT-UNRENDERABLE-ABSTIME
           END-IF.
      *
      *----------------------------------------------------------------*
      * REPORT-UNRENDERABLE-ABSTIME - names the value on the run log   *
      * and renders the documented fallback date.                      *
      *----------------------------------------------------------------*
      * Reached for an abstime of zero or below and for one whose month
      * or day falls outside the MM/DD/YYYY layout. The value received
      * is left as the caller holds it and the fallback is named in the
      * report, so a substituted date stands in the log of the case.
       REPORT-UNRENDERABLE-ABSTIME.
           MOVE HARNESS-FALLBACK-DATE TO WS-RENDERED-DATE
           DISPLAY 'CICS-FORMATTIME: ABSTIME ' LK-ABSTIME
                   ' NAMES NO DATE AS YYYYMMDD'
                   ' - RENDERING THE FALLBACK '
                   HARNESS-FALLBACK-DATE
           END-DISPLAY.
      *----------------------------------------------------------------*
