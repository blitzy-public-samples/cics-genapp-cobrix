******************************************************************
*  COPYBOOK  : GMNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : ND
******************************************************************
 01  RT-MND-RATING.

          03 RT-MND-TERRITORY-CODE            PIC X(3).
          03 RT-MND-CLASS-CODE                PIC X(4).
          03 RT-MND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MND-RATED-PREMIUM             PIC 9(9)V9(2).
