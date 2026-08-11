******************************************************************
*  COPYBOOK  : GRLAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : LA
******************************************************************
 01  RT-RLA-RATING.

          03 RT-RLA-TERRITORY-CODE            PIC X(3).
          03 RT-RLA-CLASS-CODE                PIC X(4).
          03 RT-RLA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RLA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RLA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RLA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RLA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RLA-RATED-PREMIUM             PIC 9(9)V9(2).
