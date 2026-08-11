******************************************************************
*  COPYBOOK  : GPPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : PA
******************************************************************
 01  RT-PPA-RATING.

          03 RT-PPA-TERRITORY-CODE            PIC X(3).
          03 RT-PPA-CLASS-CODE                PIC X(4).
          03 RT-PPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PPA-RATED-PREMIUM             PIC 9(9)V9(2).
