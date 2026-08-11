******************************************************************
*  COPYBOOK  : GMNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NC
******************************************************************
 01  RT-MNC-RATING.

          03 RT-MNC-TERRITORY-CODE            PIC X(3).
          03 RT-MNC-CLASS-CODE                PIC X(4).
          03 RT-MNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MNC-RATED-PREMIUM             PIC 9(9)V9(2).
