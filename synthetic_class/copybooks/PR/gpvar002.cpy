******************************************************************
*  COPYBOOK  : GPVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : VA
******************************************************************
 01  RT-PVA-RATING.

          03 RT-PVA-TERRITORY-CODE            PIC X(3).
          03 RT-PVA-CLASS-CODE                PIC X(4).
          03 RT-PVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PVA-RATED-PREMIUM             PIC 9(9)V9(2).
