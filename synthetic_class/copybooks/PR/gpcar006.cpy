******************************************************************
*  COPYBOOK  : GPCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : CA
******************************************************************
 01  RT-PCA-RATING.

          03 RT-PCA-TERRITORY-CODE            PIC X(3).
          03 RT-PCA-CLASS-CODE                PIC X(4).
          03 RT-PCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PCA-RATED-PREMIUM             PIC 9(9)V9(2).
