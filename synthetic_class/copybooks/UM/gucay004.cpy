******************************************************************
*  COPYBOOK  : GUCAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : CA
******************************************************************
 01  PT-UCA-PARTY.

          03 PT-UCA-INSURED-NAME              PIC X(40).
          03 PT-UCA-TAX-ID                    PIC X(11).
          03 PT-UCA-ADDRESS-LINE1             PIC X(30).
          03 PT-UCA-ADDRESS-LINE2             PIC X(30).
          03 PT-UCA-CITY                      PIC X(20).
          03 PT-UCA-STATE-CODE                PIC X(2).
          03 PT-UCA-ZIP-CODE                  PIC X(9).
          03 PT-UCA-PHONE                     PIC X(14).
          03 PT-UCA-AGENCY-CODE               PIC X(6).
          03 PT-UCA-AGENT-NAME                PIC X(30).
