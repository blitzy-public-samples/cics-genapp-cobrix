******************************************************************
*  COPYBOOK  : GRCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : CA
******************************************************************
 01  RT-RCA-RATING.

          03 RT-RCA-TERRITORY-CODE            PIC X(3).
          03 RT-RCA-CLASS-CODE                PIC X(4).
          03 RT-RCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RCA-RATED-PREMIUM             PIC 9(9)V9(2).
