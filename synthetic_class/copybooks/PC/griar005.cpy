******************************************************************
*  COPYBOOK  : GRIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : IA
******************************************************************
 01  RT-RIA-RATING.

          03 RT-RIA-TERRITORY-CODE            PIC X(3).
          03 RT-RIA-CLASS-CODE                PIC X(4).
          03 RT-RIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RIA-RATED-PREMIUM             PIC 9(9)V9(2).
