******************************************************************
*  COPYBOOK  : GASDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : SD
******************************************************************
 01  RT-ASD-RATING.

          03 RT-ASD-TERRITORY-CODE            PIC X(3).
          03 RT-ASD-CLASS-CODE                PIC X(4).
          03 RT-ASD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ASD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ASD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ASD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ASD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ASD-RATED-PREMIUM             PIC 9(9)V9(2).
