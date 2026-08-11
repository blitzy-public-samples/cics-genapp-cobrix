******************************************************************
*  COPYBOOK  : GCPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : PA
******************************************************************
 01  RT-CPA-RATING.

          03 RT-CPA-TERRITORY-CODE            PIC X(3).
          03 RT-CPA-CLASS-CODE                PIC X(4).
          03 RT-CPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CPA-RATED-PREMIUM             PIC 9(9)V9(2).
