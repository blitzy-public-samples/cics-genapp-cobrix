******************************************************************
*  COPYBOOK  : GUMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MS
******************************************************************
 01  RT-UMS-RATING.

          03 RT-UMS-TERRITORY-CODE            PIC X(3).
          03 RT-UMS-CLASS-CODE                PIC X(4).
          03 RT-UMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UMS-RATED-PREMIUM             PIC 9(9)V9(2).
