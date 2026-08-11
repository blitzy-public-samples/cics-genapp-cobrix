******************************************************************
*  COPYBOOK  : GNPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : PA
******************************************************************
 01  RT-NPA-RATING.

          03 RT-NPA-TERRITORY-CODE            PIC X(3).
          03 RT-NPA-CLASS-CODE                PIC X(4).
          03 RT-NPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NPA-RATED-PREMIUM             PIC 9(9)V9(2).
