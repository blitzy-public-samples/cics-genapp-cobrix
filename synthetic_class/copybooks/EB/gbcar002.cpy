******************************************************************
*  COPYBOOK  : GBCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : CA
******************************************************************
 01  RT-BCA-RATING.

          03 RT-BCA-TERRITORY-CODE            PIC X(3).
          03 RT-BCA-CLASS-CODE                PIC X(4).
          03 RT-BCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BCA-RATED-PREMIUM             PIC 9(9)V9(2).
