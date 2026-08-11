******************************************************************
*  COPYBOOK  : GQNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : NV
******************************************************************
 01  RT-QNV-RATING.

          03 RT-QNV-TERRITORY-CODE            PIC X(3).
          03 RT-QNV-CLASS-CODE                PIC X(4).
          03 RT-QNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QNV-RATED-PREMIUM             PIC 9(9)V9(2).
