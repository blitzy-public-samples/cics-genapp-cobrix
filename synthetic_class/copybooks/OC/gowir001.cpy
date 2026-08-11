******************************************************************
*  COPYBOOK  : GOWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : WI
******************************************************************
 01  RT-OWI-RATING.

          03 RT-OWI-TERRITORY-CODE            PIC X(3).
          03 RT-OWI-CLASS-CODE                PIC X(4).
          03 RT-OWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OWI-RATED-PREMIUM             PIC 9(9)V9(2).
