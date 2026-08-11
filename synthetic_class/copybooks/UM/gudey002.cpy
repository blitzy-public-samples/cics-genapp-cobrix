******************************************************************
*  COPYBOOK  : GUDEY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : DE
******************************************************************
 01  PT-UDE-PARTY.

          03 PT-UDE-INSURED-NAME              PIC X(40).
          03 PT-UDE-TAX-ID                    PIC X(11).
          03 PT-UDE-ADDRESS-LINE1             PIC X(30).
          03 PT-UDE-ADDRESS-LINE2             PIC X(30).
          03 PT-UDE-CITY                      PIC X(20).
          03 PT-UDE-STATE-CODE                PIC X(2).
          03 PT-UDE-ZIP-CODE                  PIC X(9).
          03 PT-UDE-PHONE                     PIC X(14).
          03 PT-UDE-AGENCY-CODE               PIC X(6).
          03 PT-UDE-AGENT-NAME                PIC X(30).
