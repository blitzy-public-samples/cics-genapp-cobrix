******************************************************************
*  COPYBOOK  : GAKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : KY
******************************************************************
 01  RT-AKY-RATING.

          03 RT-AKY-TERRITORY-CODE            PIC X(3).
          03 RT-AKY-CLASS-CODE                PIC X(4).
          03 RT-AKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AKY-RATED-PREMIUM             PIC 9(9)V9(2).
