******************************************************************
*  COPYBOOK  : GULAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : LA
******************************************************************
 01  RT-ULA-RATING.

          03 RT-ULA-TERRITORY-CODE            PIC X(3).
          03 RT-ULA-CLASS-CODE                PIC X(4).
          03 RT-ULA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ULA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ULA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ULA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ULA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ULA-RATED-PREMIUM             PIC 9(9)V9(2).
