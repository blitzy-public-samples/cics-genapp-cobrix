******************************************************************
*  COPYBOOK  : GCKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : KY
******************************************************************
 01  RT-CKY-RATING.

          03 RT-CKY-TERRITORY-CODE            PIC X(3).
          03 RT-CKY-CLASS-CODE                PIC X(4).
          03 RT-CKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CKY-RATED-PREMIUM             PIC 9(9)V9(2).
