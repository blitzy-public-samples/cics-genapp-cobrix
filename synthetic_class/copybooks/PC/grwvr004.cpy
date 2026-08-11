******************************************************************
*  COPYBOOK  : GRWVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : WV
******************************************************************
 01  RT-RWV-RATING.

          03 RT-RWV-TERRITORY-CODE            PIC X(3).
          03 RT-RWV-CLASS-CODE                PIC X(4).
          03 RT-RWV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RWV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RWV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RWV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RWV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RWV-RATED-PREMIUM             PIC 9(9)V9(2).
