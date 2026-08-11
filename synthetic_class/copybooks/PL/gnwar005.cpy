******************************************************************
*  COPYBOOK  : GNWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : WA
******************************************************************
 01  RT-NWA-RATING.

          03 RT-NWA-TERRITORY-CODE            PIC X(3).
          03 RT-NWA-CLASS-CODE                PIC X(4).
          03 RT-NWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NWA-RATED-PREMIUM             PIC 9(9)V9(2).
