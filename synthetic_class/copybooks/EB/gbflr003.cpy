******************************************************************
*  COPYBOOK  : GBFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : FL
******************************************************************
 01  RT-BFL-RATING.

          03 RT-BFL-TERRITORY-CODE            PIC X(3).
          03 RT-BFL-CLASS-CODE                PIC X(4).
          03 RT-BFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BFL-RATED-PREMIUM             PIC 9(9)V9(2).
