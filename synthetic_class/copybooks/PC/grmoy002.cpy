******************************************************************
*  COPYBOOK  : GRMOY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MO
******************************************************************
 01  PT-RMO-PARTY.

          03 PT-RMO-INSURED-NAME              PIC X(40).
          03 PT-RMO-TAX-ID                    PIC X(11).
          03 PT-RMO-ADDRESS-LINE1             PIC X(30).
          03 PT-RMO-ADDRESS-LINE2             PIC X(30).
          03 PT-RMO-CITY                      PIC X(20).
          03 PT-RMO-STATE-CODE                PIC X(2).
          03 PT-RMO-ZIP-CODE                  PIC X(9).
          03 PT-RMO-PHONE                     PIC X(14).
          03 PT-RMO-AGENCY-CODE               PIC X(6).
          03 PT-RMO-AGENT-NAME                PIC X(30).
