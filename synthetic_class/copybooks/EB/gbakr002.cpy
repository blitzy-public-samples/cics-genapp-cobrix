******************************************************************
*  COPYBOOK  : GBAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : AK
******************************************************************
 01  RT-BAK-RATING.

          03 RT-BAK-TERRITORY-CODE            PIC X(3).
          03 RT-BAK-CLASS-CODE                PIC X(4).
          03 RT-BAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BAK-RATED-PREMIUM             PIC 9(9)V9(2).
