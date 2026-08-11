******************************************************************
*  COPYBOOK  : GCNCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : NC
******************************************************************
 01  PT-CNC-PARTY.

          03 PT-CNC-INSURED-NAME              PIC X(40).
          03 PT-CNC-TAX-ID                    PIC X(11).
          03 PT-CNC-ADDRESS-LINE1             PIC X(30).
          03 PT-CNC-ADDRESS-LINE2             PIC X(30).
          03 PT-CNC-CITY                      PIC X(20).
          03 PT-CNC-STATE-CODE                PIC X(2).
          03 PT-CNC-ZIP-CODE                  PIC X(9).
          03 PT-CNC-PHONE                     PIC X(14).
          03 PT-CNC-AGENCY-CODE               PIC X(6).
          03 PT-CNC-AGENT-NAME                PIC X(30).
