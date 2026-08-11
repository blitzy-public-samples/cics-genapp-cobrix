******************************************************************
*  COPYBOOK  : GPMDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : MD
******************************************************************
 01  RT-PMD-RATING.

          03 RT-PMD-TERRITORY-CODE            PIC X(3).
          03 RT-PMD-CLASS-CODE                PIC X(4).
          03 RT-PMD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PMD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PMD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PMD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PMD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PMD-RATED-PREMIUM             PIC 9(9)V9(2).
