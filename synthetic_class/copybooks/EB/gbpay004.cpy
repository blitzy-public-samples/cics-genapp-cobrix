******************************************************************
*  COPYBOOK  : GBPAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : PA
******************************************************************
 01  PT-BPA-PARTY.

          03 PT-BPA-INSURED-NAME              PIC X(40).
          03 PT-BPA-TAX-ID                    PIC X(11).
          03 PT-BPA-ADDRESS-LINE1             PIC X(30).
          03 PT-BPA-ADDRESS-LINE2             PIC X(30).
          03 PT-BPA-CITY                      PIC X(20).
          03 PT-BPA-STATE-CODE                PIC X(2).
          03 PT-BPA-ZIP-CODE                  PIC X(9).
          03 PT-BPA-PHONE                     PIC X(14).
          03 PT-BPA-AGENCY-CODE               PIC X(6).
          03 PT-BPA-AGENT-NAME                PIC X(30).
