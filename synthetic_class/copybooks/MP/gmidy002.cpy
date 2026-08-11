******************************************************************
*  COPYBOOK  : GMIDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : ID
******************************************************************
 01  PT-MID-PARTY.

          03 PT-MID-INSURED-NAME              PIC X(40).
          03 PT-MID-TAX-ID                    PIC X(11).
          03 PT-MID-ADDRESS-LINE1             PIC X(30).
          03 PT-MID-ADDRESS-LINE2             PIC X(30).
          03 PT-MID-CITY                      PIC X(20).
          03 PT-MID-STATE-CODE                PIC X(2).
          03 PT-MID-ZIP-CODE                  PIC X(9).
          03 PT-MID-PHONE                     PIC X(14).
          03 PT-MID-AGENCY-CODE               PIC X(6).
          03 PT-MID-AGENT-NAME                PIC X(30).
