******************************************************************
*  COPYBOOK  : GMNVY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NV
******************************************************************
 01  PT-MNV-PARTY.

          03 PT-MNV-INSURED-NAME              PIC X(40).
          03 PT-MNV-TAX-ID                    PIC X(11).
          03 PT-MNV-ADDRESS-LINE1             PIC X(30).
          03 PT-MNV-ADDRESS-LINE2             PIC X(30).
          03 PT-MNV-CITY                      PIC X(20).
          03 PT-MNV-STATE-CODE                PIC X(2).
          03 PT-MNV-ZIP-CODE                  PIC X(9).
          03 PT-MNV-PHONE                     PIC X(14).
          03 PT-MNV-AGENCY-CODE               PIC X(6).
          03 PT-MNV-AGENT-NAME                PIC X(30).
