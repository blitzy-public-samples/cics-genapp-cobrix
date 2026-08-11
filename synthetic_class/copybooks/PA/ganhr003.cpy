******************************************************************
*  COPYBOOK  : GANHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : NH
******************************************************************
 01  RT-ANH-RATING.

          03 RT-ANH-TERRITORY-CODE            PIC X(3).
          03 RT-ANH-CLASS-CODE                PIC X(4).
          03 RT-ANH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ANH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ANH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ANH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ANH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ANH-RATED-PREMIUM             PIC 9(9)V9(2).
