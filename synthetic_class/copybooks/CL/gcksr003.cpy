******************************************************************
*  COPYBOOK  : GCKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : KS
******************************************************************
 01  RT-CKS-RATING.

          03 RT-CKS-TERRITORY-CODE            PIC X(3).
          03 RT-CKS-CLASS-CODE                PIC X(4).
          03 RT-CKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CKS-RATED-PREMIUM             PIC 9(9)V9(2).
