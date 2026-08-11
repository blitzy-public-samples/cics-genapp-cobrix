******************************************************************
*  COPYBOOK  : GHTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : TN
******************************************************************
 01  RT-HTN-RATING.

          03 RT-HTN-TERRITORY-CODE            PIC X(3).
          03 RT-HTN-CLASS-CODE                PIC X(4).
          03 RT-HTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HTN-RATED-PREMIUM             PIC 9(9)V9(2).
