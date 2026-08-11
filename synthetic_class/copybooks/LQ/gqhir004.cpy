******************************************************************
*  COPYBOOK  : GQHIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : HI
******************************************************************
 01  RT-QHI-RATING.

          03 RT-QHI-TERRITORY-CODE            PIC X(3).
          03 RT-QHI-CLASS-CODE                PIC X(4).
          03 RT-QHI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QHI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QHI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QHI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QHI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QHI-RATED-PREMIUM             PIC 9(9)V9(2).
