******************************************************************
*  COPYBOOK  : GQNER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : NE
******************************************************************
 01  RT-QNE-RATING.

          03 RT-QNE-TERRITORY-CODE            PIC X(3).
          03 RT-QNE-CLASS-CODE                PIC X(4).
          03 RT-QNE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QNE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QNE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QNE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QNE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QNE-RATED-PREMIUM             PIC 9(9)V9(2).
