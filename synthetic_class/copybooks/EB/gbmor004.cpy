******************************************************************
*  COPYBOOK  : GBMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : MO
******************************************************************
 01  RT-BMO-RATING.

          03 RT-BMO-TERRITORY-CODE            PIC X(3).
          03 RT-BMO-CLASS-CODE                PIC X(4).
          03 RT-BMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BMO-RATED-PREMIUM             PIC 9(9)V9(2).
