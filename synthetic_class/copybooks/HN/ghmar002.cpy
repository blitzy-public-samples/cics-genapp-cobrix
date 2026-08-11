******************************************************************
*  COPYBOOK  : GHMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : MA
******************************************************************
 01  RT-HMA-RATING.

          03 RT-HMA-TERRITORY-CODE            PIC X(3).
          03 RT-HMA-CLASS-CODE                PIC X(4).
          03 RT-HMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HMA-RATED-PREMIUM             PIC 9(9)V9(2).
