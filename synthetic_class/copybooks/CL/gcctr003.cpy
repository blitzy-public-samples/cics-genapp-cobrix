******************************************************************
*  COPYBOOK  : GCCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : CT
******************************************************************
 01  RT-CCT-RATING.

          03 RT-CCT-TERRITORY-CODE            PIC X(3).
          03 RT-CCT-CLASS-CODE                PIC X(4).
          03 RT-CCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CCT-RATED-PREMIUM             PIC 9(9)V9(2).
