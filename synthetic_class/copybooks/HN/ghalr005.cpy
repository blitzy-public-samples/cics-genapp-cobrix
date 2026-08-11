******************************************************************
*  COPYBOOK  : GHALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : AL
******************************************************************
 01  RT-HAL-RATING.

          03 RT-HAL-TERRITORY-CODE            PIC X(3).
          03 RT-HAL-CLASS-CODE                PIC X(4).
          03 RT-HAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HAL-RATED-PREMIUM             PIC 9(9)V9(2).
