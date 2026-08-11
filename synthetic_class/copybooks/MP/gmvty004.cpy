******************************************************************
*  COPYBOOK  : GMVTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : VT
******************************************************************
 01  PT-MVT-PARTY.

          03 PT-MVT-INSURED-NAME              PIC X(40).
          03 PT-MVT-TAX-ID                    PIC X(11).
          03 PT-MVT-ADDRESS-LINE1             PIC X(30).
          03 PT-MVT-ADDRESS-LINE2             PIC X(30).
          03 PT-MVT-CITY                      PIC X(20).
          03 PT-MVT-STATE-CODE                PIC X(2).
          03 PT-MVT-ZIP-CODE                  PIC X(9).
          03 PT-MVT-PHONE                     PIC X(14).
          03 PT-MVT-AGENCY-CODE               PIC X(6).
          03 PT-MVT-AGENT-NAME                PIC X(30).
