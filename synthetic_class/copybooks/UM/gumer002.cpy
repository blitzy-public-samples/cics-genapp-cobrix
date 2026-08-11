******************************************************************
*  COPYBOOK  : GUMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : ME
******************************************************************
 01  RT-UME-RATING.

          03 RT-UME-TERRITORY-CODE            PIC X(3).
          03 RT-UME-CLASS-CODE                PIC X(4).
          03 RT-UME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UME-RATED-PREMIUM             PIC 9(9)V9(2).
