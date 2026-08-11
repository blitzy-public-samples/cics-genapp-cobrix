******************************************************************
*  COPYBOOK  : GRINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : IN
******************************************************************
 01  RT-RIN-RATING.

          03 RT-RIN-TERRITORY-CODE            PIC X(3).
          03 RT-RIN-CLASS-CODE                PIC X(4).
          03 RT-RIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RIN-RATED-PREMIUM             PIC 9(9)V9(2).
