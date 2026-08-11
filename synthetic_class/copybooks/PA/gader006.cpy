******************************************************************
*  COPYBOOK  : GADER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : DE
******************************************************************
 01  RT-ADE-RATING.

          03 RT-ADE-TERRITORY-CODE            PIC X(3).
          03 RT-ADE-CLASS-CODE                PIC X(4).
          03 RT-ADE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ADE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ADE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ADE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ADE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ADE-RATED-PREMIUM             PIC 9(9)V9(2).
