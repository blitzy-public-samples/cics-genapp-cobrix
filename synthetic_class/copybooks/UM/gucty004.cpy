******************************************************************
*  COPYBOOK  : GUCTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : CT
******************************************************************
 01  PT-UCT-PARTY.

          03 PT-UCT-INSURED-NAME              PIC X(40).
          03 PT-UCT-TAX-ID                    PIC X(11).
          03 PT-UCT-ADDRESS-LINE1             PIC X(30).
          03 PT-UCT-ADDRESS-LINE2             PIC X(30).
          03 PT-UCT-CITY                      PIC X(20).
          03 PT-UCT-STATE-CODE                PIC X(2).
          03 PT-UCT-ZIP-CODE                  PIC X(9).
          03 PT-UCT-PHONE                     PIC X(14).
          03 PT-UCT-AGENCY-CODE               PIC X(6).
          03 PT-UCT-AGENT-NAME                PIC X(30).
