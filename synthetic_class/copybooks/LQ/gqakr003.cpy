******************************************************************
*  COPYBOOK  : GQAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : AK
******************************************************************
 01  RT-QAK-RATING.

          03 RT-QAK-TERRITORY-CODE            PIC X(3).
          03 RT-QAK-CLASS-CODE                PIC X(4).
          03 RT-QAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QAK-RATED-PREMIUM             PIC 9(9)V9(2).
