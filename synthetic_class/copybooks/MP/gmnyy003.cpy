******************************************************************
*  COPYBOOK  : GMNYY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NY
******************************************************************
 01  PT-MNY-PARTY.

          03 PT-MNY-INSURED-NAME              PIC X(40).
          03 PT-MNY-TAX-ID                    PIC X(11).
          03 PT-MNY-ADDRESS-LINE1             PIC X(30).
          03 PT-MNY-ADDRESS-LINE2             PIC X(30).
          03 PT-MNY-CITY                      PIC X(20).
          03 PT-MNY-STATE-CODE                PIC X(2).
          03 PT-MNY-ZIP-CODE                  PIC X(9).
          03 PT-MNY-PHONE                     PIC X(14).
          03 PT-MNY-AGENCY-CODE               PIC X(6).
          03 PT-MNY-AGENT-NAME                PIC X(30).
