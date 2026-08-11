******************************************************************
*  COPYBOOK  : GRAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : AK
******************************************************************
 01  RT-RAK-RATING.

          03 RT-RAK-TERRITORY-CODE            PIC X(3).
          03 RT-RAK-CLASS-CODE                PIC X(4).
          03 RT-RAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RAK-RATED-PREMIUM             PIC 9(9)V9(2).
