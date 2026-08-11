******************************************************************
*  COPYBOOK  : GUOHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : OH
******************************************************************
 01  RT-UOH-RATING.

          03 RT-UOH-TERRITORY-CODE            PIC X(3).
          03 RT-UOH-CLASS-CODE                PIC X(4).
          03 RT-UOH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UOH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UOH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UOH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UOH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UOH-RATED-PREMIUM             PIC 9(9)V9(2).
