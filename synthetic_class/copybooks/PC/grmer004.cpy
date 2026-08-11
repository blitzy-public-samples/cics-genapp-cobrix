******************************************************************
*  COPYBOOK  : GRMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : ME
******************************************************************
 01  RT-RME-RATING.

          03 RT-RME-TERRITORY-CODE            PIC X(3).
          03 RT-RME-CLASS-CODE                PIC X(4).
          03 RT-RME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RME-RATED-PREMIUM             PIC 9(9)V9(2).
