******************************************************************
*  COPYBOOK  : GMAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : AZ
******************************************************************
 01  RT-MAZ-RATING.

          03 RT-MAZ-TERRITORY-CODE            PIC X(3).
          03 RT-MAZ-CLASS-CODE                PIC X(4).
          03 RT-MAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MAZ-RATED-PREMIUM             PIC 9(9)V9(2).
