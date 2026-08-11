******************************************************************
*  COPYBOOK  : GOVTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : VT
******************************************************************
 01  PT-OVT-PARTY.

          03 PT-OVT-INSURED-NAME              PIC X(40).
          03 PT-OVT-TAX-ID                    PIC X(11).
          03 PT-OVT-ADDRESS-LINE1             PIC X(30).
          03 PT-OVT-ADDRESS-LINE2             PIC X(30).
          03 PT-OVT-CITY                      PIC X(20).
          03 PT-OVT-STATE-CODE                PIC X(2).
          03 PT-OVT-ZIP-CODE                  PIC X(9).
          03 PT-OVT-PHONE                     PIC X(14).
          03 PT-OVT-AGENCY-CODE               PIC X(6).
          03 PT-OVT-AGENT-NAME                PIC X(30).
