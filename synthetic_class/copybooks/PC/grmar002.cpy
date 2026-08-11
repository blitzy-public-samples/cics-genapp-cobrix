******************************************************************
*  COPYBOOK  : GRMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MA
******************************************************************
 01  RT-RMA-RATING.

          03 RT-RMA-TERRITORY-CODE            PIC X(3).
          03 RT-RMA-CLASS-CODE                PIC X(4).
          03 RT-RMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RMA-RATED-PREMIUM             PIC 9(9)V9(2).
