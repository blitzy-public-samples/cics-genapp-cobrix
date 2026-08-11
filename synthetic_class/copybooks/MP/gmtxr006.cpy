******************************************************************
*  COPYBOOK  : GMTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : TX
******************************************************************
 01  RT-MTX-RATING.

          03 RT-MTX-TERRITORY-CODE            PIC X(3).
          03 RT-MTX-CLASS-CODE                PIC X(4).
          03 RT-MTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MTX-RATED-PREMIUM             PIC 9(9)V9(2).
