******************************************************************
*  COPYBOOK  : GQMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : MO
******************************************************************
 01  RT-QMO-RATING.

          03 RT-QMO-TERRITORY-CODE            PIC X(3).
          03 RT-QMO-CLASS-CODE                PIC X(4).
          03 RT-QMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QMO-RATED-PREMIUM             PIC 9(9)V9(2).
