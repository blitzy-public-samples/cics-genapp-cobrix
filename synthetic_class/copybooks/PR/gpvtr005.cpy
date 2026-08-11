******************************************************************
*  COPYBOOK  : GPVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : VT
******************************************************************
 01  RT-PVT-RATING.

          03 RT-PVT-TERRITORY-CODE            PIC X(3).
          03 RT-PVT-CLASS-CODE                PIC X(4).
          03 RT-PVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PVT-RATED-PREMIUM             PIC 9(9)V9(2).
