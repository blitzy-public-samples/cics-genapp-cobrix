******************************************************************
*  COPYBOOK  : GQVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : VA
******************************************************************
 01  RT-QVA-RATING.

          03 RT-QVA-TERRITORY-CODE            PIC X(3).
          03 RT-QVA-CLASS-CODE                PIC X(4).
          03 RT-QVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QVA-RATED-PREMIUM             PIC 9(9)V9(2).
