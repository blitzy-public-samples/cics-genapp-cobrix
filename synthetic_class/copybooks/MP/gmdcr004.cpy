******************************************************************
*  COPYBOOK  : GMDCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : DC
******************************************************************
 01  RT-MDC-RATING.

          03 RT-MDC-TERRITORY-CODE            PIC X(3).
          03 RT-MDC-CLASS-CODE                PIC X(4).
          03 RT-MDC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MDC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MDC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MDC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MDC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MDC-RATED-PREMIUM             PIC 9(9)V9(2).
