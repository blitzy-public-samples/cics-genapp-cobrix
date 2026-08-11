******************************************************************
*  COPYBOOK  : GBKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : KS
******************************************************************
 01  RT-BKS-RATING.

          03 RT-BKS-TERRITORY-CODE            PIC X(3).
          03 RT-BKS-CLASS-CODE                PIC X(4).
          03 RT-BKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BKS-RATED-PREMIUM             PIC 9(9)V9(2).
