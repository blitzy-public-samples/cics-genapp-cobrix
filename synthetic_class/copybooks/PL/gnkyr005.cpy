******************************************************************
*  COPYBOOK  : GNKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : KY
******************************************************************
 01  RT-NKY-RATING.

          03 RT-NKY-TERRITORY-CODE            PIC X(3).
          03 RT-NKY-CLASS-CODE                PIC X(4).
          03 RT-NKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NKY-RATED-PREMIUM             PIC 9(9)V9(2).
