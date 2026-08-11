******************************************************************
*  COPYBOOK  : GBDCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Employee Benefits Liability (EB)
*  STATE     : DC
******************************************************************
 01  RT-BDC-RATING.

          03 RT-BDC-TERRITORY-CODE            PIC X(3).
          03 RT-BDC-CLASS-CODE                PIC X(4).
          03 RT-BDC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-BDC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-BDC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-BDC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-BDC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-BDC-RATED-PREMIUM             PIC 9(9)V9(2).
