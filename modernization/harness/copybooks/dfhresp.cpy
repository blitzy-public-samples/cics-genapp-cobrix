      ******************************************************************
      *                                                                *
      *                    DFHRESP                                     *
      *                                                                *
      * Named CICS response-condition constant for the GnuCOBOL        *
      * validation harness.                                            *
      *                                                                *
      ******************************************************************
      *
      * Stands in for the CICS translator macro DFHRESP(NORMAL).
      *
      * Source construct : DFHRESP(NORMAL)
      *                    base/src/lgapvs01.cbl:142
      * Target item      : DFHRESP-NORMAL
      *
      * Harness status: modernization/harness/translate.py stands in
      * the tree, and every run of the harness regenerates the tree
      * modernization/harness/build/ with the translated LGAPVS01 in
      * it; every statement below about the harness or about a
      * translated program describes the delivered contract.
      *
      * Usage: the translated LGAPVS01 compares WS-RESP
      * [base/src/lgapvs01.cbl:18] against this item after the
      * KSDSPOLY write returns RESP [base/src/lgapvs01.cbl:140].
      * An equal compare continues on the normal path; an unequal
      * compare sets CA-RETURN-CODE to '80'
      * [base/src/lgapvs01.cbl:144].
      *
      * modernization/harness/translate.py inserts COPY DFHRESP. into
      * the translated LGAPVS01 only, and copies this file verbatim
      * into the harness build tree.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      * See modernization/docs/decision-log.md, row D-77:
      * normal-response constant representation.
      *
      *----------------------------------------------------------------*
      * DFHRESP-NORMAL - value of the CICS NORMAL response             *
      * condition, compared against WS-RESP by the translated          *
      * LGAPVS01 response test.                                        *
      *----------------------------------------------------------------*
       01  DFHRESP-NORMAL            PIC S9(8) COMP VALUE +0.
