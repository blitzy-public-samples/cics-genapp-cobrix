******************************************************************
*  COPYBOOK  : GUALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : AL
******************************************************************
 01  RT-UAL-RATING.

          03 RT-UAL-TERRITORY-CODE            PIC X(3).
          03 RT-UAL-CLASS-CODE                PIC X(4).
          03 RT-UAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UAL-RATED-PREMIUM             PIC 9(9)V9(2).
