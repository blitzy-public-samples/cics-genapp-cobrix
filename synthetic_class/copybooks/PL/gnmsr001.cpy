******************************************************************
*  COPYBOOK  : GNMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : MS
******************************************************************
 01  RT-NMS-RATING.

          03 RT-NMS-TERRITORY-CODE            PIC X(3).
          03 RT-NMS-CLASS-CODE                PIC X(4).
          03 RT-NMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NMS-RATED-PREMIUM             PIC 9(9)V9(2).
