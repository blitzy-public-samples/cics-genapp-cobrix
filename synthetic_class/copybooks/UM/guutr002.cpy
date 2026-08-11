******************************************************************
*  COPYBOOK  : GUUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : UT
******************************************************************
 01  RT-UUT-RATING.

          03 RT-UUT-TERRITORY-CODE            PIC X(3).
          03 RT-UUT-CLASS-CODE                PIC X(4).
          03 RT-UUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UUT-RATED-PREMIUM             PIC 9(9)V9(2).
