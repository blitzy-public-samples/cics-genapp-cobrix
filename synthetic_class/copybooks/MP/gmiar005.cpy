******************************************************************
*  COPYBOOK  : GMIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : IA
******************************************************************
 01  RT-MIA-RATING.

          03 RT-MIA-TERRITORY-CODE            PIC X(3).
          03 RT-MIA-CLASS-CODE                PIC X(4).
          03 RT-MIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MIA-RATED-PREMIUM             PIC 9(9)V9(2).
