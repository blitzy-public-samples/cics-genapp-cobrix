******************************************************************
*  COPYBOOK  : GUWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : WY
******************************************************************
 01  RT-UWY-RATING.

          03 RT-UWY-TERRITORY-CODE            PIC X(3).
          03 RT-UWY-CLASS-CODE                PIC X(4).
          03 RT-UWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UWY-RATED-PREMIUM             PIC 9(9)V9(2).
