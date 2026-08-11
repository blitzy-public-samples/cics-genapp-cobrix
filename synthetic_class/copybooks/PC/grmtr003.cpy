******************************************************************
*  COPYBOOK  : GRMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MT
******************************************************************
 01  RT-RMT-RATING.

          03 RT-RMT-TERRITORY-CODE            PIC X(3).
          03 RT-RMT-CLASS-CODE                PIC X(4).
          03 RT-RMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RMT-RATED-PREMIUM             PIC 9(9)V9(2).
