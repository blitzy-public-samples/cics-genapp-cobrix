******************************************************************
*  COPYBOOK  : GQSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : SC
******************************************************************
 01  RT-QSC-RATING.

          03 RT-QSC-TERRITORY-CODE            PIC X(3).
          03 RT-QSC-CLASS-CODE                PIC X(4).
          03 RT-QSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QSC-RATED-PREMIUM             PIC 9(9)V9(2).
