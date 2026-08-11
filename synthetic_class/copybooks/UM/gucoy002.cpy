******************************************************************
*  COPYBOOK  : GUCOY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : CO
******************************************************************
 01  PT-UCO-PARTY.

          03 PT-UCO-INSURED-NAME              PIC X(40).
          03 PT-UCO-TAX-ID                    PIC X(11).
          03 PT-UCO-ADDRESS-LINE1             PIC X(30).
          03 PT-UCO-ADDRESS-LINE2             PIC X(30).
          03 PT-UCO-CITY                      PIC X(20).
          03 PT-UCO-STATE-CODE                PIC X(2).
          03 PT-UCO-ZIP-CODE                  PIC X(9).
          03 PT-UCO-PHONE                     PIC X(14).
          03 PT-UCO-AGENCY-CODE               PIC X(6).
          03 PT-UCO-AGENT-NAME                PIC X(30).
