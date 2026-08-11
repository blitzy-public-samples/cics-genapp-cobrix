******************************************************************
*  COPYBOOK  : GPINY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : IN
******************************************************************
 01  PT-PIN-PARTY.

          03 PT-PIN-INSURED-NAME              PIC X(40).
          03 PT-PIN-TAX-ID                    PIC X(11).
          03 PT-PIN-ADDRESS-LINE1             PIC X(30).
          03 PT-PIN-ADDRESS-LINE2             PIC X(30).
          03 PT-PIN-CITY                      PIC X(20).
          03 PT-PIN-STATE-CODE                PIC X(2).
          03 PT-PIN-ZIP-CODE                  PIC X(9).
          03 PT-PIN-PHONE                     PIC X(14).
          03 PT-PIN-AGENCY-CODE               PIC X(6).
          03 PT-PIN-AGENT-NAME                PIC X(30).
