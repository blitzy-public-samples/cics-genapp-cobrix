******************************************************************
*  COPYBOOK  : GCVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : VT
******************************************************************
 01  RT-CVT-RATING.

          03 RT-CVT-TERRITORY-CODE            PIC X(3).
          03 RT-CVT-CLASS-CODE                PIC X(4).
          03 RT-CVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CVT-RATED-PREMIUM             PIC 9(9)V9(2).
