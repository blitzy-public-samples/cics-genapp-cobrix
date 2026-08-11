******************************************************************
*  COPYBOOK  : GMALY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : AL
******************************************************************
 01  PT-MAL-PARTY.

          03 PT-MAL-INSURED-NAME              PIC X(40).
          03 PT-MAL-TAX-ID                    PIC X(11).
          03 PT-MAL-ADDRESS-LINE1             PIC X(30).
          03 PT-MAL-ADDRESS-LINE2             PIC X(30).
          03 PT-MAL-CITY                      PIC X(20).
          03 PT-MAL-STATE-CODE                PIC X(2).
          03 PT-MAL-ZIP-CODE                  PIC X(9).
          03 PT-MAL-PHONE                     PIC X(14).
          03 PT-MAL-AGENCY-CODE               PIC X(6).
          03 PT-MAL-AGENT-NAME                PIC X(30).
