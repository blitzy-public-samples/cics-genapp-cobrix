******************************************************************
*  COPYBOOK  : GNMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : MT
******************************************************************
 01  RT-NMT-RATING.

          03 RT-NMT-TERRITORY-CODE            PIC X(3).
          03 RT-NMT-CLASS-CODE                PIC X(4).
          03 RT-NMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NMT-RATED-PREMIUM             PIC 9(9)V9(2).
