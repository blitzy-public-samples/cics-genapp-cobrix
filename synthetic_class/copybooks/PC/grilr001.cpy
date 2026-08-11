******************************************************************
*  COPYBOOK  : GRILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : IL
******************************************************************
 01  RT-RIL-RATING.

          03 RT-RIL-TERRITORY-CODE            PIC X(3).
          03 RT-RIL-CLASS-CODE                PIC X(4).
          03 RT-RIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RIL-RATED-PREMIUM             PIC 9(9)V9(2).
