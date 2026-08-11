******************************************************************
*  COPYBOOK  : GMCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : CA
******************************************************************
 01  RT-MCA-RATING.

          03 RT-MCA-TERRITORY-CODE            PIC X(3).
          03 RT-MCA-CLASS-CODE                PIC X(4).
          03 RT-MCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MCA-RATED-PREMIUM             PIC 9(9)V9(2).
