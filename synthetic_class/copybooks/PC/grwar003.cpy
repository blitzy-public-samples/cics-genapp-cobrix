******************************************************************
*  COPYBOOK  : GRWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : WA
******************************************************************
 01  RT-RWA-RATING.

          03 RT-RWA-TERRITORY-CODE            PIC X(3).
          03 RT-RWA-CLASS-CODE                PIC X(4).
          03 RT-RWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RWA-RATED-PREMIUM             PIC 9(9)V9(2).
