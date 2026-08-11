******************************************************************
*  COPYBOOK  : GBGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : GA
******************************************************************
 01  RT-BGA-RATING.

          03 RT-BGA-TERRITORY-CODE            PIC X(3).
          03 RT-BGA-CLASS-CODE                PIC X(4).
          03 RT-BGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BGA-RATED-PREMIUM             PIC 9(9)V9(2).
