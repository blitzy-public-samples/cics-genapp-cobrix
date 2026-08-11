******************************************************************
*  COPYBOOK  : GHNVY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : NV
******************************************************************
 01  PT-HNV-PARTY.

          03 PT-HNV-INSURED-NAME              PIC X(40).
          03 PT-HNV-TAX-ID                    PIC X(11).
          03 PT-HNV-ADDRESS-LINE1             PIC X(30).
          03 PT-HNV-ADDRESS-LINE2             PIC X(30).
          03 PT-HNV-CITY                      PIC X(20).
          03 PT-HNV-STATE-CODE                PIC X(2).
          03 PT-HNV-ZIP-CODE                  PIC X(9).
          03 PT-HNV-PHONE                     PIC X(14).
          03 PT-HNV-AGENCY-CODE               PIC X(6).
          03 PT-HNV-AGENT-NAME                PIC X(30).
