******************************************************************
*  COPYBOOK  : GRGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : GA
******************************************************************
 01  RT-RGA-RATING.

          03 RT-RGA-TERRITORY-CODE            PIC X(3).
          03 RT-RGA-CLASS-CODE                PIC X(4).
          03 RT-RGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RGA-RATED-PREMIUM             PIC 9(9)V9(2).
