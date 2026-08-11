******************************************************************
*  COPYBOOK  : GMCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : CT
******************************************************************
 01  RT-MCT-RATING.

          03 RT-MCT-TERRITORY-CODE            PIC X(3).
          03 RT-MCT-CLASS-CODE                PIC X(4).
          03 RT-MCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MCT-RATED-PREMIUM             PIC 9(9)V9(2).
