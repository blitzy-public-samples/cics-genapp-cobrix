******************************************************************
*  COPYBOOK  : GCIDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : ID
******************************************************************
 01  PT-CID-PARTY.

          03 PT-CID-INSURED-NAME              PIC X(40).
          03 PT-CID-TAX-ID                    PIC X(11).
          03 PT-CID-ADDRESS-LINE1             PIC X(30).
          03 PT-CID-ADDRESS-LINE2             PIC X(30).
          03 PT-CID-CITY                      PIC X(20).
          03 PT-CID-STATE-CODE                PIC X(2).
          03 PT-CID-ZIP-CODE                  PIC X(9).
          03 PT-CID-PHONE                     PIC X(14).
          03 PT-CID-AGENCY-CODE               PIC X(6).
          03 PT-CID-AGENT-NAME                PIC X(30).
