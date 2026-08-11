******************************************************************
*  COPYBOOK  : GNNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : ND
******************************************************************
 01  RT-NND-RATING.

          03 RT-NND-TERRITORY-CODE            PIC X(3).
          03 RT-NND-CLASS-CODE                PIC X(4).
          03 RT-NND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NND-RATED-PREMIUM             PIC 9(9)V9(2).
