******************************************************************
*  COPYBOOK  : GQSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : SD
******************************************************************
 01  RT-QSD-RATING.

          03 RT-QSD-TERRITORY-CODE            PIC X(3).
          03 RT-QSD-CLASS-CODE                PIC X(4).
          03 RT-QSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QSD-RATED-PREMIUM             PIC 9(9)V9(2).
