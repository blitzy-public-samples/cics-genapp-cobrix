******************************************************************
*  COPYBOOK  : GMALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : AL
******************************************************************
 01  RT-MAL-RATING.

          03 RT-MAL-TERRITORY-CODE            PIC X(3).
          03 RT-MAL-CLASS-CODE                PIC X(4).
          03 RT-MAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MAL-RATED-PREMIUM             PIC 9(9)V9(2).
