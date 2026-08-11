******************************************************************
*  COPYBOOK  : GCINY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : IN
******************************************************************
 01  PT-CIN-PARTY.

          03 PT-CIN-INSURED-NAME              PIC X(40).
          03 PT-CIN-TAX-ID                    PIC X(11).
          03 PT-CIN-ADDRESS-LINE1             PIC X(30).
          03 PT-CIN-ADDRESS-LINE2             PIC X(30).
          03 PT-CIN-CITY                      PIC X(20).
          03 PT-CIN-STATE-CODE                PIC X(2).
          03 PT-CIN-ZIP-CODE                  PIC X(9).
          03 PT-CIN-PHONE                     PIC X(14).
          03 PT-CIN-AGENCY-CODE               PIC X(6).
          03 PT-CIN-AGENT-NAME                PIC X(30).
