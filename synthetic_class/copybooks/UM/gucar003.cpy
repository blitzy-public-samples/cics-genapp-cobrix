******************************************************************
*  COPYBOOK  : GUCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : CA
******************************************************************
 01  RT-UCA-RATING.

          03 RT-UCA-TERRITORY-CODE            PIC X(3).
          03 RT-UCA-CLASS-CODE                PIC X(4).
          03 RT-UCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UCA-RATED-PREMIUM             PIC 9(9)V9(2).
