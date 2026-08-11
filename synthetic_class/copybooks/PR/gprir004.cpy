******************************************************************
*  COPYBOOK  : GPRIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : RI
******************************************************************
 01  RT-PRI-RATING.

          03 RT-PRI-TERRITORY-CODE            PIC X(3).
          03 RT-PRI-CLASS-CODE                PIC X(4).
          03 RT-PRI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PRI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PRI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PRI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PRI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PRI-RATED-PREMIUM             PIC 9(9)V9(2).
