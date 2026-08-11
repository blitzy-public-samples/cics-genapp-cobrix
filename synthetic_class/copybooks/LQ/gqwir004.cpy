******************************************************************
*  COPYBOOK  : GQWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : WI
******************************************************************
 01  RT-QWI-RATING.

          03 RT-QWI-TERRITORY-CODE            PIC X(3).
          03 RT-QWI-CLASS-CODE                PIC X(4).
          03 RT-QWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QWI-RATED-PREMIUM             PIC 9(9)V9(2).
