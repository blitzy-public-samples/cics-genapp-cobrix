******************************************************************
*  COPYBOOK  : GMMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MA
******************************************************************
 01  RT-MMA-RATING.

          03 RT-MMA-TERRITORY-CODE            PIC X(3).
          03 RT-MMA-CLASS-CODE                PIC X(4).
          03 RT-MMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MMA-RATED-PREMIUM             PIC 9(9)V9(2).
