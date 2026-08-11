******************************************************************
*  COPYBOOK  : GCMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MA
******************************************************************
 01  RT-CMA-RATING.

          03 RT-CMA-TERRITORY-CODE            PIC X(3).
          03 RT-CMA-CLASS-CODE                PIC X(4).
          03 RT-CMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CMA-RATED-PREMIUM             PIC 9(9)V9(2).
