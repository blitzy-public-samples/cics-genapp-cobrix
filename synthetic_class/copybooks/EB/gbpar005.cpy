******************************************************************
*  COPYBOOK  : GBPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : PA
******************************************************************
 01  RT-BPA-RATING.

          03 RT-BPA-TERRITORY-CODE            PIC X(3).
          03 RT-BPA-CLASS-CODE                PIC X(4).
          03 RT-BPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BPA-RATED-PREMIUM             PIC 9(9)V9(2).
