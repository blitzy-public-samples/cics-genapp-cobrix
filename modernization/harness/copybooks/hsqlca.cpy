      ******************************************************************
      *                                                                *
      *                    HSQLCA                                      *
      *                                                                *
      * SQL communications area for the GnuCOBOL validation harness.   *
      *                                                                *
      ******************************************************************
      *
      * Stands in for the DB2 SQLCA that the z/OS precompiler supplies
      * to base/src/lgapdb01.cbl, which is compiled there under the
      * PROCESS SQL directive [base/src/lgapdb01.cbl:1].
      *
      * Source construct : EXEC SQL INCLUDE SQLCA
      *                    base/src/lgapdb01.cbl:124-126
      * Target statement : COPY HSQLCA.
      *                    modernization/harness/statement_map.yml,
      *                    includes entry include_sqlca
      * Target items     : SQLCA, SQLCODE
      * Related locators : base/src/lgapdb01.cbl:83-86, the DB2 to
      *                    COBOL type mapping the program records;
      *                    base/src/lgapdb01.cbl:53, the EM-SQLRC
      *                    field that receives SQLCODE at line 564
      *
      * Harness status: modernization/harness/translate.py,
      * modernization/harness/driver.cbl and the stub members under
      * modernization/harness/stubs/ stand in the tree, and every run
      * of the harness regenerates the tree
      * modernization/harness/build/; every statement below about the
      * harness or about a translated program describes the delivered
      * contract.
      *
      * translate.py inserts COPY HSQLCA. into the translated LGAPDB01
      * only. base/src/lgapol01.cbl and base/src/lgapvs01.cbl contain
      * no SQL statement and do not copy this member. translate.py
      * copies this file verbatim into the harness build tree; it is
      * never preprocessed in place.
      *
      * The group is EXTERNAL: every compilation unit that COPYs this
      * member addresses the same storage. The SQL stub programs in
      * modernization/harness/stubs/ set SQLCODE on each call, and the
      * translated LGAPDB01 reads it at the locators recorded below.
      *
      * No item is initialised in this member. The harness driver seeds
      * the shared state procedurally before it calls the chain.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      * See modernization/docs/decision-log.md (planned deliverable;
      * not present at this milestone):
      * "shared EXTERNAL harness state" and "minimal SQLCA field set".
      *
      *----------------------------------------------------------------*
      * SQLCA - SQL communications area of the translated LGAPDB01.    *
      *----------------------------------------------------------------*
       01  SQLCA EXTERNAL.
      *
      * SQLCODE - result of the most recent SQL operation. Zero
      *   reports success; a negative value reports a failure.
      *   Evaluated at base/src/lgapdb01.cbl:290, where the When 0
      *   branch at line 292 moves '00' to CA-RETURN-CODE, the
      *   When -530 branch at line 295 moves '70', and the When Other
      *   branch at line 300 moves '90'.
      *   Compared against zero by IF SQLCODE NOT EQUAL 0 at
      *   base/src/lgapdb01.cbl:389, 427, 473 and 547, following the
      *   endowment, house, motor and commercial inserts. Each unequal
      *   compare moves '90' to CA-RETURN-CODE and abends with ABCODE
      *   'LGSQ'.
      *   Moved at base/src/lgapdb01.cbl:564 to EM-SQLRC, the
      *   PIC +9(5) USAGE DISPLAY field declared at
      *   base/src/lgapdb01.cbl:53.
      *   Signed nine-digit binary. The values that reach it are the
      *   zero the harness SQL stubs report on a call that injects
      *   nothing, the SQLCODE a case injects through HC-INJECT of
      *   modernization/harness/copybooks/hcapture.cpy, and the -530
      *   compared at base/src/lgapdb01.cbl:295.
           03 SQLCODE                  PIC S9(9) COMP-5.
      *----------------------------------------------------------------*
