******************************************************************
*  COPYBOOK  : GUVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : VA
******************************************************************
 01  RT-UVA-RATING.

          03 RT-UVA-TERRITORY-CODE            PIC X(3).
          03 RT-UVA-CLASS-CODE                PIC X(4).
          03 RT-UVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UVA-RATED-PREMIUM             PIC 9(9)V9(2).
