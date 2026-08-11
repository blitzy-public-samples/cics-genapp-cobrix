******************************************************************
*  COPYBOOK  : GMOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : OK
******************************************************************
 01  RT-MOK-RATING.

          03 RT-MOK-TERRITORY-CODE            PIC X(3).
          03 RT-MOK-CLASS-CODE                PIC X(4).
          03 RT-MOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MOK-RATED-PREMIUM             PIC 9(9)V9(2).
