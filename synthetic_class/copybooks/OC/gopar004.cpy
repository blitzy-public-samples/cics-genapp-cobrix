******************************************************************
*  COPYBOOK  : GOPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : PA
******************************************************************
 01  RT-OPA-RATING.

          03 RT-OPA-TERRITORY-CODE            PIC X(3).
          03 RT-OPA-CLASS-CODE                PIC X(4).
          03 RT-OPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OPA-RATED-PREMIUM             PIC 9(9)V9(2).
