******************************************************************
*  COPYBOOK  : GOWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : WY
******************************************************************
 01  RT-OWY-RATING.

          03 RT-OWY-TERRITORY-CODE            PIC X(3).
          03 RT-OWY-CLASS-CODE                PIC X(4).
          03 RT-OWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OWY-RATED-PREMIUM             PIC 9(9)V9(2).
