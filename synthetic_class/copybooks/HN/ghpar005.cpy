******************************************************************
*  COPYBOOK  : GHPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : PA
******************************************************************
 01  RT-HPA-RATING.

          03 RT-HPA-TERRITORY-CODE            PIC X(3).
          03 RT-HPA-CLASS-CODE                PIC X(4).
          03 RT-HPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HPA-RATED-PREMIUM             PIC 9(9)V9(2).
