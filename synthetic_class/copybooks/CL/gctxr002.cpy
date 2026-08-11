******************************************************************
*  COPYBOOK  : GCTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : TX
******************************************************************
 01  RT-CTX-RATING.

          03 RT-CTX-TERRITORY-CODE            PIC X(3).
          03 RT-CTX-CLASS-CODE                PIC X(4).
          03 RT-CTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CTX-RATED-PREMIUM             PIC 9(9)V9(2).
