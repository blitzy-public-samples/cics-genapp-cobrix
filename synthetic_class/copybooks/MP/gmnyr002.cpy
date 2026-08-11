******************************************************************
*  COPYBOOK  : GMNYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NY
******************************************************************
 01  RT-MNY-RATING.

          03 RT-MNY-TERRITORY-CODE            PIC X(3).
          03 RT-MNY-CLASS-CODE                PIC X(4).
          03 RT-MNY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MNY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MNY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MNY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MNY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MNY-RATED-PREMIUM             PIC 9(9)V9(2).
