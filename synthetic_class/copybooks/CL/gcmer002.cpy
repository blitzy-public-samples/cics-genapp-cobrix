******************************************************************
*  COPYBOOK  : GCMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : ME
******************************************************************
 01  RT-CME-RATING.

          03 RT-CME-TERRITORY-CODE            PIC X(3).
          03 RT-CME-CLASS-CODE                PIC X(4).
          03 RT-CME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CME-RATED-PREMIUM             PIC 9(9)V9(2).
