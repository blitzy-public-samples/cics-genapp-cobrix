******************************************************************
*  COPYBOOK  : GNDCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : DC
******************************************************************
 01  RT-NDC-RATING.

          03 RT-NDC-TERRITORY-CODE            PIC X(3).
          03 RT-NDC-CLASS-CODE                PIC X(4).
          03 RT-NDC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NDC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NDC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NDC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NDC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NDC-RATED-PREMIUM             PIC 9(9)V9(2).
