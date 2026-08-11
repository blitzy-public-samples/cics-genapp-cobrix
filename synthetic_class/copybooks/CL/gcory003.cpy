******************************************************************
*  COPYBOOK  : GCORY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : OR
******************************************************************
 01  PT-COR-PARTY.

          03 PT-COR-INSURED-NAME              PIC X(40).
          03 PT-COR-TAX-ID                    PIC X(11).
          03 PT-COR-ADDRESS-LINE1             PIC X(30).
          03 PT-COR-ADDRESS-LINE2             PIC X(30).
          03 PT-COR-CITY                      PIC X(20).
          03 PT-COR-STATE-CODE                PIC X(2).
          03 PT-COR-ZIP-CODE                  PIC X(9).
          03 PT-COR-PHONE                     PIC X(14).
          03 PT-COR-AGENCY-CODE               PIC X(6).
          03 PT-COR-AGENT-NAME                PIC X(30).
