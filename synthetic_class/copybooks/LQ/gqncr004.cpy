******************************************************************
*  COPYBOOK  : GQNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : NC
******************************************************************
 01  RT-QNC-RATING.

          03 RT-QNC-TERRITORY-CODE            PIC X(3).
          03 RT-QNC-CLASS-CODE                PIC X(4).
          03 RT-QNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QNC-RATED-PREMIUM             PIC 9(9)V9(2).
