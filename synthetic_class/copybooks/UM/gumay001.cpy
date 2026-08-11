******************************************************************
*  COPYBOOK  : GUMAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MA
******************************************************************
 01  PT-UMA-PARTY.

          03 PT-UMA-INSURED-NAME              PIC X(40).
          03 PT-UMA-TAX-ID                    PIC X(11).
          03 PT-UMA-ADDRESS-LINE1             PIC X(30).
          03 PT-UMA-ADDRESS-LINE2             PIC X(30).
          03 PT-UMA-CITY                      PIC X(20).
          03 PT-UMA-STATE-CODE                PIC X(2).
          03 PT-UMA-ZIP-CODE                  PIC X(9).
          03 PT-UMA-PHONE                     PIC X(14).
          03 PT-UMA-AGENCY-CODE               PIC X(6).
          03 PT-UMA-AGENT-NAME                PIC X(30).
