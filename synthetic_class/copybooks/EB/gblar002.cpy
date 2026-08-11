******************************************************************
*  COPYBOOK  : GBLAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : LA
******************************************************************
 01  RT-BLA-RATING.

          03 RT-BLA-TERRITORY-CODE            PIC X(3).
          03 RT-BLA-CLASS-CODE                PIC X(4).
          03 RT-BLA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BLA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BLA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BLA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BLA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BLA-RATED-PREMIUM             PIC 9(9)V9(2).
