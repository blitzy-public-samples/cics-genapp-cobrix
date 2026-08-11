******************************************************************
*  COPYBOOK  : GOWAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : WA
******************************************************************
 01  RT-OWA-RATING.

          03 RT-OWA-TERRITORY-CODE            PIC X(3).
          03 RT-OWA-CLASS-CODE                PIC X(4).
          03 RT-OWA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OWA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OWA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OWA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OWA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OWA-RATED-PREMIUM             PIC 9(9)V9(2).
