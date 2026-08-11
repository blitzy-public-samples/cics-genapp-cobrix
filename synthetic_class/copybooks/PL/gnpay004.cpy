******************************************************************
*  COPYBOOK  : GNPAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : PA
******************************************************************
 01  PT-NPA-PARTY.

          03 PT-NPA-INSURED-NAME              PIC X(40).
          03 PT-NPA-TAX-ID                    PIC X(11).
          03 PT-NPA-ADDRESS-LINE1             PIC X(30).
          03 PT-NPA-ADDRESS-LINE2             PIC X(30).
          03 PT-NPA-CITY                      PIC X(20).
          03 PT-NPA-STATE-CODE                PIC X(2).
          03 PT-NPA-ZIP-CODE                  PIC X(9).
          03 PT-NPA-PHONE                     PIC X(14).
          03 PT-NPA-AGENCY-CODE               PIC X(6).
          03 PT-NPA-AGENT-NAME                PIC X(30).
