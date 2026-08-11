******************************************************************
*  COPYBOOK  : GCCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : CO
******************************************************************
 01  RT-CCO-RATING.

          03 RT-CCO-TERRITORY-CODE            PIC X(3).
          03 RT-CCO-CLASS-CODE                PIC X(4).
          03 RT-CCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CCO-RATED-PREMIUM             PIC 9(9)V9(2).
