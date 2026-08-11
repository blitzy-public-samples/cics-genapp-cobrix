******************************************************************
*  COPYBOOK  : GCNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : NH
******************************************************************
 01  RT-CNH-RATING.

          03 RT-CNH-TERRITORY-CODE            PIC X(3).
          03 RT-CNH-CLASS-CODE                PIC X(4).
          03 RT-CNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CNH-RATED-PREMIUM             PIC 9(9)V9(2).
