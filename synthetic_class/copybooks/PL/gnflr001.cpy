******************************************************************
*  COPYBOOK  : GNFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : FL
******************************************************************
 01  RT-NFL-RATING.

          03 RT-NFL-TERRITORY-CODE            PIC X(3).
          03 RT-NFL-CLASS-CODE                PIC X(4).
          03 RT-NFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NFL-RATED-PREMIUM             PIC 9(9)V9(2).
