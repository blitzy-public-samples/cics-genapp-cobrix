******************************************************************
*  COPYBOOK  : GUNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : NH
******************************************************************
 01  RT-UNH-RATING.

          03 RT-UNH-TERRITORY-CODE            PIC X(3).
          03 RT-UNH-CLASS-CODE                PIC X(4).
          03 RT-UNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UNH-RATED-PREMIUM             PIC 9(9)V9(2).
