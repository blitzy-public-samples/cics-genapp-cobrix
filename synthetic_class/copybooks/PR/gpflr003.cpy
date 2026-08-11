******************************************************************
*  COPYBOOK  : GPFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : FL
******************************************************************
 01  RT-PFL-RATING.

          03 RT-PFL-TERRITORY-CODE            PIC X(3).
          03 RT-PFL-CLASS-CODE                PIC X(4).
          03 RT-PFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PFL-RATED-PREMIUM             PIC 9(9)V9(2).
