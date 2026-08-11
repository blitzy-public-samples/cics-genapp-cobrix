******************************************************************
*  COPYBOOK  : GHPAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : PA
******************************************************************
 01  PT-HPA-PARTY.

          03 PT-HPA-INSURED-NAME              PIC X(40).
          03 PT-HPA-TAX-ID                    PIC X(11).
          03 PT-HPA-ADDRESS-LINE1             PIC X(30).
          03 PT-HPA-ADDRESS-LINE2             PIC X(30).
          03 PT-HPA-CITY                      PIC X(20).
          03 PT-HPA-STATE-CODE                PIC X(2).
          03 PT-HPA-ZIP-CODE                  PIC X(9).
          03 PT-HPA-PHONE                     PIC X(14).
          03 PT-HPA-AGENCY-CODE               PIC X(6).
          03 PT-HPA-AGENT-NAME                PIC X(30).
