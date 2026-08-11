******************************************************************
*  COPYBOOK  : GHIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : IA
******************************************************************
 01  RT-HIA-RATING.

          03 RT-HIA-TERRITORY-CODE            PIC X(3).
          03 RT-HIA-CLASS-CODE                PIC X(4).
          03 RT-HIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HIA-RATED-PREMIUM             PIC 9(9)V9(2).
