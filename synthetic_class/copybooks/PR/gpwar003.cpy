******************************************************************
*  COPYBOOK  : GPWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : WA
******************************************************************
 01  RT-PWA-RATING.

          03 RT-PWA-TERRITORY-CODE            PIC X(3).
          03 RT-PWA-CLASS-CODE                PIC X(4).
          03 RT-PWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PWA-RATED-PREMIUM             PIC 9(9)V9(2).
