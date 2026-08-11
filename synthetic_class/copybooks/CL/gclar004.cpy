******************************************************************
*  COPYBOOK  : GCLAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : LA
******************************************************************
 01  RT-CLA-RATING.

          03 RT-CLA-TERRITORY-CODE            PIC X(3).
          03 RT-CLA-CLASS-CODE                PIC X(4).
          03 RT-CLA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CLA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CLA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CLA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CLA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CLA-RATED-PREMIUM             PIC 9(9)V9(2).
