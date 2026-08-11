******************************************************************
*  COPYBOOK  : GCNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : NC
******************************************************************
 01  RT-CNC-RATING.

          03 RT-CNC-TERRITORY-CODE            PIC X(3).
          03 RT-CNC-CLASS-CODE                PIC X(4).
          03 RT-CNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CNC-RATED-PREMIUM             PIC 9(9)V9(2).
