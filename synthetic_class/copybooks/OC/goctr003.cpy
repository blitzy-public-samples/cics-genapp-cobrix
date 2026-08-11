******************************************************************
*  COPYBOOK  : GOCTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : CT
******************************************************************
 01  RT-OCT-RATING.

          03 RT-OCT-TERRITORY-CODE            PIC X(3).
          03 RT-OCT-CLASS-CODE                PIC X(4).
          03 RT-OCT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OCT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OCT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OCT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OCT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OCT-RATED-PREMIUM             PIC 9(9)V9(2).
