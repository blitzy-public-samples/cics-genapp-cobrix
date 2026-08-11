******************************************************************
*  COPYBOOK  : GAOHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : OH
******************************************************************
 01  RT-AOH-RATING.

          03 RT-AOH-TERRITORY-CODE            PIC X(3).
          03 RT-AOH-CLASS-CODE                PIC X(4).
          03 RT-AOH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AOH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AOH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AOH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AOH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AOH-RATED-PREMIUM             PIC 9(9)V9(2).
