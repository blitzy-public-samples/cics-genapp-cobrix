******************************************************************
*  COPYBOOK  : GQNYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : NY
******************************************************************
 01  RT-QNY-RATING.

          03 RT-QNY-TERRITORY-CODE            PIC X(3).
          03 RT-QNY-CLASS-CODE                PIC X(4).
          03 RT-QNY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QNY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QNY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QNY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QNY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QNY-RATED-PREMIUM             PIC 9(9)V9(2).
