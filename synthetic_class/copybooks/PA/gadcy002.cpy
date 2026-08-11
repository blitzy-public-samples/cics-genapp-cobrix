******************************************************************
*  COPYBOOK  : GADCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : DC
******************************************************************
 01  PT-ADC-PARTY.

          03 PT-ADC-INSURED-NAME              PIC X(40).
          03 PT-ADC-TAX-ID                    PIC X(11).
          03 PT-ADC-ADDRESS-LINE1             PIC X(30).
          03 PT-ADC-ADDRESS-LINE2             PIC X(30).
          03 PT-ADC-CITY                      PIC X(20).
          03 PT-ADC-STATE-CODE                PIC X(2).
          03 PT-ADC-ZIP-CODE                  PIC X(9).
          03 PT-ADC-PHONE                     PIC X(14).
          03 PT-ADC-AGENCY-CODE               PIC X(6).
          03 PT-ADC-AGENT-NAME                PIC X(30).
