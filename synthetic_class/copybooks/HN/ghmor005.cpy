******************************************************************
*  COPYBOOK  : GHMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : MO
******************************************************************
 01  RT-HMO-RATING.

          03 RT-HMO-TERRITORY-CODE            PIC X(3).
          03 RT-HMO-CLASS-CODE                PIC X(4).
          03 RT-HMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HMO-RATED-PREMIUM             PIC 9(9)V9(2).
