******************************************************************
*  COPYBOOK  : GRDCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : DC
******************************************************************
 01  PT-RDC-PARTY.

          03 PT-RDC-INSURED-NAME              PIC X(40).
          03 PT-RDC-TAX-ID                    PIC X(11).
          03 PT-RDC-ADDRESS-LINE1             PIC X(30).
          03 PT-RDC-ADDRESS-LINE2             PIC X(30).
          03 PT-RDC-CITY                      PIC X(20).
          03 PT-RDC-STATE-CODE                PIC X(2).
          03 PT-RDC-ZIP-CODE                  PIC X(9).
          03 PT-RDC-PHONE                     PIC X(14).
          03 PT-RDC-AGENCY-CODE               PIC X(6).
          03 PT-RDC-AGENT-NAME                PIC X(30).
