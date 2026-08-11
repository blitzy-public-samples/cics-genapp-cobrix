******************************************************************
*  COPYBOOK  : GNSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : SD
******************************************************************
 01  RT-NSD-RATING.

          03 RT-NSD-TERRITORY-CODE            PIC X(3).
          03 RT-NSD-CLASS-CODE                PIC X(4).
          03 RT-NSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NSD-RATED-PREMIUM             PIC 9(9)V9(2).
