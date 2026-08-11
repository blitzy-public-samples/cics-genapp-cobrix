******************************************************************
*  COPYBOOK  : GRTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : TN
******************************************************************
 01  RT-RTN-RATING.

          03 RT-RTN-TERRITORY-CODE            PIC X(3).
          03 RT-RTN-CLASS-CODE                PIC X(4).
          03 RT-RTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RTN-RATED-PREMIUM             PIC 9(9)V9(2).
