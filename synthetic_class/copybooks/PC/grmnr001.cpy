******************************************************************
*  COPYBOOK  : GRMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : MN
******************************************************************
 01  RT-RMN-RATING.

          03 RT-RMN-TERRITORY-CODE            PIC X(3).
          03 RT-RMN-CLASS-CODE                PIC X(4).
          03 RT-RMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RMN-RATED-PREMIUM             PIC 9(9)V9(2).
