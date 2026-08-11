******************************************************************
*  COPYBOOK  : GHWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : WA
******************************************************************
 01  RT-HWA-RATING.

          03 RT-HWA-TERRITORY-CODE            PIC X(3).
          03 RT-HWA-CLASS-CODE                PIC X(4).
          03 RT-HWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HWA-RATED-PREMIUM             PIC 9(9)V9(2).
