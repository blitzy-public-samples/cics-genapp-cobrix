******************************************************************
*  COPYBOOK  : GMPAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : PA
******************************************************************
 01  PT-MPA-PARTY.

          03 PT-MPA-INSURED-NAME              PIC X(40).
          03 PT-MPA-TAX-ID                    PIC X(11).
          03 PT-MPA-ADDRESS-LINE1             PIC X(30).
          03 PT-MPA-ADDRESS-LINE2             PIC X(30).
          03 PT-MPA-CITY                      PIC X(20).
          03 PT-MPA-STATE-CODE                PIC X(2).
          03 PT-MPA-ZIP-CODE                  PIC X(9).
          03 PT-MPA-PHONE                     PIC X(14).
          03 PT-MPA-AGENCY-CODE               PIC X(6).
          03 PT-MPA-AGENT-NAME                PIC X(30).
