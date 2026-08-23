      ******************************************************************
      *                                                                *
      *                         CICS-DIAG-LINK                         *
      *                                                                *
      *           Diagnostic-link absorber for the GnuCOBOL            *
      *                       validation harness                       *
      *                                                                *
      ******************************************************************
      *
      * Stands in for the diagnostic EXEC CICS LINK of the three
      * translated programs. Accepts the diagnostic area and its
      * length, counts the call in the shared capture group and
      * returns. The area content is never referenced.
      *
      * Source construct : EXEC CICS LINK PROGRAM('LGSTSQ')
      *                    nine sites, three in each program:
      *                    base/src/lgapol01.cbl:149
      *                    base/src/lgapol01.cbl:157
      *                    base/src/lgapol01.cbl:163
      *                    base/src/lgapdb01.cbl:575
      *                    base/src/lgapdb01.cbl:583
      *                    base/src/lgapdb01.cbl:589
      *                    base/src/lgapvs01.cbl:169
      *                    base/src/lgapvs01.cbl:176
      *                    base/src/lgapvs01.cbl:182
      * Target statement : MOVE LENGTH OF <area> TO HARNESS-DIAG-LEN
      *                    followed by CALL 'CICS-DIAG-LINK' USING
      *                    <area> HARNESS-DIAG-LEN, emitted by rule
      *                    R6 of modernization/harness/translate.py
      * Target items     : HC-DIAG-LINK-COUNT, LK-DIAG-AREA,
      *                    LK-DIAG-LEN
      * Related locators : the COMMAREA operand is ERROR-MSG at
      *                    base/src/lgapol01.cbl:149,
      *                    base/src/lgapdb01.cbl:575 and
      *                    base/src/lgapvs01.cbl:169, and
      *                    CA-ERROR-MSG at the other six sites; the
      *                    ERROR-MSG declarations are
      *                    base/src/lgapol01.cbl:41-46,
      *                    base/src/lgapdb01.cbl:41-53 and
      *                    base/src/lgapvs01.cbl:58-73; the
      *                    CA-ERROR-MSG declarations are
      *                    base/src/lgapol01.cbl:48-50,
      *                    base/src/lgapdb01.cbl:55-57 and
      *                    base/src/lgapvs01.cbl:75-77; the holding
      *                    paragraphs are WRITE-ERROR-MESSAGE at
      *                    base/src/lgapol01.cbl:137,
      *                    base/src/lgapdb01.cbl:562 and
      *                    base/src/lgapvs01.cbl:155
      *
      * Harness status: modernization/harness/driver.cbl,
      * modernization/harness/run_harness.sh and the remaining members
      * of modernization/harness/stubs/ stand in the tree, and every
      * run of the harness regenerates the tree
      * modernization/harness/build/.
      * modernization/harness/translation-rules.md,
      * modernization/validation/diff_harness_vs_warehouse.py,
      * modernization/docs/decision-log.md and
      * modernization/docs/traceability-matrix.md all stand in the
      * tree.
      *
      * modernization/harness/run_harness.sh compiles this file as a
      * callable module with cobc -m -std=ibm -fbinary-truncate
      * -ffold-copy=LOWER -ext cpy -I build/src
      * -o build/bin/CICS-DIAG-LINK.so. The
      * module basename equals the PROGRAM-ID, which is the name the
      * dynamic CALL resolves.
      *
      * The nine sites supply four area lengths: 45 bytes at
      * base/src/lgapol01.cbl:149, 87 bytes at
      * base/src/lgapdb01.cbl:575, 101 bytes at
      * base/src/lgapvs01.cbl:169, and 99 bytes at each of the six
      * CA-ERROR-MSG sites.
      *
      * This module binds the area as a one-byte item. It never
      * reads, moves, displays or reference-modifies that item, and it
      * never assigns to it.
      *
      * This module performs no output. It writes no queue, no file
      * and no terminal, and it displays nothing. It reads no clock,
      * calendar, environment variable or system service.
      *
      * Every one of the nine sites sits inside the error paragraph
      * named above. A case that returns '00' loads this module and
      * never calls it, leaving the counter at the value
      * modernization/harness/driver.cbl set.
      *
      * Order guard: this module carries no prerequisite. The nine
      * sites belong to the diagnostic paragraph of each program. The
      * counter this module keeps carries no ordering, and neither
      * HC-ORDER-VIOLATION nor HC-ORDER-VIOLATION-STMT is read or
      * written here: the order verdict of the case stays exactly as
      * the capturing stubs left it. The eight stubs whose sites carry
      * an ordering constraint of that source test it themselves.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      * See modernization/docs/decision-log.md, rows: diagnostic-link
      * stub in place of the linked program; diagnostic area bound
      * without reference; uniform stub-side capture-order guard;
      * unexercised diagnostic paths.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CICS-DIAG-LINK.
      *
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      *----------------------------------------------------------------*
      * HC-CAPTURE-STATE - shared harness capture group.               *
      *----------------------------------------------------------------*
      * Copied by modernization/harness/driver.cbl and by every member
      * of modernization/harness/stubs/. The group is EXTERNAL and
      * carries no VALUE clause. This module adds 1 to
      * HC-DIAG-LINK-COUNT, declared at
      * modernization/harness/copybooks/hcapture.cpy:1019, and reads,
      * writes or initialises no other item of the group. It performs
      * no INITIALIZE and never zeroes the counter. The values
      * modernization/harness/driver.cbl set before the case, and the
      * captures other members recorded in the same run unit, are
      * unchanged by this module.
           COPY HCAPTURE.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
       LINKAGE SECTION.
      *
      *----------------------------------------------------------------*
      * LK-DIAG-AREA - the COMMAREA operand of the site.               *
      *----------------------------------------------------------------*
      * Parameter 1, bound and never referenced. Holds the address of
      * the diagnostic area the site supplies: ERROR-MSG at three
      * sites and CA-ERROR-MSG at six, of 45, 87, 99 or 101 bytes as
      * listed above. Declared as one byte and passed by reference. No
      * statement of this module reads it, assigns to it, moves it,
      * displays it or applies reference modification to it.
       01  LK-DIAG-AREA                PIC X(1).
      *
      *----------------------------------------------------------------*
      * LK-DIAG-LEN - the LENGTH operand of the site.                  *
      *----------------------------------------------------------------*
      * Parameter 2, bound and never referenced. Receives
      * HARNESS-DIAG-LEN, the item rule R6 of
      * modernization/harness/translate.py declares as PIC S9(8) COMP
      * and loads from the LENGTH(LENGTH OF ...) operand of the site.
      * Same shape as that item. The shared capture group declares no
      * diagnostic-link length item, and this module records no
      * length. It performs no validation of the value, does not use
      * it to address LK-DIAG-AREA and compares it with nothing.
       01  LK-DIAG-LEN                 PIC S9(8) COMP.
      *
      *----------------------------------------------------------------*
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION USING LK-DIAG-AREA, LK-DIAG-LEN.
      *
      *----------------------------------------------------------------*
      * MAINLINE - counts the call and returns.                        *
      *----------------------------------------------------------------*
      * Counts this call in the shared capture group.
      * modernization/harness/driver.cbl emits the counter as the
      * DIAG_LINK_COUNT key of build/run/<case>/captures.txt. A case
      * that returns '00' reaches no site and reports zero.
       MAINLINE.
           ADD 1 TO HC-DIAG-LINK-COUNT
           END-ADD
           GOBACK.
      *----------------------------------------------------------------*
