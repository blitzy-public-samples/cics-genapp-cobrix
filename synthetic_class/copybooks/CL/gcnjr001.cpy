******************************************************************
*  COPYBOOK  : GCNJR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : NJ
******************************************************************
 01  RT-CNJ-RATING.

          03 RT-CNJ-TERRITORY-CODE            PIC X(3).
          03 RT-CNJ-CLASS-CODE                PIC X(4).
          03 RT-CNJ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CNJ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CNJ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CNJ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CNJ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CNJ-RATED-PREMIUM             PIC 9(9)V9(2).
