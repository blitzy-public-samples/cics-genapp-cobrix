******************************************************************
*  COPYBOOK  : GFPAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : PA
******************************************************************
 01  PT-FPA-PARTY.

          03 PT-FPA-INSURED-NAME              PIC X(40).
          03 PT-FPA-TAX-ID                    PIC X(11).
          03 PT-FPA-ADDRESS-LINE1             PIC X(30).
          03 PT-FPA-ADDRESS-LINE2             PIC X(30).
          03 PT-FPA-CITY                      PIC X(20).
          03 PT-FPA-STATE-CODE                PIC X(2).
          03 PT-FPA-ZIP-CODE                  PIC X(9).
          03 PT-FPA-PHONE                     PIC X(14).
          03 PT-FPA-AGENCY-CODE               PIC X(6).
          03 PT-FPA-AGENT-NAME                PIC X(30).
