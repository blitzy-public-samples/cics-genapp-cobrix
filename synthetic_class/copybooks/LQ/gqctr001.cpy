******************************************************************
*  COPYBOOK  : GQCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : CT
******************************************************************
 01  RT-QCT-RATING.

          03 RT-QCT-TERRITORY-CODE            PIC X(3).
          03 RT-QCT-CLASS-CODE                PIC X(4).
          03 RT-QCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QCT-RATED-PREMIUM             PIC 9(9)V9(2).
