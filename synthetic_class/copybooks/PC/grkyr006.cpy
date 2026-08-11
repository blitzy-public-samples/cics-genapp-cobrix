******************************************************************
*  COPYBOOK  : GRKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : KY
******************************************************************
 01  RT-RKY-RATING.

          03 RT-RKY-TERRITORY-CODE            PIC X(3).
          03 RT-RKY-CLASS-CODE                PIC X(4).
          03 RT-RKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RKY-RATED-PREMIUM             PIC 9(9)V9(2).
