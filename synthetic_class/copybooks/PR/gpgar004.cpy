******************************************************************
*  COPYBOOK  : GPGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : GA
******************************************************************
 01  RT-PGA-RATING.

          03 RT-PGA-TERRITORY-CODE            PIC X(3).
          03 RT-PGA-CLASS-CODE                PIC X(4).
          03 RT-PGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PGA-RATED-PREMIUM             PIC 9(9)V9(2).
