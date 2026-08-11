******************************************************************
*  COPYBOOK  : GAWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : WI
******************************************************************
 01  RT-AWI-RATING.

          03 RT-AWI-TERRITORY-CODE            PIC X(3).
          03 RT-AWI-CLASS-CODE                PIC X(4).
          03 RT-AWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AWI-RATED-PREMIUM             PIC 9(9)V9(2).
