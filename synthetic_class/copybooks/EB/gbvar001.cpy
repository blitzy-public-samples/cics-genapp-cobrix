******************************************************************
*  COPYBOOK  : GBVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : VA
******************************************************************
 01  RT-BVA-RATING.

          03 RT-BVA-TERRITORY-CODE            PIC X(3).
          03 RT-BVA-CLASS-CODE                PIC X(4).
          03 RT-BVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BVA-RATED-PREMIUM             PIC 9(9)V9(2).
