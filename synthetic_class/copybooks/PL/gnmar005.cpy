******************************************************************
*  COPYBOOK  : GNMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : MA
******************************************************************
 01  RT-NMA-RATING.

          03 RT-NMA-TERRITORY-CODE            PIC X(3).
          03 RT-NMA-CLASS-CODE                PIC X(4).
          03 RT-NMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NMA-RATED-PREMIUM             PIC 9(9)V9(2).
