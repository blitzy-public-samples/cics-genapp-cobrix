******************************************************************
*  COPYBOOK  : GRNMY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NM
******************************************************************
 01  PT-RNM-PARTY.

          03 PT-RNM-INSURED-NAME              PIC X(40).
          03 PT-RNM-TAX-ID                    PIC X(11).
          03 PT-RNM-ADDRESS-LINE1             PIC X(30).
          03 PT-RNM-ADDRESS-LINE2             PIC X(30).
          03 PT-RNM-CITY                      PIC X(20).
          03 PT-RNM-STATE-CODE                PIC X(2).
          03 PT-RNM-ZIP-CODE                  PIC X(9).
          03 PT-RNM-PHONE                     PIC X(14).
          03 PT-RNM-AGENCY-CODE               PIC X(6).
          03 PT-RNM-AGENT-NAME                PIC X(30).
