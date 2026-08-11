******************************************************************
*  COPYBOOK  : GANDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : ND
******************************************************************
 01  RT-AND-RATING.

          03 RT-AND-TERRITORY-CODE            PIC X(3).
          03 RT-AND-CLASS-CODE                PIC X(4).
          03 RT-AND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AND-RATED-PREMIUM             PIC 9(9)V9(2).
