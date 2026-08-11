******************************************************************
*  COPYBOOK  : GUNER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : NE
******************************************************************
 01  RT-UNE-RATING.

          03 RT-UNE-TERRITORY-CODE            PIC X(3).
          03 RT-UNE-CLASS-CODE                PIC X(4).
          03 RT-UNE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UNE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UNE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UNE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UNE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UNE-RATED-PREMIUM             PIC 9(9)V9(2).
