******************************************************************
*  COPYBOOK  : GCDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : DE
******************************************************************
 01  RT-CDE-RATING.

          03 RT-CDE-TERRITORY-CODE            PIC X(3).
          03 RT-CDE-CLASS-CODE                PIC X(4).
          03 RT-CDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CDE-RATED-PREMIUM             PIC 9(9)V9(2).
