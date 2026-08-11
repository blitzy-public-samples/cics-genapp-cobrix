******************************************************************
*  COPYBOOK  : GBIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : IA
******************************************************************
 01  RT-BIA-RATING.

          03 RT-BIA-TERRITORY-CODE            PIC X(3).
          03 RT-BIA-CLASS-CODE                PIC X(4).
          03 RT-BIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BIA-RATED-PREMIUM             PIC 9(9)V9(2).
