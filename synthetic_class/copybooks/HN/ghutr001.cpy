******************************************************************
*  COPYBOOK  : GHUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : UT
******************************************************************
 01  RT-HUT-RATING.

          03 RT-HUT-TERRITORY-CODE            PIC X(3).
          03 RT-HUT-CLASS-CODE                PIC X(4).
          03 RT-HUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HUT-RATED-PREMIUM             PIC 9(9)V9(2).
