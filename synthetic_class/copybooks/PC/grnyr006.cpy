******************************************************************
*  COPYBOOK  : GRNYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NY
******************************************************************
 01  RT-RNY-RATING.

          03 RT-RNY-TERRITORY-CODE            PIC X(3).
          03 RT-RNY-CLASS-CODE                PIC X(4).
          03 RT-RNY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RNY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RNY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RNY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RNY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RNY-RATED-PREMIUM             PIC 9(9)V9(2).
