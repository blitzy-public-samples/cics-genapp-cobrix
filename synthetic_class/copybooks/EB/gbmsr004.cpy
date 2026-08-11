******************************************************************
*  COPYBOOK  : GBMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : MS
******************************************************************
 01  RT-BMS-RATING.

          03 RT-BMS-TERRITORY-CODE            PIC X(3).
          03 RT-BMS-CLASS-CODE                PIC X(4).
          03 RT-BMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BMS-RATED-PREMIUM             PIC 9(9)V9(2).
