******************************************************************
*  COPYBOOK  : GAHIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : HI
******************************************************************
 01  RT-AHI-RATING.

          03 RT-AHI-TERRITORY-CODE            PIC X(3).
          03 RT-AHI-CLASS-CODE                PIC X(4).
          03 RT-AHI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AHI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AHI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AHI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AHI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AHI-RATED-PREMIUM             PIC 9(9)V9(2).
