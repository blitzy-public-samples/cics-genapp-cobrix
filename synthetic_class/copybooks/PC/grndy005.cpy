******************************************************************
*  COPYBOOK  : GRNDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : ND
******************************************************************
 01  PT-RND-PARTY.

          03 PT-RND-INSURED-NAME              PIC X(40).
          03 PT-RND-TAX-ID                    PIC X(11).
          03 PT-RND-ADDRESS-LINE1             PIC X(30).
          03 PT-RND-ADDRESS-LINE2             PIC X(30).
          03 PT-RND-CITY                      PIC X(20).
          03 PT-RND-STATE-CODE                PIC X(2).
          03 PT-RND-ZIP-CODE                  PIC X(9).
          03 PT-RND-PHONE                     PIC X(14).
          03 PT-RND-AGENCY-CODE               PIC X(6).
          03 PT-RND-AGENT-NAME                PIC X(30).
