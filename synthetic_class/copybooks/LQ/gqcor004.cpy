******************************************************************
*  COPYBOOK  : GQCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : CO
******************************************************************
 01  RT-QCO-RATING.

          03 RT-QCO-TERRITORY-CODE            PIC X(3).
          03 RT-QCO-CLASS-CODE                PIC X(4).
          03 RT-QCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QCO-RATED-PREMIUM             PIC 9(9)V9(2).
