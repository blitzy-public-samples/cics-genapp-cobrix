******************************************************************
*  COPYBOOK  : GRDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : DE
******************************************************************
 01  RT-RDE-RATING.

          03 RT-RDE-TERRITORY-CODE            PIC X(3).
          03 RT-RDE-CLASS-CODE                PIC X(4).
          03 RT-RDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RDE-RATED-PREMIUM             PIC 9(9)V9(2).
