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
      * Usage: the translated LGAPVS01 compares WS-RESP
      * [base/src/lgapvs01.cbl:18] against this item after the
      * KSDSPOLY write returns RESP [base/src/lgapvs01.cbl:140].
      * An equal compare continues on the normal path; an unequal
      * compare sets CA-RETURN-CODE to '80'
      * [base/src/lgapvs01.cbl:144].
      *
      * COPY DFHRESP. is inserted into the translated LGAPVS01 only.
      * This file is copied verbatim into the harness build tree.
      *
      * Harness topology: Figure 5 "Validation Harness Control Flow"
      * in modernization/docs/architecture.md.
      *
      * See modernization/docs/decision-log.md:
      * "normal-response constant representation".
      *
      *----------------------------------------------------------------*
      * DFHRESP-NORMAL - value of the CICS NORMAL response             *
      * condition, compared against WS-RESP by the translated          *
      * LGAPVS01 response test.                                        *
      *----------------------------------------------------------------*
       01  DFHRESP-NORMAL            PIC S9(8) COMP VALUE +0.
