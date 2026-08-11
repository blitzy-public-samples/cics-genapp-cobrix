******************************************************************
*  COPYBOOK  : GRSDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : SD
******************************************************************
 01  PT-RSD-PARTY.

          03 PT-RSD-INSURED-NAME              PIC X(40).
          03 PT-RSD-TAX-ID                    PIC X(11).
          03 PT-RSD-ADDRESS-LINE1             PIC X(30).
          03 PT-RSD-ADDRESS-LINE2             PIC X(30).
          03 PT-RSD-CITY                      PIC X(20).
          03 PT-RSD-STATE-CODE                PIC X(2).
          03 PT-RSD-ZIP-CODE                  PIC X(9).
          03 PT-RSD-PHONE                     PIC X(14).
          03 PT-RSD-AGENCY-CODE               PIC X(6).
          03 PT-RSD-AGENT-NAME                PIC X(30).
