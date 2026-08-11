******************************************************************
*  COPYBOOK  : GUMDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MD
******************************************************************
 01  PT-UMD-PARTY.

          03 PT-UMD-INSURED-NAME              PIC X(40).
          03 PT-UMD-TAX-ID                    PIC X(11).
          03 PT-UMD-ADDRESS-LINE1             PIC X(30).
          03 PT-UMD-ADDRESS-LINE2             PIC X(30).
          03 PT-UMD-CITY                      PIC X(20).
          03 PT-UMD-STATE-CODE                PIC X(2).
          03 PT-UMD-ZIP-CODE                  PIC X(9).
          03 PT-UMD-PHONE                     PIC X(14).
          03 PT-UMD-AGENCY-CODE               PIC X(6).
          03 PT-UMD-AGENT-NAME                PIC X(30).
