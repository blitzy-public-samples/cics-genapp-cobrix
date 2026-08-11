******************************************************************
*  COPYBOOK  : GHAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : AK
******************************************************************
 01  RT-HAK-RATING.

          03 RT-HAK-TERRITORY-CODE            PIC X(3).
          03 RT-HAK-CLASS-CODE                PIC X(4).
          03 RT-HAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HAK-RATED-PREMIUM             PIC 9(9)V9(2).
