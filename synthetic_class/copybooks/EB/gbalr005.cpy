******************************************************************
*  COPYBOOK  : GBALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : AL
******************************************************************
 01  RT-BAL-RATING.

          03 RT-BAL-TERRITORY-CODE            PIC X(3).
          03 RT-BAL-CLASS-CODE                PIC X(4).
          03 RT-BAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BAL-RATED-PREMIUM             PIC 9(9)V9(2).
