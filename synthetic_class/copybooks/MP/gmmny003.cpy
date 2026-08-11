******************************************************************
*  COPYBOOK  : GMMNY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MN
******************************************************************
 01  PT-MMN-PARTY.

          03 PT-MMN-INSURED-NAME              PIC X(40).
          03 PT-MMN-TAX-ID                    PIC X(11).
          03 PT-MMN-ADDRESS-LINE1             PIC X(30).
          03 PT-MMN-ADDRESS-LINE2             PIC X(30).
          03 PT-MMN-CITY                      PIC X(20).
          03 PT-MMN-STATE-CODE                PIC X(2).
          03 PT-MMN-ZIP-CODE                  PIC X(9).
          03 PT-MMN-PHONE                     PIC X(14).
          03 PT-MMN-AGENCY-CODE               PIC X(6).
          03 PT-MMN-AGENT-NAME                PIC X(30).
