******************************************************************
*  COPYBOOK  : GHKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : KY
******************************************************************
 01  RT-HKY-RATING.

          03 RT-HKY-TERRITORY-CODE            PIC X(3).
          03 RT-HKY-CLASS-CODE                PIC X(4).
          03 RT-HKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HKY-RATED-PREMIUM             PIC 9(9)V9(2).
