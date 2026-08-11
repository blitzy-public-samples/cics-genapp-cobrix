******************************************************************
*  COPYBOOK  : GMNER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NE
******************************************************************
 01  RT-MNE-RATING.

          03 RT-MNE-TERRITORY-CODE            PIC X(3).
          03 RT-MNE-CLASS-CODE                PIC X(4).
          03 RT-MNE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MNE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MNE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MNE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MNE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MNE-RATED-PREMIUM             PIC 9(9)V9(2).
