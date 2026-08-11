******************************************************************
*  COPYBOOK  : GHMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : ME
******************************************************************
 01  RT-HME-RATING.

          03 RT-HME-TERRITORY-CODE            PIC X(3).
          03 RT-HME-CLASS-CODE                PIC X(4).
          03 RT-HME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HME-RATED-PREMIUM             PIC 9(9)V9(2).
