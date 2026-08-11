******************************************************************
*  COPYBOOK  : GHWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : WI
******************************************************************
 01  RT-HWI-RATING.

          03 RT-HWI-TERRITORY-CODE            PIC X(3).
          03 RT-HWI-CLASS-CODE                PIC X(4).
          03 RT-HWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HWI-RATED-PREMIUM             PIC 9(9)V9(2).
