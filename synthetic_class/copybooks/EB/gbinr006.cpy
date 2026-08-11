******************************************************************
*  COPYBOOK  : GBINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : IN
******************************************************************
 01  RT-BIN-RATING.

          03 RT-BIN-TERRITORY-CODE            PIC X(3).
          03 RT-BIN-CLASS-CODE                PIC X(4).
          03 RT-BIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BIN-RATED-PREMIUM             PIC 9(9)V9(2).
