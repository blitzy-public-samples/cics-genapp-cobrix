******************************************************************
*  COPYBOOK  : GNNYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : NY
******************************************************************
 01  RT-NNY-RATING.

          03 RT-NNY-TERRITORY-CODE            PIC X(3).
          03 RT-NNY-CLASS-CODE                PIC X(4).
          03 RT-NNY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NNY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NNY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NNY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NNY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NNY-RATED-PREMIUM             PIC 9(9)V9(2).
