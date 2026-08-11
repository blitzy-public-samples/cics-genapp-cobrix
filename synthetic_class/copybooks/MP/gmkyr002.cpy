******************************************************************
*  COPYBOOK  : GMKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : KY
******************************************************************
 01  RT-MKY-RATING.

          03 RT-MKY-TERRITORY-CODE            PIC X(3).
          03 RT-MKY-CLASS-CODE                PIC X(4).
          03 RT-MKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MKY-RATED-PREMIUM             PIC 9(9)V9(2).
