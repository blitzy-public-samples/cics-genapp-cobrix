******************************************************************
*  COPYBOOK  : GHCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : CA
******************************************************************
 01  RT-HCA-RATING.

          03 RT-HCA-TERRITORY-CODE            PIC X(3).
          03 RT-HCA-CLASS-CODE                PIC X(4).
          03 RT-HCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HCA-RATED-PREMIUM             PIC 9(9)V9(2).
