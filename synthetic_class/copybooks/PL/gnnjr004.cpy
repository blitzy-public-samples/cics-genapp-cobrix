******************************************************************
*  COPYBOOK  : GNNJR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : NJ
******************************************************************
 01  RT-NNJ-RATING.

          03 RT-NNJ-TERRITORY-CODE            PIC X(3).
          03 RT-NNJ-CLASS-CODE                PIC X(4).
          03 RT-NNJ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NNJ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NNJ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NNJ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NNJ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NNJ-RATED-PREMIUM             PIC 9(9)V9(2).
