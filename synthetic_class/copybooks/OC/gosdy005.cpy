******************************************************************
*  COPYBOOK  : GOSDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : SD
******************************************************************
 01  PT-OSD-PARTY.

          03 PT-OSD-INSURED-NAME              PIC X(40).
          03 PT-OSD-TAX-ID                    PIC X(11).
          03 PT-OSD-ADDRESS-LINE1             PIC X(30).
          03 PT-OSD-ADDRESS-LINE2             PIC X(30).
          03 PT-OSD-CITY                      PIC X(20).
          03 PT-OSD-STATE-CODE                PIC X(2).
          03 PT-OSD-ZIP-CODE                  PIC X(9).
          03 PT-OSD-PHONE                     PIC X(14).
          03 PT-OSD-AGENCY-CODE               PIC X(6).
          03 PT-OSD-AGENT-NAME                PIC X(30).
