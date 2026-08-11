******************************************************************
*  COPYBOOK  : GOSCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : SC
******************************************************************
 01  PT-OSC-PARTY.

          03 PT-OSC-INSURED-NAME              PIC X(40).
          03 PT-OSC-TAX-ID                    PIC X(11).
          03 PT-OSC-ADDRESS-LINE1             PIC X(30).
          03 PT-OSC-ADDRESS-LINE2             PIC X(30).
          03 PT-OSC-CITY                      PIC X(20).
          03 PT-OSC-STATE-CODE                PIC X(2).
          03 PT-OSC-ZIP-CODE                  PIC X(9).
          03 PT-OSC-PHONE                     PIC X(14).
          03 PT-OSC-AGENCY-CODE               PIC X(6).
          03 PT-OSC-AGENT-NAME                PIC X(30).
