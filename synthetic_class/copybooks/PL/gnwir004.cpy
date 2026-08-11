******************************************************************
*  COPYBOOK  : GNWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : WI
******************************************************************
 01  RT-NWI-RATING.

          03 RT-NWI-TERRITORY-CODE            PIC X(3).
          03 RT-NWI-CLASS-CODE                PIC X(4).
          03 RT-NWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NWI-RATED-PREMIUM             PIC 9(9)V9(2).
