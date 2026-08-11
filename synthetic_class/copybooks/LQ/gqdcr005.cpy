******************************************************************
*  COPYBOOK  : GQDCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : DC
******************************************************************
 01  RT-QDC-RATING.

          03 RT-QDC-TERRITORY-CODE            PIC X(3).
          03 RT-QDC-CLASS-CODE                PIC X(4).
          03 RT-QDC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QDC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QDC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QDC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QDC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QDC-RATED-PREMIUM             PIC 9(9)V9(2).
