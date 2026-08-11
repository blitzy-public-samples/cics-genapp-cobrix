******************************************************************
*  COPYBOOK  : GCMTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MT
******************************************************************
 01  PT-CMT-PARTY.

          03 PT-CMT-INSURED-NAME              PIC X(40).
          03 PT-CMT-TAX-ID                    PIC X(11).
          03 PT-CMT-ADDRESS-LINE1             PIC X(30).
          03 PT-CMT-ADDRESS-LINE2             PIC X(30).
          03 PT-CMT-CITY                      PIC X(20).
          03 PT-CMT-STATE-CODE                PIC X(2).
          03 PT-CMT-ZIP-CODE                  PIC X(9).
          03 PT-CMT-PHONE                     PIC X(14).
          03 PT-CMT-AGENCY-CODE               PIC X(6).
          03 PT-CMT-AGENT-NAME                PIC X(30).
