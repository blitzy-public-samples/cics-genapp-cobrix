******************************************************************
*  COPYBOOK  : GQMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : MA
******************************************************************
 01  RT-QMA-RATING.

          03 RT-QMA-TERRITORY-CODE            PIC X(3).
          03 RT-QMA-CLASS-CODE                PIC X(4).
          03 RT-QMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QMA-RATED-PREMIUM             PIC 9(9)V9(2).
