******************************************************************
*  COPYBOOK  : GHIDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : ID
******************************************************************
 01  PT-HID-PARTY.

          03 PT-HID-INSURED-NAME              PIC X(40).
          03 PT-HID-TAX-ID                    PIC X(11).
          03 PT-HID-ADDRESS-LINE1             PIC X(30).
          03 PT-HID-ADDRESS-LINE2             PIC X(30).
          03 PT-HID-CITY                      PIC X(20).
          03 PT-HID-STATE-CODE                PIC X(2).
          03 PT-HID-ZIP-CODE                  PIC X(9).
          03 PT-HID-PHONE                     PIC X(14).
          03 PT-HID-AGENCY-CODE               PIC X(6).
          03 PT-HID-AGENT-NAME                PIC X(30).
