******************************************************************
*  COPYBOOK  : GMMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MT
******************************************************************
 01  RT-MMT-RATING.

          03 RT-MMT-TERRITORY-CODE            PIC X(3).
          03 RT-MMT-CLASS-CODE                PIC X(4).
          03 RT-MMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MMT-RATED-PREMIUM             PIC 9(9)V9(2).
