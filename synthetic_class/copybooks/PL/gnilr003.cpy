******************************************************************
*  COPYBOOK  : GNILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : IL
******************************************************************
 01  RT-NIL-RATING.

          03 RT-NIL-TERRITORY-CODE            PIC X(3).
          03 RT-NIL-CLASS-CODE                PIC X(4).
          03 RT-NIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NIL-RATED-PREMIUM             PIC 9(9)V9(2).
