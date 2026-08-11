******************************************************************
*  COPYBOOK  : GMINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : IN
******************************************************************
 01  RT-MIN-RATING.

          03 RT-MIN-TERRITORY-CODE            PIC X(3).
          03 RT-MIN-CLASS-CODE                PIC X(4).
          03 RT-MIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MIN-RATED-PREMIUM             PIC 9(9)V9(2).
