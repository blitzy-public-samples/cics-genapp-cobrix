******************************************************************
*  COPYBOOK  : GPIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : ID
******************************************************************
 01  RT-PID-RATING.

          03 RT-PID-TERRITORY-CODE            PIC X(3).
          03 RT-PID-CLASS-CODE                PIC X(4).
          03 RT-PID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PID-RATED-PREMIUM             PIC 9(9)V9(2).
