******************************************************************
*  COPYBOOK  : GMSDY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Medical Payments (MP)
*  STATE     : SD
******************************************************************
 01  PT-MSD-PARTY.

          03 PT-MSD-INSURED-NAME              PIC X(40).
          03 PT-MSD-TAX-ID                    PIC X(11).
          03 PT-MSD-ADDRESS-LINE1             PIC X(30).
          03 PT-MSD-ADDRESS-LINE2             PIC X(30).
          03 PT-MSD-CITY                      PIC X(20).
          03 PT-MSD-STATE-CODE                PIC X(2).
          03 PT-MSD-ZIP-CODE                  PIC X(9).
          03 PT-MSD-PHONE                     PIC X(14).
          03 PT-MSD-AGENCY-CODE               PIC X(6).
          03 PT-MSD-AGENT-NAME                PIC X(30).
