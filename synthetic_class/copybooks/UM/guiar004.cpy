******************************************************************
*  COPYBOOK  : GUIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : IA
******************************************************************
 01  RT-UIA-RATING.

          03 RT-UIA-TERRITORY-CODE            PIC X(3).
          03 RT-UIA-CLASS-CODE                PIC X(4).
          03 RT-UIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UIA-RATED-PREMIUM             PIC 9(9)V9(2).
