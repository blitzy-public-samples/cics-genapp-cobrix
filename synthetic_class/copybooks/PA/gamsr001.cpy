******************************************************************
*  COPYBOOK  : GAMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : MS
******************************************************************
 01  RT-AMS-RATING.

          03 RT-AMS-TERRITORY-CODE            PIC X(3).
          03 RT-AMS-CLASS-CODE                PIC X(4).
          03 RT-AMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AMS-RATED-PREMIUM             PIC 9(9)V9(2).
