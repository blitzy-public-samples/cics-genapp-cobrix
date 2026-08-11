******************************************************************
*  COPYBOOK  : GMMDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MD
******************************************************************
 01  PT-MMD-PARTY.

          03 PT-MMD-INSURED-NAME              PIC X(40).
          03 PT-MMD-TAX-ID                    PIC X(11).
          03 PT-MMD-ADDRESS-LINE1             PIC X(30).
          03 PT-MMD-ADDRESS-LINE2             PIC X(30).
          03 PT-MMD-CITY                      PIC X(20).
          03 PT-MMD-STATE-CODE                PIC X(2).
          03 PT-MMD-ZIP-CODE                  PIC X(9).
          03 PT-MMD-PHONE                     PIC X(14).
          03 PT-MMD-AGENCY-CODE               PIC X(6).
          03 PT-MMD-AGENT-NAME                PIC X(30).
