******************************************************************
*  COPYBOOK  : GNMSY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : MS
******************************************************************
 01  PT-NMS-PARTY.

          03 PT-NMS-INSURED-NAME              PIC X(40).
          03 PT-NMS-TAX-ID                    PIC X(11).
          03 PT-NMS-ADDRESS-LINE1             PIC X(30).
          03 PT-NMS-ADDRESS-LINE2             PIC X(30).
          03 PT-NMS-CITY                      PIC X(20).
          03 PT-NMS-STATE-CODE                PIC X(2).
          03 PT-NMS-ZIP-CODE                  PIC X(9).
          03 PT-NMS-PHONE                     PIC X(14).
          03 PT-NMS-AGENCY-CODE               PIC X(6).
          03 PT-NMS-AGENT-NAME                PIC X(30).
