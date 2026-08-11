******************************************************************
*  COPYBOOK  : GUAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : AZ
******************************************************************
 01  RT-UAZ-RATING.

          03 RT-UAZ-TERRITORY-CODE            PIC X(3).
          03 RT-UAZ-CLASS-CODE                PIC X(4).
          03 RT-UAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UAZ-RATED-PREMIUM             PIC 9(9)V9(2).
