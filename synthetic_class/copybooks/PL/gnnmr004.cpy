******************************************************************
*  COPYBOOK  : GNNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : NM
******************************************************************
 01  RT-NNM-RATING.

          03 RT-NNM-TERRITORY-CODE            PIC X(3).
          03 RT-NNM-CLASS-CODE                PIC X(4).
          03 RT-NNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NNM-RATED-PREMIUM             PIC 9(9)V9(2).
