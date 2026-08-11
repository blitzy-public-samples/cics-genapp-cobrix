******************************************************************
*  COPYBOOK  : GMWVY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : WV
******************************************************************
 01  PT-MWV-PARTY.

          03 PT-MWV-INSURED-NAME              PIC X(40).
          03 PT-MWV-TAX-ID                    PIC X(11).
          03 PT-MWV-ADDRESS-LINE1             PIC X(30).
          03 PT-MWV-ADDRESS-LINE2             PIC X(30).
          03 PT-MWV-CITY                      PIC X(20).
          03 PT-MWV-STATE-CODE                PIC X(2).
          03 PT-MWV-ZIP-CODE                  PIC X(9).
          03 PT-MWV-PHONE                     PIC X(14).
          03 PT-MWV-AGENCY-CODE               PIC X(6).
          03 PT-MWV-AGENT-NAME                PIC X(30).
