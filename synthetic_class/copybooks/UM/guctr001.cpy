******************************************************************
*  COPYBOOK  : GUCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : CT
******************************************************************
 01  RT-UCT-RATING.

          03 RT-UCT-TERRITORY-CODE            PIC X(3).
          03 RT-UCT-CLASS-CODE                PIC X(4).
          03 RT-UCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UCT-RATED-PREMIUM             PIC 9(9)V9(2).
