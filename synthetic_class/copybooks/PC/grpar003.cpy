******************************************************************
*  COPYBOOK  : GRPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : PA
******************************************************************
 01  RT-RPA-RATING.

          03 RT-RPA-TERRITORY-CODE            PIC X(3).
          03 RT-RPA-CLASS-CODE                PIC X(4).
          03 RT-RPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RPA-RATED-PREMIUM             PIC 9(9)V9(2).
