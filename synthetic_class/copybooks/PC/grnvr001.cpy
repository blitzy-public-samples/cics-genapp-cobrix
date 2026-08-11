******************************************************************
*  COPYBOOK  : GRNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NV
******************************************************************
 01  RT-RNV-RATING.

          03 RT-RNV-TERRITORY-CODE            PIC X(3).
          03 RT-RNV-CLASS-CODE                PIC X(4).
          03 RT-RNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RNV-RATED-PREMIUM             PIC 9(9)V9(2).
