******************************************************************
*  COPYBOOK  : GCDCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : DC
******************************************************************
 01  PT-CDC-PARTY.

          03 PT-CDC-INSURED-NAME              PIC X(40).
          03 PT-CDC-TAX-ID                    PIC X(11).
          03 PT-CDC-ADDRESS-LINE1             PIC X(30).
          03 PT-CDC-ADDRESS-LINE2             PIC X(30).
          03 PT-CDC-CITY                      PIC X(20).
          03 PT-CDC-STATE-CODE                PIC X(2).
          03 PT-CDC-ZIP-CODE                  PIC X(9).
          03 PT-CDC-PHONE                     PIC X(14).
          03 PT-CDC-AGENCY-CODE               PIC X(6).
          03 PT-CDC-AGENT-NAME                PIC X(30).
