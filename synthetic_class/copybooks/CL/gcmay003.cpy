******************************************************************
*  COPYBOOK  : GCMAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MA
******************************************************************
 01  PT-CMA-PARTY.

          03 PT-CMA-INSURED-NAME              PIC X(40).
          03 PT-CMA-TAX-ID                    PIC X(11).
          03 PT-CMA-ADDRESS-LINE1             PIC X(30).
          03 PT-CMA-ADDRESS-LINE2             PIC X(30).
          03 PT-CMA-CITY                      PIC X(20).
          03 PT-CMA-STATE-CODE                PIC X(2).
          03 PT-CMA-ZIP-CODE                  PIC X(9).
          03 PT-CMA-PHONE                     PIC X(14).
          03 PT-CMA-AGENCY-CODE               PIC X(6).
          03 PT-CMA-AGENT-NAME                PIC X(30).
