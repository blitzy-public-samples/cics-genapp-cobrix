******************************************************************
*  COPYBOOK  : GMOKY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : OK
******************************************************************
 01  PT-MOK-PARTY.

          03 PT-MOK-INSURED-NAME              PIC X(40).
          03 PT-MOK-TAX-ID                    PIC X(11).
          03 PT-MOK-ADDRESS-LINE1             PIC X(30).
          03 PT-MOK-ADDRESS-LINE2             PIC X(30).
          03 PT-MOK-CITY                      PIC X(20).
          03 PT-MOK-STATE-CODE                PIC X(2).
          03 PT-MOK-ZIP-CODE                  PIC X(9).
          03 PT-MOK-PHONE                     PIC X(14).
          03 PT-MOK-AGENCY-CODE               PIC X(6).
          03 PT-MOK-AGENT-NAME                PIC X(30).
