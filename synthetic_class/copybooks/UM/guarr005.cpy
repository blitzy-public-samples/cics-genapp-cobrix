******************************************************************
*  COPYBOOK  : GUARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : AR
******************************************************************
 01  RT-UAR-RATING.

          03 RT-UAR-TERRITORY-CODE            PIC X(3).
          03 RT-UAR-CLASS-CODE                PIC X(4).
          03 RT-UAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UAR-RATED-PREMIUM             PIC 9(9)V9(2).
