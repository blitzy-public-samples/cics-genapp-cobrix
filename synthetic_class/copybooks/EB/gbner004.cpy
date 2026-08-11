******************************************************************
*  COPYBOOK  : GBNER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : NE
******************************************************************
 01  RT-BNE-RATING.

          03 RT-BNE-TERRITORY-CODE            PIC X(3).
          03 RT-BNE-CLASS-CODE                PIC X(4).
          03 RT-BNE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BNE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BNE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BNE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BNE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BNE-RATED-PREMIUM             PIC 9(9)V9(2).
