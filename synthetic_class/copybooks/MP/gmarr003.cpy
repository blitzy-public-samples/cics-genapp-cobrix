******************************************************************
*  COPYBOOK  : GMARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : AR
******************************************************************
 01  RT-MAR-RATING.

          03 RT-MAR-TERRITORY-CODE            PIC X(3).
          03 RT-MAR-CLASS-CODE                PIC X(4).
          03 RT-MAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MAR-RATED-PREMIUM             PIC 9(9)V9(2).
