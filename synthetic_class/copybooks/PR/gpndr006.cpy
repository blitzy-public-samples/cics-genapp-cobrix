******************************************************************
*  COPYBOOK  : GPNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : ND
******************************************************************
 01  RT-PND-RATING.

          03 RT-PND-TERRITORY-CODE            PIC X(3).
          03 RT-PND-CLASS-CODE                PIC X(4).
          03 RT-PND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PND-RATED-PREMIUM             PIC 9(9)V9(2).
