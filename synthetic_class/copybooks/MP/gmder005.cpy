******************************************************************
*  COPYBOOK  : GMDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : DE
******************************************************************
 01  RT-MDE-RATING.

          03 RT-MDE-TERRITORY-CODE            PIC X(3).
          03 RT-MDE-CLASS-CODE                PIC X(4).
          03 RT-MDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MDE-RATED-PREMIUM             PIC 9(9)V9(2).
