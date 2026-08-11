******************************************************************
*  COPYBOOK  : GUAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : AK
******************************************************************
 01  RT-UAK-RATING.

          03 RT-UAK-TERRITORY-CODE            PIC X(3).
          03 RT-UAK-CLASS-CODE                PIC X(4).
          03 RT-UAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UAK-RATED-PREMIUM             PIC 9(9)V9(2).
