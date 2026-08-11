******************************************************************
*  COPYBOOK  : GBHIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : HI
******************************************************************
 01  RT-BHI-RATING.

          03 RT-BHI-TERRITORY-CODE            PIC X(3).
          03 RT-BHI-CLASS-CODE                PIC X(4).
          03 RT-BHI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BHI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BHI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BHI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BHI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BHI-RATED-PREMIUM             PIC 9(9)V9(2).
