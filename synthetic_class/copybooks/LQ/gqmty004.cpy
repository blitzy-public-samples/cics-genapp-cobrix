******************************************************************
*  COPYBOOK  : GQMTY001
*  KIND      : PARTY-RECORD (named insured / agency)
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : MT
******************************************************************
 01  PT-QMT-PARTY.

          03 PT-QMT-INSURED-NAME              PIC X(40).
          03 PT-QMT-TAX-ID                    PIC X(11).
          03 PT-QMT-ADDRESS-LINE1             PIC X(30).
          03 PT-QMT-ADDRESS-LINE2             PIC X(30).
          03 PT-QMT-CITY                      PIC X(20).
          03 PT-QMT-STATE-CODE                PIC X(2).
          03 PT-QMT-ZIP-CODE                  PIC X(9).
          03 PT-QMT-PHONE                     PIC X(14).
          03 PT-QMT-AGENCY-CODE               PIC X(6).
          03 PT-QMT-AGENT-NAME                PIC X(30).
