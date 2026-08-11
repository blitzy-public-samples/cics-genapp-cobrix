******************************************************************
*  COPYBOOK  : GCAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : AK
******************************************************************
 01  RT-CAK-RATING.

          03 RT-CAK-TERRITORY-CODE            PIC X(3).
          03 RT-CAK-CLASS-CODE                PIC X(4).
          03 RT-CAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CAK-RATED-PREMIUM             PIC 9(9)V9(2).
