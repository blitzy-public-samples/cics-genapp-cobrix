******************************************************************
*  COPYBOOK  : GQOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : OK
******************************************************************
 01  RT-QOK-RATING.

          03 RT-QOK-TERRITORY-CODE            PIC X(3).
          03 RT-QOK-CLASS-CODE                PIC X(4).
          03 RT-QOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QOK-RATED-PREMIUM             PIC 9(9)V9(2).
