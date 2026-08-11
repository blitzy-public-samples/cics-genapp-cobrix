******************************************************************
*  COPYBOOK  : GAGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : GA
******************************************************************
 01  RT-AGA-RATING.

          03 RT-AGA-TERRITORY-CODE            PIC X(3).
          03 RT-AGA-CLASS-CODE                PIC X(4).
          03 RT-AGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AGA-RATED-PREMIUM             PIC 9(9)V9(2).
