******************************************************************
*  COPYBOOK  : GHRIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : RI
******************************************************************
 01  RT-HRI-RATING.

          03 RT-HRI-TERRITORY-CODE            PIC X(3).
          03 RT-HRI-CLASS-CODE                PIC X(4).
          03 RT-HRI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HRI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HRI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HRI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HRI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HRI-RATED-PREMIUM             PIC 9(9)V9(2).
