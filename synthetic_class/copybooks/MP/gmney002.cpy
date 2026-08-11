******************************************************************
*  COPYBOOK  : GMNEY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NE
******************************************************************
 01  PT-MNE-PARTY.

          03 PT-MNE-INSURED-NAME              PIC X(40).
          03 PT-MNE-TAX-ID                    PIC X(11).
          03 PT-MNE-ADDRESS-LINE1             PIC X(30).
          03 PT-MNE-ADDRESS-LINE2             PIC X(30).
          03 PT-MNE-CITY                      PIC X(20).
          03 PT-MNE-STATE-CODE                PIC X(2).
          03 PT-MNE-ZIP-CODE                  PIC X(9).
          03 PT-MNE-PHONE                     PIC X(14).
          03 PT-MNE-AGENCY-CODE               PIC X(6).
          03 PT-MNE-AGENT-NAME                PIC X(30).
