******************************************************************
*  COPYBOOK  : GRTXY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : TX
******************************************************************
 01  PT-RTX-PARTY.

          03 PT-RTX-INSURED-NAME              PIC X(40).
          03 PT-RTX-TAX-ID                    PIC X(11).
          03 PT-RTX-ADDRESS-LINE1             PIC X(30).
          03 PT-RTX-ADDRESS-LINE2             PIC X(30).
          03 PT-RTX-CITY                      PIC X(20).
          03 PT-RTX-STATE-CODE                PIC X(2).
          03 PT-RTX-ZIP-CODE                  PIC X(9).
          03 PT-RTX-PHONE                     PIC X(14).
          03 PT-RTX-AGENCY-CODE               PIC X(6).
          03 PT-RTX-AGENT-NAME                PIC X(30).
