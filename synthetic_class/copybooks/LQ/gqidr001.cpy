******************************************************************
*  COPYBOOK  : GQIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : ID
******************************************************************
 01  RT-QID-RATING.

          03 RT-QID-TERRITORY-CODE            PIC X(3).
          03 RT-QID-CLASS-CODE                PIC X(4).
          03 RT-QID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QID-RATED-PREMIUM             PIC 9(9)V9(2).
