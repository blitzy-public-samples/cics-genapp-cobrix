******************************************************************
*  COPYBOOK  : GANER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : NE
******************************************************************
 01  RT-ANE-RATING.

          03 RT-ANE-TERRITORY-CODE            PIC X(3).
          03 RT-ANE-CLASS-CODE                PIC X(4).
          03 RT-ANE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ANE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ANE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ANE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ANE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ANE-RATED-PREMIUM             PIC 9(9)V9(2).
