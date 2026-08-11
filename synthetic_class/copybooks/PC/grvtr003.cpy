******************************************************************
*  COPYBOOK  : GRVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : VT
******************************************************************
 01  RT-RVT-RATING.

          03 RT-RVT-TERRITORY-CODE            PIC X(3).
          03 RT-RVT-CLASS-CODE                PIC X(4).
          03 RT-RVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RVT-RATED-PREMIUM             PIC 9(9)V9(2).
