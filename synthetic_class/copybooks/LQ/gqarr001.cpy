******************************************************************
*  COPYBOOK  : GQARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : AR
******************************************************************
 01  RT-QAR-RATING.

          03 RT-QAR-TERRITORY-CODE            PIC X(3).
          03 RT-QAR-CLASS-CODE                PIC X(4).
          03 RT-QAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QAR-RATED-PREMIUM             PIC 9(9)V9(2).
