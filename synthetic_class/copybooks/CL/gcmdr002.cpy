******************************************************************
*  COPYBOOK  : GCMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MD
******************************************************************
 01  RT-CMD-RATING.

          03 RT-CMD-TERRITORY-CODE            PIC X(3).
          03 RT-CMD-CLASS-CODE                PIC X(4).
          03 RT-CMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CMD-RATED-PREMIUM             PIC 9(9)V9(2).
