******************************************************************
*  COPYBOOK  : GBNDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : ND
******************************************************************
 01  PT-BND-PARTY.

          03 PT-BND-INSURED-NAME              PIC X(40).
          03 PT-BND-TAX-ID                    PIC X(11).
          03 PT-BND-ADDRESS-LINE1             PIC X(30).
          03 PT-BND-ADDRESS-LINE2             PIC X(30).
          03 PT-BND-CITY                      PIC X(20).
          03 PT-BND-STATE-CODE                PIC X(2).
          03 PT-BND-ZIP-CODE                  PIC X(9).
          03 PT-BND-PHONE                     PIC X(14).
          03 PT-BND-AGENCY-CODE               PIC X(6).
          03 PT-BND-AGENT-NAME                PIC X(30).
