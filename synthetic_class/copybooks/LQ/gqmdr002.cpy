******************************************************************
*  COPYBOOK  : GQMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : MD
******************************************************************
 01  RT-QMD-RATING.

          03 RT-QMD-TERRITORY-CODE            PIC X(3).
          03 RT-QMD-CLASS-CODE                PIC X(4).
          03 RT-QMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QMD-RATED-PREMIUM             PIC 9(9)V9(2).
