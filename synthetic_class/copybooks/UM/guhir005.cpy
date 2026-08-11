******************************************************************
*  COPYBOOK  : GUHIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : HI
******************************************************************
 01  RT-UHI-RATING.

          03 RT-UHI-TERRITORY-CODE            PIC X(3).
          03 RT-UHI-CLASS-CODE                PIC X(4).
          03 RT-UHI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UHI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UHI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UHI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UHI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UHI-RATED-PREMIUM             PIC 9(9)V9(2).
