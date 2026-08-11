******************************************************************
*  COPYBOOK  : GMTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : TN
******************************************************************
 01  RT-MTN-RATING.

          03 RT-MTN-TERRITORY-CODE            PIC X(3).
          03 RT-MTN-CLASS-CODE                PIC X(4).
          03 RT-MTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MTN-RATED-PREMIUM             PIC 9(9)V9(2).
