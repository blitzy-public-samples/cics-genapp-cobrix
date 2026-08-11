******************************************************************
*  COPYBOOK  : GMUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : UT
******************************************************************
 01  RT-MUT-RATING.

          03 RT-MUT-TERRITORY-CODE            PIC X(3).
          03 RT-MUT-CLASS-CODE                PIC X(4).
          03 RT-MUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MUT-RATED-PREMIUM             PIC 9(9)V9(2).
