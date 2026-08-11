******************************************************************
*  COPYBOOK  : GUMSY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MS
******************************************************************
 01  PT-UMS-PARTY.

          03 PT-UMS-INSURED-NAME              PIC X(40).
          03 PT-UMS-TAX-ID                    PIC X(11).
          03 PT-UMS-ADDRESS-LINE1             PIC X(30).
          03 PT-UMS-ADDRESS-LINE2             PIC X(30).
          03 PT-UMS-CITY                      PIC X(20).
          03 PT-UMS-STATE-CODE                PIC X(2).
          03 PT-UMS-ZIP-CODE                  PIC X(9).
          03 PT-UMS-PHONE                     PIC X(14).
          03 PT-UMS-AGENCY-CODE               PIC X(6).
          03 PT-UMS-AGENT-NAME                PIC X(30).
