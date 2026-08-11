******************************************************************
*  COPYBOOK  : GNDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : DE
******************************************************************
 01  RT-NDE-RATING.

          03 RT-NDE-TERRITORY-CODE            PIC X(3).
          03 RT-NDE-CLASS-CODE                PIC X(4).
          03 RT-NDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NDE-RATED-PREMIUM             PIC 9(9)V9(2).
