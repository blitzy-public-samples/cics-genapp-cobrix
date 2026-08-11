******************************************************************
*  COPYBOOK  : GBMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : MT
******************************************************************
 01  RT-BMT-RATING.

          03 RT-BMT-TERRITORY-CODE            PIC X(3).
          03 RT-BMT-CLASS-CODE                PIC X(4).
          03 RT-BMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BMT-RATED-PREMIUM             PIC 9(9)V9(2).
