******************************************************************
*  COPYBOOK  : GUCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : CO
******************************************************************
 01  RT-UCO-RATING.

          03 RT-UCO-TERRITORY-CODE            PIC X(3).
          03 RT-UCO-CLASS-CODE                PIC X(4).
          03 RT-UCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UCO-RATED-PREMIUM             PIC 9(9)V9(2).
