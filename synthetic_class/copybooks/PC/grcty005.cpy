******************************************************************
*  COPYBOOK  : GRCTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : CT
******************************************************************
 01  PT-RCT-PARTY.

          03 PT-RCT-INSURED-NAME              PIC X(40).
          03 PT-RCT-TAX-ID                    PIC X(11).
          03 PT-RCT-ADDRESS-LINE1             PIC X(30).
          03 PT-RCT-ADDRESS-LINE2             PIC X(30).
          03 PT-RCT-CITY                      PIC X(20).
          03 PT-RCT-STATE-CODE                PIC X(2).
          03 PT-RCT-ZIP-CODE                  PIC X(9).
          03 PT-RCT-PHONE                     PIC X(14).
          03 PT-RCT-AGENCY-CODE               PIC X(6).
          03 PT-RCT-AGENT-NAME                PIC X(30).
