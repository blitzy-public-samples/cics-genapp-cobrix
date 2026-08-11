******************************************************************
*  COPYBOOK  : GBMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : MA
******************************************************************
 01  RT-BMA-RATING.

          03 RT-BMA-TERRITORY-CODE            PIC X(3).
          03 RT-BMA-CLASS-CODE                PIC X(4).
          03 RT-BMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BMA-RATED-PREMIUM             PIC 9(9)V9(2).
