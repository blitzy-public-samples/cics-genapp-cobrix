******************************************************************
*  COPYBOOK  : GMDEY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : DE
******************************************************************
 01  PT-MDE-PARTY.

          03 PT-MDE-INSURED-NAME              PIC X(40).
          03 PT-MDE-TAX-ID                    PIC X(11).
          03 PT-MDE-ADDRESS-LINE1             PIC X(30).
          03 PT-MDE-ADDRESS-LINE2             PIC X(30).
          03 PT-MDE-CITY                      PIC X(20).
          03 PT-MDE-STATE-CODE                PIC X(2).
          03 PT-MDE-ZIP-CODE                  PIC X(9).
          03 PT-MDE-PHONE                     PIC X(14).
          03 PT-MDE-AGENCY-CODE               PIC X(6).
          03 PT-MDE-AGENT-NAME                PIC X(30).
