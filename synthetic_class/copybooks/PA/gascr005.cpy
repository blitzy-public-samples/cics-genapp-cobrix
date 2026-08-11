******************************************************************
*  COPYBOOK  : GASCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : SC
******************************************************************
 01  RT-ASC-RATING.

          03 RT-ASC-TERRITORY-CODE            PIC X(3).
          03 RT-ASC-CLASS-CODE                PIC X(4).
          03 RT-ASC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ASC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ASC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ASC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ASC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ASC-RATED-PREMIUM             PIC 9(9)V9(2).
