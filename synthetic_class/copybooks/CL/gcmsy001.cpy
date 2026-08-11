******************************************************************
*  COPYBOOK  : GCMSY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MS
******************************************************************
 01  PT-CMS-PARTY.

          03 PT-CMS-INSURED-NAME              PIC X(40).
          03 PT-CMS-TAX-ID                    PIC X(11).
          03 PT-CMS-ADDRESS-LINE1             PIC X(30).
          03 PT-CMS-ADDRESS-LINE2             PIC X(30).
          03 PT-CMS-CITY                      PIC X(20).
          03 PT-CMS-STATE-CODE                PIC X(2).
          03 PT-CMS-ZIP-CODE                  PIC X(9).
          03 PT-CMS-PHONE                     PIC X(14).
          03 PT-CMS-AGENCY-CODE               PIC X(6).
          03 PT-CMS-AGENT-NAME                PIC X(30).
