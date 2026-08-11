******************************************************************
*  COPYBOOK  : GMNCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NC
******************************************************************
 01  PT-MNC-PARTY.

          03 PT-MNC-INSURED-NAME              PIC X(40).
          03 PT-MNC-TAX-ID                    PIC X(11).
          03 PT-MNC-ADDRESS-LINE1             PIC X(30).
          03 PT-MNC-ADDRESS-LINE2             PIC X(30).
          03 PT-MNC-CITY                      PIC X(20).
          03 PT-MNC-STATE-CODE                PIC X(2).
          03 PT-MNC-ZIP-CODE                  PIC X(9).
          03 PT-MNC-PHONE                     PIC X(14).
          03 PT-MNC-AGENCY-CODE               PIC X(6).
          03 PT-MNC-AGENT-NAME                PIC X(30).
