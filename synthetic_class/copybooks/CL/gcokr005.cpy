******************************************************************
*  COPYBOOK  : GCOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : OK
******************************************************************
 01  RT-COK-RATING.

          03 RT-COK-TERRITORY-CODE            PIC X(3).
          03 RT-COK-CLASS-CODE                PIC X(4).
          03 RT-COK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-COK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-COK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-COK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-COK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-COK-RATED-PREMIUM             PIC 9(9)V9(2).
