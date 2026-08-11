******************************************************************
*  COPYBOOK  : GHFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : FL
******************************************************************
 01  RT-HFL-RATING.

          03 RT-HFL-TERRITORY-CODE            PIC X(3).
          03 RT-HFL-CLASS-CODE                PIC X(4).
          03 RT-HFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HFL-RATED-PREMIUM             PIC 9(9)V9(2).
