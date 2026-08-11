******************************************************************
*  COPYBOOK  : GASDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : SD
******************************************************************
 01  PT-ASD-PARTY.

          03 PT-ASD-INSURED-NAME              PIC X(40).
          03 PT-ASD-TAX-ID                    PIC X(11).
          03 PT-ASD-ADDRESS-LINE1             PIC X(30).
          03 PT-ASD-ADDRESS-LINE2             PIC X(30).
          03 PT-ASD-CITY                      PIC X(20).
          03 PT-ASD-STATE-CODE                PIC X(2).
          03 PT-ASD-ZIP-CODE                  PIC X(9).
          03 PT-ASD-PHONE                     PIC X(14).
          03 PT-ASD-AGENCY-CODE               PIC X(6).
          03 PT-ASD-AGENT-NAME                PIC X(30).
