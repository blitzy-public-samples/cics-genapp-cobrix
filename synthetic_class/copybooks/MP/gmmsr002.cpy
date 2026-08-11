******************************************************************
*  COPYBOOK  : GMMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MS
******************************************************************
 01  RT-MMS-RATING.

          03 RT-MMS-TERRITORY-CODE            PIC X(3).
          03 RT-MMS-CLASS-CODE                PIC X(4).
          03 RT-MMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MMS-RATED-PREMIUM             PIC 9(9)V9(2).
