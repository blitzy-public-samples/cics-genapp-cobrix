******************************************************************
*  COPYBOOK  : GOKYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : KY
******************************************************************
 01  RT-OKY-RATING.

          03 RT-OKY-TERRITORY-CODE            PIC X(3).
          03 RT-OKY-CLASS-CODE                PIC X(4).
          03 RT-OKY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OKY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OKY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OKY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OKY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OKY-RATED-PREMIUM             PIC 9(9)V9(2).
