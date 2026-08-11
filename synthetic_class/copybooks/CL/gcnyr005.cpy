******************************************************************
*  COPYBOOK  : GCNYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : NY
******************************************************************
 01  RT-CNY-RATING.

          03 RT-CNY-TERRITORY-CODE            PIC X(3).
          03 RT-CNY-CLASS-CODE                PIC X(4).
          03 RT-CNY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CNY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CNY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CNY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CNY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CNY-RATED-PREMIUM             PIC 9(9)V9(2).
