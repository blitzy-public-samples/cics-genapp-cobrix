******************************************************************
*  COPYBOOK  : GQVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : VT
******************************************************************
 01  RT-QVT-RATING.

          03 RT-QVT-TERRITORY-CODE            PIC X(3).
          03 RT-QVT-CLASS-CODE                PIC X(4).
          03 RT-QVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QVT-RATED-PREMIUM             PIC 9(9)V9(2).
