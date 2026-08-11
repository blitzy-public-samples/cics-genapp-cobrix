******************************************************************
*  COPYBOOK  : GRSCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : SC
******************************************************************
 01  PT-RSC-PARTY.

          03 PT-RSC-INSURED-NAME              PIC X(40).
          03 PT-RSC-TAX-ID                    PIC X(11).
          03 PT-RSC-ADDRESS-LINE1             PIC X(30).
          03 PT-RSC-ADDRESS-LINE2             PIC X(30).
          03 PT-RSC-CITY                      PIC X(20).
          03 PT-RSC-STATE-CODE                PIC X(2).
          03 PT-RSC-ZIP-CODE                  PIC X(9).
          03 PT-RSC-PHONE                     PIC X(14).
          03 PT-RSC-AGENCY-CODE               PIC X(6).
          03 PT-RSC-AGENT-NAME                PIC X(30).
