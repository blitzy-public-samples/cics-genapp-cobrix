******************************************************************
*  COPYBOOK  : GRMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MI
******************************************************************
 01  RT-RMI-RATING.

          03 RT-RMI-TERRITORY-CODE            PIC X(3).
          03 RT-RMI-CLASS-CODE                PIC X(4).
          03 RT-RMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RMI-RATED-PREMIUM             PIC 9(9)V9(2).
