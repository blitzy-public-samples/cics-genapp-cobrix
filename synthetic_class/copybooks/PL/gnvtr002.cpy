******************************************************************
*  COPYBOOK  : GNVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : VT
******************************************************************
 01  RT-NVT-RATING.

          03 RT-NVT-TERRITORY-CODE            PIC X(3).
          03 RT-NVT-CLASS-CODE                PIC X(4).
          03 RT-NVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NVT-RATED-PREMIUM             PIC 9(9)V9(2).
