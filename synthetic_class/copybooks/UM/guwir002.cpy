******************************************************************
*  COPYBOOK  : GUWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : WI
******************************************************************
 01  RT-UWI-RATING.

          03 RT-UWI-TERRITORY-CODE            PIC X(3).
          03 RT-UWI-CLASS-CODE                PIC X(4).
          03 RT-UWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UWI-RATED-PREMIUM             PIC 9(9)V9(2).
