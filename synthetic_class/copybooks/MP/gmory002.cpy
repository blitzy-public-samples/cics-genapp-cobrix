******************************************************************
*  COPYBOOK  : GMORY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : OR
******************************************************************
 01  PT-MOR-PARTY.

          03 PT-MOR-INSURED-NAME              PIC X(40).
          03 PT-MOR-TAX-ID                    PIC X(11).
          03 PT-MOR-ADDRESS-LINE1             PIC X(30).
          03 PT-MOR-ADDRESS-LINE2             PIC X(30).
          03 PT-MOR-CITY                      PIC X(20).
          03 PT-MOR-STATE-CODE                PIC X(2).
          03 PT-MOR-ZIP-CODE                  PIC X(9).
          03 PT-MOR-PHONE                     PIC X(14).
          03 PT-MOR-AGENCY-CODE               PIC X(6).
          03 PT-MOR-AGENT-NAME                PIC X(30).
