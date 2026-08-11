******************************************************************
*  COPYBOOK  : GCALY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : AL
******************************************************************
 01  PT-CAL-PARTY.

          03 PT-CAL-INSURED-NAME              PIC X(40).
          03 PT-CAL-TAX-ID                    PIC X(11).
          03 PT-CAL-ADDRESS-LINE1             PIC X(30).
          03 PT-CAL-ADDRESS-LINE2             PIC X(30).
          03 PT-CAL-CITY                      PIC X(20).
          03 PT-CAL-STATE-CODE                PIC X(2).
          03 PT-CAL-ZIP-CODE                  PIC X(9).
          03 PT-CAL-PHONE                     PIC X(14).
          03 PT-CAL-AGENCY-CODE               PIC X(6).
          03 PT-CAL-AGENT-NAME                PIC X(30).
