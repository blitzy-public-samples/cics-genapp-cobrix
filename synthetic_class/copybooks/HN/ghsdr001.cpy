******************************************************************
*  COPYBOOK  : GHSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : SD
******************************************************************
 01  RT-HSD-RATING.

          03 RT-HSD-TERRITORY-CODE            PIC X(3).
          03 RT-HSD-CLASS-CODE                PIC X(4).
          03 RT-HSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HSD-RATED-PREMIUM             PIC 9(9)V9(2).
