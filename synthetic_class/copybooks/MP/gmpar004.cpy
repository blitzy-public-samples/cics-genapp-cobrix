******************************************************************
*  COPYBOOK  : GMPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : PA
******************************************************************
 01  RT-MPA-RATING.

          03 RT-MPA-TERRITORY-CODE            PIC X(3).
          03 RT-MPA-CLASS-CODE                PIC X(4).
          03 RT-MPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MPA-RATED-PREMIUM             PIC 9(9)V9(2).
