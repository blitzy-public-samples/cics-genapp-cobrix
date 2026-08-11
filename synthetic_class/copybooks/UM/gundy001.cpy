******************************************************************
*  COPYBOOK  : GUNDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : ND
******************************************************************
 01  PT-UND-PARTY.

          03 PT-UND-INSURED-NAME              PIC X(40).
          03 PT-UND-TAX-ID                    PIC X(11).
          03 PT-UND-ADDRESS-LINE1             PIC X(30).
          03 PT-UND-ADDRESS-LINE2             PIC X(30).
          03 PT-UND-CITY                      PIC X(20).
          03 PT-UND-STATE-CODE                PIC X(2).
          03 PT-UND-ZIP-CODE                  PIC X(9).
          03 PT-UND-PHONE                     PIC X(14).
          03 PT-UND-AGENCY-CODE               PIC X(6).
          03 PT-UND-AGENT-NAME                PIC X(30).
