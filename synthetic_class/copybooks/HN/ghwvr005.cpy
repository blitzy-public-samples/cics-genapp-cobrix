******************************************************************
*  COPYBOOK  : GHWVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : WV
******************************************************************
 01  RT-HWV-RATING.

          03 RT-HWV-TERRITORY-CODE            PIC X(3).
          03 RT-HWV-CLASS-CODE                PIC X(4).
          03 RT-HWV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HWV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HWV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HWV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HWV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HWV-RATED-PREMIUM             PIC 9(9)V9(2).
