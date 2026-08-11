******************************************************************
*  COPYBOOK  : GUMOY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MO
******************************************************************
 01  PT-UMO-PARTY.

          03 PT-UMO-INSURED-NAME              PIC X(40).
          03 PT-UMO-TAX-ID                    PIC X(11).
          03 PT-UMO-ADDRESS-LINE1             PIC X(30).
          03 PT-UMO-ADDRESS-LINE2             PIC X(30).
          03 PT-UMO-CITY                      PIC X(20).
          03 PT-UMO-STATE-CODE                PIC X(2).
          03 PT-UMO-ZIP-CODE                  PIC X(9).
          03 PT-UMO-PHONE                     PIC X(14).
          03 PT-UMO-AGENCY-CODE               PIC X(6).
          03 PT-UMO-AGENT-NAME                PIC X(30).
