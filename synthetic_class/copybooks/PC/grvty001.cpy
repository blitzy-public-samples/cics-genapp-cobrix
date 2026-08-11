******************************************************************
*  COPYBOOK  : GRVTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : VT
******************************************************************
 01  PT-RVT-PARTY.

          03 PT-RVT-INSURED-NAME              PIC X(40).
          03 PT-RVT-TAX-ID                    PIC X(11).
          03 PT-RVT-ADDRESS-LINE1             PIC X(30).
          03 PT-RVT-ADDRESS-LINE2             PIC X(30).
          03 PT-RVT-CITY                      PIC X(20).
          03 PT-RVT-STATE-CODE                PIC X(2).
          03 PT-RVT-ZIP-CODE                  PIC X(9).
          03 PT-RVT-PHONE                     PIC X(14).
          03 PT-RVT-AGENCY-CODE               PIC X(6).
          03 PT-RVT-AGENT-NAME                PIC X(30).
