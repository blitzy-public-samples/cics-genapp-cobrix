******************************************************************
*  COPYBOOK  : GPNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : NH
******************************************************************
 01  RT-PNH-RATING.

          03 RT-PNH-TERRITORY-CODE            PIC X(3).
          03 RT-PNH-CLASS-CODE                PIC X(4).
          03 RT-PNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PNH-RATED-PREMIUM             PIC 9(9)V9(2).
