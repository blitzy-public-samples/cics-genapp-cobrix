******************************************************************
*  COPYBOOK  : GBSDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : SD
******************************************************************
 01  PT-BSD-PARTY.

          03 PT-BSD-INSURED-NAME              PIC X(40).
          03 PT-BSD-TAX-ID                    PIC X(11).
          03 PT-BSD-ADDRESS-LINE1             PIC X(30).
          03 PT-BSD-ADDRESS-LINE2             PIC X(30).
          03 PT-BSD-CITY                      PIC X(20).
          03 PT-BSD-STATE-CODE                PIC X(2).
          03 PT-BSD-ZIP-CODE                  PIC X(9).
          03 PT-BSD-PHONE                     PIC X(14).
          03 PT-BSD-AGENCY-CODE               PIC X(6).
          03 PT-BSD-AGENT-NAME                PIC X(30).
