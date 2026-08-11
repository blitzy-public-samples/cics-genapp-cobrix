******************************************************************
*  COPYBOOK  : GMMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MI
******************************************************************
 01  RT-MMI-RATING.

          03 RT-MMI-TERRITORY-CODE            PIC X(3).
          03 RT-MMI-CLASS-CODE                PIC X(4).
          03 RT-MMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MMI-RATED-PREMIUM             PIC 9(9)V9(2).
