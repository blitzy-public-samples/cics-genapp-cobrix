******************************************************************
*  COPYBOOK  : GCSDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : SD
******************************************************************
 01  PT-CSD-PARTY.

          03 PT-CSD-INSURED-NAME              PIC X(40).
          03 PT-CSD-TAX-ID                    PIC X(11).
          03 PT-CSD-ADDRESS-LINE1             PIC X(30).
          03 PT-CSD-ADDRESS-LINE2             PIC X(30).
          03 PT-CSD-CITY                      PIC X(20).
          03 PT-CSD-STATE-CODE                PIC X(2).
          03 PT-CSD-ZIP-CODE                  PIC X(9).
          03 PT-CSD-PHONE                     PIC X(14).
          03 PT-CSD-AGENCY-CODE               PIC X(6).
          03 PT-CSD-AGENT-NAME                PIC X(30).
