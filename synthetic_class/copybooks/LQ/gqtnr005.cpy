******************************************************************
*  COPYBOOK  : GQTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : TN
******************************************************************
 01  RT-QTN-RATING.

          03 RT-QTN-TERRITORY-CODE            PIC X(3).
          03 RT-QTN-CLASS-CODE                PIC X(4).
          03 RT-QTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QTN-RATED-PREMIUM             PIC 9(9)V9(2).
