******************************************************************
*  COPYBOOK  : GNCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : CO
******************************************************************
 01  RT-NCO-RATING.

          03 RT-NCO-TERRITORY-CODE            PIC X(3).
          03 RT-NCO-CLASS-CODE                PIC X(4).
          03 RT-NCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NCO-RATED-PREMIUM             PIC 9(9)V9(2).
