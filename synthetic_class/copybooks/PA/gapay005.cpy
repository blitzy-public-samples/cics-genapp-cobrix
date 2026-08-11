******************************************************************
*  COPYBOOK  : GAPAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : PA
******************************************************************
 01  PT-APA-PARTY.

          03 PT-APA-INSURED-NAME              PIC X(40).
          03 PT-APA-TAX-ID                    PIC X(11).
          03 PT-APA-ADDRESS-LINE1             PIC X(30).
          03 PT-APA-ADDRESS-LINE2             PIC X(30).
          03 PT-APA-CITY                      PIC X(20).
          03 PT-APA-STATE-CODE                PIC X(2).
          03 PT-APA-ZIP-CODE                  PIC X(9).
          03 PT-APA-PHONE                     PIC X(14).
          03 PT-APA-AGENCY-CODE               PIC X(6).
          03 PT-APA-AGENT-NAME                PIC X(30).
