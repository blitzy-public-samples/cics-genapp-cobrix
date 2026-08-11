******************************************************************
*  COPYBOOK  : GRMAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MA
******************************************************************
 01  PT-RMA-PARTY.

          03 PT-RMA-INSURED-NAME              PIC X(40).
          03 PT-RMA-TAX-ID                    PIC X(11).
          03 PT-RMA-ADDRESS-LINE1             PIC X(30).
          03 PT-RMA-ADDRESS-LINE2             PIC X(30).
          03 PT-RMA-CITY                      PIC X(20).
          03 PT-RMA-STATE-CODE                PIC X(2).
          03 PT-RMA-ZIP-CODE                  PIC X(9).
          03 PT-RMA-PHONE                     PIC X(14).
          03 PT-RMA-AGENCY-CODE               PIC X(6).
          03 PT-RMA-AGENT-NAME                PIC X(30).
