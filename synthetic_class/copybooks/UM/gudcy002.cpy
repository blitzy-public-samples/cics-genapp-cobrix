******************************************************************
*  COPYBOOK  : GUDCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : DC
******************************************************************
 01  PT-UDC-PARTY.

          03 PT-UDC-INSURED-NAME              PIC X(40).
          03 PT-UDC-TAX-ID                    PIC X(11).
          03 PT-UDC-ADDRESS-LINE1             PIC X(30).
          03 PT-UDC-ADDRESS-LINE2             PIC X(30).
          03 PT-UDC-CITY                      PIC X(20).
          03 PT-UDC-STATE-CODE                PIC X(2).
          03 PT-UDC-ZIP-CODE                  PIC X(9).
          03 PT-UDC-PHONE                     PIC X(14).
          03 PT-UDC-AGENCY-CODE               PIC X(6).
          03 PT-UDC-AGENT-NAME                PIC X(30).
