******************************************************************
*  COPYBOOK  : GMLAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : LA
******************************************************************
 01  PT-MLA-PARTY.

          03 PT-MLA-INSURED-NAME              PIC X(40).
          03 PT-MLA-TAX-ID                    PIC X(11).
          03 PT-MLA-ADDRESS-LINE1             PIC X(30).
          03 PT-MLA-ADDRESS-LINE2             PIC X(30).
          03 PT-MLA-CITY                      PIC X(20).
          03 PT-MLA-STATE-CODE                PIC X(2).
          03 PT-MLA-ZIP-CODE                  PIC X(9).
          03 PT-MLA-PHONE                     PIC X(14).
          03 PT-MLA-AGENCY-CODE               PIC X(6).
          03 PT-MLA-AGENT-NAME                PIC X(30).
