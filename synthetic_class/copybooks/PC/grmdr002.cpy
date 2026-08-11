******************************************************************
*  COPYBOOK  : GRMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MD
******************************************************************
 01  RT-RMD-RATING.

          03 RT-RMD-TERRITORY-CODE            PIC X(3).
          03 RT-RMD-CLASS-CODE                PIC X(4).
          03 RT-RMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RMD-RATED-PREMIUM             PIC 9(9)V9(2).
