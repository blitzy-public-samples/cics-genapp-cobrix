******************************************************************
*  COPYBOOK  : GUIDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : ID
******************************************************************
 01  PT-UID-PARTY.

          03 PT-UID-INSURED-NAME              PIC X(40).
          03 PT-UID-TAX-ID                    PIC X(11).
          03 PT-UID-ADDRESS-LINE1             PIC X(30).
          03 PT-UID-ADDRESS-LINE2             PIC X(30).
          03 PT-UID-CITY                      PIC X(20).
          03 PT-UID-STATE-CODE                PIC X(2).
          03 PT-UID-ZIP-CODE                  PIC X(9).
          03 PT-UID-PHONE                     PIC X(14).
          03 PT-UID-AGENCY-CODE               PIC X(6).
          03 PT-UID-AGENT-NAME                PIC X(30).
