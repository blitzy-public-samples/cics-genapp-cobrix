******************************************************************
*  COPYBOOK  : GAMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : MD
******************************************************************
 01  RT-AMD-RATING.

          03 RT-AMD-TERRITORY-CODE            PIC X(3).
          03 RT-AMD-CLASS-CODE                PIC X(4).
          03 RT-AMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AMD-RATED-PREMIUM             PIC 9(9)V9(2).
