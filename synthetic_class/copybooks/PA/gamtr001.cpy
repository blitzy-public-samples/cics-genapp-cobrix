******************************************************************
*  COPYBOOK  : GAMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : MT
******************************************************************
 01  RT-AMT-RATING.

          03 RT-AMT-TERRITORY-CODE            PIC X(3).
          03 RT-AMT-CLASS-CODE                PIC X(4).
          03 RT-AMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AMT-RATED-PREMIUM             PIC 9(9)V9(2).
