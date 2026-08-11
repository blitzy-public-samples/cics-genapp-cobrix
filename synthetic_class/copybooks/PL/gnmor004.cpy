******************************************************************
*  COPYBOOK  : GNMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : MO
******************************************************************
 01  RT-NMO-RATING.

          03 RT-NMO-TERRITORY-CODE            PIC X(3).
          03 RT-NMO-CLASS-CODE                PIC X(4).
          03 RT-NMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NMO-RATED-PREMIUM             PIC 9(9)V9(2).
