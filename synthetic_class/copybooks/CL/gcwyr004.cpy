******************************************************************
*  COPYBOOK  : GCWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : WY
******************************************************************
 01  RT-CWY-RATING.

          03 RT-CWY-TERRITORY-CODE            PIC X(3).
          03 RT-CWY-CLASS-CODE                PIC X(4).
          03 RT-CWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CWY-RATED-PREMIUM             PIC 9(9)V9(2).
