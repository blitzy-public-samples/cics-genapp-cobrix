******************************************************************
*  COPYBOOK  : GUILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : IL
******************************************************************
 01  RT-UIL-RATING.

          03 RT-UIL-TERRITORY-CODE            PIC X(3).
          03 RT-UIL-CLASS-CODE                PIC X(4).
          03 RT-UIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UIL-RATED-PREMIUM             PIC 9(9)V9(2).
