******************************************************************
*  COPYBOOK  : GMNJR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NJ
******************************************************************
 01  RT-MNJ-RATING.

          03 RT-MNJ-TERRITORY-CODE            PIC X(3).
          03 RT-MNJ-CLASS-CODE                PIC X(4).
          03 RT-MNJ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MNJ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MNJ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MNJ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MNJ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MNJ-RATED-PREMIUM             PIC 9(9)V9(2).
