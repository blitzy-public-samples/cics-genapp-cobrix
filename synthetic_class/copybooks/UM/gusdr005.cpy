******************************************************************
*  COPYBOOK  : GUSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : SD
******************************************************************
 01  RT-USD-RATING.

          03 RT-USD-TERRITORY-CODE            PIC X(3).
          03 RT-USD-CLASS-CODE                PIC X(4).
          03 RT-USD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-USD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-USD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-USD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-USD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-USD-RATED-PREMIUM             PIC 9(9)V9(2).
