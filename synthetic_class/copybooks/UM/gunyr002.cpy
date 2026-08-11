******************************************************************
*  COPYBOOK  : GUNYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : NY
******************************************************************
 01  RT-UNY-RATING.

          03 RT-UNY-TERRITORY-CODE            PIC X(3).
          03 RT-UNY-CLASS-CODE                PIC X(4).
          03 RT-UNY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UNY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UNY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UNY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UNY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UNY-RATED-PREMIUM             PIC 9(9)V9(2).
