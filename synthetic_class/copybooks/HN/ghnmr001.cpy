******************************************************************
*  COPYBOOK  : GHNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : NM
******************************************************************
 01  RT-HNM-RATING.

          03 RT-HNM-TERRITORY-CODE            PIC X(3).
          03 RT-HNM-CLASS-CODE                PIC X(4).
          03 RT-HNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HNM-RATED-PREMIUM             PIC 9(9)V9(2).
