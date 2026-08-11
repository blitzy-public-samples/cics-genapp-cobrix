******************************************************************
*  COPYBOOK  : GRKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : KS
******************************************************************
 01  RT-RKS-RATING.

          03 RT-RKS-TERRITORY-CODE            PIC X(3).
          03 RT-RKS-CLASS-CODE                PIC X(4).
          03 RT-RKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RKS-RATED-PREMIUM             PIC 9(9)V9(2).
