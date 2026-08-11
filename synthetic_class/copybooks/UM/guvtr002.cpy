******************************************************************
*  COPYBOOK  : GUVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : VT
******************************************************************
 01  RT-UVT-RATING.

          03 RT-UVT-TERRITORY-CODE            PIC X(3).
          03 RT-UVT-CLASS-CODE                PIC X(4).
          03 RT-UVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UVT-RATED-PREMIUM             PIC 9(9)V9(2).
