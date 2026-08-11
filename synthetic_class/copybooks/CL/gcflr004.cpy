******************************************************************
*  COPYBOOK  : GCFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : FL
******************************************************************
 01  RT-CFL-RATING.

          03 RT-CFL-TERRITORY-CODE            PIC X(3).
          03 RT-CFL-CLASS-CODE                PIC X(4).
          03 RT-CFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CFL-RATED-PREMIUM             PIC 9(9)V9(2).
