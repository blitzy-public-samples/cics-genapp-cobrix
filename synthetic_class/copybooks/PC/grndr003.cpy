******************************************************************
*  COPYBOOK  : GRNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : ND
******************************************************************
 01  RT-RND-RATING.

          03 RT-RND-TERRITORY-CODE            PIC X(3).
          03 RT-RND-CLASS-CODE                PIC X(4).
          03 RT-RND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RND-RATED-PREMIUM             PIC 9(9)V9(2).
