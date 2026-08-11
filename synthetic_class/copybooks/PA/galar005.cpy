******************************************************************
*  COPYBOOK  : GALAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : LA
******************************************************************
 01  RT-ALA-RATING.

          03 RT-ALA-TERRITORY-CODE            PIC X(3).
          03 RT-ALA-CLASS-CODE                PIC X(4).
          03 RT-ALA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ALA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ALA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ALA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ALA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ALA-RATED-PREMIUM             PIC 9(9)V9(2).
