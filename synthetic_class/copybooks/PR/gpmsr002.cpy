******************************************************************
*  COPYBOOK  : GPMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : MS
******************************************************************
 01  RT-PMS-RATING.

          03 RT-PMS-TERRITORY-CODE            PIC X(3).
          03 RT-PMS-CLASS-CODE                PIC X(4).
          03 RT-PMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PMS-RATED-PREMIUM             PIC 9(9)V9(2).
