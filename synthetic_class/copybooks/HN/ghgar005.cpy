******************************************************************
*  COPYBOOK  : GHGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : GA
******************************************************************
 01  RT-HGA-RATING.

          03 RT-HGA-TERRITORY-CODE            PIC X(3).
          03 RT-HGA-CLASS-CODE                PIC X(4).
          03 RT-HGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HGA-RATED-PREMIUM             PIC 9(9)V9(2).
