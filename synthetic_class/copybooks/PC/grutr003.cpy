******************************************************************
*  COPYBOOK  : GRUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : UT
******************************************************************
 01  RT-RUT-RATING.

          03 RT-RUT-TERRITORY-CODE            PIC X(3).
          03 RT-RUT-CLASS-CODE                PIC X(4).
          03 RT-RUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RUT-RATED-PREMIUM             PIC 9(9)V9(2).
