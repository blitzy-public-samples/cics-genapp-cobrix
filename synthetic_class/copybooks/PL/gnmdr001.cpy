******************************************************************
*  COPYBOOK  : GNMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : MD
******************************************************************
 01  RT-NMD-RATING.

          03 RT-NMD-TERRITORY-CODE            PIC X(3).
          03 RT-NMD-CLASS-CODE                PIC X(4).
          03 RT-NMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NMD-RATED-PREMIUM             PIC 9(9)V9(2).
