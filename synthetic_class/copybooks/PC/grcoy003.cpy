******************************************************************
*  COPYBOOK  : GRCOY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : CO
******************************************************************
 01  PT-RCO-PARTY.

          03 PT-RCO-INSURED-NAME              PIC X(40).
          03 PT-RCO-TAX-ID                    PIC X(11).
          03 PT-RCO-ADDRESS-LINE1             PIC X(30).
          03 PT-RCO-ADDRESS-LINE2             PIC X(30).
          03 PT-RCO-CITY                      PIC X(20).
          03 PT-RCO-STATE-CODE                PIC X(2).
          03 PT-RCO-ZIP-CODE                  PIC X(9).
          03 PT-RCO-PHONE                     PIC X(14).
          03 PT-RCO-AGENCY-CODE               PIC X(6).
          03 PT-RCO-AGENT-NAME                PIC X(30).
