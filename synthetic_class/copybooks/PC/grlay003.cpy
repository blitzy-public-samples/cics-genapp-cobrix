******************************************************************
*  COPYBOOK  : GRLAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : LA
******************************************************************
 01  PT-RLA-PARTY.

          03 PT-RLA-INSURED-NAME              PIC X(40).
          03 PT-RLA-TAX-ID                    PIC X(11).
          03 PT-RLA-ADDRESS-LINE1             PIC X(30).
          03 PT-RLA-ADDRESS-LINE2             PIC X(30).
          03 PT-RLA-CITY                      PIC X(20).
          03 PT-RLA-STATE-CODE                PIC X(2).
          03 PT-RLA-ZIP-CODE                  PIC X(9).
          03 PT-RLA-PHONE                     PIC X(14).
          03 PT-RLA-AGENCY-CODE               PIC X(6).
          03 PT-RLA-AGENT-NAME                PIC X(30).
