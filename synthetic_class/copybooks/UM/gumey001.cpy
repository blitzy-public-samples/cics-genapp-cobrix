******************************************************************
*  COPYBOOK  : GUMEY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : ME
******************************************************************
 01  PT-UME-PARTY.

          03 PT-UME-INSURED-NAME              PIC X(40).
          03 PT-UME-TAX-ID                    PIC X(11).
          03 PT-UME-ADDRESS-LINE1             PIC X(30).
          03 PT-UME-ADDRESS-LINE2             PIC X(30).
          03 PT-UME-CITY                      PIC X(20).
          03 PT-UME-STATE-CODE                PIC X(2).
          03 PT-UME-ZIP-CODE                  PIC X(9).
          03 PT-UME-PHONE                     PIC X(14).
          03 PT-UME-AGENCY-CODE               PIC X(6).
          03 PT-UME-AGENT-NAME                PIC X(30).
