******************************************************************
*  COPYBOOK  : GMLAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : LA
******************************************************************
 01  RT-MLA-RATING.

          03 RT-MLA-TERRITORY-CODE            PIC X(3).
          03 RT-MLA-CLASS-CODE                PIC X(4).
          03 RT-MLA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MLA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MLA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MLA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MLA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MLA-RATED-PREMIUM             PIC 9(9)V9(2).
