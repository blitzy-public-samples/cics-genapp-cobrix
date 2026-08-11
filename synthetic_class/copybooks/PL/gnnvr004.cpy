******************************************************************
*  COPYBOOK  : GNNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : NV
******************************************************************
 01  RT-NNV-RATING.

          03 RT-NNV-TERRITORY-CODE            PIC X(3).
          03 RT-NNV-CLASS-CODE                PIC X(4).
          03 RT-NNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NNV-RATED-PREMIUM             PIC 9(9)V9(2).
