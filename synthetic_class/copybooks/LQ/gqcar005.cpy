******************************************************************
*  COPYBOOK  : GQCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : CA
******************************************************************
 01  RT-QCA-RATING.

          03 RT-QCA-TERRITORY-CODE            PIC X(3).
          03 RT-QCA-CLASS-CODE                PIC X(4).
          03 RT-QCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QCA-RATED-PREMIUM             PIC 9(9)V9(2).
