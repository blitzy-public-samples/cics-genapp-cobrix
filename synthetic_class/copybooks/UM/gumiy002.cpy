******************************************************************
*  COPYBOOK  : GUMIY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MI
******************************************************************
 01  PT-UMI-PARTY.

          03 PT-UMI-INSURED-NAME              PIC X(40).
          03 PT-UMI-TAX-ID                    PIC X(11).
          03 PT-UMI-ADDRESS-LINE1             PIC X(30).
          03 PT-UMI-ADDRESS-LINE2             PIC X(30).
          03 PT-UMI-CITY                      PIC X(20).
          03 PT-UMI-STATE-CODE                PIC X(2).
          03 PT-UMI-ZIP-CODE                  PIC X(9).
          03 PT-UMI-PHONE                     PIC X(14).
          03 PT-UMI-AGENCY-CODE               PIC X(6).
          03 PT-UMI-AGENT-NAME                PIC X(30).
