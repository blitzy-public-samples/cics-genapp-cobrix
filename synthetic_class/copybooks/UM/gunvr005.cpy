******************************************************************
*  COPYBOOK  : GUNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : NV
******************************************************************
 01  RT-UNV-RATING.

          03 RT-UNV-TERRITORY-CODE            PIC X(3).
          03 RT-UNV-CLASS-CODE                PIC X(4).
          03 RT-UNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UNV-RATED-PREMIUM             PIC 9(9)V9(2).
