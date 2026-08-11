******************************************************************
*  COPYBOOK  : GNVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : VA
******************************************************************
 01  RT-NVA-RATING.

          03 RT-NVA-TERRITORY-CODE            PIC X(3).
          03 RT-NVA-CLASS-CODE                PIC X(4).
          03 RT-NVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NVA-RATED-PREMIUM             PIC 9(9)V9(2).
