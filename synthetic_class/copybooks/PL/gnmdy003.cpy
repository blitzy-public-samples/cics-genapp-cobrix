******************************************************************
*  COPYBOOK  : GNMDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : MD
******************************************************************
 01  PT-NMD-PARTY.

          03 PT-NMD-INSURED-NAME              PIC X(40).
          03 PT-NMD-TAX-ID                    PIC X(11).
          03 PT-NMD-ADDRESS-LINE1             PIC X(30).
          03 PT-NMD-ADDRESS-LINE2             PIC X(30).
          03 PT-NMD-CITY                      PIC X(20).
          03 PT-NMD-STATE-CODE                PIC X(2).
          03 PT-NMD-ZIP-CODE                  PIC X(9).
          03 PT-NMD-PHONE                     PIC X(14).
          03 PT-NMD-AGENCY-CODE               PIC X(6).
          03 PT-NMD-AGENT-NAME                PIC X(30).
