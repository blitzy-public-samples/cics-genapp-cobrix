******************************************************************
*  COPYBOOK  : GQGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : GA
******************************************************************
 01  RT-QGA-RATING.

          03 RT-QGA-TERRITORY-CODE            PIC X(3).
          03 RT-QGA-CLASS-CODE                PIC X(4).
          03 RT-QGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QGA-RATED-PREMIUM             PIC 9(9)V9(2).
