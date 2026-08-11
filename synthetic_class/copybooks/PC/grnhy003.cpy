******************************************************************
*  COPYBOOK  : GRNHY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NH
******************************************************************
 01  PT-RNH-PARTY.

          03 PT-RNH-INSURED-NAME              PIC X(40).
          03 PT-RNH-TAX-ID                    PIC X(11).
          03 PT-RNH-ADDRESS-LINE1             PIC X(30).
          03 PT-RNH-ADDRESS-LINE2             PIC X(30).
          03 PT-RNH-CITY                      PIC X(20).
          03 PT-RNH-STATE-CODE                PIC X(2).
          03 PT-RNH-ZIP-CODE                  PIC X(9).
          03 PT-RNH-PHONE                     PIC X(14).
          03 PT-RNH-AGENCY-CODE               PIC X(6).
          03 PT-RNH-AGENT-NAME                PIC X(30).
