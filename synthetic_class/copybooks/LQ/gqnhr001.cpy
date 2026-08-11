******************************************************************
*  COPYBOOK  : GQNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : NH
******************************************************************
 01  RT-QNH-RATING.

          03 RT-QNH-TERRITORY-CODE            PIC X(3).
          03 RT-QNH-CLASS-CODE                PIC X(4).
          03 RT-QNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QNH-RATED-PREMIUM             PIC 9(9)V9(2).
