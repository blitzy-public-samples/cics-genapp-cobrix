******************************************************************
*  COPYBOOK  : GRNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NH
******************************************************************
 01  RT-RNH-RATING.

          03 RT-RNH-TERRITORY-CODE            PIC X(3).
          03 RT-RNH-CLASS-CODE                PIC X(4).
          03 RT-RNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RNH-RATED-PREMIUM             PIC 9(9)V9(2).
