******************************************************************
*  COPYBOOK  : GUNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : NC
******************************************************************
 01  RT-UNC-RATING.

          03 RT-UNC-TERRITORY-CODE            PIC X(3).
          03 RT-UNC-CLASS-CODE                PIC X(4).
          03 RT-UNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UNC-RATED-PREMIUM             PIC 9(9)V9(2).
