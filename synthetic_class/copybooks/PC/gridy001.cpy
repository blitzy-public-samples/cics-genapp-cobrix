******************************************************************
*  COPYBOOK  : GRIDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : ID
******************************************************************
 01  PT-RID-PARTY.

          03 PT-RID-INSURED-NAME              PIC X(40).
          03 PT-RID-TAX-ID                    PIC X(11).
          03 PT-RID-ADDRESS-LINE1             PIC X(30).
          03 PT-RID-ADDRESS-LINE2             PIC X(30).
          03 PT-RID-CITY                      PIC X(20).
          03 PT-RID-STATE-CODE                PIC X(2).
          03 PT-RID-ZIP-CODE                  PIC X(9).
          03 PT-RID-PHONE                     PIC X(14).
          03 PT-RID-AGENCY-CODE               PIC X(6).
          03 PT-RID-AGENT-NAME                PIC X(30).
