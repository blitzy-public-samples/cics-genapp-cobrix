******************************************************************
*  COPYBOOK  : GHNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : ND
******************************************************************
 01  RT-HND-RATING.

          03 RT-HND-TERRITORY-CODE            PIC X(3).
          03 RT-HND-CLASS-CODE                PIC X(4).
          03 RT-HND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HND-RATED-PREMIUM             PIC 9(9)V9(2).
