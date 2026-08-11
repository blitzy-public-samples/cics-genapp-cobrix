******************************************************************
*  COPYBOOK  : GMMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MD
******************************************************************
 01  RT-MMD-RATING.

          03 RT-MMD-TERRITORY-CODE            PIC X(3).
          03 RT-MMD-CLASS-CODE                PIC X(4).
          03 RT-MMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MMD-RATED-PREMIUM             PIC 9(9)V9(2).
