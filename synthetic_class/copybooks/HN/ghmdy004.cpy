******************************************************************
*  COPYBOOK  : GHMDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : MD
******************************************************************
 01  PT-HMD-PARTY.

          03 PT-HMD-INSURED-NAME              PIC X(40).
          03 PT-HMD-TAX-ID                    PIC X(11).
          03 PT-HMD-ADDRESS-LINE1             PIC X(30).
          03 PT-HMD-ADDRESS-LINE2             PIC X(30).
          03 PT-HMD-CITY                      PIC X(20).
          03 PT-HMD-STATE-CODE                PIC X(2).
          03 PT-HMD-ZIP-CODE                  PIC X(9).
          03 PT-HMD-PHONE                     PIC X(14).
          03 PT-HMD-AGENCY-CODE               PIC X(6).
          03 PT-HMD-AGENT-NAME                PIC X(30).
