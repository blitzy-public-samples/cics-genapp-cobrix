******************************************************************
*  COPYBOOK  : GMNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NM
******************************************************************
 01  RT-MNM-RATING.

          03 RT-MNM-TERRITORY-CODE            PIC X(3).
          03 RT-MNM-CLASS-CODE                PIC X(4).
          03 RT-MNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MNM-RATED-PREMIUM             PIC 9(9)V9(2).
