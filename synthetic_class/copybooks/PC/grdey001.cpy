******************************************************************
*  COPYBOOK  : GRDEY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : DE
******************************************************************
 01  PT-RDE-PARTY.

          03 PT-RDE-INSURED-NAME              PIC X(40).
          03 PT-RDE-TAX-ID                    PIC X(11).
          03 PT-RDE-ADDRESS-LINE1             PIC X(30).
          03 PT-RDE-ADDRESS-LINE2             PIC X(30).
          03 PT-RDE-CITY                      PIC X(20).
          03 PT-RDE-STATE-CODE                PIC X(2).
          03 PT-RDE-ZIP-CODE                  PIC X(9).
          03 PT-RDE-PHONE                     PIC X(14).
          03 PT-RDE-AGENCY-CODE               PIC X(6).
          03 PT-RDE-AGENT-NAME                PIC X(30).
