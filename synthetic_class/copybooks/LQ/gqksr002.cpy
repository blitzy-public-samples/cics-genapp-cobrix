******************************************************************
*  COPYBOOK  : GQKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : KS
******************************************************************
 01  RT-QKS-RATING.

          03 RT-QKS-TERRITORY-CODE            PIC X(3).
          03 RT-QKS-CLASS-CODE                PIC X(4).
          03 RT-QKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QKS-RATED-PREMIUM             PIC 9(9)V9(2).
