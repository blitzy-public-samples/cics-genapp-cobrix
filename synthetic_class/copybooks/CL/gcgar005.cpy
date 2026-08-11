******************************************************************
*  COPYBOOK  : GCGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : GA
******************************************************************
 01  RT-CGA-RATING.

          03 RT-CGA-TERRITORY-CODE            PIC X(3).
          03 RT-CGA-CLASS-CODE                PIC X(4).
          03 RT-CGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CGA-RATED-PREMIUM             PIC 9(9)V9(2).
