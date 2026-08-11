******************************************************************
*  COPYBOOK  : GQNJR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : NJ
******************************************************************
 01  RT-QNJ-RATING.

          03 RT-QNJ-TERRITORY-CODE            PIC X(3).
          03 RT-QNJ-CLASS-CODE                PIC X(4).
          03 RT-QNJ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QNJ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QNJ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QNJ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QNJ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QNJ-RATED-PREMIUM             PIC 9(9)V9(2).
