******************************************************************
*  COPYBOOK  : GUWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : WA
******************************************************************
 01  RT-UWA-RATING.

          03 RT-UWA-TERRITORY-CODE            PIC X(3).
          03 RT-UWA-CLASS-CODE                PIC X(4).
          03 RT-UWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UWA-RATED-PREMIUM             PIC 9(9)V9(2).
