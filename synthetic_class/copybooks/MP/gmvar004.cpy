******************************************************************
*  COPYBOOK  : GMVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : VA
******************************************************************
 01  RT-MVA-RATING.

          03 RT-MVA-TERRITORY-CODE            PIC X(3).
          03 RT-MVA-CLASS-CODE                PIC X(4).
          03 RT-MVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MVA-RATED-PREMIUM             PIC 9(9)V9(2).
