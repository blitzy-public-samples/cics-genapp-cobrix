******************************************************************
*  COPYBOOK  : GRNER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NE
******************************************************************
 01  RT-RNE-RATING.

          03 RT-RNE-TERRITORY-CODE            PIC X(3).
          03 RT-RNE-CLASS-CODE                PIC X(4).
          03 RT-RNE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RNE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RNE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RNE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RNE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RNE-RATED-PREMIUM             PIC 9(9)V9(2).
