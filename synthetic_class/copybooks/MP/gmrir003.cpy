******************************************************************
*  COPYBOOK  : GMRIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : RI
******************************************************************
 01  RT-MRI-RATING.

          03 RT-MRI-TERRITORY-CODE            PIC X(3).
          03 RT-MRI-CLASS-CODE                PIC X(4).
          03 RT-MRI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MRI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MRI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MRI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MRI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MRI-RATED-PREMIUM             PIC 9(9)V9(2).
