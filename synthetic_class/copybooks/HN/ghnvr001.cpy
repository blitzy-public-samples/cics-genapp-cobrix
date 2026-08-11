******************************************************************
*  COPYBOOK  : GHNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : NV
******************************************************************
 01  RT-HNV-RATING.

          03 RT-HNV-TERRITORY-CODE            PIC X(3).
          03 RT-HNV-CLASS-CODE                PIC X(4).
          03 RT-HNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HNV-RATED-PREMIUM             PIC 9(9)V9(2).
