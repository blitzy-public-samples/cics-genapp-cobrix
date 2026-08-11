******************************************************************
*  COPYBOOK  : GBNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : NM
******************************************************************
 01  RT-BNM-RATING.

          03 RT-BNM-TERRITORY-CODE            PIC X(3).
          03 RT-BNM-CLASS-CODE                PIC X(4).
          03 RT-BNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BNM-RATED-PREMIUM             PIC 9(9)V9(2).
