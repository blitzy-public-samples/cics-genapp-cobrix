******************************************************************
*  COPYBOOK  : GPHIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : HI
******************************************************************
 01  RT-PHI-RATING.

          03 RT-PHI-TERRITORY-CODE            PIC X(3).
          03 RT-PHI-CLASS-CODE                PIC X(4).
          03 RT-PHI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PHI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PHI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PHI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PHI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PHI-RATED-PREMIUM             PIC 9(9)V9(2).
