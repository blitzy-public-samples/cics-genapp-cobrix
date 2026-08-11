******************************************************************
*  COPYBOOK  : GPCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : CO
******************************************************************
 01  RT-PCO-RATING.

          03 RT-PCO-TERRITORY-CODE            PIC X(3).
          03 RT-PCO-CLASS-CODE                PIC X(4).
          03 RT-PCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PCO-RATED-PREMIUM             PIC 9(9)V9(2).
