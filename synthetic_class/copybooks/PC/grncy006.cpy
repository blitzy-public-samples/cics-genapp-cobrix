******************************************************************
*  COPYBOOK  : GRNCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NC
******************************************************************
 01  PT-RNC-PARTY.

          03 PT-RNC-INSURED-NAME              PIC X(40).
          03 PT-RNC-TAX-ID                    PIC X(11).
          03 PT-RNC-ADDRESS-LINE1             PIC X(30).
          03 PT-RNC-ADDRESS-LINE2             PIC X(30).
          03 PT-RNC-CITY                      PIC X(20).
          03 PT-RNC-STATE-CODE                PIC X(2).
          03 PT-RNC-ZIP-CODE                  PIC X(9).
          03 PT-RNC-PHONE                     PIC X(14).
          03 PT-RNC-AGENCY-CODE               PIC X(6).
          03 PT-RNC-AGENT-NAME                PIC X(30).
