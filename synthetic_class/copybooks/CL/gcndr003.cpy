******************************************************************
*  COPYBOOK  : GCNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : ND
******************************************************************
 01  RT-CND-RATING.

          03 RT-CND-TERRITORY-CODE            PIC X(3).
          03 RT-CND-CLASS-CODE                PIC X(4).
          03 RT-CND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CND-RATED-PREMIUM             PIC 9(9)V9(2).
