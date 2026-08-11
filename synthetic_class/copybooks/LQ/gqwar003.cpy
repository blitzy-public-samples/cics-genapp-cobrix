******************************************************************
*  COPYBOOK  : GQWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : WA
******************************************************************
 01  RT-QWA-RATING.

          03 RT-QWA-TERRITORY-CODE            PIC X(3).
          03 RT-QWA-CLASS-CODE                PIC X(4).
          03 RT-QWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QWA-RATED-PREMIUM             PIC 9(9)V9(2).
