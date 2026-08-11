******************************************************************
*  COPYBOOK  : GUMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MD
******************************************************************
 01  RT-UMD-RATING.

          03 RT-UMD-TERRITORY-CODE            PIC X(3).
          03 RT-UMD-CLASS-CODE                PIC X(4).
          03 RT-UMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UMD-RATED-PREMIUM             PIC 9(9)V9(2).
