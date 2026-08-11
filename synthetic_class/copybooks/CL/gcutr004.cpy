******************************************************************
*  COPYBOOK  : GCUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : UT
******************************************************************
 01  RT-CUT-RATING.

          03 RT-CUT-TERRITORY-CODE            PIC X(3).
          03 RT-CUT-CLASS-CODE                PIC X(4).
          03 RT-CUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CUT-RATED-PREMIUM             PIC 9(9)V9(2).
