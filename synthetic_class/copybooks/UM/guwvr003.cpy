******************************************************************
*  COPYBOOK  : GUWVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : WV
******************************************************************
 01  RT-UWV-RATING.

          03 RT-UWV-TERRITORY-CODE            PIC X(3).
          03 RT-UWV-CLASS-CODE                PIC X(4).
          03 RT-UWV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UWV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UWV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UWV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UWV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UWV-RATED-PREMIUM             PIC 9(9)V9(2).
