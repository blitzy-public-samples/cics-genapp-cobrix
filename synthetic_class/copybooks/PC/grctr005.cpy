******************************************************************
*  COPYBOOK  : GRCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : CT
******************************************************************
 01  RT-RCT-RATING.

          03 RT-RCT-TERRITORY-CODE            PIC X(3).
          03 RT-RCT-CLASS-CODE                PIC X(4).
          03 RT-RCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RCT-RATED-PREMIUM             PIC 9(9)V9(2).
