******************************************************************
*  COPYBOOK  : GOCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : CO
******************************************************************
 01  RT-OCO-RATING.

          03 RT-OCO-TERRITORY-CODE            PIC X(3).
          03 RT-OCO-CLASS-CODE                PIC X(4).
          03 RT-OCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OCO-RATED-PREMIUM             PIC 9(9)V9(2).
