******************************************************************
*  COPYBOOK  : GRSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : SD
******************************************************************
 01  RT-RSD-RATING.

          03 RT-RSD-TERRITORY-CODE            PIC X(3).
          03 RT-RSD-CLASS-CODE                PIC X(4).
          03 RT-RSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RSD-RATED-PREMIUM             PIC 9(9)V9(2).
