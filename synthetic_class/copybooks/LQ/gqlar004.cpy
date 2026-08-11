******************************************************************
*  COPYBOOK  : GQLAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : LA
******************************************************************
 01  RT-QLA-RATING.

          03 RT-QLA-TERRITORY-CODE            PIC X(3).
          03 RT-QLA-CLASS-CODE                PIC X(4).
          03 RT-QLA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QLA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QLA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QLA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QLA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QLA-RATED-PREMIUM             PIC 9(9)V9(2).
