******************************************************************
*  COPYBOOK  : GUPAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : PA
******************************************************************
 01  PT-UPA-PARTY.

          03 PT-UPA-INSURED-NAME              PIC X(40).
          03 PT-UPA-TAX-ID                    PIC X(11).
          03 PT-UPA-ADDRESS-LINE1             PIC X(30).
          03 PT-UPA-ADDRESS-LINE2             PIC X(30).
          03 PT-UPA-CITY                      PIC X(20).
          03 PT-UPA-STATE-CODE                PIC X(2).
          03 PT-UPA-ZIP-CODE                  PIC X(9).
          03 PT-UPA-PHONE                     PIC X(14).
          03 PT-UPA-AGENCY-CODE               PIC X(6).
          03 PT-UPA-AGENT-NAME                PIC X(30).
