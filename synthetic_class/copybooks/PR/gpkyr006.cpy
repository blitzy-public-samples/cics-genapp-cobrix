******************************************************************
*  COPYBOOK  : GPKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : KY
******************************************************************
 01  RT-PKY-RATING.

          03 RT-PKY-TERRITORY-CODE            PIC X(3).
          03 RT-PKY-CLASS-CODE                PIC X(4).
          03 RT-PKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PKY-RATED-PREMIUM             PIC 9(9)V9(2).
