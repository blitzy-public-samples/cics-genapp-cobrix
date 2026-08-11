******************************************************************
*  COPYBOOK  : GQMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : ME
******************************************************************
 01  RT-QME-RATING.

          03 RT-QME-TERRITORY-CODE            PIC X(3).
          03 RT-QME-CLASS-CODE                PIC X(4).
          03 RT-QME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QME-RATED-PREMIUM             PIC 9(9)V9(2).
