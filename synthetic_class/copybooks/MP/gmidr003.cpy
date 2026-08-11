******************************************************************
*  COPYBOOK  : GMIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : ID
******************************************************************
 01  RT-MID-RATING.

          03 RT-MID-TERRITORY-CODE            PIC X(3).
          03 RT-MID-CLASS-CODE                PIC X(4).
          03 RT-MID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MID-RATED-PREMIUM             PIC 9(9)V9(2).
