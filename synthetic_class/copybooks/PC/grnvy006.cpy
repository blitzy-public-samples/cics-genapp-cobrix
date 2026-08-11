******************************************************************
*  COPYBOOK  : GRNVY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NV
******************************************************************
 01  PT-RNV-PARTY.

          03 PT-RNV-INSURED-NAME              PIC X(40).
          03 PT-RNV-TAX-ID                    PIC X(11).
          03 PT-RNV-ADDRESS-LINE1             PIC X(30).
          03 PT-RNV-ADDRESS-LINE2             PIC X(30).
          03 PT-RNV-CITY                      PIC X(20).
          03 PT-RNV-STATE-CODE                PIC X(2).
          03 PT-RNV-ZIP-CODE                  PIC X(9).
          03 PT-RNV-PHONE                     PIC X(14).
          03 PT-RNV-AGENCY-CODE               PIC X(6).
          03 PT-RNV-AGENT-NAME                PIC X(30).
