******************************************************************
*  COPYBOOK  : GRMSY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MS
******************************************************************
 01  PT-RMS-PARTY.

          03 PT-RMS-INSURED-NAME              PIC X(40).
          03 PT-RMS-TAX-ID                    PIC X(11).
          03 PT-RMS-ADDRESS-LINE1             PIC X(30).
          03 PT-RMS-ADDRESS-LINE2             PIC X(30).
          03 PT-RMS-CITY                      PIC X(20).
          03 PT-RMS-STATE-CODE                PIC X(2).
          03 PT-RMS-ZIP-CODE                  PIC X(9).
          03 PT-RMS-PHONE                     PIC X(14).
          03 PT-RMS-AGENCY-CODE               PIC X(6).
          03 PT-RMS-AGENT-NAME                PIC X(30).
