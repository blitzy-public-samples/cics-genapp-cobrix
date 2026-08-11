******************************************************************
*  COPYBOOK  : GMNDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : ND
******************************************************************
 01  PT-MND-PARTY.

          03 PT-MND-INSURED-NAME              PIC X(40).
          03 PT-MND-TAX-ID                    PIC X(11).
          03 PT-MND-ADDRESS-LINE1             PIC X(30).
          03 PT-MND-ADDRESS-LINE2             PIC X(30).
          03 PT-MND-CITY                      PIC X(20).
          03 PT-MND-STATE-CODE                PIC X(2).
          03 PT-MND-ZIP-CODE                  PIC X(9).
          03 PT-MND-PHONE                     PIC X(14).
          03 PT-MND-AGENCY-CODE               PIC X(6).
          03 PT-MND-AGENT-NAME                PIC X(30).
