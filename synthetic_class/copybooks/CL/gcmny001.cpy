******************************************************************
*  COPYBOOK  : GCMNY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MN
******************************************************************
 01  PT-CMN-PARTY.

          03 PT-CMN-INSURED-NAME              PIC X(40).
          03 PT-CMN-TAX-ID                    PIC X(11).
          03 PT-CMN-ADDRESS-LINE1             PIC X(30).
          03 PT-CMN-ADDRESS-LINE2             PIC X(30).
          03 PT-CMN-CITY                      PIC X(20).
          03 PT-CMN-STATE-CODE                PIC X(2).
          03 PT-CMN-ZIP-CODE                  PIC X(9).
          03 PT-CMN-PHONE                     PIC X(14).
          03 PT-CMN-AGENCY-CODE               PIC X(6).
          03 PT-CMN-AGENT-NAME                PIC X(30).
