******************************************************************
*  COPYBOOK  : GAMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : ME
******************************************************************
 01  RT-AME-RATING.

          03 RT-AME-TERRITORY-CODE            PIC X(3).
          03 RT-AME-CLASS-CODE                PIC X(4).
          03 RT-AME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AME-RATED-PREMIUM             PIC 9(9)V9(2).
