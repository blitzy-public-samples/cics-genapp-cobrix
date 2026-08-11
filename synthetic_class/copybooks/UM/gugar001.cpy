******************************************************************
*  COPYBOOK  : GUGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : GA
******************************************************************
 01  RT-UGA-RATING.

          03 RT-UGA-TERRITORY-CODE            PIC X(3).
          03 RT-UGA-CLASS-CODE                PIC X(4).
          03 RT-UGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UGA-RATED-PREMIUM             PIC 9(9)V9(2).
