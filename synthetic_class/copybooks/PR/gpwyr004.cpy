******************************************************************
*  COPYBOOK  : GPWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : WY
******************************************************************
 01  RT-PWY-RATING.

          03 RT-PWY-TERRITORY-CODE            PIC X(3).
          03 RT-PWY-CLASS-CODE                PIC X(4).
          03 RT-PWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PWY-RATED-PREMIUM             PIC 9(9)V9(2).
