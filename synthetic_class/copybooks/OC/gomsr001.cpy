******************************************************************
*  COPYBOOK  : GOMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : MS
******************************************************************
 01  RT-OMS-RATING.

          03 RT-OMS-TERRITORY-CODE            PIC X(3).
          03 RT-OMS-CLASS-CODE                PIC X(4).
          03 RT-OMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OMS-RATED-PREMIUM             PIC 9(9)V9(2).
