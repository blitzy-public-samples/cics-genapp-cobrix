******************************************************************
*  COPYBOOK  : GQNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : ND
******************************************************************
 01  RT-QND-RATING.

          03 RT-QND-TERRITORY-CODE            PIC X(3).
          03 RT-QND-CLASS-CODE                PIC X(4).
          03 RT-QND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QND-RATED-PREMIUM             PIC 9(9)V9(2).
