******************************************************************
*  COPYBOOK  : GRPAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : PA
******************************************************************
 01  PT-RPA-PARTY.

          03 PT-RPA-INSURED-NAME              PIC X(40).
          03 PT-RPA-TAX-ID                    PIC X(11).
          03 PT-RPA-ADDRESS-LINE1             PIC X(30).
          03 PT-RPA-ADDRESS-LINE2             PIC X(30).
          03 PT-RPA-CITY                      PIC X(20).
          03 PT-RPA-STATE-CODE                PIC X(2).
          03 PT-RPA-ZIP-CODE                  PIC X(9).
          03 PT-RPA-PHONE                     PIC X(14).
          03 PT-RPA-AGENCY-CODE               PIC X(6).
          03 PT-RPA-AGENT-NAME                PIC X(30).
