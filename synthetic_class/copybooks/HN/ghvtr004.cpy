******************************************************************
*  COPYBOOK  : GHVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : VT
******************************************************************
 01  RT-HVT-RATING.

          03 RT-HVT-TERRITORY-CODE            PIC X(3).
          03 RT-HVT-CLASS-CODE                PIC X(4).
          03 RT-HVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HVT-RATED-PREMIUM             PIC 9(9)V9(2).
