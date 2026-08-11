******************************************************************
*  COPYBOOK  : GQPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : PA
******************************************************************
 01  RT-QPA-RATING.

          03 RT-QPA-TERRITORY-CODE            PIC X(3).
          03 RT-QPA-CLASS-CODE                PIC X(4).
          03 RT-QPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QPA-RATED-PREMIUM             PIC 9(9)V9(2).
