******************************************************************
*  COPYBOOK  : GBSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : SC
******************************************************************
 01  RT-BSC-RATING.

          03 RT-BSC-TERRITORY-CODE            PIC X(3).
          03 RT-BSC-CLASS-CODE                PIC X(4).
          03 RT-BSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BSC-RATED-PREMIUM             PIC 9(9)V9(2).
