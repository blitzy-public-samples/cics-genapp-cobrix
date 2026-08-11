******************************************************************
*  COPYBOOK  : GBMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : ME
******************************************************************
 01  RT-BME-RATING.

          03 RT-BME-TERRITORY-CODE            PIC X(3).
          03 RT-BME-CLASS-CODE                PIC X(4).
          03 RT-BME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BME-RATED-PREMIUM             PIC 9(9)V9(2).
