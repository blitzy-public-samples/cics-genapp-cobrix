******************************************************************
*  COPYBOOK  : GUMTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MT
******************************************************************
 01  PT-UMT-PARTY.

          03 PT-UMT-INSURED-NAME              PIC X(40).
          03 PT-UMT-TAX-ID                    PIC X(11).
          03 PT-UMT-ADDRESS-LINE1             PIC X(30).
          03 PT-UMT-ADDRESS-LINE2             PIC X(30).
          03 PT-UMT-CITY                      PIC X(20).
          03 PT-UMT-STATE-CODE                PIC X(2).
          03 PT-UMT-ZIP-CODE                  PIC X(9).
          03 PT-UMT-PHONE                     PIC X(14).
          03 PT-UMT-AGENCY-CODE               PIC X(6).
          03 PT-UMT-AGENT-NAME                PIC X(30).
