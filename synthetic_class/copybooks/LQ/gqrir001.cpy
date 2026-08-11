******************************************************************
*  COPYBOOK  : GQRIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : RI
******************************************************************
 01  RT-QRI-RATING.

          03 RT-QRI-TERRITORY-CODE            PIC X(3).
          03 RT-QRI-CLASS-CODE                PIC X(4).
          03 RT-QRI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QRI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QRI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QRI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QRI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QRI-RATED-PREMIUM             PIC 9(9)V9(2).
