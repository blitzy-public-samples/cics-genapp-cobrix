******************************************************************
*  COPYBOOK  : GQTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : TX
******************************************************************
 01  RT-QTX-RATING.

          03 RT-QTX-TERRITORY-CODE            PIC X(3).
          03 RT-QTX-CLASS-CODE                PIC X(4).
          03 RT-QTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QTX-RATED-PREMIUM             PIC 9(9)V9(2).
