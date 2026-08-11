******************************************************************
*  COPYBOOK  : GQNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : NM
******************************************************************
 01  RT-QNM-RATING.

          03 RT-QNM-TERRITORY-CODE            PIC X(3).
          03 RT-QNM-CLASS-CODE                PIC X(4).
          03 RT-QNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QNM-RATED-PREMIUM             PIC 9(9)V9(2).
