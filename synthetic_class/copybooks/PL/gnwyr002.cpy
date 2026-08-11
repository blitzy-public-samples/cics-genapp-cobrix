******************************************************************
*  COPYBOOK  : GNWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : WY
******************************************************************
 01  RT-NWY-RATING.

          03 RT-NWY-TERRITORY-CODE            PIC X(3).
          03 RT-NWY-CLASS-CODE                PIC X(4).
          03 RT-NWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NWY-RATED-PREMIUM             PIC 9(9)V9(2).
