******************************************************************
*  COPYBOOK  : GRAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : AZ
******************************************************************
 01  RT-RAZ-RATING.

          03 RT-RAZ-TERRITORY-CODE            PIC X(3).
          03 RT-RAZ-CLASS-CODE                PIC X(4).
          03 RT-RAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RAZ-RATED-PREMIUM             PIC 9(9)V9(2).
