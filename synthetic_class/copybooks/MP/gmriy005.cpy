******************************************************************
*  COPYBOOK  : GMRIY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : RI
******************************************************************
 01  PT-MRI-PARTY.

          03 PT-MRI-INSURED-NAME              PIC X(40).
          03 PT-MRI-TAX-ID                    PIC X(11).
          03 PT-MRI-ADDRESS-LINE1             PIC X(30).
          03 PT-MRI-ADDRESS-LINE2             PIC X(30).
          03 PT-MRI-CITY                      PIC X(20).
          03 PT-MRI-STATE-CODE                PIC X(2).
          03 PT-MRI-ZIP-CODE                  PIC X(9).
          03 PT-MRI-PHONE                     PIC X(14).
          03 PT-MRI-AGENCY-CODE               PIC X(6).
          03 PT-MRI-AGENT-NAME                PIC X(30).
