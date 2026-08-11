******************************************************************
*  COPYBOOK  : GRARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : AR
******************************************************************
 01  RT-RAR-RATING.

          03 RT-RAR-TERRITORY-CODE            PIC X(3).
          03 RT-RAR-CLASS-CODE                PIC X(4).
          03 RT-RAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RAR-RATED-PREMIUM             PIC 9(9)V9(2).
