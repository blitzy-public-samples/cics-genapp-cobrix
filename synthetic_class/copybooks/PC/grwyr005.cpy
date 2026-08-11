******************************************************************
*  COPYBOOK  : GRWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : WY
******************************************************************
 01  RT-RWY-RATING.

          03 RT-RWY-TERRITORY-CODE            PIC X(3).
          03 RT-RWY-CLASS-CODE                PIC X(4).
          03 RT-RWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RWY-RATED-PREMIUM             PIC 9(9)V9(2).
