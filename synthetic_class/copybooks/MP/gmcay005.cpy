******************************************************************
*  COPYBOOK  : GMCAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : CA
******************************************************************
 01  PT-MCA-PARTY.

          03 PT-MCA-INSURED-NAME              PIC X(40).
          03 PT-MCA-TAX-ID                    PIC X(11).
          03 PT-MCA-ADDRESS-LINE1             PIC X(30).
          03 PT-MCA-ADDRESS-LINE2             PIC X(30).
          03 PT-MCA-CITY                      PIC X(20).
          03 PT-MCA-STATE-CODE                PIC X(2).
          03 PT-MCA-ZIP-CODE                  PIC X(9).
          03 PT-MCA-PHONE                     PIC X(14).
          03 PT-MCA-AGENCY-CODE               PIC X(6).
          03 PT-MCA-AGENT-NAME                PIC X(30).
