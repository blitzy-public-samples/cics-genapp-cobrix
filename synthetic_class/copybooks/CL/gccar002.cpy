******************************************************************
*  COPYBOOK  : GCCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : CA
******************************************************************
 01  RT-CCA-RATING.

          03 RT-CCA-TERRITORY-CODE            PIC X(3).
          03 RT-CCA-CLASS-CODE                PIC X(4).
          03 RT-CCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CCA-RATED-PREMIUM             PIC 9(9)V9(2).
