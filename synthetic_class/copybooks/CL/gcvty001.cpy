******************************************************************
*  COPYBOOK  : GCVTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : VT
******************************************************************
 01  PT-CVT-PARTY.

          03 PT-CVT-INSURED-NAME              PIC X(40).
          03 PT-CVT-TAX-ID                    PIC X(11).
          03 PT-CVT-ADDRESS-LINE1             PIC X(30).
          03 PT-CVT-ADDRESS-LINE2             PIC X(30).
          03 PT-CVT-CITY                      PIC X(20).
          03 PT-CVT-STATE-CODE                PIC X(2).
          03 PT-CVT-ZIP-CODE                  PIC X(9).
          03 PT-CVT-PHONE                     PIC X(14).
          03 PT-CVT-AGENCY-CODE               PIC X(6).
          03 PT-CVT-AGENT-NAME                PIC X(30).
