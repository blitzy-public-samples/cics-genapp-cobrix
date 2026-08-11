******************************************************************
*  COPYBOOK  : GMVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : VT
******************************************************************
 01  RT-MVT-RATING.

          03 RT-MVT-TERRITORY-CODE            PIC X(3).
          03 RT-MVT-CLASS-CODE                PIC X(4).
          03 RT-MVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MVT-RATED-PREMIUM             PIC 9(9)V9(2).
