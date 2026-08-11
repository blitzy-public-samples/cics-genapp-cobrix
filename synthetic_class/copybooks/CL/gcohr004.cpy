******************************************************************
*  COPYBOOK  : GCOHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : OH
******************************************************************
 01  RT-COH-RATING.

          03 RT-COH-TERRITORY-CODE            PIC X(3).
          03 RT-COH-CLASS-CODE                PIC X(4).
          03 RT-COH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-COH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-COH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-COH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-COH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-COH-RATED-PREMIUM             PIC 9(9)V9(2).
