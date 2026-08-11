******************************************************************
*  COPYBOOK  : GQIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : IA
******************************************************************
 01  RT-QIA-RATING.

          03 RT-QIA-TERRITORY-CODE            PIC X(3).
          03 RT-QIA-CLASS-CODE                PIC X(4).
          03 RT-QIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QIA-RATED-PREMIUM             PIC 9(9)V9(2).
