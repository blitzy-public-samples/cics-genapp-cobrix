******************************************************************
*  COPYBOOK  : GAINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : IN
******************************************************************
 01  RT-AIN-RATING.

          03 RT-AIN-TERRITORY-CODE            PIC X(3).
          03 RT-AIN-CLASS-CODE                PIC X(4).
          03 RT-AIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AIN-RATED-PREMIUM             PIC 9(9)V9(2).
