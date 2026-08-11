******************************************************************
*  COPYBOOK  : GURIY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : RI
******************************************************************
 01  PT-URI-PARTY.

          03 PT-URI-INSURED-NAME              PIC X(40).
          03 PT-URI-TAX-ID                    PIC X(11).
          03 PT-URI-ADDRESS-LINE1             PIC X(30).
          03 PT-URI-ADDRESS-LINE2             PIC X(30).
          03 PT-URI-CITY                      PIC X(20).
          03 PT-URI-STATE-CODE                PIC X(2).
          03 PT-URI-ZIP-CODE                  PIC X(9).
          03 PT-URI-PHONE                     PIC X(14).
          03 PT-URI-AGENCY-CODE               PIC X(6).
          03 PT-URI-AGENT-NAME                PIC X(30).
