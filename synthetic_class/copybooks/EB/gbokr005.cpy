******************************************************************
*  COPYBOOK  : GBOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : OK
******************************************************************
 01  RT-BOK-RATING.

          03 RT-BOK-TERRITORY-CODE            PIC X(3).
          03 RT-BOK-CLASS-CODE                PIC X(4).
          03 RT-BOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BOK-RATED-PREMIUM             PIC 9(9)V9(2).
