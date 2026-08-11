******************************************************************
*  COPYBOOK  : GMVAY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : VA
******************************************************************
 01  PT-MVA-PARTY.

          03 PT-MVA-INSURED-NAME              PIC X(40).
          03 PT-MVA-TAX-ID                    PIC X(11).
          03 PT-MVA-ADDRESS-LINE1             PIC X(30).
          03 PT-MVA-ADDRESS-LINE2             PIC X(30).
          03 PT-MVA-CITY                      PIC X(20).
          03 PT-MVA-STATE-CODE                PIC X(2).
          03 PT-MVA-ZIP-CODE                  PIC X(9).
          03 PT-MVA-PHONE                     PIC X(14).
          03 PT-MVA-AGENCY-CODE               PIC X(6).
          03 PT-MVA-AGENT-NAME                PIC X(30).
