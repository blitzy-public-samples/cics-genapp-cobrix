******************************************************************
*  COPYBOOK  : GBMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : MD
******************************************************************
 01  RT-BMD-RATING.

          03 RT-BMD-TERRITORY-CODE            PIC X(3).
          03 RT-BMD-CLASS-CODE                PIC X(4).
          03 RT-BMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BMD-RATED-PREMIUM             PIC 9(9)V9(2).
