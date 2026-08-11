******************************************************************
*  COPYBOOK  : GOMDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : MD
******************************************************************
 01  PT-OMD-PARTY.

          03 PT-OMD-INSURED-NAME              PIC X(40).
          03 PT-OMD-TAX-ID                    PIC X(11).
          03 PT-OMD-ADDRESS-LINE1             PIC X(30).
          03 PT-OMD-ADDRESS-LINE2             PIC X(30).
          03 PT-OMD-CITY                      PIC X(20).
          03 PT-OMD-STATE-CODE                PIC X(2).
          03 PT-OMD-ZIP-CODE                  PIC X(9).
          03 PT-OMD-PHONE                     PIC X(14).
          03 PT-OMD-AGENCY-CODE               PIC X(6).
          03 PT-OMD-AGENT-NAME                PIC X(30).
