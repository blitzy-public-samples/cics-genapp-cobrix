******************************************************************
*  COPYBOOK  : GNDCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : DC
******************************************************************
 01  PT-NDC-PARTY.

          03 PT-NDC-INSURED-NAME              PIC X(40).
          03 PT-NDC-TAX-ID                    PIC X(11).
          03 PT-NDC-ADDRESS-LINE1             PIC X(30).
          03 PT-NDC-ADDRESS-LINE2             PIC X(30).
          03 PT-NDC-CITY                      PIC X(20).
          03 PT-NDC-STATE-CODE                PIC X(2).
          03 PT-NDC-ZIP-CODE                  PIC X(9).
          03 PT-NDC-PHONE                     PIC X(14).
          03 PT-NDC-AGENCY-CODE               PIC X(6).
          03 PT-NDC-AGENT-NAME                PIC X(30).
