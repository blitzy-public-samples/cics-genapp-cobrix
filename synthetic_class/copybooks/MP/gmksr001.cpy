******************************************************************
*  COPYBOOK  : GMKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : KS
******************************************************************
 01  RT-MKS-RATING.

          03 RT-MKS-TERRITORY-CODE            PIC X(3).
          03 RT-MKS-CLASS-CODE                PIC X(4).
          03 RT-MKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MKS-RATED-PREMIUM             PIC 9(9)V9(2).
