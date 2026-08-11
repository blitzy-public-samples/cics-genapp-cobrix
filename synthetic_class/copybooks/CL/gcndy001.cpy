******************************************************************
*  COPYBOOK  : GCNDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : ND
******************************************************************
 01  PT-CND-PARTY.

          03 PT-CND-INSURED-NAME              PIC X(40).
          03 PT-CND-TAX-ID                    PIC X(11).
          03 PT-CND-ADDRESS-LINE1             PIC X(30).
          03 PT-CND-ADDRESS-LINE2             PIC X(30).
          03 PT-CND-CITY                      PIC X(20).
          03 PT-CND-STATE-CODE                PIC X(2).
          03 PT-CND-ZIP-CODE                  PIC X(9).
          03 PT-CND-PHONE                     PIC X(14).
          03 PT-CND-AGENCY-CODE               PIC X(6).
          03 PT-CND-AGENT-NAME                PIC X(30).
