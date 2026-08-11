******************************************************************
*  COPYBOOK  : GNINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : IN
******************************************************************
 01  RT-NIN-RATING.

          03 RT-NIN-TERRITORY-CODE            PIC X(3).
          03 RT-NIN-CLASS-CODE                PIC X(4).
          03 RT-NIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NIN-RATED-PREMIUM             PIC 9(9)V9(2).
