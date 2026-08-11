******************************************************************
*  COPYBOOK  : GNKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : KS
******************************************************************
 01  RT-NKS-RATING.

          03 RT-NKS-TERRITORY-CODE            PIC X(3).
          03 RT-NKS-CLASS-CODE                PIC X(4).
          03 RT-NKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NKS-RATED-PREMIUM             PIC 9(9)V9(2).
