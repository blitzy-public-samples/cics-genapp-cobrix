******************************************************************
*  COPYBOOK  : GOUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : UT
******************************************************************
 01  RT-OUT-RATING.

          03 RT-OUT-TERRITORY-CODE            PIC X(3).
          03 RT-OUT-CLASS-CODE                PIC X(4).
          03 RT-OUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OUT-RATED-PREMIUM             PIC 9(9)V9(2).
