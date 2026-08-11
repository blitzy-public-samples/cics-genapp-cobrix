******************************************************************
*  COPYBOOK  : GCNVY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : NV
******************************************************************
 01  PT-CNV-PARTY.

          03 PT-CNV-INSURED-NAME              PIC X(40).
          03 PT-CNV-TAX-ID                    PIC X(11).
          03 PT-CNV-ADDRESS-LINE1             PIC X(30).
          03 PT-CNV-ADDRESS-LINE2             PIC X(30).
          03 PT-CNV-CITY                      PIC X(20).
          03 PT-CNV-STATE-CODE                PIC X(2).
          03 PT-CNV-ZIP-CODE                  PIC X(9).
          03 PT-CNV-PHONE                     PIC X(14).
          03 PT-CNV-AGENCY-CODE               PIC X(6).
          03 PT-CNV-AGENT-NAME                PIC X(30).
