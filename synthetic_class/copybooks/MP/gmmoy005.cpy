******************************************************************
*  COPYBOOK  : GMMOY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MO
******************************************************************
 01  PT-MMO-PARTY.

          03 PT-MMO-INSURED-NAME              PIC X(40).
          03 PT-MMO-TAX-ID                    PIC X(11).
          03 PT-MMO-ADDRESS-LINE1             PIC X(30).
          03 PT-MMO-ADDRESS-LINE2             PIC X(30).
          03 PT-MMO-CITY                      PIC X(20).
          03 PT-MMO-STATE-CODE                PIC X(2).
          03 PT-MMO-ZIP-CODE                  PIC X(9).
          03 PT-MMO-PHONE                     PIC X(14).
          03 PT-MMO-AGENCY-CODE               PIC X(6).
          03 PT-MMO-AGENT-NAME                PIC X(30).
