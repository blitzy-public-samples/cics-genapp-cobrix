******************************************************************
*  COPYBOOK  : GNIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : IA
******************************************************************
 01  RT-NIA-RATING.

          03 RT-NIA-TERRITORY-CODE            PIC X(3).
          03 RT-NIA-CLASS-CODE                PIC X(4).
          03 RT-NIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NIA-RATED-PREMIUM             PIC 9(9)V9(2).
