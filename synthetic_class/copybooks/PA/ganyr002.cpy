******************************************************************
*  COPYBOOK  : GANYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : NY
******************************************************************
 01  RT-ANY-RATING.

          03 RT-ANY-TERRITORY-CODE            PIC X(3).
          03 RT-ANY-CLASS-CODE                PIC X(4).
          03 RT-ANY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ANY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ANY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ANY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ANY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ANY-RATED-PREMIUM             PIC 9(9)V9(2).
