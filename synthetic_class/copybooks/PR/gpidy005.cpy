******************************************************************
*  COPYBOOK  : GPIDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : ID
******************************************************************
 01  PT-PID-PARTY.

          03 PT-PID-INSURED-NAME              PIC X(40).
          03 PT-PID-TAX-ID                    PIC X(11).
          03 PT-PID-ADDRESS-LINE1             PIC X(30).
          03 PT-PID-ADDRESS-LINE2             PIC X(30).
          03 PT-PID-CITY                      PIC X(20).
          03 PT-PID-STATE-CODE                PIC X(2).
          03 PT-PID-ZIP-CODE                  PIC X(9).
          03 PT-PID-PHONE                     PIC X(14).
          03 PT-PID-AGENCY-CODE               PIC X(6).
          03 PT-PID-AGENT-NAME                PIC X(30).
