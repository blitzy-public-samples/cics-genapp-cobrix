******************************************************************
*  COPYBOOK  : GUNVY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : NV
******************************************************************
 01  PT-UNV-PARTY.

          03 PT-UNV-INSURED-NAME              PIC X(40).
          03 PT-UNV-TAX-ID                    PIC X(11).
          03 PT-UNV-ADDRESS-LINE1             PIC X(30).
          03 PT-UNV-ADDRESS-LINE2             PIC X(30).
          03 PT-UNV-CITY                      PIC X(20).
          03 PT-UNV-STATE-CODE                PIC X(2).
          03 PT-UNV-ZIP-CODE                  PIC X(9).
          03 PT-UNV-PHONE                     PIC X(14).
          03 PT-UNV-AGENCY-CODE               PIC X(6).
          03 PT-UNV-AGENT-NAME                PIC X(30).
