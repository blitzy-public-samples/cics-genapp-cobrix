******************************************************************
*  COPYBOOK  : GHDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : DE
******************************************************************
 01  RT-HDE-RATING.

          03 RT-HDE-TERRITORY-CODE            PIC X(3).
          03 RT-HDE-CLASS-CODE                PIC X(4).
          03 RT-HDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HDE-RATED-PREMIUM             PIC 9(9)V9(2).
