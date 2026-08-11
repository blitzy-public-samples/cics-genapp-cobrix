******************************************************************
*  COPYBOOK  : GCWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : WA
******************************************************************
 01  RT-CWA-RATING.

          03 RT-CWA-TERRITORY-CODE            PIC X(3).
          03 RT-CWA-CLASS-CODE                PIC X(4).
          03 RT-CWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CWA-RATED-PREMIUM             PIC 9(9)V9(2).
