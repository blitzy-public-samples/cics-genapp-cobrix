******************************************************************
*  COPYBOOK  : GPMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : ME
******************************************************************
 01  RT-PME-RATING.

          03 RT-PME-TERRITORY-CODE            PIC X(3).
          03 RT-PME-CLASS-CODE                PIC X(4).
          03 RT-PME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PME-RATED-PREMIUM             PIC 9(9)V9(2).
