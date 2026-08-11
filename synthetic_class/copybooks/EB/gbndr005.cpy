******************************************************************
*  COPYBOOK  : GBNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : ND
******************************************************************
 01  RT-BND-RATING.

          03 RT-BND-TERRITORY-CODE            PIC X(3).
          03 RT-BND-CLASS-CODE                PIC X(4).
          03 RT-BND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BND-RATED-PREMIUM             PIC 9(9)V9(2).
