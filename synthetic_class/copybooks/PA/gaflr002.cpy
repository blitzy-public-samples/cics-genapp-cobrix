******************************************************************
*  COPYBOOK  : GAFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : FL
******************************************************************
 01  RT-AFL-RATING.

          03 RT-AFL-TERRITORY-CODE            PIC X(3).
          03 RT-AFL-CLASS-CODE                PIC X(4).
          03 RT-AFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AFL-RATED-PREMIUM             PIC 9(9)V9(2).
