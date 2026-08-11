******************************************************************
*  COPYBOOK  : GBCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : CO
******************************************************************
 01  RT-BCO-RATING.

          03 RT-BCO-TERRITORY-CODE            PIC X(3).
          03 RT-BCO-CLASS-CODE                PIC X(4).
          03 RT-BCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BCO-RATED-PREMIUM             PIC 9(9)V9(2).
