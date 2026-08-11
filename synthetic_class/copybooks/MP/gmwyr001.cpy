******************************************************************
*  COPYBOOK  : GMWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : WY
******************************************************************
 01  RT-MWY-RATING.

          03 RT-MWY-TERRITORY-CODE            PIC X(3).
          03 RT-MWY-CLASS-CODE                PIC X(4).
          03 RT-MWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MWY-RATED-PREMIUM             PIC 9(9)V9(2).
