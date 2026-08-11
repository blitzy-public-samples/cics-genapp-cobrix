******************************************************************
*  COPYBOOK  : GCMOY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MO
******************************************************************
 01  PT-CMO-PARTY.

          03 PT-CMO-INSURED-NAME              PIC X(40).
          03 PT-CMO-TAX-ID                    PIC X(11).
          03 PT-CMO-ADDRESS-LINE1             PIC X(30).
          03 PT-CMO-ADDRESS-LINE2             PIC X(30).
          03 PT-CMO-CITY                      PIC X(20).
          03 PT-CMO-STATE-CODE                PIC X(2).
          03 PT-CMO-ZIP-CODE                  PIC X(9).
          03 PT-CMO-PHONE                     PIC X(14).
          03 PT-CMO-AGENCY-CODE               PIC X(6).
          03 PT-CMO-AGENT-NAME                PIC X(30).
