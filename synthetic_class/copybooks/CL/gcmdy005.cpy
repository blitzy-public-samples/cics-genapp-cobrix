******************************************************************
*  COPYBOOK  : GCMDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MD
******************************************************************
 01  PT-CMD-PARTY.

          03 PT-CMD-INSURED-NAME              PIC X(40).
          03 PT-CMD-TAX-ID                    PIC X(11).
          03 PT-CMD-ADDRESS-LINE1             PIC X(30).
          03 PT-CMD-ADDRESS-LINE2             PIC X(30).
          03 PT-CMD-CITY                      PIC X(20).
          03 PT-CMD-STATE-CODE                PIC X(2).
          03 PT-CMD-ZIP-CODE                  PIC X(9).
          03 PT-CMD-PHONE                     PIC X(14).
          03 PT-CMD-AGENCY-CODE               PIC X(6).
          03 PT-CMD-AGENT-NAME                PIC X(30).
