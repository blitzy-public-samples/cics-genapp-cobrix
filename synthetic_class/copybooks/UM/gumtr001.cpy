******************************************************************
*  COPYBOOK  : GUMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MT
******************************************************************
 01  RT-UMT-RATING.

          03 RT-UMT-TERRITORY-CODE            PIC X(3).
          03 RT-UMT-CLASS-CODE                PIC X(4).
          03 RT-UMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UMT-RATED-PREMIUM             PIC 9(9)V9(2).
