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
      * Milestone note: the translated LGAPVS01, produced by
      * modernization/harness/translate.py, and the generated tree
      * modernization/harness/build/ are planned artifacts and are not
      * present in the tree at this milestone; every statement below
      * about the harness or about a translated program is the planned
      * contract.
      *
      * Planned usage: the translated LGAPVS01 will compare WS-RESP
      * [base/src/lgapvs01.cbl:18] against this item after the
      * KSDSPOLY write returns RESP [base/src/lgapvs01.cbl:140].
      * An equal compare continues on the normal path; an unequal
      * compare sets CA-RETURN-CODE to '80'
      * [base/src/lgapvs01.cbl:144].
      *
      * COPY DFHRESP. is to be inserted into the translated LGAPVS01
      * only. This file is to be copied verbatim into the harness
      * build tree.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      * See modernization/docs/decision-log.md (planned deliverable;
      * not present at this milestone):
      * "normal-response constant representation".
      *
      *----------------------------------------------------------------*
      * DFHRESP-NORMAL - value of the CICS NORMAL response             *
      * condition, to be compared against WS-RESP by the translated    *
      * LGAPVS01 response test.                                        *
      *----------------------------------------------------------------*
       01  DFHRESP-NORMAL            PIC S9(8) COMP VALUE +0.
