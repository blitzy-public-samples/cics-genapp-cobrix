******************************************************************
*  COPYBOOK  : GMHIY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : HI
******************************************************************
 01  PT-MHI-PARTY.

          03 PT-MHI-INSURED-NAME              PIC X(40).
          03 PT-MHI-TAX-ID                    PIC X(11).
          03 PT-MHI-ADDRESS-LINE1             PIC X(30).
          03 PT-MHI-ADDRESS-LINE2             PIC X(30).
          03 PT-MHI-CITY                      PIC X(20).
          03 PT-MHI-STATE-CODE                PIC X(2).
          03 PT-MHI-ZIP-CODE                  PIC X(9).
          03 PT-MHI-PHONE                     PIC X(14).
          03 PT-MHI-AGENCY-CODE               PIC X(6).
          03 PT-MHI-AGENT-NAME                PIC X(30).
