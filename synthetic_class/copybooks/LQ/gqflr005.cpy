******************************************************************
*  COPYBOOK  : GQFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : FL
******************************************************************
 01  RT-QFL-RATING.

          03 RT-QFL-TERRITORY-CODE            PIC X(3).
          03 RT-QFL-CLASS-CODE                PIC X(4).
          03 RT-QFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QFL-RATED-PREMIUM             PIC 9(9)V9(2).
