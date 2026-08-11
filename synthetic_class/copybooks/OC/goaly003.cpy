******************************************************************
*  COPYBOOK  : GOALY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : AL
******************************************************************
 01  PT-OAL-PARTY.

          03 PT-OAL-INSURED-NAME              PIC X(40).
          03 PT-OAL-TAX-ID                    PIC X(11).
          03 PT-OAL-ADDRESS-LINE1             PIC X(30).
          03 PT-OAL-ADDRESS-LINE2             PIC X(30).
          03 PT-OAL-CITY                      PIC X(20).
          03 PT-OAL-STATE-CODE                PIC X(2).
          03 PT-OAL-ZIP-CODE                  PIC X(9).
          03 PT-OAL-PHONE                     PIC X(14).
          03 PT-OAL-AGENCY-CODE               PIC X(6).
          03 PT-OAL-AGENT-NAME                PIC X(30).
