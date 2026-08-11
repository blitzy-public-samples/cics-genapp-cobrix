******************************************************************
*  COPYBOOK  : GHMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : MT
******************************************************************
 01  RT-HMT-RATING.

          03 RT-HMT-TERRITORY-CODE            PIC X(3).
          03 RT-HMT-CLASS-CODE                PIC X(4).
          03 RT-HMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HMT-RATED-PREMIUM             PIC 9(9)V9(2).
