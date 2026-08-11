******************************************************************
*  COPYBOOK  : GCWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : WI
******************************************************************
 01  RT-CWI-RATING.

          03 RT-CWI-TERRITORY-CODE            PIC X(3).
          03 RT-CWI-CLASS-CODE                PIC X(4).
          03 RT-CWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CWI-RATED-PREMIUM             PIC 9(9)V9(2).
