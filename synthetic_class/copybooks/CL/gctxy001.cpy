******************************************************************
*  COPYBOOK  : GCTXY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : TX
******************************************************************
 01  PT-CTX-PARTY.

          03 PT-CTX-INSURED-NAME              PIC X(40).
          03 PT-CTX-TAX-ID                    PIC X(11).
          03 PT-CTX-ADDRESS-LINE1             PIC X(30).
          03 PT-CTX-ADDRESS-LINE2             PIC X(30).
          03 PT-CTX-CITY                      PIC X(20).
          03 PT-CTX-STATE-CODE                PIC X(2).
          03 PT-CTX-ZIP-CODE                  PIC X(9).
          03 PT-CTX-PHONE                     PIC X(14).
          03 PT-CTX-AGENCY-CODE               PIC X(6).
          03 PT-CTX-AGENT-NAME                PIC X(30).
