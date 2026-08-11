******************************************************************
*  COPYBOOK  : GMSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : SD
******************************************************************
 01  RT-MSD-RATING.

          03 RT-MSD-TERRITORY-CODE            PIC X(3).
          03 RT-MSD-CLASS-CODE                PIC X(4).
          03 RT-MSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MSD-RATED-PREMIUM             PIC 9(9)V9(2).
