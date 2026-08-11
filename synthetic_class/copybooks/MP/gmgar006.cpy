******************************************************************
*  COPYBOOK  : GMGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : GA
******************************************************************
 01  RT-MGA-RATING.

          03 RT-MGA-TERRITORY-CODE            PIC X(3).
          03 RT-MGA-CLASS-CODE                PIC X(4).
          03 RT-MGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MGA-RATED-PREMIUM             PIC 9(9)V9(2).
