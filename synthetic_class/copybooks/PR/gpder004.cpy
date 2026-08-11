******************************************************************
*  COPYBOOK  : GPDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : DE
******************************************************************
 01  RT-PDE-RATING.

          03 RT-PDE-TERRITORY-CODE            PIC X(3).
          03 RT-PDE-CLASS-CODE                PIC X(4).
          03 RT-PDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PDE-RATED-PREMIUM             PIC 9(9)V9(2).
