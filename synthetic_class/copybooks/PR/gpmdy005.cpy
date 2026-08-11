******************************************************************
*  COPYBOOK  : GPMDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : MD
******************************************************************
 01  PT-PMD-PARTY.

          03 PT-PMD-INSURED-NAME              PIC X(40).
          03 PT-PMD-TAX-ID                    PIC X(11).
          03 PT-PMD-ADDRESS-LINE1             PIC X(30).
          03 PT-PMD-ADDRESS-LINE2             PIC X(30).
          03 PT-PMD-CITY                      PIC X(20).
          03 PT-PMD-STATE-CODE                PIC X(2).
          03 PT-PMD-ZIP-CODE                  PIC X(9).
          03 PT-PMD-PHONE                     PIC X(14).
          03 PT-PMD-AGENCY-CODE               PIC X(6).
          03 PT-PMD-AGENT-NAME                PIC X(30).
