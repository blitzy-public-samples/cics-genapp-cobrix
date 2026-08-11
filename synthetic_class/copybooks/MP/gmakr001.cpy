******************************************************************
*  COPYBOOK  : GMAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : AK
******************************************************************
 01  RT-MAK-RATING.

          03 RT-MAK-TERRITORY-CODE            PIC X(3).
          03 RT-MAK-CLASS-CODE                PIC X(4).
          03 RT-MAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MAK-RATED-PREMIUM             PIC 9(9)V9(2).
