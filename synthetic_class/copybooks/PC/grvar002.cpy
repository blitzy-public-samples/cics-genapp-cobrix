******************************************************************
*  COPYBOOK  : GRVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : VA
******************************************************************
 01  RT-RVA-RATING.

          03 RT-RVA-TERRITORY-CODE            PIC X(3).
          03 RT-RVA-CLASS-CODE                PIC X(4).
          03 RT-RVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RVA-RATED-PREMIUM             PIC 9(9)V9(2).
