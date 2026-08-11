******************************************************************
*  COPYBOOK  : GACAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : CA
******************************************************************
 01  RT-ACA-RATING.

          03 RT-ACA-TERRITORY-CODE            PIC X(3).
          03 RT-ACA-CLASS-CODE                PIC X(4).
          03 RT-ACA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ACA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ACA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ACA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ACA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ACA-RATED-PREMIUM             PIC 9(9)V9(2).
