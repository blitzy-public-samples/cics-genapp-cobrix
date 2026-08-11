******************************************************************
*  COPYBOOK  : GNMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : ME
******************************************************************
 01  RT-NME-RATING.

          03 RT-NME-TERRITORY-CODE            PIC X(3).
          03 RT-NME-CLASS-CODE                PIC X(4).
          03 RT-NME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NME-RATED-PREMIUM             PIC 9(9)V9(2).
