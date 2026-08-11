******************************************************************
*  COPYBOOK  : GRMEY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : ME
******************************************************************
 01  PT-RME-PARTY.

          03 PT-RME-INSURED-NAME              PIC X(40).
          03 PT-RME-TAX-ID                    PIC X(11).
          03 PT-RME-ADDRESS-LINE1             PIC X(30).
          03 PT-RME-ADDRESS-LINE2             PIC X(30).
          03 PT-RME-CITY                      PIC X(20).
          03 PT-RME-STATE-CODE                PIC X(2).
          03 PT-RME-ZIP-CODE                  PIC X(9).
          03 PT-RME-PHONE                     PIC X(14).
          03 PT-RME-AGENCY-CODE               PIC X(6).
          03 PT-RME-AGENT-NAME                PIC X(30).
