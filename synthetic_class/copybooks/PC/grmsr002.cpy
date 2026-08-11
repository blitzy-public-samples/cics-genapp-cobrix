******************************************************************
*  COPYBOOK  : GRMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MS
******************************************************************
 01  RT-RMS-RATING.

          03 RT-RMS-TERRITORY-CODE            PIC X(3).
          03 RT-RMS-CLASS-CODE                PIC X(4).
          03 RT-RMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RMS-RATED-PREMIUM             PIC 9(9)V9(2).
