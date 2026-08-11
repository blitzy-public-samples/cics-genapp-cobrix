******************************************************************
*  COPYBOOK  : GRNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NC
******************************************************************
 01  RT-RNC-RATING.

          03 RT-RNC-TERRITORY-CODE            PIC X(3).
          03 RT-RNC-CLASS-CODE                PIC X(4).
          03 RT-RNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RNC-RATED-PREMIUM             PIC 9(9)V9(2).
