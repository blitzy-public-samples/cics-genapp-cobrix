******************************************************************
*  COPYBOOK  : GAOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : OK
******************************************************************
 01  RT-AOK-RATING.

          03 RT-AOK-TERRITORY-CODE            PIC X(3).
          03 RT-AOK-CLASS-CODE                PIC X(4).
          03 RT-AOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AOK-RATED-PREMIUM             PIC 9(9)V9(2).
