******************************************************************
*  COPYBOOK  : GCNER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : NE
******************************************************************
 01  RT-CNE-RATING.

          03 RT-CNE-TERRITORY-CODE            PIC X(3).
          03 RT-CNE-CLASS-CODE                PIC X(4).
          03 RT-CNE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CNE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CNE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CNE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CNE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CNE-RATED-PREMIUM             PIC 9(9)V9(2).
