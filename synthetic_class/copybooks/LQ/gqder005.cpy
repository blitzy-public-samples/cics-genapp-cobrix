******************************************************************
*  COPYBOOK  : GQDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : DE
******************************************************************
 01  RT-QDE-RATING.

          03 RT-QDE-TERRITORY-CODE            PIC X(3).
          03 RT-QDE-CLASS-CODE                PIC X(4).
          03 RT-QDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QDE-RATED-PREMIUM             PIC 9(9)V9(2).
