******************************************************************
*  COPYBOOK  : GNGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : GA
******************************************************************
 01  RT-NGA-RATING.

          03 RT-NGA-TERRITORY-CODE            PIC X(3).
          03 RT-NGA-CLASS-CODE                PIC X(4).
          03 RT-NGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NGA-RATED-PREMIUM             PIC 9(9)V9(2).
