******************************************************************
*  COPYBOOK  : GMFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : FL
******************************************************************
 01  RT-MFL-RATING.

          03 RT-MFL-TERRITORY-CODE            PIC X(3).
          03 RT-MFL-CLASS-CODE                PIC X(4).
          03 RT-MFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MFL-RATED-PREMIUM             PIC 9(9)V9(2).
