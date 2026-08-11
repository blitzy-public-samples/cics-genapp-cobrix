******************************************************************
*  COPYBOOK  : GBVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : VT
******************************************************************
 01  RT-BVT-RATING.

          03 RT-BVT-TERRITORY-CODE            PIC X(3).
          03 RT-BVT-CLASS-CODE                PIC X(4).
          03 RT-BVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BVT-RATED-PREMIUM             PIC 9(9)V9(2).
