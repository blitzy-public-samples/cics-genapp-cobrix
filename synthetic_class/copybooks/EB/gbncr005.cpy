******************************************************************
*  COPYBOOK  : GBNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : NC
******************************************************************
 01  RT-BNC-RATING.

          03 RT-BNC-TERRITORY-CODE            PIC X(3).
          03 RT-BNC-CLASS-CODE                PIC X(4).
          03 RT-BNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BNC-RATED-PREMIUM             PIC 9(9)V9(2).
