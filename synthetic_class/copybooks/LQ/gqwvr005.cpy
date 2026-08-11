******************************************************************
*  COPYBOOK  : GQWVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : WV
******************************************************************
 01  RT-QWV-RATING.

          03 RT-QWV-TERRITORY-CODE            PIC X(3).
          03 RT-QWV-CLASS-CODE                PIC X(4).
          03 RT-QWV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QWV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QWV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QWV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QWV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QWV-RATED-PREMIUM             PIC 9(9)V9(2).
