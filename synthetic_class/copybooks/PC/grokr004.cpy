******************************************************************
*  COPYBOOK  : GROKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : OK
******************************************************************
 01  RT-ROK-RATING.

          03 RT-ROK-TERRITORY-CODE            PIC X(3).
          03 RT-ROK-CLASS-CODE                PIC X(4).
          03 RT-ROK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ROK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ROK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ROK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ROK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ROK-RATED-PREMIUM             PIC 9(9)V9(2).
