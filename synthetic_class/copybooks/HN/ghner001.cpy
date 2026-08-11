******************************************************************
*  COPYBOOK  : GHNER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : NE
******************************************************************
 01  RT-HNE-RATING.

          03 RT-HNE-TERRITORY-CODE            PIC X(3).
          03 RT-HNE-CLASS-CODE                PIC X(4).
          03 RT-HNE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HNE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HNE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HNE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HNE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HNE-RATED-PREMIUM             PIC 9(9)V9(2).
