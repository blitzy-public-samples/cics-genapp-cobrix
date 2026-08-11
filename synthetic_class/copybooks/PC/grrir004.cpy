******************************************************************
*  COPYBOOK  : GRRIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : RI
******************************************************************
 01  RT-RRI-RATING.

          03 RT-RRI-TERRITORY-CODE            PIC X(3).
          03 RT-RRI-CLASS-CODE                PIC X(4).
          03 RT-RRI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RRI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RRI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RRI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RRI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RRI-RATED-PREMIUM             PIC 9(9)V9(2).
