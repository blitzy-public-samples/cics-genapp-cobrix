******************************************************************
*  COPYBOOK  : GHNDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : ND
******************************************************************
 01  PT-HND-PARTY.

          03 PT-HND-INSURED-NAME              PIC X(40).
          03 PT-HND-TAX-ID                    PIC X(11).
          03 PT-HND-ADDRESS-LINE1             PIC X(30).
          03 PT-HND-ADDRESS-LINE2             PIC X(30).
          03 PT-HND-CITY                      PIC X(20).
          03 PT-HND-STATE-CODE                PIC X(2).
          03 PT-HND-ZIP-CODE                  PIC X(9).
          03 PT-HND-PHONE                     PIC X(14).
          03 PT-HND-AGENCY-CODE               PIC X(6).
          03 PT-HND-AGENT-NAME                PIC X(30).
