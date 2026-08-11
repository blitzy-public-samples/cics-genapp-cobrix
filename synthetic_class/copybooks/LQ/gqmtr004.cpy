******************************************************************
*  COPYBOOK  : GQMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : MT
******************************************************************
 01  RT-QMT-RATING.

          03 RT-QMT-TERRITORY-CODE            PIC X(3).
          03 RT-QMT-CLASS-CODE                PIC X(4).
          03 RT-QMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QMT-RATED-PREMIUM             PIC 9(9)V9(2).
