******************************************************************
*  COPYBOOK  : GAAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : AK
******************************************************************
 01  RT-AAK-RATING.

          03 RT-AAK-TERRITORY-CODE            PIC X(3).
          03 RT-AAK-CLASS-CODE                PIC X(4).
          03 RT-AAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AAK-RATED-PREMIUM             PIC 9(9)V9(2).
