******************************************************************
*  COPYBOOK  : GHCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : CT
******************************************************************
 01  RT-HCT-RATING.

          03 RT-HCT-TERRITORY-CODE            PIC X(3).
          03 RT-HCT-CLASS-CODE                PIC X(4).
          03 RT-HCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HCT-RATED-PREMIUM             PIC 9(9)V9(2).
