******************************************************************
*  COPYBOOK  : GMDCY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : DC
******************************************************************
 01  PT-MDC-PARTY.

          03 PT-MDC-INSURED-NAME              PIC X(40).
          03 PT-MDC-TAX-ID                    PIC X(11).
          03 PT-MDC-ADDRESS-LINE1             PIC X(30).
          03 PT-MDC-ADDRESS-LINE2             PIC X(30).
          03 PT-MDC-CITY                      PIC X(20).
          03 PT-MDC-STATE-CODE                PIC X(2).
          03 PT-MDC-ZIP-CODE                  PIC X(9).
          03 PT-MDC-PHONE                     PIC X(14).
          03 PT-MDC-AGENCY-CODE               PIC X(6).
          03 PT-MDC-AGENT-NAME                PIC X(30).
