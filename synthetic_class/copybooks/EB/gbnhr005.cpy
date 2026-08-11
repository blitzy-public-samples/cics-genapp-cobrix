******************************************************************
*  COPYBOOK  : GBNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : NH
******************************************************************
 01  RT-BNH-RATING.

          03 RT-BNH-TERRITORY-CODE            PIC X(3).
          03 RT-BNH-CLASS-CODE                PIC X(4).
          03 RT-BNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BNH-RATED-PREMIUM             PIC 9(9)V9(2).
