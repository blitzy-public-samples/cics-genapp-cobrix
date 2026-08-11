******************************************************************
*  COPYBOOK  : GUALY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : AL
******************************************************************
 01  PT-UAL-PARTY.

          03 PT-UAL-INSURED-NAME              PIC X(40).
          03 PT-UAL-TAX-ID                    PIC X(11).
          03 PT-UAL-ADDRESS-LINE1             PIC X(30).
          03 PT-UAL-ADDRESS-LINE2             PIC X(30).
          03 PT-UAL-CITY                      PIC X(20).
          03 PT-UAL-STATE-CODE                PIC X(2).
          03 PT-UAL-ZIP-CODE                  PIC X(9).
          03 PT-UAL-PHONE                     PIC X(14).
          03 PT-UAL-AGENCY-CODE               PIC X(6).
          03 PT-UAL-AGENT-NAME                PIC X(30).
