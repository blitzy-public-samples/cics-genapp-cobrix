******************************************************************
*  COPYBOOK  : GHARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : AR
******************************************************************
 01  RT-HAR-RATING.

          03 RT-HAR-TERRITORY-CODE            PIC X(3).
          03 RT-HAR-CLASS-CODE                PIC X(4).
          03 RT-HAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HAR-RATED-PREMIUM             PIC 9(9)V9(2).
