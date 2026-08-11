******************************************************************
*  COPYBOOK  : GOWVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : WV
******************************************************************
 01  RT-OWV-RATING.

          03 RT-OWV-TERRITORY-CODE            PIC X(3).
          03 RT-OWV-CLASS-CODE                PIC X(4).
          03 RT-OWV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OWV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OWV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OWV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OWV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OWV-RATED-PREMIUM             PIC 9(9)V9(2).
