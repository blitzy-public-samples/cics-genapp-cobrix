******************************************************************
*  COPYBOOK  : GHKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : KS
******************************************************************
 01  RT-HKS-RATING.

          03 RT-HKS-TERRITORY-CODE            PIC X(3).
          03 RT-HKS-CLASS-CODE                PIC X(4).
          03 RT-HKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HKS-RATED-PREMIUM             PIC 9(9)V9(2).
