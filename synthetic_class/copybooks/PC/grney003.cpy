******************************************************************
*  COPYBOOK  : GRNEY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NE
******************************************************************
 01  PT-RNE-PARTY.

          03 PT-RNE-INSURED-NAME              PIC X(40).
          03 PT-RNE-TAX-ID                    PIC X(11).
          03 PT-RNE-ADDRESS-LINE1             PIC X(30).
          03 PT-RNE-ADDRESS-LINE2             PIC X(30).
          03 PT-RNE-CITY                      PIC X(20).
          03 PT-RNE-STATE-CODE                PIC X(2).
          03 PT-RNE-ZIP-CODE                  PIC X(9).
          03 PT-RNE-PHONE                     PIC X(14).
          03 PT-RNE-AGENCY-CODE               PIC X(6).
          03 PT-RNE-AGENT-NAME                PIC X(30).
