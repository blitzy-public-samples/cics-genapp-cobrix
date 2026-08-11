******************************************************************
*  COPYBOOK  : GAIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : IA
******************************************************************
 01  RT-AIA-RATING.

          03 RT-AIA-TERRITORY-CODE            PIC X(3).
          03 RT-AIA-CLASS-CODE                PIC X(4).
          03 RT-AIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AIA-RATED-PREMIUM             PIC 9(9)V9(2).
