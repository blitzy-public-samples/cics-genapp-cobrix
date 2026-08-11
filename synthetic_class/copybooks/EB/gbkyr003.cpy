******************************************************************
*  COPYBOOK  : GBKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : KY
******************************************************************
 01  RT-BKY-RATING.

          03 RT-BKY-TERRITORY-CODE            PIC X(3).
          03 RT-BKY-CLASS-CODE                PIC X(4).
          03 RT-BKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BKY-RATED-PREMIUM             PIC 9(9)V9(2).
