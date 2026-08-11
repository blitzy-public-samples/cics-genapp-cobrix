******************************************************************
*  COPYBOOK  : GRIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : ID
******************************************************************
 01  RT-RID-RATING.

          03 RT-RID-TERRITORY-CODE            PIC X(3).
          03 RT-RID-CLASS-CODE                PIC X(4).
          03 RT-RID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RID-RATED-PREMIUM             PIC 9(9)V9(2).
