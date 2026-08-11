******************************************************************
*  COPYBOOK  : GUORY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : OR
******************************************************************
 01  PT-UOR-PARTY.

          03 PT-UOR-INSURED-NAME              PIC X(40).
          03 PT-UOR-TAX-ID                    PIC X(11).
          03 PT-UOR-ADDRESS-LINE1             PIC X(30).
          03 PT-UOR-ADDRESS-LINE2             PIC X(30).
          03 PT-UOR-CITY                      PIC X(20).
          03 PT-UOR-STATE-CODE                PIC X(2).
          03 PT-UOR-ZIP-CODE                  PIC X(9).
          03 PT-UOR-PHONE                     PIC X(14).
          03 PT-UOR-AGENCY-CODE               PIC X(6).
          03 PT-UOR-AGENT-NAME                PIC X(30).
