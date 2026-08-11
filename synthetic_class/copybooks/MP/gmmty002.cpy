******************************************************************
*  COPYBOOK  : GMMTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MT
******************************************************************
 01  PT-MMT-PARTY.

          03 PT-MMT-INSURED-NAME              PIC X(40).
          03 PT-MMT-TAX-ID                    PIC X(11).
          03 PT-MMT-ADDRESS-LINE1             PIC X(30).
          03 PT-MMT-ADDRESS-LINE2             PIC X(30).
          03 PT-MMT-CITY                      PIC X(20).
          03 PT-MMT-STATE-CODE                PIC X(2).
          03 PT-MMT-ZIP-CODE                  PIC X(9).
          03 PT-MMT-PHONE                     PIC X(14).
          03 PT-MMT-AGENCY-CODE               PIC X(6).
          03 PT-MMT-AGENT-NAME                PIC X(30).
