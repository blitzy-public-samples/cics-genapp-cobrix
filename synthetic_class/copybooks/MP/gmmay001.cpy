******************************************************************
*  COPYBOOK  : GMMAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MA
******************************************************************
 01  PT-MMA-PARTY.

          03 PT-MMA-INSURED-NAME              PIC X(40).
          03 PT-MMA-TAX-ID                    PIC X(11).
          03 PT-MMA-ADDRESS-LINE1             PIC X(30).
          03 PT-MMA-ADDRESS-LINE2             PIC X(30).
          03 PT-MMA-CITY                      PIC X(20).
          03 PT-MMA-STATE-CODE                PIC X(2).
          03 PT-MMA-ZIP-CODE                  PIC X(9).
          03 PT-MMA-PHONE                     PIC X(14).
          03 PT-MMA-AGENCY-CODE               PIC X(6).
          03 PT-MMA-AGENT-NAME                PIC X(30).
