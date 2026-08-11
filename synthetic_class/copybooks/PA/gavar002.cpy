******************************************************************
*  COPYBOOK  : GAVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : VA
******************************************************************
 01  RT-AVA-RATING.

          03 RT-AVA-TERRITORY-CODE            PIC X(3).
          03 RT-AVA-CLASS-CODE                PIC X(4).
          03 RT-AVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AVA-RATED-PREMIUM             PIC 9(9)V9(2).
