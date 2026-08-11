******************************************************************
*  COPYBOOK  : GAIDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : ID
******************************************************************
 01  PT-AID-PARTY.

          03 PT-AID-INSURED-NAME              PIC X(40).
          03 PT-AID-TAX-ID                    PIC X(11).
          03 PT-AID-ADDRESS-LINE1             PIC X(30).
          03 PT-AID-ADDRESS-LINE2             PIC X(30).
          03 PT-AID-CITY                      PIC X(20).
          03 PT-AID-STATE-CODE                PIC X(2).
          03 PT-AID-ZIP-CODE                  PIC X(9).
          03 PT-AID-PHONE                     PIC X(14).
          03 PT-AID-AGENCY-CODE               PIC X(6).
          03 PT-AID-AGENT-NAME                PIC X(30).
