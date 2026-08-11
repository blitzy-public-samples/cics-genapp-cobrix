******************************************************************
*  COPYBOOK  : GHINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : IN
******************************************************************
 01  RT-HIN-RATING.

          03 RT-HIN-TERRITORY-CODE            PIC X(3).
          03 RT-HIN-CLASS-CODE                PIC X(4).
          03 RT-HIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HIN-RATED-PREMIUM             PIC 9(9)V9(2).
