******************************************************************
*  COPYBOOK  : GCARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : AR
******************************************************************
 01  RT-CAR-RATING.

          03 RT-CAR-TERRITORY-CODE            PIC X(3).
          03 RT-CAR-CLASS-CODE                PIC X(4).
          03 RT-CAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CAR-RATED-PREMIUM             PIC 9(9)V9(2).
