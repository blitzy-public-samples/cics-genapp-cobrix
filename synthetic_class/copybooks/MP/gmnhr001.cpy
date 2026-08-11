******************************************************************
*  COPYBOOK  : GMNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NH
******************************************************************
 01  RT-MNH-RATING.

          03 RT-MNH-TERRITORY-CODE            PIC X(3).
          03 RT-MNH-CLASS-CODE                PIC X(4).
          03 RT-MNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MNH-RATED-PREMIUM             PIC 9(9)V9(2).
