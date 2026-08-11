******************************************************************
*  COPYBOOK  : GHMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : MI
******************************************************************
 01  RT-HMI-RATING.

          03 RT-HMI-TERRITORY-CODE            PIC X(3).
          03 RT-HMI-CLASS-CODE                PIC X(4).
          03 RT-HMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HMI-RATED-PREMIUM             PIC 9(9)V9(2).
