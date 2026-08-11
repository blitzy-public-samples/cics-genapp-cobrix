******************************************************************
*  COPYBOOK  : GMCOY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : CO
******************************************************************
 01  PT-MCO-PARTY.

          03 PT-MCO-INSURED-NAME              PIC X(40).
          03 PT-MCO-TAX-ID                    PIC X(11).
          03 PT-MCO-ADDRESS-LINE1             PIC X(30).
          03 PT-MCO-ADDRESS-LINE2             PIC X(30).
          03 PT-MCO-CITY                      PIC X(20).
          03 PT-MCO-STATE-CODE                PIC X(2).
          03 PT-MCO-ZIP-CODE                  PIC X(9).
          03 PT-MCO-PHONE                     PIC X(14).
          03 PT-MCO-AGENCY-CODE               PIC X(6).
          03 PT-MCO-AGENT-NAME                PIC X(30).
