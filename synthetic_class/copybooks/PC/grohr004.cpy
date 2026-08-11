******************************************************************
*  COPYBOOK  : GROHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : OH
******************************************************************
 01  RT-ROH-RATING.

          03 RT-ROH-TERRITORY-CODE            PIC X(3).
          03 RT-ROH-CLASS-CODE                PIC X(4).
          03 RT-ROH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ROH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ROH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ROH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ROH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ROH-RATED-PREMIUM             PIC 9(9)V9(2).
