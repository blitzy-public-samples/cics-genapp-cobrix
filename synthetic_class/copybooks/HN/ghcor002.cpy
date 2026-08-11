******************************************************************
*  COPYBOOK  : GHCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : CO
******************************************************************
 01  RT-HCO-RATING.

          03 RT-HCO-TERRITORY-CODE            PIC X(3).
          03 RT-HCO-CLASS-CODE                PIC X(4).
          03 RT-HCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HCO-RATED-PREMIUM             PIC 9(9)V9(2).
