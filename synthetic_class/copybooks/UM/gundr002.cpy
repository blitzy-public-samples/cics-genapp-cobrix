******************************************************************
*  COPYBOOK  : GUNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : ND
******************************************************************
 01  RT-UND-RATING.

          03 RT-UND-TERRITORY-CODE            PIC X(3).
          03 RT-UND-CLASS-CODE                PIC X(4).
          03 RT-UND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UND-RATED-PREMIUM             PIC 9(9)V9(2).
