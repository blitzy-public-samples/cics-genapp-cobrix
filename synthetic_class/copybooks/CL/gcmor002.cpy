******************************************************************
*  COPYBOOK  : GCMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MO
******************************************************************
 01  RT-CMO-RATING.

          03 RT-CMO-TERRITORY-CODE            PIC X(3).
          03 RT-CMO-CLASS-CODE                PIC X(4).
          03 RT-CMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CMO-RATED-PREMIUM             PIC 9(9)V9(2).
