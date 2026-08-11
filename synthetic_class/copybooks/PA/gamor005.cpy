******************************************************************
*  COPYBOOK  : GAMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : MO
******************************************************************
 01  RT-AMO-RATING.

          03 RT-AMO-TERRITORY-CODE            PIC X(3).
          03 RT-AMO-CLASS-CODE                PIC X(4).
          03 RT-AMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AMO-RATED-PREMIUM             PIC 9(9)V9(2).
