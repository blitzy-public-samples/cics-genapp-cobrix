******************************************************************
*  COPYBOOK  : GBAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : AZ
******************************************************************
 01  RT-BAZ-RATING.

          03 RT-BAZ-TERRITORY-CODE            PIC X(3).
          03 RT-BAZ-CLASS-CODE                PIC X(4).
          03 RT-BAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BAZ-RATED-PREMIUM             PIC 9(9)V9(2).
