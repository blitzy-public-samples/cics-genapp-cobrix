******************************************************************
*  COPYBOOK  : GOHIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : HI
******************************************************************
 01  RT-OHI-RATING.

          03 RT-OHI-TERRITORY-CODE            PIC X(3).
          03 RT-OHI-CLASS-CODE                PIC X(4).
          03 RT-OHI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OHI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OHI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OHI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OHI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OHI-RATED-PREMIUM             PIC 9(9)V9(2).
