******************************************************************
*  COPYBOOK  : GBIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : ID
******************************************************************
 01  RT-BID-RATING.

          03 RT-BID-TERRITORY-CODE            PIC X(3).
          03 RT-BID-CLASS-CODE                PIC X(4).
          03 RT-BID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BID-RATED-PREMIUM             PIC 9(9)V9(2).
