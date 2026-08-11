******************************************************************
*  COPYBOOK  : GMWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : WA
******************************************************************
 01  RT-MWA-RATING.

          03 RT-MWA-TERRITORY-CODE            PIC X(3).
          03 RT-MWA-CLASS-CODE                PIC X(4).
          03 RT-MWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MWA-RATED-PREMIUM             PIC 9(9)V9(2).
