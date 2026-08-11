******************************************************************
*  COPYBOOK  : GUPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : PA
******************************************************************
 01  RT-UPA-RATING.

          03 RT-UPA-TERRITORY-CODE            PIC X(3).
          03 RT-UPA-CLASS-CODE                PIC X(4).
          03 RT-UPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UPA-RATED-PREMIUM             PIC 9(9)V9(2).
