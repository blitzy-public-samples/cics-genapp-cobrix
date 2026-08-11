******************************************************************
*  COPYBOOK  : GRTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : TX
******************************************************************
 01  RT-RTX-RATING.

          03 RT-RTX-TERRITORY-CODE            PIC X(3).
          03 RT-RTX-CLASS-CODE                PIC X(4).
          03 RT-RTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RTX-RATED-PREMIUM             PIC 9(9)V9(2).
