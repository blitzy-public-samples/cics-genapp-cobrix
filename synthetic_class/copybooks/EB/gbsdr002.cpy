******************************************************************
*  COPYBOOK  : GBSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : SD
******************************************************************
 01  RT-BSD-RATING.

          03 RT-BSD-TERRITORY-CODE            PIC X(3).
          03 RT-BSD-CLASS-CODE                PIC X(4).
          03 RT-BSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BSD-RATED-PREMIUM             PIC 9(9)V9(2).
