******************************************************************
*  COPYBOOK  : GPNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : NC
******************************************************************
 01  RT-PNC-RATING.

          03 RT-PNC-TERRITORY-CODE            PIC X(3).
          03 RT-PNC-CLASS-CODE                PIC X(4).
          03 RT-PNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PNC-RATED-PREMIUM             PIC 9(9)V9(2).
