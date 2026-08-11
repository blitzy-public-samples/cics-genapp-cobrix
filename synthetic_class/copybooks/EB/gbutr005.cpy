******************************************************************
*  COPYBOOK  : GBUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : UT
******************************************************************
 01  RT-BUT-RATING.

          03 RT-BUT-TERRITORY-CODE            PIC X(3).
          03 RT-BUT-CLASS-CODE                PIC X(4).
          03 RT-BUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BUT-RATED-PREMIUM             PIC 9(9)V9(2).
