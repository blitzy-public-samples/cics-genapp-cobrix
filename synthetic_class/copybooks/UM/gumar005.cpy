******************************************************************
*  COPYBOOK  : GUMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MA
******************************************************************
 01  RT-UMA-RATING.

          03 RT-UMA-TERRITORY-CODE            PIC X(3).
          03 RT-UMA-CLASS-CODE                PIC X(4).
          03 RT-UMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UMA-RATED-PREMIUM             PIC 9(9)V9(2).
