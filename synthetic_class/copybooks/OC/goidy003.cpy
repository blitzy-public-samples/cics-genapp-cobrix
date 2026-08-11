******************************************************************
*  COPYBOOK  : GOIDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : ID
******************************************************************
 01  PT-OID-PARTY.

          03 PT-OID-INSURED-NAME              PIC X(40).
          03 PT-OID-TAX-ID                    PIC X(11).
          03 PT-OID-ADDRESS-LINE1             PIC X(30).
          03 PT-OID-ADDRESS-LINE2             PIC X(30).
          03 PT-OID-CITY                      PIC X(20).
          03 PT-OID-STATE-CODE                PIC X(2).
          03 PT-OID-ZIP-CODE                  PIC X(9).
          03 PT-OID-PHONE                     PIC X(14).
          03 PT-OID-AGENCY-CODE               PIC X(6).
          03 PT-OID-AGENT-NAME                PIC X(30).
