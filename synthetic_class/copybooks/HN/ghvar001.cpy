******************************************************************
*  COPYBOOK  : GHVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : VA
******************************************************************
 01  RT-HVA-RATING.

          03 RT-HVA-TERRITORY-CODE            PIC X(3).
          03 RT-HVA-CLASS-CODE                PIC X(4).
          03 RT-HVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HVA-RATED-PREMIUM             PIC 9(9)V9(2).
