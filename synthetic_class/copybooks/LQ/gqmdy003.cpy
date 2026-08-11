******************************************************************
*  COPYBOOK  : GQMDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : MD
******************************************************************
 01  PT-QMD-PARTY.

          03 PT-QMD-INSURED-NAME              PIC X(40).
          03 PT-QMD-TAX-ID                    PIC X(11).
          03 PT-QMD-ADDRESS-LINE1             PIC X(30).
          03 PT-QMD-ADDRESS-LINE2             PIC X(30).
          03 PT-QMD-CITY                      PIC X(20).
          03 PT-QMD-STATE-CODE                PIC X(2).
          03 PT-QMD-ZIP-CODE                  PIC X(9).
          03 PT-QMD-PHONE                     PIC X(14).
          03 PT-QMD-AGENCY-CODE               PIC X(6).
          03 PT-QMD-AGENT-NAME                PIC X(30).
