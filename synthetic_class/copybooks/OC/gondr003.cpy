******************************************************************
*  COPYBOOK  : GONDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : ND
******************************************************************
 01  RT-OND-RATING.

          03 RT-OND-TERRITORY-CODE            PIC X(3).
          03 RT-OND-CLASS-CODE                PIC X(4).
          03 RT-OND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OND-RATED-PREMIUM             PIC 9(9)V9(2).
