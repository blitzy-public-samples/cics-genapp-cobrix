******************************************************************
*  COPYBOOK  : GCRIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : RI
******************************************************************
 01  RT-CRI-RATING.

          03 RT-CRI-TERRITORY-CODE            PIC X(3).
          03 RT-CRI-CLASS-CODE                PIC X(4).
          03 RT-CRI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CRI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CRI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CRI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CRI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CRI-RATED-PREMIUM             PIC 9(9)V9(2).
