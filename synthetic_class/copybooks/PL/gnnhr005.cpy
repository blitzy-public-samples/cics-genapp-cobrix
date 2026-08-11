******************************************************************
*  COPYBOOK  : GNNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : NH
******************************************************************
 01  RT-NNH-RATING.

          03 RT-NNH-TERRITORY-CODE            PIC X(3).
          03 RT-NNH-CLASS-CODE                PIC X(4).
          03 RT-NNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NNH-RATED-PREMIUM             PIC 9(9)V9(2).
